"""Lane D D40 replay optimization freeze summary.

This module freezes the completed Lane D replay_optimization contract phase.

D40 is freeze-summary only. It does not execute replay, create result packs,
write candidate artifacts, attach candidate context, perform matching, bind
labels, calculate PnL, train/predict models, call brokers, write live Redis,
mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

LANE_D_FREEZE_SUMMARY_CONTRACT_VERSION = "replay_optimization_d40_lane_d_freeze_summary_contract_v1"
LANE_D_FREEZE_SUMMARY_ACCEPTED_FOR = "LANE_D_FREEZE_SUMMARY_NO_EXECUTION"

FREEZE_STATUS_COMPLETE_NO_EXECUTION = "LANE_D_REPLAY_OPTIMIZATION_FREEZE_COMPLETE_NO_EXECUTION"
FREEZE_STATUS_BLOCKED_MISSING_REQUIRED_PROOF = "BLOCKED_MISSING_REQUIRED_PROOF"
FREEZE_STATUS_BLOCKED_REQUIRED_PROOF_NOT_PASS = "BLOCKED_REQUIRED_PROOF_NOT_PASS"
FREEZE_STATUS_BLOCKED_REQUIRED_STATUS_MISMATCH = "BLOCKED_REQUIRED_STATUS_MISMATCH"
FREEZE_STATUS_BLOCKED_UNSAFE_FLAG = "BLOCKED_UNSAFE_FLAG"

FREEZE_ROW_STATUS_PASS = "PASS"
FREEZE_ROW_STATUS_MISSING = "MISSING"
FREEZE_ROW_STATUS_NOT_PASS = "NOT_PASS"
FREEZE_ROW_STATUS_STATUS_MISMATCH = "STATUS_MISMATCH"
FREEZE_ROW_STATUS_UNSAFE = "UNSAFE"

REQUIRED_FREEZE_PROOFS = (
    ("D31", "proof_lane_d_d31_candidate_replay_binding_requirement_latest.json", "requirement_status", "CANDIDATE_REPLAY_BINDING_REQUIRED_BEFORE_LABELS"),
    ("D32", "proof_lane_d_d32_candidate_replay_binding_plan_latest.json", "plan_status", "CANDIDATE_REPLAY_BINDING_PLAN_SCHEMA_READY_NO_EXECUTION"),
    ("D33", "proof_lane_d_d33_candidate_replay_binding_plan_validator_latest.json", "validation_status", "CANDIDATE_REPLAY_BINDING_PLAN_VALIDATION_PASS_NO_EXECUTION"),
    ("D34", "proof_lane_d_d34_candidate_replay_materialization_latest.json", "materialization_status", "CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_READY_NO_EXECUTION"),
    ("D35", "proof_lane_d_d35_candidate_replay_materialization_validator_latest.json", "validation_status", "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATION_PASS_NO_EXECUTION"),
    ("D36", "proof_lane_d_d36_candidate_replay_materialization_preflight_latest.json", "preflight_status", "CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_PASS_NO_EXECUTION"),
    ("D37", "proof_lane_d_d37_lane_ce_handoff_latest.json", "handoff_status", "LANE_CE_HANDOFF_READY_NO_EXECUTION"),
    ("D38", "proof_lane_d_d38_phase_gate_summary_latest.json", "phase_status", "REPLAY_OPTIMIZATION_PHASE_READY_FOR_LANE_CE_HANDOFF_NO_EXECUTION"),
    ("D39", "proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json", "package_status", "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_READY_NO_EXECUTION"),
)

MUST_BE_FALSE_SAFETY_KEYS = (
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed",
    "result_pack_created",
    "artifact_file_creation_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
    "runtime_services_started",
    "strategy_doctrine_changed",
    "replay_engine_changed",
    "production_profit_claim_allowed",
)

FREEZE_COLUMNS = (
    "optimization_id",
    "freeze_row_id",
    "batch",
    "proof_path",
    "proof_present",
    "proof_verdict",
    "status_key",
    "expected_status",
    "observed_status",
    "status_match",
    "safety_ok",
    "unsafe_keys",
    "freeze_row_status",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class LaneDFreezeSummaryRow:
    optimization_id: str
    freeze_row_id: str
    batch: str
    proof_path: str
    proof_present: bool
    proof_verdict: str | None
    status_key: str
    expected_status: str
    observed_status: str | None
    status_match: bool
    safety_ok: bool
    unsafe_keys: str
    freeze_row_status: str
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class LaneDFreezeSummaryBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    freeze_schema_path: str
    freeze_summary_path: str
    freeze_rows_json_path: str
    freeze_rows_csv_path: str
    optimizer_verdict_path: str
    required_proof_count: int
    passed_proof_count: int
    missing_proof_count: int
    failed_proof_count: int
    unsafe_proof_count: int
    candidate_count: int
    package_ready_count: int
    freeze_status: str
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
        raise ValueError(f"D40 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _proof_path(filename: str) -> Path:
    return Path("run/proofs") / filename


def _unsafe_keys(payload: Mapping[str, Any]) -> tuple[str, ...]:
    safety = payload.get("safety")
    if not isinstance(safety, dict):
        return tuple()
    bad: list[str] = []
    for key in MUST_BE_FALSE_SAFETY_KEYS:
        if key in safety and safety.get(key) is not False:
            bad.append(key)
    return tuple(bad)


def build_lane_d_freeze_rows(optimization_id: str) -> tuple[LaneDFreezeSummaryRow, ...]:
    rows: list[LaneDFreezeSummaryRow] = []

    for idx, (batch, proof_file, status_key, expected_status) in enumerate(REQUIRED_FREEZE_PROOFS, start=1):
        path = _proof_path(proof_file)
        payload = _safe_load_json(path)
        proof_present = isinstance(payload, dict)
        proof_verdict = str(payload.get("verdict")) if proof_present and payload.get("verdict") is not None else None
        observed_status = str(payload.get(status_key)) if proof_present and payload.get(status_key) is not None else None
        status_match = observed_status == expected_status
        unsafe = _unsafe_keys(payload) if isinstance(payload, dict) else tuple()
        safety_ok = not unsafe

        if not proof_present:
            row_status = FREEZE_ROW_STATUS_MISSING
            remarks = "Required latest proof is missing or unreadable."
        elif proof_verdict != "PASS":
            row_status = FREEZE_ROW_STATUS_NOT_PASS
            remarks = "Required latest proof did not report PASS."
        elif not status_match:
            row_status = FREEZE_ROW_STATUS_STATUS_MISMATCH
            remarks = "Required latest proof status does not match expected freeze status."
        elif not safety_ok:
            row_status = FREEZE_ROW_STATUS_UNSAFE
            remarks = "Required latest proof has unsafe safety flags."
        else:
            row_status = FREEZE_ROW_STATUS_PASS
            remarks = "Required freeze proof passed."

        rows.append(
            LaneDFreezeSummaryRow(
                optimization_id=optimization_id,
                freeze_row_id=f"FREEZE_{idx:04d}",
                batch=batch,
                proof_path=path.as_posix(),
                proof_present=proof_present,
                proof_verdict=proof_verdict,
                status_key=status_key,
                expected_status=expected_status,
                observed_status=observed_status,
                status_match=status_match,
                safety_ok=safety_ok,
                unsafe_keys=",".join(unsafe),
                freeze_row_status=row_status,
                remarks=remarks,
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


def write_lane_d_freeze_summary(
    optimization_id: str,
    output_dir: str | Path,
) -> LaneDFreezeSummaryBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_lane_d_freeze_rows(optimization_id)
    row_dicts = [asdict(row) for row in rows]

    missing = sum(1 for row in rows if row.freeze_row_status == FREEZE_ROW_STATUS_MISSING)
    not_pass = sum(1 for row in rows if row.freeze_row_status == FREEZE_ROW_STATUS_NOT_PASS)
    mismatch = sum(1 for row in rows if row.freeze_row_status == FREEZE_ROW_STATUS_STATUS_MISMATCH)
    unsafe = sum(1 for row in rows if row.freeze_row_status == FREEZE_ROW_STATUS_UNSAFE)
    passed = sum(1 for row in rows if row.freeze_row_status == FREEZE_ROW_STATUS_PASS)
    failed = not_pass + mismatch

    d32 = _safe_load_json(_proof_path("proof_lane_d_d32_candidate_replay_binding_plan_latest.json"))
    d39 = _safe_load_json(_proof_path("proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json"))

    candidate_count = int(d32.get("candidate_count") or 0) if isinstance(d32, dict) else 0
    package_ready_count = int(d39.get("package_ready_count") or 0) if isinstance(d39, dict) else 0

    if missing:
        status = FREEZE_STATUS_BLOCKED_MISSING_REQUIRED_PROOF
    elif failed:
        status = FREEZE_STATUS_BLOCKED_REQUIRED_STATUS_MISMATCH if mismatch else FREEZE_STATUS_BLOCKED_REQUIRED_PROOF_NOT_PASS
    elif unsafe:
        status = FREEZE_STATUS_BLOCKED_UNSAFE_FLAG
    else:
        status = FREEZE_STATUS_COMPLETE_NO_EXECUTION

    schema_path = out / "43_lane_d_freeze_summary_schema.json"
    summary_path = out / "43_lane_d_freeze_summary.json"
    rows_json_path = out / "43_lane_d_freeze_rows.json"
    rows_csv_path = out / "43_lane_d_freeze_rows.csv"
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
        "schema_name": "MME-ScalpX Replay Optimization Lane D Freeze Summary",
        "contract_version": LANE_D_FREEZE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": LANE_D_FREEZE_SUMMARY_ACCEPTED_FOR,
        "columns": list(FREEZE_COLUMNS),
        "required_freeze_proofs": [
            {
                "batch": batch,
                "proof_file": proof_file,
                "status_key": status_key,
                "expected_status": expected_status
            }
            for batch, proof_file, status_key, expected_status in REQUIRED_FREEZE_PROOFS
        ],
        "freeze_policy": {
            "d40_is_freeze_summary_only": True,
            "lane_d_complete_up_to_execution_package_requirement": True,
            "lane_d_execution_allowed": False,
            "future_execution_owner_must_be_lane_c_or_lane_e_compatible": True,
            "label_binding_still_blocked_until_verified_candidate_result_packs": True,
            "production_profit_claim_allowed": False
        },
        "safety": safety,
    }
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    summary = {
        "schema_name": "MME-ScalpX Replay Optimization Lane D Freeze Summary",
        "contract_version": LANE_D_FREEZE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": LANE_D_FREEZE_SUMMARY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "freeze_status": status,
        "required_proof_count": len(rows),
        "passed_proof_count": passed,
        "missing_proof_count": missing,
        "failed_proof_count": failed,
        "unsafe_proof_count": unsafe,
        "candidate_count": candidate_count,
        "package_ready_count": package_ready_count,
        "lane_d_scope_completed": [
            "candidate replay binding requirement",
            "candidate replay binding plan",
            "binding plan validation",
            "candidate replay materialization contract",
            "materialization validation",
            "materialization preflight",
            "Lane C/E handoff",
            "phase gate summary",
            "Lane C/E execution package requirement"
        ],
        "lane_d_stop_point": "Lane D stops here. Future replay/result-pack materialization must be Lane C/E-owned.",
        "next_required_owner": "Lane C or Lane E compatible replay/materialization flow",
        "recommended_owner": "Lane E replay-data durable execution / artifact audit owner unless Lane C runner behavior changes are required",
        "important_limitation": "D40 does not execute replay, create artifacts/result packs, attach context, match trades, bind labels, calculate PnL, train/predict, or approve optimization.",
        "rows": row_dicts,
        "safety": safety,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Lane D Freeze Rows",
        "contract_version": LANE_D_FREEZE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": LANE_D_FREEZE_SUMMARY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "freeze_status": status,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, FREEZE_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": LANE_D_FREEZE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": LANE_D_FREEZE_SUMMARY_ACCEPTED_FOR,
        "freeze_status": status,
        "required_proof_count": len(rows),
        "passed_proof_count": passed,
        "missing_proof_count": missing,
        "failed_proof_count": failed,
        "unsafe_proof_count": unsafe,
        "candidate_count": candidate_count,
        "package_ready_count": package_ready_count,
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
        "remarks": "Lane D freeze complete if all required proofs pass. Future execution/materialization must be Lane C/E-owned.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return LaneDFreezeSummaryBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=LANE_D_FREEZE_SUMMARY_CONTRACT_VERSION,
        accepted_for=LANE_D_FREEZE_SUMMARY_ACCEPTED_FOR,
        freeze_schema_path=schema_path.as_posix(),
        freeze_summary_path=summary_path.as_posix(),
        freeze_rows_json_path=rows_json_path.as_posix(),
        freeze_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        required_proof_count=len(rows),
        passed_proof_count=passed,
        missing_proof_count=missing,
        failed_proof_count=failed,
        unsafe_proof_count=unsafe,
        candidate_count=candidate_count,
        package_ready_count=package_ready_count,
        freeze_status=status,
    )


__all__ = (
    "LANE_D_FREEZE_SUMMARY_CONTRACT_VERSION",
    "LANE_D_FREEZE_SUMMARY_ACCEPTED_FOR",
    "FREEZE_STATUS_COMPLETE_NO_EXECUTION",
    "FREEZE_STATUS_BLOCKED_MISSING_REQUIRED_PROOF",
    "FREEZE_STATUS_BLOCKED_REQUIRED_PROOF_NOT_PASS",
    "FREEZE_STATUS_BLOCKED_REQUIRED_STATUS_MISMATCH",
    "FREEZE_STATUS_BLOCKED_UNSAFE_FLAG",
    "FREEZE_ROW_STATUS_PASS",
    "FREEZE_ROW_STATUS_MISSING",
    "FREEZE_ROW_STATUS_NOT_PASS",
    "FREEZE_ROW_STATUS_STATUS_MISMATCH",
    "FREEZE_ROW_STATUS_UNSAFE",
    "REQUIRED_FREEZE_PROOFS",
    "MUST_BE_FALSE_SAFETY_KEYS",
    "FREEZE_COLUMNS",
    "LaneDFreezeSummaryRow",
    "LaneDFreezeSummaryBuildResult",
    "build_lane_d_freeze_rows",
    "write_lane_d_freeze_summary",
)
