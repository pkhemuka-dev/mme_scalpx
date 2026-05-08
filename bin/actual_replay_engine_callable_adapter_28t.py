#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

REPLAY_MODULES = [
    "app.mme_scalpx.replay.dataset",
    "app.mme_scalpx.replay.runner",
    "app.mme_scalpx.replay.engine",
    "app.mme_scalpx.replay.topology",
    "app.mme_scalpx.replay.injector",
    "app.mme_scalpx.replay.integrity",
    "app.mme_scalpx.replay.safety",
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
    return str(path.resolve()).startswith(str(replay_root) + "/")

def find_surface(input_dir: pathlib.Path, key: str) -> pathlib.Path:
    for suffix in (".json", ".log", ".txt", ".csv", ".dat"):
        candidate = input_dir / f"{key}{suffix}"
        if candidate.is_file():
            return candidate
    return input_dir / f"{key}.json"

def discover_callables() -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for module_name in REPLAY_MODULES:
        item: dict[str, Any] = {
            "module": module_name,
            "import_ok": False,
            "import_error": None,
            "functions": [],
            "classes": [],
            "candidate_callables": [],
        }
        try:
            module = importlib.import_module(module_name)
            item["import_ok"] = True
        except Exception as exc:
            item["import_error"] = f"{type(exc).__name__}: {exc}"
            inventory[module_name] = item
            continue

        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue
            try:
                sig = str(inspect.signature(obj)) if callable(obj) else None
            except Exception:
                sig = None

            if inspect.isfunction(obj):
                record = {"name": name, "signature": sig}
                item["functions"].append(record)
                lname = name.lower()
                if any(tok in lname for tok in ("run", "replay", "execute", "simulate", "engine")):
                    item["candidate_callables"].append({
                        "kind": "function",
                        "name": name,
                        "signature": sig,
                    })
            elif inspect.isclass(obj):
                record = {"name": name, "signature": sig}
                item["classes"].append(record)
                lname = name.lower()
                if any(tok in lname for tok in ("runner", "engine", "replay")):
                    item["candidate_callables"].append({
                        "kind": "class",
                        "name": name,
                        "signature": sig,
                    })

        inventory[module_name] = item
    return inventory

def score_candidate(module_name: str, candidate: dict[str, Any]) -> int:
    name = str(candidate.get("name", "")).lower()
    sig = str(candidate.get("signature") or "").lower()
    score = 0
    if "runner" in module_name or "engine" in module_name:
        score += 2
    if "replay" in name:
        score += 3
    if "run" in name or "execute" in name:
        score += 2
    if "dataset" in sig:
        score += 2
    if "output" in sig or "artifact" in sig or "run_dir" in sig:
        score += 1
    if "broker" in sig or "redis" in sig:
        score -= 5
    return score

def main() -> int:
    parser = argparse.ArgumentParser(description="Actual replay-engine callable adapter discovery for Batch 28T.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--discover-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit("dataset candidate root must stay under run/replay")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output root must stay under run/replay")

    output_root.mkdir(parents=True, exist_ok=True)

    input_dir = dataset_candidate_root / "input_surfaces"
    input_surfaces = {}
    missing_surfaces = []
    for key in EXPECTED_INPUT_SURFACES:
        path = find_surface(input_dir, key)
        state = file_state(project_root, path)
        input_surfaces[key] = state
        if not state["present"]:
            missing_surfaces.append(key)

    inventory = discover_callables()

    scored = []
    for module_name, item in inventory.items():
        for candidate in item.get("candidate_callables", []):
            scored.append({
                "module": module_name,
                **candidate,
                "score": score_candidate(module_name, candidate),
            })
    scored = sorted(scored, key=lambda x: x.get("score", 0), reverse=True)

    selected = scored[0] if scored and scored[0].get("score", 0) >= 4 else None

    callable_adapter_ready = bool(
        args.no_broker
        and args.no_live_redis
        and args.observe_only
        and args.dry_run
        and not missing_surfaces
        and selected is not None
    )

    manifest = {
        "schema_version": "actual_replay_engine_callable_adapter_manifest_28t_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "ACTUAL_REPLAY_ENGINE_CALLABLE_DISCOVERY_AND_ADAPTER_CONTRACT_ONLY",
        "callable_adapter_ready": bool(callable_adapter_ready),
        "selected_callable": selected,
        "candidate_count": len(scored),
        "discover_only": bool(args.discover_only),
        "dataset_candidate_root": str(dataset_candidate_root),
        "output_root": str(output_root),
        "missing_surfaces": missing_surfaces,
        "replay_engine_invoked": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28T",
    }

    write_json(output_root / "00_callable_adapter_manifest.json", manifest)
    write_json(output_root / "01_replay_callable_inventory.json", {
        "schema_version": "actual_replay_callable_inventory_28t_v1",
        "inventory": inventory,
        "scored_candidates": scored,
    })
    write_json(output_root / "02_callable_selection_report.json", {
        "schema_version": "actual_replay_callable_selection_report_28t_v1",
        "callable_adapter_ready": bool(callable_adapter_ready),
        "selected_callable": selected,
        "candidate_count": len(scored),
        "selection_rule": "score>=4 and no missing required input surfaces",
    })
    write_json(output_root / "03_dataset_bridge_contract.json", {
        "schema_version": "actual_replay_callable_dataset_bridge_contract_28t_v1",
        "dataset_candidate_root": str(dataset_candidate_root),
        "input_dir": str(input_dir),
        "input_surfaces": input_surfaces,
        "missing_surfaces": missing_surfaces,
    })
    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", {
        "schema_version": "actual_replay_callable_adapter_no_boundary_28t_v1",
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
        "replay_engine_invoked": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28T",
    })
    write_json(output_root / "05_next_callable_execution_contract.json", {
        "schema_version": "actual_replay_callable_next_execution_contract_28t_v1",
        "callable_adapter_ready": bool(callable_adapter_ready),
        "selected_callable": selected,
        "next_batch": "Batch 28U — execute selected replay callable through guarded adapter, still not paper/live enablement." if callable_adapter_ready else "Batch 28U — repair replay callable surface or add explicit offline replay callable, still not paper/live enablement.",
        "allowed_next_actions": [
            "execute only selected callable if still valid",
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

    result = {
        "schema_version": "actual_replay_engine_callable_adapter_result_28t_v1",
        "accepted_for": "ACTUAL_REPLAY_ENGINE_CALLABLE_DISCOVERY_AND_ADAPTER_CONTRACT_ONLY",
        "callable_adapter_ready": bool(callable_adapter_ready),
        "selected_callable": selected,
        "candidate_count": len(scored),
        "missing_surfaces": missing_surfaces,
        "written_count": 6,
        "replay_engine_invoked": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28T",
        "next_batch": "Batch 28U — execute selected replay callable through guarded adapter, still not paper/live enablement." if callable_adapter_ready else "Batch 28U — repair replay callable surface or add explicit offline replay callable, still not paper/live enablement.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if callable_adapter_ready else 2

if __name__ == "__main__":
    raise SystemExit(main())
