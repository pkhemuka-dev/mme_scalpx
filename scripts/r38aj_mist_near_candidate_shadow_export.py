#!/usr/bin/env python3
"""
R38AJ MIST near-candidate shadow exporter.

Safety:
- Reads sealed features.redisraw.gz only.
- Writes audit files only.
- Does not import broker/risk/execution.
- Does not write Redis.
- Does not start replay/paper/live.
- Does not change strategy thresholds.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

FAMILY = "MIST"
VALID_BRANCHES = {"CALL", "PUT"}
LATE_STAGE_FAILURES = {
    "pullback",
    "futures_impulse",
    "futures_bias",
    "score_below_threshold",
    "futures_impulse_insufficient",
}
decoder = json.JSONDecoder()


def safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v in (None, ""):
            return default
        return float(v)
    except Exception:
        return default


def safe_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on", "pass", "passed"}


def as_map(v: Any) -> dict[str, Any]:
    return dict(v) if isinstance(v, Mapping) else {}


def iter_json_objects(text: str):
    s = text.strip()
    if not s:
        return
    if s.startswith("{"):
        try:
            yield json.loads(s)
            return
        except Exception:
            pass

    for m in re.finditer(r"\{", text):
        start = m.start()
        try:
            obj, _ = decoder.raw_decode(text[start:])
            if isinstance(obj, dict):
                yield obj
        except Exception:
            continue


def walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk(x)


def extract_candidate(obj: Mapping[str, Any]) -> dict[str, Any] | None:
    fid = str(obj.get("family_id") or obj.get("doctrine_id") or "").upper()
    if fid != FAMILY:
        return None

    branch = str(obj.get("branch_id") or obj.get("side") or "").upper()
    if branch not in VALID_BRANCHES:
        return None

    eligible = safe_bool(obj.get("eligible"))
    if eligible:
        return None

    failed_stage = str(
        obj.get("failed_stage")
        or obj.get("batch9_freeze_blocked_reason")
        or obj.get("pre_batch9_failed_stage")
        or ""
    ).strip()

    if failed_stage not in LATE_STAGE_FAILURES:
        return None

    selected = as_map(obj.get("selected_features"))
    option = as_map(obj.get("option_features"))
    trad = as_map(obj.get("tradability") or obj.get("tradability_surface"))

    selected_present = safe_bool(selected.get("present"))
    option_present = safe_bool(option.get("present"))
    trad_present = safe_bool(trad.get("present"))
    trad_pass = safe_bool(obj.get("option_tradability_pass") or obj.get("tradability_pass") or trad.get("entry_pass") or trad.get("tradability_ok"))
    provider_ready = safe_bool(obj.get("provider_ready"))

    token = (
        selected.get("option_token")
        or selected.get("instrument_token")
        or option.get("option_token")
        or option.get("instrument_token")
        or ""
    )
    symbol = (
        selected.get("trading_symbol")
        or selected.get("option_symbol")
        or option.get("trading_symbol")
        or option.get("option_symbol")
        or ""
    )

    # This is shadow-only. Keep it conservative:
    # require provider/tradability/selected option to exist, and exactly one known late-stage blocker.
    if not (selected_present and option_present and trad_present and trad_pass and provider_ready and token and symbol):
        return None

    passed = obj.get("passed_stages") or []
    if not isinstance(passed, list):
        passed = []

    setup_score = safe_float(obj.get("setup_score"), 0.0)

    # Do not treat low quality rows as near-candidates.
    if len(passed) < 4:
        return None

    event_basis = json.dumps(
        {
            "family_id": FAMILY,
            "branch_id": branch,
            "failed_stage": failed_stage,
            "token": str(token),
            "symbol": str(symbol),
            "setup_score": round(setup_score, 6),
            "passed_stages": passed,
        },
        sort_keys=True,
        default=str,
    )
    event_id = "R38AJ_MIST_NEAR|" + hashlib.sha256(event_basis.encode()).hexdigest()[:20]

    return {
        "schema": "r38aj_mist_near_candidate_shadow_v1",
        "family_id": FAMILY,
        "branch_id": branch,
        "side": branch,
        "shadow_only": True,
        "routable_to_risk": False,
        "routable_to_execution": False,
        "paper_allowed": False,
        "live_allowed": False,
        "eligible": False,
        "near_candidate": True,
        "failed_stage": failed_stage,
        "setup_score": setup_score,
        "passed_stage_count": len(passed),
        "passed_stages": passed,
        "provider_ready": provider_ready,
        "selected_present": selected_present,
        "option_present": option_present,
        "tradability_present": trad_present,
        "tradability_pass": trad_pass,
        "instrument_token": str(token),
        "option_symbol": str(symbol),
        "ltp": safe_float(selected.get("ltp") or option.get("ltp"), 0.0),
        "best_bid": safe_float(selected.get("best_bid") or option.get("best_bid"), 0.0),
        "best_ask": safe_float(selected.get("best_ask") or option.get("best_ask"), 0.0),
        "strike": safe_float(selected.get("strike") or option.get("strike"), 0.0),
        "event_id": event_id,
        "safety_note": "shadow_only_near_candidate_not_order_routable",
    }


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: r38aj_mist_near_candidate_shadow_export.py FEATURES_GZ OUT_JSONL OUT_SUMMARY_JSON", file=sys.stderr)
        return 2

    features_gz = Path(sys.argv[1])
    out_jsonl = Path(sys.argv[2])
    out_summary = Path(sys.argv[3])

    rows: list[dict[str, Any]] = []
    line_count = 0
    json_count = 0

    with gzip.open(features_gz, "rt", errors="ignore") as f:
        for line in f:
            line_count += 1
            if "MIST" not in line:
                continue
            for root in iter_json_objects(line):
                json_count += 1
                for obj in walk(root):
                    if isinstance(obj, dict):
                        row = extract_candidate(obj)
                        if row:
                            rows.append(row)

    # De-duplicate by event_id.
    seen = set()
    dedup = []
    for r in sorted(rows, key=lambda x: (x.get("setup_score", 0), x.get("passed_stage_count", 0)), reverse=True):
        eid = r["event_id"]
        if eid in seen:
            continue
        seen.add(eid)
        dedup.append(r)

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as fp:
        for r in dedup:
            fp.write(json.dumps(r, sort_keys=True, default=str) + "\n")

    stage_counts = Counter(r["failed_stage"] for r in dedup)
    branch_counts = Counter(r["branch_id"] for r in dedup)

    summary = {
        "schema": "r38aj_mist_near_candidate_shadow_summary_v1",
        "source": str(features_gz),
        "line_count": line_count,
        "json_objects_seen": json_count,
        "raw_near_rows": len(rows),
        "dedup_near_rows": len(dedup),
        "stage_counts": dict(stage_counts),
        "branch_counts": dict(branch_counts),
        "top_rows": dedup[:25],
        "safety": {
            "shadow_only": True,
            "routable_to_risk": False,
            "routable_to_execution": False,
            "paper_allowed": False,
            "live_allowed": False,
            "redis_write": False,
            "order_attempt": False,
        },
    }

    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print("features_gz=" + str(features_gz))
    print("out_jsonl=" + str(out_jsonl))
    print("out_summary=" + str(out_summary))
    print("raw_near_rows=" + str(len(rows)))
    print("dedup_near_rows=" + str(len(dedup)))
    print("stage_counts=" + json.dumps(dict(stage_counts), sort_keys=True))
    print("branch_counts=" + json.dumps(dict(branch_counts), sort_keys=True))
    print("top_rows:")
    for r in dedup[:15]:
        print(
            f"{r['family_id']}/{r['branch_id']} score={r['setup_score']} "
            f"passed={r['passed_stage_count']} failed={r['failed_stage']} "
            f"symbol={r['option_symbol']} token={r['instrument_token']} "
            f"shadow_only={r['shadow_only']}"
        )

    return 0 if dedup else 3


if __name__ == "__main__":
    raise SystemExit(main())
