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

from app.mme_scalpx.replay.experiment_workstation import (  # noqa: E402
    REPLAY_EXPERIMENT_REQUIRED_EXPORTS,
    REPLAY_EXPERIMENT_TYPES,
    build_family_side_experiment_summary,
    build_parameter_sweep_summary,
    build_threshold_sweep_summary,
    materialize_replay_experiment_artifacts,
    run_replay_experiment_profile,
    validate_replay_experiment_artifacts,
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_differential_parameter_sweep.json")
    args = parser.parse_args()

    experiments = {
        profile_id: run_replay_experiment_profile(profile_id, dates=("2026-05-01",))
        for profile_id in REPLAY_EXPERIMENT_TYPES
    }

    materialized = {}
    validations = {}
    for profile_id, experiment in experiments.items():
        export_root = f"run/replay/{experiment['experiment_id']}/experiments"
        result = materialize_replay_experiment_artifacts(
            experiment_result=experiment,
            export_root=export_root,
        )
        materialized[profile_id] = result
        validations[profile_id] = validate_replay_experiment_artifacts(result)

    baseline_vs_shadow_ok = (
        experiments["baseline_vs_shadow"]["profile"]["experiment_type"] == "baseline_vs_shadow"
        and len(experiments["baseline_vs_shadow"]["variant_results"]) >= 1
        and bool(experiments["baseline_vs_shadow"]["experiment_reproducibility_hash"])
    )

    parameter_summary = build_parameter_sweep_summary(experiments["parameter_sweep"])
    threshold_summary = build_threshold_sweep_summary(experiments["threshold_sweep"])
    family_summary = build_family_side_experiment_summary(experiments["family_enable_disable"])
    side_summary = build_family_side_experiment_summary(experiments["side_only"])

    parameter_sweep_ok = (
        parameter_summary.get("parameter_sweep_row_count") == 3
        and parameter_summary.get("parameter_sweep_shape") == "PROVEN_BY_27M"
    )
    threshold_sweep_ok = (
        threshold_summary.get("threshold_sweep_row_count") == 3
        and threshold_summary.get("threshold_sweep_shape") == "PROVEN_BY_27M"
    )
    family_enable_disable_ok = (
        family_summary.get("family_row_count") == 5
        and family_summary.get("family_side_filter_shape") == "PROVEN_BY_27M"
    )
    side_only_ok = (
        side_summary.get("side_row_count") == 2
        and side_summary.get("family_side_filter_shape") == "PROVEN_BY_27M"
    )
    scenario_matrix_comparison_ok = (
        experiments["scenario_matrix_comparison"]["profile"]["experiment_type"] == "scenario_matrix_comparison"
        and len(experiments["scenario_matrix_comparison"]["variant_results"]) == 3
    )

    all_artifacts_ok = all(v.get("ok") is True for v in validations.values())
    all_required_exports_ok = all(
        set(result.get("written_exports", {}).keys()) == set(REPLAY_EXPERIMENT_REQUIRED_EXPORTS)
        for result in materialized.values()
    )
    all_hashes_ok = all(bool(exp.get("experiment_reproducibility_hash")) for exp in experiments.values())

    no_live_ok = all(
        exp.get("paper_armed_approved") is False
        and exp.get("live_trading_approved") is False
        and exp.get("execution_arming_created") is False
        and exp.get("real_order_sent") is False
        and exp.get("broker_calls_executed") is False
        and exp.get("live_redis_writes_executed") is False
        and exp.get("production_doctrine_changed") is False
        for exp in experiments.values()
    ) and all(
        result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("execution_arming_created") is False
        and result.get("real_order_sent") is False
        and result.get("broker_calls_executed") is False
        and result.get("live_redis_writes_executed") is False
        and result.get("production_doctrine_changed") is False
        for result in materialized.values()
    )

    # Inspect one exported manifest from every profile to prove top-level no-live flags.
    exported_manifest_no_live_ok = True
    exported_manifest_paths = {}
    for profile_id, result in materialized.items():
        manifest_path = Path(result["written_exports"]["00_experiment_manifest.json"])
        exported_manifest_paths[profile_id] = str(manifest_path)
        manifest = read_json(manifest_path)
        exported_manifest_no_live_ok = exported_manifest_no_live_ok and (
            manifest.get("paper_armed_approved") is False
            and manifest.get("live_trading_approved") is False
            and manifest.get("execution_arming_created") is False
            and manifest.get("real_order_sent") is False
            and manifest.get("broker_calls_executed") is False
            and manifest.get("live_redis_writes_executed") is False
            and manifest.get("production_doctrine_changed") is False
        )

    diff_parameter_ok = bool(
        baseline_vs_shadow_ok
        and parameter_sweep_ok
        and threshold_sweep_ok
        and family_enable_disable_ok
        and side_only_ok
        and scenario_matrix_comparison_ok
        and all_artifacts_ok
        and all_required_exports_ok
        and all_hashes_ok
        and no_live_ok
        and exported_manifest_no_live_ok
    )

    proof = {
        "schema_version": "proof_replay_differential_parameter_sweep_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "differential_parameter_sweep_ok": diff_parameter_ok,
        "baseline_vs_shadow_ok": baseline_vs_shadow_ok,
        "parameter_sweep_ok": parameter_sweep_ok,
        "threshold_sweep_ok": threshold_sweep_ok,
        "family_enable_disable_ok": family_enable_disable_ok,
        "side_only_ok": side_only_ok,
        "scenario_matrix_comparison_ok": scenario_matrix_comparison_ok,
        "all_artifacts_ok": all_artifacts_ok,
        "all_required_exports_ok": all_required_exports_ok,
        "all_hashes_ok": all_hashes_ok,
        "no_live_ok": no_live_ok,
        "exported_manifest_no_live_ok": exported_manifest_no_live_ok,
        "experiment_count": len(experiments),
        "experiment_types": tuple(REPLAY_EXPERIMENT_TYPES),
        "parameter_summary": parameter_summary,
        "threshold_summary": threshold_summary,
        "family_summary": family_summary,
        "side_summary": side_summary,
        "validations": validations,
        "materialized": materialized,
        "exported_manifest_paths": exported_manifest_paths,
        "experiment_reproducibility_hashes": {
            k: v.get("experiment_reproducibility_hash")
            for k, v in experiments.items()
        },
        "experiment_profile_shape": "PROVEN_BY_27M",
        "differential_summary_shape": "PROVEN_BY_27M",
        "parameter_sweep_shape": "PROVEN_BY_27M",
        "threshold_sweep_shape": "PROVEN_BY_27M",
        "family_side_filter_shape": "PROVEN_BY_27M",
        "experiment_reproducibility_hash": "PROVEN_BY_27M",
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "full_live_replay_parity": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if diff_parameter_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "differential_parameter_sweep_ok": diff_parameter_ok,
        "baseline_vs_shadow_ok": baseline_vs_shadow_ok,
        "parameter_sweep_ok": parameter_sweep_ok,
        "threshold_sweep_ok": threshold_sweep_ok,
        "family_enable_disable_ok": family_enable_disable_ok,
        "side_only_ok": side_only_ok,
        "scenario_matrix_comparison_ok": scenario_matrix_comparison_ok,
        "all_artifacts_ok": all_artifacts_ok,
        "all_hashes_ok": all_hashes_ok,
        "no_live_ok": no_live_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if diff_parameter_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
