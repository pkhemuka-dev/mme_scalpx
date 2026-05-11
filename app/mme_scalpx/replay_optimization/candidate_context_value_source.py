"""Lane D D30 candidate-context value source audit.

This module audits whether required candidate-side context values can be sourced
from existing candidate/matching/context rows.

D30 is audit-only. It does not infer/fill candidate context, attach candidates
to result context, perform candidate-to-trade matching, bind labels, calculate
PnL, train/predict models, execute replay, call brokers, write live Redis,
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

CANDIDATE_CONTEXT_VALUE_SOURCE_CONTRACT_VERSION = "replay_optimization_d30_candidate_context_value_source_contract_v1"
CANDIDATE_CONTEXT_VALUE_SOURCE_ACCEPTED_FOR = "CANDIDATE_CONTEXT_VALUE_SOURCE_AUDIT_ONLY"

VALUE_SOURCE_STATUS_BLOCKED_NO_CANDIDATE_CONTEXT_ROWS = "BLOCKED_NO_CANDIDATE_CONTEXT_ROWS"
VALUE_SOURCE_STATUS_BLOCKED_NO_CANDIDATE_INPUT_ROWS = "BLOCKED_NO_CANDIDATE_INPUT_ROWS"
VALUE_SOURCE_STATUS_BLOCKED_REQUIRED_CANDIDATE_CONTEXT_VALUES_NOT_AVAILABLE = "BLOCKED_REQUIRED_CANDIDATE_CONTEXT_VALUES_NOT_AVAILABLE"
VALUE_SOURCE_STATUS_VALUE_SOURCES_FOUND_AUDIT_ONLY = "CANDIDATE_CONTEXT_VALUE_SOURCES_FOUND_AUDIT_ONLY_NOT_LABEL_READY"

SOURCE_ROW_STATUS_NO_SOURCE_KEYS = "NO_SOURCE_KEYS_IN_INPUT"
SOURCE_ROW_STATUS_SOURCE_KEYS_NULL = "SOURCE_KEYS_PRESENT_BUT_VALUES_NULL"
SOURCE_ROW_STATUS_SOURCE_VALUES_FOUND_AUDIT_ONLY = "SOURCE_VALUES_FOUND_AUDIT_ONLY"

REQUIRED_CONTEXT_KEYS = (
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
)

SOURCE_INPUTS = (
    "candidate_context_rows",
    "matching_rows",
    "candidate_matrix_rows",
)

CANDIDATE_SOURCE_KEYS = {
    "context_symbol": (
        "context_symbol",
        "symbol",
        "tradingsymbol",
        "instrument",
        "instrument_key",
        "instrument_token",
        "selected_symbol",
        "selected_instrument",
        "option_symbol",
        "underlying_symbol",
    ),
    "context_event_time": (
        "context_event_time",
        "event_time",
        "event_ts",
        "event_ts_ns",
        "timestamp",
        "timestamp_ns",
        "ts",
        "ts_ns",
        "frame_ts_ns",
        "decision_ts_ns",
        "created_at",
    ),
    "context_frame_id": (
        "context_frame_id",
        "frame_id",
        "source_frame_id",
        "feature_frame_id",
        "bar_id",
        "tick_id",
        "snapshot_id",
        "frame_ts_ns",
    ),
    "context_decision_id": (
        "context_decision_id",
        "decision_id",
        "strategy_decision_id",
        "source_decision_id",
        "signal_id",
    ),
    "context_risk_id": (
        "context_risk_id",
        "risk_id",
        "source_risk_id",
        "risk_output_id",
        "execution_shadow_id",
        "order_shadow_id",
    ),
}

VALUE_SOURCE_COLUMNS = (
    "optimization_id",
    "source_row_id",
    "context_key",
    "source_input_name",
    "input_row_count",
    "candidate_source_keys",
    "available_source_keys",
    "available_source_key_count",
    "non_null_value_count",
    "unique_value_count",
    "sample_value",
    "source_row_status",
    "candidate_context_inference_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateContextValueSourceRow:
    optimization_id: str
    source_row_id: str
    context_key: str
    source_input_name: str
    input_row_count: int
    candidate_source_keys: str
    available_source_keys: str
    available_source_key_count: int
    non_null_value_count: int
    unique_value_count: int
    sample_value: str | None
    source_row_status: str
    candidate_context_inference_allowed: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateContextValueSourceBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    candidate_context_rows_path: str | None
    matching_rows_path: str | None
    candidate_matrix_path: str | None
    value_source_report_path: str
    value_source_rows_json_path: str
    value_source_rows_csv_path: str
    optimizer_verdict_path: str
    candidate_context_row_count: int
    matching_row_count: int
    candidate_matrix_row_count: int
    value_source_row_count: int
    required_context_keys_with_value_sources_count: int
    required_context_keys_missing_value_sources_count: int
    value_source_status: str
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
        raise ValueError(f"D30 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _keys_from_rows(rows: Sequence[Mapping[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in rows:
        keys.update(str(key) for key in row.keys())
    return keys


def _non_null_values(rows: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> tuple[str, ...]:
    values: list[str] = []
    for row in rows:
        for key in keys:
            value = row.get(key)
            if value is None:
                continue
            value_text = str(value).strip()
            if value_text:
                values.append(value_text)
    return tuple(values)


def _sample(values: Sequence[str]) -> str | None:
    return values[0] if values else None


def build_candidate_context_value_source_rows(
    optimization_id: str,
    *,
    candidate_context_rows_path: str | Path | None,
    matching_rows_path: str | Path | None,
    candidate_matrix_path: str | Path | None,
) -> tuple[CandidateContextValueSourceRow, ...]:
    input_rows = {
        "candidate_context_rows": _rows_from_payload(_safe_load_json(candidate_context_rows_path)),
        "matching_rows": _rows_from_payload(_safe_load_json(matching_rows_path)),
        "candidate_matrix_rows": _rows_from_payload(_safe_load_json(candidate_matrix_path)),
    }

    out: list[CandidateContextValueSourceRow] = []
    idx = 0

    for context_key in REQUIRED_CONTEXT_KEYS:
        candidate_keys = CANDIDATE_SOURCE_KEYS[context_key]
        for source_input_name in SOURCE_INPUTS:
            idx += 1
            rows = input_rows[source_input_name]
            input_keys = _keys_from_rows(rows)
            available_keys = tuple(key for key in candidate_keys if key in input_keys)
            values = _non_null_values(rows, available_keys)
            unique_values = sorted(set(values))

            if not available_keys:
                status = SOURCE_ROW_STATUS_NO_SOURCE_KEYS
                remarks = "Input rows do not contain any candidate-side source key for this context key."
            elif not values:
                status = SOURCE_ROW_STATUS_SOURCE_KEYS_NULL
                remarks = "Input rows contain candidate-side source key(s), but all values are null or empty."
            else:
                status = SOURCE_ROW_STATUS_SOURCE_VALUES_FOUND_AUDIT_ONLY
                remarks = "Candidate-side source values found. D30 does not infer/fill context or bind labels."

            out.append(
                CandidateContextValueSourceRow(
                    optimization_id=optimization_id,
                    source_row_id=f"CVSRC_{idx:04d}",
                    context_key=context_key,
                    source_input_name=source_input_name,
                    input_row_count=len(rows),
                    candidate_source_keys=",".join(candidate_keys),
                    available_source_keys=",".join(available_keys),
                    available_source_key_count=len(available_keys),
                    non_null_value_count=len(values),
                    unique_value_count=len(unique_values),
                    sample_value=_sample(unique_values),
                    source_row_status=status,
                    candidate_context_inference_allowed=False,
                    candidate_context_attached=False,
                    candidate_trade_matching_allowed=False,
                    candidate_trade_matching_performed=False,
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


def write_candidate_context_value_source_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_context_rows_path: str | Path | None,
    matching_rows_path: str | Path | None,
    candidate_matrix_path: str | Path | None,
) -> CandidateContextValueSourceBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    candidate_context_rows = _rows_from_payload(_safe_load_json(candidate_context_rows_path))
    matching_rows = _rows_from_payload(_safe_load_json(matching_rows_path))
    candidate_matrix_rows = _rows_from_payload(_safe_load_json(candidate_matrix_path))

    source_rows = build_candidate_context_value_source_rows(
        optimization_id,
        candidate_context_rows_path=candidate_context_rows_path,
        matching_rows_path=matching_rows_path,
        candidate_matrix_path=candidate_matrix_path,
    )
    source_dicts = [asdict(row) for row in source_rows]

    keys_with_values = {
        row.context_key
        for row in source_rows
        if row.non_null_value_count > 0
    }
    missing_keys = tuple(key for key in REQUIRED_CONTEXT_KEYS if key not in keys_with_values)

    if not candidate_context_rows:
        status = VALUE_SOURCE_STATUS_BLOCKED_NO_CANDIDATE_CONTEXT_ROWS
    elif not matching_rows and not candidate_matrix_rows:
        status = VALUE_SOURCE_STATUS_BLOCKED_NO_CANDIDATE_INPUT_ROWS
    elif missing_keys:
        status = VALUE_SOURCE_STATUS_BLOCKED_REQUIRED_CANDIDATE_CONTEXT_VALUES_NOT_AVAILABLE
    else:
        status = VALUE_SOURCE_STATUS_VALUE_SOURCES_FOUND_AUDIT_ONLY

    report_path = out / "33_candidate_context_value_source_audit.json"
    rows_json_path = out / "33_candidate_context_value_source_rows.json"
    rows_csv_path = out / "33_candidate_context_value_source_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
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
        "schema_name": "MME-ScalpX Replay Optimization Candidate Context Value Source Audit",
        "contract_version": CANDIDATE_CONTEXT_VALUE_SOURCE_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_CONTEXT_VALUE_SOURCE_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "candidate_context_rows_path": str(candidate_context_rows_path) if candidate_context_rows_path else None,
        "matching_rows_path": str(matching_rows_path) if matching_rows_path else None,
        "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
        "candidate_context_row_count": len(candidate_context_rows),
        "matching_row_count": len(matching_rows),
        "candidate_matrix_row_count": len(candidate_matrix_rows),
        "required_context_keys": list(REQUIRED_CONTEXT_KEYS),
        "required_context_keys_with_value_sources": sorted(keys_with_values),
        "required_context_keys_missing_value_sources": list(missing_keys),
        "required_context_keys_with_value_sources_count": len(keys_with_values),
        "required_context_keys_missing_value_sources_count": len(missing_keys),
        "value_source_row_count": len(source_rows),
        "value_source_status": status,
        "important_limitation": (
            "D30 audits existing candidate-side value sources only. It does not "
            "infer/fill candidate context, attach candidate rows, match trades, or bind labels."
        ),
        "rows": source_dicts,
        "safety": safety,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Context Value Source Rows",
        "contract_version": CANDIDATE_CONTEXT_VALUE_SOURCE_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_CONTEXT_VALUE_SOURCE_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "value_source_status": status,
        "value_source_row_count": len(source_rows),
        "rows": source_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, VALUE_SOURCE_COLUMNS, source_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_CONTEXT_VALUE_SOURCE_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_CONTEXT_VALUE_SOURCE_ACCEPTED_FOR,
        "value_source_status": status,
        "candidate_context_row_count": len(candidate_context_rows),
        "matching_row_count": len(matching_rows),
        "candidate_matrix_row_count": len(candidate_matrix_rows),
        "value_source_row_count": len(source_rows),
        "required_context_keys_with_value_sources_count": len(keys_with_values),
        "required_context_keys_missing_value_sources_count": len(missing_keys),
        "candidate_context_inference_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D30 value-source audit only. Existing candidate inputs must provide bridge values before attachment/matching.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateContextValueSourceBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_CONTEXT_VALUE_SOURCE_CONTRACT_VERSION,
        accepted_for=CANDIDATE_CONTEXT_VALUE_SOURCE_ACCEPTED_FOR,
        candidate_context_rows_path=str(candidate_context_rows_path) if candidate_context_rows_path else None,
        matching_rows_path=str(matching_rows_path) if matching_rows_path else None,
        candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
        value_source_report_path=report_path.as_posix(),
        value_source_rows_json_path=rows_json_path.as_posix(),
        value_source_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        candidate_context_row_count=len(candidate_context_rows),
        matching_row_count=len(matching_rows),
        candidate_matrix_row_count=len(candidate_matrix_rows),
        value_source_row_count=len(source_rows),
        required_context_keys_with_value_sources_count=len(keys_with_values),
        required_context_keys_missing_value_sources_count=len(missing_keys),
        value_source_status=status,
    )


__all__ = (
    "CANDIDATE_CONTEXT_VALUE_SOURCE_CONTRACT_VERSION",
    "CANDIDATE_CONTEXT_VALUE_SOURCE_ACCEPTED_FOR",
    "VALUE_SOURCE_STATUS_BLOCKED_NO_CANDIDATE_CONTEXT_ROWS",
    "VALUE_SOURCE_STATUS_BLOCKED_NO_CANDIDATE_INPUT_ROWS",
    "VALUE_SOURCE_STATUS_BLOCKED_REQUIRED_CANDIDATE_CONTEXT_VALUES_NOT_AVAILABLE",
    "VALUE_SOURCE_STATUS_VALUE_SOURCES_FOUND_AUDIT_ONLY",
    "SOURCE_ROW_STATUS_NO_SOURCE_KEYS",
    "SOURCE_ROW_STATUS_SOURCE_KEYS_NULL",
    "SOURCE_ROW_STATUS_SOURCE_VALUES_FOUND_AUDIT_ONLY",
    "REQUIRED_CONTEXT_KEYS",
    "SOURCE_INPUTS",
    "CANDIDATE_SOURCE_KEYS",
    "VALUE_SOURCE_COLUMNS",
    "CandidateContextValueSourceRow",
    "CandidateContextValueSourceBuildResult",
    "build_candidate_context_value_source_rows",
    "write_candidate_context_value_source_audit",
)
