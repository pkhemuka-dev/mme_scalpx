"""Lane D D28 context-enrichment dry-run audit.

This module builds a result-context catalog from verified replay artifacts using
D27 source mappings.

D28 does not attach context to candidate rows, perform candidate-to-trade
matching, bind labels, calculate PnL, train/predict models, execute replay,
call brokers, write live Redis, mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CONTEXT_ENRICHMENT_DRY_RUN_CONTRACT_VERSION = "replay_optimization_d28_context_enrichment_dry_run_contract_v1"
CONTEXT_ENRICHMENT_DRY_RUN_ACCEPTED_FOR = "CONTEXT_ENRICHMENT_DRY_RUN_AUDIT_ONLY"

DRY_RUN_STATUS_RESULT_CONTEXT_CATALOG_READY = "RESULT_CONTEXT_CATALOG_DRY_RUN_READY_NOT_LABEL_READY"
DRY_RUN_STATUS_BLOCKED_NO_CONTEXT_ROWS = "BLOCKED_NO_D25_CONTEXT_ROWS"
DRY_RUN_STATUS_BLOCKED_NO_MAPPING_ROWS = "BLOCKED_NO_D27_MAPPING_ROWS"
DRY_RUN_STATUS_BLOCKED_INCOMPLETE_MAPPING = "BLOCKED_INCOMPLETE_CONTEXT_SOURCE_MAPPING"
DRY_RUN_STATUS_BLOCKED_NO_RESULT_ROWS = "BLOCKED_NO_RESULT_ROWS_FOR_CONTEXT_CATALOG"

REQUIRED_CONTEXT_KEYS = (
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
)

RESULT_CONTEXT_COLUMNS = (
    "optimization_id",
    "result_context_id",
    "result_row_index",
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
    "source_context_symbol",
    "source_context_event_time",
    "source_context_frame_id",
    "source_context_decision_id",
    "source_context_risk_id",
    "result_context_complete",
    "candidate_id",
    "candidate_context_attached",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "label_pnl",
    "label_profitable",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class ResultContextCatalogRow:
    optimization_id: str
    result_context_id: str
    result_row_index: int
    context_symbol: str | None
    context_event_time: str | None
    context_frame_id: str | None
    context_decision_id: str | None
    context_risk_id: str | None
    source_context_symbol: str | None
    source_context_event_time: str | None
    source_context_frame_id: str | None
    source_context_decision_id: str | None
    source_context_risk_id: str | None
    result_context_complete: bool
    candidate_id: str | None = None
    candidate_context_attached: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    label_pnl: float | None = None
    label_profitable: bool | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ContextEnrichmentDryRunBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    context_rows_path: str | None
    mapping_rows_path: str | None
    dry_run_report_path: str
    result_context_rows_json_path: str
    result_context_rows_csv_path: str
    optimizer_verdict_path: str
    candidate_context_row_count: int
    candidate_context_complete_count: int
    candidate_context_attached_count: int
    result_context_row_count: int
    result_context_complete_count: int
    mapping_row_count: int
    dry_run_status: str
    result_context_catalog_built: bool = False
    candidate_context_inference_allowed: bool = False
    candidate_context_attached: bool = False
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
        raise ValueError(f"D28 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _mapping_by_context_key(mapping_rows: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    out: dict[str, Mapping[str, Any]] = {}
    for row in mapping_rows:
        key = row.get("context_key")
        source_key = row.get("selected_source_key")
        ref = row.get("selected_artifact_ref")
        if isinstance(key, str) and key and source_key and ref:
            out[key] = row
    return out


def _load_rows_for_mapping(mapping: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _rows_from_payload(_safe_load_json(mapping.get("selected_artifact_ref")))


def _value_at(mapping: Mapping[str, Any], source_rows: Sequence[Mapping[str, Any]], index: int) -> str | None:
    if index >= len(source_rows):
        return None
    source_key = mapping.get("selected_source_key")
    if not isinstance(source_key, str) or not source_key:
        return None
    value = source_rows[index].get(source_key)
    return None if value is None else str(value)


def build_result_context_catalog_rows(
    optimization_id: str,
    *,
    mapping_rows_path: str | Path | None,
) -> tuple[ResultContextCatalogRow, ...]:
    mapping_payload = _safe_load_json(mapping_rows_path)
    mapping_rows = _rows_from_payload(mapping_payload)
    mapping_by_key = _mapping_by_context_key(mapping_rows)

    if any(key not in mapping_by_key for key in REQUIRED_CONTEXT_KEYS):
        return tuple()

    source_rows_by_key = {
        key: _load_rows_for_mapping(mapping_by_key[key])
        for key in REQUIRED_CONTEXT_KEYS
    }
    row_counts = [len(rows) for rows in source_rows_by_key.values()]
    if not row_counts or min(row_counts) <= 0:
        return tuple()

    min_rows = min(row_counts)
    out: list[ResultContextCatalogRow] = []

    for index in range(min_rows):
        values = {
            key: _value_at(mapping_by_key[key], source_rows_by_key[key], index)
            for key in REQUIRED_CONTEXT_KEYS
        }
        complete = all(values.get(key) is not None for key in REQUIRED_CONTEXT_KEYS)

        out.append(
            ResultContextCatalogRow(
                optimization_id=optimization_id,
                result_context_id=f"RCTX_{index + 1:06d}",
                result_row_index=index,
                context_symbol=values["context_symbol"],
                context_event_time=values["context_event_time"],
                context_frame_id=values["context_frame_id"],
                context_decision_id=values["context_decision_id"],
                context_risk_id=values["context_risk_id"],
                source_context_symbol=str(mapping_by_key["context_symbol"].get("selected_artifact_label")) + "." + str(mapping_by_key["context_symbol"].get("selected_source_key")),
                source_context_event_time=str(mapping_by_key["context_event_time"].get("selected_artifact_label")) + "." + str(mapping_by_key["context_event_time"].get("selected_source_key")),
                source_context_frame_id=str(mapping_by_key["context_frame_id"].get("selected_artifact_label")) + "." + str(mapping_by_key["context_frame_id"].get("selected_source_key")),
                source_context_decision_id=str(mapping_by_key["context_decision_id"].get("selected_artifact_label")) + "." + str(mapping_by_key["context_decision_id"].get("selected_source_key")),
                source_context_risk_id=str(mapping_by_key["context_risk_id"].get("selected_artifact_label")) + "." + str(mapping_by_key["context_risk_id"].get("selected_source_key")),
                result_context_complete=complete,
                candidate_id=None,
                candidate_context_attached=False,
                candidate_trade_matching_performed=False,
                label_binding_allowed=False,
                labels_bound=False,
                label_pnl=None,
                label_profitable=None,
                remarks=(
                    "D28 result-context catalog row only. This row is not attached "
                    "to any candidate and cannot be used as a label."
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


def write_context_enrichment_dry_run(
    optimization_id: str,
    output_dir: str | Path,
    *,
    context_rows_path: str | Path | None,
    mapping_rows_path: str | Path | None,
) -> ContextEnrichmentDryRunBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    context_payload = _safe_load_json(context_rows_path)
    context_rows = _rows_from_payload(context_payload)

    mapping_payload = _safe_load_json(mapping_rows_path)
    mapping_rows = _rows_from_payload(mapping_payload)

    result_context_rows = build_result_context_catalog_rows(
        optimization_id,
        mapping_rows_path=mapping_rows_path,
    )
    result_context_dicts = [asdict(row) for row in result_context_rows]

    candidate_context_complete = sum(1 for row in context_rows if row.get("candidate_context_complete") is True)
    candidate_context_attached = 0
    result_context_complete = sum(1 for row in result_context_rows if row.result_context_complete)

    if not context_rows:
        status = DRY_RUN_STATUS_BLOCKED_NO_CONTEXT_ROWS
    elif not mapping_rows:
        status = DRY_RUN_STATUS_BLOCKED_NO_MAPPING_ROWS
    elif len(mapping_rows) < len(REQUIRED_CONTEXT_KEYS):
        status = DRY_RUN_STATUS_BLOCKED_INCOMPLETE_MAPPING
    elif not result_context_rows:
        status = DRY_RUN_STATUS_BLOCKED_NO_RESULT_ROWS
    else:
        status = DRY_RUN_STATUS_RESULT_CONTEXT_CATALOG_READY

    report_path = out / "31_context_enrichment_dry_run_report.json"
    rows_json_path = out / "31_result_context_catalog_rows.json"
    rows_csv_path = out / "31_result_context_catalog_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
        "result_context_catalog_built": bool(result_context_rows),
        "candidate_context_inference_allowed": False,
        "candidate_context_attached": False,
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
        "paper_or_live_enabled": False,
    }

    report = {
        "schema_name": "MME-ScalpX Replay Optimization Context Enrichment Dry-Run Audit",
        "contract_version": CONTEXT_ENRICHMENT_DRY_RUN_CONTRACT_VERSION,
        "accepted_for": CONTEXT_ENRICHMENT_DRY_RUN_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "context_rows_path": str(context_rows_path) if context_rows_path else None,
        "mapping_rows_path": str(mapping_rows_path) if mapping_rows_path else None,
        "candidate_context_row_count": len(context_rows),
        "candidate_context_complete_count": candidate_context_complete,
        "candidate_context_attached_count": candidate_context_attached,
        "mapping_row_count": len(mapping_rows),
        "result_context_row_count": len(result_context_rows),
        "result_context_complete_count": result_context_complete,
        "dry_run_status": status,
        "important_limitation": (
            "D28 builds a result-context catalog only. It does not attach context "
            "to candidate rows and does not permit labels."
        ),
        "safety": safety,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Result Context Catalog Rows",
        "contract_version": CONTEXT_ENRICHMENT_DRY_RUN_CONTRACT_VERSION,
        "accepted_for": CONTEXT_ENRICHMENT_DRY_RUN_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "dry_run_status": status,
        "result_context_row_count": len(result_context_rows),
        "rows": result_context_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, RESULT_CONTEXT_COLUMNS, result_context_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CONTEXT_ENRICHMENT_DRY_RUN_CONTRACT_VERSION,
        "accepted_for": CONTEXT_ENRICHMENT_DRY_RUN_ACCEPTED_FOR,
        "dry_run_status": status,
        "candidate_context_row_count": len(context_rows),
        "candidate_context_complete_count": candidate_context_complete,
        "candidate_context_attached_count": candidate_context_attached,
        "mapping_row_count": len(mapping_rows),
        "result_context_row_count": len(result_context_rows),
        "result_context_complete_count": result_context_complete,
        "result_context_catalog_built": bool(result_context_rows),
        "candidate_context_inference_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D28 dry-runs result-context catalog only. Candidate bridge keys are required next.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return ContextEnrichmentDryRunBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CONTEXT_ENRICHMENT_DRY_RUN_CONTRACT_VERSION,
        accepted_for=CONTEXT_ENRICHMENT_DRY_RUN_ACCEPTED_FOR,
        context_rows_path=str(context_rows_path) if context_rows_path else None,
        mapping_rows_path=str(mapping_rows_path) if mapping_rows_path else None,
        dry_run_report_path=report_path.as_posix(),
        result_context_rows_json_path=rows_json_path.as_posix(),
        result_context_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        candidate_context_row_count=len(context_rows),
        candidate_context_complete_count=candidate_context_complete,
        candidate_context_attached_count=candidate_context_attached,
        result_context_row_count=len(result_context_rows),
        result_context_complete_count=result_context_complete,
        mapping_row_count=len(mapping_rows),
        dry_run_status=status,
        result_context_catalog_built=bool(result_context_rows),
    )


__all__ = (
    "CONTEXT_ENRICHMENT_DRY_RUN_CONTRACT_VERSION",
    "CONTEXT_ENRICHMENT_DRY_RUN_ACCEPTED_FOR",
    "DRY_RUN_STATUS_RESULT_CONTEXT_CATALOG_READY",
    "DRY_RUN_STATUS_BLOCKED_NO_CONTEXT_ROWS",
    "DRY_RUN_STATUS_BLOCKED_NO_MAPPING_ROWS",
    "DRY_RUN_STATUS_BLOCKED_INCOMPLETE_MAPPING",
    "DRY_RUN_STATUS_BLOCKED_NO_RESULT_ROWS",
    "REQUIRED_CONTEXT_KEYS",
    "RESULT_CONTEXT_COLUMNS",
    "ResultContextCatalogRow",
    "ContextEnrichmentDryRunBuildResult",
    "build_result_context_catalog_rows",
    "write_context_enrichment_dry_run",
)
