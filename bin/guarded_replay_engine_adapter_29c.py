#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
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

def rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except Exception:
        return str(path)

def import_candidate(project_root: pathlib.Path, module_file: str, candidate_name: str) -> dict[str, Any]:
    module_path = project_root / module_file
    package_name = module_file.replace("/", ".")
    if package_name.endswith(".py"):
        package_name = package_name[:-3]

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    errors: list[str] = []
    selected_obj = None
    mode = None

    try:
        importlib.invalidate_caches()
        module = importlib.import_module(package_name)
        selected_obj = getattr(module, candidate_name)
        mode = "package"
    except Exception as exc:
        errors.append(f"package:{type(exc).__name__}: {exc}")

    if selected_obj is None:
        try:
            spec = importlib.util.spec_from_file_location("replay_engine_adapter_29c_direct", str(module_path))
            if spec is None or spec.loader is None:
                raise RuntimeError("spec/loader unavailable")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            selected_obj = getattr(module, candidate_name)
            mode = "direct"
        except Exception as exc:
            errors.append(f"direct:{type(exc).__name__}: {exc}")

    if selected_obj is None:
        return {"ok": False, "errors": errors}

    is_class = inspect.isclass(selected_obj)
    is_protocol = bool(getattr(selected_obj, "_is_protocol", False))
    is_abstract = bool(getattr(selected_obj, "__abstractmethods__", False))

    report: dict[str, Any] = {
        "ok": True,
        "mode": mode,
        "module_file": module_file,
        "candidate_name": candidate_name,
        "object_kind": "class" if is_class else "function" if inspect.isfunction(selected_obj) else type(selected_obj).__name__,
        "is_class": is_class,
        "is_protocol": is_protocol,
        "is_abstract": is_abstract,
        "callable": callable(selected_obj),
        "errors": errors,
    }

    try:
        report["constructor_signature"] = str(inspect.signature(selected_obj)) if callable(selected_obj) else None
    except Exception as exc:
        report["constructor_signature_error"] = f"{type(exc).__name__}: {exc}"

    for method_name in ("build_context", "execute", "run", "__call__"):
        if hasattr(selected_obj, method_name):
            try:
                method_obj = getattr(selected_obj, method_name)
                report[f"{method_name}_signature"] = str(inspect.signature(method_obj))
                report[f"{method_name}_present"] = True
            except Exception as exc:
                report[f"{method_name}_signature_error"] = f"{type(exc).__name__}: {exc}"
                report[f"{method_name}_present"] = True
        else:
            report[f"{method_name}_present"] = False

    return report

def ast_class_report(project_root: pathlib.Path, module_file: str, candidate_name: str) -> dict[str, Any]:
    path = project_root / module_file
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    report: dict[str, Any] = {
        "module_file": module_file,
        "candidate_name": candidate_name,
        "parse_ok": False,
        "class_found": False,
        "methods": [],
    }
    try:
        tree = ast.parse(text)
        report["parse_ok"] = True
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        return report

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == candidate_name:
            report["class_found"] = True
            report["class_lineno"] = getattr(node, "lineno", None)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in item.args.args]
                    defaults = len(item.args.defaults or [])
                    required_excluding_self = max(0, len(args) - 1 - defaults) if args and args[0] in ("self", "cls") else max(0, len(args) - defaults)
                    report["methods"].append({
                        "name": item.name,
                        "lineno": getattr(item, "lineno", None),
                        "args": args,
                        "required_arg_count_excluding_self": required_excluding_self,
                        "defaults_count": defaults,
                    })
            break
    return report

def known_value_keys() -> set[str]:
    return {
        "project_root",
        "root",
        "dataset_candidate_root",
        "dataset_root",
        "dataset_path",
        "input_root",
        "input_dir",
        "callable_output_root",
        "previous_output_root",
        "output_root",
        "out_root",
        "run_dir",
        "artifact_root",
        "no_broker",
        "no_live_redis",
        "observe_only",
        "dry_run",
    }

def signature_gap_from_ast(ast_report: dict[str, Any]) -> dict[str, Any]:
    known = known_value_keys()
    gaps: dict[str, Any] = {}
    for method in ast_report.get("methods", []):
        name = method.get("name")
        args = list(method.get("args") or [])
        effective = [x for x in args if x not in ("self", "cls")]
        required_count = int(method.get("required_arg_count_excluding_self") or 0)
        required_args = effective[:required_count]
        missing = [x for x in required_args if x not in known]
        mapped = [x for x in required_args if x in known]
        gaps[str(name)] = {
            "args": args,
            "required_args": required_args,
            "mapped_required_args": mapped,
            "missing_required_args": missing,
            "binding_ready": not missing,
        }
    return gaps

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 29C guarded ReplayEngine adapter contract builder.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--callable-output-root", required=True)
    parser.add_argument("--selection-root-29b", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--module-file", required=True)
    parser.add_argument("--candidate-name", required=True)
    parser.add_argument("--candidate-kind", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    callable_output_root = pathlib.Path(args.callable_output_root).resolve()
    selection_root_29b = pathlib.Path(args.selection_root_29b).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit("dataset candidate root must stay under run/replay")
    if not safe_under_run_replay(project_root, callable_output_root):
        raise SystemExit("callable output root must stay under run/replay")
    if not safe_under_run_replay(project_root, selection_root_29b):
        raise SystemExit("29B selection root must stay under run/replay")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output root must stay under run/replay")
    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run")

    output_root.mkdir(parents=True, exist_ok=True)

    candidate_report = import_candidate(project_root, args.module_file, args.candidate_name)
    source_report = ast_class_report(project_root, args.module_file, args.candidate_name)
    signature_gaps = signature_gap_from_ast(source_report)

    selection_manifest = load_json(selection_root_29b / "00_protocol_safe_candidate_selection_manifest.json")
    concrete_pool = load_json(selection_root_29b / "03_concrete_candidate_pool.json")
    callable_manifest = load_json(callable_output_root / "00_offline_replay_callable_manifest.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")

    execute_gap = signature_gaps.get("execute", {})
    build_context_gap = signature_gaps.get("build_context", {})
    constructor_gap = signature_gaps.get("__init__", {})

    concrete_candidate_ok = (
        candidate_report.get("ok") is True
        and candidate_report.get("is_protocol") is False
        and candidate_report.get("is_abstract") is False
        and source_report.get("class_found") is True
    )

    offline_inputs_ready = (
        callable_manifest.get("replay_run_completed") is True
        and isinstance(input_index.get("input_surfaces"), dict)
        and not input_index.get("missing_surfaces")
    )

    core_execution_binding_ready = bool(
        concrete_candidate_ok
        and offline_inputs_ready
        and execute_gap.get("binding_ready") is True
    )

    adapter_ready = bool(concrete_candidate_ok and offline_inputs_ready)

    if core_execution_binding_ready:
        next_batch = "Batch 29D — execute guarded concrete ReplayEngine adapter dry-run, still not paper/live enablement."
        next_path = "EXECUTION_BINDING_READY"
    else:
        next_batch = "Batch 29D — build ReplayEngine run_context/topology_plan/stage_executor bridge, still not paper/live enablement."
        next_path = "EXECUTION_CONTEXT_BRIDGE_REQUIRED"

    write_json(output_root / "00_guarded_replay_engine_adapter_manifest.json", {
        "schema_version": "guarded_replay_engine_adapter_manifest_29c_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_REPLAY_ENGINE_ADAPTER_BUILD_ONLY",
        "adapter_ready": adapter_ready,
        "core_execution_binding_ready": core_execution_binding_ready,
        "next_path": next_path,
        "selected_candidate": {
            "module_file": args.module_file,
            "name": args.candidate_name,
            "kind": args.candidate_kind,
        },
        "candidate_report": candidate_report,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29C",
        "next_batch": next_batch,
    })
    write_json(output_root / "01_replay_engine_signature_report.json", {
        "schema_version": "replay_engine_signature_report_29c_v1",
        "candidate_report": candidate_report,
        "source_report": source_report,
        "selection_manifest": selection_manifest,
        "concrete_pool_selected": concrete_pool.get("selected_candidate"),
    })
    write_json(output_root / "02_execution_argument_gap_report.json", {
        "schema_version": "execution_argument_gap_report_29c_v1",
        "signature_gaps": signature_gaps,
        "constructor_gap": constructor_gap,
        "build_context_gap": build_context_gap,
        "execute_gap": execute_gap,
        "core_execution_binding_ready": core_execution_binding_ready,
    })
    write_json(output_root / "03_offline_context_bridge_requirements.json", {
        "schema_version": "offline_context_bridge_requirements_29c_v1",
        "required_for_execute": execute_gap.get("missing_required_args", []),
        "likely_required_bridge_objects": {
            "run_context": "construct from replay contracts/dataset/materialized observe_only candidate",
            "topology_plan": "construct from replay topology contract without live services",
            "stage_executor": "construct offline-only stage executor or shim with no broker/no live Redis",
        },
        "offline_inputs_ready": offline_inputs_ready,
        "input_surface_count": len(input_index.get("input_surfaces", {}) if isinstance(input_index.get("input_surfaces"), dict) else {}),
        "missing_surfaces": input_index.get("missing_surfaces"),
    })
    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", {
        "schema_version": "guarded_replay_engine_adapter_no_boundary_29c_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29C",
    })
    write_json(output_root / "05_next_execution_context_contract.json", {
        "schema_version": "next_execution_context_contract_29c_v1",
        "next_batch": next_batch,
        "next_path": next_path,
        "core_execution_binding_ready": core_execution_binding_ready,
        "execute_missing_required_args": execute_gap.get("missing_required_args", []),
        "allowed_next_actions": [
            "build only offline run_context/topology_plan/stage_executor bridge if required",
            "do not start services",
            "do not read or write live Redis",
            "do not call broker APIs",
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
        "schema_version": "guarded_replay_engine_adapter_result_29c_v1",
        "accepted_for": "GUARDED_REPLAY_ENGINE_ADAPTER_BUILD_ONLY",
        "adapter_ready": adapter_ready,
        "core_execution_binding_ready": core_execution_binding_ready,
        "execute_missing_required_args": execute_gap.get("missing_required_args", []),
        "selected_candidate": {
            "module_file": args.module_file,
            "name": args.candidate_name,
            "kind": args.candidate_kind,
        },
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29C",
        "next_batch": next_batch,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if adapter_ready else 2

if __name__ == "__main__":
    raise SystemExit(main())
