"""Lane D D36 candidate replay materialization preflight contract.

This module freezes preflight checks that must pass before any future
Lane C/E-compatible candidate replay/result-pack materialization.

D36 is preflight-contract only. It does not execute replay, create result packs,
write candidate artifacts, attach candidate context, perform matching, bind
labels, calculate PnL, train/predict models, call brokers, write live Redis,
mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_VERSION = "replay_optimization_d36_candidate_replay_materialization_preflight_contract_v1"
CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_ACCEPTED_FOR = "CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_NO_EXECUTION"

PREFLIGHT_STATUS_PASS_NO_EXECUTION = "CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_PASS_NO_EXECUTION"
PREFLIGHT_STATUS_BLOCKED_NO_D35_VALIDATION_ROWS = "BLOCKED_NO_D35_VALIDATION_ROWS"
PREFLIGHT_STATUS_BLOCKED_INVALID_D35_VALIDATION_ROWS = "BLOCKED_INVALID_D35_VALIDATION_ROWS"
PREFLIGHT_STATUS_BLOCKED_MISSING_PREFLIGHT_REQUIREMENT = "BLOCKED_MISSING_PREFLIGHT_REQUIREMENT"
PREFLIGHT_STATUS_BLOCKED_LANE_OWNERSHIP_RISK = "BLOCKED_LANE_OWNERSHIP_RISK"

ROW_STATUS_PREFLIGHT_READY_NO_EXECUTION = "PREFLIGHT_READY_NO_EXECUTION"
ROW_STATUS_BLOCKED_INVALID_VALIDATION = "BLOCKED_INVALID_VALIDATION"
ROW_STATUS_BLOCKED_MISSING_REQUIREMENT = "BLOCKED_MISSING_REQUIREMENT"

PREFLIGHT_REQUIREMENTS = (
    "d35_validation_passed",
    "candidate_id_present",
    "candidate_fingerprint_present",
    "materialization_id_present",
    "planned_result_pack_root_present",
    "candidate_root_policy_validated",
    "artifact_plan_validated",
    "execution_owner_declared_lane_c_or_lane_e_compatible",
    "replay_execution_not_allowed_in_lane_d",
    "result_pack_creation_not_allowed_in_lane_d",
    "label_binding_not_allowed_in_lane_d",
)

PREFLIGHT_COLUMNS = (
    "optimization_id",
    "preflight_id",
    "materialization_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_result_pack_root",
    "execution_owner_required",
    "execution_owner_current_lane",
    "d35_validation_status",
    "preflight_requirements",
    "preflight_requirement_count",
    "missing_preflight_requirements",
    "missing_preflight_requirement_count",
    "preflight_row_status",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed",
    "result_pack_created",
    "artifact_file_creation_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateReplayMaterializationPreflightRow:
    optimization_id: str
    preflight_id: str
    materialization_id: str | None
    candidate_id: str | None
    candidate_fingerprint: str | None
    planned_result_pack_root: str | None
    execution_owner_required: str
    execution_owner_current_lane: str
    d35_validation_status: str | None
    preflight_requirements: str
    preflight_requirement_count: int
    missing_preflight_requirements: str
    missing_preflight_requirement_count: int
    preflight_row_status: str
    replay_execution_allowed: bool = False
    replay_execution_performed: bool = False
    result_pack_creation_allowed: bool = False
    result_pack_created: bool = False
    artifact_file_creation_allowed: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateReplayMaterializationPreflightBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    validation_rows_path: str | None
    preflight_schema_path: str
    preflight_rows_json_path: str
    preflight_rows_csv_path: str
    optimizer_verdict_path: str
    validation_row_count: int
    preflight_row_count: int
    preflight_ready_count: int
    blocked_row_count: int
    missing_preflight_requirement_row_count: int
    preflight_status: str
    replay_execution_allowed: bool = False
    replay_execution_performed: bool = False
    result_pack_creation_allowed: bool = False
    result_pack_created: bool = False
    artifact_file_creation_allowed: bool = False
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
        raise ValueError(f"D36 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _candidate_root_policy_ok(row: Mapping[str, Any]) -> bool:
    root = str(row.get("planned_result_pack_root") or "").strip()
    candidate_id = str(row.get("candidate_id") or "").strip()
    return (
        bool(root)
        and bool(candidate_id)
        and root.startswith("run/replay_optimization/candidate_replays/")
        and candidate_id in root
    )


def _artifact_plan_validated(row: Mapping[str, Any]) -> bool:
    return (
        row.get("artifact_path_count_ok") is True
        and row.get("artifact_paths_under_candidate_root") is True
        and row.get("artifact_suffixes_ok") is True
        and row.get("required_fields_present") is True
        and row.get("planned_no_execution_ok") is True
    )


def _missing_requirements(row: Mapping[str, Any]) -> tuple[str, ...]:
    missing: list[str] = []

    if row.get("validation_row_status") != "VALID_MATERIALIZATION_PLAN_NO_EXECUTION":
        missing.append("d35_validation_passed")
    if not _present(row.get("candidate_id")):
        missing.append("candidate_id_present")
    if not _present(row.get("candidate_fingerprint")):
        missing.append("candidate_fingerprint_present")
    if not _present(row.get("materialization_id")):
        missing.append("materialization_id_present")
    if not _present(row.get("planned_result_pack_root")):
        missing.append("planned_result_pack_root_present")
    if not _candidate_root_policy_ok(row):
        missing.append("candidate_root_policy_validated")
    if not _artifact_plan_validated(row):
        missing.append("artifact_plan_validated")

    return tuple(missing)


def build_candidate_replay_materialization_preflight_rows(
    optimization_id: str,
    *,
    validation_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[CandidateReplayMaterializationPreflightRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    validation_rows = _rows_from_payload(_safe_load_json(validation_rows_path))
    out: list[CandidateReplayMaterializationPreflightRow] = []

    for idx, row in enumerate(validation_rows[:max_rows], start=1):
        missing = _missing_requirements(row)
        d35_status = str(row.get("validation_row_status")) if row.get("validation_row_status") is not None else None

        if missing:
            status = ROW_STATUS_BLOCKED_MISSING_REQUIREMENT
            remarks = "Preflight row is blocked because one or more materialization requirements are missing."
        elif d35_status != "VALID_MATERIALIZATION_PLAN_NO_EXECUTION":
            status = ROW_STATUS_BLOCKED_INVALID_VALIDATION
            remarks = "D35 validation row is not valid."
        else:
            status = ROW_STATUS_PREFLIGHT_READY_NO_EXECUTION
            remarks = (
                "Preflight-ready for future Lane C/E-compatible materialization. "
                "Lane D still does not execute replay or create artifacts."
            )

        out.append(
            CandidateReplayMaterializationPreflightRow(
                optimization_id=optimization_id,
                preflight_id=f"PREFLIGHT_{idx:06d}",
                materialization_id=str(row.get("materialization_id")) if row.get("materialization_id") is not None else None,
                candidate_id=str(row.get("candidate_id")) if row.get("candidate_id") is not None else None,
                candidate_fingerprint=str(row.get("candidate_fingerprint")) if row.get("candidate_fingerprint") is not None else None,
                planned_result_pack_root=str(row.get("planned_result_pack_root")) if row.get("planned_result_pack_root") is not None else None,
                execution_owner_required="Lane C or Lane E compatible replay/materialization executor",
                execution_owner_current_lane="Lane D contract/preflight only",
                d35_validation_status=d35_status,
                preflight_requirements=",".join(PREFLIGHT_REQUIREMENTS),
                preflight_requirement_count=len(PREFLIGHT_REQUIREMENTS),
                missing_preflight_requirements=",".join(missing),
                missing_preflight_requirement_count=len(missing),
                preflight_row_status=status,
                replay_execution_allowed=False,
                replay_execution_performed=False,
                result_pack_creation_allowed=False,
                result_pack_created=False,
                artifact_file_creation_allowed=False,
                candidate_context_attached=False,
                candidate_trade_matching_allowed=False,
                label_binding_allowed=False,
                labels_bound=False,
                remarks=remarks,
            )
        )

    return tuple(out)


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_candidate_replay_materialization_preflight_contract(
    optimization_id: str,
    output_dir: str | Path,
    *,
    validation_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> CandidateReplayMaterializationPreflightBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    validation_rows = _rows_from_payload(_safe_load_json(validation_rows_path))
    preflight_rows = build_candidate_replay_materialization_preflight_rows(
        optimization_id,
        validation_rows_path=validation_rows_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in preflight_rows]

    ready_count = sum(1 for row in preflight_rows if row.preflight_row_status == ROW_STATUS_PREFLIGHT_READY_NO_EXECUTION)
    blocked_count = len(preflight_rows) - ready_count
    missing_count = sum(1 for row in preflight_rows if row.missing_preflight_requirement_count > 0)
    invalid_validation_count = sum(
        1 for row in preflight_rows
        if row.d35_validation_status != "VALID_MATERIALIZATION_PLAN_NO_EXECUTION"
    )

    if not validation_rows:
        status = PREFLIGHT_STATUS_BLOCKED_NO_D35_VALIDATION_ROWS
    elif invalid_validation_count:
        status = PREFLIGHT_STATUS_BLOCKED_INVALID_D35_VALIDATION_ROWS
    elif missing_count:
        status = PREFLIGHT_STATUS_BLOCKED_MISSING_PREFLIGHT_REQUIREMENT
    elif ready_count != len(preflight_rows):
        status = PREFLIGHT_STATUS_BLOCKED_LANE_OWNERSHIP_RISK
    else:
        status = PREFLIGHT_STATUS_PASS_NO_EXECUTION

    schema_path = out / "39_candidate_replay_materialization_preflight_schema.json"
    rows_json_path = out / "39_candidate_replay_materialization_preflight_rows.json"
    rows_csv_path = out / "39_candidate_replay_materialization_preflight_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed": False,
        "result_pack_created": False,
        "artifact_file_creation_allowed": False,
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

    schema = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Materialization Preflight Contract",
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_ACCEPTED_FOR,
        "columns": list(PREFLIGHT_COLUMNS),
        "preflight_requirements": list(PREFLIGHT_REQUIREMENTS),
        "preflight_policy": {
            "d36_is_preflight_contract_only": True,
            "lane_d_may_validate_but_not_execute": True,
            "future_execution_owner_must_be_lane_c_or_lane_e_compatible": True,
            "replay_execution_allowed_in_d36": False,
            "result_pack_creation_allowed_in_d36": False,
            "artifact_file_creation_allowed_in_d36": False,
            "candidate_context_attachment_allowed_in_d36": False,
            "label_binding_allowed_in_d36": False,
            "future_lane_c_or_e_execution_handoff_required": True
        },
        "safety": safety,
    }
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Materialization Preflight Rows",
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "validation_rows_path": str(validation_rows_path) if validation_rows_path else None,
        "preflight_status": status,
        "validation_row_count": len(validation_rows),
        "preflight_row_count": len(preflight_rows),
        "preflight_ready_count": ready_count,
        "blocked_row_count": blocked_count,
        "missing_preflight_requirement_row_count": missing_count,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, PREFLIGHT_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_ACCEPTED_FOR,
        "preflight_status": status,
        "validation_row_count": len(validation_rows),
        "preflight_row_count": len(preflight_rows),
        "preflight_ready_count": ready_count,
        "blocked_row_count": blocked_count,
        "missing_preflight_requirement_row_count": missing_count,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed": False,
        "result_pack_created": False,
        "artifact_file_creation_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D36 creates preflight contract rows only. Future materialization must be handed to Lane C/E-compatible execution flow.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateReplayMaterializationPreflightBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_VERSION,
        accepted_for=CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_ACCEPTED_FOR,
        validation_rows_path=str(validation_rows_path) if validation_rows_path else None,
        preflight_schema_path=schema_path.as_posix(),
        preflight_rows_json_path=rows_json_path.as_posix(),
        preflight_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        validation_row_count=len(validation_rows),
        preflight_row_count=len(preflight_rows),
        preflight_ready_count=ready_count,
        blocked_row_count=blocked_count,
        missing_preflight_requirement_row_count=missing_count,
        preflight_status=status,
    )


__all__ = (
    "CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_VERSION",
    "CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_ACCEPTED_FOR",
    "PREFLIGHT_STATUS_PASS_NO_EXECUTION",
    "PREFLIGHT_STATUS_BLOCKED_NO_D35_VALIDATION_ROWS",
    "PREFLIGHT_STATUS_BLOCKED_INVALID_D35_VALIDATION_ROWS",
    "PREFLIGHT_STATUS_BLOCKED_MISSING_PREFLIGHT_REQUIREMENT",
    "PREFLIGHT_STATUS_BLOCKED_LANE_OWNERSHIP_RISK",
    "ROW_STATUS_PREFLIGHT_READY_NO_EXECUTION",
    "ROW_STATUS_BLOCKED_INVALID_VALIDATION",
    "ROW_STATUS_BLOCKED_MISSING_REQUIREMENT",
    "PREFLIGHT_REQUIREMENTS",
    "PREFLIGHT_COLUMNS",
    "CandidateReplayMaterializationPreflightRow",
    "CandidateReplayMaterializationPreflightBuildResult",
    "build_candidate_replay_materialization_preflight_rows",
    "write_candidate_replay_materialization_preflight_contract",
)
