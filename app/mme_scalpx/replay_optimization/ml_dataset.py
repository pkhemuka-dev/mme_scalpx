"""Lane D D7 ML dataset schema/exporter contract.

This module exports a research-only ML dataset shell from D5 candidate-matrix
rows. It intentionally does not train models and does not bind real PnL labels
until future verified replay-result binding exists.

It must not execute replay, train models, call brokers, write live state,
start runtime services, mutate strategy doctrine, or mutate replay engine code.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import (
    ML_DATASET_COLUMNS,
    OUTPUT_ROOT,
    VERDICT_NOT_READY_REPLAY_SOURCE_MISSING,
    VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
    MLDatasetRow,
    OptimizerVerdictRow,
    row_to_dict,
)

ML_DATASET_CONTRACT_VERSION = "replay_optimization_d7_ml_dataset_export_contract_v1"
ML_DATASET_ACCEPTED_FOR = "ML_DATASET_SCHEMA_EXPORT_CONTRACT_ONLY"


@dataclass(frozen=True, slots=True)
class MLDatasetExportResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    candidate_matrix_path: str | None
    ml_dataset_schema_path: str
    ml_dataset_json_path: str
    ml_dataset_csv_path: str
    ml_training_manifest_path: str
    optimizer_verdict_path: str
    ml_dataset_row_count: int
    readiness_verdict: str
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
        raise ValueError(f"D7 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _matrix_rows(candidate_matrix_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not candidate_matrix_payload:
        return []
    rows = candidate_matrix_payload.get("rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _readiness_from_matrix(candidate_matrix_payload: Mapping[str, Any] | None) -> str:
    rows = _matrix_rows(candidate_matrix_payload)
    if not rows:
        return VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    value = rows[0].get("readiness_verdict")
    if isinstance(value, str) and value:
        return value
    return VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE


def _feature_vector_ref(row: Mapping[str, Any]) -> str:
    parts = [
        row.get("candidate_id"),
        row.get("strategy_family"),
        row.get("side"),
        row.get("regime"),
        row.get("parameter_group"),
        row.get("parameter_name"),
        row.get("candidate_value"),
    ]
    return "|".join("" if value is None else str(value) for value in parts)


def build_ml_dataset_rows(
    optimization_id: str,
    *,
    candidate_matrix_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[MLDatasetRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    matrix_payload = _safe_load_json(candidate_matrix_path)
    matrix_rows = _matrix_rows(matrix_payload)

    out: list[MLDatasetRow] = []
    for i, row in enumerate(matrix_rows[:max_rows], start=1):
        out.append(
            MLDatasetRow(
                optimization_id=optimization_id,
                row_id=f"MLROW_{i:06d}",
                candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                replay_run_id="UNBOUND_D7_NO_REPLAY_RESULT_LABEL",
                strategy_family=str(row.get("strategy_family") or "UNKNOWN"),
                side=str(row.get("side") or "UNKNOWN"),
                regime=str(row.get("regime") or "UNKNOWN"),
                feature_vector_ref=_feature_vector_ref(row),
                label_pnl=None,
                label_profitable=None,
                label_exit_reason=None,
                usage_class="research_only_unlabeled",
                compute_stage="schema_export_only",
                storage_target=OUTPUT_ROOT,
                source_verified=False,
                remarks=(
                    "D7 schema-only ML dataset row. Labels are intentionally null "
                    "until verified replay-result binding exists."
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


def write_ml_dataset_export(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_matrix_path: str | Path | None,
    max_rows: int = 10000,
) -> MLDatasetExportResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    matrix_payload = _safe_load_json(candidate_matrix_path)
    readiness = _readiness_from_matrix(matrix_payload)
    rows = build_ml_dataset_rows(
        optimization_id,
        candidate_matrix_path=candidate_matrix_path,
        max_rows=max_rows,
    )
    row_dicts = [row_to_dict(row) for row in rows]

    schema_path = out / "07_ml_dataset_schema.json"
    dataset_json_path = out / "07_ml_dataset_rows.json"
    dataset_csv_path = out / "07_ml_dataset_rows.csv"
    training_manifest_path = out / "08_ml_training_manifest.json"
    verdict_path = out / "09_optimizer_verdict.json"

    schema_payload = {
        "schema_name": "MME-ScalpX Replay Optimization ML Dataset Schema",
        "contract_version": ML_DATASET_CONTRACT_VERSION,
        "accepted_for": ML_DATASET_ACCEPTED_FOR,
        "columns": list(ML_DATASET_COLUMNS),
        "label_policy": {
            "label_pnl_required_for_training": True,
            "label_profitable_required_for_training": True,
            "d7_labels_are_null": True,
            "training_allowed_in_d7": False,
            "production_claim_allowed": False
        },
        "source_policy": {
            "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
            "requires_future_verified_replay_result_binding": True,
            "requires_future_sample_size_report": True,
            "requires_future_overfit_risk_report": True
        },
        "safety": {
            "replay_execution_performed": False,
            "model_training_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False
        }
    }
    schema_path.write_text(json.dumps(schema_payload, indent=2, sort_keys=True), encoding="utf-8")

    dataset_json_path.write_text(
        json.dumps(
            {
                "schema_name": "MME-ScalpX Replay Optimization ML Dataset Rows",
                "contract_version": ML_DATASET_CONTRACT_VERSION,
                "accepted_for": ML_DATASET_ACCEPTED_FOR,
                "optimization_id": optimization_id,
                "created_at": _utc_now(),
                "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
                "ml_dataset_row_count": len(rows),
                "rows": row_dicts,
                "safety": {
                    "replay_execution_performed": False,
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

    _write_csv(dataset_csv_path, ML_DATASET_COLUMNS, row_dicts)

    training_manifest = {
        "schema_name": "MME-ScalpX Replay Optimization ML Training Manifest",
        "contract_version": ML_DATASET_CONTRACT_VERSION,
        "accepted_for": ML_DATASET_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "training_status": "NOT_STARTED_D7_SCHEMA_ONLY",
        "training_allowed": False,
        "reason": "D7 exports schema/unlabeled rows only. Verified labels are not bound yet.",
        "dataset_json_path": dataset_json_path.as_posix(),
        "dataset_csv_path": dataset_csv_path.as_posix(),
        "row_count": len(rows),
        "label_pnl_bound": False,
        "label_profitable_bound": False,
        "overfit_report_present": False,
        "sample_size_report_present": False,
        "production_claim_allowed": False,
        "paper_live_approved": False,
        "safety": {
            "replay_execution_performed": False,
            "model_training_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False
        }
    }
    training_manifest_path.write_text(json.dumps(training_manifest, indent=2, sort_keys=True), encoding="utf-8")

    verdict_row = OptimizerVerdictRow(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        verdict=readiness,
        sample_days=0,
        sample_trades=0,
        risk_notes=(
            "D7 exports ML dataset schema only. No labels, no training, no PnL claim, "
            "no paper/live approval."
        ),
        production_claim_allowed=False,
        paper_live_approved=False,
        remarks="ML dataset rows are unlabeled research-only shells.",
    )
    verdict_path.write_text(json.dumps(row_to_dict(verdict_row), indent=2, sort_keys=True), encoding="utf-8")

    return MLDatasetExportResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=ML_DATASET_CONTRACT_VERSION,
        accepted_for=ML_DATASET_ACCEPTED_FOR,
        candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
        ml_dataset_schema_path=schema_path.as_posix(),
        ml_dataset_json_path=dataset_json_path.as_posix(),
        ml_dataset_csv_path=dataset_csv_path.as_posix(),
        ml_training_manifest_path=training_manifest_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        ml_dataset_row_count=len(rows),
        readiness_verdict=readiness,
    )


def ml_dataset_summary(
    *,
    candidate_matrix_path: str | Path | None,
    max_rows: int = 10000,
) -> dict[str, Any]:
    rows = build_ml_dataset_rows(
        "D7_SUMMARY",
        candidate_matrix_path=candidate_matrix_path,
        max_rows=max_rows,
    )
    matrix_payload = _safe_load_json(candidate_matrix_path)
    readiness = _readiness_from_matrix(matrix_payload)
    return {
        "contract_version": ML_DATASET_CONTRACT_VERSION,
        "accepted_for": ML_DATASET_ACCEPTED_FOR,
        "ml_dataset_row_count": len(rows),
        "readiness_verdict": readiness,
        "labels_bound": False,
        "training_allowed": False,
        "replay_execution_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "ML_DATASET_CONTRACT_VERSION",
    "ML_DATASET_ACCEPTED_FOR",
    "MLDatasetExportResult",
    "build_ml_dataset_rows",
    "write_ml_dataset_export",
    "ml_dataset_summary",
)
