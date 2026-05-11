"""Lane D D39 Lane C/E execution package requirement.

This module freezes the requirement surface that a future Lane C/E-compatible
execution/materialization package must satisfy before any candidate-specific
replay/result-pack materialization can run.

D39 is requirement-only. It does not execute replay, create result packs, write
candidate artifacts, attach candidate context, perform matching, bind labels,
calculate PnL, train/predict models, call brokers, write live Redis, mutate
doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_CONTRACT_VERSION = "replay_optimization_d39_lane_ce_execution_package_requirement_contract_v1"
LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_ACCEPTED_FOR = "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION"

PACKAGE_STATUS_READY_NO_EXECUTION = "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_READY_NO_EXECUTION"
PACKAGE_STATUS_BLOCKED_NO_PHASE_GATE = "BLOCKED_NO_D38_PHASE_GATE_SUMMARY"
PACKAGE_STATUS_BLOCKED_PHASE_GATE_NOT_READY = "BLOCKED_D38_PHASE_GATE_NOT_READY"
PACKAGE_STATUS_BLOCKED_NO_HANDOFF_ROWS = "BLOCKED_NO_D37_HANDOFF_ROWS"

PACKAGE_ROW_STATUS_REQUIRED_NO_EXECUTION = "PACKAGE_REQUIREMENT_REQUIRED_NO_EXECUTION"
PACKAGE_ROW_STATUS_BLOCKED_HANDOFF_NOT_READY = "BLOCKED_HANDOFF_NOT_READY"

EXECUTION_PACKAGE_REQUIREMENTS = (
    "latest_d38_phase_gate_pass",
    "latest_d37_handoff_ready",
    "lane_owner_declared_c_or_e",
    "lane_d_execution_blocked",
    "candidate_subset_or_batch_size_declared",
    "source_handoff_rows_declared",
    "candidate_profile_materialization_plan_declared",
    "candidate_effective_inputs_plan_declared",
    "candidate_replay_manifest_plan_declared",
    "candidate_result_pack_manifest_plan_declared",
    "candidate_integrity_report_plan_declared",
    "candidate_context_catalog_plan_declared",
    "candidate_label_precondition_plan_declared",
    "offline_execution_shadow_scope_declared",
    "no_broker_no_live_redis_no_paper_live_policy_declared",
    "lane_c_runner_dependency_check_declared",
    "lane_e_artifact_audit_check_declared",
    "post_materialization_validation_required",
    "label_binding_still_blocked_until_verified_result_pack",
)

PACKAGE_COLUMNS = (
    "optimization_id",
    "package_requirement_id",
    "handoff_id",
    "candidate_id",
    "candidate_fingerprint",
    "planned_result_pack_root",
    "recommended_owner",
    "required_execution_owner_options",
    "package_requirements",
    "package_requirement_count",
    "missing_package_requirements",
    "missing_package_requirement_count",
    "package_row_status",
    "lane_d_execution_allowed",
    "lane_c_or_e_execution_required",
    "replay_execution_allowed_in_lane_d",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "artifact_file_creation_allowed_in_lane_d",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class LaneCEExecutionPackageRequirementRow:
    optimization_id: str
    package_requirement_id: str
    handoff_id: str | None
    candidate_id: str | None
    candidate_fingerprint: str | None
    planned_result_pack_root: str | None
    recommended_owner: str | None
    required_execution_owner_options: str
    package_requirements: str
    package_requirement_count: int
    missing_package_requirements: str
    missing_package_requirement_count: int
    package_row_status: str
    lane_d_execution_allowed: bool = False
    lane_c_or_e_execution_required: bool = True
    replay_execution_allowed_in_lane_d: bool = False
    replay_execution_performed: bool = False
    result_pack_creation_allowed_in_lane_d: bool = False
    result_pack_created: bool = False
    artifact_file_creation_allowed_in_lane_d: bool = False
    candidate_context_attached: bool = False
    candidate_trade_matching_allowed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class LaneCEExecutionPackageRequirementBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    phase_summary_path: str | None
    handoff_rows_path: str | None
    package_schema_path: str
    package_rows_json_path: str
    package_rows_csv_path: str
    optimizer_verdict_path: str
    handoff_row_count: int
    package_row_count: int
    package_ready_count: int
    blocked_row_count: int
    missing_package_requirement_row_count: int
    package_status: str
    lane_d_execution_allowed: bool = False
    lane_c_or_e_execution_required: bool = True
    replay_execution_allowed: bool = False
    replay_execution_performed: bool = False
    result_pack_creation_allowed: bool = False
    result_pack_created: bool = False
    artifact_file_creation_allowed: bool = False
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
        raise ValueError(f"D39 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _phase_status(phase_summary_path: str | Path | None) -> str | None:
    payload = _safe_load_json(phase_summary_path)
    if isinstance(payload, dict):
        value = payload.get("phase_status")
        return str(value) if value is not None else None
    return None


def _missing_requirements(
    row: Mapping[str, Any],
    *,
    phase_ready: bool,
) -> tuple[str, ...]:
    missing: list[str] = []

    if not phase_ready:
        missing.append("latest_d38_phase_gate_pass")
    if row.get("handoff_row_status") != "HANDOFF_READY_NO_EXECUTION":
        missing.append("latest_d37_handoff_ready")
    if not row.get("recommended_owner"):
        missing.append("lane_owner_declared_c_or_e")
    if row.get("lane_d_execution_allowed") is not False:
        missing.append("lane_d_execution_blocked")
    if not row.get("handoff_id"):
        missing.append("source_handoff_rows_declared")
    if not row.get("planned_result_pack_root"):
        missing.append("candidate_profile_materialization_plan_declared")
        missing.append("candidate_effective_inputs_plan_declared")
        missing.append("candidate_replay_manifest_plan_declared")
        missing.append("candidate_result_pack_manifest_plan_declared")
        missing.append("candidate_integrity_report_plan_declared")
        missing.append("candidate_context_catalog_plan_declared")
        missing.append("candidate_label_precondition_plan_declared")

    return tuple(sorted(set(missing)))


def build_lane_ce_execution_package_requirement_rows(
    optimization_id: str,
    *,
    phase_summary_path: str | Path | None,
    handoff_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[LaneCEExecutionPackageRequirementRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    handoff_rows = _rows_from_payload(_safe_load_json(handoff_rows_path))
    phase_ready = _phase_status(phase_summary_path) == "REPLAY_OPTIMIZATION_PHASE_READY_FOR_LANE_CE_HANDOFF_NO_EXECUTION"

    out: list[LaneCEExecutionPackageRequirementRow] = []
    for idx, row in enumerate(handoff_rows[:max_rows], start=1):
        missing = _missing_requirements(row, phase_ready=phase_ready)

        if missing:
            status = PACKAGE_ROW_STATUS_BLOCKED_HANDOFF_NOT_READY
            remarks = "Execution package requirement row blocked because one or more prerequisite requirements are missing."
        else:
            status = PACKAGE_ROW_STATUS_REQUIRED_NO_EXECUTION
            remarks = (
                "Execution package requirements frozen. Lane D remains no-execution; "
                "future execution/materialization package must be Lane C/E-owned."
            )

        out.append(
            LaneCEExecutionPackageRequirementRow(
                optimization_id=optimization_id,
                package_requirement_id=f"EXECPKGREQ_{idx:06d}",
                handoff_id=str(row.get("handoff_id")) if row.get("handoff_id") is not None else None,
                candidate_id=str(row.get("candidate_id")) if row.get("candidate_id") is not None else None,
                candidate_fingerprint=str(row.get("candidate_fingerprint")) if row.get("candidate_fingerprint") is not None else None,
                planned_result_pack_root=str(row.get("planned_result_pack_root")) if row.get("planned_result_pack_root") is not None else None,
                recommended_owner=str(row.get("recommended_owner")) if row.get("recommended_owner") is not None else None,
                required_execution_owner_options=str(row.get("handoff_target_owner_options") or "Lane C replay runner / staging compatibility owner | Lane E replay-data durable execution / artifact audit owner"),
                package_requirements=",".join(EXECUTION_PACKAGE_REQUIREMENTS),
                package_requirement_count=len(EXECUTION_PACKAGE_REQUIREMENTS),
                missing_package_requirements=",".join(missing),
                missing_package_requirement_count=len(missing),
                package_row_status=status,
                lane_d_execution_allowed=False,
                lane_c_or_e_execution_required=True,
                replay_execution_allowed_in_lane_d=False,
                replay_execution_performed=False,
                result_pack_creation_allowed_in_lane_d=False,
                result_pack_created=False,
                artifact_file_creation_allowed_in_lane_d=False,
                candidate_context_attached=False,
                candidate_trade_matching_allowed=False,
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


def write_lane_ce_execution_package_requirement(
    optimization_id: str,
    output_dir: str | Path,
    *,
    phase_summary_path: str | Path | None,
    handoff_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> LaneCEExecutionPackageRequirementBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    phase_ready = _phase_status(phase_summary_path) == "REPLAY_OPTIMIZATION_PHASE_READY_FOR_LANE_CE_HANDOFF_NO_EXECUTION"
    handoff_rows = _rows_from_payload(_safe_load_json(handoff_rows_path))
    package_rows = build_lane_ce_execution_package_requirement_rows(
        optimization_id,
        phase_summary_path=phase_summary_path,
        handoff_rows_path=handoff_rows_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in package_rows]

    ready_count = sum(1 for row in package_rows if row.package_row_status == PACKAGE_ROW_STATUS_REQUIRED_NO_EXECUTION)
    blocked_count = len(package_rows) - ready_count
    missing_count = sum(1 for row in package_rows if row.missing_package_requirement_count > 0)

    if not _safe_load_json(phase_summary_path):
        status = PACKAGE_STATUS_BLOCKED_NO_PHASE_GATE
    elif not phase_ready:
        status = PACKAGE_STATUS_BLOCKED_PHASE_GATE_NOT_READY
    elif not handoff_rows:
        status = PACKAGE_STATUS_BLOCKED_NO_HANDOFF_ROWS
    else:
        status = PACKAGE_STATUS_READY_NO_EXECUTION

    schema_path = out / "42_lane_ce_execution_package_requirement_schema.json"
    rows_json_path = out / "42_lane_ce_execution_package_requirement_rows.json"
    rows_csv_path = out / "42_lane_ce_execution_package_requirement_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    safety = {
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed": False,
        "result_pack_created": False,
        "artifact_file_creation_allowed": False,
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

    schema = {
        "schema_name": "MME-ScalpX Replay Optimization Lane C/E Execution Package Requirement",
        "contract_version": LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_CONTRACT_VERSION,
        "accepted_for": LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_ACCEPTED_FOR,
        "columns": list(PACKAGE_COLUMNS),
        "execution_package_requirements": list(EXECUTION_PACKAGE_REQUIREMENTS),
        "package_policy": {
            "d39_is_requirement_only": True,
            "lane_d_may_define_execution_package_requirements_but_not_execute": True,
            "future_execution_owner_must_be_lane_c_or_lane_e_compatible": True,
            "label_binding_still_blocked_until_verified_candidate_result_packs": True,
            "replay_execution_allowed_in_d39": False,
            "result_pack_creation_allowed_in_d39": False,
            "artifact_file_creation_allowed_in_d39": False,
            "candidate_context_attachment_allowed_in_d39": False,
            "candidate_trade_matching_allowed_in_d39": False,
            "future_lane_c_or_e_execution_package_required": True
        },
        "safety": safety,
    }
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Lane C/E Execution Package Requirement Rows",
        "contract_version": LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_CONTRACT_VERSION,
        "accepted_for": LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "phase_summary_path": str(phase_summary_path) if phase_summary_path else None,
        "handoff_rows_path": str(handoff_rows_path) if handoff_rows_path else None,
        "package_status": status,
        "handoff_row_count": len(handoff_rows),
        "package_row_count": len(package_rows),
        "package_ready_count": ready_count,
        "blocked_row_count": blocked_count,
        "missing_package_requirement_row_count": missing_count,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, PACKAGE_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_CONTRACT_VERSION,
        "accepted_for": LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_ACCEPTED_FOR,
        "package_status": status,
        "handoff_row_count": len(handoff_rows),
        "package_row_count": len(package_rows),
        "package_ready_count": ready_count,
        "blocked_row_count": blocked_count,
        "missing_package_requirement_row_count": missing_count,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed": False,
        "result_pack_created": False,
        "artifact_file_creation_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D39 freezes Lane C/E execution-package requirements only. No execution or materialization.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return LaneCEExecutionPackageRequirementBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_CONTRACT_VERSION,
        accepted_for=LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_ACCEPTED_FOR,
        phase_summary_path=str(phase_summary_path) if phase_summary_path else None,
        handoff_rows_path=str(handoff_rows_path) if handoff_rows_path else None,
        package_schema_path=schema_path.as_posix(),
        package_rows_json_path=rows_json_path.as_posix(),
        package_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        handoff_row_count=len(handoff_rows),
        package_row_count=len(package_rows),
        package_ready_count=ready_count,
        blocked_row_count=blocked_count,
        missing_package_requirement_row_count=missing_count,
        package_status=status,
    )


__all__ = (
    "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_CONTRACT_VERSION",
    "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_ACCEPTED_FOR",
    "PACKAGE_STATUS_READY_NO_EXECUTION",
    "PACKAGE_STATUS_BLOCKED_NO_PHASE_GATE",
    "PACKAGE_STATUS_BLOCKED_PHASE_GATE_NOT_READY",
    "PACKAGE_STATUS_BLOCKED_NO_HANDOFF_ROWS",
    "PACKAGE_ROW_STATUS_REQUIRED_NO_EXECUTION",
    "PACKAGE_ROW_STATUS_BLOCKED_HANDOFF_NOT_READY",
    "EXECUTION_PACKAGE_REQUIREMENTS",
    "PACKAGE_COLUMNS",
    "LaneCEExecutionPackageRequirementRow",
    "LaneCEExecutionPackageRequirementBuildResult",
    "build_lane_ce_execution_package_requirement_rows",
    "write_lane_ce_execution_package_requirement",
)
