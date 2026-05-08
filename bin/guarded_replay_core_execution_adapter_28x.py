#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import inspect
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

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    return str(path.resolve()).startswith(str(replay_root) + "/")

def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": f"{type(exc).__name__}: {exc}"}

def import_candidate(project_root: pathlib.Path, module_file: str, candidate_name: str) -> dict[str, Any]:
    module_path = project_root / module_file
    package_name = module_file.replace("/", ".")
    if package_name.endswith(".py"):
        package_name = package_name[:-3]

    package_result: dict[str, Any] = {"ok": False}
    direct_result: dict[str, Any] = {"ok": False}
    selected_obj = None

    try:
        importlib.invalidate_caches()
        module = importlib.import_module(package_name)
        obj = getattr(module, candidate_name)
        package_result = {
            "ok": True,
            "module": package_name,
            "object_present": True,
            "object_kind": "class" if inspect.isclass(obj) else "function" if inspect.isfunction(obj) else type(obj).__name__,
            "signature": str(inspect.signature(obj)) if callable(obj) else None,
        }
        selected_obj = obj
    except Exception as exc:
        package_result = {"ok": False, "module": package_name, "error": f"{type(exc).__name__}: {exc}"}

    if selected_obj is None:
        try:
            spec = importlib.util.spec_from_file_location("replay_core_candidate_28x_direct", str(module_path))
            if spec is None or spec.loader is None:
                raise RuntimeError("spec/loader unavailable")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            obj = getattr(module, candidate_name)
            direct_result = {
                "ok": True,
                "module_file": str(module_path),
                "object_present": True,
                "object_kind": "class" if inspect.isclass(obj) else "function" if inspect.isfunction(obj) else type(obj).__name__,
                "signature": str(inspect.signature(obj)) if callable(obj) else None,
            }
            selected_obj = obj
        except Exception as exc:
            direct_result = {"ok": False, "module_file": str(module_path), "error": f"{type(exc).__name__}: {exc}"}

    call_signature = None
    init_signature = None
    object_kind = None
    callable_ready = False

    if selected_obj is not None:
        object_kind = "class" if inspect.isclass(selected_obj) else "function" if inspect.isfunction(selected_obj) else type(selected_obj).__name__
        try:
            init_signature = str(inspect.signature(selected_obj))
        except Exception:
            init_signature = None

        if inspect.isclass(selected_obj) and hasattr(selected_obj, "__call__"):
            try:
                call_signature = str(inspect.signature(selected_obj.__call__))
            except Exception:
                call_signature = None
            callable_ready = True
        elif callable(selected_obj):
            try:
                call_signature = str(inspect.signature(selected_obj))
            except Exception:
                call_signature = None
            callable_ready = True

    return {
        "candidate_name": candidate_name,
        "module_file": module_file,
        "package_import": package_result,
        "direct_import": direct_result,
        "object_kind": object_kind,
        "init_signature": init_signature,
        "call_signature": call_signature,
        "candidate_resolved": selected_obj is not None,
        "candidate_callable_ready": bool(callable_ready),
        "candidate_executed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded replay core execution adapter builder for Batch 28X.")
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
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    callable_output_root = pathlib.Path(args.callable_output_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, dataset_candidate_root):
        raise SystemExit("dataset_candidate_root must stay under run/replay")
    if not safe_under_run_replay(project_root, callable_output_root):
        raise SystemExit("callable_output_root must stay under run/replay")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output_root must stay under run/replay")
    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run):
        raise SystemExit("adapter requires no-broker/no-live-redis/observe-only/dry-run")

    output_root.mkdir(parents=True, exist_ok=True)

    candidate_report = import_candidate(project_root, args.module_file, args.candidate_name)

    callable_manifest = load_json(callable_output_root / "00_offline_replay_callable_manifest.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")
    dry_run_plan = load_json(callable_output_root / "02_replay_dry_run_plan.json")

    bridge_ready = (
        callable_manifest.get("replay_engine_callable_invoked") is True
        and callable_manifest.get("replay_run_completed") is True
        and callable_manifest.get("replay_engine_core_completed") is False
        and isinstance(input_index.get("input_surfaces"), dict)
        and not input_index.get("missing_surfaces")
    )

    core_adapter_ready = bool(
        candidate_report.get("candidate_callable_ready")
        and bridge_ready
        and args.contract_only
    )

    manifest = {
        "schema_version": "guarded_replay_core_execution_adapter_manifest_28x_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_REPLAY_CORE_EXECUTION_ADAPTER_BUILD_ONLY",
        "core_adapter_ready": bool(core_adapter_ready),
        "selected_candidate": {
            "module_file": args.module_file,
            "kind": args.candidate_kind,
            "name": args.candidate_name,
        },
        "candidate_report": candidate_report,
        "dataset_candidate_root": str(dataset_candidate_root),
        "callable_output_root": str(callable_output_root),
        "output_root": str(output_root),
        "bridge_ready": bool(bridge_ready),
        "contract_only": bool(args.contract_only),
        "candidate_executed": False,
        "replay_core_executed": False,
        "replay_run_completed": False,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28X",
    }

    write_json(output_root / "00_core_execution_adapter_manifest.json", manifest)
    write_json(output_root / "01_selected_core_candidate_report.json", {
        "schema_version": "selected_core_candidate_report_28x_v1",
        "selected_candidate": manifest["selected_candidate"],
        "candidate_report": candidate_report,
    })
    write_json(output_root / "02_candidate_import_signature_report.json", {
        "schema_version": "candidate_import_signature_report_28x_v1",
        "candidate_callable_ready": bool(candidate_report.get("candidate_callable_ready")),
        "package_import_ok": candidate_report.get("package_import", {}).get("ok") is True,
        "direct_import_ok": candidate_report.get("direct_import", {}).get("ok") is True,
        "init_signature": candidate_report.get("init_signature"),
        "call_signature": candidate_report.get("call_signature"),
        "candidate_executed": False,
    })
    write_json(output_root / "03_dataset_callable_bridge_contract.json", {
        "schema_version": "dataset_callable_bridge_contract_28x_v1",
        "bridge_ready": bool(bridge_ready),
        "dataset_candidate_root": str(dataset_candidate_root),
        "callable_output_root": str(callable_output_root),
        "callable_manifest": callable_manifest,
        "input_index_summary": {
            "input_surface_count": len(input_index.get("input_surfaces", {}) if isinstance(input_index.get("input_surfaces"), dict) else {}),
            "missing_surfaces": input_index.get("missing_surfaces"),
        },
        "dry_run_plan": dry_run_plan,
    })
    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", {
        "schema_version": "guarded_core_execution_adapter_no_boundary_28x_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28X",
    })
    write_json(output_root / "05_next_core_execution_contract.json", {
        "schema_version": "next_guarded_core_execution_contract_28x_v1",
        "core_adapter_ready": bool(core_adapter_ready),
        "next_batch": "Batch 28Y — execute guarded replay core candidate adapter dry-run, still not paper/live enablement." if core_adapter_ready else "Batch 28Y — repair selected replay core candidate import/signature bridge, still not paper/live enablement.",
        "allowed_next_actions": [
            "instantiate/call selected replay core candidate only if constructor/call signature can be satisfied",
            "use only offline dataset/callable outputs",
            "write outputs under run/replay only",
            "do not compare parity until core output exists",
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
        "schema_version": "guarded_replay_core_execution_adapter_result_28x_v1",
        "accepted_for": "GUARDED_REPLAY_CORE_EXECUTION_ADAPTER_BUILD_ONLY",
        "core_adapter_ready": bool(core_adapter_ready),
        "selected_candidate": manifest["selected_candidate"],
        "candidate_report": candidate_report,
        "bridge_ready": bool(bridge_ready),
        "written_count": 6,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_28X",
        "next_batch": "Batch 28Y — execute guarded replay core candidate adapter dry-run, still not paper/live enablement." if core_adapter_ready else "Batch 28Y — repair selected replay core candidate import/signature bridge, still not paper/live enablement.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if core_adapter_ready else 2

if __name__ == "__main__":
    raise SystemExit(main())
