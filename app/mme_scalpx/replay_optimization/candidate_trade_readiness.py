"""Lane D D21 candidate-to-trade matching readiness audit.

This module audits D20 matching-schema rows and determines whether the system is
ready for future real candidate-to-trade matching.

D21 is audit-only. It does not perform matching, bind labels, calculate PnL,
train/predict models, execute replay, call brokers, write live Redis, mutate
doctrine, or approve paper/live.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .contracts import OUTPUT_ROOT

CANDIDATE_TRADE_READINESS_CONTRACT_VERSION = "replay_optimization_d21_candidate_trade_readiness_contract_v1"
CANDIDATE_TRADE_READINESS_ACCEPTED_FOR = "CANDIDATE_TRADE_MATCHING_READINESS_AUDIT_ONLY"

READINESS_STATUS_BLOCKED_NO_MATCHING_ROWS = "BLOCKED_NO_MATCHING_ROWS"
READINESS_STATUS_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED = "BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED"
READINESS_STATUS_BLOCKED_SCHEMA_ONLY_UNMATCHED_ROWS = "BLOCKED_SCHEMA_ONLY_UNMATCHED_ROWS"
READINESS_STATUS_BLOCKED_RESULT_SCOPE_TOO_SMALL = "BLOCKED_RESULT_SCOPE_TOO_SMALL_FOR_810_CANDIDATES"
READINESS_STATUS_READY_FOR_MATCH_KEY_DISCOVERY = "READY_FOR_MATCH_KEY_DISCOVERY_AUDIT_ONLY"

MATCH_REF_FIELDS = (
    "matched_trade_ref",
    "matched_trade_index",
    "matched_decision_ref",
    "matched_execution_ref",
)

LABEL_FIELDS = (
    "label_pnl",
    "label_profitable",
    "label_exit_reason",
)


@dataclass(frozen=True, slots=True)
class CandidateTradeReadinessAudit:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    matching_rows_path: str | None
    nonzero_verification_report_path: str | None
    matching_row_count: int
    unique_candidate_count: int
    unique_verified_pack_count: int
    verified_pack_ids: tuple[str, ...]
    verified_candidate_roots: tuple[str, ...]
    features_row_count: int
    strategy_row_count: int
    risk_row_count: int
    execution_shadow_row_count: int
    result_pack_min_row_count: int
    result_pack_max_row_count: int
    result_pack_equal_positive: bool
    unmatched_row_count: int
    matched_row_count: int
    labels_bound_row_count: int
    label_allowed_row_count: int
    null_label_row_count: int
    schema_only_row_count: int
    readiness_status: str
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
    production_claim_allowed: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateTradeReadinessBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    readiness_audit_path: str
    optimizer_verdict_path: str
    readiness_status: str
    matching_row_count: int
    unmatched_row_count: int
    labels_bound_row_count: int
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
        raise ValueError(f"D21 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _all_match_refs_empty(row: dict[str, Any]) -> bool:
    return all(row.get(field) is None for field in MATCH_REF_FIELDS)


def _any_match_ref_present(row: dict[str, Any]) -> bool:
    return any(row.get(field) is not None for field in MATCH_REF_FIELDS)


def _all_labels_null(row: dict[str, Any]) -> bool:
    return all(row.get(field) is None for field in LABEL_FIELDS)


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def build_candidate_trade_readiness_audit(
    optimization_id: str,
    *,
    matching_rows_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
) -> CandidateTradeReadinessAudit:
    rows_payload = _safe_load_json(matching_rows_path)
    rows = _rows_from_payload(rows_payload)

    nonzero_report = _safe_load_json(nonzero_verification_report_path)
    d19_audit = nonzero_report.get("audit") if isinstance(nonzero_report, dict) else None
    d19_audit = d19_audit if isinstance(d19_audit, dict) else {}

    matching_count = len(rows)
    candidate_ids = {str(row.get("candidate_id")) for row in rows if row.get("candidate_id")}
    pack_ids = {str(row.get("verified_pack_id")) for row in rows if row.get("verified_pack_id")}
    roots = {str(row.get("verified_candidate_root")) for row in rows if row.get("verified_candidate_root")}

    unmatched_count = sum(1 for row in rows if _all_match_refs_empty(row))
    matched_count = sum(1 for row in rows if _any_match_ref_present(row))
    labels_bound_count = sum(1 for row in rows if not _all_labels_null(row))
    label_allowed_count = sum(1 for row in rows if row.get("label_binding_allowed") is True)
    null_label_count = sum(1 for row in rows if _all_labels_null(row))
    schema_only_count = sum(1 for row in rows if row.get("match_status") == "SCHEMA_ONLY_UNMATCHED_NO_LABEL_BINDING")

    if rows:
        sample = rows[0]
        features_count = _as_int(sample.get("features_row_count"))
        strategy_count = _as_int(sample.get("strategy_row_count"))
        risk_count = _as_int(sample.get("risk_row_count"))
        execution_count = _as_int(sample.get("execution_shadow_row_count"))
    else:
        features_count = strategy_count = risk_count = execution_count = 0

    result_counts = [features_count, strategy_count, risk_count, execution_count]
    positive_counts = [value for value in result_counts if value > 0]
    min_result = min(result_counts) if result_counts else 0
    max_result = max(result_counts) if result_counts else 0
    equal_positive = bool(positive_counts) and len(set(result_counts)) == 1 and result_counts[0] > 0

    if not rows:
        status = READINESS_STATUS_BLOCKED_NO_MATCHING_ROWS
        remarks = "D20 matching rows are missing."
    elif labels_bound_count or label_allowed_count:
        status = READINESS_STATUS_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED
        remarks = "Labels or label permission appeared before matching approval."
    elif unmatched_count == matching_count and schema_only_count == matching_count:
        status = READINESS_STATUS_BLOCKED_SCHEMA_ONLY_UNMATCHED_ROWS
        remarks = "All rows are schema-only/unmatched. D22 must discover candidate/result join keys before matching."
    elif matching_count > max_result and matched_count == 0:
        status = READINESS_STATUS_BLOCKED_RESULT_SCOPE_TOO_SMALL
        remarks = "Candidate rows exceed verified result rows and no matching keys exist yet."
    else:
        status = READINESS_STATUS_READY_FOR_MATCH_KEY_DISCOVERY
        remarks = "Only match-key discovery may proceed. Matching and labels remain blocked."

    return CandidateTradeReadinessAudit(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_TRADE_READINESS_CONTRACT_VERSION,
        accepted_for=CANDIDATE_TRADE_READINESS_ACCEPTED_FOR,
        matching_rows_path=str(matching_rows_path) if matching_rows_path else None,
        nonzero_verification_report_path=str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        matching_row_count=matching_count,
        unique_candidate_count=len(candidate_ids),
        unique_verified_pack_count=len(pack_ids),
        verified_pack_ids=tuple(sorted(pack_ids)),
        verified_candidate_roots=tuple(sorted(roots)),
        features_row_count=features_count,
        strategy_row_count=strategy_count,
        risk_row_count=risk_count,
        execution_shadow_row_count=execution_count,
        result_pack_min_row_count=min_result,
        result_pack_max_row_count=max_result,
        result_pack_equal_positive=equal_positive,
        unmatched_row_count=unmatched_count,
        matched_row_count=matched_count,
        labels_bound_row_count=labels_bound_count,
        label_allowed_row_count=label_allowed_count,
        null_label_row_count=null_label_count,
        schema_only_row_count=schema_only_count,
        readiness_status=status,
        remarks=remarks,
    )


def write_candidate_trade_readiness_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    matching_rows_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
) -> CandidateTradeReadinessBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit = build_candidate_trade_readiness_audit(
        optimization_id,
        matching_rows_path=matching_rows_path,
        nonzero_verification_report_path=nonzero_verification_report_path,
    )

    audit_path = out / "24_candidate_trade_matching_readiness_audit.json"
    verdict_path = out / "09_optimizer_verdict.json"

    audit_path.write_text(json.dumps(asdict(audit), indent=2, sort_keys=True), encoding="utf-8")

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_TRADE_READINESS_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_TRADE_READINESS_ACCEPTED_FOR,
        "readiness_status": audit.readiness_status,
        "matching_row_count": audit.matching_row_count,
        "unmatched_row_count": audit.unmatched_row_count,
        "matched_row_count": audit.matched_row_count,
        "labels_bound_row_count": audit.labels_bound_row_count,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": audit.remarks,
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateTradeReadinessBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_TRADE_READINESS_CONTRACT_VERSION,
        accepted_for=CANDIDATE_TRADE_READINESS_ACCEPTED_FOR,
        readiness_audit_path=audit_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        readiness_status=audit.readiness_status,
        matching_row_count=audit.matching_row_count,
        unmatched_row_count=audit.unmatched_row_count,
        labels_bound_row_count=audit.labels_bound_row_count,
    )


__all__ = (
    "CANDIDATE_TRADE_READINESS_CONTRACT_VERSION",
    "CANDIDATE_TRADE_READINESS_ACCEPTED_FOR",
    "READINESS_STATUS_BLOCKED_NO_MATCHING_ROWS",
    "READINESS_STATUS_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED",
    "READINESS_STATUS_BLOCKED_SCHEMA_ONLY_UNMATCHED_ROWS",
    "READINESS_STATUS_BLOCKED_RESULT_SCOPE_TOO_SMALL",
    "READINESS_STATUS_READY_FOR_MATCH_KEY_DISCOVERY",
    "MATCH_REF_FIELDS",
    "LABEL_FIELDS",
    "CandidateTradeReadinessAudit",
    "CandidateTradeReadinessBuildResult",
    "build_candidate_trade_readiness_audit",
    "write_candidate_trade_readiness_audit",
)
