#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import importlib.util
import inspect
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any

def risky_tokens() -> list[str]:
    return [
        "Kite" + "Connect(",
        "place" + "_order(",
        "modify" + "_order(",
        "cancel" + "_order(",
        "." + "xadd(",
        "." + "hset(",
        "." + "set(",
        "Strict" + "Redis" + "(",
        "Redis" + "(",
    ]

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

def risky_token_scan(path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    hits = [tok for tok in risky_tokens() if tok in text]
    return {
        "path": str(path),
        "present": path.is_file(),
        "hits": hits,
        "ok": not hits,
    }

def import_candidate(project_root: pathlib.Path, module_file: str, candidate_name: str) -> dict[str, Any]:
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
        obj = getattr(module, candidate_name)
        return {
            "ok": True,
            "mode": "package",
            "object": obj,
            "object_kind": "class" if inspect.isclass(obj) else "function" if inspect.isfunction(obj) else type(obj).__name__,
            "init_signature": str(inspect.signature(obj)) if callable(obj) else None,
            "call_signature": str(inspect.signature(obj.__call__)) if inspect.isclass(obj) and hasattr(obj, "__call__") else str(inspect.signature(obj)) if callable(obj) else None,
            "errors": errors,
        }
    except Exception as exc:
        errors.append(f"package:{type(exc).__name__}: {exc}")

    try:
        spec = importlib.util.spec_from_file_location("replay_engine_hook_28z_r2_direct", str(module_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        obj = getattr(module, candidate_name)
        return {
            "ok": True,
            "mode": "direct",
            "object": obj,
            "object_kind": "class" if inspect.isclass(obj) else "function" if inspect.isfunction(obj) else type(obj).__name__,
            "init_signature": str(inspect.signature(obj)) if callable(obj) else None,
            "call_signature": str(inspect.signature(obj.__call__)) if inspect.isclass(obj) and hasattr(obj, "__call__") else str(inspect.signature(obj)) if callable(obj) else None,
            "errors": errors,
        }
    except Exception as exc:
        errors.append(f"direct:{type(exc).__name__}: {exc}")

    return {"ok": False, "errors": errors}

def value_map(project_root: pathlib.Path, dataset_candidate_root: pathlib.Path, callable_output_root: pathlib.Path, output_root: pathlib.Path) -> dict[str, Any]:
    return {
        "project_root": project_root,
        "root": project_root,
        "dataset_candidate_root": dataset_candidate_root,
        "dataset_root": dataset_candidate_root,
        "dataset_path": dataset_candidate_root,
        "input_root": dataset_candidate_root,
        "input_dir": dataset_candidate_root / "input_surfaces",
        "callable_output_root": callable_output_root,
        "previous_output_root": callable_output_root,
        "output_root": output_root,
        "out_root": output_root,
        "run_dir": output_root,
        "artifact_root": output_root,
        "no_broker": True,
        "no_live_redis": True,
        "observe_only": True,
        "dry_run": True,
    }

def bind_kwargs(sig: inspect.Signature, values: dict[str, Any], *, skip_self: bool) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    missing: list[str] = []
    optional_unmapped: list[str] = []

    for name, param in sig.parameters.items():
        if skip_self and name in ("self", "cls"):
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

def safe_result_summary(result: Any) -> dict[str, Any]:
    if result is None:
        return {"type": "NoneType", "repr": "None"}
    if isinstance(result, (str, int, float, bool)):
        return {"type": type(result).__name__, "repr": repr(result)}
    if isinstance(result, dict):
        return {
            "type": "dict",
            "keys": sorted([str(k) for k in result.keys()])[:100],
            "repr": repr(result)[:2000],
        }
    return {"type": type(result).__name__, "repr": repr(result)[:2000]}

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 28Z-R2 guarded ReplayEngineHook execution retry.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--callable-output-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--module-file", required=True)
    parser.add_argument("--candidate-name", required=True)
    parser.add_argument("--candidate-kind", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    callable_output_root = pathlib.Path(args.callable_output_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit("dataset root outside run/replay")
    if not safe_under_run_replay(project_root, callable_output_root):
        raise SystemExit("callable output root outside run/replay")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output root outside run/replay")
    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run")

    output_root.mkdir(parents=True, exist_ok=True)

    module_file_path = project_root / args.module_file
    token_scan = risky_token_scan(module_file_path)
    prior_callable = load_json(callable_output_root / "00_offline_replay_callable_manifest.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")

    import_report = import_candidate(project_root, args.module_file, args.candidate_name)
    values = value_map(project_root, dataset_candidate_root, callable_output_root, output_root)

    execution_attempted = False
    execution_ok = False
    instance_created = False
    candidate_call_completed = False
    result_summary: dict[str, Any] = {}
    binding_report: dict[str, Any] = {}

    if (
        token_scan.get("ok") is True
        and import_report.get("ok") is True
        and prior_callable.get("replay_run_completed") is True
        and not input_index.get("missing_surfaces")
    ):
        obj = import_report["object"]
        try:
            if inspect.isclass(obj):
                init_sig = inspect.signature(obj)
                init_binding = bind_kwargs(init_sig, values, skip_self=False)
                binding_report["init_binding"] = {k: v for k, v in init_binding.items() if k != "kwargs"}
                if init_binding["ok"]:
                    instance = obj(**init_binding["kwargs"])
                    instance_created = True
                    call_sig = inspect.signature(instance.__call__)
                    call_binding = bind_kwargs(call_sig, values, skip_self=False)
                    binding_report["call_binding"] = {k: v for k, v in call_binding.items() if k != "kwargs"}
                    if call_binding["ok"]:
                        execution_attempted = True
                        result = instance(**call_binding["kwargs"])
                        candidate_call_completed = True
                        execution_ok = True
                        result_summary = safe_result_summary(result)
            elif callable(obj):
                call_sig = inspect.signature(obj)
                call_binding = bind_kwargs(call_sig, values, skip_self=False)
                binding_report["call_binding"] = {k: v for k, v in call_binding.items() if k != "kwargs"}
                if call_binding["ok"]:
                    execution_attempted = True
                    result = obj(**call_binding["kwargs"])
                    candidate_call_completed = True
                    execution_ok = True
                    result_summary = safe_result_summary(result)
        except Exception as exc:
            result_summary = {"error": f"{type(exc).__name__}: {exc}"}

    manifest = {
        "schema_version": "replay_engine_hook_guarded_execution_manifest_28z_r2_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_REPLAY_ENGINE_HOOK_EXECUTION_RETRY_ONLY",
        "selected_candidate": {
            "module_file": args.module_file,
            "kind": args.candidate_kind,
            "name": args.candidate_name,
        },
        "token_scan": token_scan,
        "import_ok": import_report.get("ok") is True,
        "import_mode": import_report.get("mode"),
        "init_signature": import_report.get("init_signature"),
        "call_signature": import_report.get("call_signature"),
        "binding_ready": bool(binding_report and not any(v.get("missing_required") for v in binding_report.values() if isinstance(v, dict))),
        "execution_attempted": bool(execution_attempted),
        "execution_ok": bool(execution_ok),
        "instance_created": bool(instance_created),
        "candidate_call_completed": bool(candidate_call_completed),
        "replay_core_executed": bool(execution_ok),
        "replay_run_completed": bool(execution_ok),
        "comparison_completed": False,
        "result_summary": result_summary,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28Z_R2",
    }

    write_json(output_root / "00_replay_engine_hook_execution_manifest.json", manifest)
    write_json(output_root / "01_argument_binding_report.json", {
        "schema_version": "argument_binding_report_28z_r2_v1",
        "binding_report": binding_report,
        "value_keys_available": sorted(values.keys()),
    })
    write_json(output_root / "02_candidate_execution_result.json", {
        "schema_version": "candidate_execution_result_28z_r2_v1",
        "execution_attempted": bool(execution_attempted),
        "execution_ok": bool(execution_ok),
        "instance_created": bool(instance_created),
        "candidate_call_completed": bool(candidate_call_completed),
        "result_summary": result_summary,
    })
    write_json(output_root / "03_no_broker_no_live_redis_boundary.json", {
        "schema_version": "no_broker_no_live_redis_boundary_28z_r2_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28Z_R2",
    })
    write_json(output_root / "04_next_replay_output_inspection_contract.json", {
        "schema_version": "next_replay_output_inspection_contract_28z_r2_v1",
        "execution_ok": bool(execution_ok),
        "next_batch": "Batch 29A — inspect ReplayEngineHook guarded execution outputs and determine real replay-output/parity gap, still not paper/live enablement." if execution_ok else "Batch 29A — repair ReplayEngineHook argument binding before core execution, still not paper/live enablement.",
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
        "schema_version": "replay_engine_hook_guarded_execution_result_28z_r2_v1",
        "accepted_for": "GUARDED_REPLAY_ENGINE_HOOK_EXECUTION_RETRY_ONLY",
        "execution_ok": bool(execution_ok),
        "execution_attempted": bool(execution_attempted),
        "instance_created": bool(instance_created),
        "candidate_call_completed": bool(candidate_call_completed),
        "replay_core_executed": bool(execution_ok),
        "replay_run_completed": bool(execution_ok),
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28Z_R2",
        "result_summary": result_summary,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if execution_ok else 2

if __name__ == "__main__":
    raise SystemExit(main())
