"""Lane D D33 candidate replay binding plan validator.

This module validates D32 candidate replay binding plan rows before any future
candidate-specific replay materialization.

D33 is validator-only. It does not execute replay, create result packs, attach
candidate context, perform candidate-to-trade matching, bind labels, calculate
PnL, train/predict models, call brokers, write live Redis, mutate doctrine, or
approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_CONTRACT_VERSION = "replay_optimization_d33_candidate_replay_binding_plan_validator_contract_v1"
CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_ACCEPTED_FOR = "CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_NO_EXECUTION"

VALIDATION_STATUS_PASS_NO_EXECUTION = "CANDIDATE_REPLAY_BINDING_PLAN_VALIDATION_PASS_NO_EXECUTION"
VALIDATION_STATUS_BLOCKED_NO_PLAN_ROWS = "BLOCKED_NO_D32_PLAN_ROWS"
VALIDATION_STATUS_BLOCKED_DUPLICATE_PLAN_IDS = "BLOCKED_DUPLICATE_PLAN_IDS"
VALIDATION_STATUS_BLOCKED_DUPLICATE_CANDIDATE_IDS = "BLOCKED_DUPLICATE_CANDIDATE_IDS"
VALIDATION_STATUS_BLOCKED_MISSING_REQUIRED_PLAN_FIELDS = "BLOCKED_MISSING_REQUIRED_PLAN_FIELDS"
VALIDATION_STATUS_BLOCKED_SAFETY_FLAG_VIOLATION = "BLOCKED_SAFETY_FLAG_VIOLATION"
VALIDATION_STATUS_BLOCKED_UNEXPECTED_EXECUTION_STATE = "BLOCKED_UNEXPECTED_EXECUTION_STATE"

ROW_STATUS_VALID_NO_EXECUTION = "VALID_NO_EXECUTION"
ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD = "INVALID_MISSING_REQUIRED_FIELD"
ROW_STATUS_INVALID_SAFETY_FLAG = "INVALID_SAFETY_FLAG"
ROW_STATUS_INVALID_EXECUTION_STATE = "INVALID_EXECUTION_STATE"

REQUIRED_PLAN_FIELDS = (
    "plan_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_replay_scope",
    "planned_replay_mode",
    "planned_profile_id",
    "planned_result_pack_id",
    "planned_result_pack_root",
    "planned_integrity_required",
    "planned_context_catalog_required",
    "candidate_context_bridge_required",
    "plan_row_status",
)

FALSE_SAFETY_FIELDS = (
    "label_binding_allowed",
    "labels_bound",
)

TRUE_REQUIREMENT_FIELDS = (
    "planned_integrity_required",
    "planned_context_catalog_required",
    "candidate_context_bridge_required",
)

VALIDATION_COLUMNS = (
    "optimization_id",
    "validation_id",
    "plan_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_profile_id",
    "planned_result_pack_id",
    "planned_result_pack_root",
    "required_fields_present",
    "false_safety_fields_ok",
    "true_requirement_fields_ok",
    "planned_no_execution_ok",
    "validation_row_status",
    "missing_required_fields",
    "invalid_safety_fields",
    "invalid_requirement_fields",
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
class CandidateReplayBindingPlanValidationRow:
    optimization_id: str
    validation_id: str
    plan_id: str | None
    candidate_id: str | None
    candidate_fingerprint: str | None
    planned_profile_id: str | None
    planned_result_pack_id: str | None
    planned_result_pack_root: str | None
    required_fields_present: bool
    false_safety_fields_ok: bool
    true_requirement_fields_ok: bool
    planned_no_execution_ok: bool
    validation_row_status: str
    missing_required_fields: str
    invalid_safety_fields: str
    invalid_requirement_fields: str
    replay_execution_allowed: bool = False
    replay_execution_performed: bool = False
    result_pack_created: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateReplayBindingPlanValidatorBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    plan_rows_path: str | None
    validation_report_path: str
    validation_rows_json_path: str
    validation_rows_csv_path: str
    optimizer_verdict_path: str
    plan_row_count: int
    validation_row_count: int
    valid_no_execution_count: int
    invalid_row_count: int
    duplicate_plan_id_count: int
    duplicate_candidate_id_count: int
    missing_required_field_row_count: int
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
        raise ValueError(f"D33 output must stay under {OUTPUT_ROOT}: {output_dir}")
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


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def build_candidate_replay_binding_plan_validation_rows(
    optimization_id: str,
    *,
    plan_rows_path: str | Path | None,
) -> tuple[CandidateReplayBindingPlanValidationRow, ...]:
    plan_rows = _rows_from_payload(_safe_load_json(plan_rows_path))
    out: list[CandidateReplayBindingPlanValidationRow] = []

    for idx, row in enumerate(plan_rows, start=1):
        missing_required = tuple(
            field for field in REQUIRED_PLAN_FIELDS
            if not _truthy_present(row.get(field))
        )
        invalid_safety = tuple(
            field for field in FALSE_SAFETY_FIELDS
            if row.get(field) is not False
        )
        invalid_requirement = tuple(
            field for field in TRUE_REQUIREMENT_FIELDS
            if row.get(field) is not True
        )

        required_ok = not missing_required
        safety_ok = not invalid_safety
        requirement_ok = not invalid_requirement
        planned_no_execution_ok = row.get("plan_row_status") == "PLANNED_NO_EXECUTION"

        if not required_ok:
            status = ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD
            remarks = "Plan row is missing required future replay-binding planning fields."
        elif not safety_ok:
            status = ROW_STATUS_INVALID_SAFETY_FLAG
            remarks = "Plan row has unsafe label safety flags."
        elif not requirement_ok or not planned_no_execution_ok:
            status = ROW_STATUS_INVALID_EXECUTION_STATE
            remarks = "Plan row is not in strict planned/no-execution state."
        else:
            status = ROW_STATUS_VALID_NO_EXECUTION
            remarks = "Plan row is valid for future validator chain only; no execution is allowed."

        out.append(
            CandidateReplayBindingPlanValidationRow(
                optimization_id=optimization_id,
                validation_id=f"PLANVAL_{idx:06d}",
                plan_id=str(row.get("plan_id")) if row.get("plan_id") is not None else None,
                candidate_id=str(row.get("candidate_id")) if row.get("candidate_id") is not None else None,
                candidate_fingerprint=str(row.get("candidate_fingerprint")) if row.get("candidate_fingerprint") is not None else None,
                planned_profile_id=str(row.get("planned_profile_id")) if row.get("planned_profile_id") is not None else None,
                planned_result_pack_id=str(row.get("planned_result_pack_id")) if row.get("planned_result_pack_id") is not None else None,
                planned_result_pack_root=str(row.get("planned_result_pack_root")) if row.get("planned_result_pack_root") is not None else None,
                required_fields_present=required_ok,
                false_safety_fields_ok=safety_ok,
                true_requirement_fields_ok=requirement_ok,
                planned_no_execution_ok=planned_no_execution_ok,
                validation_row_status=status,
                missing_required_fields=",".join(missing_required),
                invalid_safety_fields=",".join(invalid_safety),
                invalid_requirement_fields=",".join(invalid_requirement),
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


def write_candidate_replay_binding_plan_validation(
    optimization_id: str,
    output_dir: str | Path,
    *,
    plan_rows_path: str | Path | None,
) -> CandidateReplayBindingPlanValidatorBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    plan_rows = _rows_from_payload(_safe_load_json(plan_rows_path))
    validation_rows = build_candidate_replay_binding_plan_validation_rows(
        optimization_id,
        plan_rows_path=plan_rows_path,
    )
    validation_dicts = [asdict(row) for row in validation_rows]

    valid_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_VALID_NO_EXECUTION)
    invalid_count = len(validation_rows) - valid_count
    missing_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD)
    safety_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_INVALID_SAFETY_FLAG)
    state_count = sum(1 for row in validation_rows if row.validation_row_status == ROW_STATUS_INVALID_EXECUTION_STATE)

    plan_ids = [str(row.get("plan_id")) for row in plan_rows if row.get("plan_id")]
    candidate_ids = [str(row.get("candidate_id")) for row in plan_rows if row.get("candidate_id")]
    duplicate_plan_ids = _count_duplicates(plan_ids)
    duplicate_candidate_ids = _count_duplicates(candidate_ids)

    if not plan_rows:
        status = VALIDATION_STATUS_BLOCKED_NO_PLAN_ROWS
    elif duplicate_plan_ids:
        status = VALIDATION_STATUS_BLOCKED_DUPLICATE_PLAN_IDS
    elif duplicate_candidate_ids:
        status = VALIDATION_STATUS_BLOCKED_DUPLICATE_CANDIDATE_IDS
    elif missing_count:
        status = VALIDATION_STATUS_BLOCKED_MISSING_REQUIRED_PLAN_FIELDS
    elif safety_count:
        status = VALIDATION_STATUS_BLOCKED_SAFETY_FLAG_VIOLATION
    elif state_count:
        status = VALIDATION_STATUS_BLOCKED_UNEXPECTED_EXECUTION_STATE
    else:
        status = VALIDATION_STATUS_PASS_NO_EXECUTION

    report_path = out / "36_candidate_replay_binding_plan_validation_report.json"
    rows_json_path = out / "36_candidate_replay_binding_plan_validation_rows.json"
    rows_csv_path = out / "36_candidate_replay_binding_plan_validation_rows.csv"
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
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Binding Plan Validator",
        "contract_version": CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "plan_rows_path": str(plan_rows_path) if plan_rows_path else None,
        "plan_row_count": len(plan_rows),
        "validation_row_count": len(validation_rows),
        "valid_no_execution_count": valid_count,
        "invalid_row_count": invalid_count,
        "duplicate_plan_id_count": duplicate_plan_ids,
        "duplicate_candidate_id_count": duplicate_candidate_ids,
        "missing_required_field_row_count": missing_count,
        "safety_violation_row_count": safety_count,
        "unexpected_execution_state_row_count": state_count,
        "validation_status": status,
        "important_limitation": (
            "D33 validates the plan only. It does not execute candidate replays, "
            "create result packs, attach candidate context, match trades, or bind labels."
        ),
        "rows": validation_dicts,
        "safety": safety,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Binding Plan Validation Rows",
        "contract_version": CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_ACCEPTED_FOR,
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
        "contract_version": CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_ACCEPTED_FOR,
        "validation_status": status,
        "plan_row_count": len(plan_rows),
        "validation_row_count": len(validation_rows),
        "valid_no_execution_count": valid_count,
        "invalid_row_count": invalid_count,
        "duplicate_plan_id_count": duplicate_plan_ids,
        "duplicate_candidate_id_count": duplicate_candidate_ids,
        "missing_required_field_row_count": missing_count,
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
        "remarks": "D33 validates candidate replay binding plan rows only. No execution.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateReplayBindingPlanValidatorBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_CONTRACT_VERSION,
        accepted_for=CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_ACCEPTED_FOR,
        plan_rows_path=str(plan_rows_path) if plan_rows_path else None,
        validation_report_path=report_path.as_posix(),
        validation_rows_json_path=rows_json_path.as_posix(),
        validation_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        plan_row_count=len(plan_rows),
        validation_row_count=len(validation_rows),
        valid_no_execution_count=valid_count,
        invalid_row_count=invalid_count,
        duplicate_plan_id_count=duplicate_plan_ids,
        duplicate_candidate_id_count=duplicate_candidate_ids,
        missing_required_field_row_count=missing_count,
        safety_violation_row_count=safety_count,
        unexpected_execution_state_row_count=state_count,
        validation_status=status,
    )


__all__ = (
    "CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_CONTRACT_VERSION",
    "CANDIDATE_REPLAY_BINDING_PLAN_VALIDATOR_ACCEPTED_FOR",
    "VALIDATION_STATUS_PASS_NO_EXECUTION",
    "VALIDATION_STATUS_BLOCKED_NO_PLAN_ROWS",
    "VALIDATION_STATUS_BLOCKED_DUPLICATE_PLAN_IDS",
    "VALIDATION_STATUS_BLOCKED_DUPLICATE_CANDIDATE_IDS",
    "VALIDATION_STATUS_BLOCKED_MISSING_REQUIRED_PLAN_FIELDS",
    "VALIDATION_STATUS_BLOCKED_SAFETY_FLAG_VIOLATION",
    "VALIDATION_STATUS_BLOCKED_UNEXPECTED_EXECUTION_STATE",
    "ROW_STATUS_VALID_NO_EXECUTION",
    "ROW_STATUS_INVALID_MISSING_REQUIRED_FIELD",
    "ROW_STATUS_INVALID_SAFETY_FLAG",
    "ROW_STATUS_INVALID_EXECUTION_STATE",
    "REQUIRED_PLAN_FIELDS",
    "FALSE_SAFETY_FIELDS",
    "TRUE_REQUIREMENT_FIELDS",
    "VALIDATION_COLUMNS",
    "CandidateReplayBindingPlanValidationRow",
    "CandidateReplayBindingPlanValidatorBuildResult",
    "build_candidate_replay_binding_plan_validation_rows",
    "write_candidate_replay_binding_plan_validation",
)
