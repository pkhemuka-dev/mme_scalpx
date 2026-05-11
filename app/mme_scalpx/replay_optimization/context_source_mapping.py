"""Lane D D27 context-source mapping schema contract.

This module freezes a schema-only mapping from required candidate context keys
to discovered source keys in verified replay artifacts.

D27 does not infer/fill candidate context, perform candidate-to-trade matching,
bind labels, calculate PnL, train/predict models, execute replay, call brokers,
write live Redis, mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CONTEXT_SOURCE_MAPPING_CONTRACT_VERSION = "replay_optimization_d27_context_source_mapping_contract_v1"
CONTEXT_SOURCE_MAPPING_ACCEPTED_FOR = "CONTEXT_SOURCE_MAPPING_SCHEMA_CONTRACT_ONLY"

MAPPING_STATUS_SCHEMA_ONLY_NOT_LABEL_READY = "CONTEXT_SOURCE_MAPPING_SCHEMA_ONLY_NOT_LABEL_READY"
MAPPING_STATUS_BLOCKED_NO_SOURCE_DISCOVERY = "BLOCKED_NO_D26_SOURCE_DISCOVERY"
MAPPING_STATUS_BLOCKED_MISSING_REQUIRED_CONTEXT_MAPPING = "BLOCKED_MISSING_REQUIRED_CONTEXT_MAPPING"

REQUIRED_CONTEXT_KEYS = (
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
)

ARTIFACT_PRIORITY = {
    "context_symbol": ("features_ref", "strategy_ref", "risk_ref", "execution_shadow_ref"),
    "context_event_time": ("features_ref", "strategy_ref", "risk_ref", "execution_shadow_ref"),
    "context_frame_id": ("features_ref", "strategy_ref", "risk_ref", "execution_shadow_ref"),
    "context_decision_id": ("strategy_ref", "risk_ref", "features_ref", "execution_shadow_ref"),
    "context_risk_id": ("risk_ref", "execution_shadow_ref", "strategy_ref", "features_ref"),
}

CONTEXT_SOURCE_MAPPING_COLUMNS = (
    "optimization_id",
    "mapping_id",
    "context_key",
    "selected_artifact_field",
    "selected_artifact_label",
    "selected_artifact_ref",
    "selected_source_key",
    "candidate_source_keys",
    "available_source_keys",
    "source_row_id",
    "artifact_row_count",
    "all_rows_have_at_least_one_source_key",
    "mapping_confidence",
    "mapping_status",
    "candidate_context_inference_allowed",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class ContextSourceMappingRow:
    optimization_id: str
    mapping_id: str
    context_key: str
    selected_artifact_field: str | None
    selected_artifact_label: str | None
    selected_artifact_ref: str | None
    selected_source_key: str | None
    candidate_source_keys: str
    available_source_keys: str
    source_row_id: str | None
    artifact_row_count: int
    all_rows_have_at_least_one_source_key: bool
    mapping_confidence: str
    mapping_status: str
    candidate_context_inference_allowed: bool = False
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ContextSourceMappingBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    source_discovery_report_path: str | None
    mapping_schema_path: str
    mapping_rows_json_path: str
    mapping_rows_csv_path: str
    optimizer_verdict_path: str
    mapping_row_count: int
    required_context_mapping_count: int
    missing_required_context_mapping_count: int
    mapping_status: str
    candidate_context_inference_allowed: bool = False
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
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
        raise ValueError(f"D27 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _select_source_row(context_key: str, rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    candidates = [
        row for row in rows
        if row.get("context_key") == context_key
        and int(row.get("available_source_key_count") or 0) > 0
    ]
    if not candidates:
        return None

    priority = ARTIFACT_PRIORITY.get(context_key, tuple())
    for artifact_field in priority:
        for row in candidates:
            if row.get("artifact_field") == artifact_field:
                return row

    return candidates[0]


def _first_available_key(row: Mapping[str, Any] | None) -> str | None:
    if not row:
        return None
    keys = str(row.get("available_source_keys") or "").split(",")
    keys = [key.strip() for key in keys if key.strip()]
    return keys[0] if keys else None


def build_context_source_mapping_rows(
    optimization_id: str,
    *,
    source_discovery_report_path: str | Path | None,
) -> tuple[ContextSourceMappingRow, ...]:
    payload = _safe_load_json(source_discovery_report_path)
    rows = _rows_from_payload(payload)

    if not rows:
        return tuple()

    mapped_rows: list[ContextSourceMappingRow] = []
    for i, context_key in enumerate(REQUIRED_CONTEXT_KEYS, start=1):
        source = _select_source_row(context_key, rows)
        selected_source_key = _first_available_key(source)

        if source and selected_source_key:
            status = MAPPING_STATUS_SCHEMA_ONLY_NOT_LABEL_READY
            confidence = "schema_source_available"
            remarks = (
                "Source mapping selected from D26 discovery. D27 does not infer/fill "
                "candidate context or bind labels."
            )
        else:
            status = MAPPING_STATUS_BLOCKED_MISSING_REQUIRED_CONTEXT_MAPPING
            confidence = "none"
            remarks = "No usable source key mapping found for this required context key."

        mapped_rows.append(
            ContextSourceMappingRow(
                optimization_id=optimization_id,
                mapping_id=f"MAP_{i:04d}",
                context_key=context_key,
                selected_artifact_field=str(source.get("artifact_field")) if source else None,
                selected_artifact_label=str(source.get("artifact_label")) if source else None,
                selected_artifact_ref=str(source.get("artifact_ref")) if source and source.get("artifact_ref") else None,
                selected_source_key=selected_source_key,
                candidate_source_keys=str(source.get("candidate_source_keys") or "") if source else "",
                available_source_keys=str(source.get("available_source_keys") or "") if source else "",
                source_row_id=str(source.get("source_row_id")) if source else None,
                artifact_row_count=int(source.get("artifact_row_count") or 0) if source else 0,
                all_rows_have_at_least_one_source_key=bool(source.get("all_rows_have_at_least_one_source_key")) if source else False,
                mapping_confidence=confidence,
                mapping_status=status,
                candidate_context_inference_allowed=False,
                candidate_trade_matching_allowed=False,
                candidate_trade_matching_performed=False,
                label_binding_allowed=False,
                labels_bound=False,
                remarks=remarks,
            )
        )

    return tuple(mapped_rows)


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_context_source_mapping_schema(
    optimization_id: str,
    output_dir: str | Path,
    *,
    source_discovery_report_path: str | Path | None,
) -> ContextSourceMappingBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_context_source_mapping_rows(
        optimization_id,
        source_discovery_report_path=source_discovery_report_path,
    )
    row_dicts = [asdict(row) for row in rows]

    required_mapped = sum(
        1 for row in rows
        if row.context_key in REQUIRED_CONTEXT_KEYS
        and row.selected_source_key
        and row.mapping_status == MAPPING_STATUS_SCHEMA_ONLY_NOT_LABEL_READY
    )
    missing = len(REQUIRED_CONTEXT_KEYS) - required_mapped

    if not rows:
        status = MAPPING_STATUS_BLOCKED_NO_SOURCE_DISCOVERY
    elif missing:
        status = MAPPING_STATUS_BLOCKED_MISSING_REQUIRED_CONTEXT_MAPPING
    else:
        status = MAPPING_STATUS_SCHEMA_ONLY_NOT_LABEL_READY

    schema_path = out / "30_context_source_mapping_schema.json"
    rows_json_path = out / "30_context_source_mapping_rows.json"
    rows_csv_path = out / "30_context_source_mapping_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    schema_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Context Source Mapping Schema",
        "contract_version": CONTEXT_SOURCE_MAPPING_CONTRACT_VERSION,
        "accepted_for": CONTEXT_SOURCE_MAPPING_ACCEPTED_FOR,
        "columns": list(CONTEXT_SOURCE_MAPPING_COLUMNS),
        "required_context_keys": list(REQUIRED_CONTEXT_KEYS),
        "mapping_policy": {
            "d27_is_schema_only": True,
            "source_mapping_selected": True,
            "candidate_context_inference_allowed_in_d27": False,
            "candidate_trade_matching_allowed_in_d27": False,
            "label_binding_allowed_in_d27": False,
            "future_context_enrichment_dry_run_required": True
        },
        "safety": {
            "candidate_context_inference_allowed": False,
            "candidate_trade_matching_allowed": False,
            "candidate_trade_matching_performed": False,
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
    }
    schema_path.write_text(json.dumps(schema_payload, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Context Source Mapping Rows",
        "contract_version": CONTEXT_SOURCE_MAPPING_CONTRACT_VERSION,
        "accepted_for": CONTEXT_SOURCE_MAPPING_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "source_discovery_report_path": str(source_discovery_report_path) if source_discovery_report_path else None,
        "mapping_status": status,
        "mapping_row_count": len(rows),
        "required_context_mapping_count": required_mapped,
        "missing_required_context_mapping_count": missing,
        "rows": row_dicts,
        "safety": schema_payload["safety"],
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, CONTEXT_SOURCE_MAPPING_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CONTEXT_SOURCE_MAPPING_CONTRACT_VERSION,
        "accepted_for": CONTEXT_SOURCE_MAPPING_ACCEPTED_FOR,
        "mapping_status": status,
        "mapping_row_count": len(rows),
        "required_context_mapping_count": required_mapped,
        "missing_required_context_mapping_count": missing,
        "candidate_context_inference_allowed": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D27 freezes context source mappings only. No context values are filled.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return ContextSourceMappingBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CONTEXT_SOURCE_MAPPING_CONTRACT_VERSION,
        accepted_for=CONTEXT_SOURCE_MAPPING_ACCEPTED_FOR,
        source_discovery_report_path=str(source_discovery_report_path) if source_discovery_report_path else None,
        mapping_schema_path=schema_path.as_posix(),
        mapping_rows_json_path=rows_json_path.as_posix(),
        mapping_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        mapping_row_count=len(rows),
        required_context_mapping_count=required_mapped,
        missing_required_context_mapping_count=missing,
        mapping_status=status,
    )


__all__ = (
    "CONTEXT_SOURCE_MAPPING_CONTRACT_VERSION",
    "CONTEXT_SOURCE_MAPPING_ACCEPTED_FOR",
    "MAPPING_STATUS_SCHEMA_ONLY_NOT_LABEL_READY",
    "MAPPING_STATUS_BLOCKED_NO_SOURCE_DISCOVERY",
    "MAPPING_STATUS_BLOCKED_MISSING_REQUIRED_CONTEXT_MAPPING",
    "REQUIRED_CONTEXT_KEYS",
    "ARTIFACT_PRIORITY",
    "CONTEXT_SOURCE_MAPPING_COLUMNS",
    "ContextSourceMappingRow",
    "ContextSourceMappingBuildResult",
    "build_context_source_mapping_rows",
    "write_context_source_mapping_schema",
)
