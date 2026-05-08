#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
import pathlib
import sys
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

def rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except Exception:
        return str(path)

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    return str(path.resolve()).startswith(str(replay_root) + "/")

def ast_signature_report(engine_file: pathlib.Path, class_name: str) -> dict[str, Any]:
    text = engine_file.read_text(encoding="utf-8", errors="replace") if engine_file.is_file() else ""
    report: dict[str, Any] = {
        "engine_file": str(engine_file),
        "engine_sha256": sha256_file(engine_file),
        "class_name": class_name,
        "parse_ok": False,
        "class_found": False,
        "init_found": False,
        "call_found": False,
        "init_args": [],
        "call_args": [],
        "methods": [],
        "class_lineno": None,
        "error": None,
    }
    try:
        tree = ast.parse(text)
        report["parse_ok"] = True
    except SyntaxError as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        return report

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            report["class_found"] = True
            report["class_lineno"] = getattr(node, "lineno", None)
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in item.args.args]
                    defaults_count = len(item.args.defaults or [])
                    required_count = max(0, len(args) - 1 - defaults_count)
                    rec = {
                        "name": item.name,
                        "lineno": getattr(item, "lineno", None),
                        "args": args,
                        "required_arg_count_excluding_self": required_count,
                        "defaults_count": defaults_count,
                    }
                    methods.append(rec)
                    if item.name == "__init__":
                        report["init_found"] = True
                        report["init_args"] = args
                        report["init_required_arg_count_excluding_self"] = required_count
                    if item.name == "__call__":
                        report["call_found"] = True
                        report["call_args"] = args
                        report["call_required_arg_count_excluding_self"] = required_count
            report["methods"] = methods
            break
    return report

def import_retry(project_root: pathlib.Path, module_file: str, class_name: str) -> dict[str, Any]:
    module_path = project_root / module_file
    package_name = module_file.replace("/", ".")
    if package_name.endswith(".py"):
        package_name = package_name[:-3]

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    package_result: dict[str, Any] = {"ok": False}
    direct_result: dict[str, Any] = {"ok": False}

    try:
        importlib.invalidate_caches()
        module = importlib.import_module(package_name)
        obj = getattr(module, class_name)
        package_result = {
            "ok": True,
            "module": package_name,
            "object_kind": "class" if inspect.isclass(obj) else type(obj).__name__,
            "init_signature": str(inspect.signature(obj)) if callable(obj) else None,
            "call_signature": str(inspect.signature(obj.__call__)) if inspect.isclass(obj) and hasattr(obj, "__call__") else None,
        }
    except Exception as exc:
        package_result = {"ok": False, "module": package_name, "error": f"{type(exc).__name__}: {exc}"}

    try:
        spec = importlib.util.spec_from_file_location("replay_core_candidate_28y_direct", str(module_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        obj = getattr(module, class_name)
        direct_result = {
            "ok": True,
            "module_file": str(module_path),
            "object_kind": "class" if inspect.isclass(obj) else type(obj).__name__,
            "init_signature": str(inspect.signature(obj)) if callable(obj) else None,
            "call_signature": str(inspect.signature(obj.__call__)) if inspect.isclass(obj) and hasattr(obj, "__call__") else None,
        }
    except Exception as exc:
        direct_result = {"ok": False, "module_file": str(module_path), "error": f"{type(exc).__name__}: {exc}"}

    return {
        "package_import": package_result,
        "direct_import": direct_result,
        "import_ready": package_result.get("ok") is True or direct_result.get("ok") is True,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 28Y ReplayEngineHook signature bridge repair.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--callable-output-root", required=True)
    parser.add_argument("--adapter-root-28x", required=True)
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
    adapter_root_28x = pathlib.Path(args.adapter_root_28x).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit("dataset candidate root must stay under run/replay")
    if not safe_under_run_replay(project_root, callable_output_root):
        raise SystemExit("callable output root must stay under run/replay")
    if not safe_under_run_replay(project_root, adapter_root_28x):
        raise SystemExit("28X adapter root must stay under run/replay")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output root must stay under run/replay")
    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run")

    output_root.mkdir(parents=True, exist_ok=True)

    engine_file = project_root / args.module_file
    source_report = ast_signature_report(engine_file, args.candidate_name)
    import_report = import_retry(project_root, args.module_file, args.candidate_name)

    prior_manifest = load_json(adapter_root_28x / "00_core_execution_adapter_manifest.json")
    prior_signature = load_json(adapter_root_28x / "02_candidate_import_signature_report.json")
    callable_manifest = load_json(callable_output_root / "00_offline_replay_callable_manifest.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")

    bridge_ready = (
        source_report.get("parse_ok") is True
        and source_report.get("class_found") is True
        and source_report.get("call_found") is True
        and callable_manifest.get("replay_engine_callable_invoked") is True
        and callable_manifest.get("replay_run_completed") is True
        and callable_manifest.get("replay_engine_core_completed") is False
        and isinstance(input_index.get("input_surfaces"), dict)
        and not input_index.get("missing_surfaces")
        and args.contract_only is True
    )

    import_execution_ready = bool(import_report.get("import_ready"))
    source_signature_bridge_ready = bool(bridge_ready)
    execution_ready = bool(bridge_ready and import_execution_ready)

    if execution_ready:
        next_batch = "Batch 28Z — execute ReplayEngineHook through guarded import-ready core adapter, still not paper/live enablement."
        readiness_kind = "IMPORT_READY_CORE_CANDIDATE"
    else:
        next_batch = "Batch 28Z — build explicit source-signature core shim/adapter for ReplayEngineHook, still not paper/live enablement."
        readiness_kind = "SOURCE_SIGNATURE_READY_IMPORT_NOT_READY" if source_signature_bridge_ready else "SOURCE_SIGNATURE_BRIDGE_NOT_READY"

    write_json(output_root / "00_candidate_signature_bridge_manifest.json", {
        "schema_version": "candidate_signature_bridge_manifest_28y_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "REPLAY_CORE_CANDIDATE_IMPORT_SIGNATURE_BRIDGE_ONLY",
        "candidate": {
            "module_file": args.module_file,
            "kind": args.candidate_kind,
            "name": args.candidate_name,
        },
        "source_signature_bridge_ready": source_signature_bridge_ready,
        "import_execution_ready": import_execution_ready,
        "core_execution_ready": execution_ready,
        "readiness_kind": readiness_kind,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28Y",
    })
    write_json(output_root / "01_prior_28x_diagnostics.json", {
        "schema_version": "prior_28x_diagnostics_28y_v1",
        "prior_manifest": prior_manifest,
        "prior_signature": prior_signature,
    })
    write_json(output_root / "02_engine_source_signature_report.json", {
        "schema_version": "engine_source_signature_report_28y_v1",
        "source_report": source_report,
    })
    write_json(output_root / "03_import_retry_diagnostics.json", {
        "schema_version": "import_retry_diagnostics_28y_v1",
        "import_report": import_report,
    })
    write_json(output_root / "04_execution_argument_bridge_contract.json", {
        "schema_version": "execution_argument_bridge_contract_28y_v1",
        "dataset_candidate_root": str(dataset_candidate_root),
        "callable_output_root": str(callable_output_root),
        "input_surface_count": len(input_index.get("input_surfaces", {}) if isinstance(input_index.get("input_surfaces"), dict) else {}),
        "missing_surfaces": input_index.get("missing_surfaces"),
        "source_signature_bridge_ready": source_signature_bridge_ready,
        "import_execution_ready": import_execution_ready,
        "core_execution_ready": execution_ready,
        "remarks": [
            "28Y does not execute ReplayEngineHook.",
            "If import_execution_ready=false, next batch must build a shim/adapter and not call unknown core code directly.",
        ],
    })
    write_json(output_root / "05_no_broker_no_live_redis_boundary.json", {
        "schema_version": "candidate_signature_bridge_no_boundary_28y_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28Y",
    })
    write_json(output_root / "06_next_core_execution_contract.json", {
        "schema_version": "next_core_execution_contract_28y_v1",
        "next_batch": next_batch,
        "readiness_kind": readiness_kind,
        "core_execution_ready": execution_ready,
        "source_signature_bridge_ready": source_signature_bridge_ready,
        "import_execution_ready": import_execution_ready,
        "allowed_next_actions": [
            "execute ReplayEngineHook only if import and constructor/call bridge are proven",
            "otherwise build explicit shim/adapter from source signature",
            "use only offline dataset/callable outputs",
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
        "schema_version": "candidate_signature_bridge_result_28y_v1",
        "accepted_for": "REPLAY_CORE_CANDIDATE_IMPORT_SIGNATURE_BRIDGE_ONLY",
        "source_signature_bridge_ready": source_signature_bridge_ready,
        "import_execution_ready": import_execution_ready,
        "core_execution_ready": execution_ready,
        "readiness_kind": readiness_kind,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28Y",
        "next_batch": next_batch,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if source_signature_bridge_ready else 2

if __name__ == "__main__":
    raise SystemExit(main())
