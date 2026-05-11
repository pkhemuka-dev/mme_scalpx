from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


CONTRACT_VERSION = "replay_optimization_d3_d41_result_registry_contract_v1"
SCHEMA_NAME = "MME-ScalpX Lane D3 Result Registry Schema Contract"
ACCEPTED_FOR = "RESULT_REGISTRY_SCHEMA_CONTRACT_NO_EXECUTION"

RESULT_REGISTRY_COLUMNS: tuple[str, ...] = (
    "registry_id",
    "candidate_id",
    "candidate_fingerprint",
    "subset_id",
    "handoff_id",
    "package_requirement_id",
    "planned_result_pack_id",
    "planned_result_pack_root",
    "actual_result_pack_id",
    "actual_result_pack_root",
    "result_pack_integrity_status",
    "label_status",
    "pnl_status",
    "leaderboard_eligible",
    "ml_export_eligible",
    "source_lane",
    "verification_timestamp",
    "remarks",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "leaderboard_built",
    "ml_export_performed",
    "replay_execution_performed",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
    "runtime_services_started",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_performed",
)

RESULT_REGISTRY_SQLITE_TYPES: dict[str, str] = {
    "registry_id": "TEXT PRIMARY KEY",
    "candidate_id": "TEXT NOT NULL",
    "candidate_fingerprint": "TEXT NOT NULL",
    "subset_id": "TEXT",
    "handoff_id": "TEXT",
    "package_requirement_id": "TEXT",
    "planned_result_pack_id": "TEXT",
    "planned_result_pack_root": "TEXT",
    "actual_result_pack_id": "TEXT",
    "actual_result_pack_root": "TEXT",
    "result_pack_integrity_status": "TEXT NOT NULL",
    "label_status": "TEXT NOT NULL",
    "pnl_status": "TEXT NOT NULL",
    "leaderboard_eligible": "INTEGER NOT NULL",
    "ml_export_eligible": "INTEGER NOT NULL",
    "source_lane": "TEXT NOT NULL",
    "verification_timestamp": "TEXT",
    "remarks": "TEXT",
    "label_binding_allowed": "INTEGER NOT NULL",
    "labels_bound": "INTEGER NOT NULL",
    "real_pnl_calculation_performed": "INTEGER NOT NULL",
    "leaderboard_built": "INTEGER NOT NULL",
    "ml_export_performed": "INTEGER NOT NULL",
    "replay_execution_performed": "INTEGER NOT NULL",
    "broker_calls_executed": "INTEGER NOT NULL",
    "live_redis_writes_executed": "INTEGER NOT NULL",
    "paper_or_live_enabled": "INTEGER NOT NULL",
    "runtime_services_started": "INTEGER NOT NULL",
    "result_pack_created": "INTEGER NOT NULL",
    "candidate_context_attached": "INTEGER NOT NULL",
    "candidate_trade_matching_performed": "INTEGER NOT NULL",
}

BLOCKED_RESULT_PACK_STATUS = "UNVERIFIED_AWAITING_LANE_E_VERIFIED_RESULT_PACK"
BLOCKED_LABEL_STATUS = "UNBOUND_BLOCKED_AWAITING_VERIFIED_RESULT_PACK"
BLOCKED_PNL_STATUS = "BLOCKED_AWAITING_VERIFIED_RESULT_PACK"

BOOLEAN_FALSE_GUARD_COLUMNS: tuple[str, ...] = (
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "leaderboard_built",
    "ml_export_performed",
    "replay_execution_performed",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
    "runtime_services_started",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_performed",
)


@dataclass(frozen=True)
class ResultRegistryRow:
    registry_id: str
    candidate_id: str
    candidate_fingerprint: str
    subset_id: str | None
    handoff_id: str | None
    package_requirement_id: str | None
    planned_result_pack_id: str | None
    planned_result_pack_root: str | None
    actual_result_pack_id: str | None
    actual_result_pack_root: str | None
    result_pack_integrity_status: str
    label_status: str
    pnl_status: str
    leaderboard_eligible: bool
    ml_export_eligible: bool
    source_lane: str
    verification_timestamp: str | None
    remarks: str
    label_binding_allowed: bool = False
    labels_bound: bool = False
    real_pnl_calculation_performed: bool = False
    leaderboard_built: bool = False
    ml_export_performed: bool = False
    replay_execution_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False
    runtime_services_started: bool = False
    result_pack_created: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_performed: bool = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_unbound_registry_row(
    *,
    candidate_id: str,
    candidate_fingerprint: str,
    subset_id: str | None = None,
    handoff_id: str | None = None,
    package_requirement_id: str | None = None,
    planned_result_pack_id: str | None = None,
    planned_result_pack_root: str | None = None,
    source_lane: str = "LANE_D3",
    remarks: str = "Schema-only unbound registry row. Actual result pack, labels, PnL, leaderboard, and ML export remain blocked.",
) -> ResultRegistryRow:
    registry_id = f"RESULT_REGISTRY::{candidate_id}::{candidate_fingerprint}"
    return ResultRegistryRow(
        registry_id=registry_id,
        candidate_id=candidate_id,
        candidate_fingerprint=candidate_fingerprint,
        subset_id=subset_id,
        handoff_id=handoff_id,
        package_requirement_id=package_requirement_id,
        planned_result_pack_id=planned_result_pack_id,
        planned_result_pack_root=planned_result_pack_root,
        actual_result_pack_id=None,
        actual_result_pack_root=None,
        result_pack_integrity_status=BLOCKED_RESULT_PACK_STATUS,
        label_status=BLOCKED_LABEL_STATUS,
        pnl_status=BLOCKED_PNL_STATUS,
        leaderboard_eligible=False,
        ml_export_eligible=False,
        source_lane=source_lane,
        verification_timestamp=None,
        remarks=remarks,
    )


def row_to_dict(row: ResultRegistryRow) -> dict[str, Any]:
    payload = asdict(row)
    return {key: payload.get(key) for key in RESULT_REGISTRY_COLUMNS}


def schema_payload() -> dict[str, Any]:
    return {
        "schema_name": SCHEMA_NAME,
        "contract_version": CONTRACT_VERSION,
        "accepted_for": ACCEPTED_FOR,
        "columns": list(RESULT_REGISTRY_COLUMNS),
        "sqlite_types": RESULT_REGISTRY_SQLITE_TYPES,
        "duckdb_ready": True,
        "sqlite_ready": True,
        "blocked_statuses": {
            "result_pack_integrity_status": BLOCKED_RESULT_PACK_STATUS,
            "label_status": BLOCKED_LABEL_STATUS,
            "pnl_status": BLOCKED_PNL_STATUS,
        },
        "eligibility_policy": {
            "leaderboard_eligible_default": False,
            "ml_export_eligible_default": False,
            "label_binding_requires_verified_candidate_result_pack": True,
            "real_pnl_requires_verified_candidate_result_pack": True,
            "leaderboard_requires_verified_labels": True,
            "ml_export_requires_sample_size_and_verified_labels": True,
        },
        "safety": {
            "schema_contract_only": True,
            "registry_schema_file_creation_allowed": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_creation_allowed": False,
            "result_pack_created": False,
            "replay_artifact_materialization_allowed": False,
            "candidate_context_attachment_allowed": False,
            "candidate_context_attached": False,
            "candidate_trade_matching_allowed": False,
            "candidate_trade_matching_performed": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_allowed": False,
            "real_pnl_calculation_performed": False,
            "leaderboard_built": False,
            "ml_export_performed": False,
            "model_training_allowed": False,
            "model_training_performed": False,
            "model_prediction_allowed": False,
            "prediction_performed": False,
            "broker_calls_allowed": False,
            "broker_calls_executed": False,
            "live_redis_writes_allowed": False,
            "live_redis_writes_executed": False,
            "paper_live_enablement_allowed": False,
            "paper_or_live_enabled": False,
            "runtime_service_start_allowed": False,
            "runtime_services_started": False,
            "strategy_doctrine_mutation_allowed": False,
            "strategy_doctrine_changed": False,
            "replay_engine_mutation_allowed": False,
            "replay_engine_changed": False,
            "production_profit_claim_allowed": False,
        },
    }


def validate_result_registry_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    missing = [column for column in RESULT_REGISTRY_COLUMNS if column not in row]
    if missing:
        errors.append(f"missing_columns={missing}")

    for key in BOOLEAN_FALSE_GUARD_COLUMNS:
        if row.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    if row.get("actual_result_pack_id") is not None:
        errors.append("actual_result_pack_id_must_be_null_until_verified")
    if row.get("actual_result_pack_root") is not None:
        errors.append("actual_result_pack_root_must_be_null_until_verified")
    if row.get("result_pack_integrity_status") != BLOCKED_RESULT_PACK_STATUS:
        errors.append("result_pack_integrity_status_must_remain_blocked")
    if row.get("label_status") != BLOCKED_LABEL_STATUS:
        errors.append("label_status_must_remain_unbound")
    if row.get("pnl_status") != BLOCKED_PNL_STATUS:
        errors.append("pnl_status_must_remain_blocked")
    if row.get("leaderboard_eligible") is not False:
        errors.append("leaderboard_eligible_must_be_false")
    if row.get("ml_export_eligible") is not False:
        errors.append("ml_export_eligible_must_be_false")

    return errors


def validate_schema_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != CONTRACT_VERSION:
        errors.append("contract_version_mismatch")
    if tuple(payload.get("columns", [])) != RESULT_REGISTRY_COLUMNS:
        errors.append("columns_mismatch")
    safety = payload.get("safety")
    if not isinstance(safety, dict):
        errors.append("missing_safety")
        return errors
    for key, expected in {
        "schema_contract_only": True,
        "registry_schema_file_creation_allowed": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed": False,
        "result_pack_created": False,
        "candidate_context_attachment_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "real_pnl_calculation_allowed": False,
        "real_pnl_calculation_performed": False,
        "leaderboard_built": False,
        "ml_export_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
        "runtime_services_started": False,
    }.items():
        if safety.get(key) is not expected:
            errors.append(f"safety_{key}_expected_{expected}")
    return errors


__all__ = [
    "ACCEPTED_FOR",
    "BLOCKED_LABEL_STATUS",
    "BLOCKED_PNL_STATUS",
    "BLOCKED_RESULT_PACK_STATUS",
    "BOOLEAN_FALSE_GUARD_COLUMNS",
    "CONTRACT_VERSION",
    "RESULT_REGISTRY_COLUMNS",
    "RESULT_REGISTRY_SQLITE_TYPES",
    "ResultRegistryRow",
    "SCHEMA_NAME",
    "make_unbound_registry_row",
    "row_to_dict",
    "schema_payload",
    "utc_now",
    "validate_result_registry_row",
    "validate_schema_payload",
]
