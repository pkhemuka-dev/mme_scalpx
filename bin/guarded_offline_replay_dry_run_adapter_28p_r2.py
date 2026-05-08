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

def find_surface(input_dir: pathlib.Path, key: str) -> pathlib.Path:
    for suffix in (".json", ".log", ".txt", ".csv", ".dat"):
        candidate = input_dir / f"{key}{suffix}"
        if candidate.is_file():
            return candidate
    return input_dir / f"{key}.json"

def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded offline replay dry-run adapter for Batch 28P-R2/28P-R3.")
    parser.add_argument("--offline", action="store_true", required=True)
    parser.add_argument("--dataset-candidate", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate = pathlib.Path(args.dataset_candidate).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate):
        raise SystemExit(f"dataset candidate must stay under run/replay: {dataset_candidate}")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit(f"output root must stay under run/replay: {output_root}")

    input_dir = dataset_candidate / "input_surfaces"
    output_root.mkdir(parents=True, exist_ok=True)

    input_surfaces = {}
    missing_surfaces = []
    for key in EXPECTED_INPUT_SURFACES:
        path = find_surface(input_dir, key)
        state = file_state(project_root, path)
        input_surfaces[key] = state
        if not state["present"]:
            missing_surfaces.append(key)

    adapter_ready = (
        args.offline
        and args.no_broker
        and args.no_live_redis
        and args.observe_only
        and args.dry_run
        and dataset_candidate.is_dir()
        and input_dir.is_dir()
        and not missing_surfaces
    )

    manifest = {
        "schema_version": "guarded_offline_replay_dry_run_adapter_manifest_28p_r2_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_REPLAY_CLI_ADAPTER_COMPATIBILITY_ONLY",
        "adapter_ready": bool(adapter_ready),
        "project_root": str(project_root),
        "dataset_candidate": str(dataset_candidate),
        "output_root": str(output_root),
        "input_surface_count": len(input_surfaces) - len(missing_surfaces),
        "missing_surfaces": missing_surfaces,
        "contract_only": bool(args.contract_only),
        "adapter_executed_replay_engine": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28P_R2",
    }

    write_json(output_root / "00_adapter_manifest.json", manifest)
    write_json(output_root / "01_adapter_command_contract.json", {
        "schema_version": "guarded_offline_replay_adapter_command_contract_28p_r2_v1",
        "adapter_ready": bool(adapter_ready),
        "adapter_command": [
            "python",
            "bin/guarded_offline_replay_dry_run_adapter_28p_r2.py",
            "--offline",
            "--dataset-candidate",
            str(dataset_candidate),
            "--output-root",
            str(output_root),
            "--no-broker",
            "--no-live-redis",
            "--observe-only",
            "--dry-run",
            "--project-root",
            str(project_root),
        ],
        "future_execution_batch": "28P-R3",
        "replay_engine_execution_allowed_in_28p_r2": False,
    })
    write_json(output_root / "02_dataset_candidate_validation.json", {
        "schema_version": "guarded_offline_replay_adapter_dataset_validation_28p_r2_v1",
        "adapter_ready": bool(adapter_ready),
        "dataset_candidate": str(dataset_candidate),
        "input_dir": str(input_dir),
        "input_surfaces": input_surfaces,
        "missing_surfaces": missing_surfaces,
    })
    write_json(output_root / "03_no_broker_no_live_redis_boundary.json", {
        "schema_version": "guarded_offline_replay_adapter_no_boundary_28p_r2_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28P_R2",
    })
    write_json(output_root / "04_next_execution_contract.json", {
        "schema_version": "guarded_offline_replay_adapter_next_execution_contract_28p_r2_v1",
        "adapter_ready": bool(adapter_ready),
        "next_batch": "Batch 28P-R3 — execute guarded offline replay dry-run through the 28P-R2 adapter, still not paper/live enablement.",
        "allowed_next_actions": [
            "execute only the guarded adapter command",
            "stay under run/replay output root",
            "write proof before comparison",
        ],
        "forbidden_next_actions_without_new_gate": [
            "start services",
            "read live Redis",
            "write live Redis",
            "call broker APIs",
            "approve paper_armed",
            "approve live trading",
            "claim full replay/live parity",
        ],
    })

    result = {
        "schema_version": "guarded_offline_replay_dry_run_adapter_result_28p_r2_v1",
        "accepted_for": "GUARDED_REPLAY_CLI_ADAPTER_COMPATIBILITY_ONLY",
        "adapter_ready": bool(adapter_ready),
        "output_root": str(output_root),
        "input_surface_count": len(input_surfaces) - len(missing_surfaces),
        "missing_surfaces": missing_surfaces,
        "written_count": 5,
        "adapter_executed_replay_engine": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28P_R2",
        "next_batch": "Batch 28P-R3 — execute guarded offline replay dry-run through the 28P-R2 adapter, still not paper/live enablement.",
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if adapter_ready else 1

if __name__ == "__main__":
    raise SystemExit(main())
