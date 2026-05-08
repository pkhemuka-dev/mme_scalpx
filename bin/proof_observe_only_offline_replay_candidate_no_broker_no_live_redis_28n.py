#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

EXPECTED_CANDIDATE_ARTIFACTS = [
    "00_dataset_candidate_manifest.json",
    "01_source_evidence_catalog.json",
    "02_materialized_file_index.json",
    "03_service_surface_dataset_plan.json",
    "04_no_broker_no_live_redis_boundary.json",
    "05_candidate_readiness.json",
    "06_next_replay_dry_run_contract.json",
]

EXPECTED_INPUT_SURFACES = [
    "provider_runtime",
    "feed_snapshot",
    "feature_payload",
    "family_surfaces",
    "strategy_activation",
    "no_order_sent",
    "live_capture_log",
    "live_stream_inventory",
    "live_hash_inventory",
    "provider_health_snapshot",
    "selected_option_context",
    "dhan_oi_ladder_context_if_available",
]

NO_ENABLEMENT_FIELDS = [
    "starts_services",
    "reads_live_redis",
    "writes_live_redis",
    "calls_broker_api",
    "broker_call_reachable",
    "live_redis_write_reachable",
    "runtime_promotion_reachable",
    "paper_armed_approved",
    "live_trading_approved",
    "execution_arming_created",
    "real_order_sent",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "production_doctrine_changed",
]

def sha256_file(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": type(exc).__name__, "_read_error_text": str(exc), "_path": str(path)}

def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except Exception:
        return str(path)

def file_state(root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    return {
        "path": rel(root, path),
        "present": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256_file(path),
    }

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    target = path.resolve()
    return str(target).startswith(str(replay_root) + "/")

def no_enablement_clean(payload: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    observed = {}
    clean = True
    for field in NO_ENABLEMENT_FIELDS:
        if field in payload:
            observed[field] = payload.get(field)
        if payload.get(field) is True:
            clean = False
    return clean, observed

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--candidate-proof", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()
    candidate_proof_path = pathlib.Path(args.candidate_proof).resolve()

    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit(f"output root must stay under run/replay: {output_root}")
    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit(f"dataset candidate root must stay under run/replay: {dataset_candidate_root}")

    candidate_proof = read_json(candidate_proof_path)
    candidate_manifest = read_json(dataset_candidate_root / "00_dataset_candidate_manifest.json")
    materialized_index = read_json(dataset_candidate_root / "02_materialized_file_index.json")
    no_boundary = read_json(dataset_candidate_root / "04_no_broker_no_live_redis_boundary.json")
    readiness = read_json(dataset_candidate_root / "05_candidate_readiness.json")
    next_contract = read_json(dataset_candidate_root / "06_next_replay_dry_run_contract.json")

    dataset_id = candidate_manifest.get("dataset_id") or candidate_proof.get("dataset_id")
    capture_id = candidate_manifest.get("capture_id") or candidate_proof.get("capture_id")

    artifact_states = {
        name: file_state(project_root, dataset_candidate_root / name)
        for name in EXPECTED_CANDIDATE_ARTIFACTS
    }

    input_surface_dir = dataset_candidate_root / "input_surfaces"
    input_surface_states = {}
    missing_input_surfaces = []
    for key in EXPECTED_INPUT_SURFACES:
        found = None
        for suffix in (".json", ".log", ".txt", ".csv", ".dat"):
            candidate = input_surface_dir / f"{key}{suffix}"
            if candidate.is_file():
                found = candidate
                break
        if found is None:
            found = input_surface_dir / f"{key}.json"
        state = file_state(project_root, found)
        input_surface_states[key] = state
        if not state["present"]:
            missing_input_surfaces.append(key)

    no_boundary_clean, no_boundary_observed = no_enablement_clean(no_boundary)
    candidate_proof_clean, candidate_proof_observed = no_enablement_clean(candidate_proof)

    future_forbidden = next_contract.get("forbidden_next_actions_without_new_gate")
    if not isinstance(future_forbidden, list):
        future_forbidden = []

    required_future_forbidden = [
        "start services",
        "read live Redis",
        "write live Redis",
        "call broker APIs",
        "approve paper_armed",
        "approve live trading",
        "claim full replay/live parity",
    ]

    missing_future_forbidden = [
        item for item in required_future_forbidden
        if item not in future_forbidden
    ]

    safety_gate_ok = (
        candidate_proof.get("observe_only_offline_replay_dataset_candidate_28m_ok") is True
        and candidate_proof.get("dataset_candidate_materialized") is True
        and candidate_proof.get("dataset_materialized_for_replay_run") is False
        and candidate_proof.get("replay_run_completed") is False
        and candidate_proof.get("comparison_completed") is False
        and readiness.get("dataset_candidate_materialized") is True
        and readiness.get("dataset_materialized_for_replay_run") is False
        and readiness.get("blocking_gap_count") == 0
        and no_boundary_clean
        and candidate_proof_clean
        and not missing_input_surfaces
        and not missing_future_forbidden
    )

    output_root.mkdir(parents=True, exist_ok=True)

    gate_manifest = {
        "schema_version": "offline_replay_candidate_no_broker_no_live_redis_gate_28n_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "NO_BROKER_NO_LIVE_REDIS_GATE_BEFORE_REPLAY_DRY_RUN",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "dataset_candidate_root": str(dataset_candidate_root),
        "output_root": str(output_root),
        "safety_gate_ok": bool(safety_gate_ok),
        "candidate_artifact_states": artifact_states,
        "input_surface_states": input_surface_states,
        "missing_input_surfaces": missing_input_surfaces,
        "no_boundary_clean": bool(no_boundary_clean),
        "no_boundary_observed": no_boundary_observed,
        "candidate_proof_clean": bool(candidate_proof_clean),
        "candidate_proof_observed": candidate_proof_observed,
        "missing_future_forbidden": missing_future_forbidden,
        "dataset_materialized_for_replay_run": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "broker_call_reachable": False,
        "live_redis_write_reachable": False,
        "runtime_promotion_reachable": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28N",
        "next_batch": "Batch 28O — prepare guarded offline replay engine dry-run command contract, still not paper/live enablement.",
    }

    write_json(output_root / "00_no_broker_no_live_redis_gate_manifest.json", gate_manifest)
    write_json(output_root / "01_candidate_artifact_safety_index.json", {
        "schema_version": "offline_replay_candidate_artifact_safety_index_28n_v1",
        "dataset_id": dataset_id,
        "candidate_artifact_states": artifact_states,
        "input_surface_states": input_surface_states,
        "missing_input_surfaces": missing_input_surfaces,
    })
    write_json(output_root / "02_no_enablement_field_audit.json", {
        "schema_version": "offline_replay_no_enablement_field_audit_28n_v1",
        "dataset_id": dataset_id,
        "no_boundary_clean": bool(no_boundary_clean),
        "no_boundary_observed": no_boundary_observed,
        "candidate_proof_clean": bool(candidate_proof_clean),
        "candidate_proof_observed": candidate_proof_observed,
    })
    write_json(output_root / "03_future_dry_run_guard_contract.json", {
        "schema_version": "offline_replay_future_dry_run_guard_contract_28n_v1",
        "dataset_id": dataset_id,
        "allowed_next_batch": "28O",
        "allowed_next_actions": [
            "prepare guarded offline replay engine dry-run command contract",
            "inspect replay entrypoints",
            "write no-broker/no-live-Redis proof",
        ],
        "still_forbidden_in_28O": required_future_forbidden,
        "missing_future_forbidden": missing_future_forbidden,
        "replay_engine_run_allowed_in_28N": False,
    })
    write_json(output_root / "04_safety_readiness.json", {
        "schema_version": "offline_replay_candidate_safety_readiness_28n_v1",
        "dataset_id": dataset_id,
        "safety_gate_ok": bool(safety_gate_ok),
        "dataset_candidate_ready": True,
        "replay_engine_run_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28N",
    })

    result = {
        "schema_version": "offline_replay_candidate_no_broker_no_live_redis_gate_result_28n_v1",
        "accepted_for": "NO_BROKER_NO_LIVE_REDIS_GATE_BEFORE_REPLAY_DRY_RUN",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "output_root": str(output_root),
        "safety_gate_ok": bool(safety_gate_ok),
        "missing_input_surfaces": missing_input_surfaces,
        "missing_future_forbidden": missing_future_forbidden,
        "written_count": 5,
        "dataset_materialized_for_replay_run": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28N",
        "next_batch": gate_manifest["next_batch"],
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if safety_gate_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
