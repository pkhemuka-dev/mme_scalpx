#!/usr/bin/env python3
from __future__ import annotations



# ===== BATCH 29AW PROVIDER FEATURE SUMMARY PATCH START =====
def _batch29aw_json_safe(value):
    try:
        json.dumps(value, default=str)
        return value
    except Exception:
        return str(value)

def _batch29aw_flatten_provider_feature_candidates(obj, prefix="", limit=20000):
    out = {}

    def walk(x, p):
        if len(out) >= limit:
            return
        if isinstance(x, dict):
            for k, v in x.items():
                key = f"{p}.{k}" if p else str(k)
                walk(v, key)
        elif isinstance(x, (list, tuple)):
            if len(x) <= 100:
                for i, v in enumerate(x):
                    walk(v, f"{p}[{i}]")
            else:
                out[p + ".__len__"] = len(x)
                out[p + ".__sample_text__"] = json.dumps(list(x[:20]), default=str)
        elif isinstance(x, (str, int, float, bool)) or x is None:
            out[p] = x
        else:
            out[p] = str(x)

    walk(obj, prefix)
    return out

def _batch29aw_extract_provider_feature_value(field_name, source_payloads):
    # Replay-side evidence only. This helper must not read live Redis, broker APIs, or live reference artifacts.
    # It returns bool only when a directly replay-side boolean/string-boolean value exists.
    # Otherwise it returns None with provenance.
    replayish_terms = (
        "guarded_replay_summary",
        "execution_output_summary",
        "engine_execution_report",
        "context_reconstruction_report",
        "replay_result",
        "engine_result",
        "boundary",
        "summary",
    )

    rejected = []
    for source_name, payload in source_payloads.items():
        flat = _batch29aw_flatten_provider_feature_candidates(payload)
        for path, value in flat.items():
            path_low = str(path).lower()
            source_low = str(source_name).lower()
            if not (path.endswith("." + field_name) or path == field_name or path.split(".")[-1] == field_name):
                continue

            if "live_reference" in path_low or "live_reference" in source_low:
                rejected.append({
                    "source": source_name,
                    "path": path,
                    "value": _batch29aw_json_safe(value),
                    "reason": "live_reference_not_allowed_as_replay_source",
                })
                continue

            replayish = any(term in path_low or term in source_low for term in replayish_terms)
            if isinstance(value, bool) and replayish:
                return value, {
                    "source": source_name,
                    "path": path,
                    "value_kind": "REAL_REPLAY_BOOLEAN",
                    "rejected_candidates": rejected[:25],
                }

            if isinstance(value, str) and value.strip().lower() in ("true", "false") and replayish:
                return value.strip().lower() == "true", {
                    "source": source_name,
                    "path": path,
                    "value_kind": "REAL_REPLAY_STRING_BOOLEAN",
                    "rejected_candidates": rejected[:25],
                }

            rejected.append({
                "source": source_name,
                "path": path,
                "value": _batch29aw_json_safe(value),
                "reason": "candidate_not_usable_boolean_replay_evidence",
            })

    return None, {
        "source": None,
        "path": None,
        "value_kind": "NULL_SAFE_NO_REAL_REPLAY_BOOLEAN_SOURCE",
        "rejected_candidates": rejected[:25],
    }

def _batch29aw_build_provider_feature_summary(dataset_id=None, run_id=None, source_payloads=None):
    source_payloads = source_payloads or {}
    fields = ['provider_runtime_ok', 'feed_snapshot_ok', 'feature_payload_ok', 'family_surfaces_ok']
    values = {}
    provenance = {}

    for field_name in fields:
        value, prov = _batch29aw_extract_provider_feature_value(field_name, source_payloads)
        values[field_name] = value
        provenance[field_name] = {
            "field_name": field_name,
            "value": value,
            "value_status": "KNOWN_BOOLEAN" if isinstance(value, bool) else "NULL_SAFE_SOURCE_UNAVAILABLE",
            "source": prov.get("source"),
            "path": prov.get("path"),
            "value_kind": prov.get("value_kind"),
            "rejected_candidates": prov.get("rejected_candidates", []),
            "law": "Do not infer replay provider-feature values from live reference. Null is not false.",
        }

    known_boolean_count = sum(1 for v in values.values() if isinstance(v, bool))
    null_value_count = sum(1 for v in values.values() if v is None)

    return {
        "schema_version": "guarded_replay_provider_feature_summary_29aw_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": dataset_id,
        "run_id": run_id,
        "surface": "guarded_replay_provider_feature_summary",
        "values": values,
        "provenance": provenance,
        "field_count": len(fields),
        "known_boolean_count": known_boolean_count,
        "null_value_count": null_value_count,
        "null_safe_materialization": null_value_count > 0,
        "value_comparison_ready": known_boolean_count == len(fields),
        "replay_only": True,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "real_order_sent": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "warning": "Replay-only guarded artifact. Null means no real replay-side boolean source was present; null must not be interpreted as false.",
    }

def _batch29aw_write_provider_feature_summary(audit_root, *, dataset_id=None, run_id=None, source_payloads=None):
    artifact_path = None
    error_path = None
    try:
        audit_root = pathlib.Path(audit_root)
        audit_root.mkdir(parents=True, exist_ok=True)
        artifact_path = audit_root / "06_guarded_replay_provider_feature_summary.json"

        payload = _batch29aw_build_provider_feature_summary(
            dataset_id=dataset_id,
            run_id=run_id,
            source_payloads=source_payloads or {},
        )

        write_json_atomic(artifact_path, payload)
        return payload, str(artifact_path)
    except Exception as exc:
        err_payload = {
            "schema_version": "guarded_replay_provider_feature_summary_29aw_r3_error_v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "surface": "guarded_replay_provider_feature_summary",
            "dataset_id": dataset_id,
            "run_id": run_id,
            "values": {field: None for field in ['provider_runtime_ok', 'feed_snapshot_ok', 'feature_payload_ok', 'family_surfaces_ok']},
            "provenance": {
                field: {
                    "field_name": field,
                    "value": None,
                    "value_status": "NULL_SAFE_EMISSION_ERROR",
                    "error": f"{type(exc).__name__}: {exc}",
                    "law": "Null is not false. Emission error must be audited before parity.",
                }
                for field in ['provider_runtime_ok', 'feed_snapshot_ok', 'feature_payload_ok', 'family_surfaces_ok']
            },
            "field_count": len(['provider_runtime_ok', 'feed_snapshot_ok', 'feature_payload_ok', 'family_surfaces_ok']),
            "known_boolean_count": 0,
            "null_value_count": len(['provider_runtime_ok', 'feed_snapshot_ok', 'feature_payload_ok', 'family_surfaces_ok']),
            "null_safe_materialization": True,
            "value_comparison_ready": False,
            "replay_only": True,
            "reads_live_redis": False,
            "writes_live_redis": False,
            "calls_broker_api": False,
            "real_order_sent": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

        try:
            audit_root = pathlib.Path(audit_root)
            audit_root.mkdir(parents=True, exist_ok=True)
            error_path = audit_root / "06_guarded_replay_provider_feature_summary.json"
            write_json_atomic(error_path, err_payload)
            return err_payload, str(error_path)
        except Exception:
            return err_payload, None


# BATCH29AW_R9_FORCE_OUTPUT_ROOT_PROVIDER_FEATURE_HELPER
def _batch29aw_r9_json_safe(value):
    try:
        json.dumps(value, default=str)
        return value
    except Exception:
        return str(value)

def _batch29aw_r9_flatten(obj, prefix="", limit=20000):
    out = {}
    def walk(x, p):
        if len(out) >= limit:
            return
        if isinstance(x, dict):
            for k, v in x.items():
                key = f"{p}.{k}" if p else str(k)
                walk(v, key)
        elif isinstance(x, (list, tuple)):
            if len(x) <= 100:
                for i, v in enumerate(x):
                    walk(v, f"{p}[{i}]")
        elif isinstance(x, (str, int, float, bool)) or x is None:
            out[p] = x
        else:
            out[p] = str(x)
    walk(obj, prefix)
    return out

def _batch29aw_r9_extract_field(field_name, source_payloads):
    rejected = []
    for source_name, payload in (source_payloads or {}).items():
        flat = _batch29aw_r9_flatten(payload)
        for path, value in flat.items():
            direct = path == field_name or path.endswith("." + field_name) or path.split(".")[-1] == field_name
            if not direct:
                continue
            if "live_reference" in str(source_name).lower() or "live_reference" in str(path).lower():
                rejected.append({"source": source_name, "path": path, "reason": "live_reference_forbidden"})
                continue
            if isinstance(value, bool):
                return value, {"source": source_name, "path": path, "value_kind": "BOOLEAN"}
            if isinstance(value, str) and value.strip().lower() in ("true", "false"):
                return value.strip().lower() == "true", {"source": source_name, "path": path, "value_kind": "STRING_BOOLEAN"}
            rejected.append({"source": source_name, "path": path, "value": _batch29aw_r9_json_safe(value), "reason": "not_boolean"})
    return None, {"source": None, "path": None, "value_kind": "NULL_SAFE_SOURCE_UNAVAILABLE", "rejected_candidates": rejected[:25]}

def _batch29aw_r9_force_provider_feature_summary(args, result, source_payloads=None):
    output_root = None
    if args is not None:
        output_root = getattr(args, "output_root", None)
    if output_root is None and isinstance(result, dict):
        output_root = result.get("output_root")
    if output_root is None:
        output_root = "."
    output_root = pathlib.Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    artifact_path = output_root / "06_guarded_replay_provider_feature_summary.json"
    fields = ['provider_runtime_ok', 'feed_snapshot_ok', 'feature_payload_ok', 'family_surfaces_ok']
    source_payloads = source_payloads or {}
    if isinstance(result, dict):
        source_payloads = dict(source_payloads)
        source_payloads.setdefault("stdout_result", result)

    values = {}
    provenance = {}
    for field in fields:
        value, prov = _batch29aw_r9_extract_field(field, source_payloads)
        values[field] = value
        provenance[field] = {
            "field_name": field,
            "value": value,
            "value_status": "KNOWN_BOOLEAN" if isinstance(value, bool) else "NULL_SAFE_SOURCE_UNAVAILABLE",
            "source": prov.get("source"),
            "path": prov.get("path"),
            "value_kind": prov.get("value_kind"),
            "law": "Replay-only artifact. Null is not false. Do not infer replay values from live references.",
        }

    known_boolean_count = sum(1 for v in values.values() if isinstance(v, bool))
    null_value_count = sum(1 for v in values.values() if v is None)

    payload = {
        "schema_version": "guarded_replay_provider_feature_summary_29aw_r9_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "surface": "guarded_replay_provider_feature_summary",
        "dataset_id": getattr(args, "dataset_id", None) if args is not None else None,
        "run_id": getattr(args, "run_id", None) if args is not None else None,
        "values": values,
        "provenance": provenance,
        "field_count": len(fields),
        "known_boolean_count": known_boolean_count,
        "null_value_count": null_value_count,
        "null_safe_materialization": null_value_count > 0,
        "value_comparison_ready": known_boolean_count == len(fields),
        "artifact_path": str(artifact_path),
        "output_root": str(output_root),
        "replay_only": True,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "real_order_sent": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "warning": "Null-safe provider-feature summary emitted for validation; null must not be treated as false.",
    }

    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return payload, str(artifact_path)

# ===== BATCH 29AW PROVIDER FEATURE SUMMARY PATCH END =====

import argparse
import importlib
import importlib.util
import inspect
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any

BLOCKED_MODULE_PREFIXES = (
    "kiteconnect",
    "redis",
)

BLOCKED_NAME_PARTS = (
    "dhan_execution",
    "zerodha",
    "broker_api",
    "broker_auth",
)

def guarded_import(name: str):
    lowered = name.lower()
    if lowered.startswith(BLOCKED_MODULE_PREFIXES) or any(part in lowered for part in BLOCKED_NAME_PARTS):
        raise RuntimeError(f"blocked unsafe import during guarded replay dry-run: {name}")
    return importlib.import_module(name)

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
        module = guarded_import(package_name)
        obj = getattr(module, name)
        return {"ok": True, "mode": "package", "object": obj, "errors": errors}
    except Exception as exc:
        errors.append(f"package:{type(exc).__name__}: {exc}")

    try:
        spec = importlib.util.spec_from_file_location("guarded_replay_execute_29g_direct", str(module_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        obj = getattr(module, name)
        return {"ok": True, "mode": "direct", "object": obj, "errors": errors}
    except Exception as exc:
        errors.append(f"direct:{type(exc).__name__}: {exc}")

    return {"ok": False, "errors": errors}

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

def materialize_from_selected(
    *,
    target_name: str,
    selected_candidate: dict[str, Any] | None,
    project_root: pathlib.Path,
    values: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(selected_candidate, dict):
        return {"target": target_name, "materialized": False, "reason": "missing_selected_candidate"}

    module_file = str(selected_candidate.get("module_file") or "")
    name = str(selected_candidate.get("name") or "")
    if not module_file or not name:
        return {"target": target_name, "materialized": False, "reason": "missing_module_or_name", "candidate": selected_candidate}

    if selected_candidate.get("is_protocol_like") is True:
        return {"target": target_name, "materialized": False, "reason": "protocol_like_excluded", "candidate": selected_candidate}

    imported = import_surface(project_root, module_file, name)
    if not imported.get("ok"):
        return {"target": target_name, "materialized": False, "reason": "import_failed", "candidate": selected_candidate, "errors": imported.get("errors")}

    obj = imported["object"]
    is_protocol = bool(getattr(obj, "_is_protocol", False))
    is_abstract = bool(getattr(obj, "__abstractmethods__", False))
    if is_protocol or is_abstract:
        return {
            "target": target_name,
            "materialized": False,
            "reason": "runtime_protocol_or_abstract_excluded",
            "candidate": selected_candidate,
            "is_protocol": is_protocol,
            "is_abstract": is_abstract,
        }

    try:
        sig = inspect.signature(obj)
        binding = bind_kwargs(sig, values)
    except Exception as exc:
        return {"target": target_name, "materialized": False, "reason": "signature_failed", "error": f"{type(exc).__name__}: {exc}"}

    if not binding["ok"]:
        return {
            "target": target_name,
            "materialized": False,
            "reason": "binding_missing_required",
            "signature": binding["signature"],
            "missing_required": binding["missing_required"],
            "optional_unmapped": binding["optional_unmapped"],
            "candidate": selected_candidate,
        }

    try:
        materialized = obj(**binding["kwargs"]) if callable(obj) else obj
    except Exception as exc:
        return {
            "target": target_name,
            "materialized": False,
            "reason": "construction_failed",
            "signature": binding["signature"],
            "mapped_kwargs": sorted(binding["kwargs"].keys()),
            "error": f"{type(exc).__name__}: {exc}",
            "candidate": selected_candidate,
        }

    return {
        "target": target_name,
        "materialized": True,
        "selected_candidate": selected_candidate,
        "import_mode": imported.get("mode"),
        "signature": binding["signature"],
        "mapped_kwargs": sorted(binding["kwargs"].keys()),
        "object": materialized,
        "object_summary": summarize_object(materialized),
    }


# BEGIN BATCH29U-R2 STAGE_EXECUTOR MAPPING WRAPPER
def wrap_stage_executor_mapping_29u_r2(
    stage_executor: Any,
    stage_result: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    """Wrap a replay-only materialized mapping as the callable expected by ReplayEngine.

    This is guarded dry-run glue only. It does not start services, read/write live Redis,
    call broker APIs, change production strategy doctrine, or approve paper/live runtime.
    """

    report: dict[str, Any] = {
        "schema_version": "stage_executor_mapping_wrapper_29u_r2_v1",
        "wrapped": False,
        "input_type": type(stage_executor).__name__,
        "input_callable": callable(stage_executor),
        "reason": "not_required",
    }

    if callable(stage_executor):
        report["reason"] = "already_callable"
        return stage_executor, report

    if not isinstance(stage_executor, dict):
        report["reason"] = "unsupported_non_callable_type"
        return stage_executor, report

    source_mapping = dict(stage_executor)
    selected_candidate = stage_result.get("selected_candidate") if isinstance(stage_result, dict) else None
    object_summary = stage_result.get("object_summary") if isinstance(stage_result, dict) else None

    def _guarded_stage_executor_mapping_wrapper_29u_r2(context: Any, stage: Any) -> dict[str, Any]:
        stage_name = getattr(stage, "stage_name", None) or getattr(stage, "name", None)
        order_index = getattr(stage, "order_index", None)
        terminal_stage = bool(getattr(stage, "terminal_stage", False))
        return {
            "schema_version": "guarded_stage_executor_mapping_wrapper_29u_r2_output_v1",
            "status": "offline_stage_executor_mapping_wrapped_29u_r2",
            "offline_only": True,
            "stage_name": stage_name,
            "order_index": order_index,
            "terminal_stage": terminal_stage,
            "context_type": type(context).__name__,
            "source_stage_executor_type": "dict",
            "source_mapping_keys": sorted([str(k) for k in source_mapping.keys()]),
            "selected_candidate": selected_candidate,
            "object_summary": object_summary,
        }

    report.update({
        "wrapped": True,
        "reason": "dict_mapping_wrapped_as_callable",
        "output_callable": True,
        "source_mapping_keys": sorted([str(k) for k in source_mapping.keys()]),
        "selected_candidate": selected_candidate,
        "object_summary": object_summary,
    })
    return _guarded_stage_executor_mapping_wrapper_29u_r2, report
# END BATCH29U-R2 STAGE_EXECUTOR MAPPING WRAPPER

def safe_result_summary(result: Any) -> dict[str, Any]:
    if result is None:
        return {"type": "NoneType", "repr": "None"}
    if isinstance(result, (str, int, float, bool)):
        return {"type": type(result).__name__, "repr": repr(result)}
    if isinstance(result, dict):
        return {"type": "dict", "keys": sorted([str(k) for k in result.keys()])[:100], "repr": repr(result)[:3000]}
    if isinstance(result, (list, tuple)):
        return {"type": type(result).__name__, "length": len(result), "repr": repr(result[:10])[:3000]}
    return {"type": type(result).__name__, "module": type(result).__module__, "repr": repr(result)[:3000]}

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 29G guarded offline ReplayEngine execute dry-run.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--dataset-candidate-root", required=True)
    parser.add_argument("--callable-output-root", required=True)
    parser.add_argument("--materialization-root-29e", required=True)
    parser.add_argument("--shim-root-29f", required=True)
    parser.add_argument("--adapter-root-29c", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--no-broker", action="store_true", required=True)
    parser.add_argument("--no-live-redis", action="store_true", required=True)
    parser.add_argument("--observe-only", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--execute-guarded", action="store_true", required=True)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    dataset_candidate_root = pathlib.Path(args.dataset_candidate_root).resolve()
    callable_output_root = pathlib.Path(args.callable_output_root).resolve()
    materialization_root_29e = pathlib.Path(args.materialization_root_29e).resolve()
    shim_root_29f = pathlib.Path(args.shim_root_29f).resolve()
    adapter_root_29c = pathlib.Path(args.adapter_root_29c).resolve()
    output_root = pathlib.Path(args.output_root).resolve()

    for label, path in {
        "dataset_candidate_root": dataset_candidate_root,
        "callable_output_root": callable_output_root,
        "materialization_root_29e": materialization_root_29e,
        "shim_root_29f": shim_root_29f,
        "adapter_root_29c": adapter_root_29c,
        "output_root": output_root,
    }.items():
        if not safe_under_run_replay(project_root, path):
            raise SystemExit(f"{label} must stay under run/replay")

    if not (args.no_broker and args.no_live_redis and args.observe_only and args.dry_run and args.execute_guarded):
        raise SystemExit("requires no-broker/no-live-redis/observe-only/dry-run/execute-guarded")

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    output_root.mkdir(parents=True, exist_ok=True)


    shim_manifest = load_json(shim_root_29f / "00_offline_run_context_shim_manifest.json")
    shim_reconstruction = load_json(shim_root_29f / "03_reconstruction_contract.json")
    prior_29e_reconstruction = load_json(materialization_root_29e / "04_reconstruction_contract.json")
    topology_report_29e = load_json(materialization_root_29e / "02_topology_plan_materialization_report.json")
    stage_report_29e = load_json(materialization_root_29e / "03_stage_executor_materialization_report.json")
    adapter_manifest = load_json(adapter_root_29c / "00_guarded_replay_engine_adapter_manifest.json")
    dataset_manifest = load_json(dataset_candidate_root / "00_dataset_candidate_manifest.json")
    input_index = load_json(callable_output_root / "01_input_surface_index.json")

    run_context_import_ok = False
    run_context_import_error = None
    run_context = None

    try:
        module = guarded_import("app.mme_scalpx.replay.offline_context_shim")
        factory = getattr(module, "build_offline_replay_run_context")
        run_context = factory(
            project_root=project_root,
            dataset_candidate_root=dataset_candidate_root,
            callable_output_root=callable_output_root,
            materialization_root_29e=materialization_root_29e,
            output_root=output_root,
            metadata={
                "source_batch": "29G",
                "shim_root_29f": str(shim_root_29f),
                "dataset_manifest_present": bool(dataset_manifest),
                "input_surface_count": len(input_index.get("input_surfaces", {}) if isinstance(input_index.get("input_surfaces"), dict) else {}),
            },
        )
        run_context_import_ok = True
    except Exception as exc:
        run_context_import_error = f"{type(exc).__name__}: {exc}"

    values = {
        "project_root": project_root,
        "root": project_root,
        "dataset_candidate_root": dataset_candidate_root,
        "dataset_root": dataset_candidate_root,
        "dataset_path": dataset_candidate_root,
        "input_root": dataset_candidate_root,
        "input_dir": dataset_candidate_root,
        "callable_output_root": callable_output_root,
        "previous_output_root": callable_output_root,
        "materialization_root_29e": materialization_root_29e,
        "shim_root_29f": shim_root_29f,
        "adapter_root_29c": adapter_root_29c,
        "output_root": output_root,
        "out_root": output_root,
        "run_dir": output_root,
        "artifact_root": output_root,
        "dataset_manifest": dataset_manifest,
        "input_index": input_index,
        "no_broker": True,
        "no_live_redis": True,
        "observe_only": True,
        "dry_run": True,
    }

    topology_selected = None
    stage_selected = None

    prior_selected = prior_29e_reconstruction.get("selected_surfaces")
    if isinstance(prior_selected, dict):
        topology_selected = prior_selected.get("topology_plan")
        stage_selected = prior_selected.get("stage_executor")

    if not topology_selected:
        topo_result = topology_report_29e.get("result") if isinstance(topology_report_29e.get("result"), dict) else {}
        topology_selected = topo_result.get("selected_candidate")

    if not stage_selected:
        stage_result = stage_report_29e.get("result") if isinstance(stage_report_29e.get("result"), dict) else {}
        stage_selected = stage_result.get("selected_candidate")

    topology_result = materialize_from_selected(
        target_name="topology_plan",
        selected_candidate=topology_selected,
        project_root=project_root,
        values=values,
    )

    stage_result = materialize_from_selected(
        target_name="stage_executor",
        selected_candidate=stage_selected,
        project_root=project_root,
        values=values,
    )

    topology_plan = topology_result.get("object")
    topology_wrap_report = {"wrapped": False, "reason": "not_attempted"}
    try:
        import importlib.util as _importlib_util_29k_r2
        import sys as _sys_29k_r2
        from pathlib import Path as _Path_29k_r2

        _locals_29k_r2 = locals()
        _project_root_29k_r2 = _locals_29k_r2.get("project_root")
        if _project_root_29k_r2 is None:
            _args_29k_r2 = _locals_29k_r2.get("args")
            _project_root_29k_r2 = getattr(_args_29k_r2, "project_root", ".")
        _shim_path_29k_r2 = (
            _Path_29k_r2(_project_root_29k_r2)
            / "app"
            / "mme_scalpx"
            / "replay"
            / "offline_context_shim.py"
        )
        _spec_29k_r2 = _importlib_util_29k_r2.spec_from_file_location(
            "offline_context_shim_29k_r2",
            str(_shim_path_29k_r2),
        )
        if _spec_29k_r2 is None or _spec_29k_r2.loader is None:
            raise RuntimeError(f"unable to load offline_context_shim from {_shim_path_29k_r2}")
        _module_29k_r2 = _importlib_util_29k_r2.module_from_spec(_spec_29k_r2)
        _sys_29k_r2.modules[_spec_29k_r2.name] = _module_29k_r2
        _spec_29k_r2.loader.exec_module(_module_29k_r2)
        _ensure_topology_29k_r2 = getattr(_module_29k_r2, "ensure_offline_topology_plan")

        _values_29k_r2 = {}
        if isinstance(_locals_29k_r2.get("values"), dict):
            _values_29k_r2.update(_locals_29k_r2.get("values"))
        _values_29k_r2["run_context"] = _locals_29k_r2.get("run_context")
        _dataset_root_29k_r2 = _locals_29k_r2.get("dataset_candidate_root")
        _values_29k_r2["dataset_id"] = getattr(_dataset_root_29k_r2, "name", None)

        topology_plan, topology_wrap_report = _ensure_topology_29k_r2(
            topology_plan,
            values=_values_29k_r2,
        )
    except Exception as exc:
        topology_wrap_report = {
            "wrapped": False,
            "reason": "topology_wrapper_failed",
            "error": f"{type(exc).__name__}: {exc}",
        }
    stage_executor = stage_result.get("object")
    stage_executor, stage_executor_wrap_report = wrap_stage_executor_mapping_29u_r2(
        stage_executor,
        stage_result,
    )

    context_reconstruction_ready = bool(
        run_context_import_ok
        and run_context is not None
        and topology_result.get("materialized")
        and stage_result.get("materialized")
        and shim_manifest.get("full_context_reconstruction_ready") is True
    )

    engine_import = import_surface(project_root, "app/mme_scalpx/replay/engine.py", "ReplayEngine")
    engine_instance = None
    engine_instance_ready = False
    engine_error = None

    if engine_import.get("ok"):
        try:
            engine_cls = engine_import["object"]
            sig = inspect.signature(engine_cls)
            init_binding = bind_kwargs(sig, values)
            if init_binding["ok"]:
                engine_instance = engine_cls(**init_binding["kwargs"])
                engine_instance_ready = True
            else:
                engine_error = {
                    "kind": "init_binding_missing_required",
                    "signature": init_binding["signature"],
                    "missing_required": init_binding["missing_required"],
                    "optional_unmapped": init_binding["optional_unmapped"],
                }
        except Exception as exc:
            engine_error = {"kind": "engine_instantiation_failed", "error": f"{type(exc).__name__}: {exc}"}
    else:
        engine_error = {"kind": "engine_import_failed", "errors": engine_import.get("errors")}

    execution_attempted = False
    execution_ok = False
    replay_run_completed = False
    execution_result_summary: dict[str, Any] = {}
    execute_binding_report: dict[str, Any] = {}

    if context_reconstruction_ready and engine_instance_ready:
        try:
            execute_method = getattr(engine_instance, "execute")
            sig = inspect.signature(execute_method)
            execute_values = dict(values)
            execute_values.update({
                "run_context": run_context,
                "topology_plan": topology_plan,
                "stage_executor": stage_executor,
            })
            binding = bind_kwargs(sig, execute_values)
            execute_binding_report = {k: v for k, v in binding.items() if k != "kwargs"}
            if binding["ok"]:
                execution_attempted = True
                result = execute_method(**binding["kwargs"])
                execution_ok = True
                replay_run_completed = True
                execution_result_summary = safe_result_summary(result)
            else:
                execution_result_summary = {
                    "error": "execute_binding_missing_required",
                    "missing_required": binding["missing_required"],
                    "signature": binding["signature"],
                    "optional_unmapped": binding["optional_unmapped"],
                }
        except Exception as exc:
            execution_result_summary = {"error": f"{type(exc).__name__}: {exc}"}

    write_json(output_root / "00_guarded_replay_engine_execute_manifest.json", {
        "schema_version": "guarded_replay_engine_execute_manifest_29g_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_REPLAY_ENGINE_EXECUTE_DRY_RUN_ONLY",
        "context_reconstruction_ready": context_reconstruction_ready,
        "engine_instance_ready": engine_instance_ready,
        "execution_attempted": execution_attempted,
        "execution_ok": execution_ok,
        "replay_core_executed": execution_ok,
        "replay_run_completed": replay_run_completed,
        "comparison_completed": False,
        "shim_manifest": shim_manifest,
        "adapter_manifest": adapter_manifest,
        "engine_error": engine_error,
        "candidate_executed": execution_ok,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_29G",
    })

    write_json(output_root / "01_context_reconstruction_report.json", {
        "schema_version": "context_reconstruction_report_29g_v1",
        "context_reconstruction_ready": context_reconstruction_ready,
        "run_context_import_ok": run_context_import_ok,
        "run_context_import_error": run_context_import_error,
        "run_context_summary": summarize_object(run_context) if run_context is not None else None,
        "topology_plan_result": {k: v for k, v in topology_result.items() if k != "object"},
        "stage_executor_result": {k: v for k, v in stage_result.items() if k != "object"},
        "stage_executor_wrap_report": stage_executor_wrap_report,
    })

    write_json(output_root / "02_engine_execution_report.json", {
        "schema_version": "engine_execution_report_29g_v1",
        "engine_import": {k: v for k, v in engine_import.items() if k != "object"},
        "engine_instance_ready": engine_instance_ready,
        "engine_error": engine_error,
        "execute_binding_report": execute_binding_report,
        "stage_executor_wrap_report": stage_executor_wrap_report,
        "execution_attempted": execution_attempted,
        "execution_ok": execution_ok,
        "replay_run_completed": replay_run_completed,
        "execution_result_summary": execution_result_summary,
    })

    write_json(output_root / "03_execution_output_summary.json", {
        "schema_version": "execution_output_summary_29g_v1",
        "execution_ok": execution_ok,
        "replay_run_completed": replay_run_completed,
        "result_summary": execution_result_summary,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_29G",
    })

    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", {
        "schema_version": "guarded_execute_no_boundary_29g_v1",
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
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_29G",
    })

    if execution_ok:
        next_batch = "Batch 29H — inspect ReplayEngine dry-run outputs and build replay/live parity comparison contract, still not paper/live enablement."
        next_path = "REPLAY_ENGINE_DRY_RUN_OUTPUT_INSPECTION_READY"
    else:
        next_batch = "Batch 29H — repair guarded ReplayEngine dry-run runtime gap before output comparison, still not paper/live enablement."
        next_path = "REPLAY_ENGINE_DRY_RUN_RUNTIME_GAP"

    write_json(output_root / "05_next_replay_output_parity_contract.json", {
        "schema_version": "next_replay_output_parity_contract_29g_v1",
        "next_batch": next_batch,
        "next_path": next_path,
        "execution_ok": execution_ok,
        "replay_run_completed": replay_run_completed,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_29G",
        "allowed_next_actions": [
            "inspect offline ReplayEngine outputs only if execution_ok=true",
            "compare only against observe_only captured evidence outputs",
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
        "schema_version": "guarded_replay_engine_execute_result_29g_v1",
        "accepted_for": "GUARDED_REPLAY_ENGINE_EXECUTE_DRY_RUN_ONLY",
        "context_reconstruction_ready": context_reconstruction_ready,
        "engine_instance_ready": engine_instance_ready,
        "execution_attempted": execution_attempted,
        "execution_ok": execution_ok,
        "candidate_executed": execution_ok,
        "replay_core_executed": execution_ok,
        "replay_run_completed": replay_run_completed,
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
        "full_live_replay_parity": "NOT_PROVEN_IN_29G",
        "next_batch": next_batch,
    }
    # BATCH29AW_R9_FORCE_OUTPUT_ROOT_PROVIDER_FEATURE_SUMMARY_EMIT
    _batch29aw_r9_locals = locals()
    _batch29aw_r9_args = _batch29aw_r9_locals.get("args")
    _batch29aw_r9_sources = {
        "stdout_result": result if isinstance(result, dict) else {},
        "boundary": _batch29aw_r9_locals.get("boundary") if isinstance(_batch29aw_r9_locals.get("boundary"), dict) else {},
        "context": _batch29aw_r9_locals.get("context") if isinstance(_batch29aw_r9_locals.get("context"), dict) else {},
        "engine_report": _batch29aw_r9_locals.get("engine_report") if isinstance(_batch29aw_r9_locals.get("engine_report"), dict) else {},
        "execution_summary": _batch29aw_r9_locals.get("execution_summary") if isinstance(_batch29aw_r9_locals.get("execution_summary"), dict) else {},
    }
    _batch29aw_provider_feature_summary, _batch29aw_provider_feature_summary_path = _batch29aw_r9_force_provider_feature_summary(
        _batch29aw_r9_args,
        result if isinstance(result, dict) else {},
        source_payloads=_batch29aw_r9_sources,
    )
    if isinstance(result, dict):
        result["provider_feature_summary_path"] = _batch29aw_provider_feature_summary_path
        result["provider_feature_summary_found"] = bool(_batch29aw_provider_feature_summary_path)
        result["provider_feature_field_count"] = _batch29aw_provider_feature_summary.get("field_count")
        result["known_boolean_count"] = _batch29aw_provider_feature_summary.get("known_boolean_count")
        result["null_value_count"] = _batch29aw_provider_feature_summary.get("null_value_count")
        result["provider_feature_value_comparison_ready"] = _batch29aw_provider_feature_summary.get("value_comparison_ready") is True
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if execution_ok else 2

if __name__ == "__main__":
    raise SystemExit(main())
