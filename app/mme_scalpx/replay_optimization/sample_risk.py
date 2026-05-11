"""Lane D D9 sample-size and overfit-risk contract.

This module creates a risk gate for future optimization/ML work. It checks
whether result-binding rows contain enough verified labels to even consider
future model training.

D9 intentionally performs no model training, no prediction, no replay execution,
no PnL calculation, and no strategy ranking claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    OUTPUT_ROOT,
    VERDICT_NOT_READY_REPLAY_SOURCE_MISSING,
    VERDICT_REJECT_INSUFFICIENT_SAMPLE,
    VERDICT_REJECT_OVERFIT_RISK,
    OptimizerVerdictRow,
    row_to_dict,
)

SAMPLE_RISK_CONTRACT_VERSION = "replay_optimization_d9_sample_size_overfit_contract_v1"
SAMPLE_RISK_ACCEPTED_FOR = "SAMPLE_SIZE_OVERFIT_RISK_CONTRACT_ONLY"

SAMPLE_STATUS_INSUFFICIENT = "INSUFFICIENT_SAMPLE"
SAMPLE_STATUS_UNLABELED = "UNLABELED_SAMPLE"
SAMPLE_STATUS_RESEARCH_READY_FUTURE_ONLY = "RESEARCH_READY_FUTURE_ONLY"

OVERFIT_RISK_HIGH = "HIGH_NOT_READY"
OVERFIT_RISK_MEDIUM = "MEDIUM_REQUIRES_REVIEW"
OVERFIT_RISK_LOW_RESEARCH_ONLY = "LOW_RESEARCH_ONLY"

DEFAULT_MIN_SAMPLE_DAYS = 20
DEFAULT_MIN_LABELED_TRADES = 100
DEFAULT_MIN_STRATEGIES = 5
DEFAULT_MIN_SIDES = 2


@dataclass(frozen=True, slots=True)
class SampleSizeReport:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    result_binding_rows_path: str | None
    binding_row_count: int
    labeled_row_count: int
    source_verified_label_count: int
    sample_days: int
    sample_trades: int
    strategy_family_count: int
    side_count: int
    min_sample_days_required: int
    min_labeled_trades_required: int
    min_strategy_families_required: int
    min_sides_required: int
    sample_status: str
    readiness_verdict: str
    training_allowed: bool = False
    production_claim_allowed: bool = False
    paper_live_approved: bool = False


@dataclass(frozen=True, slots=True)
class OverfitRiskReport:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    overfit_risk_level: str
    reason: str
    labeled_row_count: int
    sample_days: int
    sample_trades: int
    parameter_candidate_count: int
    strategy_family_count: int
    side_count: int
    train_test_split_allowed: bool = False
    model_training_allowed: bool = False
    model_prediction_allowed: bool = False
    production_claim_allowed: bool = False
    paper_live_approved: bool = False


@dataclass(frozen=True, slots=True)
class SampleRiskBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    result_binding_rows_path: str | None
    sample_size_report_path: str
    overfit_risk_report_path: str
    optimizer_verdict_path: str
    readiness_verdict: str
    overfit_risk_level: str
    training_allowed: bool = False
    replay_execution_performed: bool = False
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


def _rows_from_payload(payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


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
        raise ValueError(f"D9 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _label_bound(row: Mapping[str, Any]) -> bool:
    return row.get("label_pnl") is not None or row.get("label_profitable") is not None


def _source_verified_label(row: Mapping[str, Any]) -> bool:
    return bool(row.get("source_verified")) and _label_bound(row)


def _strategy_count(rows: list[dict[str, Any]]) -> int:
    values = {
        str(row.get("feature_vector_ref", "")).split("|")[1]
        for row in rows
        if "|" in str(row.get("feature_vector_ref", ""))
    }
    return len({v for v in values if v})


def _side_count(rows: list[dict[str, Any]]) -> int:
    values = {
        str(row.get("feature_vector_ref", "")).split("|")[2]
        for row in rows
        if len(str(row.get("feature_vector_ref", "")).split("|")) >= 3
    }
    return len({v for v in values if v})


def _sample_days(rows: list[dict[str, Any]]) -> int:
    days = set()
    for row in rows:
        for key in ("session_date", "trade_date", "replay_date", "selected_date"):
            value = row.get(key)
            if isinstance(value, str) and value:
                days.add(value)
    return len(days)


def build_sample_size_report(
    optimization_id: str,
    *,
    result_binding_rows_path: str | Path | None,
    min_sample_days: int = DEFAULT_MIN_SAMPLE_DAYS,
    min_labeled_trades: int = DEFAULT_MIN_LABELED_TRADES,
    min_strategy_families: int = DEFAULT_MIN_STRATEGIES,
    min_sides: int = DEFAULT_MIN_SIDES,
) -> SampleSizeReport:
    payload = _safe_load_json(result_binding_rows_path)
    rows = _rows_from_payload(payload)

    binding_count = len(rows)
    labeled_count = sum(1 for row in rows if _label_bound(row))
    verified_labeled_count = sum(1 for row in rows if _source_verified_label(row))
    sample_days = _sample_days(rows)
    strategy_count = _strategy_count(rows)
    side_count = _side_count(rows)

    if binding_count <= 0:
        sample_status = SAMPLE_STATUS_INSUFFICIENT
        verdict = VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    elif labeled_count <= 0:
        sample_status = SAMPLE_STATUS_UNLABELED
        verdict = VERDICT_REJECT_INSUFFICIENT_SAMPLE
    elif (
        sample_days < min_sample_days
        or verified_labeled_count < min_labeled_trades
        or strategy_count < min_strategy_families
        or side_count < min_sides
    ):
        sample_status = SAMPLE_STATUS_INSUFFICIENT
        verdict = VERDICT_REJECT_INSUFFICIENT_SAMPLE
    else:
        sample_status = SAMPLE_STATUS_RESEARCH_READY_FUTURE_ONLY
        verdict = VERDICT_REJECT_OVERFIT_RISK

    return SampleSizeReport(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=SAMPLE_RISK_CONTRACT_VERSION,
        accepted_for=SAMPLE_RISK_ACCEPTED_FOR,
        result_binding_rows_path=str(result_binding_rows_path) if result_binding_rows_path else None,
        binding_row_count=binding_count,
        labeled_row_count=labeled_count,
        source_verified_label_count=verified_labeled_count,
        sample_days=sample_days,
        sample_trades=verified_labeled_count,
        strategy_family_count=strategy_count,
        side_count=side_count,
        min_sample_days_required=min_sample_days,
        min_labeled_trades_required=min_labeled_trades,
        min_strategy_families_required=min_strategy_families,
        min_sides_required=min_sides,
        sample_status=sample_status,
        readiness_verdict=verdict,
    )


def build_overfit_risk_report(
    optimization_id: str,
    sample_report: SampleSizeReport,
) -> OverfitRiskReport:
    if sample_report.labeled_row_count <= 0:
        level = OVERFIT_RISK_HIGH
        reason = "No verified replay-result labels are bound. Training would be invalid."
    elif sample_report.sample_status == SAMPLE_STATUS_INSUFFICIENT:
        level = OVERFIT_RISK_HIGH
        reason = "Sample is below minimum days/trades/coverage gates."
    elif sample_report.sample_status == SAMPLE_STATUS_RESEARCH_READY_FUTURE_ONLY:
        level = OVERFIT_RISK_MEDIUM
        reason = "Sample may be sufficient for future research review but still requires split and overfit reports."
    else:
        level = OVERFIT_RISK_HIGH
        reason = "Sample status is not approved for training."

    return OverfitRiskReport(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=SAMPLE_RISK_CONTRACT_VERSION,
        accepted_for=SAMPLE_RISK_ACCEPTED_FOR,
        overfit_risk_level=level,
        reason=reason,
        labeled_row_count=sample_report.labeled_row_count,
        sample_days=sample_report.sample_days,
        sample_trades=sample_report.sample_trades,
        parameter_candidate_count=sample_report.binding_row_count,
        strategy_family_count=sample_report.strategy_family_count,
        side_count=sample_report.side_count,
    )


def write_sample_risk_reports(
    optimization_id: str,
    output_dir: str | Path,
    *,
    result_binding_rows_path: str | Path | None,
) -> SampleRiskBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    sample_report = build_sample_size_report(
        optimization_id,
        result_binding_rows_path=result_binding_rows_path,
    )
    overfit_report = build_overfit_risk_report(optimization_id, sample_report)

    sample_path = out / "11_sample_size_report.json"
    overfit_path = out / "12_overfit_risk_report.json"
    verdict_path = out / "09_optimizer_verdict.json"

    sample_path.write_text(json.dumps(asdict(sample_report), indent=2, sort_keys=True), encoding="utf-8")
    overfit_path.write_text(json.dumps(asdict(overfit_report), indent=2, sort_keys=True), encoding="utf-8")

    verdict_row = OptimizerVerdictRow(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        verdict=sample_report.readiness_verdict,
        sample_days=sample_report.sample_days,
        sample_trades=sample_report.sample_trades,
        risk_notes=(
            f"D9 sample status={sample_report.sample_status}; "
            f"overfit risk={overfit_report.overfit_risk_level}; "
            "training remains forbidden."
        ),
        production_claim_allowed=False,
        paper_live_approved=False,
        remarks="D9 is a sample/overfit gate only. No training or prediction.",
    )
    verdict_path.write_text(json.dumps(row_to_dict(verdict_row), indent=2, sort_keys=True), encoding="utf-8")

    return SampleRiskBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=SAMPLE_RISK_CONTRACT_VERSION,
        accepted_for=SAMPLE_RISK_ACCEPTED_FOR,
        result_binding_rows_path=str(result_binding_rows_path) if result_binding_rows_path else None,
        sample_size_report_path=sample_path.as_posix(),
        overfit_risk_report_path=overfit_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        readiness_verdict=sample_report.readiness_verdict,
        overfit_risk_level=overfit_report.overfit_risk_level,
    )


def sample_risk_summary(*, result_binding_rows_path: str | Path | None) -> dict[str, Any]:
    sample_report = build_sample_size_report(
        "D9_SUMMARY",
        result_binding_rows_path=result_binding_rows_path,
    )
    overfit_report = build_overfit_risk_report("D9_SUMMARY", sample_report)
    return {
        "contract_version": SAMPLE_RISK_CONTRACT_VERSION,
        "accepted_for": SAMPLE_RISK_ACCEPTED_FOR,
        "binding_row_count": sample_report.binding_row_count,
        "labeled_row_count": sample_report.labeled_row_count,
        "sample_days": sample_report.sample_days,
        "sample_trades": sample_report.sample_trades,
        "sample_status": sample_report.sample_status,
        "overfit_risk_level": overfit_report.overfit_risk_level,
        "readiness_verdict": sample_report.readiness_verdict,
        "training_allowed": False,
        "replay_execution_performed": False,
        "model_training_performed": False,
        "model_prediction_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "SAMPLE_RISK_CONTRACT_VERSION",
    "SAMPLE_RISK_ACCEPTED_FOR",
    "SAMPLE_STATUS_INSUFFICIENT",
    "SAMPLE_STATUS_UNLABELED",
    "SAMPLE_STATUS_RESEARCH_READY_FUTURE_ONLY",
    "OVERFIT_RISK_HIGH",
    "OVERFIT_RISK_MEDIUM",
    "OVERFIT_RISK_LOW_RESEARCH_ONLY",
    "DEFAULT_MIN_SAMPLE_DAYS",
    "DEFAULT_MIN_LABELED_TRADES",
    "DEFAULT_MIN_STRATEGIES",
    "DEFAULT_MIN_SIDES",
    "SampleSizeReport",
    "OverfitRiskReport",
    "SampleRiskBuildResult",
    "build_sample_size_report",
    "build_overfit_risk_report",
    "write_sample_risk_reports",
    "sample_risk_summary",
)
