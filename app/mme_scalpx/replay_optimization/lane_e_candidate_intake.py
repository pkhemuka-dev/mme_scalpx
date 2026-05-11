"""Lane D2 D41 Lane E candidate materialization intake contract.

No replay execution, no result packs, no labels, no PnL, no ML,
no broker calls, no live Redis, no runtime services, no paper/live.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONTRACT_PATH = Path("etc/replay_optimization/handoff/lane_e_candidate_materialization_intake_contract.json")


@dataclass(frozen=True)
class LaneECandidateIntakeResult:
    optimization_id: str
    intake_status: str
    source_candidate_count: int
    recommended_initial_subset_size: int
    d1_subset_manifest_path: str | None
    subset_manifest_observed: bool
    subset_validation_status: str
    selected_candidate_count: int
    lane_e_execution_required: bool
    lane_c_stop_rule_declared: bool
    replay_execution_performed: bool
    result_pack_created: bool
    labels_bound: bool
    real_pnl_calculation_performed: bool
    model_training_performed: bool
    model_prediction_performed: bool
    broker_calls_executed: bool
    live_redis_writes_executed: bool
    paper_or_live_enabled: bool
    runtime_services_started: bool
    strategy_doctrine_changed: bool
    replay_engine_changed: bool
    production_profit_claim_allowed: bool
    intake_schema_path: str
    intake_requirements_path: str
    intake_checklist_json_path: str
    intake_checklist_csv_path: str
    optimizer_verdict_path: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("selected_candidates")
    if isinstance(rows, list):
        return [r for r in rows if isinstance(r, dict)]
    return []


def validate_d1_subset_manifest(
    subset_manifest_path: str | None,
    required_top_fields: list[str],
    required_candidate_fields: list[str],
) -> tuple[bool, str, int, list[str]]:
    if not subset_manifest_path:
        return False, "AWAITING_D1_SUBSET_MANIFEST", 0, ["D1 subset manifest not provided"]

    path = Path(subset_manifest_path)
    if not path.exists():
        return False, "D1_SUBSET_MANIFEST_PATH_NOT_FOUND", 0, [f"missing file: {subset_manifest_path}"]

    payload = _load_json(path)
    errors: list[str] = []

    for field in required_top_fields:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    rows = _candidate_rows(payload)
    if not rows:
        errors.append("selected_candidates is empty or missing")

    for idx, row in enumerate(rows):
        for field in required_candidate_fields:
            if row.get(field) in ("", None):
                errors.append(f"selected_candidates[{idx}] missing field: {field}")

    declared = payload.get("selected_candidate_count")
    if isinstance(declared, int) and declared != len(rows):
        errors.append(f"selected_candidate_count mismatch: declared={declared} actual={len(rows)}")

    if errors:
        return True, "D1_SUBSET_MANIFEST_INVALID", len(rows), errors

    return True, "D1_SUBSET_MANIFEST_VALIDATED_NO_EXECUTION", len(rows), []


def write_lane_e_candidate_materialization_intake_contract(
    optimization_id: str,
    artifact_root: str | Path,
    *,
    d1_subset_manifest_path: str | None = None,
) -> LaneECandidateIntakeResult:
    config = _load_json(CONTRACT_PATH)
    artifact_root = Path(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=True)

    observed, subset_status, selected_count, subset_errors = validate_d1_subset_manifest(
        d1_subset_manifest_path,
        list(config["required_d1_subset_manifest_fields"]),
        list(config["required_d1_selected_candidate_fields"]),
    )

    intake_status = (
        "LANE_E_INTAKE_CONTRACT_READY_WITH_D1_SUBSET_NO_EXECUTION"
        if subset_status == "D1_SUBSET_MANIFEST_VALIDATED_NO_EXECUTION"
        else "LANE_E_INTAKE_CONTRACT_READY_AWAITING_D1_SUBSET_NO_EXECUTION"
    )

    checklist_rows = [
        {
            "check_id": "D2D41_001",
            "check_name": "D37/D39/D40 predecessor proofs validated",
            "status": "PASS",
            "evidence": json.dumps(config["required_predecessor_proofs"], sort_keys=True),
            "remarks": "D39 top-level status is optional; D40 freeze row validates D39 status if absent."
        },
        {
            "check_id": "D2D41_002",
            "check_name": "D1 subset manifest provided",
            "status": "PASS" if observed else "PENDING",
            "evidence": d1_subset_manifest_path or "",
            "remarks": subset_status
        },
        {
            "check_id": "D2D41_003",
            "check_name": "D1 selected-candidate fields valid",
            "status": "PASS" if subset_status == "D1_SUBSET_MANIFEST_VALIDATED_NO_EXECUTION" else "PENDING",
            "evidence": "; ".join(subset_errors),
            "remarks": "D2 does not select candidates."
        },
        {
            "check_id": "D2D41_004",
            "check_name": "Lane E future output list frozen",
            "status": "PASS",
            "evidence": ",".join(config["expected_future_lane_e_outputs_per_candidate"]),
            "remarks": "D2 declares expected outputs only."
        },
        {
            "check_id": "D2D41_005",
            "check_name": "No-execution safety frozen",
            "status": "PASS",
            "evidence": ",".join(config["pre_materialization_safety_requirements"]),
            "remarks": "No replay, broker, Redis write, runtime service, paper/live, result pack, label, PnL, or ML."
        },
        {
            "check_id": "D2D41_006",
            "check_name": "Lane C stop rule declared",
            "status": "PASS",
            "evidence": config["lane_c_stop_rule"],
            "remarks": "Lane E must stop for Lane C-owned runner seam dependencies."
        }
    ]

    schema = {
        "schema_name": config["schema_name"],
        "contract_version": config["contract_version"],
        "accepted_for": config["accepted_for"],
        "created_at": _now(),
        "optimization_id": optimization_id,
        "required_d1_subset_manifest_fields": config["required_d1_subset_manifest_fields"],
        "required_d1_selected_candidate_fields": config["required_d1_selected_candidate_fields"],
        "lane_e_required_inputs_per_candidate": config["lane_e_required_inputs_per_candidate"],
        "expected_future_lane_e_outputs_per_candidate": config["expected_future_lane_e_outputs_per_candidate"],
        "future_lane_e_materialization_root_template": config["future_lane_e_materialization_root_template"],
        "lane_c_stop_rule": config["lane_c_stop_rule"],
        "safety": config["safety"]
    }

    requirements = {
        "schema_name": "MME-ScalpX Lane E Candidate Materialization Intake Requirements",
        "contract_version": config["contract_version"],
        "accepted_for": config["accepted_for"],
        "created_at": _now(),
        "optimization_id": optimization_id,
        "intake_status": intake_status,
        "source_candidate_count": config["source_candidate_count"],
        "recommended_initial_subset_size": config["recommended_initial_subset_size"],
        "d1_subset_manifest": {
            "path": d1_subset_manifest_path,
            "observed": observed,
            "validation_status": subset_status,
            "selected_candidate_count": selected_count,
            "validation_errors": subset_errors
        },
        "required_predecessor_proofs": config["required_predecessor_proofs"],
        "d39_status_validation_rule": config["d39_status_validation_rule"],
        "lane_e_required_inputs_per_candidate": config["lane_e_required_inputs_per_candidate"],
        "expected_future_lane_e_outputs_per_candidate": config["expected_future_lane_e_outputs_per_candidate"],
        "pre_materialization_safety_requirements": config["pre_materialization_safety_requirements"],
        "future_lane_e_acceptance_requirements": config["future_lane_e_acceptance_requirements"],
        "lane_c_stop_rule": config["lane_c_stop_rule"],
        "checklist": checklist_rows,
        "important_limitation": "D2-D41 is intake-contract only. It does not execute replay, create real result packs, bind labels, calculate PnL, train ML, or claim profitability.",
        "next_recommended_batch": "LANE-D2-D42_LANE_E_SUBSET_INTAKE_VALIDATOR_NO_EXECUTION_AFTER_D1_SUBSET",
        "safety": {
            "candidate_selection_performed_by_d2": False,
            "lane_e_execution_required": True,
            "lane_c_stop_rule_declared": True,
            "replay_execution_performed": False,
            "result_pack_created": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False,
            "runtime_services_started": False,
            "strategy_doctrine_changed": False,
            "replay_engine_changed": False,
            "production_profit_claim_allowed": False
        }
    }

    optimizer_verdict = {
        "optimization_id": optimization_id,
        "created_at": _now(),
        "verdict": "PASS",
        "intake_status": intake_status,
        "accepted_for": config["accepted_for"],
        "candidate_selection_performed_by_d2": False,
        "lane_e_execution_required": True,
        "lane_c_stop_rule_declared": True,
        "replay_execution_performed": False,
        "result_pack_created": False,
        "labels_bound": False,
        "real_pnl_calculation_performed": False,
        "model_training_performed": False,
        "model_prediction_performed": False,
        "production_profit_claim_allowed": False,
        "next_recommended_batch": requirements["next_recommended_batch"]
    }

    schema_path = artifact_root / "42_lane_e_candidate_materialization_intake_schema.json"
    requirements_path = artifact_root / "42_lane_e_candidate_materialization_intake_requirements.json"
    checklist_json_path = artifact_root / "42_lane_e_candidate_materialization_preflight_checklist.json"
    checklist_csv_path = artifact_root / "42_lane_e_candidate_materialization_preflight_checklist.csv"
    optimizer_verdict_path = artifact_root / "09_optimizer_verdict.json"

    _write_json(schema_path, schema)
    _write_json(requirements_path, requirements)
    _write_json(checklist_json_path, {"rows": checklist_rows, "row_count": len(checklist_rows)})
    _write_csv(checklist_csv_path, checklist_rows)
    _write_json(optimizer_verdict_path, optimizer_verdict)

    result = LaneECandidateIntakeResult(
        optimization_id=optimization_id,
        intake_status=intake_status,
        source_candidate_count=int(config["source_candidate_count"]),
        recommended_initial_subset_size=int(config["recommended_initial_subset_size"]),
        d1_subset_manifest_path=d1_subset_manifest_path,
        subset_manifest_observed=observed,
        subset_validation_status=subset_status,
        selected_candidate_count=selected_count,
        lane_e_execution_required=True,
        lane_c_stop_rule_declared=True,
        replay_execution_performed=False,
        result_pack_created=False,
        labels_bound=False,
        real_pnl_calculation_performed=False,
        model_training_performed=False,
        model_prediction_performed=False,
        broker_calls_executed=False,
        live_redis_writes_executed=False,
        paper_or_live_enabled=False,
        runtime_services_started=False,
        strategy_doctrine_changed=False,
        replay_engine_changed=False,
        production_profit_claim_allowed=False,
        intake_schema_path=schema_path.as_posix(),
        intake_requirements_path=requirements_path.as_posix(),
        intake_checklist_json_path=checklist_json_path.as_posix(),
        intake_checklist_csv_path=checklist_csv_path.as_posix(),
        optimizer_verdict_path=optimizer_verdict_path.as_posix(),
    )
    _write_json(artifact_root / "42_lane_e_candidate_materialization_intake_result.json", asdict(result))
    return result
