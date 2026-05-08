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

def rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except Exception:
        return str(path)

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    return str(path.resolve()).startswith(str(replay_root) + "/")

def base_names(node: ast.ClassDef) -> list[str]:
    out: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            out.append(base.id)
        elif isinstance(base, ast.Attribute):
            out.append(base.attr)
        elif isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name):
                out.append(base.value.id)
            elif isinstance(base.value, ast.Attribute):
                out.append(base.value.attr)
    return out

def decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    out: list[str] = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            out.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            out.append(dec.attr)
        elif isinstance(dec, ast.Call):
            fn = dec.func
            if isinstance(fn, ast.Name):
                out.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                out.append(fn.attr)
    return out

def arg_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]

def required_count(node: ast.FunctionDef | ast.AsyncFunctionDef, *, skip_self: bool) -> int:
    args = [a.arg for a in node.args.args]
    if skip_self and args and args[0] in ("self", "cls"):
        args = args[1:]
    defaults = len(node.args.defaults or [])
    required_pos = max(0, len(args) - defaults)
    required_kwonly = sum(1 for default in node.args.kw_defaults if default is None)
    return required_pos + required_kwonly

def score_name(module_rel: str, name: str, methods: list[str], args: list[str]) -> int:
    lower_name = name.lower()
    lower_module = module_rel.lower()
    lower_methods = [m.lower() for m in methods]
    lower_args = [a.lower() for a in args]

    score = 0
    if "engine" in lower_module:
        score += 4
    if "runner" in lower_module:
        score += 4
    if "dataset" in lower_module:
        score += 1
    if lower_name in ("replayengine", "replayrunner", "runner", "engine"):
        score += 8
    if "replay" in lower_name:
        score += 4
    if "engine" in lower_name:
        score += 4
    if "runner" in lower_name:
        score += 4
    if "run" in lower_name or "execute" in lower_name:
        score += 4
    if any(m in lower_methods for m in ("run", "execute", "__call__", "replay")):
        score += 5
    if any(a in lower_args for a in ("dataset", "dataset_root", "dataset_path", "input_root", "output_root", "run_dir", "artifact_root")):
        score += 3
    if "hook" in lower_name or "protocol" in lower_name or "interface" in lower_name:
        score -= 20
    return score

def parse_module(project_root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    module_rel = rel(project_root, path)
    report: dict[str, Any] = {
        "module_file": module_rel,
        "present": path.is_file(),
        "sha256": sha256_file(path),
        "parse_ok": False,
        "classes": [],
        "functions": [],
        "errors": [],
    }
    try:
        tree = ast.parse(text)
        report["parse_ok"] = True
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        return report

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = base_names(node)
            is_protocol = any(base in ("Protocol", "GenericProtocol") for base in bases) or node.name.lower().endswith("protocol")
            methods = []
            has_abstract = False
            call_args: list[str] = []
            run_args: list[str] = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    decs = decorator_names(item)
                    if "abstractmethod" in decs:
                        has_abstract = True
                    methods.append(item.name)
                    if item.name == "__call__":
                        call_args = arg_names(item)
                    if item.name in ("run", "execute", "replay"):
                        run_args = arg_names(item)
            is_abstract = "ABC" in bases or has_abstract
            args_for_score = call_args or run_args
            score = score_name(module_rel, node.name, methods, args_for_score)
            report["classes"].append({
                "name": node.name,
                "kind": "class",
                "lineno": getattr(node, "lineno", None),
                "bases": bases,
                "methods": methods,
                "is_protocol": is_protocol,
                "is_abstract": is_abstract,
                "has_call": "__call__" in methods,
                "has_run_or_execute": any(m in methods for m in ("run", "execute", "replay")),
                "call_args": call_args,
                "run_args": run_args,
                "score": score,
                "excluded_reason": "protocol" if is_protocol else "abstract" if is_abstract else "low_score_or_no_executable_method",
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = arg_names(node)
            score = score_name(module_rel, node.name, [], args)
            report["functions"].append({
                "name": node.name,
                "kind": "function",
                "lineno": getattr(node, "lineno", None),
                "args": args,
                "required_arg_count": required_count(node, skip_self=False),
                "score": score,
                "excluded_reason": "low_score" if score < 4 else None,
            })
    return report

def import_candidate(project_root: pathlib.Path, module_file: str, candidate_name: str) -> dict[str, Any]:
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
        obj = getattr(module, candidate_name)
        package_result = describe_object(obj, package_name)
    except Exception as exc:
        package_result = {"ok": False, "module": package_name, "error": f"{type(exc).__name__}: {exc}"}

    try:
        spec = importlib.util.spec_from_file_location("candidate_selector_29b_direct", str(module_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        obj = getattr(module, candidate_name)
        direct_result = describe_object(obj, str(module_path))
    except Exception as exc:
        direct_result = {"ok": False, "module_file": str(module_path), "error": f"{type(exc).__name__}: {exc}"}

    return {
        "package_import": package_result,
        "direct_import": direct_result,
        "import_ready": package_result.get("ok") is True or direct_result.get("ok") is True,
    }

def describe_object(obj: Any, module_label: str) -> dict[str, Any]:
    is_class = inspect.isclass(obj)
    is_protocol = bool(getattr(obj, "_is_protocol", False))
    is_abstract = bool(getattr(obj, "__abstractmethods__", False))
    payload: dict[str, Any] = {
        "ok": True,
        "module": module_label,
        "object_kind": "class" if is_class else "function" if inspect.isfunction(obj) else type(obj).__name__,
        "is_protocol": is_protocol,
        "is_abstract": is_abstract,
        "callable": callable(obj),
        "signature": None,
        "call_signature": None,
    }
    try:
        payload["signature"] = str(inspect.signature(obj)) if callable(obj) else None
    except Exception as exc:
        payload["signature_error"] = f"{type(exc).__name__}: {exc}"
    if is_class and hasattr(obj, "__call__"):
        try:
            payload["call_signature"] = str(inspect.signature(obj.__call__))
        except Exception as exc:
            payload["call_signature_error"] = f"{type(exc).__name__}: {exc}"
    return payload

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 29B protocol-safe replay core candidate selector.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--replay-dir", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    replay_dir = pathlib.Path(args.replay_dir).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit("output root must stay under run/replay")
    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run")

    output_root.mkdir(parents=True, exist_ok=True)

    module_reports = []
    candidate_pool = []
    excluded_protocols = []
    excluded_abstract = []

    for path in sorted(replay_dir.glob("*.py")):
        report = parse_module(project_root, path)
        module_reports.append(report)

        for cls in report.get("classes", []):
            record = {
                "module_file": report["module_file"],
                "kind": "class",
                **cls,
            }
            if cls.get("is_protocol"):
                excluded_protocols.append(record)
                continue
            if cls.get("is_abstract"):
                excluded_abstract.append(record)
                continue
            if (cls.get("has_call") or cls.get("has_run_or_execute")) and cls.get("score", 0) >= 4:
                candidate_pool.append(record)

        for fn in report.get("functions", []):
            record = {
                "module_file": report["module_file"],
                "kind": "function",
                **fn,
            }
            if fn.get("score", 0) >= 4:
                candidate_pool.append(record)

    candidate_pool = sorted(candidate_pool, key=lambda x: x.get("score", 0), reverse=True)

    selected = None
    selected_import_report = None
    for candidate in candidate_pool:
        import_report = import_candidate(project_root, candidate["module_file"], candidate["name"])
        package = import_report.get("package_import", {})
        direct = import_report.get("direct_import", {})
        protocol_runtime = package.get("is_protocol") is True or direct.get("is_protocol") is True
        abstract_runtime = package.get("is_abstract") is True or direct.get("is_abstract") is True
        if import_report.get("import_ready") and not protocol_runtime and not abstract_runtime:
            selected = candidate
            selected_import_report = import_report
            break

    concrete_candidate_selected = selected is not None
    if concrete_candidate_selected:
        next_batch = "Batch 29C — build guarded adapter for selected concrete replay-core candidate, still not paper/live enablement."
    else:
        next_batch = "Batch 29C — add explicit concrete offline replay-core shim because no concrete candidate was import-ready, still not paper/live enablement."

    write_json(output_root / "00_protocol_safe_candidate_selection_manifest.json", {
        "schema_version": "protocol_safe_candidate_selection_manifest_29b_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "PROTOCOL_SAFE_CONCRETE_REPLAY_CORE_CANDIDATE_SELECTION_ONLY",
        "concrete_candidate_selected": concrete_candidate_selected,
        "selected_candidate": selected,
        "selected_import_report": selected_import_report,
        "candidate_count": len(candidate_pool),
        "excluded_protocol_count": len(excluded_protocols),
        "excluded_abstract_count": len(excluded_abstract),
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29B",
        "next_batch": next_batch,
    })
    write_json(output_root / "01_replay_core_source_inventory.json", {
        "schema_version": "replay_core_source_inventory_29b_v1",
        "module_reports": module_reports,
    })
    write_json(output_root / "02_excluded_protocol_and_abstract_surfaces.json", {
        "schema_version": "excluded_protocol_and_abstract_surfaces_29b_v1",
        "excluded_protocols": excluded_protocols,
        "excluded_abstract": excluded_abstract,
    })
    write_json(output_root / "03_concrete_candidate_pool.json", {
        "schema_version": "concrete_candidate_pool_29b_v1",
        "candidate_pool": candidate_pool,
        "selected_candidate": selected,
        "selected_import_report": selected_import_report,
    })
    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", {
        "schema_version": "protocol_safe_candidate_selection_no_boundary_29b_v1",
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29B",
    })
    write_json(output_root / "05_next_concrete_candidate_contract.json", {
        "schema_version": "next_concrete_candidate_contract_29b_v1",
        "concrete_candidate_selected": concrete_candidate_selected,
        "selected_candidate": selected,
        "next_batch": next_batch,
        "allowed_next_actions": [
            "build adapter around selected concrete candidate only",
            "do not instantiate Protocol/abstract surfaces",
            "use offline dataset/callable outputs only",
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
        "schema_version": "protocol_safe_candidate_selection_result_29b_v1",
        "accepted_for": "PROTOCOL_SAFE_CONCRETE_REPLAY_CORE_CANDIDATE_SELECTION_ONLY",
        "concrete_candidate_selected": concrete_candidate_selected,
        "selected_candidate": selected,
        "candidate_count": len(candidate_pool),
        "excluded_protocol_count": len(excluded_protocols),
        "excluded_abstract_count": len(excluded_abstract),
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29B",
        "next_batch": next_batch,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
