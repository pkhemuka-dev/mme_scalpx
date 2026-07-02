#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROFILE_ID = "MIST_PUT_NEAR_V1"
PROFILE_VERSION = "r38aq_r2"
PROFILE_MODE = "RESEARCH_SHADOW_ONLY"

DEDUP_BUCKET_SEC = 60
REFERENCE_HORIZON_SEC = 300
COST_POINTS = [0.5, 1.0, 1.5, 2.0]

ALLOW_BRANCH = "PUT"
ALLOW_STAGES = {"futures_bias", "pullback"}
BLOCK_BRANCHES = {"CALL"}
BLOCK_STAGES = {"futures_impulse"}

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
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("family_id") == "MIST" and r.get("shadow_only") is True:
                out.append(r)
    return out

def dedup_60s(rows):
    best = {}
    width_ns = DEDUP_BUCKET_SEC * 1_000_000_000

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

        if safe_float(r.get("setup_score"), 0.0) > safe_float(old.get("setup_score"), 0.0):
            best[key] = r

    return list(best.values())

def is_profile_row(r):
    branch = str(r.get("branch_id"))
    stage = str(r.get("failed_stage"))

    if branch in BLOCK_BRANCHES:
        return False
    if stage in BLOCK_STAGES:
        return False
    if branch != ALLOW_BRANCH:
        return False
    if stage not in ALLOW_STAGES:
        return False

    pnl = r.get(f"pnl_points_plus_{REFERENCE_HORIZON_SEC}s")
    if not isinstance(pnl, (int, float)):
        return False

    if safe_int(r.get("entry_ts_ns"), 0) <= 0:
        return False
    if safe_float(r.get("entry_ltp"), 0.0) <= 0:
        return False

    return True

def stats(vals):
    if not vals:
        return {"count": 0}
    return {
        "count": len(vals),
        "avg": round(sum(vals) / len(vals), 6),
        "median": round(statistics.median(vals), 6),
        "win_pct": round(sum(1 for v in vals if v > 0) / len(vals) * 100.0, 4),
        "min": round(min(vals), 6),
        "max": round(max(vals), 6),
    }

def main() -> int:
    if len(sys.argv) != 6:
        print("usage: SCRIPT r38ao_jsonl r38ap_json out_signals_jsonl out_profile_json out_profile_md", file=sys.stderr)
        return 2

    r38ao_jsonl = Path(sys.argv[1])
    r38ap_json = Path(sys.argv[2])
    out_signals = Path(sys.argv[3])
    out_profile = Path(sys.argv[4])
    out_md = Path(sys.argv[5])

    rows = load_rows(r38ao_jsonl)
    deduped = dedup_60s(rows)
    profile_rows = [r for r in deduped if is_profile_row(r)]

    signals = []
    for r in sorted(profile_rows, key=lambda x: safe_int(x.get("entry_ts_ns"), 0)):
        raw_pnl = safe_float(r.get(f"pnl_points_plus_{REFERENCE_HORIZON_SEC}s"), 0.0)
        signal = {
            "schema": "mist_put_near_v1_shadow_signal_r38aq_r2",
            "profile_id": PROFILE_ID,
            "profile_version": PROFILE_VERSION,
            "profile_mode": PROFILE_MODE,
            "source_family": "MIST",
            "source_branch": str(r.get("branch_id")),
            "source_failed_stage": str(r.get("failed_stage")),
            "instrument_token": str(r.get("instrument_token")),
            "option_symbol": str(r.get("option_symbol")),
            "entry_ts_ns": safe_int(r.get("entry_ts_ns"), 0),
            "entry_ltp": safe_float(r.get("entry_ltp"), 0.0),
            "setup_score": safe_float(r.get("setup_score"), 0.0),
            "passed_stages": r.get("passed_stages") if isinstance(r.get("passed_stages"), list) else [],
            "reference_horizon_sec": REFERENCE_HORIZON_SEC,
            "raw_pnl_points_300s": raw_pnl,
            "cost_adjusted_pnl": {str(c): round(raw_pnl - c, 6) for c in COST_POINTS},
            "near_candidate": True,
            "candidate_intent_shadow": True,
            "research_only": True,
            "paper_allowed": False,
            "live_allowed": False,
            "routable_to_risk": False,
            "routable_to_execution": False,
            "order_allowed": False,
            "activation_allowed": False,
            "why_included": "PUT only; failed_stage futures_bias/pullback; 60s dedup; 300s horizon; derived from R38AP positive segment.",
            "why_not_tradeable": "single-day evidence only; slow 300s horizon; needs multi-day validation and explicit gate before any route change."
        }
        signals.append(signal)

    out_signals.parent.mkdir(parents=True, exist_ok=True)
    with out_signals.open("w", encoding="utf-8") as f:
        for s in signals:
            f.write(json.dumps(s, sort_keys=True) + "\n")

    raw_300 = [s["raw_pnl_points_300s"] for s in signals]
    cost_stats = {
        str(c): stats([s["cost_adjusted_pnl"][str(c)] for s in signals])
        for c in COST_POINTS
    }

    profile = {
        "schema": "mist_put_near_v1_profile_r38aq_r2",
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "profile_mode": PROFILE_MODE,
        "source_r38ao_jsonl": str(r38ao_jsonl),
        "source_r38ap_json": str(r38ap_json),
        "raw_mist_shadow_rows": len(rows),
        "dedup_bucket_sec": DEDUP_BUCKET_SEC,
        "dedup_rows": len(deduped),
        "shadow_signal_count": len(signals),
        "allowed": {
            "branch": ALLOW_BRANCH,
            "failed_stages": sorted(ALLOW_STAGES),
            "reference_horizon_sec": REFERENCE_HORIZON_SEC
        },
        "blocked": {
            "branches": sorted(BLOCK_BRANCHES),
            "failed_stages": sorted(BLOCK_STAGES),
            "paper": True,
            "live": True,
            "risk_execution_route": True,
            "broker_order": True
        },
        "stage_counts": dict(Counter(s["source_failed_stage"] for s in signals)),
        "raw_300s_stats": stats(raw_300),
        "cost_adjusted_300s_stats": cost_stats,
        "decision": {
            "research_profile_created": len(signals) > 0,
            "production_patch_allowed_now": False,
            "paper_allowed_now": False,
            "live_allowed_now": False,
            "next_step": "R38AR multi-day validation of MIST_PUT_NEAR_V1 before any candidate-route patch."
        },
        "safety": {
            "read_only": True,
            "production_patch": False,
            "threshold_changed": False,
            "redis_write": False,
            "paper_allowed": False,
            "live_allowed": False,
            "order_allowed": False,
            "risk_execution_route_changed": False
        }
    }

    out_profile.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")

    md = []
    md.append("# R38AQ-R2 MIST_PUT_NEAR_V1 evidence-derived shadow profile")
    md.append("")
    md.append("## Verdict")
    md.append("")
    md.append("- Profile created: `{}`".format(len(signals) > 0))
    md.append("- Profile ID: `MIST_PUT_NEAR_V1`")
    md.append("- Mode: `RESEARCH_SHADOW_ONLY`")
    md.append("- Production patch: `false`")
    md.append("- Paper/live/risk/execution/order route: `false`")
    md.append("")
    md.append("## Why this profile exists")
    md.append("")
    md.append("R38AP showed the broad MIST near-candidate set is not good enough, but PUT-side 300s segments survived cost/dedup better than CALL/futures-impulse.")
    md.append("")
    md.append("## Rules")
    md.append("")
    md.append("- Include only `PUT`")
    md.append("- Include only failed_stage in `futures_bias,pullback`")
    md.append("- Exclude `CALL`")
    md.append("- Exclude `futures_impulse`")
    md.append("- Dedup bucket: `60s`")
    md.append("- Reference horizon: `300s`")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append("- raw_mist_shadow_rows: `{}`".format(len(rows)))
    md.append("- dedup_rows: `{}`".format(len(deduped)))
    md.append("- shadow_signal_count: `{}`".format(len(signals)))
    md.append("- stage_counts: `{}`".format(profile["stage_counts"]))
    md.append("- raw_300s_stats: `{}`".format(profile["raw_300s_stats"]))
    md.append("- cost_adjusted_300s_stats: `{}`".format(profile["cost_adjusted_300s_stats"]))
    md.append("")
    md.append("## Decision")
    md.append("")
    md.append("This is **not paper-ready**. It is a research shadow profile only. Next step is multi-day validation, not live/paper.")
    out_md.write_text("\n".join(md), encoding="utf-8")

    print("profile_id=" + PROFILE_ID)
    print("raw_rows=" + str(len(rows)))
    print("dedup_rows=" + str(len(deduped)))
    print("shadow_signal_count=" + str(len(signals)))
    print("stage_counts=" + json.dumps(profile["stage_counts"], sort_keys=True))
    print("raw_300s_stats=" + json.dumps(profile["raw_300s_stats"], sort_keys=True))
    print("cost_adjusted_300s_stats=" + json.dumps(profile["cost_adjusted_300s_stats"], sort_keys=True))
    print("out_signals=" + str(out_signals))
    print("out_profile=" + str(out_profile))
    print("out_md=" + str(out_md))
    print("")
    print("\n".join(md))
    return 0 if signals else 3

if __name__ == "__main__":
    raise SystemExit(main())
