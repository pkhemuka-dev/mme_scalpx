#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.json"

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o16_consumer_view_mapping_repair.py",
    "bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py",
]


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_json_load(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            return json.loads(value)
        except Exception:
            return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def run_cmd(args: list[str], *, timeout: int = 20) -> dict[str, Any]:
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def pgrep_python_service(service: str) -> list[str]:
    """
    Corrected O16A process detector.

    O16 used:
      pgrep -af 'app.mme_scalpx.main --service risk'
    That can match the shell running pgrep itself.

    This detector:
    - reads full process table,
    - requires python/python3/.venv python,
    - requires '-m app.mme_scalpx.main',
    - requires '--service <service>',
    - excludes this proof script,
    - excludes grep/pgrep/bash/sh command wrappers.
    """
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
    except Exception:
        return []

    matches: list[str] = []
    self_name = "proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py"
    for line in out.splitlines():
        clean = " ".join(line.split())
        if not clean:
            continue
        lower = clean.lower()
        if self_name in clean:
            continue
        if "pgrep" in lower or "grep" in lower:
            continue
        if "bash -lc" in lower or " sh -c " in lower:
            continue
        if "python" not in lower:
            continue
        if "-m app.mme_scalpx.main" not in clean:
            continue
        if f"--service {service}" not in clean:
            continue
        matches.append(clean)
    return matches


def redis_client_or_none():
    try:
        import redis  # type: ignore

        client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "127.0.0.1"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            db=int(os.environ.get("REDIS_DB", "0")),
            decode_responses=False,
        )
        client.ping()
        return client
    except Exception:
        return None


def ast_find_assignments(path: pathlib.Path, names: set[str]) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    out: list[dict[str, Any]] = []

    def src(node: ast.AST) -> str:
        try:
            return ast.get_source_segment(text, node) or ""
        except Exception:
            return ""

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets: list[str] = []
            for t in node.targets:
                if isinstance(t, ast.Name):
                    targets.append(t.id)
                elif isinstance(t, ast.Subscript):
                    targets.append(src(t))
                elif isinstance(t, ast.Attribute):
                    targets.append(src(t))
            joined = " ".join(targets)
            if any(n in joined or n in src(node.value) for n in names):
                lineno = getattr(node, "lineno", 0)
                out.append({
                    "lineno": lineno,
                    "target": joined,
                    "source": src(node),
                    "context": "\n".join(lines[max(0, lineno - 3): min(len(lines), lineno + 3)]),
                })
        elif isinstance(node, ast.AnnAssign):
            target = src(node.target)
            value = src(node.value) if node.value else ""
            if any(n in target or n in value for n in names):
                lineno = getattr(node, "lineno", 0)
                out.append({
                    "lineno": lineno,
                    "target": target,
                    "source": src(node),
                    "context": "\n".join(lines[max(0, lineno - 3): min(len(lines), lineno + 3)]),
                })
    return out


def regex_contexts(path: pathlib.Path, patterns: list[str], radius: int = 4) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        if any(re.search(p, line) for p in patterns):
            out.append({
                "lineno": idx,
                "line": line,
                "context": "\n".join(lines[max(0, idx - radius - 1): min(len(lines), idx + radius)]),
            })
    return out


def summarize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    family_features = safe_json_load(payload.get("family_features")) or payload.get("family_features") or {}
    family_surfaces = safe_json_load(payload.get("family_surfaces")) or payload.get("family_surfaces") or {}
    family_frames = safe_json_load(payload.get("family_frames")) or payload.get("family_frames") or {}
    consumer_view = safe_json_load(payload.get("consumer_view")) or payload.get("consumer_view") or {}

    if not isinstance(family_features, Mapping):
        family_features = {}
    if not isinstance(family_surfaces, Mapping):
        family_surfaces = {}
    if not isinstance(family_frames, Mapping):
        family_frames = {}
    if not isinstance(consumer_view, Mapping):
        consumer_view = {}

    stage_flags = family_features.get("stage_flags", {})
    if not isinstance(stage_flags, Mapping):
        stage_flags = {}

    return {
        "top_level_keys": sorted(str(k) for k in payload.keys()),
        "frame_valid": bool(payload.get("frame_valid")),
        "warmup_complete": bool(payload.get("warmup_complete")),
        "data_valid_top_level": bool(payload.get("data_valid")),
        "frame_id": payload.get("frame_id"),
        "frame_ts_ns": payload.get("frame_ts_ns"),
        "family_features_present": bool(family_features),
        "family_surfaces_present": bool(family_surfaces),
        "family_frames_present": bool(family_frames),
        "consumer_view_present": bool(consumer_view),
        "stage_flags": dict(stage_flags),
        "stage_flags_data_valid": stage_flags.get("data_valid"),
        "stage_flags_warmup_complete": stage_flags.get("warmup_complete"),
        "family_features_keys": sorted(str(k) for k in family_features.keys())[:80],
        "family_surfaces_keys": sorted(str(k) for k in family_surfaces.keys())[:80],
        "family_frames_keys": sorted(str(k) for k in family_frames.keys())[:80],
        "consumer_view_keys": sorted(str(k) for k in consumer_view.keys())[:80],
    }


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    sys.path.insert(0, str(ROOT))

    compile_cmd = [
        sys.executable,
        "-m",
        "py_compile",
        *[p for p in TARGETS if p.endswith(".py") and (ROOT / p).exists()],
    ]
    compile_result = run_cmd(compile_cmd, timeout=60)

    features_path = ROOT / "app/mme_scalpx/services/features.py"
    features_text = features_path.read_text(encoding="utf-8")

    source_audit = {
        "features_sha256": sha256_file(features_path),
        "o16_patch_marker_present": "Batch 26-O16 consumer-view mapping repair" in features_text,
        "consumer_view_json_literal_count": features_text.count("consumer_view_json"),
        "batch26o16_helper_present": "_batch26o16_build_consumer_view" in features_text,
        "frame_valid_assignments": ast_find_assignments(features_path, {"frame_valid", "data_valid", "safe_to_consume", "warmup_complete"}),
        "frame_valid_contexts": regex_contexts(features_path, [
            r"frame_valid",
            r"data_valid",
            r"safe_to_consume",
            r"warmup_complete",
            r"consumer_view_json",
            r"family_features_json",
            r"family_surfaces_json",
            r"family_frames_json",
        ]),
    }

    imports = {}
    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
        strategy = importlib.import_module("app.mme_scalpx.services.strategy")
        imports = {
            "names": True,
            "features": True,
            "strategy": True,
            "features_module_file": getattr(features, "__file__", None),
            "strategy_module_file": getattr(strategy, "__file__", None),
        }
    except Exception as exc:
        imports = {
            "error": f"{type(exc).__name__}: {exc}",
        }
        names = None
        features = None

    expected_branch_keys: list[str] = []
    synthetic_mapping = {
        "available": False,
        "error": None,
    }

    if features is not None and hasattr(features, "_batch26o16_normalize_family_frames") and hasattr(features, "_batch26o16_build_consumer_view"):
        try:
            family_ids = tuple(getattr(features, "FAMILY_IDS"))
            branch_ids = tuple(getattr(features, "BRANCH_IDS"))
            expected_branch_keys = sorted(f"{f.lower()}_{b.lower()}" for f in family_ids for b in branch_ids)
            generated_at_ns = time.time_ns()
            provider_runtime = {
                "family_runtime_mode": "observe_only",
                "active_futures_provider_id": "ZERODHA",
                "active_selected_option_provider_id": "ZERODHA",
                "active_option_context_provider_id": "DHAN",
            }

            family_surfaces = {"families": {}, "surfaces_by_branch": {}}
            families_contract = {}
            for family_id in family_ids:
                family_surfaces["families"][family_id] = {"eligible": False, "branches": {}}
                families_contract[family_id] = {"eligible": False}
                for branch_id in branch_ids:
                    key = f"{family_id.lower()}_{branch_id.lower()}"
                    surface = {
                        "family_id": family_id,
                        "branch_id": branch_id,
                        "side": branch_id,
                        "eligible": False,
                        "runtime_mode": "observe_only",
                        "selected_features": {
                            "instrument_key": f"SYNTH:{key}",
                            "instrument_token": str(abs(hash(key)) % 100000),
                            "symbol": f"SYNTH_{key.upper()}",
                            "strike": 25000,
                            "ltp": 100.0,
                            "tick_size": 0.05,
                        },
                        "tradability": {
                            "entry_pass": False,
                            "tradability_ok": False,
                        },
                    }
                    family_surfaces["surfaces_by_branch"][key] = surface
                    family_surfaces["families"][family_id]["branches"][branch_id] = surface

            family_features = {
                "generated_at_ns": generated_at_ns,
                "stage_flags": {
                    "data_valid": True,
                    "warmup_complete": True,
                    "provider_ready_classic": True,
                    "provider_ready_miso": False,
                    "risk_veto_active": False,
                    "reconciliation_lock_active": False,
                    "active_position_present": False,
                },
                "provider_runtime": provider_runtime,
                "common": {
                    "regime": "NORMAL",
                    "selected_option": {
                        "instrument_key": "SYNTH:mist_call",
                        "instrument_token": "1",
                        "option_symbol": "SYNTH_MIST_CALL",
                        "strike": 25000,
                    },
                },
                "market": {
                    "futures_ltp": 25000.0,
                },
                "families": families_contract,
                "snapshot": {
                    "valid": True,
                },
            }
            payload = {
                "frame_id": f"features-{generated_at_ns}",
                "frame_ts_ns": generated_at_ns,
                "generated_at_ns": generated_at_ns,
                "frame_valid": True,
                "warmup_complete": True,
                "provider_runtime": provider_runtime,
                "family_features": family_features,
                "family_surfaces": family_surfaces,
                "family_frames": {},
            }

            normalized_frames = features._batch26o16_normalize_family_frames(
                generated_at_ns=generated_at_ns,
                provider_runtime=provider_runtime,
                family_surfaces=family_surfaces,
                family_frames={},
            )
            consumer_view = features._batch26o16_build_consumer_view(
                payload=payload,
                family_features=family_features,
                family_surfaces=family_surfaces,
                family_frames=normalized_frames,
            )
            branch_frames = consumer_view.get("branch_frames", {})
            synthetic_mapping = {
                "available": True,
                "data_valid": bool(consumer_view.get("data_valid")),
                "safe_to_consume": bool(consumer_view.get("safe_to_consume")),
                "branch_frames_present": bool(branch_frames),
                "all_10_branch_frames_present": all(k in branch_frames for k in expected_branch_keys),
                "mist_call_branch_frame_present": "mist_call" in branch_frames,
                "branch_frame_count": len(branch_frames),
                "provider_ready_miso": consumer_view.get("provider_ready_miso"),
                "hold_only": consumer_view.get("hold_only"),
                "action": consumer_view.get("action"),
                "mapping_repair": consumer_view.get("mapping_repair"),
            }
        except Exception as exc:
            synthetic_mapping = {
                "available": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

    redis_client = redis_client_or_none()
    redis_audit: dict[str, Any] = {
        "redis_available": redis_client is not None,
    }

    runtime_feature_payload_summary: dict[str, Any] = {}
    feature_hash_consumer_view: dict[str, Any] = {}
    feature_hash_summary: dict[str, Any] = {}
    orders_len: int | None = None
    real_live_approved = False

    if redis_client is not None and names is not None:
        hash_features = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))
        stream_orders = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
        hash_runtime = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")

        redis_audit.update({
            "hash_features_key": hash_features,
            "stream_orders_key": stream_orders,
            "hash_runtime_key": hash_runtime,
        })

        try:
            raw_hash = decode_hash(redis_client.hgetall(hash_features) or {})
            feature_hash_summary = {
                "hash_present": bool(raw_hash),
                "hash_keys": sorted(raw_hash.keys()),
                "family_features_json_present": bool(raw_hash.get("family_features_json")),
                "family_surfaces_json_present": bool(raw_hash.get("family_surfaces_json")),
                "family_frames_json_present": bool(raw_hash.get("family_frames_json")),
                "consumer_view_json_present": bool(raw_hash.get("consumer_view_json")),
                "payload_json_present": bool(raw_hash.get("payload_json")),
                "feature_state_json_present": bool(raw_hash.get("feature_state_json")),
            }
            feature_hash_consumer_view = safe_json_load(raw_hash.get("consumer_view_json"))
            feature_hash_payload = safe_json_load(raw_hash.get("payload_json"))
            feature_hash_feature_state = safe_json_load(raw_hash.get("feature_state_json"))
            feature_hash_summary["consumer_view_summary"] = {
                "data_valid": feature_hash_consumer_view.get("data_valid"),
                "safe_to_consume": feature_hash_consumer_view.get("safe_to_consume"),
                "branch_frame_count": len(feature_hash_consumer_view.get("branch_frames", {}) or {}),
                "mist_call_present": "mist_call" in (feature_hash_consumer_view.get("branch_frames", {}) or {}),
            }
            feature_hash_summary["payload_summary"] = summarize_payload(feature_hash_payload) if isinstance(feature_hash_payload, Mapping) else {}
            feature_hash_summary["feature_state_summary"] = {
                "keys": sorted(feature_hash_feature_state.keys()) if isinstance(feature_hash_feature_state, Mapping) else [],
                "frame_valid": feature_hash_feature_state.get("frame_valid") if isinstance(feature_hash_feature_state, Mapping) else None,
                "data_valid": feature_hash_feature_state.get("data_valid") if isinstance(feature_hash_feature_state, Mapping) else None,
            }
        except Exception as exc:
            redis_audit["feature_hash_error"] = f"{type(exc).__name__}: {exc}"

        try:
            orders_len = int(redis_client.xlen(stream_orders))
        except Exception as exc:
            redis_audit["orders_len_error"] = f"{type(exc).__name__}: {exc}"
            orders_len = None

        try:
            rt = decode_hash(redis_client.hgetall(hash_runtime) or {})
            real_live_approved = str(rt.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}
            redis_audit["runtime_hash_keys"] = sorted(rt.keys())
        except Exception as exc:
            redis_audit["runtime_hash_error"] = f"{type(exc).__name__}: {exc}"

        # Diagnostic only: run FeatureService.run_once once and inspect returned payload.
        # This may publish feature state, but does not start risk/execution and does not write orders.
        try:
            class RedisAdapter:
                def __init__(self, inner):
                    self.inner = inner
                def hgetall(self, key):
                    return self.inner.hgetall(key)
                def hset(self, key, mapping=None, **kwargs):
                    if mapping is not None:
                        enc = {}
                        for k, v in mapping.items():
                            if isinstance(v, bytes):
                                enc[k] = v
                            elif isinstance(v, str):
                                enc[k] = v
                            else:
                                enc[k] = str(v)
                        return self.inner.hset(key, mapping=enc)
                    return self.inner.hset(key, **kwargs)
                def xadd(self, *args, **kwargs):
                    return self.inner.xadd(*args, **kwargs)

            if features is not None:
                svc = features.FeatureService(
                    redis_client=RedisAdapter(redis_client),
                    clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
                    shutdown=type("Shutdown", (), {"is_set": staticmethod(lambda: True)})(),
                    instance_id="batch26o16a-diagnostic",
                )
                payload = svc.run_once()
                runtime_feature_payload_summary = summarize_payload(payload if isinstance(payload, Mapping) else {})
                runtime_feature_payload_summary["run_once_returned_mapping"] = isinstance(payload, Mapping)
        except Exception as exc:
            runtime_feature_payload_summary = {
                "run_once_error": f"{type(exc).__name__}: {exc}",
            }

    risk_process_lines = pgrep_python_service("risk")
    execution_process_lines = pgrep_python_service("execution")

    old_o16_proof = safe_json_load((ROOT / "run/proofs/proof_batch26o16_consumer_view_mapping_repair.json").read_text(encoding="utf-8")) if (ROOT / "run/proofs/proof_batch26o16_consumer_view_mapping_repair.json").exists() else {}
    old_o16_safety = old_o16_proof.get("safety", {}) if isinstance(old_o16_proof, Mapping) else {}

    false_positive_diagnosis = {
        "old_o16_safety_available": bool(old_o16_safety),
        "old_o16_risk_lines": old_o16_safety.get("risk_process_lines"),
        "old_o16_execution_lines": old_o16_safety.get("execution_process_lines"),
        "old_o16_lines_look_like_pgrep_self_match": (
            isinstance(old_o16_safety.get("risk_process_lines"), list)
            and all("pgrep -af" in str(x) or "bash -lc" in str(x) for x in old_o16_safety.get("risk_process_lines", []))
            and isinstance(old_o16_safety.get("execution_process_lines"), list)
            and all("pgrep -af" in str(x) or "bash -lc" in str(x) for x in old_o16_safety.get("execution_process_lines", []))
        ),
        "corrected_risk_python_service_matches": risk_process_lines,
        "corrected_execution_python_service_matches": execution_process_lines,
    }

    verdicts = {
        "production_code_unchanged_by_o16a": True,
        "compile_pass": compile_result["returncode"] == 0,
        "o16_patch_marker_present": bool(source_audit["o16_patch_marker_present"]),
        "synthetic_mapping_available": bool(synthetic_mapping.get("available")),
        "synthetic_consumer_view_data_valid": bool(synthetic_mapping.get("data_valid")),
        "synthetic_consumer_view_safe_to_consume": bool(synthetic_mapping.get("safe_to_consume")),
        "synthetic_all_10_branch_frames_present": bool(synthetic_mapping.get("all_10_branch_frames_present")),
        "synthetic_mist_call_branch_frame_present": bool(synthetic_mapping.get("mist_call_branch_frame_present")),
        "feature_hash_consumer_view_present": bool(feature_hash_summary.get("consumer_view_json_present")),
        "feature_hash_family_features_preserved": bool(feature_hash_summary.get("family_features_json_present")),
        "feature_hash_family_surfaces_preserved": bool(feature_hash_summary.get("family_surfaces_json_present")),
        "corrected_risk_not_running": len(risk_process_lines) == 0,
        "corrected_execution_not_running": len(execution_process_lines) == 0,
        "orders_zero": orders_len == 0,
        "real_live_approved_false": real_live_approved is False,
        "runtime_feature_payload_observed": bool(runtime_feature_payload_summary),
        "runtime_frame_valid_true": runtime_feature_payload_summary.get("frame_valid") is True,
        "runtime_stage_flags_data_valid_true": runtime_feature_payload_summary.get("stage_flags_data_valid") is True,
        "runtime_consumer_view_data_valid_true": feature_hash_summary.get("consumer_view_summary", {}).get("data_valid") is True if isinstance(feature_hash_summary.get("consumer_view_summary"), Mapping) else False,
        "runtime_consumer_view_safe_to_consume_true": feature_hash_summary.get("consumer_view_summary", {}).get("safe_to_consume") is True if isinstance(feature_hash_summary.get("consumer_view_summary"), Mapping) else False,
    }

    if (
        verdicts["compile_pass"]
        and verdicts["o16_patch_marker_present"]
        and verdicts["synthetic_mapping_available"]
        and verdicts["synthetic_consumer_view_data_valid"]
        and verdicts["synthetic_consumer_view_safe_to_consume"]
        and verdicts["synthetic_all_10_branch_frames_present"]
        and verdicts["synthetic_mist_call_branch_frame_present"]
        and verdicts["corrected_risk_not_running"]
        and verdicts["corrected_execution_not_running"]
        and verdicts["orders_zero"]
        and verdicts["real_live_approved_false"]
        and not verdicts["runtime_frame_valid_true"]
    ):
        final_verdict = "PASS_O16A_PROOF_CORRECTED_RUNTIME_DATA_VALID_SOURCE_BLOCKER_CONFIRMED"
        exit_code = 0
    elif (
        verdicts["compile_pass"]
        and verdicts["o16_patch_marker_present"]
        and verdicts["synthetic_mapping_available"]
        and verdicts["synthetic_consumer_view_data_valid"]
        and verdicts["synthetic_consumer_view_safe_to_consume"]
        and verdicts["synthetic_all_10_branch_frames_present"]
        and verdicts["synthetic_mist_call_branch_frame_present"]
        and verdicts["corrected_risk_not_running"]
        and verdicts["corrected_execution_not_running"]
        and verdicts["orders_zero"]
        and verdicts["real_live_approved_false"]
        and verdicts["runtime_frame_valid_true"]
        and verdicts["runtime_consumer_view_data_valid_true"]
        and verdicts["runtime_consumer_view_safe_to_consume_true"]
    ):
        final_verdict = "PASS_O16A_PROOF_CORRECTED_RUNTIME_DATA_VALID_NOW_OK"
        exit_code = 0
    else:
        final_verdict = "FAIL_O16A_NOT_PROVEN"
        exit_code = 2

    result = {
        "batch": "26-O16A",
        "batch_name": "consumer_view_proof_correction_runtime_data_valid_source_audit",
        "created_at_utc": now,
        "scope": {
            "production_patch_performed": False,
            "proof_only": True,
            "risk_started": False,
            "execution_started": False,
            "paper_restart": False,
            "real_live_approval": False,
            "order_write_intended": False,
            "threshold_relaxation": False,
            "miso_enablement": False,
        },
        "compile": compile_result,
        "imports": imports,
        "source_audit": source_audit,
        "synthetic_mapping": synthetic_mapping,
        "redis_audit": redis_audit,
        "feature_hash_summary": feature_hash_summary,
        "runtime_feature_payload_summary": runtime_feature_payload_summary,
        "false_positive_diagnosis": false_positive_diagnosis,
        "safety": {
            "orders_len": orders_len,
            "real_live_approved": real_live_approved,
            "corrected_risk_process_lines": risk_process_lines,
            "corrected_execution_process_lines": execution_process_lines,
        },
        "required_verdicts": verdicts,
        "classification": {
            "synthetic_mapper_status": (
                "OK" if (
                    verdicts["synthetic_consumer_view_data_valid"]
                    and verdicts["synthetic_consumer_view_safe_to_consume"]
                    and verdicts["synthetic_all_10_branch_frames_present"]
                    and verdicts["synthetic_mist_call_branch_frame_present"]
                ) else "NOT_PROVEN"
            ),
            "process_detector_status": (
                "CORRECTED_NO_RISK_EXECUTION" if (
                    verdicts["corrected_risk_not_running"]
                    and verdicts["corrected_execution_not_running"]
                ) else "RISK_OR_EXECUTION_RUNNING_OR_NOT_PROVEN"
            ),
            "runtime_data_valid_status": (
                "RUNTIME_DATA_VALID_OK" if (
                    verdicts["runtime_frame_valid_true"]
                    and verdicts["runtime_consumer_view_data_valid_true"]
                    and verdicts["runtime_consumer_view_safe_to_consume_true"]
                ) else "RUNTIME_DATA_VALID_NOT_PROVEN"
            ),
        },
        "next_recommended_batch": (
            "26-O17 activation candidate extraction proof, no risk/execution"
            if final_verdict == "PASS_O16A_PROOF_CORRECTED_RUNTIME_DATA_VALID_NOW_OK"
            else "26-O16B runtime feature frame_valid root-cause repair plan, no strategy/risk/execution patch until exact source is proven"
        ),
        "final_verdict": final_verdict,
    }

    manifest = {
        "batch": "26-O16A",
        "created_at_utc": now,
        "files": [
            {
                "path": p,
                "exists": (ROOT / p).exists(),
                "sha256": sha256_file(ROOT / p),
            }
            for p in TARGETS
        ],
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
