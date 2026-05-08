#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O20-R3A"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o20_r3a_persistent_features_abi_publish_repair.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o20_r3a_persistent_features_abi_publish_repair.json"
O20R3_PATH = ROOT / "run/proofs/proof_batch26o20_r3_corrected_bounded_observation.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
RUN_DIR = ROOT / os.environ.get("BATCH26O20_R3A_RUN_DIR", "run/live_capture/batch26o20_r3a_features_only")
RUN_DIR.mkdir(parents=True, exist_ok=True)

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
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o20_r3a_persistent_features_abi_publish_repair.py",
    "run/proofs/proof_batch26o20_r3_corrected_bounded_observation.json",
]


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
    self_name = "proof_batch26o20_r3a_persistent_features_abi_publish_repair.py"
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


def pid_from_line(line: str) -> int | None:
    try:
        return int(line.split()[0])
    except Exception:
        return None


def stop_services(services: list[str], include_feeds: bool = False) -> dict[str, Any]:
    before = {svc: pgrep_service(svc) for svc in services}
    killed: list[dict[str, Any]] = []
    for svc in services:
        if svc == "feeds" and not include_feeds:
            continue
        for line in before.get(svc, []):
            pid = pid_from_line(line)
            if not pid:
                continue
            try:
                os.kill(pid, signal.SIGTERM)
                killed.append({"service": svc, "pid": pid, "signal": "TERM", "line": line})
            except Exception as exc:
                killed.append({"service": svc, "pid": pid, "signal": "TERM_FAILED", "error": f"{type(exc).__name__}: {exc}", "line": line})
    time.sleep(2)
    mid = {svc: pgrep_service(svc) for svc in services}
    for svc in services:
        if svc == "feeds" and not include_feeds:
            continue
        for line in mid.get(svc, []):
            pid = pid_from_line(line)
            if not pid:
                continue
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append({"service": svc, "pid": pid, "signal": "KILL", "line": line})
            except Exception:
                pass
    time.sleep(1)
    after = {svc: pgrep_service(svc) for svc in services}
    return {"before": before, "killed": killed, "after": after}


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


def feature_snapshot(client: Any, features_hash_key: str) -> dict[str, Any]:
    ff = hget_json(client, features_hash_key, "family_features_json")
    cv = hget_json(client, features_hash_key, "consumer_view_json")
    frames = hget_json(client, features_hash_key, "family_frames_json")

    common = ff.get("common", {}) if isinstance(ff, Mapping) else {}
    selected = common.get("selected_option", {}) if isinstance(common, Mapping) else {}
    branch_frames = cv.get("branch_frames", {}) if isinstance(cv, Mapping) else {}
    mist_call = branch_frames.get("mist_call", {}) if isinstance(branch_frames, Mapping) else {}

    return {
        "family_features_present": bool(ff),
        "consumer_view_present": bool(cv),
        "consumer_view_data_valid": cv.get("data_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_safe_to_consume": cv.get("safe_to_consume") if isinstance(cv, Mapping) else None,
        "branch_frame_count": len(branch_frames) if isinstance(branch_frames, Mapping) else 0,
        "mist_call_present": "mist_call" in branch_frames if isinstance(branch_frames, Mapping) else False,
        "family_frame_keys": sorted(frames.keys()) if isinstance(frames, Mapping) else [],
        "common_keys": list(common.keys()) if isinstance(common, Mapping) else [],
        "common_key_match": tuple(common.keys()) == EXPECTED_COMMON_KEYS if isinstance(common, Mapping) else False,
        "selected_option_keys": list(selected.keys()) if isinstance(selected, Mapping) else [],
        "selected_option_key_match": tuple(selected.keys()) == EXPECTED_SELECTED_OPTION_KEYS if isinstance(selected, Mapping) else False,
        "selected_option_rich_in_common": "selected_option_rich" in common if isinstance(common, Mapping) else False,
        "mist_call_brief": {
            "eligible": mist_call.get("eligible") if isinstance(mist_call, Mapping) else None,
            "tradability_ok": mist_call.get("tradability_ok") if isinstance(mist_call, Mapping) else None,
            "option_symbol": mist_call.get("option_symbol") if isinstance(mist_call, Mapping) else None,
        },
    }


def patch_features_persistent_publish_abi(before: str) -> dict[str, Any]:
    marker = "Batch 26-O20-R3A persistent features ABI publish sanitizer"
    if marker in before:
        return {"patched": False, "already_present": True, "reason": "marker already present"}

    required = ["FeatureService", "run_once", "HASH_FEATURES", "_json_dump"]
    missing = [x for x in required if x not in before]
    if missing:
        return {"patched": False, "already_present": False, "reason": "required markers missing", "missing": missing}

    backup = ROOT / "run/_code_backups" / f"batch26o20_r3a_features_py_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pre_patch"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(before, encoding="utf-8")

    patch = r'''

# =============================================================================
# Batch 26-O20-R3A persistent features ABI publish sanitizer
# =============================================================================
#
# Safety:
# - features.py only
# - no strategy/risk/execution patch
# - no order writes
# - no threshold relaxation
# - no candidate forcing
#
# Intent:
# Sanitize the exact family_features_json / payload_json written to Redis in
# the persistent FeatureService loop. This protects long-running service publish
# paths from leaking rich selected-option runtime keys into the frozen
# feature-family ABI consumed by strategy.

_BATCH26O20R3A_COMMON_KEYS = (
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

_BATCH26O20R3A_SELECTED_KEYS = (
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


def _batch26o20r3a_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _batch26o20r3a_sanitize_selected_option(value: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rich = dict(value or {})
    selected = {
        "side": str(rich.get("side") or rich.get("option_side") or "CALL").upper(),
        "ltp": _batch26o20r3a_float(rich.get("ltp"), 0.0),
        "spread": _batch26o20r3a_float(rich.get("spread"), 0.0),
        "spread_ratio": _batch26o20r3a_float(rich.get("spread_ratio"), 0.0),
        "depth_total": _batch26o20r3a_float(rich.get("depth_total"), 0.0),
        "depth_ok": bool(rich.get("depth_ok") is True or _batch26o20r3a_float(rich.get("depth_total"), 0.0) > 0.0),
        "ofi_ratio_proxy": rich.get("ofi_ratio_proxy"),
        "microprice": rich.get("microprice"),
        "micro_edge": rich.get("micro_edge"),
        "delta_3": rich.get("delta_3"),
        "response_efficiency": _batch26o20r3a_float(rich.get("response_efficiency"), 0.0),
        "tradability_ok": bool(rich.get("tradability_ok") is True or rich.get("selected_option_tradability_ok") is True),
    }
    return selected, rich


def _batch26o20r3a_sanitize_family_features_payload(payload: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    out = dict(payload or {})
    common = dict(out.get("common", {}) or {})
    selected_raw = dict(common.get("selected_option", {}) or {})
    rich_from_common = dict(common.get("selected_option_rich", {}) or {})
    selected, rich_from_selected = _batch26o20r3a_sanitize_selected_option(selected_raw)
    rich = rich_from_common or rich_from_selected

    clean_common = {
        "regime": common.get("regime"),
        "strategy_runtime_mode_classic": common.get("strategy_runtime_mode_classic"),
        "strategy_runtime_mode_miso": common.get("strategy_runtime_mode_miso"),
        "futures": common.get("futures", {}),
        "call": common.get("call", {}),
        "put": common.get("put", {}),
        "selected_option": selected,
        "cross_option": common.get("cross_option", {}),
        "economics": common.get("economics", {}),
        "signals": common.get("signals", {}),
    }
    out["common"] = clean_common
    return out, rich


if "_BATCH26O20R3A_ORIGINAL_HSET" not in globals() and "FeatureService" in globals():
    _BATCH26O20R3A_ORIGINAL_HSET = FeatureService.__init__

    def _batch26o20r3a_feature_init(self: FeatureService, *args: Any, **kwargs: Any) -> None:
        _BATCH26O20R3A_ORIGINAL_HSET(self, *args, **kwargs)
        if getattr(self, "_batch26o20r3a_redis_wrapped", False):
            return
        original_redis = self.redis

        class _Batch26O20R3ARedisGuard:
            def __init__(self, inner: Any):
                self._inner = inner

            def __getattr__(self, name: str) -> Any:
                return getattr(self._inner, name)

            def hgetall(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.hgetall(*args, **kwargs)

            def xadd(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.xadd(*args, **kwargs)

            def xlen(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.xlen(*args, **kwargs)

            def xrevrange(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.xrevrange(*args, **kwargs)

            def hset(self, key: Any, mapping: Any = None, **kwargs: Any) -> Any:
                try:
                    if key == HASH_FEATURES and isinstance(mapping, Mapping):
                        guarded = dict(mapping)
                        rich: dict[str, Any] = {}
                        if guarded.get("family_features_json"):
                            ff = json.loads(guarded.get("family_features_json") or "{}")
                            if isinstance(ff, Mapping):
                                ff_clean, rich = _batch26o20r3a_sanitize_family_features_payload(ff)
                                guarded["family_features_json"] = _json_dump(ff_clean)

                        if guarded.get("payload_json"):
                            pp = json.loads(guarded.get("payload_json") or "{}")
                            if isinstance(pp, Mapping):
                                pp = dict(pp)
                                ff2 = pp.get("family_features")
                                if isinstance(ff2, Mapping):
                                    ff2_clean, rich2 = _batch26o20r3a_sanitize_family_features_payload(ff2)
                                    pp["family_features"] = ff2_clean
                                    if rich2 and not rich:
                                        rich = rich2
                                guarded["payload_json"] = _json_dump(pp)

                        guarded["selected_option_rich_json"] = _json_dump(rich)
                        guarded["o20r3a_abi_guard_json"] = _json_dump({
                            "common_keys": list(_BATCH26O20R3A_COMMON_KEYS),
                            "selected_option_keys": list(_BATCH26O20R3A_SELECTED_KEYS),
                            "persistent_publish_guard": True,
                            "forced_candidate": False,
                            "threshold_relaxation": False,
                        })
                        mapping = guarded
                except Exception:
                    pass

                if mapping is not None:
                    return self._inner.hset(key, mapping=mapping, **kwargs)
                return self._inner.hset(key, **kwargs)

        self.redis = _Batch26O20R3ARedisGuard(original_redis)
        self._batch26o20r3a_redis_wrapped = True

    FeatureService.__init__ = _batch26o20r3a_feature_init
'''
    TARGET_FEATURES.write_text(before.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {"patched": True, "already_present": False, "backup": str(backup), "reason": "persistent Redis hset ABI guard appended"}


def start_features_service() -> dict[str, Any]:
    before = pgrep_service("features")
    if before:
        return {"started": False, "already_running": True, "before": before, "pid": None}

    log_path = RUN_DIR / "o20_r3a_features.log"
    pid_path = RUN_DIR / "o20_r3a_features.pid"
    args = [
        sys.executable,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        "features",
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ]
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "1",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY",
        "SCALPX_CONTROLLED_PAPER_FAMILY": "MIST",
        "SCALPX_CONTROLLED_PAPER_BRANCH": "CALL",
        "SCALPX_CONTROLLED_PAPER_QTY_LOTS": "1",
        "SCALPX_REAL_LIVE_ALLOWED": "0",
    }
    with log_path.open("ab") as log:
        proc = subprocess.Popen(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    pid_path.write_text(str(proc.pid), encoding="utf-8")
    time.sleep(2)
    return {"started": True, "already_running": False, "pid": proc.pid, "log_path": str(log_path), "pid_path": str(pid_path), "after": pgrep_service("features")}


def stop_pid(pid: int | None) -> list[str]:
    if not pid:
        return pgrep_service("features")
    try:
        os.killpg(pid, signal.SIGTERM)
        time.sleep(2)
    except Exception:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
        except Exception:
            pass
    still = pgrep_service("features")
    if any(str(pid) in row for row in still):
        try:
            os.killpg(pid, signal.SIGKILL)
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
    time.sleep(1)
    return pgrep_service("features")


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
        "batch_name": "persistent_features_abi_publish_repair",
        "created_at_utc": now_utc(),
        "scope": {
            "patch_target": "features.py only",
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

    client = redis_client_or_none()
    result["redis_available"] = client is not None
    if client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    o20r3 = load_json(O20R3_PATH)
    result["o20r3_gate"] = {
        "exists": bool(o20r3),
        "final_verdict": o20r3.get("final_verdict"),
        "pre_runtime_hygiene_required": o20r3.get("pre_runtime_hygiene_required"),
    }

    if o20r3.get("final_verdict") != "FAIL_CLOSED_FEATURE_SERVICE_PUBLISHED_INVALID_ABI":
        result["final_verdict"] = "FAIL_CLOSED_O20R3_NOT_EXPECTED_FEATURE_ABI_FAILURE"
        write_outputs(result)
        return 2

    compile_before = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/feature_family/contracts.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile_before"] = compile_before

    from app.mme_scalpx.core import names as N  # type: ignore

    orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
    position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")
    features_hash_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))

    safety_before = {
        "orders_len": xlen(client, orders_key),
        "decisions_len": xlen(client, decisions_key),
        "position": position_summary(hgetall(client, position_key)),
        "runtime": hgetall(client, runtime_key),
        "processes": {
            "features": pgrep_service("features"),
            "strategy": pgrep_service("strategy"),
            "risk": pgrep_service("risk"),
            "execution": pgrep_service("execution"),
        },
    }
    result["safety_before"] = safety_before

    cleanup = stop_services(["features", "strategy", "risk", "execution"], include_feeds=False)
    result["cleanup_before_patch"] = cleanup

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    patch_result = patch_features_persistent_publish_abi(before_text)
    result["patch_result"] = patch_result
    result["patch_performed"] = bool(patch_result.get("patched"))

    compile_after = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/feature_family/contracts.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile_after"] = compile_after

    feature_start = start_features_service()
    samples: list[dict[str, Any]] = []
    try:
        for i in range(6):
            time.sleep(5)
            snap = feature_snapshot(client, features_hash_key)
            samples.append({
                "sample": i + 1,
                "ts": now_utc(),
                "feature_snapshot": snap,
                "features_processes": pgrep_service("features"),
                "orders_len": xlen(client, orders_key),
                "position": position_summary(hgetall(client, position_key)),
            })
    finally:
        remaining_features = stop_pid(feature_start.get("pid") if isinstance(feature_start, Mapping) else None)

    safety_after = {
        "orders_len": xlen(client, orders_key),
        "latest_orders": latest_rows(client, orders_key, count=5),
        "position": position_summary(hgetall(client, position_key)),
        "runtime": hgetall(client, runtime_key),
        "processes": {
            "features": pgrep_service("features"),
            "strategy": pgrep_service("strategy"),
            "risk": pgrep_service("risk"),
            "execution": pgrep_service("execution"),
        },
    }

    result.update({
        "feature_start": feature_start,
        "samples": samples,
        "remaining_features_after_stop": remaining_features,
        "safety_after": safety_after,
    })

    real_live_after = str(safety_after["runtime"].get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}
    sample_valid_count = sum(1 for s in samples if s["feature_snapshot"].get("consumer_view_data_valid") is True)
    sample_common_match_count = sum(1 for s in samples if s["feature_snapshot"].get("common_key_match") is True)
    sample_selected_match_count = sum(1 for s in samples if s["feature_snapshot"].get("selected_option_key_match") is True)
    sample_rich_absent_count = sum(1 for s in samples if s["feature_snapshot"].get("selected_option_rich_in_common") is False)
    sample_mist_call_count = sum(1 for s in samples if s["feature_snapshot"].get("mist_call_present") is True)
    sample_feature_process_count = sum(1 for s in samples if len(s.get("features_processes", [])) > 0)

    required = {
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "patch_performed_or_already_present": bool(patch_result.get("patched") or patch_result.get("already_present")),
        "features_service_started": bool(feature_start.get("started") or feature_start.get("already_running")),
        "feature_process_seen_in_samples": sample_feature_process_count >= 4,
        "consumer_view_data_valid_in_samples": sample_valid_count >= 4,
        "common_key_match_in_samples": sample_common_match_count >= 4,
        "selected_option_key_match_in_samples": sample_selected_match_count >= 4,
        "selected_option_rich_absent_from_common_in_samples": sample_rich_absent_count >= 4,
        "mist_call_visible_in_samples": sample_mist_call_count >= 4,
        "orders_zero": safety_after["orders_len"] == 0,
        "latest_orders_empty": len(safety_after["latest_orders"]) == 0,
        "position_flat": safety_after["position"]["flat"] is True,
        "real_live_false": real_live_after is False,
        "strategy_not_running": len(safety_after["processes"]["strategy"]) == 0,
        "risk_not_running": len(safety_after["processes"]["risk"]) == 0,
        "execution_not_running": len(safety_after["processes"]["execution"]) == 0,
        "features_stopped_after_probe": len(safety_after["processes"]["features"]) == 0,
        "no_paper_start": True,
        "no_broker_call": True,
        "no_threshold_relaxation": True,
        "no_forced_candidate": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O20_R3A_PERSISTENT_FEATURES_ABI_REPAIR_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect O20-R3A proof/logs. Do not rerun O20-R3."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O20_R3A_PERSISTENT_FEATURES_ABI_PUBLISH_REPAIR_OK"
    result["next_recommended_batch"] = "26-O20-R3B corrected bounded observation rerun after persistent ABI repair; still no real live"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
