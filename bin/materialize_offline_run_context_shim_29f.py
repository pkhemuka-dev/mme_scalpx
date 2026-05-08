#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import pathlib
import sys
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

def summarize_object(obj: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": type(obj).__name__,
        "module": type(obj).__module__,
        "repr": repr(obj)[:2000],
    }
    if hasattr(obj, "as_dict"):
        try:
            payload["as_dict"] = obj.as_dict()
        except Exception as exc:
            payload["as_dict_error"] = f"{type(exc).__name__}: {exc}"
    if hasattr(obj, "__dict__"):
        try:
            payload["dict_keys"] = sorted([str(k) for k in vars(obj).keys()])[:100]
        except Exception:
            pass
    return payload

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 29F offline run-context shim materializer.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--callable-output-root", required=True)
    parser.add_argument("--materialization-root-29e", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--shim-only", action="store_true", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    callable_output_root = pathlib.Path(args.callable_output_root).resolve()
    materialization_root_29e = pathlib.Path(args.materialization_root_29e).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    for label, path in {
        "dataset_candidate_root": dataset_candidate_root,
        "callable_output_root": callable_output_root,
        "materialization_root_29e": materialization_root_29e,
        "output_root": output_root,
    }.items():
        if not safe_under_run_replay(project_root, path):
            raise SystemExit(f"{label} must stay under run/replay")

    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run and args.shim_only):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run/shim-only")

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    output_root.mkdir(parents=True, exist_ok=True)

    prior_29e_manifest = load_json(materialization_root_29e / "00_context_object_materialization_manifest.json")
    prior_run_context_report = load_json(materialization_root_29e / "01_run_context_materialization_report.json")
    prior_topology_report = load_json(materialization_root_29e / "02_topology_plan_materialization_report.json")
    prior_stage_report = load_json(materialization_root_29e / "03_stage_executor_materialization_report.json")
    prior_reconstruction = load_json(materialization_root_29e / "04_reconstruction_contract.json")
    dataset_manifest = load_json(dataset_candidate_root / "00_dataset_candidate_manifest.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")

    import_ok = False
    import_error = None
    run_context_obj = None

    try:
        module = importlib.import_module("app.mme_scalpx.replay.offline_context_shim")
        factory = getattr(module, "build_offline_replay_run_context")
        run_context_obj = factory(
            project_root=project_root,
            dataset_candidate_root=dataset_candidate_root,
            callable_output_root=callable_output_root,
            materialization_root_29e=materialization_root_29e,
            output_root=output_root,
            metadata={
                "source_batch": "29F",
                "prior_29e_context_objects_materialized": prior_29e_manifest.get("context_objects_materialized"),
                "prior_29e_run_context_materialized": prior_29e_manifest.get("run_context_materialized"),
                "prior_29e_topology_plan_materialized": prior_29e_manifest.get("topology_plan_materialized"),
                "prior_29e_stage_executor_materialized": prior_29e_manifest.get("stage_executor_materialized"),
                "dataset_manifest_present": bool(dataset_manifest),
                "input_surface_count": len(input_index.get("input_surfaces", {}) if isinstance(input_index.get("input_surfaces"), dict) else {}),
            },
        )
        import_ok = True
    except Exception as exc:
        import_error = f"{type(exc).__name__}: {exc}"

    run_context_shim_materialized = import_ok and run_context_obj is not None
    topology_plan_reusable = prior_29e_manifest.get("topology_plan_materialized") is True
    stage_executor_reusable = prior_29e_manifest.get("stage_executor_materialized") is True
    full_context_reconstruction_ready = bool(
        run_context_shim_materialized and topology_plan_reusable and stage_executor_reusable
    )

    if full_context_reconstruction_ready:
        next_batch = "Batch 29G — build guarded ReplayEngine execution dry-run using offline shim/context reconstruction, still not paper/live enablement."
        next_path = "OFFLINE_CONTEXT_RECONSTRUCTION_READY"
    else:
        next_batch = "Batch 29G — repair offline context reconstruction before any ReplayEngine execution, still not paper/live enablement."
        next_path = "OFFLINE_CONTEXT_RECONSTRUCTION_NOT_READY"

    write_json(output_root / "00_offline_run_context_shim_manifest.json", {
        "schema_version": "offline_run_context_shim_manifest_29f_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OFFLINE_RUN_CONTEXT_SHIM_MATERIALIZATION_ONLY",
        "run_context_shim_materialized": run_context_shim_materialized,
        "topology_plan_reusable_from_29e": topology_plan_reusable,
        "stage_executor_reusable_from_29e": stage_executor_reusable,
        "full_context_reconstruction_ready": full_context_reconstruction_ready,
        "next_path": next_path,
        "candidate_executed": False,
        "replay_core_executed": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29F",
        "next_batch": next_batch,
    })

    write_json(output_root / "01_run_context_shim_materialization_report.json", {
        "schema_version": "run_context_shim_materialization_report_29f_v1",
        "import_ok": import_ok,
        "import_error": import_error,
        "run_context_shim_materialized": run_context_shim_materialized,
        "object_summary": summarize_object(run_context_obj) if run_context_obj is not None else None,
        "prior_run_context_report": prior_run_context_report,
    })

    write_json(output_root / "02_topology_stage_reuse_contract.json", {
        "schema_version": "topology_stage_reuse_contract_29f_v1",
        "topology_plan_reusable_from_29e": topology_plan_reusable,
        "stage_executor_reusable_from_29e": stage_executor_reusable,
        "prior_topology_report": prior_topology_report,
        "prior_stage_report": prior_stage_report,
    })

    write_json(output_root / "03_reconstruction_contract.json", {
        "schema_version": "reconstruction_contract_29f_v1",
        "full_context_reconstruction_ready": full_context_reconstruction_ready,
        "run_context_source": "app.mme_scalpx.replay.offline_context_shim.build_offline_replay_run_context",
        "topology_plan_source": "29E selected topology_plan materialization contract",
        "stage_executor_source": "29E selected stage_executor materialization contract",
        "prior_reconstruction_contract_29e": prior_reconstruction,
        "reconstruction_note": "29F materializes only run_context shim and validates reuse of 29E topology/stage results. ReplayEngine.execute is not called.",
    })

    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", {
        "schema_version": "offline_run_context_shim_no_boundary_29f_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29F",
    })

    write_json(output_root / "05_next_guarded_execution_contract.json", {
        "schema_version": "next_guarded_execution_contract_29f_v1",
        "next_batch": next_batch,
        "next_path": next_path,
        "full_context_reconstruction_ready": full_context_reconstruction_ready,
        "allowed_next_actions": [
            "reconstruct offline run_context/topology_plan/stage_executor inside guarded process",
            "call ReplayEngine.execute only if reconstruction and no-live gates pass",
            "write outputs under run/replay only",
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
        "schema_version": "offline_run_context_shim_result_29f_v1",
        "accepted_for": "OFFLINE_RUN_CONTEXT_SHIM_MATERIALIZATION_ONLY",
        "run_context_shim_materialized": run_context_shim_materialized,
        "topology_plan_reusable_from_29e": topology_plan_reusable,
        "stage_executor_reusable_from_29e": stage_executor_reusable,
        "full_context_reconstruction_ready": full_context_reconstruction_ready,
        "candidate_executed": False,
        "replay_core_executed": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29F",
        "next_batch": next_batch,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if run_context_shim_materialized else 2

if __name__ == "__main__":
    raise SystemExit(main())
