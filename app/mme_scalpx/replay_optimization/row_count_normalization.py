"""Lane D D17 row-count normalization audit.

This module classifies D16 row-count blockers without binding labels.

It distinguishes:
- all core replay row files are zero rows;
- row counts are equal and positive;
- row counts are unequal;
- integrity is fail/unknown.

It does not execute replay, assemble packs, match candidates to trades, bind
labels, calculate PnL, train/predict models, call brokers, write live Redis,
mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import OUTPUT_ROOT

ROW_COUNT_NORMALIZATION_CONTRACT_VERSION = "replay_optimization_d17_row_count_normalization_contract_v1"
ROW_COUNT_NORMALIZATION_ACCEPTED_FOR = "ROW_COUNT_NORMALIZATION_AUDIT_ONLY"

ROW_STATUS_ALL_ZERO_NO_LABEL_SOURCE = "BLOCKED_ALL_ZERO_ROWS_NO_LABEL_SOURCE"
ROW_STATUS_EQUAL_POSITIVE_AUDIT_ONLY = "ROW_COUNTS_EQUAL_POSITIVE_AUDIT_ONLY"
ROW_STATUS_UNEQUAL_COUNTS = "BLOCKED_UNEQUAL_ROW_COUNTS"
ROW_STATUS_MISSING_SELECTED_PACK = "BLOCKED_MISSING_SELECTED_PACK"
ROW_STATUS_INTEGRITY_FAIL = "BLOCKED_INTEGRITY_FAIL_OR_UNKNOWN"

CORE_COUNT_FIELDS = (
    "features_row_count",
    "strategy_row_count",
    "risk_row_count",
    "execution_shadow_row_count",
)


@dataclass(frozen=True, slots=True)
class RowCountNormalizationAudit:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    verification_report_path: str | None
    selected_pack_id: str | None
    selected_candidate_root: str | None
    integrity_verdict: str | None
    features_row_count: int
    strategy_row_count: int
    risk_row_count: int
    execution_shadow_row_count: int
    min_row_count: int
    max_row_count: int
    all_zero_rows: bool
    equal_positive_rows: bool
    unequal_rows: bool
    normalized_row_status: str
    label_binding_allowed: bool = False
    labels_bound: bool = False
    candidate_trade_matching_allowed: bool = False
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
class RowCountNormalizationBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    row_count_audit_path: str
    optimizer_verdict_path: str
    normalized_row_status: str
    selected_pack_id: str | None
    selected_candidate_root: str | None
    label_binding_allowed: bool = False
    labels_bound: bool = False
    candidate_trade_matching_allowed: bool = False
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
        raise ValueError(f"D17 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def build_row_count_audit(
    optimization_id: str,
    *,
    verification_report_path: str | Path | None,
) -> RowCountNormalizationAudit:
    report = _safe_load_json(verification_report_path)
    selected_pack = report.get("selected_pack") if report else None

    if not isinstance(selected_pack, dict):
        return RowCountNormalizationAudit(
            optimization_id=optimization_id,
            created_at=_utc_now(),
            contract_version=ROW_COUNT_NORMALIZATION_CONTRACT_VERSION,
            accepted_for=ROW_COUNT_NORMALIZATION_ACCEPTED_FOR,
            verification_report_path=str(verification_report_path) if verification_report_path else None,
            selected_pack_id=None,
            selected_candidate_root=None,
            integrity_verdict=None,
            features_row_count=0,
            strategy_row_count=0,
            risk_row_count=0,
            execution_shadow_row_count=0,
            min_row_count=0,
            max_row_count=0,
            all_zero_rows=False,
            equal_positive_rows=False,
            unequal_rows=False,
            normalized_row_status=ROW_STATUS_MISSING_SELECTED_PACK,
            remarks="D17 could not find selected_pack in D16 verification report.",
        )

    counts = {
        key: _as_int(selected_pack.get(key))
        for key in CORE_COUNT_FIELDS
    }
    values = list(counts.values())
    min_count = min(values) if values else 0
    max_count = max(values) if values else 0
    all_zero = all(value == 0 for value in values)
    equal_positive = bool(values) and len(set(values)) == 1 and values[0] > 0
    unequal = len(set(values)) > 1

    integrity = selected_pack.get("integrity_verdict")
    integrity_text = str(integrity).strip().lower() if integrity is not None else ""

    if all_zero:
        status = ROW_STATUS_ALL_ZERO_NO_LABEL_SOURCE
        remarks = "All replay row artifacts are zero-row. This cannot produce labels."
    elif unequal:
        status = ROW_STATUS_UNEQUAL_COUNTS
        remarks = "Replay row counts are genuinely unequal and need normalization before any matching."
    elif integrity_text not in {"pass", "ok", "safe", "true"}:
        status = ROW_STATUS_INTEGRITY_FAIL
        remarks = f"Row counts are not the main blocker; integrity is not pass-like: {integrity!r}."
    elif equal_positive:
        status = ROW_STATUS_EQUAL_POSITIVE_AUDIT_ONLY
        remarks = "Row counts are equal and positive, but D17 is audit-only; label binding remains blocked."
    else:
        status = ROW_STATUS_UNEQUAL_COUNTS
        remarks = "Row count state is unknown/unhandled and remains blocked."

    return RowCountNormalizationAudit(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=ROW_COUNT_NORMALIZATION_CONTRACT_VERSION,
        accepted_for=ROW_COUNT_NORMALIZATION_ACCEPTED_FOR,
        verification_report_path=str(verification_report_path) if verification_report_path else None,
        selected_pack_id=str(selected_pack.get("pack_id") or "") or None,
        selected_candidate_root=str(selected_pack.get("candidate_root") or "") or None,
        integrity_verdict=str(integrity) if integrity is not None else None,
        features_row_count=counts["features_row_count"],
        strategy_row_count=counts["strategy_row_count"],
        risk_row_count=counts["risk_row_count"],
        execution_shadow_row_count=counts["execution_shadow_row_count"],
        min_row_count=min_count,
        max_row_count=max_count,
        all_zero_rows=all_zero,
        equal_positive_rows=equal_positive,
        unequal_rows=unequal,
        normalized_row_status=status,
        remarks=remarks,
    )


def write_row_count_normalization_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    verification_report_path: str | Path | None,
) -> RowCountNormalizationBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit = build_row_count_audit(
        optimization_id,
        verification_report_path=verification_report_path,
    )

    audit_path = out / "20_row_count_normalization_audit.json"
    verdict_path = out / "09_optimizer_verdict.json"

    audit_path.write_text(json.dumps(asdict(audit), indent=2, sort_keys=True), encoding="utf-8")

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": ROW_COUNT_NORMALIZATION_CONTRACT_VERSION,
        "accepted_for": ROW_COUNT_NORMALIZATION_ACCEPTED_FOR,
        "normalized_row_status": audit.normalized_row_status,
        "selected_pack_id": audit.selected_pack_id,
        "selected_candidate_root": audit.selected_candidate_root,
        "label_binding_allowed": False,
        "labels_bound": False,
        "candidate_trade_matching_allowed": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": audit.remarks,
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return RowCountNormalizationBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=ROW_COUNT_NORMALIZATION_CONTRACT_VERSION,
        accepted_for=ROW_COUNT_NORMALIZATION_ACCEPTED_FOR,
        row_count_audit_path=audit_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        normalized_row_status=audit.normalized_row_status,
        selected_pack_id=audit.selected_pack_id,
        selected_candidate_root=audit.selected_candidate_root,
    )


__all__ = (
    "ROW_COUNT_NORMALIZATION_CONTRACT_VERSION",
    "ROW_COUNT_NORMALIZATION_ACCEPTED_FOR",
    "ROW_STATUS_ALL_ZERO_NO_LABEL_SOURCE",
    "ROW_STATUS_EQUAL_POSITIVE_AUDIT_ONLY",
    "ROW_STATUS_UNEQUAL_COUNTS",
    "ROW_STATUS_MISSING_SELECTED_PACK",
    "ROW_STATUS_INTEGRITY_FAIL",
    "CORE_COUNT_FIELDS",
    "RowCountNormalizationAudit",
    "RowCountNormalizationBuildResult",
    "build_row_count_audit",
    "write_row_count_normalization_audit",
)
