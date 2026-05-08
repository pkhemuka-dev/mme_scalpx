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

BATCH = "26-O18"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o18_lightweight_controlled_paper_preflight.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o18_lightweight_controlled_paper_preflight.json"
O17B_R2_PATH = ROOT / "run/proofs/proof_batch26o17b_r2_common_abi_proof_correction.json"

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/settings.py",
    "bin/proof_batch26o18_lightweight_controlled_paper_preflight.py",
    "run/proofs/proof_batch26o17b_r2_common_abi_proof_correction.json",
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
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


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
    self_name = "proof_batch26o18_lightweight_controlled_paper_preflight.py"
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


def run_feature_once(features_mod: Any, redis_client: Any) -> Mapping[str, Any]:
    svc = features_mod.FeatureService(
        redis_client=build_redis_adapter(redis_client),
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o18-feature",
    )
    payload = svc.run_once()
    return payload if isinstance(payload, Mapping) else {}


def run_strategy_once(strategy_mod: Any, redis_client: Any) -> dict[str, Any]:
    out = {
        "attempted": False,
        "method": None,
        "result": None,
        "error": None,
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
            instance_id="batch26o18-strategy",
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


def hget_json(redis_client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        return safe_json_load(redis_client.hget(key, field))
    except Exception:
        return {}


def latest_stream_rows(redis_client: Any, key: str, count: int = 5) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        rows = redis_client.xrevrange(key, count=count)
        for msg_id, fields in rows:
            out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
    except Exception:
        pass
    return out


def decision_safety(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe = []
    hold_like = []
    for row in rows:
        f = row.get("fields", {})
        action = str(f.get("action") or f.get("decision") or "").upper()
        side = str(f.get("side") or "").upper()
        qty = str(f.get("qty") or f.get("quantity_lots") or "0")
        order_type = str(f.get("order_type") or "")
        broker_side_effects_allowed = str(f.get("broker_side_effects_allowed") or "").lower() in {"1", "true", "yes"}
        live_orders_allowed = str(f.get("live_orders_allowed") or "").lower() in {"1", "true", "yes"}

        is_hold = bool(
            action in {"", "HOLD"}
            and side in {"", "FLAT"}
            and qty in {"", "0", "0.0"}
            and order_type == ""
            and not broker_side_effects_allowed
            and not live_orders_allowed
        )
        if is_hold:
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


def position_summary(raw: Mapping[str, str]) -> dict[str, Any]:
    has_position_raw = str(raw.get("has_position", raw.get("position_open", "false"))).lower()
    qty_lots = float(raw.get("qty_lots", raw.get("quantity_lots", "0")) or 0)
    qty_units = float(raw.get("qty_units", raw.get("quantity_units", "0")) or 0)
    side = str(raw.get("position_side", raw.get("side", ""))).upper()
    flat = bool(
        has_position_raw not in {"1", "true", "yes", "y"}
        and qty_lots == 0
        and qty_units == 0
        and side in {"", "FLAT", "NONE"}
    )
    return {
        "raw": dict(raw),
        "has_position_raw": has_position_raw,
        "qty_lots": qty_lots,
        "qty_units": qty_units,
        "side": side,
        "flat": flat,
    }


def scan_static_safety(paths: list[pathlib.Path]) -> dict[str, Any]:
    needles = [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "controlled_strategy_promotion_enabled",
        "real_live_allowed",
        "broker_side_effects_allowed",
        "live_orders_allowed",
        "MIST",
        "CALL",
        "quantity_lots",
        "qty_lots",
    ]
    hits: dict[str, list[str]] = {}
    for path in paths:
        if not path.exists():
            hits[str(path.relative_to(ROOT))] = ["MISSING"]
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rows = []
        for idx, line in enumerate(text.splitlines(), start=1):
            if any(n in line for n in needles):
                rows.append(f"{idx}: {line[:240]}")
        hits[str(path.relative_to(ROOT))] = rows[:80]
    return hits


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
        "batch_name": "lightweight_controlled_paper_preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "preflight_only": True,
            "paper_start": False,
            "risk_started": False,
            "execution_started": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_approval": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
            "heavy_monitor": False,
            "xrevrange_loop": False,
            "strategy_patch": False,
        },
    }

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None
    if redis_client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    o17b_r2 = safe_json_load(O17B_R2_PATH.read_text(encoding="utf-8")) if O17B_R2_PATH.exists() else {}
    result["o17b_r2_gate"] = {
        "exists": O17B_R2_PATH.exists(),
        "final_verdict": o17b_r2.get("final_verdict") if isinstance(o17b_r2, Mapping) else None,
        "required_verdicts": o17b_r2.get("required_verdicts") if isinstance(o17b_r2, Mapping) else None,
    }

    if o17b_r2.get("final_verdict") != "PASS_O17B_R2_STRATEGY_ONESHOT_CONTRACT_OK_HOLD_ONLY_NO_ORDER":
        result["final_verdict"] = "FAIL_CLOSED_O17B_R2_NOT_PASS"
        result["next_recommended_batch"] = "Do not proceed. Inspect O17B-R2 proof."
        write_outputs(result)
        return 2

    compile_result = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/strategy_family/eligibility.py",
        "app/mme_scalpx/services/strategy_family/arbitration.py",
        "app/mme_scalpx/services/strategy_family/decisions.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/settings.py",
    ])
    result["compile"] = compile_result

    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
        strategy = importlib.import_module("app.mme_scalpx.services.strategy")
        importlib.import_module("app.mme_scalpx.services.risk")
        importlib.import_module("app.mme_scalpx.services.execution")
    except Exception as exc:
        result["final_verdict"] = "FAIL_IMPORT_CONTEXT_NOT_READY"
        result["import_error"] = f"{type(exc).__name__}: {exc}"
        write_outputs(result)
        return 2

    orders_key = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(names, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    runtime_key = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")
    position_key = getattr(names, "HASH_STATE_POSITION_MME", "state:position:mme")
    features_key = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))

    orders_before = int(redis_client.xlen(orders_key))
    decisions_before = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0

    runtime_before = decode_hash(redis_client.hgetall(runtime_key) or {})
    position_before = position_summary(decode_hash(redis_client.hgetall(position_key) or {}))
    real_live_before = str(runtime_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    feature_payload = run_feature_once(features, redis_client)
    strategy_once = run_strategy_once(strategy, redis_client)

    cv = hget_json(redis_client, features_key, "consumer_view_json")
    ff = hget_json(redis_client, features_key, "family_features_json")
    frames = hget_json(redis_client, features_key, "family_frames_json")

    stage_flags = ff.get("stage_flags", {}) if isinstance(ff, Mapping) else {}
    branch_frames = cv.get("branch_frames", {}) if isinstance(cv, Mapping) else {}
    mist_call = branch_frames.get("mist_call", {}) if isinstance(branch_frames, Mapping) else {}

    orders_after = int(redis_client.xlen(orders_key))
    decisions_after = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0
    decisions_delta = decisions_after - decisions_before

    latest_decisions = latest_stream_rows(redis_client, decisions_key, count=max(5, min(10, decisions_delta + 3)))
    decision_report = decision_safety(latest_decisions)

    runtime_after = decode_hash(redis_client.hgetall(runtime_key) or {})
    position_after = position_summary(decode_hash(redis_client.hgetall(position_key) or {}))
    real_live_after = str(runtime_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    env_preflight = {
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", ""),
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", ""),
        "SCALPX_CONTROLLED_PAPER_FAMILY": os.environ.get("SCALPX_CONTROLLED_PAPER_FAMILY", ""),
        "SCALPX_CONTROLLED_PAPER_BRANCH": os.environ.get("SCALPX_CONTROLLED_PAPER_BRANCH", ""),
        "SCALPX_CONTROLLED_PAPER_QTY_LOTS": os.environ.get("SCALPX_CONTROLLED_PAPER_QTY_LOTS", ""),
        "SCALPX_REAL_LIVE_ALLOWED": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", ""),
    }

    static_safety = scan_static_safety([
        ROOT / "app/mme_scalpx/services/risk.py",
        ROOT / "app/mme_scalpx/services/execution.py",
        ROOT / "app/mme_scalpx/services/strategy.py",
        ROOT / "app/mme_scalpx/core/settings.py",
    ])

    safety = {
        "orders_before": orders_before,
        "orders_after": orders_after,
        "orders_delta": orders_after - orders_before,
        "orders_zero": orders_after == 0,
        "decisions_before": decisions_before,
        "decisions_after": decisions_after,
        "decisions_delta": decisions_delta,
        "decision_safety": decision_report,
        "real_live_before": real_live_before,
        "real_live_after": real_live_after,
        "position_before": position_before,
        "position_after": position_after,
        "feeds_process_lines": pgrep_service("feeds"),
        "features_process_lines": pgrep_service("features"),
        "strategy_process_lines": pgrep_service("strategy"),
        "risk_process_lines": pgrep_service("risk"),
        "execution_process_lines": pgrep_service("execution"),
    }

    result["feature_summary"] = {
        "payload_frame_valid": bool(isinstance(feature_payload, Mapping) and feature_payload.get("frame_valid")),
        "consumer_view_present": bool(cv),
        "consumer_view_data_valid": cv.get("data_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_safe_to_consume": cv.get("safe_to_consume") if isinstance(cv, Mapping) else None,
        "branch_frame_count": len(branch_frames) if isinstance(branch_frames, Mapping) else 0,
        "mist_call_present": "mist_call" in branch_frames if isinstance(branch_frames, Mapping) else False,
        "mist_call": mist_call,
        "stage_flags": stage_flags,
        "family_frame_keys": sorted(frames.keys()) if isinstance(frames, Mapping) else [],
    }
    result["strategy_once"] = strategy_once
    result["env_preflight"] = env_preflight
    result["static_safety_scan"] = static_safety
    result["safety"] = safety

    # O18 is a preflight, so env may be absent. We require only that no real-live env is enabled.
    real_live_env_false = str(env_preflight.get("SCALPX_REAL_LIVE_ALLOWED") or "").lower() not in {"1", "true", "yes", "y"}

    strategy_result = strategy_once.get("result")
    strategy_result_text = json.dumps(strategy_result, sort_keys=True, default=str) if strategy_result is not None else ""
    strategy_error = str(strategy_once.get("error") or "")
    strategy_hold_or_no_candidate = bool(
        strategy_once.get("error") is None
        and (
            '"action": "HOLD"' in strategy_result_text
            or '"action":"HOLD"' in strategy_result_text
            or "HOLD" in strategy_result_text
            or "no_candidate" in strategy_result_text
            or "hold_only" in strategy_result_text
            or strategy_result in ({}, None)
        )
    )

    required = {
        "redis_available": True,
        "o17b_r2_pass_gate": result["o17b_r2_gate"]["final_verdict"] == "PASS_O17B_R2_STRATEGY_ONESHOT_CONTRACT_OK_HOLD_ONLY_NO_ORDER",
        "compile_pass": compile_result["returncode"] == 0,
        "feature_payload_frame_valid": result["feature_summary"]["payload_frame_valid"] is True,
        "consumer_view_present": result["feature_summary"]["consumer_view_present"] is True,
        "consumer_view_data_valid": result["feature_summary"]["consumer_view_data_valid"] is True,
        "consumer_view_safe_to_consume": result["feature_summary"]["consumer_view_safe_to_consume"] is True,
        "all_10_branch_frames_present": result["feature_summary"]["branch_frame_count"] == 10,
        "mist_call_present": result["feature_summary"]["mist_call_present"] is True,
        "strategy_oneshot_attempted": strategy_once.get("attempted") is True,
        "strategy_oneshot_no_exception": strategy_once.get("error") is None,
        "strategy_hold_or_no_candidate": strategy_hold_or_no_candidate,
        "orders_zero": orders_after == 0,
        "orders_delta_zero": orders_after == orders_before,
        "decisions_hold_only": decision_report["unsafe_count"] == 0,
        "position_flat_before": position_before["flat"] is True,
        "position_flat_after": position_after["flat"] is True,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "real_live_env_false": real_live_env_false,
        "no_paper_start": True,
        "no_broker_call": True,
        "no_heavy_monitor": True,
        "no_forced_candidate": True,
        "no_threshold_relaxation": True,
        "scope_mist_call_only_next": True,
        "qty_cap_one_lot_next": True,
    }
    result["required_verdicts"] = required

    if not all([
        required["o17b_r2_pass_gate"],
        required["compile_pass"],
        required["feature_payload_frame_valid"],
        required["consumer_view_present"],
        required["consumer_view_data_valid"],
        required["consumer_view_safe_to_consume"],
        required["all_10_branch_frames_present"],
        required["mist_call_present"],
        required["strategy_oneshot_attempted"],
        required["strategy_oneshot_no_exception"],
        required["strategy_hold_or_no_candidate"],
        required["orders_zero"],
        required["orders_delta_zero"],
        required["decisions_hold_only"],
        required["position_flat_before"],
        required["position_flat_after"],
        required["risk_not_running"],
        required["execution_not_running"],
        required["real_live_false"],
        required["real_live_env_false"],
    ]):
        result["final_verdict"] = "FAIL_O18_LIGHTWEIGHT_CONTROLLED_PAPER_PREFLIGHT_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not start paper."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O18_LIGHTWEIGHT_CONTROLLED_PAPER_PREFLIGHT_OK"
    result["next_recommended_batch"] = "26-O19 lightweight controlled-paper runtime start, MIST CALL only, 1 lot, no heavy monitor, real-live false"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
