#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import importlib
import importlib.util
import inspect
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

def import_surface(project_root: pathlib.Path, module_file: str, name: str) -> dict[str, Any]:
    module_path = project_root / module_file
    package_name = module_file.replace("/", ".")
    if package_name.endswith(".py"):
        package_name = package_name[:-3]

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    errors: list[str] = []

    try:
        importlib.invalidate_caches()
        module = importlib.import_module(package_name)
        obj = getattr(module, name)
        return {
            "ok": True,
            "mode": "package",
            "object": obj,
            "errors": errors,
        }
    except Exception as exc:
        errors.append(f"package:{type(exc).__name__}: {exc}")

    try:
        spec = importlib.util.spec_from_file_location("replay_context_materializer_29e_direct", str(module_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        obj = getattr(module, name)
        return {
            "ok": True,
            "mode": "direct",
            "object": obj,
            "errors": errors,
        }
    except Exception as exc:
        errors.append(f"direct:{type(exc).__name__}: {exc}")

    return {
        "ok": False,
        "errors": errors,
    }

def value_map(
    project_root: pathlib.Path,
    dataset_candidate_root: pathlib.Path,
    callable_output_root: pathlib.Path,
    adapter_root_29c: pathlib.Path,
    bridge_root_29d: pathlib.Path,
    output_root: pathlib.Path,
) -> dict[str, Any]:
    dataset_manifest = load_json(dataset_candidate_root / "00_dataset_candidate_manifest.json")
    materialized_index = load_json(dataset_candidate_root / "02_materialized_file_index.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")
    bridge_manifest = load_json(bridge_root_29d / "00_offline_context_bridge_manifest.json")
    adapter_manifest = load_json(adapter_root_29c / "00_guarded_replay_engine_adapter_manifest.json")

    return {
        "project_root": project_root,
        "root": project_root,
        "dataset_candidate_root": dataset_candidate_root,
        "dataset_root": dataset_candidate_root,
        "dataset_path": dataset_candidate_root,
        "input_root": dataset_candidate_root,
        "input_dir": dataset_candidate_root,
        "callable_output_root": callable_output_root,
        "previous_output_root": callable_output_root,
        "adapter_root_29c": adapter_root_29c,
        "bridge_root_29d": bridge_root_29d,
        "output_root": output_root,
        "out_root": output_root,
        "run_dir": output_root,
        "artifact_root": output_root,
        "dataset_manifest": dataset_manifest,
        "materialized_index": materialized_index,
        "input_index": input_index,
        "bridge_manifest": bridge_manifest,
        "adapter_manifest": adapter_manifest,
        "no_broker": True,
        "no_live_redis": True,
        "observe_only": True,
        "dry_run": True,
    }

def bind_kwargs(sig: inspect.Signature, values: dict[str, Any]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    missing: list[str] = []
    optional_unmapped: list[str] = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if name in values:
            kwargs[name] = values[name]
        elif param.default is inspect.Parameter.empty:
            missing.append(name)
        else:
            optional_unmapped.append(name)

    return {
        "ok": not missing,
        "kwargs": kwargs,
        "missing_required": missing,
        "optional_unmapped": optional_unmapped,
        "signature": str(sig),
    }

def summarize_object(obj: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "type": type(obj).__name__,
        "module": type(obj).__module__,
        "repr": repr(obj)[:2000],
    }
    if dataclasses.is_dataclass(obj):
        try:
            summary["dataclass"] = True
            summary["dataclass_fields"] = [f.name for f in dataclasses.fields(obj)]
        except Exception:
            summary["dataclass"] = True
    if hasattr(obj, "__dict__"):
        try:
            summary["dict_keys"] = sorted([str(k) for k in vars(obj).keys()])[:100]
        except Exception:
            pass
    return summary

def materialize_from_candidates(
    *,
    target_name: str,
    candidates: list[dict[str, Any]],
    project_root: pathlib.Path,
    values: dict[str, Any],
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("is_protocol_like") is True:
            attempts.append({"candidate": candidate, "ok": False, "reason": "protocol_like_excluded"})
            continue

        module_file = str(candidate.get("module_file") or "")
        name = str(candidate.get("name") or "")
        kind = str(candidate.get("kind") or "")

        if not module_file or not name:
            attempts.append({"candidate": candidate, "ok": False, "reason": "missing_module_or_name"})
            continue

        imported = import_surface(project_root, module_file, name)
        if not imported.get("ok"):
            attempts.append({"candidate": candidate, "ok": False, "reason": "import_failed", "import_errors": imported.get("errors")})
            continue

        obj = imported["object"]
        is_class = inspect.isclass(obj)
        is_abstract = bool(getattr(obj, "__abstractmethods__", False))
        is_protocol = bool(getattr(obj, "_is_protocol", False))

        if is_protocol or is_abstract:
            attempts.append({
                "candidate": candidate,
                "ok": False,
                "reason": "runtime_protocol_or_abstract_excluded",
                "is_protocol": is_protocol,
                "is_abstract": is_abstract,
            })
            continue

        try:
            sig = inspect.signature(obj)
            binding = bind_kwargs(sig, values)
        except Exception as exc:
            attempts.append({"candidate": candidate, "ok": False, "reason": "signature_failed", "error": f"{type(exc).__name__}: {exc}"})
            continue

        if not binding["ok"]:
            attempts.append({
                "candidate": candidate,
                "ok": False,
                "reason": "binding_missing_required",
                "signature": binding["signature"],
                "missing_required": binding["missing_required"],
                "optional_unmapped": binding["optional_unmapped"],
            })
            continue

        try:
            if is_class:
                materialized = obj(**binding["kwargs"])
            elif callable(obj):
                materialized = obj(**binding["kwargs"])
            else:
                attempts.append({"candidate": candidate, "ok": False, "reason": "not_callable"})
                continue
        except Exception as exc:
            attempts.append({
                "candidate": candidate,
                "ok": False,
                "reason": "construction_failed",
                "signature": binding["signature"],
                "mapped_kwargs": sorted(binding["kwargs"].keys()),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue

        return {
            "target": target_name,
            "materialized": True,
            "selected_candidate": candidate,
            "import_mode": imported.get("mode"),
            "signature": binding["signature"],
            "mapped_kwargs": sorted(binding["kwargs"].keys()),
            "object_summary": summarize_object(materialized),
            "attempts": attempts,
        }

    return {
        "target": target_name,
        "materialized": False,
        "selected_candidate": None,
        "attempts": attempts,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 29E guarded offline ReplayEngine context materializer.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--callable-output-root", required=True)
    parser.add_argument("--adapter-root-29c", required=True)
    parser.add_argument("--bridge-root-29d", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--materialize-only", action="store_true", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    callable_output_root = pathlib.Path(args.callable_output_root).resolve()
    adapter_root_29c = pathlib.Path(args.adapter_root_29c).resolve()
    bridge_root_29d = pathlib.Path(args.bridge_root_29d).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    for label, path in {
        "dataset_candidate_root": dataset_candidate_root,
        "callable_output_root": callable_output_root,
        "adapter_root_29c": adapter_root_29c,
        "bridge_root_29d": bridge_root_29d,
        "output_root": output_root,
    }.items():
        if not safe_under_run_replay(project_root, path):
            raise SystemExit(f"{label} must stay under run/replay")

    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run and args.materialize_only):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run/materialize-only")

    output_root.mkdir(parents=True, exist_ok=True)

    values = value_map(
        project_root=project_root,
        dataset_candidate_root=dataset_candidate_root,
        callable_output_root=callable_output_root,
        adapter_root_29c=adapter_root_29c,
        bridge_root_29d=bridge_root_29d,
        output_root=output_root,
    )

    run_context_report = load_json(bridge_root_29d / "01_run_context_surface_report.json")
    topology_plan_report = load_json(bridge_root_29d / "02_topology_plan_surface_report.json")
    stage_executor_report = load_json(bridge_root_29d / "03_stage_executor_surface_report.json")
    bridge_manifest = load_json(bridge_root_29d / "00_offline_context_bridge_manifest.json")

    run_context_result = materialize_from_candidates(
        target_name="run_context",
        candidates=run_context_report.get("candidate_surfaces", []) if isinstance(run_context_report.get("candidate_surfaces"), list) else [],
        project_root=project_root,
        values=values,
    )
    topology_plan_result = materialize_from_candidates(
        target_name="topology_plan",
        candidates=topology_plan_report.get("candidate_surfaces", []) if isinstance(topology_plan_report.get("candidate_surfaces"), list) else [],
        project_root=project_root,
        values=values,
    )
    stage_executor_result = materialize_from_candidates(
        target_name="stage_executor",
        candidates=stage_executor_report.get("candidate_surfaces", []) if isinstance(stage_executor_report.get("candidate_surfaces"), list) else [],
        project_root=project_root,
        values=values,
    )

    context_objects_materialized = bool(
        run_context_result.get("materialized")
        and topology_plan_result.get("materialized")
        and stage_executor_result.get("materialized")
    )

    if context_objects_materialized:
        next_batch = "Batch 29F — build guarded ReplayEngine execution dry-run using materialized offline context reconstruction contract, still not paper/live enablement."
        next_path = "CONTEXT_OBJECTS_MATERIALIZED"
    else:
        next_batch = "Batch 29F — add explicit offline context-object shim for unmaterialized ReplayEngine inputs, still not paper/live enablement."
        next_path = "CONTEXT_OBJECT_SHIM_REQUIRED"

    write_json(output_root / "00_context_object_materialization_manifest.json", {
        "schema_version": "context_object_materialization_manifest_29e_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "REPLAY_ENGINE_CONTEXT_OBJECT_MATERIALIZATION_ONLY",
        "context_objects_materialized": context_objects_materialized,
        "next_path": next_path,
        "run_context_materialized": bool(run_context_result.get("materialized")),
        "topology_plan_materialized": bool(topology_plan_result.get("materialized")),
        "stage_executor_materialized": bool(stage_executor_result.get("materialized")),
        "bridge_manifest": bridge_manifest,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29E",
        "next_batch": next_batch,
    })

    write_json(output_root / "01_run_context_materialization_report.json", {
        "schema_version": "run_context_materialization_report_29e_v1",
        "result": run_context_result,
    })
    write_json(output_root / "02_topology_plan_materialization_report.json", {
        "schema_version": "topology_plan_materialization_report_29e_v1",
        "result": topology_plan_result,
    })
    write_json(output_root / "03_stage_executor_materialization_report.json", {
        "schema_version": "stage_executor_materialization_report_29e_v1",
        "result": stage_executor_result,
    })
    write_json(output_root / "04_reconstruction_contract.json", {
        "schema_version": "reconstruction_contract_29e_v1",
        "context_objects_materialized": context_objects_materialized,
        "selected_surfaces": {
            "run_context": run_context_result.get("selected_candidate"),
            "topology_plan": topology_plan_result.get("selected_candidate"),
            "stage_executor": stage_executor_result.get("selected_candidate"),
        },
        "value_keys_available": sorted(values.keys()),
        "reconstruction_note": "29E validates construction/materialization only. Objects are not serialized for execution; 29F must reconstruct them from this contract in a guarded process.",
    })
    write_json(output_root / "05_no_broker_no_live_redis_boundary.json", {
        "schema_version": "context_materialization_no_boundary_29e_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29E",
    })
    write_json(output_root / "06_next_guarded_execution_contract.json", {
        "schema_version": "next_guarded_execution_contract_29e_v1",
        "next_batch": next_batch,
        "next_path": next_path,
        "context_objects_materialized": context_objects_materialized,
        "allowed_next_actions": [
            "reconstruct materialized offline context objects only inside guarded 29F process",
            "call ReplayEngine.execute only if context reconstruction and no-broker/no-live-Redis gates pass",
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
        "schema_version": "context_object_materialization_result_29e_v1",
        "accepted_for": "REPLAY_ENGINE_CONTEXT_OBJECT_MATERIALIZATION_ONLY",
        "context_objects_materialized": context_objects_materialized,
        "run_context_materialized": bool(run_context_result.get("materialized")),
        "topology_plan_materialized": bool(topology_plan_result.get("materialized")),
        "stage_executor_materialized": bool(stage_executor_result.get("materialized")),
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29E",
        "next_batch": next_batch,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
