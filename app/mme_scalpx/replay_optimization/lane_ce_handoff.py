"""Lane D D37 Lane C/E handoff contract.

This module freezes the handoff contract from Lane D replay-optimization
preflight rows to a future Lane C or Lane E compatible replay/materialization
executor.

D37 is handoff-contract only. It does not execute replay, create result packs,
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

LANE_CE_HANDOFF_CONTRACT_VERSION = "replay_optimization_d37_lane_ce_handoff_contract_v1"
LANE_CE_HANDOFF_ACCEPTED_FOR = "LANE_CE_HANDOFF_CONTRACT_NO_EXECUTION"

HANDOFF_STATUS_READY_NO_EXECUTION = "LANE_CE_HANDOFF_READY_NO_EXECUTION"
HANDOFF_STATUS_BLOCKED_NO_D36_PREFLIGHT_ROWS = "BLOCKED_NO_D36_PREFLIGHT_ROWS"
HANDOFF_STATUS_BLOCKED_NON_READY_PREFLIGHT_ROWS = "BLOCKED_NON_READY_PREFLIGHT_ROWS"
HANDOFF_STATUS_BLOCKED_LANE_OWNERSHIP_AMBIGUOUS = "BLOCKED_LANE_OWNERSHIP_AMBIGUOUS"

HANDOFF_ROW_STATUS_READY_NO_EXECUTION = "HANDOFF_READY_NO_EXECUTION"
HANDOFF_ROW_STATUS_BLOCKED_PREFLIGHT_NOT_READY = "BLOCKED_PREFLIGHT_NOT_READY"

HANDOFF_OWNER_ALLOWED = (
    "Lane C replay runner / staging compatibility owner",
    "Lane E replay-data durable execution / artifact audit owner",
)

HANDOFF_COLUMNS = (
    "optimization_id",
    "handoff_id",
    "preflight_id",
    "materialization_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_result_pack_root",
    "handoff_source_lane",
    "handoff_target_owner_options",
    "recommended_owner",
    "handoff_reason",
    "required_preflight_status",
    "observed_preflight_status",
    "handoff_ready",
    "handoff_row_status",
    "lane_d_execution_allowed",
    "lane_c_or_e_execution_required",
    "replay_execution_allowed_in_lane_d",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "artifact_file_creation_allowed_in_lane_d",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class LaneCEHandoffRow:
    optimization_id: str
    handoff_id: str
    preflight_id: str | None
    materialization_id: str | None
    candidate_id: str | None
    candidate_fingerprint: str | None
    planned_result_pack_root: str | None
    handoff_source_lane: str
    handoff_target_owner_options: str
    recommended_owner: str
    handoff_reason: str
    required_preflight_status: str
    observed_preflight_status: str | None
    handoff_ready: bool
    handoff_row_status: str
    lane_d_execution_allowed: bool = False
    lane_c_or_e_execution_required: bool = True
    replay_execution_allowed_in_lane_d: bool = False
    replay_execution_performed: bool = False
    result_pack_creation_allowed_in_lane_d: bool = False
    result_pack_created: bool = False
    artifact_file_creation_allowed_in_lane_d: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class LaneCEHandoffBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    preflight_rows_path: str | None
    handoff_schema_path: str
    handoff_rows_json_path: str
    handoff_rows_csv_path: str
    optimizer_verdict_path: str
    preflight_row_count: int
    handoff_row_count: int
    handoff_ready_count: int
    blocked_row_count: int
    handoff_status: str
    lane_d_execution_allowed: bool = False
    lane_c_or_e_execution_required: bool = True
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
        raise ValueError(f"D37 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _recommended_owner(row: Mapping[str, Any]) -> str:
    # Lane C owns replay runner / staging compatibility; Lane E owns replay-data
    # durable execution and artifact audits. For this handoff, the plan is a
    # materialization/preflight contract, so route to Lane E unless future proof
    # shows runner seam changes are required.
    return "Lane E replay-data durable execution / artifact audit owner"


def build_lane_ce_handoff_rows(
    optimization_id: str,
    *,
    preflight_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[LaneCEHandoffRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    preflight_rows = _rows_from_payload(_safe_load_json(preflight_rows_path))
    out: list[LaneCEHandoffRow] = []

    for idx, row in enumerate(preflight_rows[:max_rows], start=1):
        observed_status = str(row.get("preflight_row_status")) if row.get("preflight_row_status") is not None else None
        ready = observed_status == "PREFLIGHT_READY_NO_EXECUTION"

        if ready:
            status = HANDOFF_ROW_STATUS_READY_NO_EXECUTION
            remarks = (
                "Handoff row is ready for future Lane C/E-compatible execution path. "
                "Lane D remains contract/preflight only and must not execute."
            )
        else:
            status = HANDOFF_ROW_STATUS_BLOCKED_PREFLIGHT_NOT_READY
            remarks = "D36 preflight row is not ready; do not hand off for materialization."

        out.append(
            LaneCEHandoffRow(
                optimization_id=optimization_id,
                handoff_id=f"HANDOFF_{idx:06d}",
                preflight_id=str(row.get("preflight_id")) if row.get("preflight_id") is not None else None,
                materialization_id=str(row.get("materialization_id")) if row.get("materialization_id") is not None else None,
                candidate_id=str(row.get("candidate_id")) if row.get("candidate_id") is not None else None,
                candidate_fingerprint=str(row.get("candidate_fingerprint")) if row.get("candidate_fingerprint") is not None else None,
                planned_result_pack_root=str(row.get("planned_result_pack_root")) if row.get("planned_result_pack_root") is not None else None,
                handoff_source_lane="Lane D replay_optimization contract/preflight",
                handoff_target_owner_options=" | ".join(HANDOFF_OWNER_ALLOWED),
                recommended_owner=_recommended_owner(row),
                handoff_reason=(
                    "Candidate replay/result-pack materialization is outside Lane D ownership; "
                    "future execution must be handled by Lane C/E-compatible replay/materialization flow."
                ),
                required_preflight_status="PREFLIGHT_READY_NO_EXECUTION",
                observed_preflight_status=observed_status,
                handoff_ready=ready,
                handoff_row_status=status,
                lane_d_execution_allowed=False,
                lane_c_or_e_execution_required=True,
                replay_execution_allowed_in_lane_d=False,
                replay_execution_performed=False,
                result_pack_creation_allowed_in_lane_d=False,
                result_pack_created=False,
                artifact_file_creation_allowed_in_lane_d=False,
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


def write_lane_ce_handoff_contract(
    optimization_id: str,
    output_dir: str | Path,
    *,
    preflight_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> LaneCEHandoffBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    preflight_rows = _rows_from_payload(_safe_load_json(preflight_rows_path))
    handoff_rows = build_lane_ce_handoff_rows(
        optimization_id,
        preflight_rows_path=preflight_rows_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in handoff_rows]

    ready_count = sum(1 for row in handoff_rows if row.handoff_ready)
    blocked_count = len(handoff_rows) - ready_count

    recommended_owners = {row.recommended_owner for row in handoff_rows}
    owner_ok = bool(recommended_owners) and recommended_owners.issubset(set(HANDOFF_OWNER_ALLOWED))

    if not preflight_rows:
        status = HANDOFF_STATUS_BLOCKED_NO_D36_PREFLIGHT_ROWS
    elif blocked_count:
        status = HANDOFF_STATUS_BLOCKED_NON_READY_PREFLIGHT_ROWS
    elif not owner_ok:
        status = HANDOFF_STATUS_BLOCKED_LANE_OWNERSHIP_AMBIGUOUS
    else:
        status = HANDOFF_STATUS_READY_NO_EXECUTION

    schema_path = out / "40_lane_ce_handoff_schema.json"
    rows_json_path = out / "40_lane_ce_handoff_rows.json"
    rows_csv_path = out / "40_lane_ce_handoff_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
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
        "schema_name": "MME-ScalpX Replay Optimization Lane C/E Handoff Contract",
        "contract_version": LANE_CE_HANDOFF_CONTRACT_VERSION,
        "accepted_for": LANE_CE_HANDOFF_ACCEPTED_FOR,
        "columns": list(HANDOFF_COLUMNS),
        "allowed_target_owners": list(HANDOFF_OWNER_ALLOWED),
        "handoff_policy": {
            "d37_is_handoff_contract_only": True,
            "lane_d_may_prepare_handoff_but_not_execute": True,
            "future_execution_owner_must_be_lane_c_or_lane_e_compatible": True,
            "recommended_default_owner": "Lane E replay-data durable execution / artifact audit owner",
            "lane_c_dependency_must_stop_lane_e_if_runner_behavior_changes": True,
            "replay_execution_allowed_in_d37": False,
            "result_pack_creation_allowed_in_d37": False,
            "artifact_file_creation_allowed_in_d37": False,
            "candidate_context_attachment_allowed_in_d37": False,
            "candidate_trade_matching_allowed_in_d37": False,
            "label_binding_allowed_in_d37": False,
            "future_lane_c_or_e_execution_package_required": True
        },
        "safety": safety,
    }
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Lane C/E Handoff Rows",
        "contract_version": LANE_CE_HANDOFF_CONTRACT_VERSION,
        "accepted_for": LANE_CE_HANDOFF_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "preflight_rows_path": str(preflight_rows_path) if preflight_rows_path else None,
        "handoff_status": status,
        "preflight_row_count": len(preflight_rows),
        "handoff_row_count": len(handoff_rows),
        "handoff_ready_count": ready_count,
        "blocked_row_count": blocked_count,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, HANDOFF_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": LANE_CE_HANDOFF_CONTRACT_VERSION,
        "accepted_for": LANE_CE_HANDOFF_ACCEPTED_FOR,
        "handoff_status": status,
        "preflight_row_count": len(preflight_rows),
        "handoff_row_count": len(handoff_rows),
        "handoff_ready_count": ready_count,
        "blocked_row_count": blocked_count,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
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
        "remarks": (
            "D37 freezes Lane C/E handoff only. Lane D must stop before execution/materialization. "
            "Future execution should be performed by the correct replay/materialization lane owner."
        ),
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return LaneCEHandoffBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=LANE_CE_HANDOFF_CONTRACT_VERSION,
        accepted_for=LANE_CE_HANDOFF_ACCEPTED_FOR,
        preflight_rows_path=str(preflight_rows_path) if preflight_rows_path else None,
        handoff_schema_path=schema_path.as_posix(),
        handoff_rows_json_path=rows_json_path.as_posix(),
        handoff_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        preflight_row_count=len(preflight_rows),
        handoff_row_count=len(handoff_rows),
        handoff_ready_count=ready_count,
        blocked_row_count=blocked_count,
        handoff_status=status,
    )


__all__ = (
    "LANE_CE_HANDOFF_CONTRACT_VERSION",
    "LANE_CE_HANDOFF_ACCEPTED_FOR",
    "HANDOFF_STATUS_READY_NO_EXECUTION",
    "HANDOFF_STATUS_BLOCKED_NO_D36_PREFLIGHT_ROWS",
    "HANDOFF_STATUS_BLOCKED_NON_READY_PREFLIGHT_ROWS",
    "HANDOFF_STATUS_BLOCKED_LANE_OWNERSHIP_AMBIGUOUS",
    "HANDOFF_ROW_STATUS_READY_NO_EXECUTION",
    "HANDOFF_ROW_STATUS_BLOCKED_PREFLIGHT_NOT_READY",
    "HANDOFF_OWNER_ALLOWED",
    "HANDOFF_COLUMNS",
    "LaneCEHandoffRow",
    "LaneCEHandoffBuildResult",
    "build_lane_ce_handoff_rows",
    "write_lane_ce_handoff_contract",
)
