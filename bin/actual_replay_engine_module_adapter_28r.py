#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
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

REPLAY_MODULE_RELATIVE_FILES = [
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/runner.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/topology.py",
    "app/mme_scalpx/replay/injector.py",
    "app/mme_scalpx/replay/integrity.py",
    "app/mme_scalpx/replay/safety.py",
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
    return str(path.resolve()).startswith(str(replay_root) + "/")

def find_surface(input_dir: pathlib.Path, key: str) -> pathlib.Path:
    for suffix in (".json", ".log", ".txt", ".csv", ".dat"):
        candidate = input_dir / f"{key}{suffix}"
        if candidate.is_file():
            return candidate
    return input_dir / f"{key}.json"

def parse_surface(project_root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    out: dict[str, Any] = {
        "path": rel(project_root, path),
        "present": path.is_file(),
        "sha256": sha256_file(path),
        "functions": [],
        "classes": [],
        "parse_ok": False,
        "parse_error": None,
    }
    if not path.is_file():
        return out
    try:
        tree = ast.parse(text)
        out["parse_ok"] = True
    except SyntaxError as exc:
        out["parse_error"] = f"{type(exc).__name__}: {exc}"
        return out
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out["functions"].append({
                "name": node.name,
                "lineno": getattr(node, "lineno", None),
                "args": [a.arg for a in node.args.args],
            })
        elif isinstance(node, ast.ClassDef):
            out["classes"].append({"name": node.name, "lineno": getattr(node, "lineno", None)})
    return out

def main() -> int:
    parser = argparse.ArgumentParser(description="Narrow actual replay-engine module adapter builder for Batch 28R rescue.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit("dataset candidate root must stay under run/replay")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output root must stay under run/replay")

    input_dir = dataset_candidate_root / "input_surfaces"
    output_root.mkdir(parents=True, exist_ok=True)

    input_surfaces = {}
    missing_surfaces = []
    for key in EXPECTED_INPUT_SURFACES:
        path = find_surface(input_dir, key)
        state = file_state(project_root, path)
        input_surfaces[key] = state
        if not state["present"]:
            missing_surfaces.append(key)

    module_surfaces = {}
    for raw in REPLAY_MODULE_RELATIVE_FILES:
        module_path = project_root / raw
        module_surfaces[raw] = parse_surface(project_root, module_path)

    runner_candidates = module_surfaces.get("app/mme_scalpx/replay/runner.py", {})
    engine_candidates = module_surfaces.get("app/mme_scalpx/replay/engine.py", {})

    likely_module_path_available = bool(
        runner_candidates.get("functions")
        or runner_candidates.get("classes")
        or engine_candidates.get("functions")
        or engine_candidates.get("classes")
    )

    adapter_ready = bool(
        args.no_broker
        and args.no_live_redis
        and args.observe_only
        and args.dry_run
        and dataset_candidate_root.is_dir()
        and input_dir.is_dir()
        and not missing_surfaces
        and likely_module_path_available
    )

    manifest = {
        "schema_version": "actual_replay_engine_module_adapter_manifest_28r_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "NARROW_ACTUAL_REPLAY_ENGINE_MODULE_ADAPTER_BUILD_ONLY",
        "adapter_ready": bool(adapter_ready),
        "project_root": str(project_root),
        "dataset_candidate_root": str(dataset_candidate_root),
        "output_root": str(output_root),
        "input_surface_count": len(input_surfaces) - len(missing_surfaces),
        "missing_surfaces": missing_surfaces,
        "likely_module_path_available": bool(likely_module_path_available),
        "contract_only": bool(args.contract_only),
        "replay_engine_executed": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28R",
    }

    write_json(output_root / "00_module_adapter_manifest.json", manifest)
    write_json(output_root / "01_replay_module_interface_map.json", {
        "schema_version": "actual_replay_module_interface_map_28r_v1",
        "module_surfaces": module_surfaces,
        "likely_module_path_available": bool(likely_module_path_available),
    })
    write_json(output_root / "02_dataset_bridge_contract.json", {
        "schema_version": "actual_replay_dataset_bridge_contract_28r_v1",
        "dataset_candidate_root": str(dataset_candidate_root),
        "input_dir": str(input_dir),
        "input_surfaces": input_surfaces,
        "missing_surfaces": missing_surfaces,
        "future_bridge_mode": "dataset_candidate_to_replay_module_adapter",
    })
    write_json(output_root / "03_no_broker_no_live_redis_boundary.json", {
        "schema_version": "actual_replay_module_adapter_no_boundary_28r_v1",
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
        "replay_engine_executed": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28R",
    })
    write_json(output_root / "04_next_module_execution_contract.json", {
        "schema_version": "actual_replay_module_adapter_next_execution_contract_28r_v1",
        "adapter_ready": bool(adapter_ready),
        "next_batch": "Batch 28S — execute narrow actual replay-engine module adapter dry-run, still not paper/live enablement.",
        "allowed_next_actions": [
            "execute only this narrow module adapter",
            "stay under run/replay output root",
            "write no-broker/no-live-Redis proof",
            "do not compare parity until replay output exists",
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
    write_json(output_root / "05_adapter_readiness.json", {
        "schema_version": "actual_replay_module_adapter_readiness_28r_v1",
        "adapter_ready": bool(adapter_ready),
        "missing_surfaces": missing_surfaces,
        "likely_module_path_available": bool(likely_module_path_available),
        "replay_engine_executed": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28R",
    })

    result = {
        "schema_version": "actual_replay_engine_module_adapter_result_28r_v1",
        "accepted_for": "NARROW_ACTUAL_REPLAY_ENGINE_MODULE_ADAPTER_BUILD_ONLY",
        "adapter_ready": bool(adapter_ready),
        "output_root": str(output_root),
        "input_surface_count": len(input_surfaces) - len(missing_surfaces),
        "missing_surfaces": missing_surfaces,
        "likely_module_path_available": bool(likely_module_path_available),
        "written_count": 6,
        "replay_engine_executed": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28R",
        "next_batch": "Batch 28S — execute narrow actual replay-engine module adapter dry-run, still not paper/live enablement.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if adapter_ready else 1

if __name__ == "__main__":
    raise SystemExit(main())
