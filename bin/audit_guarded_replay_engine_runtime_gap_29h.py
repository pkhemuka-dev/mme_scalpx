#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": f"{type(exc).__name__}: {exc}"}

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    return str(path.resolve()).startswith(str(replay_root) + "/")

def extract_error(*payloads: dict[str, Any]) -> str | None:
    candidates: list[Any] = []
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        candidates.append(payload.get("error"))
        candidates.append(payload.get("result_error"))
        candidates.append(payload.get("engine_error"))
        summary = payload.get("execution_result_summary")
        if isinstance(summary, dict):
            candidates.append(summary.get("error"))
        result_summary = payload.get("result_summary")
        if isinstance(result_summary, dict):
            candidates.append(result_summary.get("error"))
    for item in candidates:
        if item is None:
            continue
        if isinstance(item, str) and item.strip():
            return item.strip()
        if isinstance(item, dict):
            return json.dumps(item, sort_keys=True, default=str)
    return None

def classify_error(error_text: str | None) -> dict[str, Any]:
    text = (error_text or "").strip()
    lower = text.lower()

    if not text:
        return {
            "runtime_gap_kind": "UNKNOWN_RUNTIME_GAP_NO_ERROR_TEXT",
            "repair_path": "INSPECT_29G_EXECUTION_REPORTS_MANUALLY",
            "next_batch": "Batch 29I — manually inspect 29G execution report because no runtime error text was captured, still not paper/live enablement.",
        }

    if "missing" in lower and ("required" in lower or "argument" in lower):
        return {
            "runtime_gap_kind": "EXECUTE_ARGUMENT_BINDING_GAP",
            "repair_path": "REPAIR_REPLAY_ENGINE_EXECUTE_ARGUMENT_BINDING",
            "next_batch": "Batch 29I — repair guarded ReplayEngine.execute argument binding, still not paper/live enablement.",
        }

    if "attributeerror" in lower or "has no attribute" in lower:
        return {
            "runtime_gap_kind": "OFFLINE_CONTEXT_ATTRIBUTE_SHAPE_GAP",
            "repair_path": "REPAIR_OFFLINE_CONTEXT_OBJECT_ATTRIBUTE_SHAPE",
            "next_batch": "Batch 29I — repair offline context object attribute/shape expected by ReplayEngine.execute, still not paper/live enablement.",
        }

    if "typeerror" in lower:
        return {
            "runtime_gap_kind": "OFFLINE_CONTEXT_TYPE_OR_SIGNATURE_GAP",
            "repair_path": "REPAIR_OFFLINE_CONTEXT_TYPE_OR_REPLAYENGINE_CALL_SHAPE",
            "next_batch": "Batch 29I — repair offline context type/signature gap for ReplayEngine.execute, still not paper/live enablement.",
        }

    if "keyerror" in lower or "indexerror" in lower:
        return {
            "runtime_gap_kind": "OFFLINE_DATA_SHAPE_GAP",
            "repair_path": "REPAIR_OFFLINE_DATASET_OR_CONTEXT_MAPPING_SHAPE",
            "next_batch": "Batch 29I — repair offline dataset/context mapping shape expected by ReplayEngine.execute, still not paper/live enablement.",
        }

    if "not implemented" in lower or "notimplemented" in lower:
        return {
            "runtime_gap_kind": "REPLAY_ENGINE_STAGE_NOT_IMPLEMENTED_GAP",
            "repair_path": "ADD_OR_ROUTE_OFFLINE_STAGE_EXECUTION_SHIM",
            "next_batch": "Batch 29I — add or route offline stage execution shim for ReplayEngine dry-run, still not paper/live enablement.",
        }

    if "blocked unsafe import" in lower:
        return {
            "runtime_gap_kind": "GUARDED_IMPORT_BLOCKED_UNSAFE_DEPENDENCY",
            "repair_path": "REMOVE_OR_SHIM_UNSAFE_RUNTIME_DEPENDENCY_FROM_OFFLINE_REPLAY_PATH",
            "next_batch": "Batch 29I — remove or shim unsafe live dependency from guarded offline replay path, still not paper/live enablement.",
        }

    return {
        "runtime_gap_kind": "UNCLASSIFIED_REPLAY_ENGINE_RUNTIME_GAP",
        "repair_path": "NARROW_RUNTIME_GAP_REPAIR_FROM_29G_ERROR_TEXT",
        "next_batch": "Batch 29I — narrow repair for classified 29G ReplayEngine runtime gap, still not paper/live enablement.",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 29H guarded ReplayEngine runtime-gap audit.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--execute-root-29g", required=True)
    parser.add_argument("--shim-root-29f", required=True)
    parser.add_argument("--materialization-root-29e", required=True)
    parser.add_argument("--adapter-root-29c", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--audit-only", action="store_true", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    execute_root_29g = pathlib.Path(args.execute_root_29g).resolve()
    shim_root_29f = pathlib.Path(args.shim_root_29f).resolve()
    materialization_root_29e = pathlib.Path(args.materialization_root_29e).resolve()
    adapter_root_29c = pathlib.Path(args.adapter_root_29c).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    for label, path in {
        "execute_root_29g": execute_root_29g,
        "shim_root_29f": shim_root_29f,
        "materialization_root_29e": materialization_root_29e,
        "adapter_root_29c": adapter_root_29c,
        "output_root": output_root,
    }.items():
        if not safe_under_run_replay(project_root, path):
            raise SystemExit(f"{label} must stay under run/replay")

    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run and args.audit_only):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run/audit-only")

    output_root.mkdir(parents=True, exist_ok=True)

    execute_manifest = load_json(execute_root_29g / "00_guarded_replay_engine_execute_manifest.json")
    context_report = load_json(execute_root_29g / "01_context_reconstruction_report.json")
    engine_report = load_json(execute_root_29g / "02_engine_execution_report.json")
    output_summary = load_json(execute_root_29g / "03_execution_output_summary.json")
    boundary = load_json(execute_root_29g / "04_no_broker_no_live_redis_boundary.json")
    next_contract_29g = load_json(execute_root_29g / "05_next_replay_output_parity_contract.json")

    shim_manifest = load_json(shim_root_29f / "00_offline_run_context_shim_manifest.json")
    shim_context_report = load_json(shim_root_29f / "01_run_context_shim_materialization_report.json")
    materialization_manifest = load_json(materialization_root_29e / "00_context_object_materialization_manifest.json")
    topology_report = load_json(materialization_root_29e / "02_topology_plan_materialization_report.json")
    stage_report = load_json(materialization_root_29e / "03_stage_executor_materialization_report.json")
    adapter_manifest = load_json(adapter_root_29c / "00_guarded_replay_engine_adapter_manifest.json")
    adapter_gap = load_json(adapter_root_29c / "02_execution_argument_gap_report.json")

    error_text = extract_error(engine_report, output_summary, execute_manifest)
    classification = classify_error(error_text)

    context_ok = bool(
        execute_manifest.get("context_reconstruction_ready") is True
        and context_report.get("context_reconstruction_ready") is True
        and shim_manifest.get("full_context_reconstruction_ready") is True
        and materialization_manifest.get("topology_plan_materialized") is True
        and materialization_manifest.get("stage_executor_materialized") is True
    )

    engine_ready = bool(
        execute_manifest.get("engine_instance_ready") is True
        and engine_report.get("engine_instance_ready") is True
    )

    execution_attempted = bool(
        execute_manifest.get("execution_attempted") is True
        and engine_report.get("execution_attempted") is True
    )

    runtime_gap_confirmed = bool(
        context_ok
        and engine_ready
        and execution_attempted
        and execute_manifest.get("execution_ok") is False
        and engine_report.get("execution_ok") is False
        and output_summary.get("execution_ok") is False
        and execute_manifest.get("replay_run_completed") is False
    )

    write_json(output_root / "00_runtime_gap_audit_manifest.json", {
        "schema_version": "runtime_gap_audit_manifest_29h_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_REPLAY_ENGINE_RUNTIME_GAP_AUDIT_ONLY",
        "runtime_gap_confirmed": runtime_gap_confirmed,
        "context_reconstruction_ready": context_ok,
        "engine_instance_ready": engine_ready,
        "execution_attempted": execution_attempted,
        "execution_ok": False,
        "replay_core_executed": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "error_text": error_text,
        "classification": classification,
        "candidate_executed": False,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_29H",
        "next_batch": classification["next_batch"],
    })

    write_json(output_root / "01_engine_execution_report_audit.json", {
        "schema_version": "engine_execution_report_audit_29h_v1",
        "engine_report": engine_report,
        "output_summary": output_summary,
        "execute_manifest": execute_manifest,
        "error_text": error_text,
    })

    write_json(output_root / "02_context_reconstruction_audit.json", {
        "schema_version": "context_reconstruction_audit_29h_v1",
        "context_reconstruction_ready": context_ok,
        "context_report": context_report,
        "shim_manifest": shim_manifest,
        "shim_context_report": shim_context_report,
        "materialization_manifest": materialization_manifest,
        "topology_report": topology_report,
        "stage_report": stage_report,
        "adapter_manifest": adapter_manifest,
        "adapter_gap": adapter_gap,
    })

    write_json(output_root / "03_error_classification_report.json", {
        "schema_version": "error_classification_report_29h_v1",
        "error_text": error_text,
        "classification": classification,
        "next_contract_29g": next_contract_29g,
    })

    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", {
        "schema_version": "runtime_gap_audit_no_boundary_29h_v1",
        "source_boundary_29g": boundary,
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
        "candidate_executed": False,
        "replay_core_executed": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_29H",
    })

    write_json(output_root / "05_next_runtime_gap_repair_contract.json", {
        "schema_version": "next_runtime_gap_repair_contract_29h_v1",
        "next_batch": classification["next_batch"],
        "runtime_gap_kind": classification["runtime_gap_kind"],
        "repair_path": classification["repair_path"],
        "error_text": error_text,
        "allowed_next_actions": [
            "repair only the classified guarded offline ReplayEngine runtime gap",
            "keep all work under offline replay/parity tooling",
            "write outputs under run/replay only",
            "do not compare parity until ReplayEngine dry-run completes",
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
        "schema_version": "runtime_gap_audit_result_29h_v1",
        "accepted_for": "GUARDED_REPLAY_ENGINE_RUNTIME_GAP_AUDIT_ONLY",
        "runtime_gap_confirmed": runtime_gap_confirmed,
        "context_reconstruction_ready": context_ok,
        "engine_instance_ready": engine_ready,
        "execution_attempted": execution_attempted,
        "execution_ok": False,
        "replay_core_executed": False,
        "replay_run_completed": False,
        "comparison_completed": False,
        "runtime_gap_kind": classification["runtime_gap_kind"],
        "repair_path": classification["repair_path"],
        "error_text": error_text,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_29H",
        "next_batch": classification["next_batch"],
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if runtime_gap_confirmed else 2

if __name__ == "__main__":
    raise SystemExit(main())
