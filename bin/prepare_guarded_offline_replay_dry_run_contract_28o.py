#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

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

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--safety-gate-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--candidate-proof", required=True)
    parser.add_argument("--safety-proof", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    safety_gate_root = pathlib.Path(args.safety_gate_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()
    candidate_proof_path = pathlib.Path(args.candidate_proof).resolve()
    safety_proof_path = pathlib.Path(args.safety_proof).resolve()

    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit(f"output root must stay under run/replay: {output_root}")
    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit(f"dataset candidate root must stay under run/replay: {dataset_candidate_root}")
    if not safe_under_run_replay(project_root, safety_gate_root):
        raise SystemExit(f"safety gate root must stay under run/replay: {safety_gate_root}")

    candidate_proof = read_json(candidate_proof_path)
    safety_proof = read_json(safety_proof_path)
    candidate_manifest = read_json(dataset_candidate_root / "00_dataset_candidate_manifest.json")
    no_boundary = read_json(dataset_candidate_root / "04_no_broker_no_live_redis_boundary.json")
    readiness = read_json(dataset_candidate_root / "05_candidate_readiness.json")
    gate_manifest = read_json(safety_gate_root / "00_no_broker_no_live_redis_gate_manifest.json")

    dataset_id = candidate_manifest.get("dataset_id") or candidate_proof.get("dataset_id")
    capture_id = candidate_manifest.get("capture_id") or candidate_proof.get("capture_id")

    input_surface_dir = dataset_candidate_root / "input_surfaces"
    input_surfaces = {}
    missing_surfaces = []
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
        input_surfaces[key] = state
        if not state["present"]:
            missing_surfaces.append(key)

    guarded_output_root = project_root / "run" / "replay" / "parity" / "offline_replay_dry_run" / str(dataset_id)
    guarded_output_root_safe = safe_under_run_replay(project_root, guarded_output_root)

    proposed_command = [
        "python",
        "bin/replay_run.py",
        "--offline",
        "--dataset-candidate",
        str(dataset_candidate_root),
        "--output-root",
        str(guarded_output_root),
        "--no-broker",
        "--no-live-redis",
        "--observe-only",
        "--dry-run",
    ]

    required_safety_booleans_false = [
        "starts_services",
        "reads_live_redis",
        "writes_live_redis",
        "calls_broker_api",
        "paper_armed_approved",
        "live_trading_approved",
        "execution_arming_created",
        "real_order_sent",
        "production_doctrine_changed",
    ]

    safety_sources = {
        "candidate_proof": candidate_proof,
        "safety_proof": safety_proof,
        "candidate_no_boundary": no_boundary,
        "safety_gate_manifest": gate_manifest,
    }

    false_field_violations = []
    for source_name, payload in safety_sources.items():
        for field in required_safety_booleans_false:
            if payload.get(field) is True:
                false_field_violations.append({"source": source_name, "field": field, "value": True})

    contract_ready = (
        candidate_proof.get("observe_only_offline_replay_dataset_candidate_28m_ok") is True
        and safety_proof.get("observe_only_offline_replay_candidate_no_broker_no_live_redis_28n_ok") is True
        and safety_proof.get("safety_gate_ok") is True
        and candidate_proof.get("dataset_candidate_materialized") is True
        and candidate_proof.get("dataset_materialized_for_replay_run") is False
        and safety_proof.get("replay_run_completed") is False
        and readiness.get("blocking_gap_count") == 0
        and not missing_surfaces
        and not false_field_violations
        and guarded_output_root_safe
    )

    output_root.mkdir(parents=True, exist_ok=True)

    command_contract = {
        "schema_version": "guarded_offline_replay_engine_dry_run_command_contract_28o_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_OFFLINE_REPLAY_DRY_RUN_COMMAND_CONTRACT_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "contract_ready": bool(contract_ready),
        "proposed_future_command_not_executed": proposed_command,
        "dataset_candidate_root": str(dataset_candidate_root),
        "safety_gate_root": str(safety_gate_root),
        "future_output_root": str(guarded_output_root),
        "future_output_root_replay_safe": bool(guarded_output_root_safe),
        "required_before_execution": [
            "re-confirm no broker API imports/calls reachable from selected dry-run path",
            "re-confirm no live Redis writes reachable from selected dry-run path",
            "run future dry-run under explicit offline/no-broker/no-live-redis mode only",
            "write proof before interpreting replay output",
        ],
        "forbidden_in_28o": [
            "execute proposed command",
            "start services",
            "read live Redis",
            "write live Redis",
            "call broker APIs",
            "approve paper_armed",
            "approve live trading",
            "claim replay/live parity",
        ],
        "dataset_materialized_for_replay_run": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28O",
    }

    input_surface_contract = {
        "schema_version": "guarded_offline_replay_input_surface_contract_28o_v1",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "expected_input_surfaces": EXPECTED_INPUT_SURFACES,
        "input_surfaces": input_surfaces,
        "missing_surfaces": missing_surfaces,
    }

    safety_boundary = {
        "schema_version": "guarded_offline_replay_dry_run_safety_boundary_28o_v1",
        "dataset_id": dataset_id,
        "false_field_violations": false_field_violations,
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
        "dataset_materialized_for_replay_run": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28O",
    }

    readiness_report = {
        "schema_version": "guarded_offline_replay_dry_run_readiness_28o_v1",
        "dataset_id": dataset_id,
        "contract_ready": bool(contract_ready),
        "candidate_28m_ok": candidate_proof.get("observe_only_offline_replay_dataset_candidate_28m_ok") is True,
        "safety_gate_28n_ok": safety_proof.get("observe_only_offline_replay_candidate_no_broker_no_live_redis_28n_ok") is True,
        "missing_surfaces": missing_surfaces,
        "false_field_violations": false_field_violations,
        "future_command_prepared": True,
        "future_command_executed": False,
        "next_batch": "Batch 28P — execute guarded offline replay engine dry-run only if 28O contract is still valid, still not paper/live enablement.",
    }

    write_json(output_root / "00_dry_run_command_contract.json", command_contract)
    write_json(output_root / "01_input_surface_contract.json", input_surface_contract)
    write_json(output_root / "02_no_broker_no_live_redis_boundary.json", safety_boundary)
    write_json(output_root / "03_future_output_root_contract.json", {
        "schema_version": "guarded_offline_replay_future_output_root_contract_28o_v1",
        "dataset_id": dataset_id,
        "future_output_root": str(guarded_output_root),
        "future_output_root_replay_safe": bool(guarded_output_root_safe),
        "must_not_write_outside_run_replay": True,
    })
    write_json(output_root / "04_readiness_report.json", readiness_report)

    result = {
        "schema_version": "guarded_offline_replay_dry_run_contract_result_28o_v1",
        "accepted_for": "GUARDED_OFFLINE_REPLAY_DRY_RUN_COMMAND_CONTRACT_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "output_root": str(output_root),
        "contract_ready": bool(contract_ready),
        "future_command_prepared": True,
        "future_command_executed": False,
        "missing_surfaces": missing_surfaces,
        "false_field_violations": false_field_violations,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28O",
        "next_batch": readiness_report["next_batch"],
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if contract_ready else 1

if __name__ == "__main__":
    raise SystemExit(main())
