#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any

HORIZONS = [15, 30, 60, 120, 180, 300]
COSTS = [0.0, 0.5, 1.0, 1.5, 2.0]
BUCKETS_SEC = [0, 15, 30, 60, 120, 300]

def safe_float(v: Any, d: float = 0.0) -> float:
    try:
        if v in (None, ""):
            return d
        return float(v)
    except Exception:
        return d

def safe_int(v: Any, d: int = 0) -> int:
    try:
        if v in (None, ""):
            return d
        return int(float(v))
    except Exception:
        return d

def load_rows(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("family_id") == "MIST" and r.get("shadow_only") is True:
                rows.append(r)
    return rows

def dedup_rows(rows, bucket_sec: int):
    if bucket_sec <= 0:
        return list(rows)

    best = {}
    width_ns = bucket_sec * 1_000_000_000
    for r in rows:
        ts = safe_int(r.get("entry_ts_ns"), 0)
        token = str(r.get("instrument_token"))
        branch = str(r.get("branch_id"))
        stage = str(r.get("failed_stage"))
        bucket = ts // width_ns if width_ns else ts
        key = (bucket, token, branch, stage)

        old = best.get(key)
        if old is None:
            best[key] = r
            continue

        # keep strongest setup row inside same bucket
        if safe_float(r.get("setup_score"), 0.0) > safe_float(old.get("setup_score"), 0.0):
            best[key] = r

    return list(best.values())

def segment_match(r, segment: str):
    branch = str(r.get("branch_id"))
    stage = str(r.get("failed_stage"))

    if segment == "ALL":
        return True
    if segment == "CALL":
        return branch == "CALL"
    if segment == "PUT":
        return branch == "PUT"
    if segment == "PULLBACK":
        return stage == "pullback"
    if segment == "FUTURES_IMPULSE":
        return stage == "futures_impulse"
    if segment == "FUTURES_BIAS":
        return stage == "futures_bias"
    if segment == "PUT_PULLBACK":
        return branch == "PUT" and stage == "pullback"
    if segment == "PUT_FUTURES_BIAS":
        return branch == "PUT" and stage == "futures_bias"
    if segment == "CALL_FUTURES_IMPULSE":
        return branch == "CALL" and stage == "futures_impulse"
    return False

def stats(vals):
    if not vals:
        return {"count": 0}
    return {
        "count": len(vals),
        "avg": round(sum(vals) / len(vals), 6),
        "median": round(statistics.median(vals), 6),
        "win_pct": round(sum(1 for x in vals if x > 0) / len(vals) * 100.0, 4),
        "min": round(min(vals), 6),
        "max": round(max(vals), 6),
    }

def main() -> int:
    if len(sys.argv) != 4:
        print("usage: SCRIPT r38ao_jsonl out_json out_md", file=sys.stderr)
        return 2

    src, out_json, out_md = map(Path, sys.argv[1:])
    rows = load_rows(src)

    segments = [
        "ALL",
        "CALL",
        "PUT",
        "PULLBACK",
        "FUTURES_IMPULSE",
        "FUTURES_BIAS",
        "PUT_PULLBACK",
        "PUT_FUTURES_BIAS",
        "CALL_FUTURES_IMPULSE",
    ]

    result = {
        "schema": "r38ap_mist_near_cost_dedup_segment_audit_v1",
        "source": str(src),
        "raw_rows": len(rows),
        "raw_branch_counts": dict(Counter(str(r.get("branch_id")) for r in rows)),
        "raw_stage_counts": dict(Counter(str(r.get("failed_stage")) for r in rows)),
        "segments": {},
        "safety": {
            "read_only": True,
            "patch_attempted": False,
            "paper_allowed": False,
            "live_allowed": False,
            "order_attempt": False,
            "redis_write": False,
        },
    }

    best_candidates = []

    for bucket in BUCKETS_SEC:
        drows = dedup_rows(rows, bucket)
        bucket_key = f"dedup_{bucket}s" if bucket else "no_dedup"
        result["segments"][bucket_key] = {
            "rows": len(drows),
            "branch_counts": dict(Counter(str(r.get("branch_id")) for r in drows)),
            "stage_counts": dict(Counter(str(r.get("failed_stage")) for r in drows)),
            "detail": {},
        }

        for seg in segments:
            srows = [r for r in drows if segment_match(r, seg)]
            result["segments"][bucket_key]["detail"][seg] = {}

            for h in HORIZONS:
                raw_vals = [
                    r.get(f"pnl_points_plus_{h}s")
                    for r in srows
                    if isinstance(r.get(f"pnl_points_plus_{h}s"), (int, float))
                ]

                result["segments"][bucket_key]["detail"][seg][f"{h}s"] = {
                    "raw": stats(raw_vals),
                    "cost_adjusted": {},
                }

                for cost in COSTS:
                    vals = [v - cost for v in raw_vals]
                    st = stats(vals)
                    result["segments"][bucket_key]["detail"][seg][f"{h}s"]["cost_adjusted"][str(cost)] = st

                    if (
                        st.get("count", 0) >= 20
                        and st.get("avg", -999) > 0
                        and st.get("win_pct", 0) >= 52
                    ):
                        best_candidates.append({
                            "bucket": bucket_key,
                            "segment": seg,
                            "horizon": f"{h}s",
                            "cost": cost,
                            "stats": st,
                        })

    # rank conservative: positive after cost, higher count, win, avg
    best_candidates.sort(
        key=lambda x: (
            x["cost"],
            x["stats"].get("count", 0),
            x["stats"].get("win_pct", 0),
            x["stats"].get("avg", 0),
        ),
        reverse=True,
    )
    result["best_candidates"] = best_candidates[:50]

    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    lines = []
    lines.append("# R38AP MIST near-candidate cost/dedup segment audit\n")
    lines.append(f"- source: `{src}`")
    lines.append(f"- raw_rows: `{len(rows)}`")
    lines.append("")
    lines.append("## Best conservative positive segments")
    if best_candidates:
        for i, b in enumerate(best_candidates[:30], 1):
            s = b["stats"]
            lines.append(
                f"{i}. bucket={b['bucket']} segment={b['segment']} horizon={b['horizon']} "
                f"cost={b['cost']} count={s.get('count')} avg={s.get('avg')} "
                f"median={s.get('median')} win_pct={s.get('win_pct')}"
            )
    else:
        lines.append("No segment survived the conservative criteria: count>=20, avg>0 after cost, win_pct>=52.")

    lines.append("")
    lines.append("## Key raw/dedup summaries")
    for bucket_key, bd in result["segments"].items():
        lines.append(f"### {bucket_key} rows={bd['rows']}")
        for seg in ["ALL", "PUT", "CALL", "PULLBACK", "PUT_PULLBACK", "FUTURES_IMPULSE"]:
            lines.append(f"- {seg}:")
            for h in [60, 120, 180, 300]:
                raw = bd["detail"][seg][f"{h}s"]["raw"]
                c05 = bd["detail"][seg][f"{h}s"]["cost_adjusted"]["0.5"]
                c10 = bd["detail"][seg][f"{h}s"]["cost_adjusted"]["1.0"]
                lines.append(
                    f"  - {h}s raw count={raw.get('count')} avg={raw.get('avg')} win={raw.get('win_pct')} | "
                    f"cost0.5 avg={c05.get('avg')} win={c05.get('win_pct')} | "
                    f"cost1.0 avg={c10.get('avg')} win={c10.get('win_pct')}"
                )
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    print("raw_rows=" + str(len(rows)))
    print("best_candidate_count=" + str(len(best_candidates)))
    print("out_json=" + str(out_json))
    print("out_md=" + str(out_md))
    print("")
    print("\n".join(lines[:160]))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
