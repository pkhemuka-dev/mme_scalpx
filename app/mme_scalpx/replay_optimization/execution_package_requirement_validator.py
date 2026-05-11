from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

D39_BATCH = "LANE-D1-D39"
D39_ACCEPTED_FOR = "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION"
D40_VALIDATION_STATUS = "EXECUTION_PACKAGE_REQUIREMENT_VALIDATED_NO_EXECUTION"
D39_ROW_STATUS = "PACKAGE_REQUIREMENT_READY_NO_EXECUTION"
D39_REQUIREMENT_STATUS = "LANE_CE_EXECUTION_PACKAGE_REQUIREMENTS_READY_NO_EXECUTION"

REQUIRED_ROW_COLUMNS = (
    "package_requirement_id",
    "candidate_id",
    "candidate_fingerprint",
    "handoff_id",
    "planned_result_pack_root",
    "planned_result_pack_manifest_path",
    "planned_run_manifest_required",
    "planned_metrics_summary_required",
    "planned_trade_log_required",
    "planned_candidate_audit_required",
    "planned_decision_trace_required",
    "planned_integrity_report_required",
    "candidate_profile_required",
    "candidate_context_catalog_required",
    "replay_execution_owner",
    "recommended_owner",
    "lane_c_or_e_execution_required",
    "lane_d_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "model_prediction_performed",
    "package_row_status",
    "remarks",
)

REQUIRED_FALSE_ROW_FLAGS = (
    "lane_d_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "model_prediction_performed",
)

REQUIRED_TRUE_ROW_FLAGS = (
    "lane_c_or_e_execution_required",
    "planned_run_manifest_required",
    "planned_metrics_summary_required",
    "planned_trade_log_required",
    "planned_candidate_audit_required",
    "planned_decision_trace_required",
    "planned_integrity_report_required",
    "candidate_profile_required",
    "candidate_context_catalog_required",
)

REQUIRED_FALSE_SUMMARY_FLAGS = (
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "artifact_file_creation_allowed_in_lane_d",
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
)


@dataclass(frozen=True)
class ExecutionPackageRequirementValidationResult:
    validation_id: str
    artifact_root: str
    validation_schema_path: str
    validation_summary_path: str
    validation_rows_path: str
    validation_verdict_path: str
    source_d39_proof_path: str
    source_d39_artifact_root: str
    candidate_count: int
    validated_row_count: int
    failed_row_count: int
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


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(row) for row in payload]
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list):
            return [dict(row) for row in rows]
    raise ValueError("rows payload does not contain a rows list")


def _validate_d39_proof(proof: dict[str, Any]) -> None:
    if proof.get("verdict") != "PASS":
        raise ValueError("D39 proof is not PASS")
    if proof.get("batch") != D39_BATCH:
        raise ValueError(f"unexpected D39 batch: {proof.get('batch')}")
    if proof.get("accepted_for") != D39_ACCEPTED_FOR:
        raise ValueError(f"unexpected D39 accepted_for: {proof.get('accepted_for')}")
    if proof.get("candidate_count") != 810:
        raise ValueError(f"D39 candidate_count expected 810, got {proof.get('candidate_count')}")
    if proof.get("package_requirement_row_count") != 810:
        raise ValueError(f"D39 package_requirement_row_count expected 810, got {proof.get('package_requirement_row_count')}")
    if proof.get("package_requirement_ready_count") != 810:
        raise ValueError(f"D39 package_requirement_ready_count expected 810, got {proof.get('package_requirement_ready_count')}")

    safety = proof.get("safety", {})
    if safety.get("lane_c_or_e_execution_required") is not True:
        raise ValueError("D39 proof safety must require Lane C/E execution")
    for key in (
        "lane_d_execution_allowed",
        "replay_execution_allowed",
        "replay_execution_performed",
        "result_pack_creation_allowed_in_lane_d",
        "result_pack_created",
        "artifact_file_creation_allowed_in_lane_d",
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
    ):
        if safety.get(key) is not False:
            raise ValueError(f"D39 proof safety failed: {key}")


def _validate_summary(summary: dict[str, Any]) -> None:
    if summary.get("candidate_count") != 810:
        raise ValueError(f"D39 summary candidate_count expected 810, got {summary.get('candidate_count')}")
    if summary.get("package_requirement_ready_count") != 810:
        raise ValueError(f"D39 summary ready count expected 810, got {summary.get('package_requirement_ready_count')}")
    if summary.get("full_universe_preserved") is not True:
        raise ValueError("D39 summary must preserve full universe")
    if summary.get("requirement_status") != D39_REQUIREMENT_STATUS:
        raise ValueError(f"unexpected D39 requirement_status: {summary.get('requirement_status')}")

    safety = summary.get("safety", {})
    if safety.get("lane_c_or_e_execution_required") is not True:
        raise ValueError("D39 summary safety must require Lane C/E execution")
    for key in REQUIRED_FALSE_SUMMARY_FLAGS:
        if safety.get(key) is not False:
            raise ValueError(f"D39 summary safety failed: {key}")


def _validate_schema(schema: dict[str, Any]) -> None:
    columns = tuple(schema.get("row_columns") or ())
    missing = [col for col in REQUIRED_ROW_COLUMNS if col not in columns]
    if missing:
        raise ValueError(f"D39 schema missing required row columns: {missing}")

    safety = schema.get("safety", {})
    if safety.get("lane_c_or_e_execution_required") is not True:
        raise ValueError("D39 schema safety must require Lane C/E execution")
    for key in (
        "lane_d_execution_allowed",
        "replay_execution_allowed",
        "replay_execution_performed",
        "result_pack_creation_allowed_in_lane_d",
        "result_pack_created",
        "label_binding_allowed",
        "labels_bound",
        "real_pnl_calculation_performed",
        "model_training_performed",
        "model_prediction_performed",
    ):
        if safety.get(key) is not False:
            raise ValueError(f"D39 schema safety failed: {key}")


def _validate_requirement_row(row: dict[str, Any], index: int) -> list[str]:
    failures: list[str] = []

    for col in REQUIRED_ROW_COLUMNS:
        if col not in row:
            failures.append(f"missing_column:{col}")

    if row.get("package_row_status") != D39_ROW_STATUS:
        failures.append("bad_package_row_status")

    for key in REQUIRED_FALSE_ROW_FLAGS:
        if row.get(key) is not False:
            failures.append(f"expected_false:{key}")

    for key in REQUIRED_TRUE_ROW_FLAGS:
        if row.get(key) is not True:
            failures.append(f"expected_true:{key}")

    for key in (
        "package_requirement_id",
        "candidate_id",
        "candidate_fingerprint",
        "planned_result_pack_root",
        "planned_result_pack_manifest_path",
        "replay_execution_owner",
        "recommended_owner",
    ):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            failures.append(f"missing_or_blank:{key}")

    manifest_path = str(row.get("planned_result_pack_manifest_path") or "")
    if manifest_path and not manifest_path.endswith("/result_pack_manifest.json"):
        failures.append("bad_planned_result_pack_manifest_path")

    return failures


def validate_execution_package_requirements(
    validation_id: str,
    d39_proof_path: Path,
    artifact_root: Path,
    root: Path | None = None,
) -> ExecutionPackageRequirementValidationResult:
    root = (root or Path.cwd()).resolve()
    artifact_root = artifact_root.resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    d39_proof_path = _resolve_path(d39_proof_path.as_posix(), root)
    d39_proof = _load_json(d39_proof_path)
    _validate_d39_proof(d39_proof)

    schema_path = _resolve_path(str(d39_proof.get("schema_path") or ""), root)
    summary_path = _resolve_path(str(d39_proof.get("summary_path") or ""), root)
    rows_json_path = _resolve_path(str(d39_proof.get("rows_json_path") or ""), root)
    optimizer_verdict_path = _resolve_path(str(d39_proof.get("optimizer_verdict_path") or ""), root)

    schema = _load_json(schema_path)
    summary = _load_json(summary_path)
    rows = _extract_rows(_load_json(rows_json_path))
    optimizer_verdict = _load_json(optimizer_verdict_path)

    _validate_schema(schema)
    _validate_summary(summary)

    if optimizer_verdict.get("verdict") != "PASS":
        raise ValueError("D39 optimizer verdict is not PASS")
    if optimizer_verdict.get("candidate_count") != 810:
        raise ValueError("D39 optimizer verdict candidate_count is not 810")
    if len(rows) != 810:
        raise ValueError(f"D39 rows expected 810, got {len(rows)}")

    seen_candidate_ids: set[str] = set()
    seen_fingerprints: set[str] = set()
    validation_rows: list[dict[str, Any]] = []
    failed_count = 0

    for index, row in enumerate(rows, start=1):
        failures = _validate_requirement_row(row, index)
        candidate_id = str(row.get("candidate_id") or "")
        fingerprint = str(row.get("candidate_fingerprint") or "")

        if candidate_id in seen_candidate_ids:
            failures.append("duplicate_candidate_id")
        if fingerprint in seen_fingerprints:
            failures.append("duplicate_candidate_fingerprint")

        seen_candidate_ids.add(candidate_id)
        seen_fingerprints.add(fingerprint)

        if failures:
            failed_count += 1

        validation_rows.append({
            "validation_id": validation_id,
            "source_package_requirement_id": row.get("package_requirement_id"),
            "candidate_id": candidate_id,
            "candidate_fingerprint": fingerprint,
            "planned_result_pack_root": row.get("planned_result_pack_root"),
            "lane_c_or_e_execution_required": row.get("lane_c_or_e_execution_required"),
            "lane_d_execution_allowed": row.get("lane_d_execution_allowed"),
            "replay_execution_performed": row.get("replay_execution_performed"),
            "result_pack_created": row.get("result_pack_created"),
            "label_binding_allowed": row.get("label_binding_allowed"),
            "labels_bound": row.get("labels_bound"),
            "real_pnl_calculation_performed": row.get("real_pnl_calculation_performed"),
            "model_training_performed": row.get("model_training_performed"),
            "model_prediction_performed": row.get("model_prediction_performed"),
            "source_package_row_status": row.get("package_row_status"),
            "validation_failures": failures,
            "validation_pass": not failures,
            "validation_status": D40_VALIDATION_STATUS if not failures else "EXECUTION_PACKAGE_REQUIREMENT_VALIDATION_FAILED",
        })

    validation_status = D40_VALIDATION_STATUS if failed_count == 0 else "EXECUTION_PACKAGE_REQUIREMENT_VALIDATION_FAILED"

    validation_schema = {
        "contract_version": "replay_optimization_d40_execution_package_requirement_validator_contract_v1",
        "validation_id": validation_id,
        "source_d39_proof_path": d39_proof_path.as_posix(),
        "source_d39_artifact_root": str(d39_proof.get("artifact_root") or ""),
        "source_required_row_columns": list(REQUIRED_ROW_COLUMNS),
        "validation_row_columns": [
            "validation_id",
            "source_package_requirement_id",
            "candidate_id",
            "candidate_fingerprint",
            "planned_result_pack_root",
            "lane_c_or_e_execution_required",
            "lane_d_execution_allowed",
            "replay_execution_performed",
            "result_pack_created",
            "label_binding_allowed",
            "labels_bound",
            "real_pnl_calculation_performed",
            "model_training_performed",
            "model_prediction_performed",
            "source_package_row_status",
            "validation_failures",
            "validation_pass",
            "validation_status"
        ],
        "safety": {
            "lane_d_execution_allowed": False,
            "lane_c_or_e_execution_required": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_created": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False
        }
    }

    validation_summary = {
        "validation_id": validation_id,
        "source_d39_proof_path": d39_proof_path.as_posix(),
        "source_d39_artifact_root": str(d39_proof.get("artifact_root") or ""),
        "candidate_count": len(rows),
        "validated_row_count": len(rows) - failed_count,
        "failed_row_count": failed_count,
        "full_universe_preserved": len(rows) == 810,
        "validation_status": validation_status,
        "accepted_for": "EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_NO_EXECUTION",
        "important_limitation": "D40 validates D39 package requirement rows only. It does not execute replay, create result packs, bind labels, calculate PnL, train models, predict, or claim profitability.",
        "safety": {
            "lane_d_execution_allowed": False,
            "lane_c_or_e_execution_required": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_creation_allowed_in_lane_d": False,
            "result_pack_created": False,
            "candidate_context_attached": False,
            "candidate_trade_matching_allowed": False,
            "candidate_trade_matching_performed": False,
            "label_binding_allowed": False,
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
        },
        "next_recommended_batch": "LANE-D1-D41_CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION"
    }

    validation_verdict = {
        "validation_id": validation_id,
        "verdict": "PASS" if failed_count == 0 else "FAIL",
        "accepted_for": "EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_NO_EXECUTION",
        "candidate_count": len(rows),
        "validated_row_count": len(rows) - failed_count,
        "failed_row_count": failed_count,
        "validation_status": validation_status,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "next_recommended_batch": "LANE-D1-D41_CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION"
    }

    validation_schema_path = artifact_root / "43_lane_ce_execution_package_requirement_validation_schema.json"
    validation_summary_path = artifact_root / "43_lane_ce_execution_package_requirement_validation_summary.json"
    validation_rows_path = artifact_root / "43_lane_ce_execution_package_requirement_validation_rows.json"
    validation_verdict_path = artifact_root / "43_lane_ce_execution_package_requirement_validation_verdict.json"

    _write_json(validation_schema_path, validation_schema)
    _write_json(validation_summary_path, validation_summary)
    _write_json(validation_rows_path, {"rows": validation_rows})
    _write_json(validation_verdict_path, validation_verdict)

    if failed_count:
        raise ValueError(f"D40 validation failed for {failed_count} rows")

    return ExecutionPackageRequirementValidationResult(
        validation_id=validation_id,
        artifact_root=artifact_root.as_posix(),
        validation_schema_path=validation_schema_path.as_posix(),
        validation_summary_path=validation_summary_path.as_posix(),
        validation_rows_path=validation_rows_path.as_posix(),
        validation_verdict_path=validation_verdict_path.as_posix(),
        source_d39_proof_path=d39_proof_path.as_posix(),
        source_d39_artifact_root=str(d39_proof.get("artifact_root") or ""),
        candidate_count=len(rows),
        validated_row_count=len(rows) - failed_count,
        failed_row_count=failed_count,
        validation_status=validation_status,
    )


__all__ = [
    "D39_BATCH",
    "D39_ACCEPTED_FOR",
    "D40_VALIDATION_STATUS",
    "D39_ROW_STATUS",
    "D39_REQUIREMENT_STATUS",
    "REQUIRED_ROW_COLUMNS",
    "ExecutionPackageRequirementValidationResult",
    "validate_execution_package_requirements",
]
