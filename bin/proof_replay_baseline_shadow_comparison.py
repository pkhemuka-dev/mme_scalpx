#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.batch_runner import build_scenario_matrix_plan, simulate_replay_batch_plan  # noqa: E402
from app.mme_scalpx.replay.report_exporter import build_baseline_shadow_comparison  # noqa: E402
from app.mme_scalpx.replay.scenarios import REPLAY_REQUIRED_SCENARIOS  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_baseline_shadow_comparison.json")
    args = parser.parse_args()

    baseline_plan = build_scenario_matrix_plan(dates=("2026-05-01",), scenarios=("full_fill",))
    shadow_plan = build_scenario_matrix_plan(dates=("2026-05-01",), scenarios=REPLAY_REQUIRED_SCENARIOS)

    baseline_result = simulate_replay_batch_plan(baseline_plan)
    shadow_result = simulate_replay_batch_plan(shadow_plan)

    comparison = build_baseline_shadow_comparison(
        baseline_label="baseline_full_fill",
        baseline_result=baseline_result,
        shadow_label="shadow_scenario_matrix",
        shadow_result=shadow_result,
    )

    comparison_ok = bool(
        comparison.get("schema_version") == "replay_baseline_shadow_comparison_v1"
        and comparison.get("baseline_result_count") == 1
        and comparison.get("shadow_result_count") == len(REPLAY_REQUIRED_SCENARIOS)
        and comparison.get("delta_result_count") == len(REPLAY_REQUIRED_SCENARIOS) - 1
        and isinstance(comparison.get("delta_shadow_pnl"), (int, float))
        and bool(comparison.get("comparison_reproducibility_hash"))
        and comparison.get("paper_armed_approved") is False
        and comparison.get("live_trading_approved") is False
        and comparison.get("execution_arming_created") is False
        and comparison.get("real_order_sent") is False
        and comparison.get("broker_calls_executed") is False
        and comparison.get("live_redis_writes_executed") is False
        and comparison.get("production_doctrine_changed") is False
    )

    proof = {
        "schema_version": "proof_replay_baseline_shadow_comparison_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_shadow_comparison_ok": comparison_ok,
        "baseline_result_count": comparison.get("baseline_result_count"),
        "shadow_result_count": comparison.get("shadow_result_count"),
        "delta_result_count": comparison.get("delta_result_count"),
        "delta_shadow_pnl": comparison.get("delta_shadow_pnl"),
        "comparison_reproducibility_hash_present": bool(comparison.get("comparison_reproducibility_hash")),
        "comparison": comparison,
        "baseline_shadow_comparison_shape": "PROVEN_BY_27L",
        "full_report_semantic_accuracy": "NOT_PROVEN_IN_27L",
        "full_live_replay_parity": "NOT_PROVEN_IN_27L",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if comparison_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "baseline_shadow_comparison_ok": comparison_ok,
        "baseline_result_count": proof["baseline_result_count"],
        "shadow_result_count": proof["shadow_result_count"],
        "delta_result_count": proof["delta_result_count"],
        "comparison_reproducibility_hash_present": proof["comparison_reproducibility_hash_present"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if comparison_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
