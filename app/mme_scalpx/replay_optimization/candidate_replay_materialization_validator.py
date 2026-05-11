"""Lane D D35 candidate replay materialization validator.

This module validates D34 candidate replay materialization contract rows before
any future candidate-specific replay/result-pack materialization.

D35 is validator-only. It does not execute replay, create result packs, write
candidate artifacts, attach candidate context, perform matching, bind labels,
calculate PnL, train/predict models, call brokers, write live Redis, mutate
doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_CONTRACT_VERSION = "replay_optimization_d35_candidate_replay_materialization_validator_contract_v1"
CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_ACCEPTED_FOR = "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_NO_EXECUTION"

VALIDATION_STATUS_PASS_NO_EXECUTION = "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATION_PASS_NO_EXECUTION"
VALIDATION_STATUS_BLOCKED_NO_MATERIALIZATION_ROWS = "BLOCKED_NO_D34_MATERIALIZATION_ROWS"
VALIDATION_STATUS_BLOCKED_DUPLICATE_MATERIALIZATION_IDS = "BLOCKED_DUPLICATE_MATERIALIZATION_IDS"
VALIDATION_STATUS_BLOCKED_DUPLICATE_CANDIDATE_IDS = "BLOCKED_DUPLICATE_CANDIDATE_IDS"
VALIDATION_STATUS_BLOCKED_MISSING_REQUIRED_FIELDS = "BLOCKED_MISSING_REQUIRED_MATERIALIZATION_FIELDS"
VALIDATION_STATUS_BLOCKED_PATH_POLICY_VIOLATION = "BLOCKED_MATERIALIZATION_PATH_POLICY_VIOLATION"
VALIDATION_STATUS_BLOCKED_SAFETY_FLAG_VIOLATION = "BLOCKED_SAFETY_FLAG_VIOLATION"
VALIDATION_STATUS_BLOCKED_UNEXPECTED_EXECUTION_STATE = "BLOCKED_UNEXPECTED_EXECUTION_STATE"

ROW_STATUS_VALID_NO_EXECUTION = "VALID_MATERIALIZATION_PLAN_NO_EXECUTION"
ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD = "INVALID_MISSING_REQUIRED_FIELD"
ROW_STATUS_INVALID_PATH_POLICY = "INVALID_PATH_POLICY"
ROW_STATUS_INVALID_SAFETY_FLAG = "INVALID_SAFETY_FLAG"
ROW_STATUS_INVALID_EXECUTION_STATE = "INVALID_EXECUTION_STATE"

REQUIRED_MATERIALIZATION_FIELDS = (
    "materialization_id",
    "plan_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_profile_id",
    "planned_result_pack_id",
    "planned_result_pack_root",
    "candidate_profile_path",
    "candidate_replay_manifest_path",
    "candidate_effective_inputs_path",
    "candidate_result_pack_manifest_path",
    "candidate_integrity_report_path",
    "candidate_result_context_catalog_path",
    "candidate_label_binding_precondition_path",
    "required_artifact_count",
    "materialization_row_status",
)

EXPECTED_ARTIFACT_PATH_SUFFIXES = (
    "candidate_profile.json",
    "candidate_replay_manifest.json",
    "candidate_effective_inputs.json",
    "candidate_result_pack_manifest.json",
    "candidate_integrity_report.json",
    "candidate_result_context_catalog.json",
    "candidate_label_binding_precondition.json",
)

PATH_FIELDS = (
    "candidate_profile_path",
    "candidate_replay_manifest_path",
    "candidate_effective_inputs_path",
    "candidate_result_pack_manifest_path",
    "candidate_integrity_report_path",
    "candidate_result_context_catalog_path",
    "candidate_label_binding_precondition_path",
)

FALSE_SAFETY_FIELDS = (
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
)

VALIDATION_COLUMNS = (
    "optimization_id",
    "validation_id",
    "materialization_id",
    "plan_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_result_pack_id",
    "planned_result_pack_root",
    "required_fields_present",
    "artifact_path_count_ok",
    "artifact_paths_under_candidate_root",
    "artifact_suffixes_ok",
    "false_safety_fields_ok",
    "planned_no_execution_ok",
    "validation_row_status",
    "missing_required_fields",
    "invalid_path_fields",
    "invalid_safety_fields",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateReplayMaterializationValidationRow:
    optimization_id: str
    validation_id: str
    materialization_id: str | None
    plan_id: str | None
    candidate_id: str | None
    candidate_fingerprint: str | None
    planned_result_pack_id: str | None
    planned_result_pack_root: str | None
    required_fields_present: bool
    artifact_path_count_ok: bool
    artifact_paths_under_candidate_root: bool
    artifact_suffixes_ok: bool
    false_safety_fields_ok: bool
    planned_no_execution_ok: bool
    validation_row_status: str
    missing_required_fields: str
    invalid_path_fields: str
    invalid_safety_fields: str
    replay_execution_allowed: bool = False
    replay_execution_performed: bool = False
    result_pack_created: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateReplayMaterializationValidatorBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    materialization_rows_path: str | None
    validation_report_path: str
    validation_rows_json_path: str
    validation_rows_csv_path: str
    optimizer_verdict_path: str
    materialization_row_count: int
    validation_row_count: int
    valid_no_execution_count: int
    invalid_row_count: int
    duplicate_materialization_id_count: int
    duplicate_candidate_id_count: int
    missing_required_field_row_count: int
    path_policy_violation_row_count: int
    safety_violation_row_count: int
    unexpected_execution_state_row_count: int
    validation_status: str
    replay_execution_allowed: bool = False
    replay_execution_performed: bool = False
    result_pack_created: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    real_pnl_calculation_performed: bool = False
    model_training_performed: bool = False
    model_prediction_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_json(path_value: str | Path | None) -> Any:
    if not path_value:
        return None
    p = Path(path_value)
    if not p.exists() or not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _rows_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("rows", "items", "records", "data", "results"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, dict)]
    return []


def _output_guard(output_dir: str | Path) -> Path:
    out = Path(output_dir)
    normalized = out.as_posix().rstrip("/")
    allowed_guard = "/" + OUTPUT_ROOT.strip("/") + "/"
    normalized_guard = "/" + normalized.strip("/") + "/"
    if not (
        normalized == OUTPUT_ROOT
        or normalized.startswith(OUTPUT_ROOT + "/")
        or normalized.startswith("run/replay_optimization/")
        or allowed_guard in normalized_guard
    ):
        raise ValueError(f"D35 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _truthy_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _count_duplicates(values: Sequence[str]) -> int:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if value in seen:
            dup.add(value)
        seen.add(value)
    return len(dup)


def _path_policy_errors(row: Mapping[str, Any]) -> tuple[str, ...]:
    root = str(row.get("planned_result_pack_root") or "").rstrip("/")
    candidate_id = str(row.get("candidate_id") or "").strip()
    errors: list[str] = []

    if not root or not candidate_id:
        return tuple(PATH_FIELDS)

    if not root.startswith("run/replay_optimization/candidate_replays/"):
        errors.append("planned_result_pack_root")

    if candidate_id not in root:
        errors.append("planned_result_pack_root_candidate_id")

    for field, suffix in zip(PATH_FIELDS, EXPECTED_ARTIFACT_PATH_SUFFIXES):
        value = str(row.get(field) or "")
        if not value:
            errors.append(field)
            continue
        if not value.startswith(root + "/"):
            errors.append(field)
        if not value.endswith("/" + suffix):
            errors.append(field + "_suffix")

    return tuple(sorted(set(errors)))


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def build_candidate_replay_materialization_validation_rows(
    optimization_id: str,
    *,
    materialization_rows_path: str | Path | None,
) -> tuple[CandidateReplayMaterializationValidationRow, ...]:
    materialization_rows = _rows_from_payload(_safe_load_json(materialization_rows_path))
    out: list[CandidateReplayMaterializationValidationRow] = []

    for idx, row in enumerate(materialization_rows, start=1):
        missing_required = tuple(
            field for field in REQUIRED_MATERIALIZATION_FIELDS
            if not _truthy_present(row.get(field))
        )
        invalid_safety = tuple(
            field for field in FALSE_SAFETY_FIELDS
            if row.get(field) is not False
        )
        path_errors = _path_policy_errors(row)

        artifact_path_count_ok = int(row.get("required_artifact_count") or 0) == len(EXPECTED_ARTIFACT_PATH_SUFFIXES)
        required_ok = not missing_required
        safety_ok = not invalid_safety
        path_ok = not path_errors
        planned_no_execution_ok = row.get("materialization_row_status") == "MATERIALIZATION_PLANNED_NO_EXECUTION"

        if not required_ok:
            status = ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD
            remarks = "Materialization row is missing required artifact-planning fields."
        elif not artifact_path_count_ok or not path_ok:
            status = ROW_STATUS_INVALID_PATH_POLICY
            remarks = "Materialization artifact paths do not satisfy candidate-root policy."
        elif not safety_ok:
            status = ROW_STATUS_INVALID_SAFETY_FLAG
            remarks = "Materialization row has unsafe execution/label flags."
        elif not planned_no_execution_ok:
            status = ROW_STATUS_INVALID_EXECUTION_STATE
            remarks = "Materialization row is not in planned/no-execution state."
        else:
            status = ROW_STATUS_VALID_NO_EXECUTION
            remarks = "Materialization row is valid for future materialization chain only; no execution is allowed."

        out.append(
            CandidateReplayMaterializationValidationRow(
                optimization_id=optimization_id,
                validation_id=f"MATVAL_{idx:06d}",
                materialization_id=str(row.get("materialization_id")) if row.get("materialization_id") is not None else None,
                plan_id=str(row.get("plan_id")) if row.get("plan_id") is not None else None,
                candidate_id=str(row.get("candidate_id")) if row.get("candidate_id") is not None else None,
                candidate_fingerprint=str(row.get("candidate_fingerprint")) if row.get("candidate_fingerprint") is not None else None,
                planned_result_pack_id=str(row.get("planned_result_pack_id")) if row.get("planned_result_pack_id") is not None else None,
                planned_result_pack_root=str(row.get("planned_result_pack_root")) if row.get("planned_result_pack_root") is not None else None,
                required_fields_present=required_ok,
                artifact_path_count_ok=artifact_path_count_ok,
                artifact_paths_under_candidate_root=path_ok,
                artifact_suffixes_ok=path_ok,
                false_safety_fields_ok=safety_ok,
                planned_no_execution_ok=planned_no_execution_ok,
                validation_row_status=status,
                missing_required_fields=",".join(missing_required),
                invalid_path_fields=",".join(path_errors),
                invalid_safety_fields=",".join(invalid_safety),
                replay_execution_allowed=False,
                replay_execution_performed=False,
                result_pack_created=False,
                candidate_context_attached=False,
                candidate_trade_matching_allowed=False,
                label_binding_allowed=False,
                labels_bound=False,
                remarks=remarks,
            )
        )

    return tuple(out)


def write_candidate_replay_materialization_validation(
    optimization_id: str,
    output_dir: str | Path,
    *,
    materialization_rows_path: str | Path | None,
) -> CandidateReplayMaterializationValidatorBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    materialization_rows = _rows_from_payload(_safe_load_json(materialization_rows_path))
    validation_rows = build_candidate_replay_materialization_validation_rows(
        optimization_id,
        materialization_rows_path=materialization_rows_path,
    )
    validation_dicts = [asdict(row) for row in validation_rows]

    valid_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_VALID_NO_EXECUTION)
    invalid_count = len(validation_rows) - valid_count
    missing_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD)
    path_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_INVALID_PATH_POLICY)
    safety_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_INVALID_SAFETY_FLAG)
    state_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_INVALID_EXECUTION_STATE)

    materialization_ids = [str(row.get("materialization_id")) for row in materialization_rows if row.get("materialization_id")]
    candidate_ids = [str(row.get("candidate_id")) for row in materialization_rows if row.get("candidate_id")]

    duplicate_materialization_ids = _count_duplicates(materialization_ids)
    duplicate_candidate_ids = _count_duplicates(candidate_ids)

    if not materialization_rows:
        status = VALIDATION_STATUS_BLOCKED_NO_MATERIALIZATION_ROWS
    elif duplicate_materialization_ids:
        status = VALIDATION_STATUS_BLOCKED_DUPLICATE_MATERIALIZATION_IDS
    elif duplicate_candidate_ids:
        status = VALIDATION_STATUS_BLOCKED_DUPLICATE_CANDIDATE_IDS
    elif missing_count:
        status = VALIDATION_STATUS_BLOCKED_MISSING_REQUIRED_FIELDS
    elif path_count:
        status = VALIDATION_STATUS_BLOCKED_PATH_POLICY_VIOLATION
    elif safety_count:
        status = VALIDATION_STATUS_BLOCKED_SAFETY_FLAG_VIOLATION
    elif state_count:
        status = VALIDATION_STATUS_BLOCKED_UNEXPECTED_EXECUTION_STATE
    else:
        status = VALIDATION_STATUS_PASS_NO_EXECUTION

    report_path = out / "38_candidate_replay_materialization_validation_report.json"
    rows_json_path = out / "38_candidate_replay_materialization_validation_rows.json"
    rows_csv_path = out / "38_candidate_replay_materialization_validation_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
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
    }

    report = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Materialization Validator",
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "materialization_rows_path": str(materialization_rows_path) if materialization_rows_path else None,
        "materialization_row_count": len(materialization_rows),
        "validation_row_count": len(validation_rows),
        "valid_no_execution_count": valid_count,
        "invalid_row_count": invalid_count,
        "duplicate_materialization_id_count": duplicate_materialization_ids,
        "duplicate_candidate_id_count": duplicate_candidate_ids,
        "missing_required_field_row_count": missing_count,
        "path_policy_violation_row_count": path_count,
        "safety_violation_row_count": safety_count,
        "unexpected_execution_state_row_count": state_count,
        "validation_status": status,
        "important_limitation": (
            "D35 validates materialization artifact-plan rows only. It does not execute "
            "candidate replays, create artifacts/result packs, attach context, match trades, or bind labels."
        ),
        "rows": validation_dicts,
        "safety": safety,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Materialization Validation Rows",
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "validation_status": status,
        "rows": validation_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, VALIDATION_COLUMNS, validation_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_ACCEPTED_FOR,
        "validation_status": status,
        "materialization_row_count": len(materialization_rows),
        "validation_row_count": len(validation_rows),
        "valid_no_execution_count": valid_count,
        "invalid_row_count": invalid_count,
        "duplicate_materialization_id_count": duplicate_materialization_ids,
        "duplicate_candidate_id_count": duplicate_candidate_ids,
        "missing_required_field_row_count": missing_count,
        "path_policy_violation_row_count": path_count,
        "safety_violation_row_count": safety_count,
        "unexpected_execution_state_row_count": state_count,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_created": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D35 validates materialization plan rows only. No execution.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateReplayMaterializationValidatorBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_CONTRACT_VERSION,
        accepted_for=CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_ACCEPTED_FOR,
        materialization_rows_path=str(materialization_rows_path) if materialization_rows_path else None,
        validation_report_path=report_path.as_posix(),
        validation_rows_json_path=rows_json_path.as_posix(),
        validation_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        materialization_row_count=len(materialization_rows),
        validation_row_count=len(validation_rows),
        valid_no_execution_count=valid_count,
        invalid_row_count=invalid_count,
        duplicate_materialization_id_count=duplicate_materialization_ids,
        duplicate_candidate_id_count=duplicate_candidate_ids,
        missing_required_field_row_count=missing_count,
        path_policy_violation_row_count=path_count,
        safety_violation_row_count=safety_count,
        unexpected_execution_state_row_count=state_count,
        validation_status=status,
    )


__all__ = (
    "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_CONTRACT_VERSION",
    "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_ACCEPTED_FOR",
    "VALIDATION_STATUS_PASS_NO_EXECUTION",
    "VALIDATION_STATUS_BLOCKED_NO_MATERIALIZATION_ROWS",
    "VALIDATION_STATUS_BLOCKED_DUPLICATE_MATERIALIZATION_IDS",
    "VALIDATION_STATUS_BLOCKED_DUPLICATE_CANDIDATE_IDS",
    "VALIDATION_STATUS_BLOCKED_MISSING_REQUIRED_FIELDS",
    "VALIDATION_STATUS_BLOCKED_PATH_POLICY_VIOLATION",
    "VALIDATION_STATUS_BLOCKED_SAFETY_FLAG_VIOLATION",
    "VALIDATION_STATUS_BLOCKED_UNEXPECTED_EXECUTION_STATE",
    "ROW_STATUS_VALID_NO_EXECUTION",
    "ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD",
    "ROW_STATUS_INVALID_PATH_POLICY",
    "ROW_STATUS_INVALID_SAFETY_FLAG",
    "ROW_STATUS_INVALID_EXECUTION_STATE",
    "REQUIRED_MATERIALIZATION_FIELDS",
    "EXPECTED_ARTIFACT_PATH_SUFFIXES",
    "PATH_FIELDS",
    "FALSE_SAFETY_FIELDS",
    "VALIDATION_COLUMNS",
    "CandidateReplayMaterializationValidationRow",
    "CandidateReplayMaterializationValidatorBuildResult",
    "build_candidate_replay_materialization_validation_rows",
    "write_candidate_replay_materialization_validation",
)
