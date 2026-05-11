"""Lane D D29 candidate-result bridge key discovery audit.

This module inventories whether D25 candidate context rows can be bridged to
D28 result-context rows.

D29 is audit-only. It does not attach candidate context, perform candidate-to-
trade matching, bind labels, calculate PnL, train/predict models, execute
replay, call brokers, write live Redis, mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CANDIDATE_RESULT_BRIDGE_CONTRACT_VERSION = "replay_optimization_d29_candidate_result_bridge_contract_v1"
CANDIDATE_RESULT_BRIDGE_ACCEPTED_FOR = "CANDIDATE_RESULT_BRIDGE_KEY_DISCOVERY_AUDIT_ONLY"

BRIDGE_STATUS_BLOCKED_NO_CANDIDATE_CONTEXT_ROWS = "BLOCKED_NO_CANDIDATE_CONTEXT_ROWS"
BRIDGE_STATUS_BLOCKED_NO_RESULT_CONTEXT_ROWS = "BLOCKED_NO_RESULT_CONTEXT_ROWS"
BRIDGE_STATUS_BLOCKED_CANDIDATE_CONTEXT_VALUES_MISSING = "BLOCKED_CANDIDATE_CONTEXT_VALUES_MISSING"
BRIDGE_STATUS_BLOCKED_NO_VALUE_OVERLAP = "BLOCKED_NO_CANDIDATE_RESULT_VALUE_OVERLAP"
BRIDGE_STATUS_BRIDGE_KEYS_DISCOVERED_AUDIT_ONLY = "BRIDGE_KEYS_DISCOVERED_AUDIT_ONLY_NOT_LABEL_READY"

KEY_STATUS_MISSING_CANDIDATE_KEY = "MISSING_CANDIDATE_KEY"
KEY_STATUS_MISSING_RESULT_KEY = "MISSING_RESULT_KEY"
KEY_STATUS_CANDIDATE_VALUES_MISSING = "CANDIDATE_VALUES_MISSING"
KEY_STATUS_RESULT_VALUES_MISSING = "RESULT_VALUES_MISSING"
KEY_STATUS_NO_VALUE_OVERLAP = "NO_VALUE_OVERLAP"
KEY_STATUS_VALUE_OVERLAP_FOUND = "VALUE_OVERLAP_FOUND_AUDIT_ONLY"

REQUIRED_BRIDGE_KEYS = (
    "context_symbol",
    "context_event_time",
    "context_frame_id",
    "context_decision_id",
    "context_risk_id",
)

BRIDGE_KEY_COLUMNS = (
    "optimization_id",
    "bridge_key_id",
    "bridge_key",
    "candidate_key_exists",
    "result_key_exists",
    "candidate_non_null_count",
    "result_non_null_count",
    "candidate_unique_count",
    "result_unique_count",
    "overlap_count",
    "sample_candidate_value",
    "sample_result_value",
    "sample_overlap_value",
    "bridge_key_status",
    "candidate_context_attachment_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateResultBridgeKeyRow:
    optimization_id: str
    bridge_key_id: str
    bridge_key: str
    candidate_key_exists: bool
    result_key_exists: bool
    candidate_non_null_count: int
    result_non_null_count: int
    candidate_unique_count: int
    result_unique_count: int
    overlap_count: int
    sample_candidate_value: str | None
    sample_result_value: str | None
    sample_overlap_value: str | None
    bridge_key_status: str
    candidate_context_attachment_allowed: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateResultBridgeBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    candidate_context_rows_path: str | None
    result_context_rows_path: str | None
    bridge_report_path: str
    bridge_rows_json_path: str
    bridge_rows_csv_path: str
    optimizer_verdict_path: str
    candidate_context_row_count: int
    result_context_row_count: int
    bridge_key_row_count: int
    required_bridge_keys_with_candidate_values_count: int
    required_bridge_keys_with_result_values_count: int
    required_bridge_keys_with_overlap_count: int
    bridge_status: str
    candidate_context_attachment_allowed: bool = False
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
        raise ValueError(f"D29 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _non_null_values(rows: Sequence[Mapping[str, Any]], key: str) -> tuple[str, ...]:
    values: list[str] = []
    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        value_text = str(value).strip()
        if value_text:
            values.append(value_text)
    return tuple(values)


def _sample(values: Sequence[str]) -> str | None:
    return values[0] if values else None


def build_candidate_result_bridge_rows(
    optimization_id: str,
    *,
    candidate_context_rows_path: str | Path | None,
    result_context_rows_path: str | Path | None,
) -> tuple[CandidateResultBridgeKeyRow, ...]:
    candidate_rows = _rows_from_payload(_safe_load_json(candidate_context_rows_path))
    result_rows = _rows_from_payload(_safe_load_json(result_context_rows_path))

    candidate_keys = set()
    result_keys = set()
    for row in candidate_rows:
        candidate_keys.update(str(key) for key in row.keys())
    for row in result_rows:
        result_keys.update(str(key) for key in row.keys())

    out: list[CandidateResultBridgeKeyRow] = []

    for i, key in enumerate(REQUIRED_BRIDGE_KEYS, start=1):
        candidate_exists = key in candidate_keys
        result_exists = key in result_keys

        candidate_values = _non_null_values(candidate_rows, key)
        result_values = _non_null_values(result_rows, key)

        candidate_unique = set(candidate_values)
        result_unique = set(result_values)
        overlap = sorted(candidate_unique & result_unique)

        if not candidate_exists:
            status = KEY_STATUS_MISSING_CANDIDATE_KEY
            remarks = "Candidate context schema does not include this bridge key."
        elif not result_exists:
            status = KEY_STATUS_MISSING_RESULT_KEY
            remarks = "Result context catalog does not include this bridge key."
        elif not candidate_values:
            status = KEY_STATUS_CANDIDATE_VALUES_MISSING
            remarks = "Candidate rows have this key but all values are null/missing."
        elif not result_values:
            status = KEY_STATUS_RESULT_VALUES_MISSING
            remarks = "Result context rows have this key but values are null/missing."
        elif not overlap:
            status = KEY_STATUS_NO_VALUE_OVERLAP
            remarks = "Candidate and result context values do not overlap."
        else:
            status = KEY_STATUS_VALUE_OVERLAP_FOUND
            remarks = "Value overlap found. D29 still does not attach candidates or bind labels."

        out.append(
            CandidateResultBridgeKeyRow(
                optimization_id=optimization_id,
                bridge_key_id=f"BRIDGE_{i:04d}",
                bridge_key=key,
                candidate_key_exists=candidate_exists,
                result_key_exists=result_exists,
                candidate_non_null_count=len(candidate_values),
                result_non_null_count=len(result_values),
                candidate_unique_count=len(candidate_unique),
                result_unique_count=len(result_unique),
                overlap_count=len(overlap),
                sample_candidate_value=_sample(candidate_values),
                sample_result_value=_sample(result_values),
                sample_overlap_value=_sample(overlap),
                bridge_key_status=status,
                candidate_context_attachment_allowed=False,
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


def write_candidate_result_bridge_discovery(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_context_rows_path: str | Path | None,
    result_context_rows_path: str | Path | None,
) -> CandidateResultBridgeBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    candidate_rows = _rows_from_payload(_safe_load_json(candidate_context_rows_path))
    result_rows = _rows_from_payload(_safe_load_json(result_context_rows_path))

    bridge_rows = build_candidate_result_bridge_rows(
        optimization_id,
        candidate_context_rows_path=candidate_context_rows_path,
        result_context_rows_path=result_context_rows_path,
    )
    bridge_dicts = [asdict(row) for row in bridge_rows]

    candidate_value_keys = sum(1 for row in bridge_rows if row.candidate_non_null_count > 0)
    result_value_keys = sum(1 for row in bridge_rows if row.result_non_null_count > 0)
    overlap_keys = sum(1 for row in bridge_rows if row.overlap_count > 0)

    if not candidate_rows:
        status = BRIDGE_STATUS_BLOCKED_NO_CANDIDATE_CONTEXT_ROWS
    elif not result_rows:
        status = BRIDGE_STATUS_BLOCKED_NO_RESULT_CONTEXT_ROWS
    elif candidate_value_keys < len(REQUIRED_BRIDGE_KEYS):
        status = BRIDGE_STATUS_BLOCKED_CANDIDATE_CONTEXT_VALUES_MISSING
    elif overlap_keys <= 0:
        status = BRIDGE_STATUS_BLOCKED_NO_VALUE_OVERLAP
    else:
        status = BRIDGE_STATUS_BRIDGE_KEYS_DISCOVERED_AUDIT_ONLY

    report_path = out / "32_candidate_result_bridge_discovery_report.json"
    rows_json_path = out / "32_candidate_result_bridge_key_rows.json"
    rows_csv_path = out / "32_candidate_result_bridge_key_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
        "candidate_context_attachment_allowed": False,
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
        "schema_name": "MME-ScalpX Replay Optimization Candidate Result Bridge Key Discovery Audit",
        "contract_version": CANDIDATE_RESULT_BRIDGE_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_RESULT_BRIDGE_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "candidate_context_rows_path": str(candidate_context_rows_path) if candidate_context_rows_path else None,
        "result_context_rows_path": str(result_context_rows_path) if result_context_rows_path else None,
        "candidate_context_row_count": len(candidate_rows),
        "result_context_row_count": len(result_rows),
        "bridge_key_row_count": len(bridge_rows),
        "required_bridge_keys": list(REQUIRED_BRIDGE_KEYS),
        "required_bridge_keys_with_candidate_values_count": candidate_value_keys,
        "required_bridge_keys_with_result_values_count": result_value_keys,
        "required_bridge_keys_with_overlap_count": overlap_keys,
        "bridge_status": status,
        "important_limitation": (
            "D29 discovers bridge key availability only. It does not attach "
            "candidate rows to result-context rows and does not permit labels."
        ),
        "rows": bridge_dicts,
        "safety": safety,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Result Bridge Key Rows",
        "contract_version": CANDIDATE_RESULT_BRIDGE_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_RESULT_BRIDGE_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "bridge_status": status,
        "bridge_key_row_count": len(bridge_rows),
        "rows": bridge_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, BRIDGE_KEY_COLUMNS, bridge_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_RESULT_BRIDGE_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_RESULT_BRIDGE_ACCEPTED_FOR,
        "bridge_status": status,
        "candidate_context_row_count": len(candidate_rows),
        "result_context_row_count": len(result_rows),
        "bridge_key_row_count": len(bridge_rows),
        "required_bridge_keys_with_candidate_values_count": candidate_value_keys,
        "required_bridge_keys_with_result_values_count": result_value_keys,
        "required_bridge_keys_with_overlap_count": overlap_keys,
        "candidate_context_attachment_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D29 bridge discovery only. Candidate context values are required before attachment/matching.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateResultBridgeBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_RESULT_BRIDGE_CONTRACT_VERSION,
        accepted_for=CANDIDATE_RESULT_BRIDGE_ACCEPTED_FOR,
        candidate_context_rows_path=str(candidate_context_rows_path) if candidate_context_rows_path else None,
        result_context_rows_path=str(result_context_rows_path) if result_context_rows_path else None,
        bridge_report_path=report_path.as_posix(),
        bridge_rows_json_path=rows_json_path.as_posix(),
        bridge_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        candidate_context_row_count=len(candidate_rows),
        result_context_row_count=len(result_rows),
        bridge_key_row_count=len(bridge_rows),
        required_bridge_keys_with_candidate_values_count=candidate_value_keys,
        required_bridge_keys_with_result_values_count=result_value_keys,
        required_bridge_keys_with_overlap_count=overlap_keys,
        bridge_status=status,
    )


__all__ = (
    "CANDIDATE_RESULT_BRIDGE_CONTRACT_VERSION",
    "CANDIDATE_RESULT_BRIDGE_ACCEPTED_FOR",
    "BRIDGE_STATUS_BLOCKED_NO_CANDIDATE_CONTEXT_ROWS",
    "BRIDGE_STATUS_BLOCKED_NO_RESULT_CONTEXT_ROWS",
    "BRIDGE_STATUS_BLOCKED_CANDIDATE_CONTEXT_VALUES_MISSING",
    "BRIDGE_STATUS_BLOCKED_NO_VALUE_OVERLAP",
    "BRIDGE_STATUS_BRIDGE_KEYS_DISCOVERED_AUDIT_ONLY",
    "KEY_STATUS_MISSING_CANDIDATE_KEY",
    "KEY_STATUS_MISSING_RESULT_KEY",
    "KEY_STATUS_CANDIDATE_VALUES_MISSING",
    "KEY_STATUS_RESULT_VALUES_MISSING",
    "KEY_STATUS_NO_VALUE_OVERLAP",
    "KEY_STATUS_VALUE_OVERLAP_FOUND",
    "REQUIRED_BRIDGE_KEYS",
    "BRIDGE_KEY_COLUMNS",
    "CandidateResultBridgeKeyRow",
    "CandidateResultBridgeBuildResult",
    "build_candidate_result_bridge_rows",
    "write_candidate_result_bridge_discovery",
)
