from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from .result_registry import (
    BLOCKED_LABEL_STATUS,
    BLOCKED_PNL_STATUS,
    BLOCKED_RESULT_PACK_STATUS,
    CONTRACT_VERSION as RESULT_REGISTRY_CONTRACT_VERSION,
    RESULT_REGISTRY_COLUMNS,
    row_to_dict,
    validate_result_registry_row,
)


INGESTION_AUDIT_CONTRACT_VERSION = "replay_optimization_d3_d42_result_registry_ingestion_audit_contract_v1"
SCHEMA_NAME = "MME-ScalpX Lane D3 Result Registry Ingestion Audit Contract"
ACCEPTED_FOR = "RESULT_REGISTRY_INGESTION_AUDIT_CONTRACT_NO_EXECUTION"

INGESTION_AUDIT_COLUMNS: tuple[str, ...] = (
    "audit_id",
    "registry_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_result_pack_id",
    "planned_result_pack_root",
    "actual_result_pack_id",
    "actual_result_pack_root",
    "result_pack_integrity_status",
    "label_status",
    "pnl_status",
    "ingestion_status",
    "ingestion_allowed",
    "verified_result_pack_present",
    "label_binding_allowed",
    "real_pnl_calculation_allowed",
    "leaderboard_allowed",
    "ml_export_allowed",
    "blocked_reason",
    "audit_timestamp",
    "source_lane",
    "remarks",
)

INGESTION_AUDIT_SQLITE_TYPES: dict[str, str] = {
    "audit_id": "TEXT PRIMARY KEY",
    "registry_id": "TEXT NOT NULL",
    "candidate_id": "TEXT NOT NULL",
    "candidate_fingerprint": "TEXT NOT NULL",
    "planned_result_pack_id": "TEXT",
    "planned_result_pack_root": "TEXT",
    "actual_result_pack_id": "TEXT",
    "actual_result_pack_root": "TEXT",
    "result_pack_integrity_status": "TEXT NOT NULL",
    "label_status": "TEXT NOT NULL",
    "pnl_status": "TEXT NOT NULL",
    "ingestion_status": "TEXT NOT NULL",
    "ingestion_allowed": "INTEGER NOT NULL",
    "verified_result_pack_present": "INTEGER NOT NULL",
    "label_binding_allowed": "INTEGER NOT NULL",
    "real_pnl_calculation_allowed": "INTEGER NOT NULL",
    "leaderboard_allowed": "INTEGER NOT NULL",
    "ml_export_allowed": "INTEGER NOT NULL",
    "blocked_reason": "TEXT NOT NULL",
    "audit_timestamp": "TEXT NOT NULL",
    "source_lane": "TEXT NOT NULL",
    "remarks": "TEXT",
}

BLOCKED_INGESTION_STATUS = "INGESTION_BLOCKED_AWAITING_VERIFIED_CANDIDATE_RESULT_PACK"
READY_FOR_FUTURE_VERIFIED_PACK_AUDIT_STATUS = "SCHEMA_READY_FOR_FUTURE_VERIFIED_PACK_AUDIT"
BLOCKED_REASON_NO_VERIFIED_PACK = "NO_VERIFIED_CANDIDATE_SPECIFIC_RESULT_PACK_PRESENT"


@dataclass(frozen=True)
class ResultRegistryIngestionAudit:
    audit_id: str
    registry_id: str
    candidate_id: str
    candidate_fingerprint: str
    planned_result_pack_id: str | None
    planned_result_pack_root: str | None
    actual_result_pack_id: str | None
    actual_result_pack_root: str | None
    result_pack_integrity_status: str
    label_status: str
    pnl_status: str
    ingestion_status: str
    ingestion_allowed: bool
    verified_result_pack_present: bool
    label_binding_allowed: bool
    real_pnl_calculation_allowed: bool
    leaderboard_allowed: bool
    ml_export_allowed: bool
    blocked_reason: str
    audit_timestamp: str
    source_lane: str
    remarks: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_ingestion_audit_for_unverified_registry_row(row: dict[str, Any]) -> ResultRegistryIngestionAudit:
    errors = validate_result_registry_row(row)
    if errors:
        blocked_reason = "REGISTRY_ROW_VALIDATION_FAILED:" + ",".join(errors)
    else:
        blocked_reason = BLOCKED_REASON_NO_VERIFIED_PACK

    audit_id = f"INGESTION_AUDIT::{row.get('registry_id')}"
    return ResultRegistryIngestionAudit(
        audit_id=audit_id,
        registry_id=str(row.get("registry_id")),
        candidate_id=str(row.get("candidate_id")),
        candidate_fingerprint=str(row.get("candidate_fingerprint")),
        planned_result_pack_id=row.get("planned_result_pack_id"),
        planned_result_pack_root=row.get("planned_result_pack_root"),
        actual_result_pack_id=row.get("actual_result_pack_id"),
        actual_result_pack_root=row.get("actual_result_pack_root"),
        result_pack_integrity_status=str(row.get("result_pack_integrity_status")),
        label_status=str(row.get("label_status")),
        pnl_status=str(row.get("pnl_status")),
        ingestion_status=BLOCKED_INGESTION_STATUS,
        ingestion_allowed=False,
        verified_result_pack_present=False,
        label_binding_allowed=False,
        real_pnl_calculation_allowed=False,
        leaderboard_allowed=False,
        ml_export_allowed=False,
        blocked_reason=blocked_reason,
        audit_timestamp=utc_now(),
        source_lane="LANE_D3",
        remarks="D42 audit contract only. Ingestion remains blocked until Lane E supplies verified candidate-specific result packs.",
    )


def audit_to_dict(audit: ResultRegistryIngestionAudit) -> dict[str, Any]:
    payload = asdict(audit)
    return {key: payload.get(key) for key in INGESTION_AUDIT_COLUMNS}


def validate_ingestion_audit(audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    missing = [column for column in INGESTION_AUDIT_COLUMNS if column not in audit]
    if missing:
        errors.append(f"missing_columns={missing}")

    false_required = (
        "ingestion_allowed",
        "verified_result_pack_present",
        "label_binding_allowed",
        "real_pnl_calculation_allowed",
        "leaderboard_allowed",
        "ml_export_allowed",
    )
    for key in false_required:
        if audit.get(key) is not False:
            errors.append(f"{key}_must_be_false_until_verified_result_pack")

    if audit.get("ingestion_status") != BLOCKED_INGESTION_STATUS:
        errors.append("ingestion_status_must_remain_blocked")
    if audit.get("actual_result_pack_id") is not None:
        errors.append("actual_result_pack_id_must_be_null")
    if audit.get("actual_result_pack_root") is not None:
        errors.append("actual_result_pack_root_must_be_null")
    if audit.get("result_pack_integrity_status") != BLOCKED_RESULT_PACK_STATUS:
        errors.append("result_pack_integrity_status_must_remain_blocked")
    if audit.get("label_status") != BLOCKED_LABEL_STATUS:
        errors.append("label_status_must_remain_unbound")
    if audit.get("pnl_status") != BLOCKED_PNL_STATUS:
        errors.append("pnl_status_must_remain_blocked")

    return errors


def ingestion_audit_schema_payload() -> dict[str, Any]:
    return {
        "schema_name": SCHEMA_NAME,
        "contract_version": INGESTION_AUDIT_CONTRACT_VERSION,
        "accepted_for": ACCEPTED_FOR,
        "depends_on_result_registry_contract": RESULT_REGISTRY_CONTRACT_VERSION,
        "source_registry_columns": list(RESULT_REGISTRY_COLUMNS),
        "ingestion_audit_columns": list(INGESTION_AUDIT_COLUMNS),
        "sqlite_types": INGESTION_AUDIT_SQLITE_TYPES,
        "duckdb_ready": True,
        "sqlite_ready": True,
        "ingestion_policy": {
            "future_verified_result_pack_required": True,
            "candidate_specific_pack_required": True,
            "integrity_status_must_pass_before_label_binding": True,
            "labels_remain_unbound_in_d42": True,
            "real_pnl_remains_blocked_in_d42": True,
            "leaderboard_remains_blocked_in_d42": True,
            "ml_export_remains_blocked_in_d42": True,
            "d42_does_not_create_or_materialize_result_packs": True,
        },
        "blocked_statuses": {
            "ingestion_status": BLOCKED_INGESTION_STATUS,
            "blocked_reason": BLOCKED_REASON_NO_VERIFIED_PACK,
            "future_ready_status": READY_FOR_FUTURE_VERIFIED_PACK_AUDIT_STATUS,
        },
        "safety": {
            "schema_contract_only": True,
            "ingestion_audit_contract_only": True,
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


def validate_ingestion_audit_schema_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != INGESTION_AUDIT_CONTRACT_VERSION:
        errors.append("contract_version_mismatch")
    if tuple(payload.get("ingestion_audit_columns", [])) != INGESTION_AUDIT_COLUMNS:
        errors.append("ingestion_audit_columns_mismatch")
    safety = payload.get("safety")
    if not isinstance(safety, dict):
        errors.append("missing_safety")
        return errors
    for key, expected in {
        "schema_contract_only": True,
        "ingestion_audit_contract_only": True,
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
    "BLOCKED_INGESTION_STATUS",
    "BLOCKED_REASON_NO_VERIFIED_PACK",
    "INGESTION_AUDIT_COLUMNS",
    "INGESTION_AUDIT_CONTRACT_VERSION",
    "INGESTION_AUDIT_SQLITE_TYPES",
    "READY_FOR_FUTURE_VERIFIED_PACK_AUDIT_STATUS",
    "ResultRegistryIngestionAudit",
    "SCHEMA_NAME",
    "audit_to_dict",
    "ingestion_audit_schema_payload",
    "make_ingestion_audit_for_unverified_registry_row",
    "utc_now",
    "validate_ingestion_audit",
    "validate_ingestion_audit_schema_payload",
]
