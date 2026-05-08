#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
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

def rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except Exception:
        return str(path)

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    return str(path.resolve()).startswith(str(replay_root) + "/")

def names_from_call(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return names_from_call(node.value)
    return None

def base_names(node: ast.ClassDef) -> list[str]:
    out: list[str] = []
    for base in node.bases:
        name = names_from_call(base)
        if name:
            out.append(name)
    return out

def function_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    pos = [a.arg for a in node.args.args]
    kwonly = [a.arg for a in node.args.kwonlyargs]
    defaults = len(node.args.defaults or [])
    required_pos = max(0, len(pos) - defaults)
    if pos and pos[0] in ("self", "cls"):
        required_pos = max(0, required_pos - 1)
    required_kwonly = [name for name, default in zip(kwonly, node.args.kw_defaults) if default is None]
    return {
        "args": pos + kwonly,
        "required_positional_count_excluding_self": required_pos,
        "required_kwonly": required_kwonly,
    }

def parse_replay_sources(project_root: pathlib.Path, replay_dir: pathlib.Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in sorted(replay_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        module_rel = rel(project_root, path)
        report: dict[str, Any] = {
            "module_file": module_rel,
            "parse_ok": False,
            "classes": [],
            "functions": [],
        }
        try:
            tree = ast.parse(text)
            report["parse_ok"] = True
        except Exception as exc:
            report["error"] = f"{type(exc).__name__}: {exc}"
            reports.append(report)
            continue

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        rec = {"name": item.name}
                        rec.update(function_args(item))
                        methods.append(rec)
                report["classes"].append({
                    "name": node.name,
                    "lineno": getattr(node, "lineno", None),
                    "bases": base_names(node),
                    "methods": methods,
                    "is_protocol_like": node.name.lower().endswith("protocol") or "Protocol" in base_names(node),
                })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                rec = {
                    "name": node.name,
                    "lineno": getattr(node, "lineno", None),
                }
                rec.update(function_args(node))
                report["functions"].append(rec)
        reports.append(report)
    return reports

def score_surface(name: str, module_file: str, target: str) -> int:
    n = name.lower()
    m = module_file.lower()
    score = 0
    if target == "run_context":
        for token in ("runcontext", "run_context", "context", "replaycontext", "sessioncontext"):
            if token in n:
                score += 8
            if token in m:
                score += 3
    elif target == "topology_plan":
        for token in ("topologyplan", "topology_plan", "topology", "plan"):
            if token in n:
                score += 8
            if token in m:
                score += 4
    elif target == "stage_executor":
        for token in ("stageexecutor", "stage_executor", "executor", "execute_stage", "stage"):
            if token in n:
                score += 8
            if token in m:
                score += 3
    if "protocol" in n or "hook" in n:
        score -= 20
    return score

def collect_surfaces(reports: list[dict[str, Any]], target: str) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for report in reports:
        module_file = report.get("module_file", "")
        for cls in report.get("classes", []):
            score = score_surface(cls.get("name", ""), module_file, target)
            if score > 0:
                surfaces.append({
                    "module_file": module_file,
                    "kind": "class",
                    "name": cls.get("name"),
                    "bases": cls.get("bases"),
                    "methods": cls.get("methods"),
                    "is_protocol_like": cls.get("is_protocol_like"),
                    "score": score,
                })
        for fn in report.get("functions", []):
            score = score_surface(fn.get("name", ""), module_file, target)
            if score > 0:
                surfaces.append({
                    "module_file": module_file,
                    "kind": "function",
                    "name": fn.get("name"),
                    "args": fn.get("args"),
                    "required_kwonly": fn.get("required_kwonly"),
                    "score": score,
                })
    return sorted(surfaces, key=lambda x: x.get("score", 0), reverse=True)

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 29D offline ReplayEngine context bridge builder.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--replay-dir", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--callable-output-root", required=True)
    parser.add_argument("--adapter-root-29c", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    replay_dir = pathlib.Path(args.replay_dir).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    callable_output_root = pathlib.Path(args.callable_output_root).resolve()
    adapter_root_29c = pathlib.Path(args.adapter_root_29c).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    for name, path in {
        "dataset_candidate_root": dataset_candidate_root,
        "callable_output_root": callable_output_root,
        "adapter_root_29c": adapter_root_29c,
        "output_root": output_root,
    }.items():
        if not safe_under_run_replay(project_root, path):
            raise SystemExit(f"{name} must stay under run/replay")

    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run and args.contract_only):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run/contract-only")

    output_root.mkdir(parents=True, exist_ok=True)

    adapter_manifest = load_json(adapter_root_29c / "00_guarded_replay_engine_adapter_manifest.json")
    argument_gap = load_json(adapter_root_29c / "02_execution_argument_gap_report.json")
    bridge_requirements = load_json(adapter_root_29c / "03_offline_context_bridge_requirements.json")
    callable_manifest = load_json(callable_output_root / "00_offline_replay_callable_manifest.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")
    dataset_manifest = load_json(dataset_candidate_root / "00_dataset_candidate_manifest.json")

    reports = parse_replay_sources(project_root, replay_dir)

    run_context_surfaces = collect_surfaces(reports, "run_context")
    topology_plan_surfaces = collect_surfaces(reports, "topology_plan")
    stage_executor_surfaces = collect_surfaces(reports, "stage_executor")

    missing_execute_args = bridge_requirements.get("required_for_execute")
    if not isinstance(missing_execute_args, list):
        missing_execute_args = []

    offline_inputs_ready = (
        callable_manifest.get("replay_run_completed") is True
        and isinstance(input_index.get("input_surfaces"), dict)
        and not input_index.get("missing_surfaces")
        and bool(dataset_manifest)
    )

    run_context_bridge_ready = bool(run_context_surfaces)
    topology_plan_bridge_ready = bool(topology_plan_surfaces)
    stage_executor_bridge_ready = bool(stage_executor_surfaces)

    context_bridge_ready = bool(
        offline_inputs_ready
        and run_context_bridge_ready
        and topology_plan_bridge_ready
        and stage_executor_bridge_ready
    )

    if context_bridge_ready:
        next_batch = "Batch 29E — materialize guarded offline ReplayEngine context objects, still not paper/live enablement."
        next_path = "OFFLINE_CONTEXT_SURFACES_READY"
    else:
        next_batch = "Batch 29E — add explicit offline ReplayEngine context shim for missing surfaces, still not paper/live enablement."
        next_path = "OFFLINE_CONTEXT_SURFACE_SHIM_REQUIRED"

    write_json(output_root / "00_offline_context_bridge_manifest.json", {
        "schema_version": "offline_context_bridge_manifest_29d_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "REPLAY_ENGINE_OFFLINE_CONTEXT_BRIDGE_CONTRACT_ONLY",
        "context_bridge_ready": context_bridge_ready,
        "next_path": next_path,
        "missing_execute_args_from_29c": missing_execute_args,
        "offline_inputs_ready": offline_inputs_ready,
        "run_context_bridge_ready": run_context_bridge_ready,
        "topology_plan_bridge_ready": topology_plan_bridge_ready,
        "stage_executor_bridge_ready": stage_executor_bridge_ready,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29D",
        "next_batch": next_batch,
    })

    write_json(output_root / "01_run_context_surface_report.json", {
        "schema_version": "run_context_surface_report_29d_v1",
        "bridge_ready": run_context_bridge_ready,
        "candidate_surfaces": run_context_surfaces,
    })

    write_json(output_root / "02_topology_plan_surface_report.json", {
        "schema_version": "topology_plan_surface_report_29d_v1",
        "bridge_ready": topology_plan_bridge_ready,
        "candidate_surfaces": topology_plan_surfaces,
    })

    write_json(output_root / "03_stage_executor_surface_report.json", {
        "schema_version": "stage_executor_surface_report_29d_v1",
        "bridge_ready": stage_executor_bridge_ready,
        "candidate_surfaces": stage_executor_surfaces,
        "note": "29C did not list stage_executor as missing, but ReplayEngine.execute surface still requires stage execution semantics to be validated before any core execution.",
    })

    write_json(output_root / "04_offline_input_mapping_contract.json", {
        "schema_version": "offline_input_mapping_contract_29d_v1",
        "dataset_candidate_root": str(dataset_candidate_root),
        "callable_output_root": str(callable_output_root),
        "adapter_root_29c": str(adapter_root_29c),
        "offline_inputs_ready": offline_inputs_ready,
        "input_surface_count": len(input_index.get("input_surfaces", {}) if isinstance(input_index.get("input_surfaces"), dict) else {}),
        "missing_surfaces": input_index.get("missing_surfaces"),
        "adapter_manifest": adapter_manifest,
        "argument_gap": argument_gap,
    })

    write_json(output_root / "05_no_broker_no_live_redis_boundary.json", {
        "schema_version": "offline_context_bridge_no_boundary_29d_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29D",
    })

    write_json(output_root / "06_next_context_materialization_contract.json", {
        "schema_version": "next_context_materialization_contract_29d_v1",
        "next_batch": next_batch,
        "next_path": next_path,
        "context_bridge_ready": context_bridge_ready,
        "run_context_bridge_ready": run_context_bridge_ready,
        "topology_plan_bridge_ready": topology_plan_bridge_ready,
        "stage_executor_bridge_ready": stage_executor_bridge_ready,
        "allowed_next_actions": [
            "materialize offline run_context/topology_plan/stage_executor objects only if bridge surfaces are sufficient",
            "otherwise add explicit offline shim under replay/parity tooling",
            "do not execute ReplayEngine until materialized objects are proven",
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
        "schema_version": "offline_context_bridge_result_29d_v1",
        "accepted_for": "REPLAY_ENGINE_OFFLINE_CONTEXT_BRIDGE_CONTRACT_ONLY",
        "context_bridge_ready": context_bridge_ready,
        "next_path": next_path,
        "missing_execute_args_from_29c": missing_execute_args,
        "run_context_bridge_ready": run_context_bridge_ready,
        "topology_plan_bridge_ready": topology_plan_bridge_ready,
        "stage_executor_bridge_ready": stage_executor_bridge_ready,
        "run_context_surface_count": len(run_context_surfaces),
        "topology_plan_surface_count": len(topology_plan_surfaces),
        "stage_executor_surface_count": len(stage_executor_surfaces),
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29D",
        "next_batch": next_batch,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
