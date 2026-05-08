#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_PROOFS = {
    "27C": ("run/proofs/proof_replay_safety_firewall_latest.json", "PASS_REPLAY_SAFETY_FIREWALL", "replay_safety_firewall_ok"),
    "27D": ("run/proofs/proof_replay_dataset_contract_expansion_latest.json", "PASS_REPLAY_DATASET_CONTRACT_EXPANSION", "dataset_contract_ok"),
    "27E": ("run/proofs/proof_replay_deterministic_reset_integrity_latest.json", "PASS_REPLAY_DETERMINISTIC_RESET_INTEGRITY", "deterministic_reset_integrity_ok"),
    "27F": ("run/proofs/proof_replay_isolated_live_shape_transport_latest.json", "PASS_REPLAY_ISOLATED_LIVE_SHAPE_TRANSPORT", "isolated_live_shape_transport_ok"),
    "27G": ("run/proofs/proof_replay_feature_family_adapter_latest.json", "PASS_REPLAY_FEATURE_FAMILY_ADAPTER", "feature_family_adapter_ok"),
    "27H": ("run/proofs/proof_replay_strategy_family_adapter_arbitration_latest.json", "PASS_REPLAY_STRATEGY_FAMILY_ADAPTER_ARBITRATION", "strategy_family_adapter_arbitration_ok"),
    "27I": ("run/proofs/proof_replay_risk_adapter_execution_shadow_latest.json", "PASS_REPLAY_RISK_ADAPTER_EXECUTION_SHADOW", "risk_adapter_execution_shadow_ok"),
    "27J": ("run/proofs/proof_replay_assumption_scenario_profile_engine_latest.json", "PASS_REPLAY_ASSUMPTION_SCENARIO_PROFILE_ENGINE", "assumption_scenario_profile_engine_ok"),
    "27K": ("run/proofs/proof_replay_batch_runner_artifact_materialization_latest.json", "PASS_REPLAY_BATCH_RUNNER_ARTIFACT_MATERIALIZATION", "batch_runner_artifact_materialization_ok"),
    "27L": ("run/proofs/proof_replay_report_export_workstation_latest.json", "PASS_REPLAY_REPORT_EXPORT_WORKSTATION", "report_export_workstation_ok"),
    "27M": ("run/proofs/proof_replay_differential_parameter_sweep_workstation_latest.json", "PASS_REPLAY_DIFFERENTIAL_PARAMETER_SWEEP_WORKSTATION", "differential_parameter_sweep_workstation_ok")
}

REQUIRED_MODULES = (
    "app.mme_scalpx.replay.safety",
    "app.mme_scalpx.replay.contracts",
    "app.mme_scalpx.replay.dataset",
    "app.mme_scalpx.replay.reset",
    "app.mme_scalpx.replay.integrity",
    "app.mme_scalpx.replay.transport",
    "app.mme_scalpx.replay.live_adapter",
    "app.mme_scalpx.replay.feature_adapter",
    "app.mme_scalpx.replay.strategy_adapter",
    "app.mme_scalpx.replay.risk_adapter",
    "app.mme_scalpx.replay.execution_shadow",
    "app.mme_scalpx.replay.scenarios",
    "app.mme_scalpx.replay.batch_runner",
    "app.mme_scalpx.replay.artifact_materializer",
    "app.mme_scalpx.replay.report_exporter",
    "app.mme_scalpx.replay.experiment_workstation"
)

REQUIRED_SCHEMA_FILES = (
    "etc/replay/schemas/replay_safety_firewall_contract_v1.json",
    "etc/replay/schemas/replay_dataset_contract_v1.json",
    "etc/replay/schemas/replay_deterministic_reset_integrity_contract_v1.json",
    "etc/replay/schemas/replay_live_shape_transport_contract_v1.json",
    "etc/replay/schemas/replay_feature_family_adapter_contract_v1.json",
    "etc/replay/schemas/replay_strategy_family_adapter_contract_v1.json",
    "etc/replay/schemas/replay_risk_execution_shadow_contract_v1.json",
    "etc/replay/schemas/replay_scenario_profile_contract_v1.json",
    "etc/replay/schemas/replay_batch_runner_contract_v1.json",
    "etc/replay/schemas/replay_report_export_contract_v1.json",
    "etc/replay/schemas/replay_experiment_workstation_contract_v1.json",
    "etc/replay/schemas/replay_workstation_acceptance_gate_contract_v1.json"
)

REQUIRED_MILESTONES = (
    "docs/milestones/BATCH27C_REPLAY_SAFETY_FIREWALL.md",
    "docs/milestones/BATCH27D_REPLAY_DATASET_CONTRACT_EXPANSION.md",
    "docs/milestones/BATCH27E_DETERMINISTIC_RESET_RUN_ID_REPLAY_INTEGRITY.md",
    "docs/milestones/BATCH27F_ISOLATED_LIVE_SHAPE_REPLAY_TRANSPORT.md",
    "docs/milestones/BATCH27G_FEATURE_FAMILY_REPLAY_ADAPTER.md",
    "docs/milestones/BATCH27H_STRATEGY_FAMILY_REPLAY_ADAPTER_ARBITRATION.md",
    "docs/milestones/BATCH27I_RISK_ADAPTER_EXECUTION_SHADOW.md",
    "docs/milestones/BATCH27J_ASSUMPTION_SCENARIO_PROFILE_ENGINE.md",
    "docs/milestones/BATCH27K_REPLAY_BATCH_RUNNER_ARTIFACT_MATERIALIZATION.md",
    "docs/milestones/BATCH27L_REPLAY_REPORT_EXPORT_WORKSTATION.md",
    "docs/milestones/BATCH27M_REPLAY_DIFFERENTIAL_PARAMETER_SWEEP_WORKSTATION.md"
)

REQUIRED_BIN = (
    "bin/proof_replay_no_broker_call.py",
    "bin/proof_replay_no_live_redis_write.py",
    "bin/proof_replay_no_runtime_promotion.py",
    "bin/proof_replay_dataset_manifest.py",
    "bin/proof_replay_deterministic_repeatability.py",
    "bin/proof_replay_integrity.py",
    "bin/proof_replay_live_shape_transport.py",
    "bin/proof_replay_feature_family_parity.py",
    "bin/proof_replay_family_coverage.py",
    "bin/proof_replay_family_arbitration.py",
    "bin/proof_replay_risk_execution_shadow.py",
    "bin/proof_replay_shadow_fill_pnl.py",
    "bin/proof_replay_scenario_profiles.py",
    "bin/proof_replay_scenario_application.py",
    "bin/proof_replay_batch_runner.py",
    "bin/proof_replay_artifact_materialization.py",
    "bin/proof_replay_report_exports.py",
    "bin/proof_replay_baseline_shadow_comparison.py",
    "bin/proof_replay_experiment_profiles.py",
    "bin/proof_replay_differential_parameter_sweep.py",
    "bin/replay_batch.py",
    "bin/replay_export_reports.py",
    "bin/replay_experiments.py"
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def proof_row(batch: str, spec: tuple[str, str, str]) -> dict:
    path, expected_verdict, ok_field = spec
    p = ROOT / path
    data = load_json(p)

    safety_ok = True
    for field in (
        "paper_armed_approved",
        "live_trading_approved",
        "execution_arming_created",
        "real_order_sent",
        "production_doctrine_changed"
    ):
        if field in data and data.get(field) is not False:
            safety_ok = False

    reachability_ok = True
    for field in (
        "broker_call_reachable",
        "live_redis_write_reachable",
        "runtime_promotion_reachable"
    ):
        if field in data and data.get(field) is not False:
            reachability_ok = False

    ok = (
        p.exists()
        and data.get("verdict") == expected_verdict
        and data.get(ok_field) is True
        and safety_ok
        and reachability_ok
    )

    return {
        "batch": batch,
        "path": path,
        "exists": p.exists(),
        "verdict": data.get("verdict"),
        "expected_verdict": expected_verdict,
        "ok_field": ok_field,
        "ok_field_value": data.get(ok_field),
        "safety_ok": safety_ok,
        "reachability_ok": reachability_ok,
        "ok": ok
    }


def path_status(paths: tuple[str, ...]) -> dict:
    rows = []
    for raw in paths:
        p = ROOT / raw
        rows.append({"path": raw, "exists": p.exists(), "is_file": p.is_file()})
    return {
        "ok": all(row["exists"] and row["is_file"] for row in rows),
        "missing": [row["path"] for row in rows if not (row["exists"] and row["is_file"])],
        "rows": rows
    }


def import_status() -> dict:
    rows = []
    ok = True
    for mod in REQUIRED_MODULES:
        try:
            importlib.import_module(mod)
            rows.append({"module": mod, "ok": True})
        except Exception as exc:
            ok = False
            rows.append({"module": mod, "ok": False, "error_type": type(exc).__name__, "error": str(exc)})
    return {"ok": ok, "rows": rows}


def run_replay_artifact_status() -> dict:
    root = ROOT / "run/replay"
    json_count = len(list(root.rglob("*.json"))) if root.exists() else 0
    csv_count = len(list(root.rglob("*.csv"))) if root.exists() else 0
    export_dirs = len([p for p in root.rglob("exports") if p.is_dir()]) if root.exists() else 0
    experiment_dirs = len([p for p in root.rglob("experiments") if p.is_dir()]) if root.exists() else 0
    ok = root.exists() and json_count > 0 and csv_count > 0 and export_dirs > 0 and experiment_dirs > 0
    return {
        "ok": ok,
        "root": str(root),
        "json_count": json_count,
        "csv_count": csv_count,
        "export_dir_count": export_dirs,
        "experiment_dir_count": experiment_dirs
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_workstation_acceptance_gate.json")
    args = parser.parse_args()

    proof_rows = {batch: proof_row(batch, spec) for batch, spec in REQUIRED_PROOFS.items()}
    proofs_ok = all(row["ok"] for row in proof_rows.values())

    milestones = path_status(REQUIRED_MILESTONES)
    schemas = path_status(REQUIRED_SCHEMA_FILES)
    bins = path_status(REQUIRED_BIN)
    imports = import_status()
    artifacts = run_replay_artifact_status()

    ok = bool(proofs_ok and milestones["ok"] and schemas["ok"] and bins["ok"] and imports["ok"] and artifacts["ok"])

    proof = {
        "schema_version": "proof_replay_workstation_acceptance_gate_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "replay_workstation_acceptance_ok": ok,
        "accepted_for": "RESEARCH_AND_BACKTEST_WORKSTATION_ONLY" if ok else "NOT_ACCEPTED",
        "proofs_ok": proofs_ok,
        "proof_rows": proof_rows,
        "milestones_ok": milestones["ok"],
        "milestones": milestones,
        "schemas_ok": schemas["ok"],
        "schemas": schemas,
        "bin_scripts_ok": bins["ok"],
        "bin_scripts": bins,
        "imports_ok": imports["ok"],
        "imports": imports,
        "run_replay_artifacts_ok": artifacts["ok"],
        "run_replay_artifacts": artifacts,
        "capabilities": {
            "safety_firewall": proof_rows["27C"]["ok"],
            "dataset_contract": proof_rows["27D"]["ok"],
            "deterministic_reset_integrity": proof_rows["27E"]["ok"],
            "isolated_live_shape_transport": proof_rows["27F"]["ok"],
            "feature_family_adapter": proof_rows["27G"]["ok"],
            "strategy_family_adapter_arbitration": proof_rows["27H"]["ok"],
            "risk_adapter_execution_shadow": proof_rows["27I"]["ok"],
            "assumption_scenario_profiles": proof_rows["27J"]["ok"],
            "batch_date_range_runner": proof_rows["27K"]["ok"],
            "report_export_workstation": proof_rows["27L"]["ok"],
            "differential_parameter_sweep_workstation": proof_rows["27M"]["ok"]
        },
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "paper_armed_readiness": "NOT_APPROVED_IN_27N",
        "live_trading_readiness": "NOT_APPROVED_IN_27N",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_27N",
        "production_doctrine_revision": "NOT_APPROVED_IN_27N",
        "full_live_replay_parity": "NOT_PROVEN_IN_27N",
        "verdict": "PASS_REPLAY_WORKSTATION_ACCEPTANCE_GATE" if ok else "FAIL_REVIEW_REQUIRED"
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "replay_workstation_acceptance_ok": ok,
        "accepted_for": proof["accepted_for"],
        "proofs_ok": proofs_ok,
        "milestones_ok": milestones["ok"],
        "schemas_ok": schemas["ok"],
        "bin_scripts_ok": bins["ok"],
        "imports_ok": imports["ok"],
        "run_replay_artifacts_ok": artifacts["ok"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_27N"
    }, indent=2, sort_keys=True))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
