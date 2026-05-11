"""Lane D D24 match-key adapter schema contract.

This module freezes a schema for adapting current candidate rows to replay
result rows. It proves whether direct/weak keys and future strong keys are
available.

D24 is schema-only. It does not perform candidate-to-trade matching, bind
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

MATCH_KEY_ADAPTER_CONTRACT_VERSION = "replay_optimization_d24_match_key_adapter_contract_v1"
MATCH_KEY_ADAPTER_ACCEPTED_FOR = "MATCH_KEY_ADAPTER_SCHEMA_CONTRACT_ONLY"

ADAPTER_STATUS_SIDE_ONLY_WEAK = "ADAPTER_SCHEMA_SIDE_ONLY_WEAK_NOT_LABEL_READY"
ADAPTER_STATUS_BLOCKED_NO_D22_AUDIT = "BLOCKED_NO_D22_MATCH_KEY_DISCOVERY_AUDIT"
ADAPTER_STATUS_BLOCKED_NO_ADAPTER_ROWS = "BLOCKED_NO_ADAPTER_ROWS"
ADAPTER_STATUS_READY_FOR_CONTEXT_ENRICHMENT = "READY_FOR_CANDIDATE_CONTEXT_ENRICHMENT_CONTRACT_ONLY"

ADAPTER_ROW_STATUS_AVAILABLE_WEAK = "AVAILABLE_WEAK"
ADAPTER_ROW_STATUS_MISSING_CANDIDATE_KEY = "MISSING_CANDIDATE_KEY"
ADAPTER_ROW_STATUS_MISSING_RESULT_KEY = "MISSING_RESULT_KEY"
ADAPTER_ROW_STATUS_AVAILABLE_STRONG_SCHEMA_ONLY = "AVAILABLE_STRONG_SCHEMA_ONLY"

ADAPTER_COLUMNS = (
    "optimization_id",
    "adapter_id",
    "candidate_key",
    "result_artifact",
    "result_key",
    "join_family",
    "match_strength",
    "required_for_label_binding",
    "available_in_current_candidate_rows",
    "available_in_current_result_rows",
    "adapter_row_status",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)

PLANNED_ADAPTER_SPECS = (
    ("side", "features", "side", "direction", "weak", False),
    ("side", "strategy", "side", "direction", "weak", False),
    ("side", "risk", "side", "direction", "weak", False),
    ("context_symbol", "features", "symbol", "instrument_identity", "strong", True),
    ("context_symbol", "strategy", "symbol", "instrument_identity", "strong", True),
    ("context_symbol", "risk", "symbol", "instrument_identity", "strong", True),
    ("context_symbol", "execution_shadow", "symbol", "instrument_identity", "strong", True),
    ("context_event_time", "features", "event_time", "time_alignment", "strong", True),
    ("context_event_time", "strategy", "event_time", "time_alignment", "strong", True),
    ("context_event_time", "risk", "event_time", "time_alignment", "strong", True),
    ("context_event_time", "execution_shadow", "event_time", "time_alignment", "strong", True),
    ("context_frame_id", "features", "frame_id", "frame_alignment", "strong", True),
    ("context_frame_id", "strategy", "frame_id", "frame_alignment", "strong", True),
    ("context_frame_id", "risk", "frame_id", "frame_alignment", "strong", True),
    ("context_decision_id", "strategy", "decision_id", "decision_alignment", "strong", True),
    ("context_decision_id", "risk", "source_decision_id", "decision_alignment", "strong", True),
    ("context_risk_id", "risk", "risk_id", "risk_alignment", "strong", True),
    ("context_risk_id", "execution_shadow", "source_risk_id", "risk_alignment", "strong", True),
)


@dataclass(frozen=True, slots=True)
class MatchKeyAdapterRow:
    optimization_id: str
    adapter_id: str
    candidate_key: str
    result_artifact: str
    result_key: str
    join_family: str
    match_strength: str
    required_for_label_binding: bool
    available_in_current_candidate_rows: bool
    available_in_current_result_rows: bool
    adapter_row_status: str
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class MatchKeyAdapterBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    match_key_discovery_path: str | None
    adapter_schema_path: str
    adapter_rows_json_path: str
    adapter_rows_csv_path: str
    optimizer_verdict_path: str
    adapter_row_count: int
    available_weak_count: int
    available_strong_count: int
    missing_required_candidate_key_count: int
    adapter_status: str
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
        raise ValueError(f"D24 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _audit_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        audit = payload.get("audit")
        if isinstance(audit, dict):
            return audit
        return payload
    return {}


def _tuple_from_list(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(str(item) for item in value if item is not None)
    return tuple()


def _artifact_keys(audit: Mapping[str, Any], artifact: str) -> tuple[str, ...]:
    if artifact == "features":
        return _tuple_from_list(audit.get("features_keys"))
    if artifact == "strategy":
        return _tuple_from_list(audit.get("strategy_keys"))
    if artifact == "risk":
        return _tuple_from_list(audit.get("risk_keys"))
    if artifact == "execution_shadow":
        return _tuple_from_list(audit.get("execution_shadow_keys"))
    return tuple()


def build_match_key_adapter_rows(
    optimization_id: str,
    *,
    match_key_discovery_path: str | Path | None,
) -> tuple[MatchKeyAdapterRow, ...]:
    payload = _safe_load_json(match_key_discovery_path)
    audit = _audit_payload(payload)

    candidate_keys = set(_tuple_from_list(audit.get("candidate_keys")))
    if not audit or not candidate_keys:
        return tuple()

    rows: list[MatchKeyAdapterRow] = []
    for i, spec in enumerate(PLANNED_ADAPTER_SPECS, start=1):
        candidate_key, artifact, result_key, join_family, strength, required = spec
        result_keys = set(_artifact_keys(audit, artifact))
        candidate_available = candidate_key in candidate_keys
        result_available = result_key in result_keys

        if candidate_available and result_available and strength == "weak":
            row_status = ADAPTER_ROW_STATUS_AVAILABLE_WEAK
            remarks = "Available today but weak; insufficient for label binding."
        elif candidate_available and result_available:
            row_status = ADAPTER_ROW_STATUS_AVAILABLE_STRONG_SCHEMA_ONLY
            remarks = "Strong key available, but D24 is schema-only."
        elif not candidate_available:
            row_status = ADAPTER_ROW_STATUS_MISSING_CANDIDATE_KEY
            remarks = "Required candidate context key is missing from current candidate rows."
        else:
            row_status = ADAPTER_ROW_STATUS_MISSING_RESULT_KEY
            remarks = "Result key is missing from verified replay result artifacts."

        rows.append(
            MatchKeyAdapterRow(
                optimization_id=optimization_id,
                adapter_id=f"ADAPT_{i:04d}",
                candidate_key=candidate_key,
                result_artifact=artifact,
                result_key=result_key,
                join_family=join_family,
                match_strength=strength,
                required_for_label_binding=required,
                available_in_current_candidate_rows=candidate_available,
                available_in_current_result_rows=result_available,
                adapter_row_status=row_status,
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


def write_match_key_adapter_schema(
    optimization_id: str,
    output_dir: str | Path,
    *,
    match_key_discovery_path: str | Path | None,
) -> MatchKeyAdapterBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_match_key_adapter_rows(
        optimization_id,
        match_key_discovery_path=match_key_discovery_path,
    )
    row_dicts = [asdict(row) for row in rows]

    available_weak = sum(1 for row in rows if row.adapter_row_status == ADAPTER_ROW_STATUS_AVAILABLE_WEAK)
    available_strong = sum(1 for row in rows if row.adapter_row_status == ADAPTER_ROW_STATUS_AVAILABLE_STRONG_SCHEMA_ONLY)
    missing_required_candidate = sum(
        1 for row in rows
        if row.required_for_label_binding and row.adapter_row_status == ADAPTER_ROW_STATUS_MISSING_CANDIDATE_KEY
    )

    if not rows:
        status = ADAPTER_STATUS_BLOCKED_NO_D22_AUDIT
    elif available_strong > 0 and missing_required_candidate == 0:
        status = ADAPTER_STATUS_READY_FOR_CONTEXT_ENRICHMENT
    elif available_weak > 0:
        status = ADAPTER_STATUS_SIDE_ONLY_WEAK
    else:
        status = ADAPTER_STATUS_BLOCKED_NO_ADAPTER_ROWS

    schema_path = out / "27_match_key_adapter_schema.json"
    rows_json_path = out / "27_match_key_adapter_rows.json"
    rows_csv_path = out / "27_match_key_adapter_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    schema_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Match Key Adapter Schema",
        "contract_version": MATCH_KEY_ADAPTER_CONTRACT_VERSION,
        "accepted_for": MATCH_KEY_ADAPTER_ACCEPTED_FOR,
        "columns": list(ADAPTER_COLUMNS),
        "adapter_policy": {
            "d24_is_schema_only": True,
            "side_only_is_weak": True,
            "required_future_candidate_context_keys": [
                "context_symbol",
                "context_event_time",
                "context_frame_id",
                "context_decision_id",
                "context_risk_id"
            ],
            "future_candidate_context_enrichment_required": True,
            "candidate_trade_matching_allowed_in_d24": False,
            "label_binding_allowed_in_d24": False
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
        "schema_name": "MME-ScalpX Replay Optimization Match Key Adapter Rows",
        "contract_version": MATCH_KEY_ADAPTER_CONTRACT_VERSION,
        "accepted_for": MATCH_KEY_ADAPTER_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "match_key_discovery_path": str(match_key_discovery_path) if match_key_discovery_path else None,
        "adapter_status": status,
        "adapter_row_count": len(rows),
        "available_weak_count": available_weak,
        "available_strong_count": available_strong,
        "missing_required_candidate_key_count": missing_required_candidate,
        "rows": row_dicts,
        "safety": schema_payload["safety"],
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, ADAPTER_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": MATCH_KEY_ADAPTER_CONTRACT_VERSION,
        "accepted_for": MATCH_KEY_ADAPTER_ACCEPTED_FOR,
        "adapter_status": status,
        "adapter_row_count": len(rows),
        "available_weak_count": available_weak,
        "available_strong_count": available_strong,
        "missing_required_candidate_key_count": missing_required_candidate,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D24 freezes adapter schema only. Strong candidate context enrichment is required before real matching.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return MatchKeyAdapterBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=MATCH_KEY_ADAPTER_CONTRACT_VERSION,
        accepted_for=MATCH_KEY_ADAPTER_ACCEPTED_FOR,
        match_key_discovery_path=str(match_key_discovery_path) if match_key_discovery_path else None,
        adapter_schema_path=schema_path.as_posix(),
        adapter_rows_json_path=rows_json_path.as_posix(),
        adapter_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        adapter_row_count=len(rows),
        available_weak_count=available_weak,
        available_strong_count=available_strong,
        missing_required_candidate_key_count=missing_required_candidate,
        adapter_status=status,
    )


__all__ = (
    "MATCH_KEY_ADAPTER_CONTRACT_VERSION",
    "MATCH_KEY_ADAPTER_ACCEPTED_FOR",
    "ADAPTER_STATUS_SIDE_ONLY_WEAK",
    "ADAPTER_STATUS_BLOCKED_NO_D22_AUDIT",
    "ADAPTER_STATUS_BLOCKED_NO_ADAPTER_ROWS",
    "ADAPTER_STATUS_READY_FOR_CONTEXT_ENRICHMENT",
    "ADAPTER_ROW_STATUS_AVAILABLE_WEAK",
    "ADAPTER_ROW_STATUS_MISSING_CANDIDATE_KEY",
    "ADAPTER_ROW_STATUS_MISSING_RESULT_KEY",
    "ADAPTER_ROW_STATUS_AVAILABLE_STRONG_SCHEMA_ONLY",
    "ADAPTER_COLUMNS",
    "PLANNED_ADAPTER_SPECS",
    "MatchKeyAdapterRow",
    "MatchKeyAdapterBuildResult",
    "build_match_key_adapter_rows",
    "write_match_key_adapter_schema",
)
