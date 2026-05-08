#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
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

DRY_RUN_ARTIFACTS = [
    "00_dataset_materialization_dry_run_manifest.json",
    "01_input_surface_catalog.json",
    "02_replay_dataset_candidate_index.json",
    "03_service_surface_feasibility.json",
    "04_no_broker_no_live_redis_boundary.json",
    "05_materialization_gap_report.json",
    "06_next_materialization_contract.json",
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

def json_top_level(path: pathlib.Path) -> dict[str, Any]:
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

def find_evidence_file(evidence_dir: pathlib.Path, key: str) -> pathlib.Path:
    for suffix in (".json", ".log", ".txt", ".csv"):
        candidate = evidence_dir / f"{key}{suffix}"
        if candidate.is_file():
            return candidate
    return evidence_dir / f"{key}.json"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--harness-manifest", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--dry-run-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    harness_manifest_path = pathlib.Path(args.harness_manifest).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit(f"output root must stay under run/replay: {output_root}")

    harness_manifest = read_json(harness_manifest_path)
    dataset_id = harness_manifest.get("dataset_id")
    capture_id = harness_manifest.get("capture_id")

    source_package_root_raw = harness_manifest.get("source_package_root")
    if not isinstance(source_package_root_raw, str) or not source_package_root_raw:
        source_package_root_raw = harness_manifest.get("package_root")
    package_root = pathlib.Path(source_package_root_raw)
    if not package_root.is_absolute():
        package_root = project_root / package_root

    evidence_dir = package_root / "evidence_files"
    output_root.mkdir(parents=True, exist_ok=True)

    evidence_catalog = {}
    missing_evidence = []
    parse_error_keys = []

    for key in EXPECTED_EVIDENCE_KEYS:
        path = find_evidence_file(evidence_dir, key)
        state = file_state(project_root, path)
        state["surface_kind"] = infer_surface_kind(path)
        state["json_summary"] = json_top_level(path)
        evidence_catalog[key] = state

        if not state["present"]:
            missing_evidence.append(key)
        if state["json_summary"].get("parse_error"):
            parse_error_keys.append(key)

    candidate_index = {
        "schema_version": "offline_replay_dataset_candidate_index_28l_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "candidate_kind": "dry_run_index_only",
        "package_root": str(package_root),
        "evidence_dir": str(evidence_dir),
        "expected_evidence_count": len(EXPECTED_EVIDENCE_KEYS),
        "present_evidence_count": len(EXPECTED_EVIDENCE_KEYS) - len(missing_evidence),
        "missing_evidence": missing_evidence,
        "parse_error_keys": parse_error_keys,
        "evidence_catalog": evidence_catalog,
        "dataset_materialized": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28L",
    }

    service_surface_feasibility = {
        "schema_version": "offline_replay_service_surface_feasibility_28l_v1",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "status": "FEASIBILITY_CATALOG_ONLY",
        "surfaces": {
            "feed_snapshot": {
                "source": "feed_snapshot",
                "required_for_future": "replay feed reconstruction candidate",
                "present": evidence_catalog.get("feed_snapshot", {}).get("present"),
                "status": "PRESENT_NOT_MATERIALIZED" if evidence_catalog.get("feed_snapshot", {}).get("present") else "MISSING",
            },
            "feature_payload": {
                "source": "feature_payload",
                "required_for_future": "feature comparability baseline",
                "present": evidence_catalog.get("feature_payload", {}).get("present"),
                "status": "PRESENT_NOT_MATERIALIZED" if evidence_catalog.get("feature_payload", {}).get("present") else "MISSING",
            },
            "family_surfaces": {
                "source": "family_surfaces",
                "required_for_future": "five-family surface comparability baseline",
                "present": evidence_catalog.get("family_surfaces", {}).get("present"),
                "status": "PRESENT_NOT_MATERIALIZED" if evidence_catalog.get("family_surfaces", {}).get("present") else "MISSING",
            },
            "strategy_activation": {
                "source": "strategy_activation",
                "required_for_future": "strategy HOLD/report-only activation comparability baseline",
                "present": evidence_catalog.get("strategy_activation", {}).get("present"),
                "status": "PRESENT_NOT_MATERIALIZED" if evidence_catalog.get("strategy_activation", {}).get("present") else "MISSING",
            },
            "no_order_boundary": {
                "source": "no_order_sent",
                "required_for_future": "no broker/no live Redis replay safety proof",
                "present": evidence_catalog.get("no_order_sent", {}).get("present"),
                "status": "PRESENT_NOT_MATERIALIZED" if evidence_catalog.get("no_order_sent", {}).get("present") else "MISSING",
            },
        },
        "future_materialization_required": True,
        "dry_run_only": True,
    }

    no_boundary = {
        "schema_version": "offline_replay_materialization_dry_run_no_boundary_28l_v1",
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
        "dataset_materialized": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28L",
    }

    gap_report = {
        "schema_version": "offline_replay_materialization_gap_report_28l_v1",
        "dataset_id": dataset_id,
        "missing_evidence": missing_evidence,
        "parse_error_keys": parse_error_keys,
        "blocking_gap_count": len(missing_evidence) + len(parse_error_keys),
        "blocking_gaps": missing_evidence + parse_error_keys,
        "materialization_dry_run_ready": len(missing_evidence) == 0 and len(parse_error_keys) == 0,
        "remarks": "28L catalogs materialization feasibility only; it does not transform evidence into replay frames.",
    }

    next_contract = {
        "schema_version": "offline_replay_next_materialization_contract_28l_v1",
        "dataset_id": dataset_id,
        "next_batch": "Batch 28M — materialize offline replay dataset candidate from the 28L dry-run, still not paper/live enablement.",
        "allowed_next_actions": [
            "read dry-run candidate index",
            "write replay-safe offline dataset candidate under run/replay",
            "write no-broker/no-live-redis proof",
            "write materialization coverage report",
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

    manifest = {
        "schema_version": "offline_replay_materialization_dry_run_manifest_28l_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OFFLINE_REPLAY_MATERIALIZATION_DRY_RUN_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "harness_manifest": str(harness_manifest_path),
        "output_root": str(output_root),
        "package_root": str(package_root),
        "evidence_dir": str(evidence_dir),
        "dry_run_completed": True,
        "materialization_dry_run_ready": gap_report["materialization_dry_run_ready"],
        "dataset_materialized": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28L",
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "next_batch": next_contract["next_batch"],
    }

    write_json(output_root / "00_dataset_materialization_dry_run_manifest.json", manifest)
    write_json(output_root / "01_input_surface_catalog.json", {
        "schema_version": "offline_replay_input_surface_catalog_28l_v1",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "evidence_catalog": evidence_catalog,
    })
    write_json(output_root / "02_replay_dataset_candidate_index.json", candidate_index)
    write_json(output_root / "03_service_surface_feasibility.json", service_surface_feasibility)
    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", no_boundary)
    write_json(output_root / "05_materialization_gap_report.json", gap_report)
    write_json(output_root / "06_next_materialization_contract.json", next_contract)

    result = {
        "schema_version": "offline_replay_materialization_dry_run_result_28l_v1",
        "accepted_for": "OFFLINE_REPLAY_MATERIALIZATION_DRY_RUN_ONLY",
        "dataset_id": dataset_id,
        "capture_id": capture_id,
        "output_root": str(output_root),
        "dry_run_completed": True,
        "materialization_dry_run_ready": gap_report["materialization_dry_run_ready"],
        "blocking_gap_count": gap_report["blocking_gap_count"],
        "missing_evidence": missing_evidence,
        "parse_error_keys": parse_error_keys,
        "written_count": len(DRY_RUN_ARTIFACTS),
        "dataset_materialized": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28L",
        "next_batch": next_contract["next_batch"],
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if gap_report["materialization_dry_run_ready"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
