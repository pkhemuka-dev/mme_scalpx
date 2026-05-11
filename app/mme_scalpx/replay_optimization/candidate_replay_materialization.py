"""Lane D D34 candidate replay materialization contract.

This module freezes the artifact contract for future candidate-specific replay
materialization.

D34 is contract-only. It does not execute replay, create real result packs,
attach candidate context, perform candidate-to-trade matching, bind labels,
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

CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_VERSION = "replay_optimization_d34_candidate_replay_materialization_contract_v1"
CANDIDATE_REPLAY_MATERIALIZATION_ACCEPTED_FOR = "CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_ONLY"

MATERIALIZATION_STATUS_CONTRACT_READY_NO_EXECUTION = "CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_READY_NO_EXECUTION"
MATERIALIZATION_STATUS_BLOCKED_NO_VALIDATION_ROWS = "BLOCKED_NO_D33_VALIDATION_ROWS"
MATERIALIZATION_STATUS_BLOCKED_INVALID_VALIDATION_ROWS = "BLOCKED_INVALID_D33_VALIDATION_ROWS"

MATERIALIZATION_ROW_STATUS_PLANNED_NO_EXECUTION = "MATERIALIZATION_PLANNED_NO_EXECUTION"
MATERIALIZATION_ROW_STATUS_BLOCKED_INVALID_PLAN = "BLOCKED_INVALID_PLAN_ROW"

MATERIALIZATION_REQUIRED_ARTIFACTS = (
    "candidate_profile.json",
    "candidate_replay_manifest.json",
    "candidate_effective_inputs.json",
    "candidate_result_pack_manifest.json",
    "candidate_integrity_report.json",
    "candidate_result_context_catalog.json",
    "candidate_label_binding_precondition.json",
)

MATERIALIZATION_COLUMNS = (
    "optimization_id",
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
class CandidateReplayMaterializationRow:
    optimization_id: str
    materialization_id: str
    plan_id: str | None
    candidate_id: str | None
    candidate_fingerprint: str | None
    planned_profile_id: str | None
    planned_result_pack_id: str | None
    planned_result_pack_root: str | None
    candidate_profile_path: str | None
    candidate_replay_manifest_path: str | None
    candidate_effective_inputs_path: str | None
    candidate_result_pack_manifest_path: str | None
    candidate_integrity_report_path: str | None
    candidate_result_context_catalog_path: str | None
    candidate_label_binding_precondition_path: str | None
    required_artifact_count: int
    materialization_row_status: str
    replay_execution_allowed: bool = False
    replay_execution_performed: bool = False
    result_pack_created: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateReplayMaterializationBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    validation_rows_path: str | None
    materialization_schema_path: str
    materialization_rows_json_path: str
    materialization_rows_csv_path: str
    optimizer_verdict_path: str
    validation_row_count: int
    materialization_row_count: int
    planned_no_execution_count: int
    blocked_row_count: int
    materialization_status: str
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
        raise ValueError(f"D34 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _path(root: str | None, filename: str) -> str | None:
    if not root:
        return None
    return f"{root.rstrip('/')}/{filename}"


def build_candidate_replay_materialization_rows(
    optimization_id: str,
    *,
    validation_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[CandidateReplayMaterializationRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    validation_rows = _rows_from_payload(_safe_load_json(validation_rows_path))
    out: list[CandidateReplayMaterializationRow] = []

    for idx, row in enumerate(validation_rows[:max_rows], start=1):
        valid = row.get("validation_row_status") == "VALID_NO_EXECUTION"
        root = str(row.get("planned_result_pack_root")) if row.get("planned_result_pack_root") else None

        if valid:
            status = MATERIALIZATION_ROW_STATUS_PLANNED_NO_EXECUTION
            remarks = (
                "Materialization contract row only. Future Lane C/E-compatible "
                "execution must create these artifacts; D34 creates none."
            )
        else:
            status = MATERIALIZATION_ROW_STATUS_BLOCKED_INVALID_PLAN
            remarks = "Validation row is not valid for materialization planning."

        out.append(
            CandidateReplayMaterializationRow(
                optimization_id=optimization_id,
                materialization_id=f"MAT_{idx:06d}",
                plan_id=str(row.get("plan_id")) if row.get("plan_id") is not None else None,
                candidate_id=str(row.get("candidate_id")) if row.get("candidate_id") is not None else None,
                candidate_fingerprint=str(row.get("candidate_fingerprint")) if row.get("candidate_fingerprint") is not None else None,
                planned_profile_id=str(row.get("planned_profile_id")) if row.get("planned_profile_id") is not None else None,
                planned_result_pack_id=str(row.get("planned_result_pack_id")) if row.get("planned_result_pack_id") is not None else None,
                planned_result_pack_root=root,
                candidate_profile_path=_path(root, "candidate_profile.json"),
                candidate_replay_manifest_path=_path(root, "candidate_replay_manifest.json"),
                candidate_effective_inputs_path=_path(root, "candidate_effective_inputs.json"),
                candidate_result_pack_manifest_path=_path(root, "candidate_result_pack_manifest.json"),
                candidate_integrity_report_path=_path(root, "candidate_integrity_report.json"),
                candidate_result_context_catalog_path=_path(root, "candidate_result_context_catalog.json"),
                candidate_label_binding_precondition_path=_path(root, "candidate_label_binding_precondition.json"),
                required_artifact_count=len(MATERIALIZATION_REQUIRED_ARTIFACTS),
                materialization_row_status=status,
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


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_candidate_replay_materialization_contract(
    optimization_id: str,
    output_dir: str | Path,
    *,
    validation_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> CandidateReplayMaterializationBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    validation_rows = _rows_from_payload(_safe_load_json(validation_rows_path))
    materialization_rows = build_candidate_replay_materialization_rows(
        optimization_id,
        validation_rows_path=validation_rows_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in materialization_rows]

    planned_count = sum(
        1 for row in materialization_rows
        if row.materialization_row_status == MATERIALIZATION_ROW_STATUS_PLANNED_NO_EXECUTION
    )
    blocked_count = len(materialization_rows) - planned_count

    if not validation_rows:
        status = MATERIALIZATION_STATUS_BLOCKED_NO_VALIDATION_ROWS
    elif blocked_count:
        status = MATERIALIZATION_STATUS_BLOCKED_INVALID_VALIDATION_ROWS
    else:
        status = MATERIALIZATION_STATUS_CONTRACT_READY_NO_EXECUTION

    schema_path = out / "37_candidate_replay_materialization_schema.json"
    rows_json_path = out / "37_candidate_replay_materialization_rows.json"
    rows_csv_path = out / "37_candidate_replay_materialization_rows.csv"
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

    schema = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Materialization Contract",
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_ACCEPTED_FOR,
        "columns": list(MATERIALIZATION_COLUMNS),
        "required_artifacts": list(MATERIALIZATION_REQUIRED_ARTIFACTS),
        "materialization_policy": {
            "d34_is_contract_only": True,
            "candidate_specific_artifact_plan_only": True,
            "replay_execution_allowed_in_d34": False,
            "result_pack_creation_allowed_in_d34": False,
            "candidate_context_attachment_allowed_in_d34": False,
            "label_binding_allowed_in_d34": False,
            "future_execution_owner_must_be_lane_c_or_lane_e_compatible": True,
            "future_materialization_validator_required": True
        },
        "safety": safety,
    }
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Materialization Rows",
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "validation_rows_path": str(validation_rows_path) if validation_rows_path else None,
        "validation_row_count": len(validation_rows),
        "materialization_status": status,
        "materialization_row_count": len(materialization_rows),
        "planned_no_execution_count": planned_count,
        "blocked_row_count": blocked_count,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, MATERIALIZATION_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_MATERIALIZATION_ACCEPTED_FOR,
        "materialization_status": status,
        "validation_row_count": len(validation_rows),
        "materialization_row_count": len(materialization_rows),
        "planned_no_execution_count": planned_count,
        "blocked_row_count": blocked_count,
        "required_artifact_count": len(MATERIALIZATION_REQUIRED_ARTIFACTS),
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
        "remarks": "D34 freezes materialization artifact contract only. No replay/result pack execution.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateReplayMaterializationBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_VERSION,
        accepted_for=CANDIDATE_REPLAY_MATERIALIZATION_ACCEPTED_FOR,
        validation_rows_path=str(validation_rows_path) if validation_rows_path else None,
        materialization_schema_path=schema_path.as_posix(),
        materialization_rows_json_path=rows_json_path.as_posix(),
        materialization_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        validation_row_count=len(validation_rows),
        materialization_row_count=len(materialization_rows),
        planned_no_execution_count=planned_count,
        blocked_row_count=blocked_count,
        materialization_status=status,
    )


__all__ = (
    "CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_VERSION",
    "CANDIDATE_REPLAY_MATERIALIZATION_ACCEPTED_FOR",
    "MATERIALIZATION_STATUS_CONTRACT_READY_NO_EXECUTION",
    "MATERIALIZATION_STATUS_BLOCKED_NO_VALIDATION_ROWS",
    "MATERIALIZATION_STATUS_BLOCKED_INVALID_VALIDATION_ROWS",
    "MATERIALIZATION_ROW_STATUS_PLANNED_NO_EXECUTION",
    "MATERIALIZATION_ROW_STATUS_BLOCKED_INVALID_PLAN",
    "MATERIALIZATION_REQUIRED_ARTIFACTS",
    "MATERIALIZATION_COLUMNS",
    "CandidateReplayMaterializationRow",
    "CandidateReplayMaterializationBuildResult",
    "build_candidate_replay_materialization_rows",
    "write_candidate_replay_materialization_contract",
)
