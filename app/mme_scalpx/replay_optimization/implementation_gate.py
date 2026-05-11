"""Lane D D10 result-binding implementation gate.

This module audits whether Lane D is ready to begin future result-binding
implementation. It does not bind labels, execute replay, calculate profit,
train models, or approve live/paper use.

The correct D10 outcome may be PASS while still blocking implementation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import OUTPUT_ROOT

IMPLEMENTATION_GATE_CONTRACT_VERSION = "replay_optimization_d10_result_binding_gate_contract_v1"
IMPLEMENTATION_GATE_ACCEPTED_FOR = "RESULT_BINDING_IMPLEMENTATION_GATE_AUDIT_ONLY"

GATE_BLOCKED_MISSING_REPLAY_INDEX = "BLOCKED_MISSING_REPLAY_INDEX"
GATE_BLOCKED_MISSING_BINDING_ROWS = "BLOCKED_MISSING_RESULT_BINDING_ROWS"
GATE_BLOCKED_MISSING_SAMPLE_RISK = "BLOCKED_MISSING_SAMPLE_RISK_REPORT"
GATE_BLOCKED_UNVERIFIED_REPLAY_SOURCE = "BLOCKED_UNVERIFIED_REPLAY_SOURCE"
GATE_BLOCKED_NO_LABELS_EXPECTED = "BLOCKED_NO_LABELS_BOUND_EXPECTED"
GATE_READY_FOR_SOURCE_MAP_CONTRACT_ONLY = "READY_FOR_SOURCE_MAP_CONTRACT_ONLY"

GATE_STATUSES = (
    GATE_BLOCKED_MISSING_REPLAY_INDEX,
    GATE_BLOCKED_MISSING_BINDING_ROWS,
    GATE_BLOCKED_MISSING_SAMPLE_RISK,
    GATE_BLOCKED_UNVERIFIED_REPLAY_SOURCE,
    GATE_BLOCKED_NO_LABELS_EXPECTED,
    GATE_READY_FOR_SOURCE_MAP_CONTRACT_ONLY,
)


@dataclass(frozen=True, slots=True)
class ResultBindingImplementationGateAudit:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    replay_index_path: str | None
    result_binding_rows_path: str | None
    sample_size_report_path: str | None
    overfit_risk_report_path: str | None
    replay_artifact_count: int
    replay_artifact_kinds: tuple[str, ...]
    binding_row_count: int
    labeled_row_count: int
    source_verified_label_count: int
    sample_days: int
    sample_trades: int
    sample_readiness_verdict: str | None
    overfit_risk_level: str | None
    gate_status: str
    implementation_allowed: bool = False
    label_binding_allowed: bool = False
    model_training_allowed: bool = False
    replay_execution_performed: bool = False
    labels_bound: bool = False
    real_pnl_calculation_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False
    production_claim_allowed: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class GateAuditBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    gate_audit_path: str
    optimizer_verdict_path: str
    gate_status: str
    implementation_allowed: bool = False
    label_binding_allowed: bool = False
    model_training_allowed: bool = False
    replay_execution_performed: bool = False
    labels_bound: bool = False
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
        raise ValueError(f"D10 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _rows_from_payload(payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _tuple_of_strings(value: Any) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(str(v) for v in value)
    return tuple()


def build_gate_audit(
    optimization_id: str,
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
    sample_size_report_path: str | Path | None,
    overfit_risk_report_path: str | Path | None,
) -> ResultBindingImplementationGateAudit:
    replay_index = _safe_load_json(replay_index_path)
    binding_rows_payload = _safe_load_json(result_binding_rows_path)
    sample_report = _safe_load_json(sample_size_report_path)
    overfit_report = _safe_load_json(overfit_risk_report_path)

    replay_artifact_count = int(replay_index.get("artifact_count", 0)) if replay_index else 0
    replay_artifact_kinds = _tuple_of_strings(replay_index.get("artifact_kinds")) if replay_index else tuple()
    binding_rows = _rows_from_payload(binding_rows_payload)

    binding_row_count = len(binding_rows)
    labeled_row_count = int(sample_report.get("labeled_row_count", 0)) if sample_report else 0
    source_verified_label_count = int(sample_report.get("source_verified_label_count", 0)) if sample_report else 0
    sample_days = int(sample_report.get("sample_days", 0)) if sample_report else 0
    sample_trades = int(sample_report.get("sample_trades", 0)) if sample_report else 0
    sample_readiness = sample_report.get("readiness_verdict") if sample_report else None
    overfit_level = overfit_report.get("overfit_risk_level") if overfit_report else None

    if not replay_index or replay_artifact_count <= 0:
        gate_status = GATE_BLOCKED_MISSING_REPLAY_INDEX
        remarks = "Replay index missing or empty."
    elif not binding_rows:
        gate_status = GATE_BLOCKED_MISSING_BINDING_ROWS
        remarks = "Result-binding rows missing."
    elif not sample_report or not overfit_report:
        gate_status = GATE_BLOCKED_MISSING_SAMPLE_RISK
        remarks = "Sample/overfit reports missing."
    elif labeled_row_count <= 0:
        gate_status = GATE_BLOCKED_NO_LABELS_EXPECTED
        remarks = "No labels are bound yet. Future source-map contract is needed before implementation."
    elif sample_readiness not in {"READY_FOR_RESEARCH_ONLY_MODEL_TRAINING", "RESEARCH_ONLY_FINDING"}:
        gate_status = GATE_BLOCKED_UNVERIFIED_REPLAY_SOURCE
        remarks = "Replay/result sources are not verified for label binding."
    else:
        gate_status = GATE_READY_FOR_SOURCE_MAP_CONTRACT_ONLY
        remarks = "Ready only for future source-map contract, not model training."

    return ResultBindingImplementationGateAudit(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=IMPLEMENTATION_GATE_CONTRACT_VERSION,
        accepted_for=IMPLEMENTATION_GATE_ACCEPTED_FOR,
        replay_index_path=str(replay_index_path) if replay_index_path else None,
        result_binding_rows_path=str(result_binding_rows_path) if result_binding_rows_path else None,
        sample_size_report_path=str(sample_size_report_path) if sample_size_report_path else None,
        overfit_risk_report_path=str(overfit_risk_report_path) if overfit_risk_report_path else None,
        replay_artifact_count=replay_artifact_count,
        replay_artifact_kinds=replay_artifact_kinds,
        binding_row_count=binding_row_count,
        labeled_row_count=labeled_row_count,
        source_verified_label_count=source_verified_label_count,
        sample_days=sample_days,
        sample_trades=sample_trades,
        sample_readiness_verdict=sample_readiness if isinstance(sample_readiness, str) else None,
        overfit_risk_level=overfit_level if isinstance(overfit_level, str) else None,
        gate_status=gate_status,
        remarks=remarks,
    )


def write_gate_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
    sample_size_report_path: str | Path | None,
    overfit_risk_report_path: str | Path | None,
) -> GateAuditBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit = build_gate_audit(
        optimization_id,
        replay_index_path=replay_index_path,
        result_binding_rows_path=result_binding_rows_path,
        sample_size_report_path=sample_size_report_path,
        overfit_risk_report_path=overfit_risk_report_path,
    )

    gate_path = out / "13_result_binding_implementation_gate.json"
    verdict_path = out / "09_optimizer_verdict.json"

    gate_path.write_text(json.dumps(asdict(audit), indent=2, sort_keys=True), encoding="utf-8")

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": IMPLEMENTATION_GATE_CONTRACT_VERSION,
        "accepted_for": IMPLEMENTATION_GATE_ACCEPTED_FOR,
        "gate_status": audit.gate_status,
        "implementation_allowed": False,
        "label_binding_allowed": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": audit.remarks,
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return GateAuditBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=IMPLEMENTATION_GATE_CONTRACT_VERSION,
        accepted_for=IMPLEMENTATION_GATE_ACCEPTED_FOR,
        gate_audit_path=gate_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        gate_status=audit.gate_status,
    )


def implementation_gate_summary(
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
    sample_size_report_path: str | Path | None,
    overfit_risk_report_path: str | Path | None,
) -> dict[str, Any]:
    audit = build_gate_audit(
        "D10_SUMMARY",
        replay_index_path=replay_index_path,
        result_binding_rows_path=result_binding_rows_path,
        sample_size_report_path=sample_size_report_path,
        overfit_risk_report_path=overfit_risk_report_path,
    )
    return {
        "contract_version": IMPLEMENTATION_GATE_CONTRACT_VERSION,
        "accepted_for": IMPLEMENTATION_GATE_ACCEPTED_FOR,
        "gate_status": audit.gate_status,
        "replay_artifact_count": audit.replay_artifact_count,
        "binding_row_count": audit.binding_row_count,
        "labeled_row_count": audit.labeled_row_count,
        "sample_days": audit.sample_days,
        "sample_trades": audit.sample_trades,
        "implementation_allowed": False,
        "label_binding_allowed": False,
        "model_training_allowed": False,
        "replay_execution_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "IMPLEMENTATION_GATE_CONTRACT_VERSION",
    "IMPLEMENTATION_GATE_ACCEPTED_FOR",
    "GATE_BLOCKED_MISSING_REPLAY_INDEX",
    "GATE_BLOCKED_MISSING_BINDING_ROWS",
    "GATE_BLOCKED_MISSING_SAMPLE_RISK",
    "GATE_BLOCKED_UNVERIFIED_REPLAY_SOURCE",
    "GATE_BLOCKED_NO_LABELS_EXPECTED",
    "GATE_READY_FOR_SOURCE_MAP_CONTRACT_ONLY",
    "GATE_STATUSES",
    "ResultBindingImplementationGateAudit",
    "GateAuditBuildResult",
    "build_gate_audit",
    "write_gate_audit",
    "implementation_gate_summary",
)
