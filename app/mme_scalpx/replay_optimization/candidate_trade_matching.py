"""Lane D D20 candidate-to-trade matching schema contract.

This module freezes a research-only matching schema between D5 candidate rows
and the verified nonzero D19 replay result pack.

D20 is schema-only. It does not perform candidate-to-trade matching, bind
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

CANDIDATE_TRADE_MATCHING_CONTRACT_VERSION = "replay_optimization_d20_candidate_trade_matching_contract_v1"
CANDIDATE_TRADE_MATCHING_ACCEPTED_FOR = "CANDIDATE_TRADE_MATCHING_SCHEMA_CONTRACT_ONLY"

MATCH_STATUS_SCHEMA_ONLY_UNMATCHED = "SCHEMA_ONLY_UNMATCHED_NO_LABEL_BINDING"
MATCH_STATUS_BLOCKED_NO_CANDIDATE_MATRIX = "BLOCKED_NO_CANDIDATE_MATRIX"
MATCH_STATUS_BLOCKED_NO_VERIFIED_NONZERO_PACK = "BLOCKED_NO_VERIFIED_NONZERO_PACK"

MATCHING_COLUMNS = (
    "optimization_id",
    "match_id",
    "candidate_id",
    "strategy_family",
    "side",
    "regime",
    "parameter_group",
    "parameter_name",
    "baseline_value",
    "candidate_value",
    "verified_pack_id",
    "verified_candidate_root",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
    "features_row_count",
    "strategy_row_count",
    "risk_row_count",
    "execution_shadow_row_count",
    "matched_trade_ref",
    "matched_trade_index",
    "matched_decision_ref",
    "matched_execution_ref",
    "match_status",
    "label_binding_allowed",
    "labels_bound",
    "label_pnl",
    "label_profitable",
    "label_exit_reason",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateTradeMatchRow:
    optimization_id: str
    match_id: str
    candidate_id: str
    strategy_family: str
    side: str
    regime: str
    parameter_group: str
    parameter_name: str
    baseline_value: str | None
    candidate_value: str | None
    verified_pack_id: str | None
    verified_candidate_root: str | None
    features_ref: str | None
    strategy_ref: str | None
    risk_ref: str | None
    execution_shadow_ref: str | None
    features_row_count: int
    strategy_row_count: int
    risk_row_count: int
    execution_shadow_row_count: int
    matched_trade_ref: str | None = None
    matched_trade_index: int | None = None
    matched_decision_ref: str | None = None
    matched_execution_ref: str | None = None
    match_status: str = MATCH_STATUS_SCHEMA_ONLY_UNMATCHED
    label_binding_allowed: bool = False
    labels_bound: bool = False
    label_pnl: float | None = None
    label_profitable: bool | None = None
    label_exit_reason: str | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateTradeMatchingBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    candidate_matrix_path: str | None
    nonzero_verification_report_path: str | None
    matching_schema_path: str
    matching_rows_json_path: str
    matching_rows_csv_path: str
    optimizer_verdict_path: str
    match_row_count: int
    match_status: str
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
    if isinstance(payload, dict):
        rows = payload.get("rows")
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
        raise ValueError(f"D20 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _verified_pack_from_d19(report: Any) -> dict[str, Any] | None:
    if not isinstance(report, dict):
        return None
    if report.get("verification_status") != "NONZERO_RESULT_PACK_VERIFY_PASS_AUDIT_ONLY":
        return None
    audit = report.get("audit")
    return audit if isinstance(audit, dict) else None


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def build_candidate_trade_match_rows(
    optimization_id: str,
    *,
    candidate_matrix_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[CandidateTradeMatchRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    candidate_payload = _safe_load_json(candidate_matrix_path)
    candidate_rows = _rows_from_payload(candidate_payload)

    verification_payload = _safe_load_json(nonzero_verification_report_path)
    verified = _verified_pack_from_d19(verification_payload)

    if not candidate_rows:
        return tuple()
    if not verified:
        return tuple()

    rows: list[CandidateTradeMatchRow] = []
    for i, candidate in enumerate(candidate_rows[:max_rows], start=1):
        rows.append(
            CandidateTradeMatchRow(
                optimization_id=optimization_id,
                match_id=f"MATCH_{i:06d}",
                candidate_id=str(candidate.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                strategy_family=str(candidate.get("strategy_family") or "UNKNOWN"),
                side=str(candidate.get("side") or "UNKNOWN"),
                regime=str(candidate.get("regime") or "UNKNOWN"),
                parameter_group=str(candidate.get("parameter_group") or "UNKNOWN"),
                parameter_name=str(candidate.get("parameter_name") or "UNKNOWN"),
                baseline_value=_as_str(candidate.get("baseline_value")),
                candidate_value=_as_str(candidate.get("candidate_value")),
                verified_pack_id=_as_str(verified.get("selected_pack_id")),
                verified_candidate_root=_as_str(verified.get("selected_candidate_root")),
                features_ref=_as_str(verified.get("features_ref")),
                strategy_ref=_as_str(verified.get("strategy_ref")),
                risk_ref=_as_str(verified.get("risk_ref")),
                execution_shadow_ref=_as_str(verified.get("execution_shadow_ref")),
                features_row_count=int(verified.get("features_row_count") or 0),
                strategy_row_count=int(verified.get("strategy_row_count") or 0),
                risk_row_count=int(verified.get("risk_row_count") or 0),
                execution_shadow_row_count=int(verified.get("execution_shadow_row_count") or 0),
                matched_trade_ref=None,
                matched_trade_index=None,
                matched_decision_ref=None,
                matched_execution_ref=None,
                match_status=MATCH_STATUS_SCHEMA_ONLY_UNMATCHED,
                label_binding_allowed=False,
                labels_bound=False,
                label_pnl=None,
                label_profitable=None,
                label_exit_reason=None,
                remarks=(
                    "D20 schema-only row. Candidate-to-trade matching and label binding "
                    "are intentionally not performed."
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


def write_candidate_trade_matching_schema(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_matrix_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
    max_rows: int = 10000,
) -> CandidateTradeMatchingBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    candidate_payload = _safe_load_json(candidate_matrix_path)
    candidate_rows = _rows_from_payload(candidate_payload)
    verification_payload = _safe_load_json(nonzero_verification_report_path)
    verified = _verified_pack_from_d19(verification_payload)

    if not candidate_rows:
        status = MATCH_STATUS_BLOCKED_NO_CANDIDATE_MATRIX
    elif not verified:
        status = MATCH_STATUS_BLOCKED_NO_VERIFIED_NONZERO_PACK
    else:
        status = MATCH_STATUS_SCHEMA_ONLY_UNMATCHED

    rows = build_candidate_trade_match_rows(
        optimization_id,
        candidate_matrix_path=candidate_matrix_path,
        nonzero_verification_report_path=nonzero_verification_report_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in rows]

    schema_path = out / "23_candidate_trade_matching_schema.json"
    rows_json_path = out / "23_candidate_trade_matching_rows.json"
    rows_csv_path = out / "23_candidate_trade_matching_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    schema_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Trade Matching Schema",
        "contract_version": CANDIDATE_TRADE_MATCHING_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_TRADE_MATCHING_ACCEPTED_FOR,
        "columns": list(MATCHING_COLUMNS),
        "input_policy": {
            "candidate_matrix_required": True,
            "verified_nonzero_pack_required": True,
            "d20_matching_performed": False,
            "future_matching_required_before_label_binding": True
        },
        "label_policy": {
            "label_binding_allowed_in_d20": False,
            "labels_bound_in_d20": False,
            "label_pnl": "NULL_UNTIL_FUTURE_VERIFIED_MATCH_AND_BINDING",
            "label_profitable": "NULL_UNTIL_FUTURE_VERIFIED_MATCH_AND_BINDING",
            "label_exit_reason": "NULL_UNTIL_FUTURE_VERIFIED_MATCH_AND_BINDING"
        },
        "safety": {
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
        "schema_name": "MME-ScalpX Replay Optimization Candidate Trade Matching Rows",
        "contract_version": CANDIDATE_TRADE_MATCHING_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_TRADE_MATCHING_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
        "nonzero_verification_report_path": str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        "match_status": status,
        "match_row_count": len(rows),
        "rows": row_dicts,
        "safety": {
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
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, MATCHING_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_TRADE_MATCHING_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_TRADE_MATCHING_ACCEPTED_FOR,
        "match_status": status,
        "match_row_count": len(rows),
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D20 freezes candidate-to-trade matching schema only. No matching or labels.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateTradeMatchingBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_TRADE_MATCHING_CONTRACT_VERSION,
        accepted_for=CANDIDATE_TRADE_MATCHING_ACCEPTED_FOR,
        candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
        nonzero_verification_report_path=str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        matching_schema_path=schema_path.as_posix(),
        matching_rows_json_path=rows_json_path.as_posix(),
        matching_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        match_row_count=len(rows),
        match_status=status,
    )


__all__ = (
    "CANDIDATE_TRADE_MATCHING_CONTRACT_VERSION",
    "CANDIDATE_TRADE_MATCHING_ACCEPTED_FOR",
    "MATCH_STATUS_SCHEMA_ONLY_UNMATCHED",
    "MATCH_STATUS_BLOCKED_NO_CANDIDATE_MATRIX",
    "MATCH_STATUS_BLOCKED_NO_VERIFIED_NONZERO_PACK",
    "MATCHING_COLUMNS",
    "CandidateTradeMatchRow",
    "CandidateTradeMatchingBuildResult",
    "build_candidate_trade_match_rows",
    "write_candidate_trade_matching_schema",
)
