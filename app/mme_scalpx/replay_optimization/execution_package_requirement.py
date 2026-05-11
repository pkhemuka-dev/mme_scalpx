from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PACKAGE_STATUS_READY_NO_EXECUTION = "PACKAGE_REQUIREMENT_READY_NO_EXECUTION"
PHASE_STATUS_READY = "REPLAY_OPTIMIZATION_PHASE_READY_FOR_LANE_CE_HANDOFF_NO_EXECUTION"

ROW_COLUMNS = (
    "package_requirement_id",
    "candidate_id",
    "candidate_fingerprint",
    "handoff_id",
    "planned_result_pack_root",
    "planned_result_pack_manifest_path",
    "planned_run_manifest_required",
    "planned_metrics_summary_required",
    "planned_trade_log_required",
    "planned_candidate_audit_required",
    "planned_decision_trace_required",
    "planned_integrity_report_required",
    "candidate_profile_required",
    "candidate_context_catalog_required",
    "replay_execution_owner",
    "recommended_owner",
    "lane_c_or_e_execution_required",
    "lane_d_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "model_prediction_performed",
    "package_row_status",
    "remarks",
)


@dataclass(frozen=True)
class ExecutionPackageRequirementResult:
    optimization_id: str
    artifact_root: str
    schema_path: str
    summary_path: str
    rows_json_path: str
    rows_csv_path: str
    optimizer_verdict_path: str
    candidate_count: int
    package_requirement_row_count: int
    package_requirement_ready_count: int
    source_handoff_row_count: int
    phase_status: str


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _resolve_path(path_value: str | None, root: Path) -> Path:
    if not path_value:
        raise FileNotFoundError("empty path cannot be resolved")

    candidate = Path(path_value)
    if candidate.exists():
        return candidate

    if candidate.is_absolute():
        marker = "mme_scalpx/"
        text = candidate.as_posix()
        if marker in text:
            rel = text.split(marker, 1)[1]
            fallback = root / rel
            if fallback.exists():
                return fallback

    fallback = root / path_value
    if fallback.exists():
        return fallback

    raise FileNotFoundError(f"unable to resolve required path: {path_value}")


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(row) for row in payload]
    if isinstance(payload, dict):
        for key in ("rows", "handoff_rows", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [dict(row) for row in value]
    raise ValueError("payload does not contain a row list")


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _require_prior_pass(proof_path: Path, expected_batch_prefix: str) -> dict[str, Any]:
    proof = _load_json(proof_path)
    if proof.get("verdict") != "PASS":
        raise ValueError(f"required proof is not PASS: {proof_path}")
    batch = str(proof.get("batch", ""))
    if not batch.startswith(expected_batch_prefix):
        raise ValueError(f"unexpected proof batch for {proof_path}: {batch}")
    return proof


def build_execution_package_requirement_rows(
    optimization_id: str,
    handoff_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for idx, source in enumerate(handoff_rows, start=1):
        candidate_id = str(source.get("candidate_id") or "").strip()
        fingerprint = str(source.get("candidate_fingerprint") or "").strip()
        planned_root = str(source.get("planned_result_pack_root") or "").strip()
        handoff_id = str(source.get("handoff_id") or "").strip()

        if not candidate_id:
            raise ValueError(f"handoff row {idx} missing candidate_id")
        if not fingerprint:
            raise ValueError(f"handoff row {idx} missing candidate_fingerprint")
        if not planned_root:
            raise ValueError(f"handoff row {idx} missing planned_result_pack_root")
        if source.get("handoff_ready") is not True:
            raise ValueError(f"handoff row {idx} is not handoff_ready=true")
        if source.get("lane_d_execution_allowed") is not False:
            raise ValueError(f"handoff row {idx} violates lane_d_execution_allowed=false")
        if source.get("replay_execution_performed") is not False:
            raise ValueError(f"handoff row {idx} violates replay_execution_performed=false")
        if source.get("result_pack_created") is not False:
            raise ValueError(f"handoff row {idx} violates result_pack_created=false")
        if source.get("label_binding_allowed") is not False:
            raise ValueError(f"handoff row {idx} violates label_binding_allowed=false")
        if source.get("labels_bound") is not False:
            raise ValueError(f"handoff row {idx} violates labels_bound=false")

        recommended_owner = str(source.get("recommended_owner") or "").strip()
        if not recommended_owner:
            recommended_owner = "Lane E replay-data durable execution / artifact audit owner"

        rows.append({
            "package_requirement_id": f"EXECPKGREQ_{idx:06d}",
            "candidate_id": candidate_id,
            "candidate_fingerprint": fingerprint,
            "handoff_id": handoff_id,
            "planned_result_pack_root": planned_root,
            "planned_result_pack_manifest_path": f"{planned_root}/result_pack_manifest.json",
            "planned_run_manifest_required": True,
            "planned_metrics_summary_required": True,
            "planned_trade_log_required": True,
            "planned_candidate_audit_required": True,
            "planned_decision_trace_required": True,
            "planned_integrity_report_required": True,
            "candidate_profile_required": True,
            "candidate_context_catalog_required": True,
            "replay_execution_owner": "Lane C/E only",
            "recommended_owner": recommended_owner,
            "lane_c_or_e_execution_required": True,
            "lane_d_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_created": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "package_row_status": PACKAGE_STATUS_READY_NO_EXECUTION,
            "remarks": "Requirement row only. Lane D1 does not execute replay or create result packs. Candidate-specific verified result pack must be produced by Lane C/E before labels, PnL, leaderboard, or ML.",
        })

    return rows


def write_execution_package_requirements(
    optimization_id: str,
    artifact_root: Path,
    root: Path | None = None,
) -> ExecutionPackageRequirementResult:
    root = (root or Path.cwd()).resolve()
    artifact_root = artifact_root.resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    d32_proof = _require_prior_pass(root / "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json", "LANE-D-D32")
    d37_proof = _require_prior_pass(root / "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json", "LANE-D-D37")
    d38_proof = _require_prior_pass(root / "run/proofs/proof_lane_d_d38_phase_gate_summary_latest.json", "LANE-D-D38")

    if d38_proof.get("phase_status") != PHASE_STATUS_READY:
        raise ValueError(f"D38 phase status is not ready: {d38_proof.get('phase_status')}")
    if d38_proof.get("candidate_count") != 810:
        raise ValueError(f"D38 expected candidate_count=810, got {d38_proof.get('candidate_count')}")
    if d38_proof.get("handoff_ready_count") != 810:
        raise ValueError(f"D38 expected handoff_ready_count=810, got {d38_proof.get('handoff_ready_count')}")
    if d37_proof.get("handoff_row_count") != 810:
        raise ValueError(f"D37 expected handoff_row_count=810, got {d37_proof.get('handoff_row_count')}")
    if d37_proof.get("handoff_ready_count") != 810:
        raise ValueError(f"D37 expected handoff_ready_count=810, got {d37_proof.get('handoff_ready_count')}")
    if d32_proof.get("candidate_count") != 810:
        raise ValueError(f"D32 expected candidate_count=810, got {d32_proof.get('candidate_count')}")

    handoff_rows_path = _resolve_path(str(d37_proof.get("handoff_rows_json_path") or ""), root)
    handoff_payload = _load_json(handoff_rows_path)
    handoff_rows = _extract_rows(handoff_payload)

    if len(handoff_rows) != 810:
        raise ValueError(f"expected 810 handoff rows, got {len(handoff_rows)}")

    rows = build_execution_package_requirement_rows(optimization_id, handoff_rows)
    ready_count = sum(1 for row in rows if row.get("package_row_status") == PACKAGE_STATUS_READY_NO_EXECUTION)

    schema = {
        "contract_version": "replay_optimization_d39_lane_ce_execution_package_requirement_contract_v1",
        "optimization_id": optimization_id,
        "row_columns": list(ROW_COLUMNS),
        "allowed_statuses": [PACKAGE_STATUS_READY_NO_EXECUTION],
        "source_proofs": {
            "d32": "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json",
            "d37": "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json",
            "d38": "run/proofs/proof_lane_d_d38_phase_gate_summary_latest.json"
        },
        "safety": {
            "lane_d_execution_allowed": False,
            "lane_c_or_e_execution_required": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_creation_allowed_in_lane_d": False,
            "result_pack_created": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False
        }
    }

    summary = {
        "accepted_for": "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION",
        "contract_version": "replay_optimization_d39_lane_ce_execution_package_requirement_contract_v1",
        "optimization_id": optimization_id,
        "candidate_count": len(rows),
        "source_handoff_row_count": len(handoff_rows),
        "package_requirement_row_count": len(rows),
        "package_requirement_ready_count": ready_count,
        "full_universe_preserved": len(rows) == 810,
        "phase_status": PHASE_STATUS_READY,
        "requirement_status": "LANE_CE_EXECUTION_PACKAGE_REQUIREMENTS_READY_NO_EXECUTION",
        "recommended_owner": "Lane E replay-data durable execution / artifact audit owner unless Lane C runner/staging behavior changes are required",
        "important_limitation": "D39 is a requirement package only. It does not execute replay, create real result packs, bind labels, calculate PnL, train models, predict, or approve production profitability.",
        "safety": {
            "lane_d_execution_allowed": False,
            "lane_c_or_e_execution_required": True,
            "replay_execution_allowed": False,
            "replay_execution_performed": False,
            "result_pack_creation_allowed_in_lane_d": False,
            "result_pack_created": False,
            "artifact_file_creation_allowed_in_lane_d": False,
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
            "runtime_services_started": False,
            "strategy_doctrine_changed": False,
            "replay_engine_changed": False,
            "production_profit_claim_allowed": False
        },
        "next_recommended_batch": "LANE-D1-D40_EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_NO_EXECUTION"
    }

    verdict = {
        "optimization_id": optimization_id,
        "verdict": "PASS",
        "accepted_for": "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION",
        "candidate_count": len(rows),
        "package_requirement_ready_count": ready_count,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "next_recommended_batch": "LANE-D1-D40_EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_NO_EXECUTION"
    }

    schema_path = artifact_root / "42_lane_ce_execution_package_requirement_schema.json"
    summary_path = artifact_root / "42_lane_ce_execution_package_requirement_summary.json"
    rows_json_path = artifact_root / "42_lane_ce_execution_package_requirement_rows.json"
    rows_csv_path = artifact_root / "42_lane_ce_execution_package_requirement_rows.csv"
    optimizer_verdict_path = artifact_root / "09_optimizer_verdict.json"

    _write_json(schema_path, schema)
    _write_json(summary_path, summary)
    _write_json(rows_json_path, {"rows": rows})
    _write_csv(rows_csv_path, rows, ROW_COLUMNS)
    _write_json(optimizer_verdict_path, verdict)

    return ExecutionPackageRequirementResult(
        optimization_id=optimization_id,
        artifact_root=artifact_root.as_posix(),
        schema_path=schema_path.as_posix(),
        summary_path=summary_path.as_posix(),
        rows_json_path=rows_json_path.as_posix(),
        rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=optimizer_verdict_path.as_posix(),
        candidate_count=len(rows),
        package_requirement_row_count=len(rows),
        package_requirement_ready_count=ready_count,
        source_handoff_row_count=len(handoff_rows),
        phase_status=PHASE_STATUS_READY,
    )


__all__ = [
    "PACKAGE_STATUS_READY_NO_EXECUTION",
    "PHASE_STATUS_READY",
    "ROW_COLUMNS",
    "ExecutionPackageRequirementResult",
    "build_execution_package_requirement_rows",
    "write_execution_package_requirements",
]
