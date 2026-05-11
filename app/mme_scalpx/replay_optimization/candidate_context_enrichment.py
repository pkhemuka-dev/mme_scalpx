"""Lane D D25 candidate-context enrichment schema contract.

This module freezes the context fields required before any future
candidate-to-trade matching can be trusted.

D25 is schema-only. It does not infer missing context, perform matching, bind
labels, calculate PnL, train/predict models, execute replay, call brokers,
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

CANDIDATE_CONTEXT_ENRICHMENT_CONTRACT_VERSION = "replay_optimization_d25_candidate_context_enrichment_contract_v1"
CANDIDATE_CONTEXT_ENRICHMENT_ACCEPTED_FOR = "CANDIDATE_CONTEXT_ENRICHMENT_SCHEMA_CONTRACT_ONLY"

CONTEXT_STATUS_SCHEMA_ONLY_MISSING_REQUIRED_KEYS = "CONTEXT_SCHEMA_ONLY_MISSING_REQUIRED_KEYS_NOT_LABEL_READY"
CONTEXT_STATUS_BLOCKED_NO_MATCHING_ROWS = "BLOCKED_NO_D20_MATCHING_ROWS"
CONTEXT_STATUS_BLOCKED_NO_ADAPTER_ROWS = "BLOCKED_NO_D24_ADAPTER_ROWS"
CONTEXT_STATUS_READY_FOR_SOURCE_DISCOVERY = "READY_FOR_CONTEXT_SOURCE_DISCOVERY_AUDIT_ONLY"

REQUIRED_CONTEXT_KEYS = (
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
)

OPTIONAL_CONTEXT_KEYS = (
    "context_side",
    "context_strategy_family",
    "context_parameter_group",
    "context_parameter_name",
)

CONTEXT_ENRICHMENT_COLUMNS = (
    "optimization_id",
    "context_row_id",
    "candidate_id",
    "strategy_family",
    "side",
    "parameter_group",
    "parameter_name",
    "verified_pack_id",
    "verified_candidate_root",
    "context_side",
    "context_strategy_family",
    "context_parameter_group",
    "context_parameter_name",
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
    "candidate_context_complete",
    "missing_required_context_keys",
    "enrichment_status",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "label_pnl",
    "label_profitable",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateContextEnrichmentRow:
    optimization_id: str
    context_row_id: str
    candidate_id: str
    strategy_family: str
    side: str
    parameter_group: str
    parameter_name: str
    verified_pack_id: str | None
    verified_candidate_root: str | None
    context_side: str | None
    context_strategy_family: str | None
    context_parameter_group: str | None
    context_parameter_name: str | None
    context_symbol: str | None = None
    context_event_time: str | None = None
    context_frame_id: str | None = None
    context_decision_id: str | None = None
    context_risk_id: str | None = None
    candidate_context_complete: bool = False
    missing_required_context_keys: str = ""
    enrichment_status: str = CONTEXT_STATUS_SCHEMA_ONLY_MISSING_REQUIRED_KEYS
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    label_pnl: float | None = None
    label_profitable: bool | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateContextEnrichmentBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    matching_rows_path: str | None
    adapter_rows_path: str | None
    context_schema_path: str
    context_rows_json_path: str
    context_rows_csv_path: str
    optimizer_verdict_path: str
    context_row_count: int
    complete_context_row_count: int
    missing_required_context_row_count: int
    adapter_missing_required_candidate_key_count: int
    enrichment_status: str
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
        raise ValueError(f"D25 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _adapter_missing_required_count(adapter_rows: Sequence[Mapping[str, Any]]) -> int:
    count = 0
    for row in adapter_rows:
        if row.get("required_for_label_binding") is True and row.get("adapter_row_status") == "MISSING_CANDIDATE_KEY":
            count += 1
    return count


def _missing_context_keys(row: CandidateContextEnrichmentRow) -> tuple[str, ...]:
    missing: list[str] = []
    for key in REQUIRED_CONTEXT_KEYS:
        if getattr(row, key) is None:
            missing.append(key)
    return tuple(missing)


def build_candidate_context_rows(
    optimization_id: str,
    *,
    matching_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[CandidateContextEnrichmentRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    matching_payload = _safe_load_json(matching_rows_path)
    matching_rows = _rows_from_payload(matching_payload)

    out: list[CandidateContextEnrichmentRow] = []
    for i, row in enumerate(matching_rows[:max_rows], start=1):
        draft = CandidateContextEnrichmentRow(
            optimization_id=optimization_id,
            context_row_id=f"CTX_{i:06d}",
            candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{i:06d}"),
            strategy_family=str(row.get("strategy_family") or "UNKNOWN"),
            side=str(row.get("side") or "UNKNOWN"),
            parameter_group=str(row.get("parameter_group") or "UNKNOWN"),
            parameter_name=str(row.get("parameter_name") or "UNKNOWN"),
            verified_pack_id=_as_str(row.get("verified_pack_id")),
            verified_candidate_root=_as_str(row.get("verified_candidate_root")),
            context_side=_as_str(row.get("side")),
            context_strategy_family=_as_str(row.get("strategy_family")),
            context_parameter_group=_as_str(row.get("parameter_group")),
            context_parameter_name=_as_str(row.get("parameter_name")),
            context_symbol=None,
            context_event_time=None,
            context_frame_id=None,
            context_decision_id=None,
            context_risk_id=None,
            candidate_context_complete=False,
            missing_required_context_keys=",".join(REQUIRED_CONTEXT_KEYS),
            enrichment_status=CONTEXT_STATUS_SCHEMA_ONLY_MISSING_REQUIRED_KEYS,
            candidate_trade_matching_allowed=False,
            candidate_trade_matching_performed=False,
            label_binding_allowed=False,
            labels_bound=False,
            label_pnl=None,
            label_profitable=None,
            remarks=(
                "D25 schema-only row. Weak context is copied from candidate metadata, "
                "but required strong context keys remain missing."
            ),
        )
        out.append(draft)
    return tuple(out)


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_candidate_context_enrichment_schema(
    optimization_id: str,
    output_dir: str | Path,
    *,
    matching_rows_path: str | Path | None,
    adapter_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> CandidateContextEnrichmentBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    context_rows = build_candidate_context_rows(
        optimization_id,
        matching_rows_path=matching_rows_path,
        max_rows=max_rows,
    )
    adapter_payload = _safe_load_json(adapter_rows_path)
    adapter_rows = _rows_from_payload(adapter_payload)

    context_dicts = [asdict(row) for row in context_rows]
    complete_count = sum(1 for row in context_rows if row.candidate_context_complete)
    missing_count = sum(1 for row in context_rows if not row.candidate_context_complete)
    adapter_missing = _adapter_missing_required_count(adapter_rows)

    if not context_rows:
        status = CONTEXT_STATUS_BLOCKED_NO_MATCHING_ROWS
    elif not adapter_rows:
        status = CONTEXT_STATUS_BLOCKED_NO_ADAPTER_ROWS
    elif missing_count:
        status = CONTEXT_STATUS_SCHEMA_ONLY_MISSING_REQUIRED_KEYS
    else:
        status = CONTEXT_STATUS_READY_FOR_SOURCE_DISCOVERY

    schema_path = out / "28_candidate_context_enrichment_schema.json"
    rows_json_path = out / "28_candidate_context_enrichment_rows.json"
    rows_csv_path = out / "28_candidate_context_enrichment_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    schema_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Context Enrichment Schema",
        "contract_version": CANDIDATE_CONTEXT_ENRICHMENT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_CONTEXT_ENRICHMENT_ACCEPTED_FOR,
        "columns": list(CONTEXT_ENRICHMENT_COLUMNS),
        "required_context_keys": list(REQUIRED_CONTEXT_KEYS),
        "optional_context_keys": list(OPTIONAL_CONTEXT_KEYS),
        "context_policy": {
            "d25_is_schema_only": True,
            "context_side_is_weak": True,
            "strong_context_required_before_matching": True,
            "candidate_trade_matching_allowed_in_d25": False,
            "label_binding_allowed_in_d25": False,
            "future_context_source_discovery_required": True
        },
        "safety": {
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
        "schema_name": "MME-ScalpX Replay Optimization Candidate Context Enrichment Rows",
        "contract_version": CANDIDATE_CONTEXT_ENRICHMENT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_CONTEXT_ENRICHMENT_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "matching_rows_path": str(matching_rows_path) if matching_rows_path else None,
        "adapter_rows_path": str(adapter_rows_path) if adapter_rows_path else None,
        "enrichment_status": status,
        "context_row_count": len(context_rows),
        "complete_context_row_count": complete_count,
        "missing_required_context_row_count": missing_count,
        "adapter_missing_required_candidate_key_count": adapter_missing,
        "rows": context_dicts,
        "safety": schema_payload["safety"],
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, CONTEXT_ENRICHMENT_COLUMNS, context_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_CONTEXT_ENRICHMENT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_CONTEXT_ENRICHMENT_ACCEPTED_FOR,
        "enrichment_status": status,
        "context_row_count": len(context_rows),
        "complete_context_row_count": complete_count,
        "missing_required_context_row_count": missing_count,
        "adapter_missing_required_candidate_key_count": adapter_missing,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D25 freezes context-enrichment schema only. Strong context source discovery is required next.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateContextEnrichmentBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_CONTEXT_ENRICHMENT_CONTRACT_VERSION,
        accepted_for=CANDIDATE_CONTEXT_ENRICHMENT_ACCEPTED_FOR,
        matching_rows_path=str(matching_rows_path) if matching_rows_path else None,
        adapter_rows_path=str(adapter_rows_path) if adapter_rows_path else None,
        context_schema_path=schema_path.as_posix(),
        context_rows_json_path=rows_json_path.as_posix(),
        context_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        context_row_count=len(context_rows),
        complete_context_row_count=complete_count,
        missing_required_context_row_count=missing_count,
        adapter_missing_required_candidate_key_count=adapter_missing,
        enrichment_status=status,
    )


__all__ = (
    "CANDIDATE_CONTEXT_ENRICHMENT_CONTRACT_VERSION",
    "CANDIDATE_CONTEXT_ENRICHMENT_ACCEPTED_FOR",
    "CONTEXT_STATUS_SCHEMA_ONLY_MISSING_REQUIRED_KEYS",
    "CONTEXT_STATUS_BLOCKED_NO_MATCHING_ROWS",
    "CONTEXT_STATUS_BLOCKED_NO_ADAPTER_ROWS",
    "CONTEXT_STATUS_READY_FOR_SOURCE_DISCOVERY",
    "REQUIRED_CONTEXT_KEYS",
    "OPTIONAL_CONTEXT_KEYS",
    "CONTEXT_ENRICHMENT_COLUMNS",
    "CandidateContextEnrichmentRow",
    "CandidateContextEnrichmentBuildResult",
    "build_candidate_context_rows",
    "write_candidate_context_enrichment_schema",
)
