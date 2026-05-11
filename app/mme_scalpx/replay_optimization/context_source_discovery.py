"""Lane D D26 candidate-context source discovery audit.

This module discovers whether required D25 context keys can be sourced from the
verified D19 replay result artifacts.

D26 is audit-only. It does not infer/fill context values, perform matching,
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

CONTEXT_SOURCE_DISCOVERY_CONTRACT_VERSION = "replay_optimization_d26_context_source_discovery_contract_v1"
CONTEXT_SOURCE_DISCOVERY_ACCEPTED_FOR = "CANDIDATE_CONTEXT_SOURCE_DISCOVERY_AUDIT_ONLY"

DISCOVERY_STATUS_BLOCKED_NO_CONTEXT_ROWS = "BLOCKED_NO_D25_CONTEXT_ROWS"
DISCOVERY_STATUS_BLOCKED_NO_D19_VERIFIED_REFS = "BLOCKED_NO_D19_VERIFIED_RESULT_REFS"
DISCOVERY_STATUS_BLOCKED_NO_RESULT_SOURCE_KEYS = "BLOCKED_NO_RESULT_SOURCE_KEYS_FOR_REQUIRED_CONTEXT"
DISCOVERY_STATUS_SOURCES_FOUND_SCHEMA_ONLY = "CONTEXT_SOURCE_KEYS_FOUND_SCHEMA_ONLY_NOT_LABEL_READY"

REQUIRED_CONTEXT_KEYS = (
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
)

RESULT_ARTIFACT_FIELDS = (
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)

ARTIFACT_LABELS = {
    "features_ref": "features",
    "strategy_ref": "strategy",
    "risk_ref": "risk",
    "execution_shadow_ref": "execution_shadow",
}

SOURCE_CANDIDATE_KEYS = {
    "context_symbol": (
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
        "frame_id",
        "frame_ts_ns",
        "bar_id",
        "tick_id",
        "snapshot_id",
        "source_frame_id",
    ),
    "context_decision_id": (
        "decision_id",
        "strategy_decision_id",
        "source_decision_id",
        "signal_id",
        "candidate_id",
    ),
    "context_risk_id": (
        "risk_id",
        "source_risk_id",
        "risk_output_id",
        "execution_shadow_id",
        "order_shadow_id",
    ),
}

CONTEXT_SOURCE_COLUMNS = (
    "optimization_id",
    "source_row_id",
    "context_key",
    "artifact_field",
    "artifact_label",
    "artifact_ref",
    "artifact_row_count",
    "candidate_source_keys",
    "available_source_keys",
    "available_source_key_count",
    "all_rows_have_at_least_one_source_key",
    "source_discovery_status",
    "candidate_context_inference_allowed",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class ContextSourceDiscoveryRow:
    optimization_id: str
    source_row_id: str
    context_key: str
    artifact_field: str
    artifact_label: str
    artifact_ref: str | None
    artifact_row_count: int
    candidate_source_keys: str
    available_source_keys: str
    available_source_key_count: int
    all_rows_have_at_least_one_source_key: bool
    source_discovery_status: str
    candidate_context_inference_allowed: bool = False
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ContextSourceDiscoveryBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    context_rows_path: str | None
    nonzero_verification_report_path: str | None
    source_discovery_report_path: str
    source_discovery_rows_csv_path: str
    optimizer_verdict_path: str
    context_row_count: int
    complete_context_row_count: int
    missing_required_context_row_count: int
    source_discovery_row_count: int
    required_context_keys_with_sources_count: int
    discovery_status: str
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
        raise ValueError(f"D26 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _d19_audit(report: Any) -> dict[str, Any]:
    if isinstance(report, dict):
        audit = report.get("audit")
        if isinstance(audit, dict):
            return audit
    return {}


def _row_keys(rows: Sequence[Mapping[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in rows:
        keys.update(str(key) for key in row.keys())
    return keys


def _rows_have_any(rows: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> bool:
    if not rows or not keys:
        return False
    key_set = set(keys)
    for row in rows:
        if not any(key in row and row.get(key) is not None for key in key_set):
            return False
    return True


def build_context_source_discovery_rows(
    optimization_id: str,
    *,
    nonzero_verification_report_path: str | Path | None,
) -> tuple[ContextSourceDiscoveryRow, ...]:
    d19_report = _safe_load_json(nonzero_verification_report_path)
    audit = _d19_audit(d19_report)

    rows: list[ContextSourceDiscoveryRow] = []
    idx = 0

    for context_key in REQUIRED_CONTEXT_KEYS:
        candidate_keys = SOURCE_CANDIDATE_KEYS[context_key]
        for artifact_field in RESULT_ARTIFACT_FIELDS:
            idx += 1
            artifact_ref = audit.get(artifact_field)
            artifact_label = ARTIFACT_LABELS[artifact_field]
            artifact_rows = _rows_from_payload(_safe_load_json(artifact_ref))
            keys = _row_keys(artifact_rows)
            available = tuple(key for key in candidate_keys if key in keys)
            all_rows_have = _rows_have_any(artifact_rows, available)

            if available:
                status = DISCOVERY_STATUS_SOURCES_FOUND_SCHEMA_ONLY
                remarks = "Source key candidate exists in verified result artifact. D26 does not infer or fill context."
            else:
                status = DISCOVERY_STATUS_BLOCKED_NO_RESULT_SOURCE_KEYS
                remarks = "No candidate source key found in this artifact for this context key."

            rows.append(
                ContextSourceDiscoveryRow(
                    optimization_id=optimization_id,
                    source_row_id=f"SRC_{idx:04d}",
                    context_key=context_key,
                    artifact_field=artifact_field,
                    artifact_label=artifact_label,
                    artifact_ref=str(artifact_ref) if artifact_ref else None,
                    artifact_row_count=len(artifact_rows),
                    candidate_source_keys=",".join(candidate_keys),
                    available_source_keys=",".join(available),
                    available_source_key_count=len(available),
                    all_rows_have_at_least_one_source_key=all_rows_have,
                    source_discovery_status=status,
                    candidate_context_inference_allowed=False,
                    candidate_trade_matching_allowed=False,
                    candidate_trade_matching_performed=False,
                    label_binding_allowed=False,
                    labels_bound=False,
                    remarks=remarks,
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


def write_context_source_discovery_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    context_rows_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
) -> ContextSourceDiscoveryBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    context_payload = _safe_load_json(context_rows_path)
    context_rows = _rows_from_payload(context_payload)

    complete_context = sum(1 for row in context_rows if row.get("candidate_context_complete") is True)
    missing_context = sum(1 for row in context_rows if row.get("candidate_context_complete") is not True)

    source_rows = build_context_source_discovery_rows(
        optimization_id,
        nonzero_verification_report_path=nonzero_verification_report_path,
    )
    source_dicts = [asdict(row) for row in source_rows]

    keys_with_sources = {
        row.context_key
        for row in source_rows
        if row.available_source_key_count > 0
    }

    d19_report = _safe_load_json(nonzero_verification_report_path)
    d19_audit = _d19_audit(d19_report)
    has_any_verified_ref = any(d19_audit.get(field) for field in RESULT_ARTIFACT_FIELDS)

    if not context_rows:
        status = DISCOVERY_STATUS_BLOCKED_NO_CONTEXT_ROWS
    elif not has_any_verified_ref:
        status = DISCOVERY_STATUS_BLOCKED_NO_D19_VERIFIED_REFS
    elif not keys_with_sources:
        status = DISCOVERY_STATUS_BLOCKED_NO_RESULT_SOURCE_KEYS
    else:
        status = DISCOVERY_STATUS_SOURCES_FOUND_SCHEMA_ONLY

    report_path = out / "29_candidate_context_source_discovery.json"
    rows_csv_path = out / "29_candidate_context_source_discovery_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    report_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Context Source Discovery Audit",
        "contract_version": CONTEXT_SOURCE_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": CONTEXT_SOURCE_DISCOVERY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "context_rows_path": str(context_rows_path) if context_rows_path else None,
        "nonzero_verification_report_path": str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        "context_row_count": len(context_rows),
        "complete_context_row_count": complete_context,
        "missing_required_context_row_count": missing_context,
        "source_discovery_row_count": len(source_rows),
        "required_context_keys": list(REQUIRED_CONTEXT_KEYS),
        "required_context_keys_with_sources": sorted(keys_with_sources),
        "required_context_keys_with_sources_count": len(keys_with_sources),
        "discovery_status": status,
        "rows": source_dicts,
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
    report_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, CONTEXT_SOURCE_COLUMNS, source_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CONTEXT_SOURCE_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": CONTEXT_SOURCE_DISCOVERY_ACCEPTED_FOR,
        "discovery_status": status,
        "context_row_count": len(context_rows),
        "complete_context_row_count": complete_context,
        "missing_required_context_row_count": missing_context,
        "source_discovery_row_count": len(source_rows),
        "required_context_keys_with_sources_count": len(keys_with_sources),
        "candidate_context_inference_allowed": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D26 discovers possible context sources only. It does not infer/fill context or bind labels.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return ContextSourceDiscoveryBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CONTEXT_SOURCE_DISCOVERY_CONTRACT_VERSION,
        accepted_for=CONTEXT_SOURCE_DISCOVERY_ACCEPTED_FOR,
        context_rows_path=str(context_rows_path) if context_rows_path else None,
        nonzero_verification_report_path=str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        source_discovery_report_path=report_path.as_posix(),
        source_discovery_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        context_row_count=len(context_rows),
        complete_context_row_count=complete_context,
        missing_required_context_row_count=missing_context,
        source_discovery_row_count=len(source_rows),
        required_context_keys_with_sources_count=len(keys_with_sources),
        discovery_status=status,
    )


__all__ = (
    "CONTEXT_SOURCE_DISCOVERY_CONTRACT_VERSION",
    "CONTEXT_SOURCE_DISCOVERY_ACCEPTED_FOR",
    "DISCOVERY_STATUS_BLOCKED_NO_CONTEXT_ROWS",
    "DISCOVERY_STATUS_BLOCKED_NO_D19_VERIFIED_REFS",
    "DISCOVERY_STATUS_BLOCKED_NO_RESULT_SOURCE_KEYS",
    "DISCOVERY_STATUS_SOURCES_FOUND_SCHEMA_ONLY",
    "REQUIRED_CONTEXT_KEYS",
    "RESULT_ARTIFACT_FIELDS",
    "ARTIFACT_LABELS",
    "SOURCE_CANDIDATE_KEYS",
    "CONTEXT_SOURCE_COLUMNS",
    "ContextSourceDiscoveryRow",
    "ContextSourceDiscoveryBuildResult",
    "build_context_source_discovery_rows",
    "write_context_source_discovery_audit",
)
