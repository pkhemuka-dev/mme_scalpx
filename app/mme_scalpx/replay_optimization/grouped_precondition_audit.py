"""Lane D D14 grouped source-map precondition audit.

This module audits D13 grouped source-map rows. It confirms whether grouping
removed mixed replay roots and whether the selected replay group contains a
complete set of required replay refs.

It does not bind labels, match candidates to trades, calculate PnL, execute
replay, train/predict models, call brokers, write live Redis, mutate doctrine,
or approve paper/live.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import OUTPUT_ROOT

GROUPED_PRECONDITION_AUDIT_CONTRACT_VERSION = "replay_optimization_d14_grouped_precondition_audit_contract_v1"
GROUPED_PRECONDITION_AUDIT_ACCEPTED_FOR = "GROUPED_SOURCE_MAP_PRECONDITION_AUDIT_ONLY"

GROUPED_PRECONDITION_BLOCKED_MISSING_GROUPED_SOURCE_MAP = "BLOCKED_MISSING_GROUPED_SOURCE_MAP"
GROUPED_PRECONDITION_BLOCKED_MIXED_REPLAY_ROOTS_REMAIN = "BLOCKED_MIXED_REPLAY_ROOTS_REMAIN"
GROUPED_PRECONDITION_BLOCKED_INCOMPLETE_REPLAY_GROUP = "BLOCKED_INCOMPLETE_REPLAY_GROUP"
GROUPED_PRECONDITION_BLOCKED_REFERENCE_ONLY_NO_TRADE_MATCH = "BLOCKED_REFERENCE_ONLY_NO_TRADE_MATCH"
GROUPED_PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED = "BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED"
GROUPED_PRECONDITION_READY_FOR_CANDIDATE_TRADE_MATCH_CONTRACT_ONLY = "READY_FOR_CANDIDATE_TRADE_MATCH_CONTRACT_ONLY"

GROUPED_SOURCE_REF_FIELDS = (
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)


@dataclass(frozen=True, slots=True)
class GroupedSourceMapRowAudit:
    optimization_id: str
    row_index: int
    grouped_source_map_id: str
    candidate_id: str
    selected_replay_root: str | None
    source_map_status: str | None
    selected_group_complete: bool
    present_ref_count: int
    missing_ref_count: int
    missing_ref_fields: tuple[str, ...]
    unique_root_count: int
    unique_roots: tuple[str, ...]
    mixed_replay_roots: bool
    label_binding_allowed: bool
    labels_bound: bool
    row_precondition_status: str
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class GroupedSourceMapPreconditionAudit:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    grouped_source_map_path: str | None
    grouping_report_path: str | None
    grouped_source_map_row_count: int
    audited_row_count: int
    complete_group_count: int
    replay_group_count: int
    partial_row_count: int
    complete_row_count: int
    mixed_root_row_count: int
    labels_allowed_row_count: int
    labels_bound_row_count: int
    precondition_status: str
    row_audits: tuple[GroupedSourceMapRowAudit, ...]
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
class GroupedPreconditionAuditBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    grouped_precondition_audit_path: str
    optimizer_verdict_path: str
    precondition_status: str
    grouped_source_map_row_count: int
    complete_group_count: int
    mixed_root_row_count: int
    partial_row_count: int
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
        raise ValueError(f"D14 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _root_signature(path_value: str) -> str:
    path = Path(path_value)
    parent = path.parent
    if parent.name == "artifacts":
        return parent.parent.as_posix()
    return parent.as_posix()


def _present_refs(row: Mapping[str, Any]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for field in GROUPED_SOURCE_REF_FIELDS:
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            refs[field] = value
    return refs


def audit_grouped_source_map_rows(
    optimization_id: str,
    *,
    grouped_source_map_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[GroupedSourceMapRowAudit, ...]:
    payload = _safe_load_json(grouped_source_map_path)
    rows = _rows_from_payload(payload)

    audits: list[GroupedSourceMapRowAudit] = []
    for i, row in enumerate(rows[:max_rows], start=1):
        refs = _present_refs(row)
        missing = tuple(field for field in GROUPED_SOURCE_REF_FIELDS if field not in refs)
        unique_roots = tuple(sorted({_root_signature(ref) for ref in refs.values()}))
        mixed = len(unique_roots) > 1
        label_allowed = bool(row.get("label_binding_allowed"))
        labels_bound = bool(row.get("labels_bound"))
        selected_complete = bool(row.get("selected_group_complete"))
        source_status = row.get("source_map_status")

        if labels_bound or label_allowed:
            row_status = GROUPED_PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED
            remarks = "Grouped source-map row unexpectedly allows or contains labels."
        elif mixed:
            row_status = GROUPED_PRECONDITION_BLOCKED_MIXED_REPLAY_ROOTS_REMAIN
            remarks = "Grouped row still has references from more than one replay root."
        elif not selected_complete or missing:
            row_status = GROUPED_PRECONDITION_BLOCKED_INCOMPLETE_REPLAY_GROUP
            remarks = "Selected replay group is incomplete or missing required refs."
        elif source_status and "NO_LABEL_BINDING" in str(source_status):
            row_status = GROUPED_PRECONDITION_BLOCKED_REFERENCE_ONLY_NO_TRADE_MATCH
            remarks = "Grouped source-map is still reference-only with no candidate-to-trade matching."
        else:
            row_status = GROUPED_PRECONDITION_READY_FOR_CANDIDATE_TRADE_MATCH_CONTRACT_ONLY
            remarks = "Only future candidate-to-trade matching contract may proceed."

        audits.append(
            GroupedSourceMapRowAudit(
                optimization_id=optimization_id,
                row_index=i,
                grouped_source_map_id=str(row.get("grouped_source_map_id") or f"GSMAP_UNKNOWN_{i:06d}"),
                candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                selected_replay_root=row.get("selected_replay_root") if isinstance(row.get("selected_replay_root"), str) else None,
                source_map_status=source_status if isinstance(source_status, str) else None,
                selected_group_complete=selected_complete,
                present_ref_count=len(refs),
                missing_ref_count=len(missing),
                missing_ref_fields=missing,
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


def build_grouped_precondition_audit(
    optimization_id: str,
    *,
    grouped_source_map_path: str | Path | None,
    grouping_report_path: str | Path | None,
    max_rows: int = 10000,
) -> GroupedSourceMapPreconditionAudit:
    payload = _safe_load_json(grouped_source_map_path)
    rows = _rows_from_payload(payload)
    grouping_payload = _safe_load_json(grouping_report_path)

    row_audits = audit_grouped_source_map_rows(
        optimization_id,
        grouped_source_map_path=grouped_source_map_path,
        max_rows=max_rows,
    )

    replay_group_count = int(grouping_payload.get("replay_group_count", 0)) if grouping_payload else 0
    complete_group_count = int(grouping_payload.get("complete_group_count", 0)) if grouping_payload else 0
    partial_count = sum(1 for audit in row_audits if not audit.selected_group_complete or audit.missing_ref_count > 0)
    complete_row_count = sum(1 for audit in row_audits if audit.selected_group_complete and audit.missing_ref_count == 0)
    mixed_count = sum(1 for audit in row_audits if audit.mixed_replay_roots)
    labels_allowed_count = sum(1 for audit in row_audits if audit.label_binding_allowed)
    labels_bound_count = sum(1 for audit in row_audits if audit.labels_bound)

    if not rows:
        status = GROUPED_PRECONDITION_BLOCKED_MISSING_GROUPED_SOURCE_MAP
        remarks = "Grouped source-map rows are missing."
    elif labels_allowed_count or labels_bound_count:
        status = GROUPED_PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED
        remarks = "Labels or label permission appeared before approval."
    elif mixed_count:
        status = GROUPED_PRECONDITION_BLOCKED_MIXED_REPLAY_ROOTS_REMAIN
        remarks = "Mixed replay roots remain after grouping."
    elif partial_count:
        status = GROUPED_PRECONDITION_BLOCKED_INCOMPLETE_REPLAY_GROUP
        remarks = "Grouped source-map is single-root but incomplete."
    else:
        status = GROUPED_PRECONDITION_BLOCKED_REFERENCE_ONLY_NO_TRADE_MATCH
        remarks = "Grouped source-map is complete enough for future matching contract, but still reference-only."

    return GroupedSourceMapPreconditionAudit(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=GROUPED_PRECONDITION_AUDIT_CONTRACT_VERSION,
        accepted_for=GROUPED_PRECONDITION_AUDIT_ACCEPTED_FOR,
        grouped_source_map_path=str(grouped_source_map_path) if grouped_source_map_path else None,
        grouping_report_path=str(grouping_report_path) if grouping_report_path else None,
        grouped_source_map_row_count=len(rows),
        audited_row_count=len(row_audits),
        complete_group_count=complete_group_count,
        replay_group_count=replay_group_count,
        partial_row_count=partial_count,
        complete_row_count=complete_row_count,
        mixed_root_row_count=mixed_count,
        labels_allowed_row_count=labels_allowed_count,
        labels_bound_row_count=labels_bound_count,
        precondition_status=status,
        row_audits=row_audits,
        remarks=remarks,
    )


def write_grouped_precondition_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    grouped_source_map_path: str | Path | None,
    grouping_report_path: str | Path | None,
    max_rows: int = 10000,
) -> GroupedPreconditionAuditBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit = build_grouped_precondition_audit(
        optimization_id,
        grouped_source_map_path=grouped_source_map_path,
        grouping_report_path=grouping_report_path,
        max_rows=max_rows,
    )

    audit_path = out / "17_grouped_source_map_precondition_audit.json"
    verdict_path = out / "09_optimizer_verdict.json"

    audit_path.write_text(json.dumps(asdict(audit), indent=2, sort_keys=True), encoding="utf-8")

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": GROUPED_PRECONDITION_AUDIT_CONTRACT_VERSION,
        "accepted_for": GROUPED_PRECONDITION_AUDIT_ACCEPTED_FOR,
        "precondition_status": audit.precondition_status,
        "grouped_source_map_row_count": audit.grouped_source_map_row_count,
        "complete_group_count": audit.complete_group_count,
        "mixed_root_row_count": audit.mixed_root_row_count,
        "partial_row_count": audit.partial_row_count,
        "candidate_trade_matching_allowed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "implementation_allowed": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": audit.remarks,
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return GroupedPreconditionAuditBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=GROUPED_PRECONDITION_AUDIT_CONTRACT_VERSION,
        accepted_for=GROUPED_PRECONDITION_AUDIT_ACCEPTED_FOR,
        grouped_precondition_audit_path=audit_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        precondition_status=audit.precondition_status,
        grouped_source_map_row_count=audit.grouped_source_map_row_count,
        complete_group_count=audit.complete_group_count,
        mixed_root_row_count=audit.mixed_root_row_count,
        partial_row_count=audit.partial_row_count,
    )


def grouped_precondition_audit_summary(
    *,
    grouped_source_map_path: str | Path | None,
    grouping_report_path: str | Path | None,
) -> dict[str, Any]:
    audit = build_grouped_precondition_audit(
        "D14_SUMMARY",
        grouped_source_map_path=grouped_source_map_path,
        grouping_report_path=grouping_report_path,
        max_rows=10000,
    )
    return {
        "contract_version": GROUPED_PRECONDITION_AUDIT_CONTRACT_VERSION,
        "accepted_for": GROUPED_PRECONDITION_AUDIT_ACCEPTED_FOR,
        "grouped_source_map_row_count": audit.grouped_source_map_row_count,
        "complete_group_count": audit.complete_group_count,
        "mixed_root_row_count": audit.mixed_root_row_count,
        "partial_row_count": audit.partial_row_count,
        "precondition_status": audit.precondition_status,
        "candidate_trade_matching_allowed": False,
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
    "GROUPED_PRECONDITION_AUDIT_CONTRACT_VERSION",
    "GROUPED_PRECONDITION_AUDIT_ACCEPTED_FOR",
    "GROUPED_PRECONDITION_BLOCKED_MISSING_GROUPED_SOURCE_MAP",
    "GROUPED_PRECONDITION_BLOCKED_MIXED_REPLAY_ROOTS_REMAIN",
    "GROUPED_PRECONDITION_BLOCKED_INCOMPLETE_REPLAY_GROUP",
    "GROUPED_PRECONDITION_BLOCKED_REFERENCE_ONLY_NO_TRADE_MATCH",
    "GROUPED_PRECONDITION_BLOCKED_LABELS_ALREADY_BOUND_UNEXPECTED",
    "GROUPED_PRECONDITION_READY_FOR_CANDIDATE_TRADE_MATCH_CONTRACT_ONLY",
    "GROUPED_SOURCE_REF_FIELDS",
    "GroupedSourceMapRowAudit",
    "GroupedSourceMapPreconditionAudit",
    "GroupedPreconditionAuditBuildResult",
    "audit_grouped_source_map_rows",
    "build_grouped_precondition_audit",
    "write_grouped_precondition_audit",
    "grouped_precondition_audit_summary",
)
