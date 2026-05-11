"""Lane D D12 result-binding precondition audit.

This module audits whether D11 source-map rows are safe enough for future
result-label binding. It does not repair the map, bind labels, calculate PnL,
execute replay, train models, or approve paper/live usage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import OUTPUT_ROOT

PRECONDITION_AUDIT_CONTRACT_VERSION = "replay_optimization_d12_precondition_audit_contract_v1"
PRECONDITION_AUDIT_ACCEPTED_FOR = "RESULT_BINDING_PRECONDITION_AUDIT_ONLY"

PRECONDITION_BLOCKED_MISSING_SOURCE_MAP = "BLOCKED_MISSING_SOURCE_MAP"
PRECONDITION_BLOCKED_REFERENCE_ONLY_SOURCE_MAP = "BLOCKED_REFERENCE_ONLY_SOURCE_MAP"
PRECONDITION_BLOCKED_MIXED_REPLAY_ARTIFACT_ROOTS = "BLOCKED_MIXED_REPLAY_ARTIFACT_ROOTS"
PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED = "BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED"
PRECONDITION_READY_FOR_FUTURE_SOURCE_MAP_REPAIR = "READY_FOR_FUTURE_SOURCE_MAP_REPAIR_CONTRACT_ONLY"

SOURCE_REF_FIELDS = (
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)


@dataclass(frozen=True, slots=True)
class SourceMapRowAudit:
    optimization_id: str
    row_index: int
    source_map_id: str
    candidate_id: str
    source_map_status: str | None
    present_ref_count: int
    missing_ref_count: int
    unique_root_count: int
    unique_roots: tuple[str, ...]
    mixed_replay_roots: bool
    label_binding_allowed: bool
    labels_bound: bool
    row_precondition_status: str
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class BindingPreconditionAudit:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    source_map_path: str | None
    source_map_row_count: int
    audited_row_count: int
    reference_only_row_count: int
    mixed_root_row_count: int
    labels_allowed_row_count: int
    labels_bound_row_count: int
    complete_reference_row_count: int
    precondition_status: str
    row_audits: tuple[SourceMapRowAudit, ...]
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
class PreconditionAuditBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    precondition_audit_path: str
    optimizer_verdict_path: str
    precondition_status: str
    source_map_row_count: int
    mixed_root_row_count: int
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
        raise ValueError(f"D12 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _root_signature(ref: str) -> str:
    path = Path(ref)
    parent = path.parent
    if parent.name == "artifacts":
        return parent.parent.as_posix()
    return parent.as_posix()


def _present_refs(row: Mapping[str, Any]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for field in SOURCE_REF_FIELDS:
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            refs[field] = value
    return refs


def audit_source_map_rows(
    optimization_id: str,
    *,
    source_map_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[SourceMapRowAudit, ...]:
    payload = _safe_load_json(source_map_path)
    rows = _rows_from_payload(payload)

    audits: list[SourceMapRowAudit] = []
    for i, row in enumerate(rows[:max_rows], start=1):
        refs = _present_refs(row)
        unique_roots = tuple(sorted({_root_signature(ref) for ref in refs.values()}))
        mixed = len(unique_roots) > 1
        label_allowed = bool(row.get("label_binding_allowed"))
        labels_bound = bool(row.get("labels_bound"))
        source_status = row.get("source_map_status")
        if labels_bound or label_allowed:
            row_status = PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED
            remarks = "Source-map row unexpectedly allows or contains labels."
        elif mixed:
            row_status = PRECONDITION_BLOCKED_MIXED_REPLAY_ARTIFACT_ROOTS
            remarks = "Source references come from more than one replay artifact root."
        elif source_status == "REFERENCE_ONLY_UNVERIFIED_NO_LABEL_BINDING":
            row_status = PRECONDITION_BLOCKED_REFERENCE_ONLY_SOURCE_MAP
            remarks = "Source map is reference-only and still unverified."
        else:
            row_status = PRECONDITION_READY_FOR_FUTURE_SOURCE_MAP_REPAIR
            remarks = "Row is not label-ready; future source-map repair still required."

        audits.append(
            SourceMapRowAudit(
                optimization_id=optimization_id,
                row_index=i,
                source_map_id=str(row.get("source_map_id") or f"SMAP_UNKNOWN_{i:06d}"),
                candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                source_map_status=source_status if isinstance(source_status, str) else None,
                present_ref_count=len(refs),
                missing_ref_count=len(SOURCE_REF_FIELDS) - len(refs),
                unique_root_count=len(unique_roots),
                unique_roots=unique_roots,
                mixed_replay_roots=mixed,
                label_binding_allowed=label_allowed,
                labels_bound=labels_bound,
                row_precondition_status=row_status,
                remarks=remarks,
            )
        )
    return tuple(audits)


def build_precondition_audit(
    optimization_id: str,
    *,
    source_map_path: str | Path | None,
    max_rows: int = 10000,
) -> BindingPreconditionAudit:
    payload = _safe_load_json(source_map_path)
    rows = _rows_from_payload(payload)
    row_audits = audit_source_map_rows(
        optimization_id,
        source_map_path=source_map_path,
        max_rows=max_rows,
    )

    reference_only_count = sum(
        1 for audit in row_audits
        if audit.source_map_status == "REFERENCE_ONLY_UNVERIFIED_NO_LABEL_BINDING"
    )
    mixed_count = sum(1 for audit in row_audits if audit.mixed_replay_roots)
    labels_allowed_count = sum(1 for audit in row_audits if audit.label_binding_allowed)
    labels_bound_count = sum(1 for audit in row_audits if audit.labels_bound)
    complete_ref_count = sum(1 for audit in row_audits if audit.present_ref_count == len(SOURCE_REF_FIELDS))

    if not rows:
        status = PRECONDITION_BLOCKED_MISSING_SOURCE_MAP
        remarks = "No source-map rows exist."
    elif labels_allowed_count or labels_bound_count:
        status = PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED
        remarks = "Labels or label permission appeared before binding approval."
    elif mixed_count:
        status = PRECONDITION_BLOCKED_MIXED_REPLAY_ARTIFACT_ROOTS
        remarks = "One or more rows reference artifacts from multiple replay roots."
    elif reference_only_count:
        status = PRECONDITION_BLOCKED_REFERENCE_ONLY_SOURCE_MAP
        remarks = "Source map remains reference-only and unverified."
    else:
        status = PRECONDITION_READY_FOR_FUTURE_SOURCE_MAP_REPAIR
        remarks = "Future source-map repair contract may proceed, but label binding remains blocked."

    return BindingPreconditionAudit(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=PRECONDITION_AUDIT_CONTRACT_VERSION,
        accepted_for=PRECONDITION_AUDIT_ACCEPTED_FOR,
        source_map_path=str(source_map_path) if source_map_path else None,
        source_map_row_count=len(rows),
        audited_row_count=len(row_audits),
        reference_only_row_count=reference_only_count,
        mixed_root_row_count=mixed_count,
        labels_allowed_row_count=labels_allowed_count,
        labels_bound_row_count=labels_bound_count,
        complete_reference_row_count=complete_ref_count,
        precondition_status=status,
        row_audits=row_audits,
        remarks=remarks,
    )


def write_precondition_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    source_map_path: str | Path | None,
    max_rows: int = 10000,
) -> PreconditionAuditBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit = build_precondition_audit(
        optimization_id,
        source_map_path=source_map_path,
        max_rows=max_rows,
    )

    audit_path = out / "15_result_binding_precondition_audit.json"
    verdict_path = out / "09_optimizer_verdict.json"

    audit_path.write_text(json.dumps(asdict(audit), indent=2, sort_keys=True), encoding="utf-8")

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": PRECONDITION_AUDIT_CONTRACT_VERSION,
        "accepted_for": PRECONDITION_AUDIT_ACCEPTED_FOR,
        "precondition_status": audit.precondition_status,
        "source_map_row_count": audit.source_map_row_count,
        "mixed_root_row_count": audit.mixed_root_row_count,
        "label_binding_allowed": False,
        "labels_bound": False,
        "implementation_allowed": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": audit.remarks,
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return PreconditionAuditBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=PRECONDITION_AUDIT_CONTRACT_VERSION,
        accepted_for=PRECONDITION_AUDIT_ACCEPTED_FOR,
        precondition_audit_path=audit_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        precondition_status=audit.precondition_status,
        source_map_row_count=audit.source_map_row_count,
        mixed_root_row_count=audit.mixed_root_row_count,
    )


def precondition_audit_summary(*, source_map_path: str | Path | None) -> dict[str, Any]:
    audit = build_precondition_audit(
        "D12_SUMMARY",
        source_map_path=source_map_path,
        max_rows=10000,
    )
    return {
        "contract_version": PRECONDITION_AUDIT_CONTRACT_VERSION,
        "accepted_for": PRECONDITION_AUDIT_ACCEPTED_FOR,
        "source_map_row_count": audit.source_map_row_count,
        "audited_row_count": audit.audited_row_count,
        "reference_only_row_count": audit.reference_only_row_count,
        "mixed_root_row_count": audit.mixed_root_row_count,
        "precondition_status": audit.precondition_status,
        "label_binding_allowed": False,
        "labels_bound": False,
        "replay_execution_performed": False,
        "real_pnl_calculation_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "PRECONDITION_AUDIT_CONTRACT_VERSION",
    "PRECONDITION_AUDIT_ACCEPTED_FOR",
    "PRECONDITION_BLOCKED_MISSING_SOURCE_MAP",
    "PRECONDITION_BLOCKED_REFERENCE_ONLY_SOURCE_MAP",
    "PRECONDITION_BLOCKED_MIXED_REPLAY_ARTIFACT_ROOTS",
    "PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED",
    "PRECONDITION_READY_FOR_FUTURE_SOURCE_MAP_REPAIR",
    "SOURCE_REF_FIELDS",
    "SourceMapRowAudit",
    "BindingPreconditionAudit",
    "PreconditionAuditBuildResult",
    "audit_source_map_rows",
    "build_precondition_audit",
    "write_precondition_audit",
    "precondition_audit_summary",
)
