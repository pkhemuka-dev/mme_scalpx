from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FULL_UNIVERSE_COUNT = 810
SUBSET_COUNT = 5

D42_SCHEMA_STATUS = "POST_RESULT_PACK_INGESTION_SCHEMA_READY_NO_EXECUTION"
D42_ROW_STATUS = "RESULT_PACK_INGESTION_REQUIREMENT_READY_NO_INGESTION"
D41_BATCH = "LANE-D1-D41"
D41_HANDOFF_STATUS = "SUBSET_EXECUTION_HANDOFF_MANIFEST_READY_NO_EXECUTION"

REQUIRED_RESULT_PACK_FILES = (
    "result_pack_manifest.json",
    "run_manifest.json",
    "metrics_summary.json",
    "trade_log.csv",
    "candidate_audit.csv",
    "decision_trace.json",
    "integrity_report.json",
)

REQUIRED_RESULT_PACK_MANIFEST_FIELDS = (
    "candidate_id",
    "candidate_fingerprint",
    "result_pack_id",
    "result_pack_root",
    "run_manifest_path",
    "metrics_summary_path",
    "trade_log_path",
    "candidate_audit_path",
    "decision_trace_path",
    "integrity_report_path",
    "execution_owner",
    "execution_lane",
    "replay_execution_performed",
    "result_pack_created",
    "result_pack_verified",
    "candidate_result_verified",
    "created_at",
)

INGESTION_REQUIREMENT_COLUMNS = (
    "ingestion_requirement_id",
    "candidate_id",
    "candidate_fingerprint",
    "subset_id",
    "subset_rank",
    "planned_result_pack_root",
    "expected_result_pack_manifest_path",
    "required_result_pack_files",
    "required_manifest_fields",
    "recommended_owner",
    "lane_c_or_e_execution_required",
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
    "ingestion_row_status",
    "remarks",
)


@dataclass(frozen=True)
class PostResultPackIngestionSchemaResult:
    schema_id: str
    artifact_root: str
    ingestion_schema_path: str
    acceptance_requirements_path: str
    ingestion_summary_path: str
    label_binding_precondition_stub_path: str
    optimizer_verdict_path: str
    full_universe_count: int
    subset_count: int
    schema_status: str


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_csv_compatible_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for row in rows:
        out: dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, (list, dict)):
                out[key] = json.dumps(value, sort_keys=True)
            else:
                out[key] = value
        converted.append(out)
    return converted


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in _write_csv_compatible_rows(rows):
            writer.writerow(row)


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
    raise ValueError("payload does not contain a rows list")


def _validate_d41_proof(d41: dict[str, Any]) -> None:
    if d41.get("verdict") != "PASS":
        raise ValueError("D41 proof is not PASS")
    if d41.get("batch") != D41_BATCH:
        raise ValueError(f"unexpected D41 batch: {d41.get('batch')}")
    if d41.get("full_universe_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D41 full_universe_count expected {FULL_UNIVERSE_COUNT}")
    if d41.get("full_universe_preserved") is not True:
        raise ValueError("D41 must preserve full universe")
    if d41.get("subset_count") != SUBSET_COUNT:
        raise ValueError(f"D41 subset_count expected {SUBSET_COUNT}")
    if d41.get("handoff_status") != D41_HANDOFF_STATUS:
        raise ValueError(f"D41 handoff_status unexpected: {d41.get('handoff_status')}")
    if d41.get("next_recommended_batch") != "LANE-D1-D42_POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION":
        raise ValueError(f"D41 does not point to D42: {d41.get('next_recommended_batch')}")

    safety = d41.get("safety", {})
    if safety.get("full_universe_preserved") is not True:
        raise ValueError("D41 safety must preserve full universe")
    if safety.get("lane_c_or_e_execution_required") is not True:
        raise ValueError("D41 safety must require Lane C/E execution")
    for key in (
        "lane_d_execution_allowed",
        "replay_execution_allowed",
        "replay_execution_performed",
        "result_pack_creation_allowed_in_lane_d",
        "result_pack_created",
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
            raise ValueError(f"D41 safety failed: {key}")


def _validate_subset_row(row: dict[str, Any], idx: int) -> None:
    for key in (
        "candidate_id",
        "candidate_fingerprint",
        "subset_id",
        "subset_rank",
        "planned_result_pack_root",
        "planned_result_pack_manifest_path",
        "recommended_owner",
    ):
        if key not in row:
            raise ValueError(f"D41 subset row {idx} missing {key}")

    if row.get("lane_c_or_e_execution_required") is not True:
        raise ValueError(f"D41 subset row {idx} must require Lane C/E execution")

    for key in (
        "lane_d_execution_allowed",
        "replay_execution_performed",
        "result_pack_created",
        "label_binding_allowed",
        "labels_bound",
        "real_pnl_calculation_performed",
        "model_training_performed",
        "model_prediction_performed",
    ):
        if row.get(key) is not False:
            raise ValueError(f"D41 subset row {idx} safety failed: {key}")


def write_post_result_pack_ingestion_schema(
    schema_id: str,
    artifact_root: Path,
    root: Path | None = None,
) -> PostResultPackIngestionSchemaResult:
    root = (root or Path.cwd()).resolve()
    artifact_root = artifact_root.resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    d41_path = root / "run/proofs/proof_lane_d_d41_candidate_subset_selection_latest.json"
    d41 = _load_json(d41_path)
    _validate_d41_proof(d41)

    subset_rows_path = _resolve_path(str(d41.get("subset_rows_json_path") or ""), root)
    handoff_manifest_path = _resolve_path(str(d41.get("handoff_manifest_json_path") or ""), root)

    subset_rows = _extract_rows(_load_json(subset_rows_path))
    handoff_manifest = _load_json(handoff_manifest_path)

    if len(subset_rows) != SUBSET_COUNT:
        raise ValueError(f"D41 subset rows expected {SUBSET_COUNT}, got {len(subset_rows)}")
    if handoff_manifest.get("subset_count") != SUBSET_COUNT:
        raise ValueError(f"D41 handoff manifest subset_count expected {SUBSET_COUNT}")
    if handoff_manifest.get("full_universe_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D41 handoff manifest full_universe_count expected {FULL_UNIVERSE_COUNT}")
    if handoff_manifest.get("handoff_status") != D41_HANDOFF_STATUS:
        raise ValueError(f"D41 handoff manifest status unexpected: {handoff_manifest.get('handoff_status')}")

    requirement_rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for idx, row in enumerate(sorted(subset_rows, key=lambda x: int(x.get("subset_rank") or 0)), start=1):
        _validate_subset_row(row, idx)

        candidate_id = str(row.get("candidate_id") or "").strip()
        fingerprint = str(row.get("candidate_fingerprint") or "").strip()
        planned_root = str(row.get("planned_result_pack_root") or "").strip()

        if not candidate_id:
            raise ValueError(f"subset row {idx} missing candidate_id")
        if candidate_id in seen:
            raise ValueError(f"duplicate candidate in subset: {candidate_id}")
        seen.add(candidate_id)

        requirement_rows.append({
            "ingestion_requirement_id": f"INGREQ_{idx:03d}",
            "candidate_id": candidate_id,
            "candidate_fingerprint": fingerprint,
            "subset_id": str(row.get("subset_id") or schema_id),
            "subset_rank": int(row.get("subset_rank") or idx),
            "planned_result_pack_root": planned_root,
            "expected_result_pack_manifest_path": f"{planned_root}/result_pack_manifest.json",
            "required_result_pack_files": list(REQUIRED_RESULT_PACK_FILES),
            "required_manifest_fields": list(REQUIRED_RESULT_PACK_MANIFEST_FIELDS),
            "recommended_owner": str(row.get("recommended_owner") or "Lane E replay-data durable execution / artifact audit owner"),
            "lane_c_or_e_execution_required": True,
            "lane_d_execution_allowed": False,
            "result_pack_exists_checked": False,
            "result_pack_verified": False,
            "result_pack_ingestion_performed": False,
            "candidate_result_verified": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "ingestion_row_status": D42_ROW_STATUS,
            "remarks": "Schema/requirement row only. Actual result-pack discovery, verification, ingestion, label binding, PnL, and ML remain blocked until Lane C/E provides verified candidate-specific result packs.",
        })

    ingestion_schema = {
        "contract_version": "replay_optimization_d42_post_result_pack_ingestion_schema_contract_v1",
        "schema_id": schema_id,
        "schema_status": D42_SCHEMA_STATUS,
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "subset_count": SUBSET_COUNT,
        "source_d41_proof_path": d41_path.as_posix(),
        "source_subset_rows_path": subset_rows_path.as_posix(),
        "source_handoff_manifest_path": handoff_manifest_path.as_posix(),
        "ingestion_requirement_columns": list(INGESTION_REQUIREMENT_COLUMNS),
        "required_result_pack_files": list(REQUIRED_RESULT_PACK_FILES),
        "required_result_pack_manifest_fields": list(REQUIRED_RESULT_PACK_MANIFEST_FIELDS),
        "acceptance_gate_order": [
            "candidate_identity_match",
            "candidate_fingerprint_match",
            "required_files_present",
            "manifest_fields_present",
            "execution_owner_is_lane_c_or_e",
            "replay_execution_performed_true",
            "result_pack_created_true",
            "integrity_report_pass",
            "candidate_result_verified_true",
            "no_lane_d_execution_claim",
            "no_label_binding_before_acceptance"
        ],
        "safety": {
            "schema_only": True,
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
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False
        }
    }

    acceptance_requirements = {
        "schema_id": schema_id,
        "schema_status": D42_SCHEMA_STATUS,
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "subset_count": SUBSET_COUNT,
        "ingestion_requirements": requirement_rows,
        "important_limitation": "These are acceptance requirements only. No real result pack has been checked, ingested, or accepted by D42.",
    }

    summary = {
        "schema_id": schema_id,
        "accepted_for": "POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION",
        "schema_status": D42_SCHEMA_STATUS,
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "full_universe_preserved": True,
        "subset_count": SUBSET_COUNT,
        "selected_candidate_ids": [row["candidate_id"] for row in requirement_rows],
        "ingestion_requirement_count": len(requirement_rows),
        "result_pack_exists_checked": False,
        "result_pack_verified_count": 0,
        "result_pack_ingestion_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "important_limitation": "D42 defines future ingestion schema only. It does not inspect, ingest, validate, create, or accept real result packs.",
        "safety": {
            "schema_only": True,
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
        "next_recommended_batch": "LANE-D1-D43_LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION"
    }

    label_binding_precondition_stub = {
        "schema_id": schema_id,
        "precondition_contract": "label_binding_requires_verified_candidate_specific_result_pack",
        "label_binding_precondition_status": "BLOCKED_UNTIL_VERIFIED_RESULT_PACKS_EXIST",
        "subset_count": SUBSET_COUNT,
        "required_verified_result_pack_count": SUBSET_COUNT,
        "current_verified_result_pack_count": 0,
        "label_binding_allowed": False,
        "labels_bound": False,
        "blocking_reasons": [
            "real_result_packs_not_supplied_to_lane_d1",
            "result_pack_verification_not_performed",
            "candidate_result_verified_false",
            "pnl_not_calculated",
            "no_labels_available"
        ],
        "next_validator": "LANE-D1-D43_LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION"
    }

    verdict = {
        "schema_id": schema_id,
        "verdict": "PASS",
        "accepted_for": "POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION",
        "schema_status": D42_SCHEMA_STATUS,
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "subset_count": SUBSET_COUNT,
        "ingestion_requirement_count": len(requirement_rows),
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "result_pack_ingestion_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "next_recommended_batch": "LANE-D1-D43_LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION"
    }

    ingestion_schema_path = artifact_root / "45_post_result_pack_ingestion_schema.json"
    acceptance_requirements_path = artifact_root / "45_result_pack_acceptance_requirements.json"
    acceptance_requirements_csv_path = artifact_root / "45_result_pack_acceptance_requirements.csv"
    ingestion_summary_path = artifact_root / "45_post_result_pack_ingestion_summary.json"
    label_binding_precondition_stub_path = artifact_root / "45_label_binding_precondition_stub.json"
    optimizer_verdict_path = artifact_root / "09_optimizer_verdict.json"

    _write_json(ingestion_schema_path, ingestion_schema)
    _write_json(acceptance_requirements_path, acceptance_requirements)
    _write_csv(acceptance_requirements_csv_path, requirement_rows, INGESTION_REQUIREMENT_COLUMNS)
    _write_json(ingestion_summary_path, summary)
    _write_json(label_binding_precondition_stub_path, label_binding_precondition_stub)
    _write_json(optimizer_verdict_path, verdict)

    return PostResultPackIngestionSchemaResult(
        schema_id=schema_id,
        artifact_root=artifact_root.as_posix(),
        ingestion_schema_path=ingestion_schema_path.as_posix(),
        acceptance_requirements_path=acceptance_requirements_path.as_posix(),
        ingestion_summary_path=ingestion_summary_path.as_posix(),
        label_binding_precondition_stub_path=label_binding_precondition_stub_path.as_posix(),
        optimizer_verdict_path=optimizer_verdict_path.as_posix(),
        full_universe_count=FULL_UNIVERSE_COUNT,
        subset_count=SUBSET_COUNT,
        schema_status=D42_SCHEMA_STATUS,
    )


__all__ = [
    "FULL_UNIVERSE_COUNT",
    "SUBSET_COUNT",
    "D42_SCHEMA_STATUS",
    "D42_ROW_STATUS",
    "REQUIRED_RESULT_PACK_FILES",
    "REQUIRED_RESULT_PACK_MANIFEST_FIELDS",
    "INGESTION_REQUIREMENT_COLUMNS",
    "PostResultPackIngestionSchemaResult",
    "write_post_result_pack_ingestion_schema",
]
