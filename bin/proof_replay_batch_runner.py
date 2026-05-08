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

from app.mme_scalpx.replay.batch_runner import (  # noqa: E402
    REPLAY_BATCH_SUPPORTED_RUN_SCOPES,
    build_date_list_plan,
    build_date_range_plan,
    build_intraday_window_plan,
    build_scenario_matrix_plan,
    build_single_day_plan,
    replay_batch_profile_manifest,
    replay_batch_runner_contract_summary,
    simulate_replay_batch_plan,
    validate_replay_batch_plan,
)
from app.mme_scalpx.replay.scenarios import REPLAY_REQUIRED_SCENARIOS  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_batch_runner.json")
    args = parser.parse_args()

    contract_file = ROOT / "etc/replay/schemas/replay_batch_runner_contract_v1.json"
    manifest_file = ROOT / "etc/replay/batches/replay_batch_profile_manifest_v1.json"

    contract = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}

    plans = {
        "single_day": build_single_day_plan(day="2026-05-01"),
        "date_range": build_date_range_plan(start_date="2026-05-01", end_date="2026-05-03"),
        "date_list": build_date_list_plan(dates=("2026-05-01", "2026-05-03")),
        "intraday_window": build_intraday_window_plan(day="2026-05-01", start_time="09:30:00", end_time="10:30:00"),
        "scenario_matrix": build_scenario_matrix_plan(dates=("2026-05-01",), scenarios=REPLAY_REQUIRED_SCENARIOS),
    }

    validations = {name: validate_replay_batch_plan(plan) for name, plan in plans.items()}
    simulations = {name: simulate_replay_batch_plan(plan) for name, plan in plans.items()}

    scopes_ok = set(plans) == set(REPLAY_BATCH_SUPPORTED_RUN_SCOPES) == set(contract.get("supported_run_scopes", ()))
    validations_ok = all(v.get("ok") is True for v in validations.values())
    result_counts_ok = all(
        simulations[name].get("result_count") == plans[name].get("request_count")
        for name in plans
    )

    single_day_ok = plans["single_day"]["request_count"] == 1
    date_range_ok = plans["date_range"]["request_count"] == 3
    date_list_ok = plans["date_list"]["request_count"] == 2
    intraday_window_ok = (
        plans["intraday_window"]["request_count"] == 1
        and plans["intraday_window"]["requests"][0]["start_time"] == "09:30:00"
        and plans["intraday_window"]["requests"][0]["end_time"] == "10:30:00"
    )
    scenario_matrix_ok = (
        plans["scenario_matrix"]["request_count"] == len(REPLAY_REQUIRED_SCENARIOS)
        and simulations["scenario_matrix"]["scenario_count"] == len(REPLAY_REQUIRED_SCENARIOS)
    )

    no_live_ok = (
        contract.get("paper_armed_approved") is False
        and contract.get("live_trading_approved") is False
        and contract.get("execution_arming_created") is False
        and contract.get("broker_calls_allowed") is False
        and contract.get("live_redis_writes_allowed") is False
        and contract.get("production_doctrine_changed") is False
        and manifest.get("paper_armed_approved") is False
        and manifest.get("live_trading_approved") is False
        and all(plan.get("paper_armed_approved") is False for plan in plans.values())
        and all(sim.get("real_order_sent") is False for sim in simulations.values())
        and all(sim.get("broker_calls_executed") is False for sim in simulations.values())
        and all(sim.get("live_redis_writes_executed") is False for sim in simulations.values())
    )

    runner_summary = replay_batch_runner_contract_summary()
    manifest_runtime = replay_batch_profile_manifest()

    batch_runner_ok = bool(
        contract_file.exists()
        and manifest_file.exists()
        and scopes_ok
        and validations_ok
        and result_counts_ok
        and single_day_ok
        and date_range_ok
        and date_list_ok
        and intraday_window_ok
        and scenario_matrix_ok
        and no_live_ok
        and runner_summary.get("paper_armed_approved") is False
        and manifest_runtime.get("paper_armed_approved") is False
    )

    proof = {
        "schema_version": "proof_replay_batch_runner_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "batch_runner_ok": batch_runner_ok,
        "contract_file_exists": contract_file.exists(),
        "manifest_file_exists": manifest_file.exists(),
        "scopes_ok": scopes_ok,
        "validations_ok": validations_ok,
        "result_counts_ok": result_counts_ok,
        "single_day_ok": single_day_ok,
        "date_range_ok": date_range_ok,
        "date_list_ok": date_list_ok,
        "intraday_window_ok": intraday_window_ok,
        "scenario_matrix_ok": scenario_matrix_ok,
        "scenario_matrix_count": plans["scenario_matrix"]["request_count"],
        "no_live_ok": no_live_ok,
        "plans": plans,
        "validations": validations,
        "simulation_summaries": {
            name: {
                "scope": sim.get("scope"),
                "request_count": sim.get("request_count"),
                "result_count": sim.get("result_count"),
                "scenario_count": sim.get("scenario_count"),
                "total_shadow_pnl": sim.get("total_shadow_pnl"),
                "real_order_sent": sim.get("real_order_sent"),
            }
            for name, sim in simulations.items()
        },
        "runner_summary": runner_summary,
        "manifest_runtime": manifest_runtime,
        "batch_runner_shape": "PROVEN_BY_27K",
        "artifact_materialization": "NOT_PROVEN_BY_THIS_PROOF",
        "full_live_replay_parity": "NOT_PROVEN_IN_27K",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if batch_runner_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "batch_runner_ok": batch_runner_ok,
        "single_day_ok": single_day_ok,
        "date_range_ok": date_range_ok,
        "date_list_ok": date_list_ok,
        "intraday_window_ok": intraday_window_ok,
        "scenario_matrix_ok": scenario_matrix_ok,
        "scenario_matrix_count": proof["scenario_matrix_count"],
        "no_live_ok": no_live_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if batch_runner_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
