#!/usr/bin/env python3
from __future__ import annotations

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O17"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o17_activation_candidate_extraction.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o17_activation_candidate_extraction.json"
O16H_R2_PATH = ROOT / "run/proofs/proof_batch26o16h_r2_persistent_final_composition.json"

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o17_activation_candidate_extraction.py",
    "run/proofs/proof_batch26o16h_r2_persistent_final_composition.json",
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


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    return {"args": args, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def pgrep_service(service: str) -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
    except Exception:
        return []
    matches: list[str] = []
    self_name = "proof_batch26o17_activation_candidate_extraction.py"
    for line in out.splitlines():
        clean = " ".join(line.split())
        lower = clean.lower()
        if not clean or self_name in clean:
            continue
        if "grep" in lower or "pgrep" in lower or "bash -lc" in lower or " sh -c " in lower:
            continue
        if "python" not in lower:
            continue
        if "-m app.mme_scalpx.main" not in clean:
            continue
        if f"--service {service}" not in clean:
            continue
        matches.append(clean)
    return matches


def grep_context(path: pathlib.Path, patterns: list[str], radius: int = 4) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
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


def build_redis_adapter(redis_client: Any):
    class RedisAdapter:
        def __init__(self, inner):
            self.inner = inner
        def hgetall(self, key):
            return self.inner.hgetall(key)
        def hset(self, key, mapping=None, **kwargs):
            if mapping is not None:
                return self.inner.hset(key, mapping={k: (v if isinstance(v, str) else str(v)) for k, v in mapping.items()})
            return self.inner.hset(key, **kwargs)
        def xadd(self, *args, **kwargs):
            return self.inner.xadd(*args, **kwargs)
        def xlen(self, *args, **kwargs):
            return self.inner.xlen(*args, **kwargs)
        def xrevrange(self, *args, **kwargs):
            return self.inner.xrevrange(*args, **kwargs)
    return RedisAdapter(redis_client)


def run_feature_once(features_mod: Any, redis_client: Any) -> Mapping[str, Any]:
    svc = features_mod.FeatureService(
        redis_client=build_redis_adapter(redis_client),
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o17-feature",
    )
    payload = svc.run_once()
    return payload if isinstance(payload, Mapping) else {}


def hget_json(redis_client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        value = redis_client.hget(key, field)
        parsed = safe_json_load(value)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def stream_latest(redis_client: Any, key: str, count: int = 3) -> list[dict[str, Any]]:
    try:
        rows = redis_client.xrevrange(key, count=count)
        out = []
        for msg_id, fields in rows:
            out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
        return out
    except Exception:
        return []


def call_maybe(fn: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    name = getattr(fn, "__name__", str(fn))
    try:
        sig = inspect.signature(fn)
        return {
            "name": name,
            "signature": str(sig),
            "callable": True,
            "called": False,
            "result": None,
            "error": None,
        }
    except Exception as exc:
        return {
            "name": name,
            "signature": None,
            "callable": callable(fn),
            "called": False,
            "result": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def summarize_activation_modules() -> dict[str, Any]:
    modules = {}
    module_names = {
        "activation": "app.mme_scalpx.services.strategy_family.activation",
        "eligibility": "app.mme_scalpx.services.strategy_family.eligibility",
        "arbitration": "app.mme_scalpx.services.strategy_family.arbitration",
        "decisions": "app.mme_scalpx.services.strategy_family.decisions",
    }
    for label, mod_name in module_names.items():
        try:
            mod = importlib.import_module(mod_name)
            funcs = {}
            for name, obj in sorted(vars(mod).items()):
                if name.startswith("_"):
                    continue
                if callable(obj):
                    try:
                        funcs[name] = str(inspect.signature(obj))
                    except Exception:
                        funcs[name] = "SIGNATURE_UNAVAILABLE"
            modules[label] = {
                "import_ok": True,
                "file": getattr(mod, "__file__", None),
                "callables": funcs,
            }
        except Exception as exc:
            modules[label] = {
                "import_ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
    return modules


def summarize_consumer_view(cv: Mapping[str, Any]) -> dict[str, Any]:
    branch_frames = cv.get("branch_frames", {})
    if not isinstance(branch_frames, Mapping):
        branch_frames = {}
    mist_call = branch_frames.get("mist_call", {})
    if not isinstance(mist_call, Mapping):
        mist_call = {}
    return {
        "present": bool(cv),
        "data_valid": cv.get("data_valid"),
        "safe_to_consume": cv.get("safe_to_consume"),
        "branch_frame_count": len(branch_frames),
        "branch_frame_keys": sorted(str(k) for k in branch_frames.keys()),
        "mist_call_present": "mist_call" in branch_frames,
        "mist_call_keys": sorted(str(k) for k in mist_call.keys())[:100],
        "mist_call_preview": mist_call,
    }


def synthetic_candidate_scan(cv: Mapping[str, Any]) -> dict[str, Any]:
    """
    This is not a strategy decision. It only proves whether activation has an
    accessible, valid MIST CALL branch frame and whether obvious direct blockers
    exist before doctrine leaf evaluation.
    """
    branch_frames = cv.get("branch_frames", {})
    if not isinstance(branch_frames, Mapping):
        branch_frames = {}
    mist_call = branch_frames.get("mist_call", {})
    if not isinstance(mist_call, Mapping):
        mist_call = {}

    text = json.dumps(mist_call, sort_keys=True, default=str).lower()
    blockers = []
    positive_terms = []
    for term in [
        "data_valid",
        "safe_to_consume",
        "present",
        "provider_ready",
        "branch_ready",
        "tradability_ok",
        "entry_pass",
        "selected_features",
        "option_features",
        "primary_features",
        "trend_confirmed",
        "pullback_detected",
        "resume_confirmed",
    ]:
        if term in text:
            positive_terms.append(term)

    for term in [
        "data_valid\": false",
        "safe_to_consume\": false",
        "present\": false",
        "provider_ready\": false",
        "branch_ready\": false",
        "tradability_ok\": false",
        "entry_pass\": false",
        "runtime_disabled",
        "view_data_invalid",
        "leaf_evaluation_skipped",
    ]:
        if term in text:
            blockers.append(term)

    return {
        "activation_view_accessible": bool(cv and cv.get("data_valid") is True and cv.get("safe_to_consume") is True),
        "mist_call_branch_accessible": bool(mist_call),
        "positive_terms": positive_terms,
        "direct_blocker_terms": blockers,
        "candidate_extraction_possible": bool(cv and cv.get("data_valid") is True and cv.get("safe_to_consume") is True and mist_call),
    }


def run_strategy_once_if_available(strategy_mod: Any, redis_client: Any) -> dict[str, Any]:
    """
    Avoid starting strategy service. Try only in-process if a safe Feature-like/Strategy-like
    service method exists. If constructor is unknown, do not force-call.
    """
    out: dict[str, Any] = {
        "attempted": False,
        "safe_inprocess_only": True,
        "result": None,
        "error": None,
        "reason": None,
    }

    svc_cls = getattr(strategy_mod, "StrategyService", None) or getattr(strategy_mod, "Service", None)
    if svc_cls is None:
        out["reason"] = "No StrategyService/Service class found"
        return out

    try:
        sig = inspect.signature(svc_cls)
        out["constructor_signature"] = str(sig)
    except Exception:
        out["constructor_signature"] = "UNAVAILABLE"

    try:
        svc = svc_cls(
            redis_client=build_redis_adapter(redis_client),
            clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
            shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
            instance_id="batch26o17-strategy",
        )
    except Exception as exc:
        out["reason"] = "Constructor not safely callable with standard args"
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    for method_name in ("run_once", "tick", "evaluate_once", "evaluate"):
        method = getattr(svc, method_name, None)
        if callable(method):
            try:
                before = time.time_ns()
                result = method()
                after = time.time_ns()
                out.update({
                    "attempted": True,
                    "method": method_name,
                    "duration_ns": after - before,
                    "result": result if isinstance(result, (dict, list, str, int, float, bool, type(None))) else repr(result),
                    "error": None,
                })
                return out
            except Exception as exc:
                out.update({
                    "attempted": True,
                    "method": method_name,
                    "result": None,
                    "error": f"{type(exc).__name__}: {exc}",
                })
                return out

    out["reason"] = "No safe one-shot method found"
    return out


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": [
            {"path": p, "exists": (ROOT / p).exists(), "sha256": sha256_file(ROOT / p)}
            for p in TARGETS
        ],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> int:
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "activation_candidate_extraction",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "audit_proof_only": True,
            "paper_restart": False,
            "risk_started": False,
            "execution_started": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_approval": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
            "strategy_patch": False,
        },
    }

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None
    if redis_client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    o16h_r2 = safe_json_load(O16H_R2_PATH.read_text(encoding="utf-8")) if O16H_R2_PATH.exists() else {}
    result["o16h_r2_gate"] = {
        "exists": O16H_R2_PATH.exists(),
        "final_verdict": o16h_r2.get("final_verdict") if isinstance(o16h_r2, Mapping) else None,
        "required_verdicts": o16h_r2.get("required_verdicts") if isinstance(o16h_r2, Mapping) else None,
    }

    if o16h_r2.get("final_verdict") != "PASS_O16H_R2_RUNTIME_DATA_VALID_SAFE_TO_CONSUME_OK":
        result["final_verdict"] = "FAIL_CLOSED_O16H_R2_NOT_PASS"
        write_outputs(result)
        return 2

    compile_result = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/strategy_family/eligibility.py",
        "app/mme_scalpx/services/strategy_family/arbitration.py",
        "app/mme_scalpx/services/strategy_family/decisions.py",
        "app/mme_scalpx/services/feature_family/tradability.py",
        "app/mme_scalpx/services/feature_family/mist_surface.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile"] = compile_result

    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
        strategy = importlib.import_module("app.mme_scalpx.services.strategy")
    except Exception as exc:
        result["final_verdict"] = "FAIL_IMPORT_CONTEXT_NOT_READY"
        result["import_error"] = f"{type(exc).__name__}: {exc}"
        write_outputs(result)
        return 2

    orders_key = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
    runtime_key = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")
    features_key = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))
    decisions_key = getattr(names, "STREAM_DECISIONS_MME", "decisions:mme:stream")

    orders_before = int(redis_client.xlen(orders_key))
    decisions_before = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0
    rt_before = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_before = str(rt_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    feature_payload = run_feature_once(features, redis_client)
    feature_payload_summary = {
        "frame_valid": bool(feature_payload.get("frame_valid")),
        "keys": sorted(str(k) for k in feature_payload.keys()) if isinstance(feature_payload, Mapping) else [],
    }

    cv = hget_json(redis_client, features_key, "consumer_view_json")
    ff = hget_json(redis_client, features_key, "family_features_json")
    frames = hget_json(redis_client, features_key, "family_frames_json")

    consumer_view_summary = summarize_consumer_view(cv)
    scan_summary = synthetic_candidate_scan(cv)

    result["feature_payload_summary"] = feature_payload_summary
    result["consumer_view_summary"] = consumer_view_summary
    result["family_features_stage_flags"] = ff.get("stage_flags", {}) if isinstance(ff, Mapping) else {}
    result["family_frame_keys"] = sorted(str(k) for k in frames.keys()) if isinstance(frames, Mapping) else []
    result["synthetic_candidate_scan"] = scan_summary
    result["activation_module_summary"] = summarize_activation_modules()

    result["source_contexts"] = {
        "activation": grep_context(
            ROOT / "app/mme_scalpx/services/strategy_family/activation.py",
            [r"consumer_view", r"branch_frames", r"candidate", r"safe_to_consume", r"data_valid", r"mist_call", r"leaf"],
        ),
        "eligibility": grep_context(
            ROOT / "app/mme_scalpx/services/strategy_family/eligibility.py",
            [r"consumer_view", r"branch", r"candidate", r"eligible", r"data_valid", r"safe"],
        ),
        "arbitration": grep_context(
            ROOT / "app/mme_scalpx/services/strategy_family/arbitration.py",
            [r"candidate", r"score", r"select", r"arbit", r"mist_call"],
        ),
        "decisions": grep_context(
            ROOT / "app/mme_scalpx/services/strategy_family/decisions.py",
            [r"candidate", r"decision", r"HOLD", r"ENTRY", r"promot", r"safe"],
        ),
        "strategy": grep_context(
            ROOT / "app/mme_scalpx/services/strategy.py",
            [r"consumer_view", r"branch_frames", r"candidate", r"activation", r"safe_to_consume", r"HOLD", r"ENTRY"],
        ),
    }

    strategy_once = run_strategy_once_if_available(strategy, redis_client)
    result["strategy_once"] = strategy_once

    orders_after = int(redis_client.xlen(orders_key))
    decisions_after = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0
    latest_decisions = stream_latest(redis_client, decisions_key, count=3)
    rt_after = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_after = str(rt_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    result["latest_decisions"] = latest_decisions

    safety = {
        "orders_before": orders_before,
        "orders_after": orders_after,
        "orders_zero": orders_after == 0,
        "orders_delta": orders_after - orders_before,
        "decisions_before": decisions_before,
        "decisions_after": decisions_after,
        "decisions_delta": decisions_after - decisions_before,
        "real_live_before": real_live_before,
        "real_live_after": real_live_after,
        "risk_process_lines": pgrep_service("risk"),
        "execution_process_lines": pgrep_service("execution"),
        "strategy_process_lines": pgrep_service("strategy"),
        "feeds_process_lines": pgrep_service("feeds"),
    }
    result["safety"] = safety

    # O17's purpose is not to require a candidate; it requires proving the activation
    # view can be consumed and candidate extraction can honestly proceed or fail by doctrine.
    required = {
        "redis_available": True,
        "o16h_r2_pass_gate": result["o16h_r2_gate"]["final_verdict"] == "PASS_O16H_R2_RUNTIME_DATA_VALID_SAFE_TO_CONSUME_OK",
        "compile_pass": compile_result["returncode"] == 0,
        "feature_payload_frame_valid": feature_payload_summary["frame_valid"] is True,
        "consumer_view_present": consumer_view_summary["present"] is True,
        "consumer_view_data_valid": consumer_view_summary["data_valid"] is True,
        "consumer_view_safe_to_consume": consumer_view_summary["safe_to_consume"] is True,
        "all_10_branch_frames_present": consumer_view_summary["branch_frame_count"] == 10,
        "mist_call_branch_frame_present": consumer_view_summary["mist_call_present"] is True,
        "activation_view_accessible": scan_summary["activation_view_accessible"] is True,
        "candidate_extraction_possible": scan_summary["candidate_extraction_possible"] is True,
        "orders_zero": orders_after == 0,
        "orders_delta_zero": orders_after == orders_before,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "no_forced_candidate": True,
        "no_threshold_relaxation": True,
    }
    result["required_verdicts"] = required

    if not all([
        required["o16h_r2_pass_gate"],
        required["compile_pass"],
        required["feature_payload_frame_valid"],
        required["consumer_view_present"],
        required["consumer_view_data_valid"],
        required["consumer_view_safe_to_consume"],
        required["all_10_branch_frames_present"],
        required["mist_call_branch_frame_present"],
        required["activation_view_accessible"],
        required["candidate_extraction_possible"],
        required["orders_zero"],
        required["orders_delta_zero"],
        required["risk_not_running"],
        required["execution_not_running"],
        required["real_live_false"],
    ]):
        result["final_verdict"] = "FAIL_O17_ACTIVATION_CANDIDATE_EXTRACTION_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to paper."
        write_outputs(result)
        return 2

    if strategy_once.get("attempted") and strategy_once.get("error"):
        result["final_verdict"] = "PASS_O17_VIEW_CONSUMABLE_STRATEGY_ONESHOT_ERROR_REVIEW_NEEDED"
        result["next_recommended_batch"] = "26-O17A strategy one-shot interface repair/audit, no risk/execution"
        write_outputs(result)
        return 0

    result["final_verdict"] = "PASS_O17_ACTIVATION_VIEW_CANDIDATE_EXTRACTION_READY_NO_ORDER"
    result["next_recommended_batch"] = "26-O18 lightweight controlled-paper preflight, MIST CALL only, 1 lot, no heavy monitor"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
