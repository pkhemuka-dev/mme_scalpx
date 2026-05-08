#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

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
        return {
            "_read_error": type(exc).__name__,
            "_read_error_text": str(exc),
            "_path": str(path),
        }

def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def file_state(root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    try:
        display = str(path.resolve().relative_to(root))
    except Exception:
        display = str(path)
    return {
        "path": display,
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
    parser.add_argument("--preflight-manifest", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--inspect-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    preflight_manifest_path = pathlib.Path(args.preflight_manifest).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit(f"output root must stay under run/replay: {output_root}")

    preflight = read_json(preflight_manifest_path)
    package_root_raw = preflight.get("package_root")
    package_root = pathlib.Path(package_root_raw)
    if not package_root.is_absolute():
        package_root = project_root / package_root

    dataset_id = preflight.get("dataset_id")
    capture_id = preflight.get("capture_id")

    evidence_dir = package_root / "evidence_files"
    evidence_files = sorted(p for p in evidence_dir.glob("*") if p.is_file())

    output_root.mkdir(parents=True, exist_ok=True)

    reference_index = {
        "schema_version": "offline_replay_dataset_source_reference_index_28k_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "package_root": str(package_root),
        "evidence_dir": str(evidence_dir),
        "evidence_file_count": len(evidence_files),
        "evidence_files": [file_state(project_root, p) for p in evidence_files],
        "read_only_reference_only": True,
    }

    manifest = {
        "schema_version": "offline_replay_materialization_harness_manifest_28k_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OFFLINE_REPLAY_MATERIALIZATION_HARNESS_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "preflight_manifest": str(preflight_manifest_path),
        "output_root": str(output_root),
        "package_root": str(package_root),
        "package_root_present": package_root.is_dir(),
        "evidence_dir_present": evidence_dir.is_dir(),
        "evidence_file_count": len(evidence_files),
        "inspect_only": bool(args.inspect_only),
        "dataset_materialized": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28K",
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
    }

    service_plan = {
        "schema_version": "offline_replay_service_surface_materialization_plan_28k_v1",
        "dataset_id": dataset_id,
        "mode": "harness_only_no_replay_execution",
        "source_surfaces": [
            "feed_snapshot",
            "feature_payload",
            "family_surfaces",
            "strategy_activation",
            "no_order_sent",
            "provider_runtime",
            "provider_health_snapshot",
            "selected_option_context",
            "dhan_oi_ladder_context_if_available",
            "live_stream_inventory",
            "live_hash_inventory",
            "live_capture_log",
        ],
        "future_materialization_targets": [
            "dataset coverage report",
            "replay feed input candidate",
            "feature replay comparability candidate",
            "strategy report-only comparability candidate",
            "no-order/no-broker/no-live-redis replay proof",
        ],
        "not_executed_in_28k": [
            "replay engine",
            "strategy runtime",
            "risk runtime",
            "execution runtime",
            "broker adapter",
            "redis transport",
        ],
    }

    no_enablement = {
        "schema_version": "offline_replay_materialization_no_enablement_boundary_28k_v1",
        "dataset_id": dataset_id,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28K",
    }

    future_contract = {
        "schema_version": "offline_replay_future_execution_contract_28k_v1",
        "dataset_id": dataset_id,
        "next_batch": "Batch 28L — run offline replay materialization dry-run from the 28K harness, still not paper/live enablement.",
        "allowed_next_actions": [
            "read 28J preflight artifacts",
            "read 28F copied evidence package",
            "materialize offline replay dataset candidate under run/replay only",
            "write no-broker/no-live-redis proof",
        ],
        "forbidden_next_actions_without_new_gate": [
            "paper_armed approval",
            "live trading approval",
            "broker call",
            "live Redis write",
            "production doctrine mutation",
            "claim full replay/live parity",
        ],
    }

    readiness = {
        "schema_version": "offline_replay_materialization_readiness_28k_v1",
        "dataset_id": dataset_id,
        "harness_built": True,
        "dataset_materialized": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "evidence_file_count": len(evidence_files),
        "ready_for_28l_materialization_dry_run": bool(package_root.is_dir() and evidence_dir.is_dir() and len(evidence_files) >= 12),
        "full_live_replay_parity": "NOT_PROVEN_IN_28K",
    }

    write_json(output_root / "00_offline_materialization_harness_manifest.json", manifest)
    write_json(output_root / "01_dataset_source_reference_index.json", reference_index)
    write_json(output_root / "02_service_surface_materialization_plan.json", service_plan)
    write_json(output_root / "03_no_enablement_boundary.json", no_enablement)
    write_json(output_root / "04_future_execution_contract.json", future_contract)
    write_json(output_root / "05_materialization_readiness.json", readiness)

    result = {
        "schema_version": "offline_replay_materialization_harness_result_28k_v1",
        "accepted_for": "OFFLINE_REPLAY_MATERIALIZATION_HARNESS_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "output_root": str(output_root),
        "harness_built": True,
        "dataset_materialized": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "evidence_file_count": len(evidence_files),
        "written_count": 6,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28K",
        "next_batch": future_contract["next_batch"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
