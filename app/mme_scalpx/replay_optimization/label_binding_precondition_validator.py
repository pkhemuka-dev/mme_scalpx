from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FULL_UNIVERSE_COUNT = 810
SUBSET_COUNT = 5

D42_BATCH = "LANE-D1-D42"
D42_SCHEMA_STATUS = "POST_RESULT_PACK_INGESTION_SCHEMA_READY_NO_EXECUTION"
D42_ROW_STATUS = "RESULT_PACK_INGESTION_REQUIREMENT_READY_NO_INGESTION"

D43_VALIDATION_STATUS = "LABEL_BINDING_PRECONDITION_VALIDATED_BLOCKED_NO_EXECUTION"
D43_LABEL_BINDING_STATUS = "BLOCKED_UNTIL_VERIFIED_RESULT_PACKS_EXIST"
D43_CANDIDATE_ROW_STATUS = "LABEL_BINDING_BLOCKED_PENDING_VERIFIED_RESULT_PACK"

REQUIRED_FALSE_PROOF_FLAGS = (
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "result_pack_exists_checked",
    "result_pack_verified",
    "result_pack_ingestion_performed",
    "candidate_result_verified",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "prediction_performed",
    "model_training_performed",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
    "runtime_services_started",
    "strategy_doctrine_changed",
    "replay_engine_changed",
    "production_profit_claim_allowed",
)

VALIDATION_ROW_COLUMNS = (
    "validation_id",
    "candidate_id",
    "candidate_fingerprint",
    "subset_rank",
    "planned_result_pack_root",
    "expected_result_pack_manifest_path",
    "required_verified_result_pack_count",
    "current_verified_result_pack_count",
    "result_pack_exists_checked",
    "result_pack_verified",
    "candidate_result_verified",
    "result_pack_ingestion_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "model_prediction_performed",
    "blocked",
    "blocking_reasons",
    "candidate_row_status",
)


@dataclass(frozen=True)
class LabelBindingPreconditionValidationResult:
    validation_id: str
    artifact_root: str
    validator_schema_path: str
    validation_summary_path: str
    candidate_rows_path: str
    blocker_report_path: str
    optimizer_verdict_path: str
    full_universe_count: int
    subset_count: int
    required_verified_result_pack_count: int
    current_verified_result_pack_count: int
    label_binding_allowed: bool
    validation_status: str


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _resolve_path(path_value: str | None, root: Path) -> Path:
    if not path_value:
        raise FileNotFoundError("empty path cannot be resolved")

    candidate = Path(path_value)
    if candidate.exists():
        return candidate

    if candidate.is_absolute():
        marker = "mme_scalpx/"
        text = candidate.as_posix()
        if marker in text:
            rel = text.split(marker, 1)[1]
            fallback = root / rel
            if fallback.exists():
                return fallback

    fallback = root / path_value
    if fallback.exists():
        return fallback

    raise FileNotFoundError(f"unable to resolve required path: {path_value}")


def _validate_d42_proof(d42: dict[str, Any]) -> None:
    if d42.get("verdict") != "PASS":
        raise ValueError("D42 proof is not PASS")
    if d42.get("batch") != D42_BATCH:
        raise ValueError(f"unexpected D42 batch: {d42.get('batch')}")
    if d42.get("full_universe_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D42 full_universe_count expected {FULL_UNIVERSE_COUNT}")
    if d42.get("full_universe_preserved") is not True:
        raise ValueError("D42 must preserve full universe")
    if d42.get("subset_count") != SUBSET_COUNT:
        raise ValueError(f"D42 subset_count expected {SUBSET_COUNT}")
    if d42.get("schema_status") != D42_SCHEMA_STATUS:
        raise ValueError(f"D42 schema_status unexpected: {d42.get('schema_status')}")
    if d42.get("next_recommended_batch") != "LANE-D1-D43_LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION":
        raise ValueError(f"D42 does not point to D43: {d42.get('next_recommended_batch')}")

    safety = d42.get("safety", {})
    if safety.get("schema_only") is not True:
        raise ValueError("D42 safety must be schema_only")
    if safety.get("full_universe_preserved") is not True:
        raise ValueError("D42 safety must preserve full universe")
    if safety.get("subset_preserved") is not True:
        raise ValueError("D42 safety must preserve subset")
    if safety.get("lane_c_or_e_execution_required") is not True:
        raise ValueError("D42 safety must require Lane C/E execution")
    for key in REQUIRED_FALSE_PROOF_FLAGS:
        if safety.get(key) is not False:
            raise ValueError(f"D42 proof safety failed: {key}")


def _validate_d42_summary(summary: dict[str, Any]) -> None:
    if summary.get("schema_status") != D42_SCHEMA_STATUS:
        raise ValueError(f"D42 summary schema_status unexpected: {summary.get('schema_status')}")
    if summary.get("full_universe_count") != FULL_UNIVERSE_COUNT:
        raise ValueError("D42 summary full_universe_count mismatch")
    if summary.get("subset_count") != SUBSET_COUNT:
        raise ValueError("D42 summary subset_count mismatch")
    if summary.get("ingestion_requirement_count") != SUBSET_COUNT:
        raise ValueError("D42 ingestion_requirement_count mismatch")
    if summary.get("result_pack_verified_count") != 0:
        raise ValueError("D42 result_pack_verified_count must be 0")
    if summary.get("result_pack_ingestion_performed") is not False:
        raise ValueError("D42 must not have performed result-pack ingestion")
    if summary.get("label_binding_allowed") is not False:
        raise ValueError("D42 must keep label binding blocked")
    if summary.get("labels_bound") is not False:
        raise ValueError("D42 must keep labels_bound=false")

    safety = summary.get("safety", {})
    if safety.get("schema_only") is not True:
        raise ValueError("D42 summary safety must be schema_only")
    if safety.get("lane_c_or_e_execution_required") is not True:
        raise ValueError("D42 summary safety must require Lane C/E execution")
    for key in (
        "lane_d_execution_allowed",
        "replay_execution_allowed",
        "replay_execution_performed",
        "result_pack_creation_allowed_in_lane_d",
        "result_pack_created",
        "result_pack_exists_checked",
        "result_pack_verified",
        "result_pack_ingestion_performed",
        "candidate_result_verified",
        "candidate_context_attached",
        "candidate_trade_matching_allowed",
        "candidate_trade_matching_performed",
        "label_binding_allowed",
        "labels_bound",
        "real_pnl_calculation_performed",
        "model_training_performed",
        "model_prediction_performed",
        "broker_calls_executed",
        "live_redis_writes_executed",
        "paper_or_live_enabled",
        "runtime_services_started",
        "strategy_doctrine_changed",
        "replay_engine_changed",
        "production_profit_claim_allowed",
    ):
        if safety.get(key) is not False:
            raise ValueError(f"D42 summary safety failed: {key}")


def _validate_label_stub(stub: dict[str, Any]) -> None:
    if stub.get("label_binding_precondition_status") != "BLOCKED_UNTIL_VERIFIED_RESULT_PACKS_EXIST":
        raise ValueError("D42 label stub must be blocked until verified result packs exist")
    if stub.get("subset_count") != SUBSET_COUNT:
        raise ValueError("D42 label stub subset_count mismatch")
    if stub.get("required_verified_result_pack_count") != SUBSET_COUNT:
        raise ValueError("D42 label stub required count mismatch")
    if stub.get("current_verified_result_pack_count") != 0:
        raise ValueError("D42 label stub current verified count must be 0")
    if stub.get("label_binding_allowed") is not False:
        raise ValueError("D42 label stub must keep label_binding_allowed=false")
    if stub.get("labels_bound") is not False:
        raise ValueError("D42 label stub must keep labels_bound=false")


def _validate_acceptance_requirements(acceptance: dict[str, Any]) -> list[dict[str, Any]]:
    rows = acceptance.get("ingestion_requirements")
    if not isinstance(rows, list):
        raise ValueError("D42 acceptance requirements missing ingestion_requirements list")
    if len(rows) != SUBSET_COUNT:
        raise ValueError(f"D42 acceptance rows expected {SUBSET_COUNT}, got {len(rows)}")

    seen: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        for key in (
            "candidate_id",
            "candidate_fingerprint",
            "subset_rank",
            "planned_result_pack_root",
            "expected_result_pack_manifest_path",
            "required_result_pack_files",
            "required_manifest_fields",
            "recommended_owner",
        ):
            if key not in row:
                raise ValueError(f"D42 acceptance row {idx} missing {key}")

        candidate_id = str(row.get("candidate_id") or "").strip()
        if not candidate_id:
            raise ValueError(f"D42 acceptance row {idx} missing candidate_id")
        if candidate_id in seen:
            raise ValueError(f"duplicate D42 acceptance candidate_id: {candidate_id}")
        seen.add(candidate_id)

        if row.get("ingestion_row_status") != D42_ROW_STATUS:
            raise ValueError(f"D42 acceptance row {idx} bad status: {row.get('ingestion_row_status')}")
        if row.get("lane_c_or_e_execution_required") is not True:
            raise ValueError(f"D42 acceptance row {idx} must require Lane C/E execution")

        for key in (
            "lane_d_execution_allowed",
            "result_pack_exists_checked",
            "result_pack_verified",
            "result_pack_ingestion_performed",
            "candidate_result_verified",
            "label_binding_allowed",
            "labels_bound",
            "real_pnl_calculation_performed",
            "model_training_performed",
            "model_prediction_performed",
        ):
            if row.get(key) is not False:
                raise ValueError(f"D42 acceptance row {idx} safety failed: {key}")

    return [dict(row) for row in rows]


def validate_label_binding_preconditions(
    validation_id: str,
    artifact_root: Path,
    root: Path | None = None,
) -> LabelBindingPreconditionValidationResult:
    root = (root or Path.cwd()).resolve()
    artifact_root = artifact_root.resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    d42_path = root / "run/proofs/proof_lane_d_d42_post_result_pack_ingestion_schema_latest.json"
    d42 = _load_json(d42_path)
    _validate_d42_proof(d42)

    ingestion_summary_path = _resolve_path(str(d42.get("ingestion_summary_path") or ""), root)
    acceptance_path = _resolve_path(str(d42.get("acceptance_requirements_path") or ""), root)
    label_stub_path = _resolve_path(str(d42.get("label_binding_precondition_stub_path") or ""), root)
    ingestion_schema_path = _resolve_path(str(d42.get("ingestion_schema_path") or ""), root)

    ingestion_summary = _load_json(ingestion_summary_path)
    acceptance = _load_json(acceptance_path)
    label_stub = _load_json(label_stub_path)
    ingestion_schema = _load_json(ingestion_schema_path)

    _validate_d42_summary(ingestion_summary)
    _validate_label_stub(label_stub)
    acceptance_rows = _validate_acceptance_requirements(acceptance)

    if ingestion_schema.get("schema_status") != D42_SCHEMA_STATUS:
        raise ValueError("D42 ingestion schema status mismatch")

    required_verified = SUBSET_COUNT
    current_verified = 0
    label_binding_allowed = False

    candidate_rows: list[dict[str, Any]] = []
    for row in sorted(acceptance_rows, key=lambda x: int(x.get("subset_rank") or 0)):
        candidate_rows.append({
            "validation_id": validation_id,
            "candidate_id": row["candidate_id"],
            "candidate_fingerprint": row["candidate_fingerprint"],
            "subset_rank": int(row.get("subset_rank") or 0),
            "planned_result_pack_root": row["planned_result_pack_root"],
            "expected_result_pack_manifest_path": row["expected_result_pack_manifest_path"],
            "required_verified_result_pack_count": required_verified,
            "current_verified_result_pack_count": current_verified,
            "result_pack_exists_checked": False,
            "result_pack_verified": False,
            "candidate_result_verified": False,
            "result_pack_ingestion_performed": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "blocked": True,
            "blocking_reasons": [
                "verified_candidate_result_pack_missing",
                "result_pack_verification_not_performed",
                "candidate_result_verified_false",
                "label_binding_precondition_unsatisfied",
                "pnl_not_calculated",
                "labels_not_available"
            ],
            "candidate_row_status": D43_CANDIDATE_ROW_STATUS,
        })

    blocker_report = {
        "validation_id": validation_id,
        "label_binding_precondition_status": D43_LABEL_BINDING_STATUS,
        "validation_status": D43_VALIDATION_STATUS,
        "required_verified_result_pack_count": required_verified,
        "current_verified_result_pack_count": current_verified,
        "candidate_blocked_count": len(candidate_rows),
        "label_binding_allowed": False,
        "labels_bound": False,
        "global_blocking_reasons": [
            "lane_c_or_e_verified_result_packs_not_available",
            "d42_schema_is_requirements_only",
            "no_result_pack_existence_check_performed",
            "no_result_pack_ingestion_performed",
            "no_candidate_result_verified",
            "no_real_pnl_labels_available"
        ],
        "next_required_external_step": "LANE_C_OR_E_EXECUTE_D41_SUBSET_AND_RETURN_VERIFIED_RESULT_PACKS",
        "next_d1_batch_after_verified_result_packs": "LANE-D1-D44_RESULT_PACK_INTAKE_AUDIT_AFTER_LANE_CE_RESULTS_NO_EXECUTION"
    }

    validator_schema = {
        "contract_version": "replay_optimization_d43_label_binding_precondition_validator_contract_v1",
        "validation_id": validation_id,
        "source_d42_proof_path": d42_path.as_posix(),
        "source_ingestion_schema_path": ingestion_schema_path.as_posix(),
        "source_acceptance_requirements_path": acceptance_path.as_posix(),
        "source_label_stub_path": label_stub_path.as_posix(),
        "validation_row_columns": list(VALIDATION_ROW_COLUMNS),
        "label_binding_precondition_status": D43_LABEL_BINDING_STATUS,
        "validation_status": D43_VALIDATION_STATUS,
        "safety": {
            "validator_only": True,
            "full_universe_preserved": True,
            "subset_preserved": True,
            "lane_d_execution_allowed": False,
            "lane_c_or_e_execution_required": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_created": False,
            "result_pack_exists_checked": False,
            "result_pack_verified": False,
            "result_pack_ingestion_performed": False,
            "candidate_result_verified": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "leaderboard_created": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
        },
    }

    validation_summary = {
        "validation_id": validation_id,
        "accepted_for": "LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION",
        "validation_status": D43_VALIDATION_STATUS,
        "label_binding_precondition_status": D43_LABEL_BINDING_STATUS,
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "full_universe_preserved": True,
        "subset_count": SUBSET_COUNT,
        "subset_preserved": True,
        "required_verified_result_pack_count": required_verified,
        "current_verified_result_pack_count": current_verified,
        "candidate_precondition_row_count": len(candidate_rows),
        "candidate_blocked_count": len(candidate_rows),
        "label_binding_allowed": label_binding_allowed,
        "labels_bound": False,
        "leaderboard_allowed": False,
        "ml_dataset_allowed": False,
        "important_limitation": "D43 validates that label binding remains blocked. It does not execute replay, inspect real result packs, ingest result packs, bind labels, calculate PnL, train models, predict, or create leaderboard outputs.",
        "safety": {
            "validator_only": True,
            "full_universe_preserved": True,
            "subset_preserved": True,
            "lane_d_execution_allowed": False,
            "lane_c_or_e_execution_required": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_creation_allowed_in_lane_d": False,
            "result_pack_created": False,
            "result_pack_exists_checked": False,
            "result_pack_verified": False,
            "result_pack_ingestion_performed": False,
            "candidate_result_verified": False,
            "candidate_context_attached": False,
            "candidate_trade_matching_allowed": False,
            "candidate_trade_matching_performed": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "leaderboard_created": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False,
            "runtime_services_started": False,
            "strategy_doctrine_changed": False,
            "replay_engine_changed": False,
            "production_profit_claim_allowed": False
        },
        "next_required_external_step": "LANE_C_OR_E_EXECUTE_D41_SUBSET_AND_RETURN_VERIFIED_RESULT_PACKS",
        "next_d1_batch_after_verified_result_packs": "LANE-D1-D44_RESULT_PACK_INTAKE_AUDIT_AFTER_LANE_CE_RESULTS_NO_EXECUTION"
    }

    optimizer_verdict = {
        "validation_id": validation_id,
        "verdict": "PASS",
        "accepted_for": "LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION",
        "validation_status": D43_VALIDATION_STATUS,
        "label_binding_precondition_status": D43_LABEL_BINDING_STATUS,
        "required_verified_result_pack_count": required_verified,
        "current_verified_result_pack_count": current_verified,
        "candidate_blocked_count": len(candidate_rows),
        "label_binding_allowed": False,
        "labels_bound": False,
        "next_required_external_step": "LANE_C_OR_E_EXECUTE_D41_SUBSET_AND_RETURN_VERIFIED_RESULT_PACKS",
        "next_d1_batch_after_verified_result_packs": "LANE-D1-D44_RESULT_PACK_INTAKE_AUDIT_AFTER_LANE_CE_RESULTS_NO_EXECUTION"
    }

    validator_schema_path = artifact_root / "46_label_binding_precondition_validator_schema.json"
    validation_summary_path = artifact_root / "46_label_binding_precondition_validation_summary.json"
    candidate_rows_path = artifact_root / "46_label_binding_candidate_precondition_rows.json"
    blocker_report_path = artifact_root / "46_label_binding_blocker_report.json"
    optimizer_verdict_path = artifact_root / "09_optimizer_verdict.json"

    _write_json(validator_schema_path, validator_schema)
    _write_json(validation_summary_path, validation_summary)
    _write_json(candidate_rows_path, {"rows": candidate_rows})
    _write_json(blocker_report_path, blocker_report)
    _write_json(optimizer_verdict_path, optimizer_verdict)

    return LabelBindingPreconditionValidationResult(
        validation_id=validation_id,
        artifact_root=artifact_root.as_posix(),
        validator_schema_path=validator_schema_path.as_posix(),
        validation_summary_path=validation_summary_path.as_posix(),
        candidate_rows_path=candidate_rows_path.as_posix(),
        blocker_report_path=blocker_report_path.as_posix(),
        optimizer_verdict_path=optimizer_verdict_path.as_posix(),
        full_universe_count=FULL_UNIVERSE_COUNT,
        subset_count=SUBSET_COUNT,
        required_verified_result_pack_count=required_verified,
        current_verified_result_pack_count=current_verified,
        label_binding_allowed=label_binding_allowed,
        validation_status=D43_VALIDATION_STATUS,
    )


__all__ = [
    "FULL_UNIVERSE_COUNT",
    "SUBSET_COUNT",
    "D43_VALIDATION_STATUS",
    "D43_LABEL_BINDING_STATUS",
    "D43_CANDIDATE_ROW_STATUS",
    "VALIDATION_ROW_COLUMNS",
    "LabelBindingPreconditionValidationResult",
    "validate_label_binding_preconditions",
]
