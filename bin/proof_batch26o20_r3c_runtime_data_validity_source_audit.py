#!/usr/bin/env python3
from __future__ import annotations

import hashlib
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

BATCH = "26-O20-R3C"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o20_r3c_runtime_data_validity_source_audit.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o20_r3c_runtime_data_validity_source_audit.json"
O20R3B_PATH = ROOT / "run/proofs/proof_batch26o20_r3b_corrected_bounded_observation.json"

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o20_r3c_runtime_data_validity_source_audit.py",
    "run/proofs/proof_batch26o20_r3b_corrected_bounded_observation.json",
    "run/proofs/proof_batch26o20_r3a_persistent_features_abi_publish_repair.json",
]

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


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists() or path.is_dir():
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


def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    obj = safe_json_load(path.read_text(encoding="utf-8", errors="replace"))
    return obj if isinstance(obj, dict) else {}


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


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


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o20_r3c_runtime_data_validity_source_audit.py"
    for clean in ps_lines():
        lower = clean.lower()
        if self_name in clean:
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


def xlen(client: Any, key: str) -> int:
    try:
        return int(client.xlen(key))
    except Exception:
        return 0


def hgetall(client: Any, key: str) -> dict[str, str]:
    try:
        return decode_hash(client.hgetall(key) or {})
    except Exception:
        return {}


def hget_json(client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        obj = safe_json_load(client.hget(key, field))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def latest_rows(client: Any, key: str, count: int = 8) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        rows = client.xrevrange(key, count=count)
        for msg_id, fields in rows:
            out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
    except Exception:
        pass
    return out


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
    return {"raw": dict(raw), "has_position_raw": has_position_raw, "qty_lots": qty_lots, "qty_units": qty_units, "side": side, "flat": flat}


def flatten(obj: Any, prefix: str = "", max_depth: int = 5) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if max_depth < 0:
        return out
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, Mapping):
                out.update(flatten(v, key, max_depth - 1))
            elif isinstance(v, list):
                out[key] = f"list[{len(v)}]"
            else:
                out[key] = v
    return out


def feature_snapshot(client: Any, features_hash_key: str) -> dict[str, Any]:
    raw = hgetall(client, features_hash_key)
    ff = hget_json(client, features_hash_key, "family_features_json")
    cv = hget_json(client, features_hash_key, "consumer_view_json")
    frames = hget_json(client, features_hash_key, "family_frames_json")
    payload = hget_json(client, features_hash_key, "payload_json")
    abi_guard = hget_json(client, features_hash_key, "o20r3a_abi_guard_json")
    rich = hget_json(client, features_hash_key, "selected_option_rich_json")

    common = ff.get("common", {}) if isinstance(ff, Mapping) else {}
    selected = common.get("selected_option", {}) if isinstance(common, Mapping) else {}
    stage_flags = ff.get("stage_flags", {}) if isinstance(ff, Mapping) else {}
    branch_frames = cv.get("branch_frames", {}) if isinstance(cv, Mapping) else {}
    mist_call = branch_frames.get("mist_call", {}) if isinstance(branch_frames, Mapping) else {}

    flat_cv = flatten(cv)
    falseish = {}
    for k, v in flat_cv.items():
        if v in (False, None, "", 0, "0", "false", "False", "UNAVAILABLE", "STALE", "MISSING"):
            falseish[k] = v

    possible_reasons = {}
    for source_name, source in {
        "family_features": ff,
        "consumer_view": cv,
        "mist_call": mist_call,
        "stage_flags": stage_flags,
        "payload": payload,
    }.items():
        flat = flatten(source)
        for k, v in flat.items():
            lk = k.lower()
            if any(token in lk for token in ["reason", "block", "fail", "invalid", "stale", "missing", "ready", "valid", "fresh", "safe"]):
                possible_reasons[f"{source_name}.{k}"] = v

    return {
        "raw_hash_keys": sorted(raw.keys()),
        "raw_hash_brief": {k: raw.get(k) for k in sorted(raw.keys()) if k.endswith("_ok") or k.endswith("_valid") or "valid" in k or "ready" in k or "stale" in k or "fresh" in k},
        "family_features_present": bool(ff),
        "payload_present": bool(payload),
        "consumer_view_present": bool(cv),
        "consumer_view_data_valid": cv.get("data_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_safe_to_consume": cv.get("safe_to_consume") if isinstance(cv, Mapping) else None,
        "consumer_view_hold_only": cv.get("hold_only") if isinstance(cv, Mapping) else None,
        "branch_frame_count": len(branch_frames) if isinstance(branch_frames, Mapping) else 0,
        "mist_call_present": "mist_call" in branch_frames if isinstance(branch_frames, Mapping) else False,
        "family_frame_keys": sorted(frames.keys()) if isinstance(frames, Mapping) else [],
        "common_keys": list(common.keys()) if isinstance(common, Mapping) else [],
        "common_key_match": tuple(common.keys()) == EXPECTED_COMMON_KEYS if isinstance(common, Mapping) else False,
        "selected_option_keys": list(selected.keys()) if isinstance(selected, Mapping) else [],
        "selected_option_key_match": tuple(selected.keys()) == EXPECTED_SELECTED_OPTION_KEYS if isinstance(selected, Mapping) else False,
        "selected_option_rich_in_common": "selected_option_rich" in common if isinstance(common, Mapping) else False,
        "selected_option_rich_json_present": bool(rich),
        "o20r3a_guard_present": bool(abi_guard),
        "stage_flags": stage_flags,
        "mist_call_brief": {
            "eligible": mist_call.get("eligible") if isinstance(mist_call, Mapping) else None,
            "tradability_ok": mist_call.get("tradability_ok") if isinstance(mist_call, Mapping) else None,
            "option_symbol": mist_call.get("option_symbol") if isinstance(mist_call, Mapping) else None,
            "failed_stage": mist_call.get("failed_stage") if isinstance(mist_call, Mapping) else None,
            "blockers": mist_call.get("blockers") if isinstance(mist_call, Mapping) else None,
        },
        "consumer_view_falseish_fields": falseish,
        "possible_reasons": possible_reasons,
    }


def run_feature_once(client: Any) -> dict[str, Any]:
    try:
        from app.mme_scalpx.services import features as F  # type: ignore

        class R:
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

        svc = F.FeatureService(
            redis_client=R(client),
            clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
            shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
            instance_id="batch26o20-r3c-feature-audit",
        )
        payload = svc.run_once()
        return {
            "ok": True,
            "error": None,
            "payload_type": type(payload).__name__,
            "payload_frame_valid": bool(isinstance(payload, Mapping) and payload.get("frame_valid")),
            "payload_keys": sorted(payload.keys()) if isinstance(payload, Mapping) else [],
            "payload_summary": {
                "frame_valid": payload.get("frame_valid") if isinstance(payload, Mapping) else None,
                "data_valid": payload.get("data_valid") if isinstance(payload, Mapping) else None,
                "safe_to_consume": payload.get("safe_to_consume") if isinstance(payload, Mapping) else None,
                "reason": payload.get("reason") if isinstance(payload, Mapping) else None,
                "blockers": payload.get("blockers") if isinstance(payload, Mapping) else None,
            } if isinstance(payload, Mapping) else {},
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "payload_frame_valid": False}


def classify(snapshot: Mapping[str, Any], runtime: Mapping[str, str], process_report: Mapping[str, list[str]]) -> dict[str, Any]:
    reasons = snapshot.get("possible_reasons", {}) if isinstance(snapshot.get("possible_reasons"), Mapping) else {}
    stage_flags = snapshot.get("stage_flags", {}) if isinstance(snapshot.get("stage_flags"), Mapping) else {}
    mist = snapshot.get("mist_call_brief", {}) if isinstance(snapshot.get("mist_call_brief"), Mapping) else {}

    false_stage_flags = sorted([k for k, v in stage_flags.items() if v is not True])
    falseish = snapshot.get("consumer_view_falseish_fields", {}) if isinstance(snapshot.get("consumer_view_falseish_fields"), Mapping) else {}

    runtime_flags = {k: v for k, v in runtime.items() if any(t in k.lower() for t in ["provider", "feed", "context", "selected", "dhan", "zerodha", "status", "failover", "seen", "ticks"])}
    feeds_running = len(process_report.get("feeds", [])) > 0

    likely = []
    if snapshot.get("common_key_match") is True and snapshot.get("selected_option_key_match") is True and snapshot.get("selected_option_rich_in_common") is False:
        likely.append("ABI_OK")
    if snapshot.get("consumer_view_data_valid") is False or snapshot.get("consumer_view_safe_to_consume") is False:
        likely.append("DATA_VALID_FALSE")
    if false_stage_flags:
        likely.append("STAGE_FLAGS_FALSE")
    if mist.get("tradability_ok") is False:
        likely.append("MIST_CALL_TRADABILITY_FALSE")
    if mist.get("option_symbol") in (None, ""):
        likely.append("SELECTED_OPTION_SYMBOL_MISSING_IN_MIST_CALL")
    if str(runtime.get("feeds_latest_context_status", "")).upper() in {"UNAVAILABLE", "STALE", "MISSING", ""}:
        likely.append("DHAN_CONTEXT_UNAVAILABLE_OR_STALE")
    if str(runtime.get("feeds_seen_tokens_dhan", "0")) in {"0", "", "0.0"}:
        likely.append("DHAN_SELECTED_OPTION_TICKS_NOT_SEEN")
    if not feeds_running:
        likely.append("FEEDS_NOT_RUNNING")
    else:
        likely.append("FEEDS_RUNNING")

    if "ABI_OK" in likely and "DATA_VALID_FALSE" in likely:
        classification = "ABI_REPAIRED_DATA_VALIDITY_BLOCKED_BY_RUNTIME_MARKETDATA_OR_TRADABILITY"
    else:
        classification = "DATA_VALIDITY_CAUSE_NOT_FULLY_CLASSIFIED"

    return {
        "classification": classification,
        "likely_tags": likely,
        "false_stage_flags": false_stage_flags,
        "mist_call_brief": mist,
        "consumer_view_falseish_fields": falseish,
        "possible_reasons": reasons,
        "runtime_flags": runtime_flags,
        "feeds_running": feeds_running,
        "recommended_next": "26-O20-R3D data-validity gate repair only if audit proves stale/unavailable data should be classified as safe HOLD instead of invalid; otherwise wait for fresh live market data",
    }


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
        "created_at_utc": now_utc(),
        "files": [{"path": p, "exists": (ROOT / p).exists(), "sha256": sha256_file(ROOT / p)} for p in TARGETS],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> int:
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "runtime_data_validity_source_audit",
        "created_at_utc": now_utc(),
        "scope": {
            "audit_only": True,
            "patch_performed": False,
            "paper_start": False,
            "strategy_start": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_enablement": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
        },
    }

    o20r3b = load_json(O20R3B_PATH)
    result["o20r3b_gate"] = {
        "exists": bool(o20r3b),
        "final_verdict": o20r3b.get("final_verdict"),
        "next_recommended_batch": o20r3b.get("next_recommended_batch"),
        "pre_runtime_hygiene": o20r3b.get("pre_runtime_hygiene"),
    }

    if o20r3b.get("final_verdict") != "FAIL_CLOSED_PRE_RUNTIME_ABI_HASH_HYGIENE_NOT_PROVEN":
        result["final_verdict"] = "FAIL_CLOSED_O20R3B_NOT_EXPECTED_DATA_VALIDITY_FAILURE"
        result["next_recommended_batch"] = "Do not continue. Inspect O20-R3B proof."
        write_outputs(result)
        return 2

    compile_result = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/feature_family/contracts.py",
        "app/mme_scalpx/services/feature_family/tradability.py",
        "app/mme_scalpx/services/feature_family/mist_surface.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile"] = compile_result

    client = redis_client_or_none()
    result["redis_available"] = client is not None
    if client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    from app.mme_scalpx.core import names as N  # type: ignore

    orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    errors_key = getattr(N, "STREAM_ERRORS_MME", "system:errors:stream")
    runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
    position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")
    features_hash_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))

    feature_once = run_feature_once(client)
    snapshot = feature_snapshot(client, features_hash_key)
    runtime = hgetall(client, runtime_key)
    position = position_summary(hgetall(client, position_key))
    orders_len = xlen(client, orders_key)
    latest_orders = latest_rows(client, orders_key, count=5)
    latest_decisions = latest_rows(client, decisions_key, count=12)
    latest_errors = latest_rows(client, errors_key, count=20)
    processes = {
        "feeds": pgrep_service("feeds"),
        "features": pgrep_service("features"),
        "strategy": pgrep_service("strategy"),
        "risk": pgrep_service("risk"),
        "execution": pgrep_service("execution"),
    }

    real_live = str(runtime.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    classification = classify(snapshot, runtime, processes)

    result.update({
        "feature_once": feature_once,
        "feature_snapshot": snapshot,
        "runtime": runtime,
        "position": position,
        "streams": {
            "orders_len": orders_len,
            "decisions_len": xlen(client, decisions_key),
        },
        "latest_orders": latest_orders,
        "latest_decisions": latest_decisions,
        "latest_errors": latest_errors,
        "processes": processes,
        "classification": classification,
    })

    required = {
        "compile_pass": compile_result["returncode"] == 0,
        "redis_available": True,
        "o20r3b_expected_fail_gate": o20r3b.get("final_verdict") == "FAIL_CLOSED_PRE_RUNTIME_ABI_HASH_HYGIENE_NOT_PROVEN",
        "feature_once_no_exception": feature_once.get("ok") is True,
        "abi_common_key_match": snapshot.get("common_key_match") is True,
        "abi_selected_option_key_match": snapshot.get("selected_option_key_match") is True,
        "abi_selected_option_rich_not_in_common": snapshot.get("selected_option_rich_in_common") is False,
        "all_10_branch_frames_present": snapshot.get("branch_frame_count") == 10,
        "mist_call_visible": snapshot.get("mist_call_present") is True,
        "data_valid_false_classified": "DATA_VALID_FALSE" in classification.get("likely_tags", []),
        "orders_zero": orders_len == 0,
        "latest_orders_empty": len(latest_orders) == 0,
        "position_flat": position["flat"] is True,
        "real_live_false": real_live is False,
        "strategy_not_running": len(processes["strategy"]) == 0,
        "risk_not_running": len(processes["risk"]) == 0,
        "execution_not_running": len(processes["execution"]) == 0,
        "patch_not_performed": True,
        "no_paper_start": True,
        "no_broker_call": True,
        "no_threshold_relaxation": True,
        "no_forced_candidate": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O20_R3C_DATA_VALIDITY_SOURCE_AUDIT_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect O20-R3C proof. Do not run O20-R3B/O23."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O20_R3C_DATA_VALIDITY_SOURCE_CLASSIFIED_ABI_OK_RUNTIME_DATA_BLOCKED"
    result["next_recommended_batch"] = "26-O20-R3D fail-closed data-validity semantics repair/audit OR wait for fresh live feed; still no real live"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
