#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUTDIR = Path(sys.argv[1])
OUTDIR.mkdir(parents=True, exist_ok=True)

FILES = [
    ROOT / "run/live_capture/pfeeds_live_raw_capture_20260430_094330.log",
    ROOT / "run/live_capture/batch26m_readonly_live_capture_20260430_100553.log.gz",
    ROOT / "run/live_capture/pfeatures_20260430_094547.log",
    ROOT / "run/live_capture/pstrategy_20260430_094557.log",
    ROOT / "run/live_capture/batch26n_all_family_paper_shadow_20260430_104130.log",
]

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]

def read_text(path: Path, limit: int = 300_000_000) -> str:
    if not path.exists():
        return ""
    if path.suffix == ".gz":
        with gzip.open(path, "rt", errors="replace") as f:
            return f.read(limit)
    return path.read_text(errors="replace")[:limit]

def extract_jsons(text: str, max_items: int = 200000) -> list[Any]:
    out = []
    for line in text.splitlines():
        if "{" not in line or "}" not in line:
            continue
        s = line[line.find("{"):line.rfind("}")+1]
        try:
            out.append(json.loads(s))
        except Exception:
            continue
        if len(out) >= max_items:
            break
    return out

def floats_for_keys(obj: Any, keys: set[str], out: list[float]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys:
                try:
                    if v is not None and str(v) != "":
                        out.append(float(v))
                except Exception:
                    pass
            floats_for_keys(v, keys, out)
    elif isinstance(obj, list):
        for x in obj:
            floats_for_keys(x, keys, out)

def count_terms(text: str) -> Counter:
    c = Counter()
    terms = [
        "trend_confirmed", "pullback_detected", "resume_confirmed",
        "shelf_confirmed", "breakout_triggered", "breakout_accepted",
        "compression_detected", "directional_breakout_triggered", "expansion_accepted", "retest_monitor_active",
        "fake_break", "range_reentry", "flow_flip", "reversal_impulse",
        "burst_detected", "aggression_ok", "tape_speed_ok", "imbalance_persist_ok",
        "eligible\":true", "entry_pass\":true", "tradability_ok\":true",
        "provider_not_ready", "runtime_disabled", "not_present", "data_valid\":false",
    ]
    low = text.lower()
    for t in terms:
        c[t] = low.count(t.lower())
    for fam in FAMILIES:
        c[fam] = len(re.findall(rf"\b{fam}\b", text, flags=re.I))
    return c

def summarize_prices(jsons: list[Any]) -> dict[str, Any]:
    fut = []
    call = []
    put = []
    selected = []

    for obj in jsons:
        floats_for_keys(obj, {"fut_ltp", "futures_ltp"}, fut)
        # Conservative broad extraction
        if isinstance(obj, dict):
            raw = json.dumps(obj)
            for pat, bucket in [
                (r'"fut_ltp"\s*:\s*([0-9.]+)', fut),
                (r'"ltp"\s*:\s*([0-9.]+)', selected),
            ]:
                for m in re.finditer(pat, raw):
                    try:
                        bucket.append(float(m.group(1)))
                    except Exception:
                        pass

            # More specific common view paths if present
            try:
                common = obj.get("consumer_view_json")
                if isinstance(common, str):
                    common = json.loads(common)
                if isinstance(common, dict):
                    cv = common.get("common", {})
                    if isinstance(cv, dict):
                        if isinstance(cv.get("futures"), dict) and cv["futures"].get("ltp"):
                            fut.append(float(cv["futures"]["ltp"]))
                        if isinstance(cv.get("call"), dict) and cv["call"].get("ltp"):
                            call.append(float(cv["call"]["ltp"]))
                        if isinstance(cv.get("put"), dict) and cv["put"].get("ltp"):
                            put.append(float(cv["put"]["ltp"]))
                        if isinstance(cv.get("selected_option"), dict) and cv["selected_option"].get("ltp"):
                            selected.append(float(cv["selected_option"]["ltp"]))
            except Exception:
                pass

    def stats(xs: list[float]) -> dict[str, Any]:
        xs = [x for x in xs if x and math.isfinite(x) and x > 0]
        if not xs:
            return {"count": 0}
        return {
            "count": len(xs),
            "first": xs[0],
            "last": xs[-1],
            "min": min(xs),
            "max": max(xs),
            "range": max(xs) - min(xs),
            "net": xs[-1] - xs[0],
            "mean": statistics.mean(xs),
        }

    return {
        "futures": stats(fut),
        "call": stats(call),
        "put": stats(put),
        "selected": stats(selected),
    }

def classify_day(term_counts: Counter, prices: dict[str, Any]) -> dict[str, Any]:
    scores = {}
    scores["MIST"] = (
        term_counts["trend_confirmed"] * 3
        + term_counts["pullback_detected"] * 2
        + term_counts["resume_confirmed"] * 4
    )
    scores["MISB"] = (
        term_counts["shelf_confirmed"] * 2
        + term_counts["breakout_triggered"] * 3
        + term_counts["breakout_accepted"] * 4
    )
    scores["MISC"] = (
        term_counts["compression_detected"] * 2
        + term_counts["directional_breakout_triggered"] * 3
        + term_counts["expansion_accepted"] * 3
        + term_counts["retest_monitor_active"] * 2
    )
    scores["MISR"] = (
        term_counts["fake_break"] * 3
        + term_counts["range_reentry"] * 3
        + term_counts["flow_flip"] * 2
        + term_counts["reversal_impulse"] * 4
    )
    scores["MISO"] = (
        term_counts["burst_detected"] * 4
        + term_counts["aggression_ok"] * 2
        + term_counts["tape_speed_ok"] * 2
        + term_counts["imbalance_persist_ok"] * 2
    )

    blocked = (
        term_counts["provider_not_ready"]
        + term_counts["runtime_disabled"]
        + term_counts["not_present"]
        + term_counts["data_valid\":false"]
    )

    best = max(scores, key=scores.get)
    best_score = scores[best]

    fut_range = prices.get("futures", {}).get("range", 0) or 0
    selected_range = prices.get("selected", {}).get("range", 0) or 0

    if best_score == 0:
        label = "NO_CLEAR_STRATEGY_DAY_FROM_CAPTURE"
    elif blocked > best_score:
        label = f"{best}_LIKE_STRUCTURE_BUT_BLOCKED"
    else:
        label = f"{best}_LIKELY_DAY"

    return {
        "label": label,
        "scores": scores,
        "best_family": best,
        "best_score": best_score,
        "blocker_score": blocked,
        "futures_range": fut_range,
        "selected_option_range": selected_range,
    }

def hypothetical_pnl(prices: dict[str, Any]) -> dict[str, Any]:
    # This is not a strategy fill model. It is only "perfect hindsight 5-point target possible?"
    selected = prices.get("selected", {})
    call = prices.get("call", {})
    put = prices.get("put", {})
    out = {}
    for name, st in [("selected", selected), ("call", call), ("put", put)]:
        if not st or st.get("count", 0) == 0:
            out[name] = {"computable": False}
            continue
        rng = st.get("range", 0) or 0
        out[name] = {
            "computable": True,
            "range_points": rng,
            "five_point_target_possible_in_hindsight": rng >= 5.0,
            "important_warning": "This is NOT strategy PnL. It is only price-range potential without entry qualification.",
        }
    return out

all_text = ""
file_inventory = []
all_jsons = []

for p in FILES:
    text = read_text(p)
    all_text += "\n" + text
    js = extract_jsons(text)
    all_jsons.extend(js)
    file_inventory.append({
        "path": str(p.relative_to(ROOT)),
        "exists": p.exists(),
        "size_mb": round(p.stat().st_size / 1024 / 1024, 3) if p.exists() else 0,
        "json_objects_extracted": len(js),
    })

terms = count_terms(all_text)
prices = summarize_prices(all_jsons)
classification = classify_day(terms, prices)
pnl = hypothetical_pnl(prices)

result = {
    "file_inventory": file_inventory,
    "term_counts": dict(terms),
    "price_summary": prices,
    "strategy_day_classification": classification,
    "hypothetical_range_pnl": pnl,
    "final_note": "If no actual candidate/entry/exit exists, strategy PnL remains not computable. Range PnL is only opportunity potential, not executable strategy PnL.",
}

(OUTDIR / "raw_day_classifier.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

md = []
md.append("# Raw Feed Strategy-Day Classifier")
md.append("")
md.append("## Classification")
md.append("")
md.append(f"```text\n{classification['label']}\n```")
md.append("")
md.append("## Scores")
md.append("")
for k, v in classification["scores"].items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Price Summary")
md.append("")
md.append("```json")
md.append(json.dumps(prices, indent=2))
md.append("```")
md.append("")
md.append("## Hypothetical Range PnL")
md.append("")
md.append("```json")
md.append(json.dumps(pnl, indent=2))
md.append("```")
md.append("")
md.append("## Warning")
md.append("")
md.append("This does not convert HOLD into a real trade. If there was no candidate/entry/exit artifact, real strategy PnL is still not computable.")
md.append("")
(OUTDIR / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print("===== RAW DAY CLASSIFIER COMPLETE =====")
print(f"OUTDIR={OUTDIR}")
print(f"REPORT={OUTDIR / 'REPORT.md'}")
print("")
print((OUTDIR / "REPORT.md").read_text())
