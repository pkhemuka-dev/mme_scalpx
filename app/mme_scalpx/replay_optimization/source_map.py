"""Lane D D11 replay result source-map contract.

This module builds a reference-only map between unbound result-binding rows and
available replay artifacts. It does not bind labels, calculate PnL, execute
replay, train/predict models, or approve paper/live usage.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

SOURCE_MAP_CONTRACT_VERSION = "replay_optimization_d11_source_map_contract_v1"
SOURCE_MAP_ACCEPTED_FOR = "REPLAY_RESULT_SOURCE_MAP_CONTRACT_ONLY"

SOURCE_MAP_STATUS_REFERENCE_ONLY = "REFERENCE_ONLY_UNVERIFIED_NO_LABEL_BINDING"
SOURCE_MAP_STATUS_MISSING_REPLAY_INDEX = "MISSING_REPLAY_INDEX"
SOURCE_MAP_STATUS_MISSING_BINDING_ROWS = "MISSING_RESULT_BINDING_ROWS"

SOURCE_MAP_COLUMNS = (
    "optimization_id",
    "source_map_id",
    "binding_id",
    "candidate_id",
    "ml_row_id",
    "feature_vector_ref",
    "replay_index_path",
    "result_binding_rows_path",
    "replay_artifact_count",
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
    "source_map_status",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class ReplayResultSourceMapRow:
    optimization_id: str
    source_map_id: str
    binding_id: str
    candidate_id: str
    ml_row_id: str
    feature_vector_ref: str
    replay_index_path: str | None
    result_binding_rows_path: str | None
    replay_artifact_count: int
    manifest_ref: str | None = None
    integrity_ref: str | None = None
    features_ref: str | None = None
    strategy_ref: str | None = None
    risk_ref: str | None = None
    execution_shadow_ref: str | None = None
    source_map_status: str = SOURCE_MAP_STATUS_REFERENCE_ONLY
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class SourceMapBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    replay_index_path: str | None
    result_binding_rows_path: str | None
    source_map_json_path: str
    source_map_csv_path: str
    optimizer_verdict_path: str
    source_map_row_count: int
    source_map_status: str
    label_binding_allowed: bool = False
    labels_bound: bool = False
    replay_execution_performed: bool = False
    real_pnl_calculation_performed: bool = False
    model_training_performed: bool = False
    model_prediction_performed: bool = False
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


def _rows_from_payload(payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


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
        raise ValueError(f"D11 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _artifact_refs_by_kind(replay_index_payload: Mapping[str, Any] | None) -> dict[str, str]:
    refs: dict[str, str] = {}
    artifacts = replay_index_payload.get("artifacts") if replay_index_payload else None
    if not isinstance(artifacts, list):
        return refs

    priority = {
        "manifest": "manifest_ref",
        "replay_manifest": "manifest_ref",
        "integrity_report": "integrity_ref",
        "features_rows": "features_ref",
        "strategy_decisions": "strategy_ref",
        "risk_outputs": "risk_ref",
        "execution_shadow_results": "execution_shadow_ref",
        "execution_results": "execution_shadow_ref",
    }

    for item in artifacts:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("artifact_kind") or "")
        path = item.get("path")
        target = priority.get(kind)
        if target and isinstance(path, str) and target not in refs:
            refs[target] = path
    return refs


def build_source_map_rows(
    optimization_id: str,
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[ReplayResultSourceMapRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    replay_index = _safe_load_json(replay_index_path)
    binding_payload = _safe_load_json(result_binding_rows_path)
    binding_rows = _rows_from_payload(binding_payload)

    if not replay_index:
        status = SOURCE_MAP_STATUS_MISSING_REPLAY_INDEX
    elif not binding_rows:
        status = SOURCE_MAP_STATUS_MISSING_BINDING_ROWS
    else:
        status = SOURCE_MAP_STATUS_REFERENCE_ONLY

    replay_artifact_count = int(replay_index.get("artifact_count", 0)) if replay_index else 0
    refs = _artifact_refs_by_kind(replay_index)

    rows: list[ReplayResultSourceMapRow] = []
    for i, row in enumerate(binding_rows[:max_rows], start=1):
        rows.append(
            ReplayResultSourceMapRow(
                optimization_id=optimization_id,
                source_map_id=f"SMAP_{i:06d}",
                binding_id=str(row.get("binding_id") or f"BIND_UNKNOWN_{i:06d}"),
                candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                ml_row_id=str(row.get("ml_row_id") or ""),
                feature_vector_ref=str(row.get("feature_vector_ref") or ""),
                replay_index_path=str(replay_index_path) if replay_index_path else None,
                result_binding_rows_path=str(result_binding_rows_path) if result_binding_rows_path else None,
                replay_artifact_count=replay_artifact_count,
                manifest_ref=refs.get("manifest_ref"),
                integrity_ref=refs.get("integrity_ref"),
                features_ref=refs.get("features_ref"),
                strategy_ref=refs.get("strategy_ref"),
                risk_ref=refs.get("risk_ref"),
                execution_shadow_ref=refs.get("execution_shadow_ref"),
                source_map_status=status,
                label_binding_allowed=False,
                labels_bound=False,
                remarks=(
                    "D11 source map is reference-only. Candidate-to-trade matching "
                    "and label binding are intentionally not performed."
                ),
            )
        )
    return tuple(rows)


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_source_map(
    optimization_id: str,
    output_dir: str | Path,
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> SourceMapBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_source_map_rows(
        optimization_id,
        replay_index_path=replay_index_path,
        result_binding_rows_path=result_binding_rows_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in rows]
    status = rows[0].source_map_status if rows else SOURCE_MAP_STATUS_MISSING_BINDING_ROWS

    json_path = out / "14_replay_result_source_map.json"
    csv_path = out / "14_replay_result_source_map.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    json_path.write_text(
        json.dumps(
            {
                "schema_name": "MME-ScalpX Replay Optimization Replay Result Source Map",
                "contract_version": SOURCE_MAP_CONTRACT_VERSION,
                "accepted_for": SOURCE_MAP_ACCEPTED_FOR,
                "optimization_id": optimization_id,
                "created_at": _utc_now(),
                "replay_index_path": str(replay_index_path) if replay_index_path else None,
                "result_binding_rows_path": str(result_binding_rows_path) if result_binding_rows_path else None,
                "source_map_row_count": len(rows),
                "source_map_status": status,
                "rows": row_dicts,
                "safety": {
                    "label_binding_allowed": False,
                    "labels_bound": False,
                    "replay_execution_performed": False,
                    "real_pnl_calculation_performed": False,
                    "model_training_performed": False,
                    "model_prediction_performed": False,
                    "broker_calls_executed": False,
                    "live_redis_writes_executed": False,
                    "paper_or_live_enabled": False
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    _write_csv(csv_path, SOURCE_MAP_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": SOURCE_MAP_CONTRACT_VERSION,
        "accepted_for": SOURCE_MAP_ACCEPTED_FOR,
        "source_map_status": status,
        "label_binding_allowed": False,
        "labels_bound": False,
        "implementation_allowed": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D11 builds source-map references only. No label binding or PnL calculation.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return SourceMapBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=SOURCE_MAP_CONTRACT_VERSION,
        accepted_for=SOURCE_MAP_ACCEPTED_FOR,
        replay_index_path=str(replay_index_path) if replay_index_path else None,
        result_binding_rows_path=str(result_binding_rows_path) if result_binding_rows_path else None,
        source_map_json_path=json_path.as_posix(),
        source_map_csv_path=csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        source_map_row_count=len(rows),
        source_map_status=status,
    )


def source_map_summary(
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
) -> dict[str, Any]:
    rows = build_source_map_rows(
        "D11_SUMMARY",
        replay_index_path=replay_index_path,
        result_binding_rows_path=result_binding_rows_path,
        max_rows=10000,
    )
    status = rows[0].source_map_status if rows else SOURCE_MAP_STATUS_MISSING_BINDING_ROWS
    return {
        "contract_version": SOURCE_MAP_CONTRACT_VERSION,
        "accepted_for": SOURCE_MAP_ACCEPTED_FOR,
        "source_map_row_count": len(rows),
        "source_map_status": status,
        "label_binding_allowed": False,
        "labels_bound": False,
        "replay_execution_performed": False,
        "real_pnl_calculation_performed": False,
        "model_training_performed": False,
        "model_prediction_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "SOURCE_MAP_CONTRACT_VERSION",
    "SOURCE_MAP_ACCEPTED_FOR",
    "SOURCE_MAP_STATUS_REFERENCE_ONLY",
    "SOURCE_MAP_STATUS_MISSING_REPLAY_INDEX",
    "SOURCE_MAP_STATUS_MISSING_BINDING_ROWS",
    "SOURCE_MAP_COLUMNS",
    "ReplayResultSourceMapRow",
    "SourceMapBuildResult",
    "build_source_map_rows",
    "write_source_map",
    "source_map_summary",
)
