from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FULL_UNIVERSE_COUNT = 810
DEFAULT_SUBSET_COUNT = 5

D41_SUBSET_ROW_STATUS = "CANDIDATE_SUBSET_SELECTED_FOR_LANE_CE_EXECUTION_NO_EXECUTION"
D41_HANDOFF_STATUS = "SUBSET_EXECUTION_HANDOFF_MANIFEST_READY_NO_EXECUTION"
D40_VALIDATION_STATUS = "EXECUTION_PACKAGE_REQUIREMENT_VALIDATED_NO_EXECUTION"
D39_ROW_STATUS = "PACKAGE_REQUIREMENT_READY_NO_EXECUTION"

SUBSET_ROW_COLUMNS = (
    "subset_id",
    "subset_rank",
    "candidate_id",
    "candidate_fingerprint",
    "package_requirement_id",
    "handoff_id",
    "planned_result_pack_root",
    "planned_result_pack_manifest_path",
    "recommended_owner",
    "replay_execution_owner",
    "planned_run_manifest_required",
    "planned_metrics_summary_required",
    "planned_trade_log_required",
    "planned_candidate_audit_required",
    "planned_decision_trace_required",
    "planned_integrity_report_required",
    "candidate_profile_required",
    "candidate_context_catalog_required",
    "lane_c_or_e_execution_required",
    "lane_d_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "model_prediction_performed",
    "subset_row_status",
    "remarks",
)


@dataclass(frozen=True)
class CandidateSubsetSelectionResult:
    selection_id: str
    artifact_root: str
    schema_path: str
    summary_path: str
    subset_rows_json_path: str
    subset_rows_csv_path: str
    handoff_manifest_json_path: str
    handoff_manifest_csv_path: str
    optimizer_verdict_path: str
    full_universe_count: int
    subset_count: int
    handoff_status: str


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
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


def _require_pass(path: Path, expected_batch: str) -> dict[str, Any]:
    proof = _load_json(path)
    if proof.get("verdict") != "PASS":
        raise ValueError(f"required proof is not PASS: {path}")
    if proof.get("batch") != expected_batch:
        raise ValueError(f"unexpected batch for {path}: {proof.get('batch')}")
    return proof


def _validate_d40(d40: dict[str, Any]) -> None:
    if d40.get("candidate_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D40 candidate_count expected {FULL_UNIVERSE_COUNT}, got {d40.get('candidate_count')}")
    if d40.get("validated_row_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D40 validated_row_count expected {FULL_UNIVERSE_COUNT}, got {d40.get('validated_row_count')}")
    if d40.get("failed_row_count") != 0:
        raise ValueError(f"D40 failed_row_count expected 0, got {d40.get('failed_row_count')}")
    if d40.get("validation_status") != D40_VALIDATION_STATUS:
        raise ValueError(f"unexpected D40 validation_status: {d40.get('validation_status')}")
    if d40.get("next_recommended_batch") != "LANE-D1-D41_CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION":
        raise ValueError(f"D40 does not point to D41: {d40.get('next_recommended_batch')}")

    safety = d40.get("safety", {})
    if safety.get("lane_c_or_e_execution_required") is not True:
        raise ValueError("D40 safety must require Lane C/E execution")
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
            raise ValueError(f"D40 safety failed: {key}")


def _validate_d39(d39: dict[str, Any]) -> None:
    if d39.get("candidate_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D39 candidate_count expected {FULL_UNIVERSE_COUNT}, got {d39.get('candidate_count')}")
    if d39.get("package_requirement_row_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D39 package row count expected {FULL_UNIVERSE_COUNT}, got {d39.get('package_requirement_row_count')}")
    if d39.get("package_requirement_ready_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D39 ready count expected {FULL_UNIVERSE_COUNT}, got {d39.get('package_requirement_ready_count')}")


def _validate_d39_row(row: dict[str, Any], idx: int) -> None:
    for key in (
        "candidate_id",
        "candidate_fingerprint",
        "package_requirement_id",
        "planned_result_pack_root",
        "planned_result_pack_manifest_path",
    ):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"D39 row {idx} missing/blank {key}")

    if row.get("package_row_status") != D39_ROW_STATUS:
        raise ValueError(f"D39 row {idx} has bad package_row_status={row.get('package_row_status')}")
    if row.get("lane_c_or_e_execution_required") is not True:
        raise ValueError(f"D39 row {idx} must require Lane C/E execution")

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
            raise ValueError(f"D39 row {idx} safety failed: {key}")


def select_candidate_subset_for_execution_handoff(
    selection_id: str,
    artifact_root: Path,
    root: Path | None = None,
    subset_count: int = DEFAULT_SUBSET_COUNT,
) -> CandidateSubsetSelectionResult:
    root = (root or Path.cwd()).resolve()
    artifact_root = artifact_root.resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    if subset_count <= 0:
        raise ValueError("subset_count must be positive")
    if subset_count > FULL_UNIVERSE_COUNT:
        raise ValueError("subset_count cannot exceed full universe count")

    d32 = _require_pass(root / "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json", "LANE-D-D32")
    d37 = _require_pass(root / "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json", "LANE-D-D37")
    d39 = _require_pass(root / "run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json", "LANE-D1-D39")
    d40 = _require_pass(root / "run/proofs/proof_lane_d_d40_execution_package_requirement_validator_latest.json", "LANE-D1-D40")

    if d32.get("candidate_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D32 candidate_count expected {FULL_UNIVERSE_COUNT}, got {d32.get('candidate_count')}")
    if d37.get("handoff_row_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D37 handoff_row_count expected {FULL_UNIVERSE_COUNT}, got {d37.get('handoff_row_count')}")
    if d37.get("handoff_ready_count") != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D37 handoff_ready_count expected {FULL_UNIVERSE_COUNT}, got {d37.get('handoff_ready_count')}")

    _validate_d39(d39)
    _validate_d40(d40)

    d39_rows_path = _resolve_path(str(d39.get("rows_json_path") or ""), root)
    d40_validation_rows_path = _resolve_path(str(d40.get("validation_rows_path") or ""), root)

    d39_rows = _extract_rows(_load_json(d39_rows_path))
    d40_validation_rows = _extract_rows(_load_json(d40_validation_rows_path))

    if len(d39_rows) != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D39 rows expected {FULL_UNIVERSE_COUNT}, got {len(d39_rows)}")
    if len(d40_validation_rows) != FULL_UNIVERSE_COUNT:
        raise ValueError(f"D40 validation rows expected {FULL_UNIVERSE_COUNT}, got {len(d40_validation_rows)}")

    validated_candidate_ids: set[str] = set()
    for idx, row in enumerate(d40_validation_rows, start=1):
        if row.get("validation_pass") is not True:
            raise ValueError(f"D40 validation row {idx} did not pass")
        if row.get("validation_status") != D40_VALIDATION_STATUS:
            raise ValueError(f"D40 validation row {idx} has bad status")
        candidate_id = str(row.get("candidate_id") or "").strip()
        if not candidate_id:
            raise ValueError(f"D40 validation row {idx} missing candidate_id")
        validated_candidate_ids.add(candidate_id)

    ordered_rows = sorted(d39_rows, key=lambda row: str(row.get("package_requirement_id") or ""))
    selected_source_rows = ordered_rows[:subset_count]

    subset_rows: list[dict[str, Any]] = []
    for rank, source in enumerate(selected_source_rows, start=1):
        _validate_d39_row(source, rank)
        candidate_id = str(source["candidate_id"]).strip()
        if candidate_id not in validated_candidate_ids:
            raise ValueError(f"selected candidate not validated by D40: {candidate_id}")

        subset_rows.append({
            "subset_id": selection_id,
            "subset_rank": rank,
            "candidate_id": candidate_id,
            "candidate_fingerprint": str(source["candidate_fingerprint"]).strip(),
            "package_requirement_id": str(source["package_requirement_id"]).strip(),
            "handoff_id": str(source.get("handoff_id") or "").strip(),
            "planned_result_pack_root": str(source["planned_result_pack_root"]).strip(),
            "planned_result_pack_manifest_path": str(source["planned_result_pack_manifest_path"]).strip(),
            "recommended_owner": str(source.get("recommended_owner") or "Lane E replay-data durable execution / artifact audit owner").strip(),
            "replay_execution_owner": str(source.get("replay_execution_owner") or "Lane C/E only").strip(),
            "planned_run_manifest_required": True,
            "planned_metrics_summary_required": True,
            "planned_trade_log_required": True,
            "planned_candidate_audit_required": True,
            "planned_decision_trace_required": True,
            "planned_integrity_report_required": True,
            "candidate_profile_required": True,
            "candidate_context_catalog_required": True,
            "lane_c_or_e_execution_required": True,
            "lane_d_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_created": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "subset_row_status": D41_SUBSET_ROW_STATUS,
            "remarks": "Selected for first tiny Lane C/E execution/materialization subset. Lane D1 does not execute replay or create result packs.",
        })

    schema = {
        "contract_version": "replay_optimization_d41_candidate_subset_execution_handoff_contract_v1",
        "selection_id": selection_id,
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "subset_count": subset_count,
        "selection_method": "deterministic_first_five_from_validated_d39_requirement_rows_sorted_by_package_requirement_id",
        "subset_row_columns": list(SUBSET_ROW_COLUMNS),
        "subset_row_status": D41_SUBSET_ROW_STATUS,
        "handoff_status": D41_HANDOFF_STATUS,
        "safety": {
            "full_universe_preserved": True,
            "lane_d_execution_allowed": False,
            "lane_c_or_e_execution_required": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_created": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
        },
    }

    handoff_manifest = {
        "contract_version": "replay_optimization_d41_candidate_subset_execution_handoff_contract_v1",
        "selection_id": selection_id,
        "handoff_manifest_id": f"{selection_id}_HANDOFF",
        "handoff_status": D41_HANDOFF_STATUS,
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "subset_count": len(subset_rows),
        "preserved_full_universe_source": str(d39_rows_path),
        "source_validation_rows": str(d40_validation_rows_path),
        "recommended_execution_owner": "Lane E replay-data durable execution / artifact audit owner unless Lane C runner/staging behavior changes are required",
        "lane_c_or_e_execution_required": True,
        "lane_d_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_created": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "real_pnl_calculation_performed": False,
        "model_training_performed": False,
        "model_prediction_performed": False,
        "package_requirements": {
            "planned_run_manifest_required": True,
            "planned_metrics_summary_required": True,
            "planned_trade_log_required": True,
            "planned_candidate_audit_required": True,
            "planned_decision_trace_required": True,
            "planned_integrity_report_required": True,
            "candidate_profile_required": True,
            "candidate_context_catalog_required": True
        },
        "candidates": subset_rows,
        "important_limitation": "This handoff manifest is not a result pack and not execution proof."
    }

    summary = {
        "selection_id": selection_id,
        "accepted_for": "CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION",
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "full_universe_preserved": True,
        "subset_count": len(subset_rows),
        "selected_candidate_ids": [row["candidate_id"] for row in subset_rows],
        "selection_method": "deterministic_first_five_from_validated_d39_requirement_rows_sorted_by_package_requirement_id",
        "handoff_status": D41_HANDOFF_STATUS,
        "lane_ce_next_external_step": "Lane C/E may use the D41 handoff manifest to execute/materialize only these five candidates under their lane ownership.",
        "important_limitation": "D41 does not execute replay, create real result packs, bind labels, calculate PnL, train/predict, or approve optimization.",
        "safety": {
            "full_universe_preserved": True,
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
        "next_recommended_batch": "LANE-D1-D42_POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION"
    }

    verdict = {
        "selection_id": selection_id,
        "verdict": "PASS",
        "accepted_for": "CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION",
        "full_universe_count": FULL_UNIVERSE_COUNT,
        "subset_count": len(subset_rows),
        "handoff_status": D41_HANDOFF_STATUS,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "next_recommended_batch": "LANE-D1-D42_POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION"
    }

    schema_path = artifact_root / "44_candidate_subset_selection_schema.json"
    summary_path = artifact_root / "44_candidate_subset_selection_summary.json"
    subset_rows_json_path = artifact_root / "44_candidate_subset_rows.json"
    subset_rows_csv_path = artifact_root / "44_candidate_subset_rows.csv"
    handoff_manifest_json_path = artifact_root / "44_execution_handoff_manifest.json"
    handoff_manifest_csv_path = artifact_root / "44_execution_handoff_manifest.csv"
    optimizer_verdict_path = artifact_root / "09_optimizer_verdict.json"

    _write_json(schema_path, schema)
    _write_json(summary_path, summary)
    _write_json(subset_rows_json_path, {"rows": subset_rows})
    _write_csv(subset_rows_csv_path, subset_rows, SUBSET_ROW_COLUMNS)
    _write_json(handoff_manifest_json_path, handoff_manifest)
    _write_csv(handoff_manifest_csv_path, subset_rows, SUBSET_ROW_COLUMNS)
    _write_json(optimizer_verdict_path, verdict)

    return CandidateSubsetSelectionResult(
        selection_id=selection_id,
        artifact_root=artifact_root.as_posix(),
        schema_path=schema_path.as_posix(),
        summary_path=summary_path.as_posix(),
        subset_rows_json_path=subset_rows_json_path.as_posix(),
        subset_rows_csv_path=subset_rows_csv_path.as_posix(),
        handoff_manifest_json_path=handoff_manifest_json_path.as_posix(),
        handoff_manifest_csv_path=handoff_manifest_csv_path.as_posix(),
        optimizer_verdict_path=optimizer_verdict_path.as_posix(),
        full_universe_count=FULL_UNIVERSE_COUNT,
        subset_count=len(subset_rows),
        handoff_status=D41_HANDOFF_STATUS,
    )


__all__ = [
    "FULL_UNIVERSE_COUNT",
    "DEFAULT_SUBSET_COUNT",
    "D41_SUBSET_ROW_STATUS",
    "D41_HANDOFF_STATUS",
    "CandidateSubsetSelectionResult",
    "select_candidate_subset_for_execution_handoff",
]
