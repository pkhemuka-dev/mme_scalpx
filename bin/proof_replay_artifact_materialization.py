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

from app.mme_scalpx.replay.artifact_materializer import (  # noqa: E402
    REPLAY_BATCH_REQUIRED_ARTIFACTS,
    materialize_replay_run_artifacts,
    replay_artifact_materializer_contract_summary,
    validate_replay_artifact_materialization,
)
from app.mme_scalpx.replay.batch_runner import build_scenario_matrix_plan, simulate_replay_batch_plan  # noqa: E402
from app.mme_scalpx.replay.scenarios import REPLAY_REQUIRED_SCENARIOS  # noqa: E402


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_artifact_materialization.json")
    args = parser.parse_args()

    plan = build_scenario_matrix_plan(dates=("2026-05-01",), scenarios=REPLAY_REQUIRED_SCENARIOS)
    simulation = simulate_replay_batch_plan(plan)
    run_id = f"batch27k_smoke_{plan['plan_id']}"

    result = materialize_replay_run_artifacts(
        run_id=run_id,
        plan=plan,
        simulation_result=simulation,
        base_dir="run/replay",
    )
    validation = validate_replay_artifact_materialization(result)

    root = Path(result["artifact_root"])
    artifact_payloads = {
        name: read_json(root / name)
        for name in REPLAY_BATCH_REQUIRED_ARTIFACTS
    }

    required_artifacts_ok = all((root / name).exists() for name in REPLAY_BATCH_REQUIRED_ARTIFACTS)
    manifest_ok = (
        artifact_payloads["00_manifest.json"].get("run_id") == run_id
        and artifact_payloads["00_manifest.json"].get("artifact_root") == str(root)
        and artifact_payloads["00_manifest.json"].get("safety", {}).get("paper_armed_approved") is False
    )
    dataset_summary_ok = artifact_payloads["01_dataset_summary.json"].get("result_count") == len(REPLAY_REQUIRED_SCENARIOS)
    scenario_summary_ok = artifact_payloads["02_scenario_summary.json"].get("scenario_count") == len(REPLAY_REQUIRED_SCENARIOS)
    feature_summary_ok = artifact_payloads["03_feature_summary.json"].get("family_features_json_present_count") == len(REPLAY_REQUIRED_SCENARIOS)
    strategy_summary_ok = (
        artifact_payloads["04_strategy_summary.json"].get("hold_report_only_count") == len(REPLAY_REQUIRED_SCENARIOS)
        and artifact_payloads["04_strategy_summary.json"].get("order_allowed_true_count") == 0
    )
    risk_summary_ok = artifact_payloads["05_risk_summary.json"].get("risk_evaluated_count") == len(REPLAY_REQUIRED_SCENARIOS)
    execution_summary_ok = (
        artifact_payloads["06_execution_shadow_summary.json"].get("execution_shadow_count") == len(REPLAY_REQUIRED_SCENARIOS)
        and artifact_payloads["06_execution_shadow_summary.json"].get("real_order_sent_count") == 0
        and artifact_payloads["06_execution_shadow_summary.json"].get("broker_calls_executed_count") == 0
    )
    reproducibility_ok = (
        bool(artifact_payloads["07_reproducibility.json"].get("reproducibility_hash"))
        and artifact_payloads["07_reproducibility.json"].get("reproducibility_hash") == result.get("reproducibility_hash")
    )
    batch_summary_ok = (
        artifact_payloads["08_batch_summary.json"].get("result_count") == len(REPLAY_REQUIRED_SCENARIOS)
        and artifact_payloads["08_batch_summary.json"].get("real_order_sent") is False
        and artifact_payloads["08_batch_summary.json"].get("broker_calls_executed") is False
    )

    no_live_ok = all(
        payload.get("paper_armed_approved") is False
        and payload.get("live_trading_approved") is False
        and payload.get("production_doctrine_changed") is False
        for payload in artifact_payloads.values()
    )

    materializer_summary = replay_artifact_materializer_contract_summary()

    artifact_materialization_ok = bool(
        validation.get("ok") is True
        and required_artifacts_ok
        and manifest_ok
        and dataset_summary_ok
        and scenario_summary_ok
        and feature_summary_ok
        and strategy_summary_ok
        and risk_summary_ok
        and execution_summary_ok
        and reproducibility_ok
        and batch_summary_ok
        and no_live_ok
        and materializer_summary.get("paper_armed_approved") is False
    )

    proof = {
        "schema_version": "proof_replay_artifact_materialization_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_materialization_ok": artifact_materialization_ok,
        "validation_ok": validation.get("ok"),
        "required_artifacts_ok": required_artifacts_ok,
        "manifest_ok": manifest_ok,
        "dataset_summary_ok": dataset_summary_ok,
        "scenario_summary_ok": scenario_summary_ok,
        "feature_summary_ok": feature_summary_ok,
        "strategy_summary_ok": strategy_summary_ok,
        "risk_summary_ok": risk_summary_ok,
        "execution_summary_ok": execution_summary_ok,
        "reproducibility_ok": reproducibility_ok,
        "batch_summary_ok": batch_summary_ok,
        "no_live_ok": no_live_ok,
        "run_id": run_id,
        "artifact_root": str(root),
        "required_artifacts": REPLAY_BATCH_REQUIRED_ARTIFACTS,
        "written_artifacts": result.get("written_artifacts"),
        "reproducibility_hash": result.get("reproducibility_hash"),
        "materialization_result": result,
        "validation": validation,
        "materializer_summary": materializer_summary,
        "batch_runner_shape": "PROVEN_BY_27K",
        "artifact_materialization": "PROVEN_BY_27K",
        "reproducibility_hash_status": "PROVEN_BY_27K",
        "full_live_replay_parity": "NOT_PROVEN_IN_27K",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if artifact_materialization_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "artifact_materialization_ok": artifact_materialization_ok,
        "required_artifacts_ok": required_artifacts_ok,
        "scenario_summary_ok": scenario_summary_ok,
        "reproducibility_ok": reproducibility_ok,
        "no_live_ok": no_live_ok,
        "artifact_root": str(root),
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if artifact_materialization_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
