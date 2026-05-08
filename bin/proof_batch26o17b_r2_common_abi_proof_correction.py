#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O17B-R2"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o17b_r2_common_abi_proof_correction.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o17b_r2_common_abi_proof_correction.json"
O17B_PATH = ROOT / "run/proofs/proof_batch26o17b_common_parent_abi_sanitizer.json"

EXPECTED_COMMON_KEYS = (
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals",
)

EXPECTED_SELECTED_OPTION_KEYS = (
    "side",
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "ofi_ratio_proxy",
    "microprice",
    "micro_edge",
    "delta_3",
    "response_efficiency",
    "tradability_ok",
)

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
    "bin/proof_batch26o17b_r2_common_abi_proof_correction.py",
    "run/proofs/proof_batch26o17b_common_parent_abi_sanitizer.json",
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
    self_name = "proof_batch26o17b_r2_common_abi_proof_correction.py"
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


def hget_json(redis_client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        return safe_json_load(redis_client.hget(key, field))
    except Exception:
        return {}


def run_feature_once(features_mod: Any, redis_client: Any) -> Mapping[str, Any]:
    svc = features_mod.FeatureService(
        redis_client=build_redis_adapter(redis_client),
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o17b-r2-feature",
    )
    payload = svc.run_once()
    return payload if isinstance(payload, Mapping) else {}


def run_strategy_once(strategy_mod: Any, redis_client: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "attempted": False,
        "result": None,
        "error": None,
        "method": None,
        "constructor_signature": None,
    }
    svc_cls = getattr(strategy_mod, "StrategyService", None) or getattr(strategy_mod, "Service", None)
    if svc_cls is None:
        out["error"] = "No StrategyService/Service class found"
        return out

    try:
        out["constructor_signature"] = str(inspect.signature(svc_cls))
    except Exception:
        out["constructor_signature"] = "UNAVAILABLE"

    try:
        svc = svc_cls(
            redis_client=build_redis_adapter(redis_client),
            clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
            shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
            instance_id="batch26o17b-r2-strategy",
        )
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    method = getattr(svc, "run_once", None)
    if not callable(method):
        out["error"] = "StrategyService.run_once not callable"
        return out

    out["attempted"] = True
    out["method"] = "run_once"
    try:
        res = method()
        out["result"] = res if isinstance(res, (dict, list, str, int, float, bool, type(None))) else repr(res)
        return out
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out


def latest_stream_rows(redis_client: Any, key: str, count: int = 5) -> list[dict[str, Any]]:
    rows_out: list[dict[str, Any]] = []
    try:
        rows = redis_client.xrevrange(key, count=count)
        for msg_id, fields in rows:
            rows_out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
    except Exception:
        pass
    return rows_out


def contract_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    ff = payload.get("family_features", {})
    if not isinstance(ff, Mapping):
        ff = {}
    common = ff.get("common", {})
    if not isinstance(common, Mapping):
        common = {}
    selected = common.get("selected_option", {})
    if not isinstance(selected, Mapping):
        selected = {}
    return {
        "frame_valid": bool(payload.get("frame_valid")),
        "common_keys": tuple(common.keys()),
        "common_key_match": tuple(common.keys()) == EXPECTED_COMMON_KEYS,
        "selected_option_keys": tuple(selected.keys()),
        "selected_option_key_match": tuple(selected.keys()) == EXPECTED_SELECTED_OPTION_KEYS,
        "selected_option_rich_in_common": "selected_option_rich" in common,
        "stage_flags": dict(ff.get("stage_flags", {}) or {}) if isinstance(ff.get("stage_flags", {}), Mapping) else {},
    }


def decision_safety(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe = []
    hold_like = []
    for row in rows:
        f = row.get("fields", {})
        action = str(f.get("action") or f.get("decision") or f.get("side") or "").upper()
        qty = str(f.get("qty") or "0")
        hold_only = str(f.get("hold_only") or "").lower() in {"1", "true", "yes"}
        order_type = str(f.get("order_type") or "")
        broker_side_effects_allowed = str(f.get("broker_side_effects_allowed") or "").lower() in {"1", "true", "yes"}
        live_orders_allowed = str(f.get("live_orders_allowed") or "").lower() in {"1", "true", "yes"}

        is_hold = bool(
            action in {"", "HOLD", "FLAT"}
            and qty in {"", "0", "0.0"}
            and order_type == ""
            and not broker_side_effects_allowed
            and not live_orders_allowed
        )
        if is_hold or hold_only:
            hold_like.append(row)
        else:
            unsafe.append(row)

    return {
        "row_count": len(rows),
        "hold_like_count": len(hold_like),
        "unsafe_count": len(unsafe),
        "unsafe_rows": unsafe,
        "latest_rows": rows,
    }


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
        "batch_name": "common_abi_proof_correction",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "audit_proof_only": True,
            "patch_performed": False,
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

    o17b = safe_json_load(O17B_PATH.read_text(encoding="utf-8")) if O17B_PATH.exists() else {}
    result["o17b_gate"] = {
        "exists": O17B_PATH.exists(),
        "final_verdict": o17b.get("final_verdict") if isinstance(o17b, Mapping) else None,
        "required_verdicts": o17b.get("required_verdicts") if isinstance(o17b, Mapping) else None,
        "post_check_parsed": o17b.get("post_check_parsed") if isinstance(o17b, Mapping) else None,
        "safety": o17b.get("safety") if isinstance(o17b, Mapping) else None,
    }

    allowed_o17b_gate = bool(
        o17b.get("final_verdict") == "FAIL_O17B_COMMON_PARENT_ABI_SANITIZER_NOT_PROVEN"
        and isinstance(o17b.get("required_verdicts"), Mapping)
        and o17b["required_verdicts"].get("common_key_match") is True
        and o17b["required_verdicts"].get("selected_option_key_match") is True
        and o17b["required_verdicts"].get("strategy_oneshot_no_feature_contract_error") is True
        and o17b["required_verdicts"].get("orders_zero") is True
        and o17b["required_verdicts"].get("risk_not_running") is True
        and o17b["required_verdicts"].get("execution_not_running") is True
        and o17b["required_verdicts"].get("real_live_false") is True
    )
    result["allowed_o17b_gate"] = allowed_o17b_gate

    if not allowed_o17b_gate:
        result["final_verdict"] = "FAIL_CLOSED_O17B_NOT_EXPECTED_PROOF_LOGIC_FAILURE"
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
    decisions_key = getattr(names, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    runtime_key = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")
    features_key = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))

    orders_before = int(redis_client.xlen(orders_key))
    decisions_before = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0
    rt_before = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_before = str(rt_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    feature_payload = run_feature_once(features, redis_client)
    contract = contract_summary(feature_payload)

    cv = hget_json(redis_client, features_key, "consumer_view_json")
    rich = hget_json(redis_client, features_key, "selected_option_rich_json")
    abi = hget_json(redis_client, features_key, "o17b_common_abi_json")

    strategy_once = run_strategy_once(strategy, redis_client)

    orders_after = int(redis_client.xlen(orders_key))
    decisions_after = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0
    decisions_delta = decisions_after - decisions_before
    latest_decisions = latest_stream_rows(redis_client, decisions_key, count=max(5, min(10, decisions_delta + 3)))
    dec_safety = decision_safety(latest_decisions)

    rt_after = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_after = str(rt_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    safety = {
        "orders_before": orders_before,
        "orders_after": orders_after,
        "orders_delta": orders_after - orders_before,
        "orders_zero": orders_after == 0,
        "decisions_before": decisions_before,
        "decisions_after": decisions_after,
        "decisions_delta": decisions_delta,
        "real_live_before": real_live_before,
        "real_live_after": real_live_after,
        "risk_process_lines": pgrep_service("risk"),
        "execution_process_lines": pgrep_service("execution"),
        "strategy_process_lines": pgrep_service("strategy"),
        "feeds_process_lines": pgrep_service("feeds"),
        "decision_safety": dec_safety,
    }

    result["feature_contract"] = contract
    result["consumer_view_summary"] = {
        "present": bool(cv),
        "data_valid": cv.get("data_valid") if isinstance(cv, Mapping) else None,
        "safe_to_consume": cv.get("safe_to_consume") if isinstance(cv, Mapping) else None,
        "branch_frame_count": len(cv.get("branch_frames", {}) or {}) if isinstance(cv, Mapping) else 0,
        "mist_call_present": "mist_call" in (cv.get("branch_frames", {}) or {}) if isinstance(cv, Mapping) else False,
    }
    result["rich_preservation"] = {
        "selected_option_rich_json_present": bool(rich),
        "selected_option_rich_key_count": len(rich) if isinstance(rich, Mapping) else 0,
        "o17b_common_abi_present": bool(abi),
        "o17b_common_abi": abi,
    }
    result["strategy_once"] = strategy_once
    result["safety"] = safety

    strategy_error = str(strategy_once.get("error") or "")

    required = {
        "redis_available": True,
        "allowed_o17b_gate": allowed_o17b_gate,
        "compile_pass": compile_result["returncode"] == 0,
        "feature_frame_valid": contract["frame_valid"] is True,
        "common_key_match": contract["common_key_match"] is True,
        "selected_option_key_match": contract["selected_option_key_match"] is True,
        "selected_option_rich_not_in_common": contract["selected_option_rich_in_common"] is False,
        "selected_option_rich_preserved_outside_common": bool(rich),
        "consumer_view_present": result["consumer_view_summary"]["present"] is True,
        "consumer_view_data_valid": result["consumer_view_summary"]["data_valid"] is True,
        "consumer_view_safe_to_consume": result["consumer_view_summary"]["safe_to_consume"] is True,
        "all_10_branch_frames_present": result["consumer_view_summary"]["branch_frame_count"] == 10,
        "mist_call_present": result["consumer_view_summary"]["mist_call_present"] is True,
        "strategy_oneshot_attempted": strategy_once.get("attempted") is True,
        "strategy_oneshot_no_feature_contract_error": "FeatureFamilyContractError" not in strategy_error,
        "strategy_oneshot_no_exception": strategy_once.get("error") is None,
        "orders_zero": orders_after == 0,
        "orders_delta_zero": orders_after == orders_before,
        "decisions_delta_allowed": decisions_delta >= 0,
        "decisions_hold_only": dec_safety["unsafe_count"] == 0,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "no_forced_candidate": True,
        "no_threshold_relaxation": True,
        "patch_not_required": True,
    }
    result["required_verdicts"] = required

    if not all([
        required["compile_pass"],
        required["feature_frame_valid"],
        required["common_key_match"],
        required["selected_option_key_match"],
        required["selected_option_rich_not_in_common"],
        required["selected_option_rich_preserved_outside_common"],
        required["consumer_view_present"],
        required["consumer_view_data_valid"],
        required["consumer_view_safe_to_consume"],
        required["all_10_branch_frames_present"],
        required["mist_call_present"],
        required["strategy_oneshot_attempted"],
        required["strategy_oneshot_no_feature_contract_error"],
        required["strategy_oneshot_no_exception"],
        required["orders_zero"],
        required["orders_delta_zero"],
        required["decisions_hold_only"],
        required["risk_not_running"],
        required["execution_not_running"],
        required["real_live_false"],
    ]):
        result["final_verdict"] = "FAIL_O17B_R2_COMMON_ABI_PROOF_CORRECTION_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to paper."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O17B_R2_STRATEGY_ONESHOT_CONTRACT_OK_HOLD_ONLY_NO_ORDER"
    result["next_recommended_batch"] = "26-O18 lightweight controlled-paper preflight, MIST CALL only, 1 lot, no heavy monitor"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
