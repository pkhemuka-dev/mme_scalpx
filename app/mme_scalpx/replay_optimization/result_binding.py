"""Lane D D8 result-binding schema contract.

This module defines how future verified replay outputs may bind labels
(label_pnl, label_profitable, label_exit_reason) to ML dataset rows.

D8 intentionally creates only UNBOUND rows. It does not execute replay, does not
calculate real PnL, does not bind labels, does not train models, and does not
approve paper/live or production profit claims.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import (
    OUTPUT_ROOT,
    VERDICT_NOT_READY_REPLAY_SOURCE_MISSING,
    VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
    OptimizerVerdictRow,
    row_to_dict,
)

RESULT_BINDING_CONTRACT_VERSION = "replay_optimization_d8_result_binding_contract_v1"
RESULT_BINDING_ACCEPTED_FOR = "RESULT_BINDING_SCHEMA_CONTRACT_ONLY"

RESULT_BINDING_STATUS_UNBOUND = "UNBOUND_PENDING_VERIFIED_REPLAY_RESULT"
RESULT_BINDING_STATUS_BLOCKED = "BLOCKED_UNVERIFIED_SOURCE"
RESULT_BINDING_STATUS_READY_FOR_FUTURE_BINDING = "READY_FOR_FUTURE_BINDING_CONTRACT_ONLY"

RESULT_BINDING_COLUMNS = (
    "optimization_id",
    "binding_id",
    "candidate_id",
    "ml_row_id",
    "feature_vector_ref",
    "candidate_matrix_path",
    "ml_dataset_path",
    "replay_index_path",
    "replay_result_candidate",
    "label_pnl",
    "label_profitable",
    "label_exit_reason",
    "label_binding_status",
    "source_verified",
    "integrity_verdict",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class ResultBindingRow:
    optimization_id: str
    binding_id: str
    candidate_id: str
    ml_row_id: str
    feature_vector_ref: str
    candidate_matrix_path: str | None
    ml_dataset_path: str | None
    replay_index_path: str | None
    replay_result_candidate: str | None = None
    label_pnl: float | None = None
    label_profitable: bool | None = None
    label_exit_reason: str | None = None
    label_binding_status: str = RESULT_BINDING_STATUS_UNBOUND
    source_verified: bool = False
    integrity_verdict: str | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ResultBindingBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    candidate_matrix_path: str | None
    ml_dataset_path: str | None
    replay_index_path: str | None
    result_binding_schema_path: str
    result_binding_rows_json_path: str
    result_binding_rows_csv_path: str
    optimizer_verdict_path: str
    binding_row_count: int
    readiness_verdict: str
    labels_bound: bool = False
    replay_execution_performed: bool = False
    model_training_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_json(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


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
        raise ValueError(f"D8 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _rows_from_payload(payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _readiness_from_sources(
    ml_dataset_payload: Mapping[str, Any] | None,
    replay_index_payload: Mapping[str, Any] | None,
) -> str:
    ml_rows = _rows_from_payload(ml_dataset_payload)
    if not ml_rows:
        return VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    if not replay_index_payload:
        return VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    return VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE


def build_result_binding_rows(
    optimization_id: str,
    *,
    candidate_matrix_path: str | Path | None,
    ml_dataset_path: str | Path | None,
    replay_index_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[ResultBindingRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    ml_payload = _safe_load_json(ml_dataset_path)
    ml_rows = _rows_from_payload(ml_payload)

    out: list[ResultBindingRow] = []
    for i, row in enumerate(ml_rows[:max_rows], start=1):
        out.append(
            ResultBindingRow(
                optimization_id=optimization_id,
                binding_id=f"BIND_{i:06d}",
                candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                ml_row_id=str(row.get("row_id") or f"MLROW_UNKNOWN_{i:06d}"),
                feature_vector_ref=str(row.get("feature_vector_ref") or ""),
                candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
                ml_dataset_path=str(ml_dataset_path) if ml_dataset_path else None,
                replay_index_path=str(replay_index_path) if replay_index_path else None,
                replay_result_candidate=None,
                label_pnl=None,
                label_profitable=None,
                label_exit_reason=None,
                label_binding_status=RESULT_BINDING_STATUS_UNBOUND,
                source_verified=False,
                integrity_verdict=None,
                remarks=(
                    "D8 schema-only result binding row. Labels intentionally remain null "
                    "until verified replay result binding is implemented."
                ),
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


def write_result_binding_schema(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_matrix_path: str | Path | None,
    ml_dataset_path: str | Path | None,
    replay_index_path: str | Path | None,
    max_rows: int = 10000,
) -> ResultBindingBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ml_payload = _safe_load_json(ml_dataset_path)
    replay_payload = _safe_load_json(replay_index_path)
    readiness = _readiness_from_sources(ml_payload, replay_payload)

    rows = build_result_binding_rows(
        optimization_id,
        candidate_matrix_path=candidate_matrix_path,
        ml_dataset_path=ml_dataset_path,
        replay_index_path=replay_index_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in rows]

    schema_path = out / "10_result_binding_schema.json"
    rows_json_path = out / "10_result_binding_rows.json"
    rows_csv_path = out / "10_result_binding_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    schema_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Result Binding Schema",
        "contract_version": RESULT_BINDING_CONTRACT_VERSION,
        "accepted_for": RESULT_BINDING_ACCEPTED_FOR,
        "columns": list(RESULT_BINDING_COLUMNS),
        "label_policy": {
            "labels_bound_in_d8": False,
            "label_pnl_source": "FUTURE_VERIFIED_REPLAY_RESULT_BINDING_ONLY",
            "label_profitable_source": "FUTURE_VERIFIED_REPLAY_RESULT_BINDING_ONLY",
            "label_exit_reason_source": "FUTURE_VERIFIED_REPLAY_RESULT_BINDING_ONLY",
            "unverified_label_binding_allowed": False,
            "manual_profit_claim_allowed": False
        },
        "source_requirements_for_future_binding": {
            "verified_replay_index_required": True,
            "integrity_verdict_pass_required": True,
            "candidate_to_replay_result_mapping_required": True,
            "sample_size_report_required_before_training": True,
            "overfit_risk_report_required_before_training": True
        },
        "safety": {
            "replay_execution_performed": False,
            "labels_bound": False,
            "model_training_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False,
            "production_claim_allowed": False
        }
    }
    schema_path.write_text(json.dumps(schema_payload, indent=2, sort_keys=True), encoding="utf-8")

    rows_json_path.write_text(
        json.dumps(
            {
                "schema_name": "MME-ScalpX Replay Optimization Result Binding Rows",
                "contract_version": RESULT_BINDING_CONTRACT_VERSION,
                "accepted_for": RESULT_BINDING_ACCEPTED_FOR,
                "optimization_id": optimization_id,
                "created_at": _utc_now(),
                "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
                "ml_dataset_path": str(ml_dataset_path) if ml_dataset_path else None,
                "replay_index_path": str(replay_index_path) if replay_index_path else None,
                "binding_row_count": len(rows),
                "rows": row_dicts,
                "safety": {
                    "replay_execution_performed": False,
                    "labels_bound": False,
                    "model_training_performed": False,
                    "broker_calls_executed": False,
                    "live_redis_writes_executed": False,
                    "paper_or_live_enabled": False
                }
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    _write_csv(rows_csv_path, RESULT_BINDING_COLUMNS, row_dicts)

    verdict_row = OptimizerVerdictRow(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        verdict=readiness,
        sample_days=0,
        sample_trades=0,
        risk_notes=(
            "D8 freezes result-binding schema only. No labels are bound, no replay is executed, "
            "no model is trained, and no profit claim is allowed."
        ),
        production_claim_allowed=False,
        paper_live_approved=False,
        remarks="Result-binding rows remain UNBOUND until verified replay binding exists.",
    )
    verdict_path.write_text(json.dumps(row_to_dict(verdict_row), indent=2, sort_keys=True), encoding="utf-8")

    return ResultBindingBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=RESULT_BINDING_CONTRACT_VERSION,
        accepted_for=RESULT_BINDING_ACCEPTED_FOR,
        candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
        ml_dataset_path=str(ml_dataset_path) if ml_dataset_path else None,
        replay_index_path=str(replay_index_path) if replay_index_path else None,
        result_binding_schema_path=schema_path.as_posix(),
        result_binding_rows_json_path=rows_json_path.as_posix(),
        result_binding_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        binding_row_count=len(rows),
        readiness_verdict=readiness,
    )


def result_binding_summary(
    *,
    ml_dataset_path: str | Path | None,
    replay_index_path: str | Path | None,
    max_rows: int = 10000,
) -> dict[str, Any]:
    rows = build_result_binding_rows(
        "D8_SUMMARY",
        candidate_matrix_path=None,
        ml_dataset_path=ml_dataset_path,
        replay_index_path=replay_index_path,
        max_rows=max_rows,
    )
    readiness = _readiness_from_sources(
        _safe_load_json(ml_dataset_path),
        _safe_load_json(replay_index_path),
    )
    return {
        "contract_version": RESULT_BINDING_CONTRACT_VERSION,
        "accepted_for": RESULT_BINDING_ACCEPTED_FOR,
        "binding_row_count": len(rows),
        "readiness_verdict": readiness,
        "labels_bound": False,
        "replay_execution_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "RESULT_BINDING_CONTRACT_VERSION",
    "RESULT_BINDING_ACCEPTED_FOR",
    "RESULT_BINDING_STATUS_UNBOUND",
    "RESULT_BINDING_STATUS_BLOCKED",
    "RESULT_BINDING_STATUS_READY_FOR_FUTURE_BINDING",
    "RESULT_BINDING_COLUMNS",
    "ResultBindingRow",
    "ResultBindingBuildResult",
    "build_result_binding_rows",
    "write_result_binding_schema",
    "result_binding_summary",
)
