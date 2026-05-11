"""Lane D D31 candidate replay binding requirement audit.

This module freezes the requirement that each optimization candidate must be
bound to a replay execution/result pack before labels or PnL can be trusted.

D31 is audit/contract only. It does not execute replay, create result packs,
attach candidate context, perform matching, bind labels, calculate PnL,
train/predict models, call brokers, write live Redis, mutate doctrine, or
approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

CANDIDATE_REPLAY_BINDING_REQUIREMENT_CONTRACT_VERSION = "replay_optimization_d31_candidate_replay_binding_requirement_contract_v1"
CANDIDATE_REPLAY_BINDING_REQUIREMENT_ACCEPTED_FOR = "CANDIDATE_REPLAY_BINDING_REQUIREMENT_AUDIT_ONLY"

REQUIREMENT_STATUS_BLOCKED_NO_CANDIDATE_MATRIX = "BLOCKED_NO_CANDIDATE_MATRIX"
REQUIREMENT_STATUS_BLOCKED_NO_VALUE_SOURCE_AUDIT = "BLOCKED_NO_D30_VALUE_SOURCE_AUDIT"
REQUIREMENT_STATUS_BLOCKED_NO_D30_VALUE_SOURCE_AUDIT = REQUIREMENT_STATUS_BLOCKED_NO_VALUE_SOURCE_AUDIT
REQUIREMENT_STATUS_REPLAY_BINDING_REQUIRED = "CANDIDATE_REPLAY_BINDING_REQUIRED_BEFORE_LABELS"
REQUIREMENT_STATUS_READY_FOR_BINDING_PLAN = "READY_FOR_CANDIDATE_REPLAY_BINDING_PLAN_CONTRACT_ONLY"

BINDING_REQUIRED_FIELDS = (
    "candidate_id",
    "candidate_fingerprint",
    "candidate_profile_ref",
    "candidate_profile_sha256",
    "replay_run_id",
    "replay_result_pack_id",
    "replay_result_pack_root",
    "replay_dataset_id",
    "replay_dataset_date",
    "replay_profile_id",
    "replay_profile_sha256",
    "result_integrity_verdict",
    "result_context_catalog_ref",
    "candidate_context_bridge_status",
    "candidate_replay_binding_status",
)

LABEL_SAFETY_FIELDS = (
    "label_binding_allowed",
    "labels_bound",
)

REQUIREMENT_COLUMNS = (
    "optimization_id",
    "requirement_id",
    "requirement_name",
    "required_before_label_binding",
    "current_status",
    "evidence_source",
    "candidate_count",
    "available_count",
    "missing_count",
    "blocking",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class CandidateReplayBindingRequirementRow:
    optimization_id: str
    requirement_id: str
    requirement_name: str
    required_before_label_binding: bool
    current_status: str
    evidence_source: str | None
    candidate_count: int
    available_count: int
    missing_count: int
    blocking: bool
    candidate_trade_matching_allowed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateReplayBindingRequirementBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    candidate_matrix_path: str | None
    value_source_report_path: str | None
    requirement_report_path: str
    requirement_rows_json_path: str
    requirement_rows_csv_path: str
    optimizer_verdict_path: str
    candidate_count: int
    requirement_row_count: int
    blocking_requirement_count: int
    binding_required_field_count: int
    requirement_status: str
    replay_execution_performed: bool = False
    result_pack_created: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
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
        raise ValueError(f"D31 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _present_count(rows: Sequence[Mapping[str, Any]], key: str) -> int:
    count = 0
    for row in rows:
        value = row.get(key)
        if value is not None and str(value).strip():
            count += 1
    return count


def build_candidate_replay_binding_requirement_rows(
    optimization_id: str,
    *,
    candidate_matrix_path: str | Path | None,
    value_source_report_path: str | Path | None,
) -> tuple[CandidateReplayBindingRequirementRow, ...]:
    candidate_rows = _rows_from_payload(_safe_load_json(candidate_matrix_path))
    value_report = _safe_load_json(value_source_report_path)
    candidate_count = len(candidate_rows)

    value_status = None
    if isinstance(value_report, dict):
        value_status = value_report.get("value_source_status")

    rows: list[CandidateReplayBindingRequirementRow] = []

    for i, field in enumerate(BINDING_REQUIRED_FIELDS, start=1):
        available = _present_count(candidate_rows, field)
        missing = max(candidate_count - available, 0)
        blocking = missing > 0

        if field in {"candidate_id"}:
            evidence = "candidate_matrix"
            status = "AVAILABLE" if available == candidate_count and candidate_count else "MISSING_OR_PARTIAL"
            blocking = False if status == "AVAILABLE" else True
        elif field in {"label_binding_allowed", "labels_bound"}:
            evidence = "D30 safety"
            available = 0
            missing = candidate_count
            status = "INTENTIONALLY_FALSE_UNTIL_REPLAY_BINDING"
            blocking = True
        else:
            evidence = "candidate_matrix / future replay binding"
            status = "MISSING_REQUIRES_REPLAY_BINDING"
            blocking = True

        rows.append(
            CandidateReplayBindingRequirementRow(
                optimization_id=optimization_id,
                requirement_id=f"REQ_{i:04d}",
                requirement_name=field,
                required_before_label_binding=True,
                current_status=status,
                evidence_source=evidence,
                candidate_count=candidate_count,
                available_count=available,
                missing_count=missing,
                blocking=blocking,
                candidate_trade_matching_allowed=False,
                label_binding_allowed=False,
                labels_bound=False,
                remarks=(
                    "Candidate rows are parameter candidates. This field must be "
                    "provided by a candidate-specific replay binding/result pack "
                    "before labels or PnL can be trusted."
                ),
            )
        )

    # This optional D30 status row is an audit row, not one of the frozen
    # BINDING_REQUIRED_FIELDS. It must not increase binding_required_field_count.
    for safety_i, field in enumerate(LABEL_SAFETY_FIELDS, start=1):
        rows.append(
            CandidateReplayBindingRequirementRow(
                optimization_id=optimization_id,
                requirement_id=f"SAFETY_{safety_i:04d}",
                requirement_name=field,
                required_before_label_binding=True,
                current_status="INTENTIONALLY_FALSE_UNTIL_REPLAY_BINDING",
                evidence_source="label safety policy",
                candidate_count=candidate_count,
                available_count=0,
                missing_count=candidate_count,
                blocking=True,
                candidate_trade_matching_allowed=False,
                label_binding_allowed=False,
                labels_bound=False,
                remarks=(
                    "Label safety fields are intentionally false until candidate-specific "
                    "replay binding and verified labels exist."
                ),
            )
        )

    if value_status:
        rows.append(
            CandidateReplayBindingRequirementRow(
                optimization_id=optimization_id,
                requirement_id=f"REQ_{len(rows) + 1:04d}",
                requirement_name="d30_value_source_status",
                required_before_label_binding=True,
                current_status=str(value_status),
                evidence_source=str(value_source_report_path) if value_source_report_path else None,
                candidate_count=candidate_count,
                available_count=0,
                missing_count=candidate_count,
                blocking=str(value_status) != "CANDIDATE_CONTEXT_VALUE_SOURCES_FOUND_AUDIT_ONLY_NOT_LABEL_READY",
                candidate_trade_matching_allowed=False,
                label_binding_allowed=False,
                labels_bound=False,
                remarks="D30 confirms whether existing candidate-side values exist. Missing values require candidate replay binding.",
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


def write_candidate_replay_binding_requirement_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_matrix_path: str | Path | None,
    value_source_report_path: str | Path | None,
) -> CandidateReplayBindingRequirementBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    candidate_rows = _rows_from_payload(_safe_load_json(candidate_matrix_path))
    value_report = _safe_load_json(value_source_report_path)

    requirement_rows = build_candidate_replay_binding_requirement_rows(
        optimization_id,
        candidate_matrix_path=candidate_matrix_path,
        value_source_report_path=value_source_report_path,
    )
    row_dicts = [asdict(row) for row in requirement_rows]

    blocking_count = sum(1 for row in requirement_rows if row.blocking)

    if not candidate_rows:
        status = REQUIREMENT_STATUS_BLOCKED_NO_CANDIDATE_MATRIX
    elif not isinstance(value_report, dict):
        status = REQUIREMENT_STATUS_BLOCKED_NO_VALUE_SOURCE_AUDIT
    elif blocking_count > 0:
        status = REQUIREMENT_STATUS_REPLAY_BINDING_REQUIRED
    else:
        status = REQUIREMENT_STATUS_READY_FOR_BINDING_PLAN

    report_path = out / "34_candidate_replay_binding_requirement_report.json"
    rows_json_path = out / "34_candidate_replay_binding_requirement_rows.json"
    rows_csv_path = out / "34_candidate_replay_binding_requirement_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
        "replay_execution_performed": False,
        "result_pack_created": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "real_pnl_calculation_performed": False,
        "model_training_performed": False,
        "model_prediction_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }

    report = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Binding Requirement Audit",
        "contract_version": CANDIDATE_REPLAY_BINDING_REQUIREMENT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_REQUIREMENT_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
        "value_source_report_path": str(value_source_report_path) if value_source_report_path else None,
        "candidate_count": len(candidate_rows),
        "requirement_row_count": len(requirement_rows),
        "blocking_requirement_count": blocking_count,
        "binding_required_fields": list(BINDING_REQUIRED_FIELDS),
        "binding_required_field_count": len(BINDING_REQUIRED_FIELDS),
        "requirement_status": status,
        "important_limitation": (
            "D31 freezes the requirement only. It does not execute candidate replays, "
            "create result packs, attach candidate context, match trades, or bind labels."
        ),
        "rows": row_dicts,
        "safety": safety,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Replay Binding Requirement Rows",
        "contract_version": CANDIDATE_REPLAY_BINDING_REQUIREMENT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_REQUIREMENT_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "requirement_status": status,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, REQUIREMENT_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": CANDIDATE_REPLAY_BINDING_REQUIREMENT_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_REPLAY_BINDING_REQUIREMENT_ACCEPTED_FOR,
        "requirement_status": status,
        "candidate_count": len(candidate_rows),
        "requirement_row_count": len(requirement_rows),
        "blocking_requirement_count": blocking_count,
        "binding_required_field_count": len(BINDING_REQUIRED_FIELDS),
        "replay_execution_performed": False,
        "result_pack_created": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "Candidate-specific replay binding/result packs are required before matching, labels, or PnL.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return CandidateReplayBindingRequirementBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_REPLAY_BINDING_REQUIREMENT_CONTRACT_VERSION,
        accepted_for=CANDIDATE_REPLAY_BINDING_REQUIREMENT_ACCEPTED_FOR,
        candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
        value_source_report_path=str(value_source_report_path) if value_source_report_path else None,
        requirement_report_path=report_path.as_posix(),
        requirement_rows_json_path=rows_json_path.as_posix(),
        requirement_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        candidate_count=len(candidate_rows),
        requirement_row_count=len(requirement_rows),
        blocking_requirement_count=blocking_count,
        binding_required_field_count=len(BINDING_REQUIRED_FIELDS),
        requirement_status=status,
    )


__all__ = (
    "CANDIDATE_REPLAY_BINDING_REQUIREMENT_CONTRACT_VERSION",
    "CANDIDATE_REPLAY_BINDING_REQUIREMENT_ACCEPTED_FOR",
    "REQUIREMENT_STATUS_BLOCKED_NO_CANDIDATE_MATRIX",
    "REQUIREMENT_STATUS_BLOCKED_NO_D30_VALUE_SOURCE_AUDIT",
    "REQUIREMENT_STATUS_REPLAY_BINDING_REQUIRED",
    "REQUIREMENT_STATUS_READY_FOR_BINDING_PLAN",
    "BINDING_REQUIRED_FIELDS",
    "LABEL_SAFETY_FIELDS",
    "REQUIREMENT_COLUMNS",
    "CandidateReplayBindingRequirementRow",
    "CandidateReplayBindingRequirementBuildResult",
    "build_candidate_replay_binding_requirement_rows",
    "write_candidate_replay_binding_requirement_audit",
)
