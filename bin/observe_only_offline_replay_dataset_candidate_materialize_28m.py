#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
from datetime import datetime, timezone
from typing import Any

EXPECTED_EVIDENCE_KEYS = [
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

DATASET_CANDIDATE_ARTIFACTS = [
    "00_dataset_candidate_manifest.json",
    "01_source_evidence_catalog.json",
    "02_materialized_file_index.json",
    "03_service_surface_dataset_plan.json",
    "04_no_broker_no_live_redis_boundary.json",
    "05_candidate_readiness.json",
    "06_next_replay_dry_run_contract.json",
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

def rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except Exception:
        return str(path)

def file_state(project_root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    return {
        "path": rel(project_root, path),
        "present": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256_file(path),
    }

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    target = path.resolve()
    return str(target).startswith(str(replay_root) + "/")

def infer_surface_kind(path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".log":
        return "log_text"
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"
    return "unknown"

def json_summary(path: pathlib.Path) -> dict[str, Any]:
    if path.suffix.lower() != ".json" or not path.is_file():
        return {
            "json_parse_attempted": False,
            "top_level_type": None,
            "top_level_keys": [],
            "parse_error": None,
        }
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return {
            "json_parse_attempted": True,
            "top_level_type": type(obj).__name__,
            "top_level_keys": sorted(obj.keys()) if isinstance(obj, dict) else [],
            "parse_error": None,
        }
    except Exception as exc:
        return {
            "json_parse_attempted": True,
            "top_level_type": None,
            "top_level_keys": [],
            "parse_error": f"{type(exc).__name__}: {exc}",
        }

def find_source_file(evidence_catalog: dict[str, Any], key: str, fallback_dir: pathlib.Path) -> pathlib.Path:
    entry = evidence_catalog.get(key)
    raw_path = entry.get("path") if isinstance(entry, dict) else None
    if isinstance(raw_path, str) and raw_path:
        p = pathlib.Path(raw_path)
        if p.is_absolute():
            return p
    for suffix in (".json", ".log", ".txt", ".csv"):
        candidate = fallback_dir / f"{key}{suffix}"
        if candidate.is_file():
            return candidate
    return fallback_dir / f"{key}.json"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dry-run-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--candidate-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dry_run_root = pathlib.Path(args.dry_run_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit(f"output root must stay under run/replay: {output_root}")

    dry_run_manifest = read_json(dry_run_root / "00_dataset_materialization_dry_run_manifest.json")
    surface_catalog = read_json(dry_run_root / "01_input_surface_catalog.json")
    candidate_index = read_json(dry_run_root / "02_replay_dataset_candidate_index.json")
    gap_report = read_json(dry_run_root / "05_materialization_gap_report.json")

    dataset_id = dry_run_manifest.get("dataset_id") or candidate_index.get("dataset_id")
    capture_id = dry_run_manifest.get("capture_id") or candidate_index.get("capture_id")
    package_root_raw = dry_run_manifest.get("package_root") or candidate_index.get("package_root")
    evidence_dir_raw = dry_run_manifest.get("evidence_dir") or candidate_index.get("evidence_dir")

    package_root = pathlib.Path(package_root_raw) if isinstance(package_root_raw, str) else None
    evidence_dir = pathlib.Path(evidence_dir_raw) if isinstance(evidence_dir_raw, str) else None
    if package_root and not package_root.is_absolute():
        package_root = project_root / package_root
    if evidence_dir and not evidence_dir.is_absolute():
        evidence_dir = project_root / evidence_dir
    if evidence_dir is None and package_root is not None:
        evidence_dir = package_root / "evidence_files"

    evidence_catalog = surface_catalog.get("evidence_catalog")
    if not isinstance(evidence_catalog, dict):
        evidence_catalog = candidate_index.get("evidence_catalog")
    if not isinstance(evidence_catalog, dict):
        evidence_catalog = {}

    output_root.mkdir(parents=True, exist_ok=True)
    copied_dir = output_root / "input_surfaces"
    copied_dir.mkdir(parents=True, exist_ok=True)

    materialized_index = {}
    missing_keys = []
    hash_mismatch_keys = []
    parse_error_keys = []

    for key in EXPECTED_EVIDENCE_KEYS:
        src = find_source_file(evidence_catalog, key, evidence_dir or copied_dir)
        if not src.is_absolute():
            src = project_root / src

        if not src.is_file():
            missing_keys.append(key)
            materialized_index[key] = {
                "source": file_state(project_root, src),
                "candidate": None,
                "copied": False,
                "hash_match": False,
            }
            continue

        suffix = src.suffix if src.suffix else ".dat"
        dst = copied_dir / f"{key}{suffix}"
        shutil.copy2(src, dst)

        source_state = file_state(project_root, src)
        candidate_state = file_state(project_root, dst)
        hash_match = source_state.get("sha256") == candidate_state.get("sha256")
        js = json_summary(dst)

        if not hash_match:
            hash_mismatch_keys.append(key)
        if js.get("parse_error"):
            parse_error_keys.append(key)

        materialized_index[key] = {
            "source": source_state,
            "candidate": candidate_state,
            "copied": True,
            "hash_match": bool(hash_match),
            "surface_kind": infer_surface_kind(dst),
            "json_summary": js,
        }

    readiness_ok = (
        len(missing_keys) == 0
        and len(hash_mismatch_keys) == 0
        and len(parse_error_keys) == 0
        and gap_report.get("blocking_gap_count") in (0, None)
    )

    manifest = {
        "schema_version": "offline_replay_dataset_candidate_manifest_28m_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OFFLINE_REPLAY_DATASET_CANDIDATE_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "output_root": str(output_root),
        "source_dry_run_root": str(dry_run_root),
        "source_package_root": str(package_root) if package_root else None,
        "source_evidence_dir": str(evidence_dir) if evidence_dir else None,
        "candidate_only": bool(args.candidate_only),
        "dataset_candidate_materialized": bool(readiness_ok),
        "dataset_materialized_for_replay_run": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28M",
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

    source_catalog_out = {
        "schema_version": "offline_replay_dataset_candidate_source_catalog_28m_v1",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "source_dry_run_manifest": str(dry_run_root / "00_dataset_materialization_dry_run_manifest.json"),
        "source_surface_catalog": str(dry_run_root / "01_input_surface_catalog.json"),
        "source_candidate_index": str(dry_run_root / "02_replay_dataset_candidate_index.json"),
        "expected_evidence_keys": EXPECTED_EVIDENCE_KEYS,
        "source_catalog": evidence_catalog,
    }

    service_plan = {
        "schema_version": "offline_replay_dataset_candidate_service_plan_28m_v1",
        "dataset_id": dataset_id,
        "candidate_kind": "input_surface_copy_candidate",
        "materialized_surfaces": sorted(materialized_index.keys()),
        "future_replay_requirements": [
            "derive replay feed frames from feed_snapshot/live_capture_log if supported",
            "derive feature comparability baseline from feature_payload",
            "derive strategy comparability baseline from strategy_activation/family_surfaces",
            "preserve no-order boundary from no_order_sent",
            "write replay no-broker/no-live-redis proof before any engine dry-run",
        ],
        "not_executed_in_28m": [
            "replay engine",
            "strategy runtime",
            "risk runtime",
            "execution runtime",
            "broker adapter",
            "redis transport",
            "paper/live arming",
        ],
    }

    no_boundary = {
        "schema_version": "offline_replay_dataset_candidate_no_boundary_28m_v1",
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
        "dataset_materialized_for_replay_run": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28M",
    }

    readiness = {
        "schema_version": "offline_replay_dataset_candidate_readiness_28m_v1",
        "dataset_id": dataset_id,
        "dataset_candidate_materialized": bool(readiness_ok),
        "dataset_materialized_for_replay_run": False,
        "missing_keys": missing_keys,
        "hash_mismatch_keys": hash_mismatch_keys,
        "parse_error_keys": parse_error_keys,
        "blocking_gap_count": len(missing_keys) + len(hash_mismatch_keys) + len(parse_error_keys),
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28M",
    }

    next_contract = {
        "schema_version": "offline_replay_dataset_candidate_next_contract_28m_v1",
        "dataset_id": dataset_id,
        "next_batch": "Batch 28N — build no-broker/no-live-Redis proof for offline replay dataset candidate before any replay engine dry-run.",
        "allowed_next_actions": [
            "read dataset candidate input_surfaces",
            "inspect replay engine entrypoints",
            "prove replay dry-run cannot call broker APIs",
            "prove replay dry-run cannot write live Redis",
            "prepare replay engine dry-run command contract",
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
    }

    write_json(output_root / "00_dataset_candidate_manifest.json", manifest)
    write_json(output_root / "01_source_evidence_catalog.json", source_catalog_out)
    write_json(output_root / "02_materialized_file_index.json", {
        "schema_version": "offline_replay_dataset_candidate_file_index_28m_v1",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "materialized_index": materialized_index,
        "missing_keys": missing_keys,
        "hash_mismatch_keys": hash_mismatch_keys,
        "parse_error_keys": parse_error_keys,
    })
    write_json(output_root / "03_service_surface_dataset_plan.json", service_plan)
    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", no_boundary)
    write_json(output_root / "05_candidate_readiness.json", readiness)
    write_json(output_root / "06_next_replay_dry_run_contract.json", next_contract)

    result = {
        "schema_version": "offline_replay_dataset_candidate_materialization_result_28m_v1",
        "accepted_for": "OFFLINE_REPLAY_DATASET_CANDIDATE_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "output_root": str(output_root),
        "dataset_candidate_materialized": bool(readiness_ok),
        "dataset_materialized_for_replay_run": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "copied_count": sum(1 for v in materialized_index.values() if v.get("copied") is True),
        "missing_keys": missing_keys,
        "hash_mismatch_keys": hash_mismatch_keys,
        "parse_error_keys": parse_error_keys,
        "blocking_gap_count": readiness["blocking_gap_count"],
        "written_count": len(DATASET_CANDIDATE_ARTIFACTS),
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28M",
        "next_batch": next_contract["next_batch"],
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if readiness_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
