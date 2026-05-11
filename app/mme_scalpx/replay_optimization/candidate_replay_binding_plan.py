"""Lane D D32 candidate replay binding plan schema contract.

This module freezes a plan schema for binding optimization parameter candidates
to future candidate-specific replay executions and result packs.

D32 is schema/plan-only. It does not execute replay, create result packs,
attach candidate context, perform candidate-to-trade matching, bind labels,
calculate PnL, train/predict models, call brokers, write live Redis, mutate
doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CANDIDATE_REPLAY_BINDING_PLAN_CONTRACT_VERSION = "replay_optimization_d32_candidate_replay_binding_plan_contract_v1"
CANDIDATE_REPLAY_BINDING_PLAN_ACCEPTED_FOR = "CANDIDATE_REPLAY_BINDING_PLAN_SCHEMA_CONTRACT_ONLY"

PLAN_STATUS_SCHEMA_READY_NO_EXECUTION = "CANDIDATE_REPLAY_BINDING_PLAN_SCHEMA_READY_NO_EXECUTION"
PLAN_STATUS_BLOCKED_NO_CANDIDATE_MATRIX = "BLOCKED_NO_CANDIDATE_MATRIX"
PLAN_STATUS_BLOCKED_NO_D31_REQUIREMENT = "BLOCKED_NO_D31_REQUIREMENT_AUDIT"
PLAN_STATUS_BLOCKED_REQUIREMENT_NOT_BINDING_REQUIRED = "BLOCKED_D31_REQUIREMENT_NOT_BINDING_REQUIRED"

PLAN_ROW_STATUS_PLANNED_NO_EXECUTION = "PLANNED_NO_EXECUTION"
PLAN_ROW_STATUS_BLOCKED_MISSING_CANDIDATE_ID = "BLOCKED_MISSING_CANDIDATE_ID"

PLAN_COLUMNS = (
    "optimization_id",
    "plan_id",
    "candidate_id",
    "candidate_fingerprint",
    "candidate_profile_ref",
    "candidate_profile_sha256",
    "planned_replay_scope",
    "planned_replay_mode",
    "planned_dataset_id",
    "planned_dataset_date",
    "planned_profile_id",
    "planned_result_pack_id",
    "planned_result_pack_root",
    "planned_integrity_required",
    "planned_context_catalog_required",
    "candidate_context_bridge_required",
    "label_binding_allowed",
    "labels_bound",
    "plan_row_status",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateReplayBindingPlanRow:
    optimization_id: str
    plan_id: str
    candidate_id: str | None
    candidate_fingerprint: str | None
    candidate_profile_ref: str | None
    candidate_profile_sha256: str | None
    planned_replay_scope: str
    planned_replay_mode: str
    planned_dataset_id: str | None
    planned_dataset_date: str | None
    planned_profile_id: str | None
    planned_result_pack_id: str | None
    planned_result_pack_root: str | None
    planned_integrity_required: bool
    planned_context_catalog_required: bool
    candidate_context_bridge_required: bool
    label_binding_allowed: bool = False
    labels_bound: bool = False
    plan_row_status: str = PLAN_ROW_STATUS_PLANNED_NO_EXECUTION
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateReplayBindingPlanBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    candidate_matrix_path: str | None
    requirement_report_path: str | None
    plan_schema_path: str
    plan_rows_json_path: str
    plan_rows_csv_path: str
    optimizer_verdict_path: str
    candidate_count: int
    plan_row_count: int
    planned_no_execution_count: int
    blocked_row_count: int
    plan_status: str
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
        raise ValueError(f"D32 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _stable_fingerprint(row: Mapping[str, Any]) -> str:
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _requirement_status(requirement_report: Any) -> str | None:
    if isinstance(requirement_report, dict):
        value = requirement_report.get("requirement_status")
        return str(value) if value is not None else None
    return None


def build_candidate_replay_binding_plan_rows(
    optimization_id: str,
    *,
    candidate_matrix_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[CandidateReplayBindingPlanRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    candidate_rows = _rows_from_payload(_safe_load_json(candidate_matrix_path))

    out: list[CandidateReplayBindingPlanRow] = []
    for i, row in enumerate(candidate_rows[:max_rows], start=1):
        candidate_id = _as_str(row.get("candidate_id"))
        fingerprint = _as_str(row.get("candidate_fingerprint")) or _stable_fingerprint(row)
        strategy_family = _as_str(row.get("strategy_family")) or "UNKNOWN"
        side = _as_str(row.get("side")) or "UNKNOWN"

        if not candidate_id:
            status = PLAN_ROW_STATUS_BLOCKED_MISSING_CANDIDATE_ID
            remarks = "Candidate ID missing; cannot plan candidate-specific replay binding."
        else:
            status = PLAN_ROW_STATUS_PLANNED_NO_EXECUTION
            remarks = (
                "Candidate replay binding plan row only. Future lane/batch must "
                "materialize a candidate-specific replay profile and result pack before labels."
            )

        planned_result_pack_id = f"PLANNED_RPACK_{i:06d}" if candidate_id else None
        planned_result_pack_root = (
            f"run/replay_optimization/candidate_replays/{candidate_id}"
            if candidate_id else None
        )

        out.append(
            CandidateReplayBindingPlanRow(
                optimization_id=optimization_id,
                plan_id=f"BINDPLAN_{i:06d}",
                candidate_id=candidate_id,
                candidate_fingerprint=fingerprint,
                candidate_profile_ref=_as_str(row.get("candidate_profile_ref")),
                candidate_profile_sha256=_as_str(row.get("candidate_profile_sha256")),
                planned_replay_scope="candidate_specific_parameter_replay",
                planned_replay_mode="execution_shadow_offline_only",
                planned_dataset_id=_as_str(row.get("dataset_id")),
                planned_dataset_date=_as_str(row.get("selected_date")),
                planned_profile_id=f"{strategy_family}_{side}_{candidate_id}" if candidate_id else None,
                planned_result_pack_id=planned_result_pack_id,
                planned_result_pack_root=planned_result_pack_root,
                planned_integrity_required=True,
                planned_context_catalog_required=True,
                candidate_context_bridge_required=True,
                label_binding_allowed=False,
                labels_bound=False,
                plan_row_status=status,
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


def write_candidate_replay_binding_plan_schema(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_matrix_path: str | Path | None,
    requirement_report_path: str | Path | None,
    max_rows: int = 10000,
) -> CandidateReplayBindingPlanBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    candidate_rows = _rows_from_payload(_safe_load_json(candidate_matrix_path))
    requirement_report = _safe_load_json(requirement_report_path)
    requirement_status = _requirement_status(requirement_report)

    plan_rows = build_candidate_replay_binding_plan_rows(
        optimization_id,
        candidate_matrix_path=candidate_matrix_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in plan_rows]

    planned_count = sum(1 for row in plan_rows if row.plan_row_status == PLAN_ROW_STATUS_PLANNED_NO_EXECUTION)
    blocked_count = sum(1 for row in plan_rows if row.plan_row_status != PLAN_ROW_STATUS_PLANNED_NO_EXECUTION)

    if not candidate_rows:
        status = PLAN_STATUS_BLOCKED_NO_CANDIDATE_MATRIX
    elif not isinstance(requirement_report, dict):
        status = PLAN_STATUS_BLOCKED_NO_D31_REQUIREMENT
    elif requirement_status != "CANDIDATE_REPLAY_BINDING_REQUIRED_BEFORE_LABELS":
        status = PLAN_STATUS_BLOCKED_REQUIREMENT_NOT_BINDING_REQUIRED
    else:
        status = PLAN_STATUS_SCHEMA_READY_NO_EXECUTION

    schema_path = out / "35_candidate_replay_binding_plan_schema.json"
    rows_json_path = out / "35_candidate_replay_binding_plan_rows.json"
    rows_csv_path = out / "35_candidate_replay_binding_plan_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
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

    schema = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Binding Plan Schema",
        "contract_version": CANDIDATE_REPLAY_BINDING_PLAN_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_PLAN_ACCEPTED_FOR,
        "columns": list(PLAN_COLUMNS),
        "plan_policy": {
            "d32_is_schema_only": True,
            "candidate_specific_replay_required": True,
            "execution_shadow_offline_only": True,
            "result_integrity_required_before_labels": True,
            "candidate_context_bridge_required_before_labels": True,
            "label_binding_allowed_in_d32": False,
            "replay_execution_allowed_in_d32": False,
            "future_candidate_replay_plan_validator_required": True
        },
        "safety": safety,
    }
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Binding Plan Rows",
        "contract_version": CANDIDATE_REPLAY_BINDING_PLAN_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_PLAN_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
        "requirement_report_path": str(requirement_report_path) if requirement_report_path else None,
        "plan_status": status,
        "candidate_count": len(candidate_rows),
        "plan_row_count": len(plan_rows),
        "planned_no_execution_count": planned_count,
        "blocked_row_count": blocked_count,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, PLAN_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_REPLAY_BINDING_PLAN_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_PLAN_ACCEPTED_FOR,
        "plan_status": status,
        "candidate_count": len(candidate_rows),
        "plan_row_count": len(plan_rows),
        "planned_no_execution_count": planned_count,
        "blocked_row_count": blocked_count,
        "replay_execution_performed": False,
        "result_pack_created": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D32 creates a candidate replay binding plan only. It does not execute candidate replays.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateReplayBindingPlanBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_REPLAY_BINDING_PLAN_CONTRACT_VERSION,
        accepted_for=CANDIDATE_REPLAY_BINDING_PLAN_ACCEPTED_FOR,
        candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
        requirement_report_path=str(requirement_report_path) if requirement_report_path else None,
        plan_schema_path=schema_path.as_posix(),
        plan_rows_json_path=rows_json_path.as_posix(),
        plan_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        candidate_count=len(candidate_rows),
        plan_row_count=len(plan_rows),
        planned_no_execution_count=planned_count,
        blocked_row_count=blocked_count,
        plan_status=status,
    )


__all__ = (
    "CANDIDATE_REPLAY_BINDING_PLAN_CONTRACT_VERSION",
    "CANDIDATE_REPLAY_BINDING_PLAN_ACCEPTED_FOR",
    "PLAN_STATUS_SCHEMA_READY_NO_EXECUTION",
    "PLAN_STATUS_BLOCKED_NO_CANDIDATE_MATRIX",
    "PLAN_STATUS_BLOCKED_NO_D31_REQUIREMENT",
    "PLAN_STATUS_BLOCKED_REQUIREMENT_NOT_BINDING_REQUIRED",
    "PLAN_ROW_STATUS_PLANNED_NO_EXECUTION",
    "PLAN_ROW_STATUS_BLOCKED_MISSING_CANDIDATE_ID",
    "PLAN_COLUMNS",
    "CandidateReplayBindingPlanRow",
    "CandidateReplayBindingPlanBuildResult",
    "build_candidate_replay_binding_plan_rows",
    "write_candidate_replay_binding_plan_schema",
)
