"""Lane D D38 replay optimization phase-gate summary.

This module freezes the current Lane D replay-optimization phase gate after
candidate replay-binding planning, validation, materialization contract,
preflight, and Lane C/E handoff readiness.

D38 is summary/phase-gate only. It does not execute replay, create result packs,
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

PHASE_GATE_SUMMARY_CONTRACT_VERSION = "replay_optimization_d38_phase_gate_summary_contract_v1"
PHASE_GATE_SUMMARY_ACCEPTED_FOR = "REPLAY_OPTIMIZATION_PHASE_GATE_SUMMARY_NO_EXECUTION"

PHASE_STATUS_READY_FOR_LANE_CE_HANDOFF = "REPLAY_OPTIMIZATION_PHASE_READY_FOR_LANE_CE_HANDOFF_NO_EXECUTION"
PHASE_STATUS_BLOCKED_MISSING_REQUIRED_PROOF = "BLOCKED_MISSING_REQUIRED_LANE_D_PROOF"
PHASE_STATUS_BLOCKED_FAILED_REQUIRED_GATE = "BLOCKED_FAILED_REQUIRED_LANE_D_GATE"
PHASE_STATUS_BLOCKED_UNSAFE_FLAG = "BLOCKED_UNSAFE_FLAG"

REQUIRED_GATE_PROOFS = (
    ("D31", "proof_lane_d_d31_candidate_replay_binding_requirement_latest.json", "requirement_status", "CANDIDATE_REPLAY_BINDING_REQUIRED_BEFORE_LABELS"),
    ("D32", "proof_lane_d_d32_candidate_replay_binding_plan_latest.json", "plan_status", "CANDIDATE_REPLAY_BINDING_PLAN_SCHEMA_READY_NO_EXECUTION"),
    ("D33", "proof_lane_d_d33_candidate_replay_binding_plan_validator_latest.json", "validation_status", "CANDIDATE_REPLAY_BINDING_PLAN_VALIDATION_PASS_NO_EXECUTION"),
    ("D34", "proof_lane_d_d34_candidate_replay_materialization_latest.json", "materialization_status", "CANDIDATE_REPLAY_MATERIALIZATION_CONTRACT_READY_NO_EXECUTION"),
    ("D35", "proof_lane_d_d35_candidate_replay_materialization_validator_latest.json", "validation_status", "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATION_PASS_NO_EXECUTION"),
    ("D36", "proof_lane_d_d36_candidate_replay_materialization_preflight_latest.json", "preflight_status", "CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_PASS_NO_EXECUTION"),
    ("D37", "proof_lane_d_d37_lane_ce_handoff_latest.json", "handoff_status", "LANE_CE_HANDOFF_READY_NO_EXECUTION"),
)

MUST_BE_FALSE_SAFETY_KEYS = (
    "replay_execution_performed",
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

PHASE_GATE_COLUMNS = (
    "optimization_id",
    "gate_id",
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
    "gate_row_status",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class PhaseGateSummaryRow:
    optimization_id: str
    gate_id: str
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
    gate_row_status: str
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class PhaseGateSummaryBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    phase_schema_path: str
    phase_summary_path: str
    phase_rows_json_path: str
    phase_rows_csv_path: str
    optimizer_verdict_path: str
    required_gate_count: int
    passed_gate_count: int
    missing_gate_count: int
    failed_gate_count: int
    unsafe_gate_count: int
    candidate_count: int
    handoff_row_count: int
    handoff_ready_count: int
    phase_status: str
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
        raise ValueError(f"D38 output must stay under {OUTPUT_ROOT}: {output_dir}")
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


def build_phase_gate_rows(optimization_id: str) -> tuple[PhaseGateSummaryRow, ...]:
    rows: list[PhaseGateSummaryRow] = []
    for idx, (batch, proof_file, status_key, expected_status) in enumerate(REQUIRED_GATE_PROOFS, start=1):
        path = _proof_path(proof_file)
        payload = _safe_load_json(path)
        proof_present = isinstance(payload, dict)
        proof_verdict = str(payload.get("verdict")) if proof_present and payload.get("verdict") is not None else None
        observed_status = str(payload.get(status_key)) if proof_present and payload.get(status_key) is not None else None
        status_match = observed_status == expected_status
        unsafe = _unsafe_keys(payload) if isinstance(payload, dict) else tuple()
        safety_ok = not unsafe

        if not proof_present:
            gate_status = "MISSING_PROOF"
            remarks = "Required latest proof is missing or unreadable."
        elif proof_verdict != "PASS":
            gate_status = "FAILED_VERDICT"
            remarks = "Required proof did not report PASS."
        elif not status_match:
            gate_status = "FAILED_STATUS"
            remarks = "Required proof status does not match expected gate status."
        elif not safety_ok:
            gate_status = "FAILED_SAFETY"
            remarks = "Required proof has unsafe safety flags."
        else:
            gate_status = "PASS"
            remarks = "Required phase gate proof passed."

        rows.append(
            PhaseGateSummaryRow(
                optimization_id=optimization_id,
                gate_id=f"GATE_{idx:04d}",
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
                gate_row_status=gate_status,
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


def write_phase_gate_summary(
    optimization_id: str,
    output_dir: str | Path,
) -> PhaseGateSummaryBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_phase_gate_rows(optimization_id)
    row_dicts = [asdict(row) for row in rows]

    missing = sum(1 for row in rows if row.gate_row_status == "MISSING_PROOF")
    failed = sum(1 for row in rows if row.gate_row_status in {"FAILED_VERDICT", "FAILED_STATUS"})
    unsafe = sum(1 for row in rows if row.gate_row_status == "FAILED_SAFETY")
    passed = sum(1 for row in rows if row.gate_row_status == "PASS")

    d32 = _safe_load_json(_proof_path("proof_lane_d_d32_candidate_replay_binding_plan_latest.json"))
    d37 = _safe_load_json(_proof_path("proof_lane_d_d37_lane_ce_handoff_latest.json"))

    candidate_count = int(d32.get("candidate_count") or 0) if isinstance(d32, dict) else 0
    handoff_row_count = int(d37.get("handoff_row_count") or 0) if isinstance(d37, dict) else 0
    handoff_ready_count = int(d37.get("handoff_ready_count") or 0) if isinstance(d37, dict) else 0

    if missing:
        status = PHASE_STATUS_BLOCKED_MISSING_REQUIRED_PROOF
    elif failed:
        status = PHASE_STATUS_BLOCKED_FAILED_REQUIRED_GATE
    elif unsafe:
        status = PHASE_STATUS_BLOCKED_UNSAFE_FLAG
    else:
        status = PHASE_STATUS_READY_FOR_LANE_CE_HANDOFF

    schema_path = out / "41_replay_optimization_phase_gate_schema.json"
    summary_path = out / "41_replay_optimization_phase_gate_summary.json"
    rows_json_path = out / "41_replay_optimization_phase_gate_rows.json"
    rows_csv_path = out / "41_replay_optimization_phase_gate_rows.csv"
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
        "schema_name": "MME-ScalpX Replay Optimization Phase Gate Summary",
        "contract_version": PHASE_GATE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": PHASE_GATE_SUMMARY_ACCEPTED_FOR,
        "columns": list(PHASE_GATE_COLUMNS),
        "required_gate_proofs": [
            {
                "batch": batch,
                "proof_file": proof_file,
                "status_key": status_key,
                "expected_status": expected_status
            }
            for batch, proof_file, status_key, expected_status in REQUIRED_GATE_PROOFS
        ],
        "phase_policy": {
            "d38_is_summary_only": True,
            "lane_d_phase_gate_summary_only": True,
            "lane_d_execution_allowed": False,
            "future_execution_owner_must_be_lane_c_or_lane_e_compatible": True,
            "candidate_count_expected_from_d32": True,
            "handoff_readiness_expected_from_d37": True,
            "next_step_must_not_be_lane_d_execution": True
        },
        "safety": safety,
    }
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    summary = {
        "schema_name": "MME-ScalpX Replay Optimization Phase Gate Summary",
        "contract_version": PHASE_GATE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": PHASE_GATE_SUMMARY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "phase_status": status,
        "required_gate_count": len(rows),
        "passed_gate_count": passed,
        "missing_gate_count": missing,
        "failed_gate_count": failed,
        "unsafe_gate_count": unsafe,
        "candidate_count": candidate_count,
        "handoff_row_count": handoff_row_count,
        "handoff_ready_count": handoff_ready_count,
        "next_required_owner": "Lane C or Lane E compatible replay/materialization flow",
        "recommended_owner": "Lane E replay-data durable execution / artifact audit owner unless Lane C runner behavior changes are required",
        "lane_d_limit": "Lane D stops at contract, schema, validator, preflight, and handoff evidence.",
        "important_limitation": "D38 does not execute replay, create artifacts/result packs, attach context, match trades, bind labels, calculate PnL, train/predict, or approve optimization.",
        "rows": row_dicts,
        "safety": safety,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Phase Gate Rows",
        "contract_version": PHASE_GATE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": PHASE_GATE_SUMMARY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "phase_status": status,
        "rows": row_dicts,
        "safety": safety,
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, PHASE_GATE_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": PHASE_GATE_SUMMARY_CONTRACT_VERSION,
        "accepted_for": PHASE_GATE_SUMMARY_ACCEPTED_FOR,
        "phase_status": status,
        "required_gate_count": len(rows),
        "passed_gate_count": passed,
        "missing_gate_count": missing,
        "failed_gate_count": failed,
        "unsafe_gate_count": unsafe,
        "candidate_count": candidate_count,
        "handoff_row_count": handoff_row_count,
        "handoff_ready_count": handoff_ready_count,
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
        "remarks": "D38 freezes Lane D phase-gate summary only. Future execution/materialization must be Lane C/E-owned.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return PhaseGateSummaryBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=PHASE_GATE_SUMMARY_CONTRACT_VERSION,
        accepted_for=PHASE_GATE_SUMMARY_ACCEPTED_FOR,
        phase_schema_path=schema_path.as_posix(),
        phase_summary_path=summary_path.as_posix(),
        phase_rows_json_path=rows_json_path.as_posix(),
        phase_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        required_gate_count=len(rows),
        passed_gate_count=passed,
        missing_gate_count=missing,
        failed_gate_count=failed,
        unsafe_gate_count=unsafe,
        candidate_count=candidate_count,
        handoff_row_count=handoff_row_count,
        handoff_ready_count=handoff_ready_count,
        phase_status=status,
    )


__all__ = (
    "PHASE_GATE_SUMMARY_CONTRACT_VERSION",
    "PHASE_GATE_SUMMARY_ACCEPTED_FOR",
    "PHASE_STATUS_READY_FOR_LANE_CE_HANDOFF",
    "PHASE_STATUS_BLOCKED_MISSING_REQUIRED_PROOF",
    "PHASE_STATUS_BLOCKED_FAILED_REQUIRED_GATE",
    "PHASE_STATUS_BLOCKED_UNSAFE_FLAG",
    "REQUIRED_GATE_PROOFS",
    "MUST_BE_FALSE_SAFETY_KEYS",
    "PHASE_GATE_COLUMNS",
    "PhaseGateSummaryRow",
    "PhaseGateSummaryBuildResult",
    "build_phase_gate_rows",
    "write_phase_gate_summary",
)
