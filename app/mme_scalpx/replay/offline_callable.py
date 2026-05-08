"""Explicit offline-only replay callable surface.

This module is intentionally narrow. It validates a materialized dataset candidate and
writes deterministic offline replay preparation artifacts. It does not call brokers,
touch live Redis, start services, approve paper/live, or claim replay/live parity.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any, Union

EXPECTED_INPUT_SURFACES = (
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
)

def _sha256_file(path: pathlib.Path) -> Union[str, None]:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def _safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    return str(path.resolve()).startswith(str(replay_root) + "/")

def _find_surface(input_dir: pathlib.Path, key: str) -> pathlib.Path:
    for suffix in (".json", ".log", ".txt", ".csv", ".dat"):
        candidate = input_dir / f"{key}{suffix}"
        if candidate.is_file():
            return candidate
    return input_dir / f"{key}.json"

def _file_state(project_root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    try:
        rel_path = str(path.resolve().relative_to(project_root))
    except Exception:
        rel_path = str(path)
    return {
        "path": rel_path,
        "present": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": _sha256_file(path),
    }

def discover_offline_replay_callable() -> dict[str, Any]:
    return {
        "module": "app.mme_scalpx.replay.offline_callable",
        "callable_name": "run_offline_replay_engine_dry_run",
        "accepted_for": "EXPLICIT_OFFLINE_REPLAY_CALLABLE_SURFACE",
        "replay_engine_core_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_BY_EXPLICIT_OFFLINE_CALLABLE",
    }

def run_offline_replay_engine_dry_run(
    *,
    project_root: Union[str, pathlib.Path],
    dataset_candidate_root: Union[str, pathlib.Path],
    output_root: Union[str, pathlib.Path],
    no_broker: bool = True,
    no_live_redis: bool = True,
    observe_only: bool = True,
    dry_run: bool = True,
) -> dict[str, Any]:
    root = pathlib.Path(project_root).resolve()
    dataset_root = pathlib.Path(dataset_candidate_root).resolve()
    out_root = pathlib.Path(output_root).resolve()

    if not _safe_under_run_replay(root, dataset_root):
        raise ValueError("dataset_candidate_root must stay under run/replay")
    if not _safe_under_run_replay(root, out_root):
        raise ValueError("output_root must stay under run/replay")
    if not (no_broker and no_live_redis and observe_only and dry_run):
        raise ValueError("offline callable requires no_broker, no_live_redis, observe_only, and dry_run")

    input_dir = dataset_root / "input_surfaces"
    out_root.mkdir(parents=True, exist_ok=True)

    input_surfaces: dict[str, Any] = {}
    missing: list[str] = []
    for key in EXPECTED_INPUT_SURFACES:
        surface = _find_surface(input_dir, key)
        state = _file_state(root, surface)
        input_surfaces[key] = state
        if not state["present"]:
            missing.append(key)

    dry_run_ready = bool(not missing and dataset_root.is_dir() and input_dir.is_dir())

    manifest = {
        "schema_version": "explicit_offline_replay_callable_execution_surface_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "EXPLICIT_OFFLINE_REPLAY_CALLABLE_DRY_RUN_SURFACE",
        "dry_run_ready": dry_run_ready,
        "project_root": str(root),
        "dataset_candidate_root": str(dataset_root),
        "output_root": str(out_root),
        "input_surface_count": len(input_surfaces) - len(missing),
        "missing_surfaces": missing,
        "replay_engine_callable_invoked": True,
        "replay_engine_core_completed": False,
        "replay_run_completed": dry_run_ready,
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
        "full_live_replay_parity": "NOT_PROVEN_BY_EXPLICIT_OFFLINE_CALLABLE",
    }

    _write_json(out_root / "00_offline_replay_callable_manifest.json", manifest)
    _write_json(out_root / "01_input_surface_index.json", {
        "schema_version": "explicit_offline_replay_callable_input_surface_index_v1",
        "input_surfaces": input_surfaces,
        "missing_surfaces": missing,
    })
    _write_json(out_root / "02_replay_dry_run_plan.json", {
        "schema_version": "explicit_offline_replay_callable_dry_run_plan_v1",
        "dry_run_ready": dry_run_ready,
        "planned_next_step": "wire this callable to concrete replay engine internals only after separate proof",
        "replay_engine_core_completed": False,
    })
    _write_json(out_root / "03_no_broker_no_live_redis_boundary.json", {
        "schema_version": "explicit_offline_replay_callable_no_boundary_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_BY_EXPLICIT_OFFLINE_CALLABLE",
    })
    _write_json(out_root / "04_next_engine_wiring_contract.json", {
        "schema_version": "explicit_offline_replay_callable_next_engine_wiring_contract_v1",
        "dry_run_ready": dry_run_ready,
        "next_batch": "Batch 28V — execute explicit offline replay callable dry-run, still not paper/live enablement.",
        "forbidden_without_new_gate": [
            "start services",
            "read live Redis",
            "write live Redis",
            "call broker APIs",
            "approve paper_armed",
            "approve live trading",
            "claim full replay/live parity",
        ],
    })
    return manifest
