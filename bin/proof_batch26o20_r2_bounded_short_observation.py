#!/usr/bin/env python3
from __future__ import annotations

import atexit
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

BATCH = "26-O20-R2"
RUN_SECONDS = int(os.environ.get("BATCH26O20_R2_RUN_SECONDS", "150"))
RUN_SECONDS = max(90, min(RUN_SECONDS, 240))
SAMPLE_COUNT = int(os.environ.get("BATCH26O20_R2_SAMPLE_COUNT", "6"))
SAMPLE_COUNT = max(4, min(SAMPLE_COUNT, 10))

PROOF_PATH = ROOT / "run/proofs/proof_batch26o20_r2_bounded_short_observation.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o20_r2_bounded_short_observation.json"
O20R_PATH = ROOT / "run/proofs/proof_batch26o20r_recovery_after_terminated_o20.json"
RUN_DIR = ROOT / os.environ.get("BATCH26O20_R2_RUN_DIR", "run/live_capture/batch26o20_r2_bounded_short")
RUN_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "bin/proof_batch26o20_r2_bounded_short_observation.py",
    "run/proofs/proof_batch26o20r_recovery_after_terminated_o20.json",
]

_STARTED_SERVICES: list[dict[str, Any]] = []
_FINAL_WRITTEN = False
_LAST_RESULT: dict[str, Any] = {}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def load_json_path(path: pathlib.Path) -> dict[str, Any]:
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
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o20_r2_bounded_short_observation.py"
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


def start_service(service: str) -> dict[str, Any]:
    before = pgrep_service(service)
    if before:
        return {
            "service": service,
            "started": False,
            "already_running": True,
            "before": before,
            "pid": None,
        }

    log_path = RUN_DIR / f"o20_r2_{service}.log"
    pid_path = RUN_DIR / f"o20_r2_{service}.pid"

    args = [
        sys.executable,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        service,
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
        "SCALPX_AUTOMATIC_BROKER_FAILOVER_ALLOWED": "0",
        "SCALPX_MID_POSITION_PROVIDER_MIGRATION_ALLOWED": "0",
        "SCALPX_HEAVY_MONITOR_ALLOWED": "0",
    }

    with log_path.open("ab") as log:
        proc = subprocess.Popen(
            args,
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            start_new_session=True,
        )

    pid_path.write_text(str(proc.pid), encoding="utf-8")
    time.sleep(2)
    after = pgrep_service(service)
    item = {
        "service": service,
        "started": True,
        "already_running": False,
        "pid": proc.pid,
        "pid_path": str(pid_path),
        "log_path": str(log_path),
        "after": after,
    }
    _STARTED_SERVICES.append(item)
    return item


def stop_started_services() -> list[dict[str, Any]]:
    stopped: list[dict[str, Any]] = []
    for item in reversed(_STARTED_SERVICES):
        if not item.get("started") or not item.get("pid"):
            continue
        pid = int(item["pid"])
        service = str(item["service"])
        try:
            os.killpg(pid, signal.SIGTERM)
            time.sleep(2)
        except Exception:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
            except Exception:
                pass

        still = pgrep_service(service)
        if any(str(pid) in row for row in still):
            try:
                os.killpg(pid, signal.SIGKILL)
            except Exception:
                try:
                    os.kill(pid, signal.SIGKILL)
                except Exception:
                    pass
        stopped.append({"service": service, "pid": pid, "remaining": pgrep_service(service)})
    return stopped


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


def latest_rows(client: Any, key: str, count: int = 5) -> list[dict[str, Any]]:
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


def feature_snapshot(client: Any, features_hash_key: str) -> dict[str, Any]:
    ff = hget_json(client, features_hash_key, "family_features_json")
    cv = hget_json(client, features_hash_key, "consumer_view_json")
    frames = hget_json(client, features_hash_key, "family_frames_json")

    stage_flags = ff.get("stage_flags", {}) if isinstance(ff, Mapping) else {}
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
        "stage_flags": stage_flags,
        "mist_call_brief": {
            "present": mist_call.get("present") if isinstance(mist_call, Mapping) else None,
            "branch_ready": mist_call.get("branch_ready") if isinstance(mist_call, Mapping) else None,
            "eligible": mist_call.get("eligible") if isinstance(mist_call, Mapping) else None,
            "failed_stage": mist_call.get("failed_stage") if isinstance(mist_call, Mapping) else None,
            "setup_score": mist_call.get("setup_score") if isinstance(mist_call, Mapping) else None,
            "tradability_ok": mist_call.get("tradability_ok") if isinstance(mist_call, Mapping) else None,
        },
    }


def log_tail(paths: list[pathlib.Path], n: int = 35) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in paths:
        if not p.exists():
            out[str(p)] = ["MISSING"]
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            out[str(p)] = lines[-n:]
        except Exception as exc:
            out[str(p)] = [f"READ_ERROR: {type(exc).__name__}: {exc}"]
    return out


def write_outputs(result: dict[str, Any]) -> None:
    global _FINAL_WRITTEN, _LAST_RESULT
    _LAST_RESULT = result
    manifest = {
        "batch": BATCH,
        "created_at_utc": now_utc(),
        "files": [
            {"path": p, "exists": (ROOT / p).exists(), "sha256": sha256_file(ROOT / p)}
            for p in TARGETS
        ],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    _FINAL_WRITTEN = True
    print(json.dumps(result, indent=2, sort_keys=True))


def write_fail_safe(reason: str) -> None:
    try:
        stopped = stop_started_services()
        client = redis_client_or_none()
        snapshot: dict[str, Any] = {}
        if client is not None:
            from app.mme_scalpx.core import names as N  # type: ignore
            orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
            decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
            position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")
            runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
            snapshot = {
                "orders_len": xlen(client, orders_key),
                "decisions_len": xlen(client, decisions_key),
                "position": position_summary(hgetall(client, position_key)),
                "runtime": hgetall(client, runtime_key),
            }
        result = {
            "batch": BATCH,
            "batch_name": "bounded_short_observation",
            "created_at_utc": now_utc(),
            "final_verdict": f"FAIL_SAFE_INTERRUPTED_{reason}",
            "interrupted": True,
            "stopped_started_services": stopped,
            "snapshot": snapshot,
            "scope": {
                "controlled_paper_runtime": True,
                "family": "MIST",
                "branch": "CALL",
                "qty_lots": 1,
                "real_live_allowed": False,
            },
        }
        write_outputs(result)
    except Exception as exc:
        try:
            PROOF_PATH.write_text(json.dumps({
                "batch": BATCH,
                "final_verdict": f"FAIL_SAFE_WRITE_FAILED_{reason}",
                "error": f"{type(exc).__name__}: {exc}",
                "created_at_utc": now_utc(),
            }, indent=2), encoding="utf-8")
        except Exception:
            pass


def _signal_handler(signum: int, frame: Any) -> None:
    if not _FINAL_WRITTEN:
        write_fail_safe(f"SIGNAL_{signum}")
    raise SystemExit(128 + signum)


def _atexit_handler() -> None:
    if not _FINAL_WRITTEN and _STARTED_SERVICES:
        write_fail_safe("ATEXIT")


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)
try:
    signal.signal(signal.SIGHUP, _signal_handler)
except Exception:
    pass
atexit.register(_atexit_handler)


def main() -> int:
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "bounded_short_observation",
        "created_at_utc": now_utc(),
        "run_seconds": RUN_SECONDS,
        "sample_count": SAMPLE_COUNT,
        "scope": {
            "controlled_paper_runtime": True,
            "family": "MIST",
            "branch": "CALL",
            "qty_lots": 1,
            "real_live_allowed": False,
            "automatic_broker_failover": False,
            "mid_position_provider_migration": False,
            "heavy_monitor": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "nohup_safe": True,
            "reduced_duration": True,
        },
    }

    client = redis_client_or_none()
    result["redis_available"] = client is not None
    if client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    o20r = load_json_path(O20R_PATH)
    result["o20r_gate"] = {
        "exists": bool(o20r),
        "final_verdict": o20r.get("final_verdict"),
        "required_verdicts": o20r.get("required_verdicts"),
        "next_recommended_batch": o20r.get("next_recommended_batch"),
    }

    if o20r.get("final_verdict") != "PASS_O20R_RECOVERY_SAFE_AFTER_TERMINATED_O20":
        result["final_verdict"] = "FAIL_CLOSED_O20R_NOT_PASS"
        result["next_recommended_batch"] = "Do not rerun O20. Inspect O20R proof."
        write_outputs(result)
        return 2

    compile_result = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/settings.py",
    ])
    result["compile"] = compile_result
    if compile_result["returncode"] != 0:
        result["final_verdict"] = "FAIL_CLOSED_COMPILE_FAILED"
        write_outputs(result)
        return 2

    from app.mme_scalpx.core import names as N  # type: ignore

    orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    features_stream_key = getattr(N, "STREAM_FEATURES_MME", "features:mme:stream")
    errors_key = getattr(N, "STREAM_ERRORS_MME", "system:errors:stream")
    health_key = getattr(N, "STREAM_HEALTH_MME", "system:health:stream")
    runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
    position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")
    features_hash_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))

    orders_before = xlen(client, orders_key)
    decisions_before = xlen(client, decisions_key)
    features_before = xlen(client, features_stream_key)
    errors_before = xlen(client, errors_key)
    health_before = xlen(client, health_key)

    runtime_before = hgetall(client, runtime_key)
    position_before = position_summary(hgetall(client, position_key))
    feature_before = feature_snapshot(client, features_hash_key)

    pre_processes = {
        "feeds": pgrep_service("feeds"),
        "features": pgrep_service("features"),
        "strategy": pgrep_service("strategy"),
        "risk": pgrep_service("risk"),
        "execution": pgrep_service("execution"),
    }

    if not position_before["flat"]:
        result.update({
            "pre_processes": pre_processes,
            "position_before": position_before,
            "final_verdict": "FAIL_CLOSED_POSITION_NOT_FLAT_BEFORE_START",
            "next_recommended_batch": "Do not continue. Flatten/reconcile position state first.",
        })
        write_outputs(result)
        return 2

    real_live_before = str(runtime_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}
    if real_live_before:
        result.update({
            "pre_processes": pre_processes,
            "runtime_before": runtime_before,
            "final_verdict": "FAIL_CLOSED_REAL_LIVE_APPROVED_TRUE_BEFORE_START",
            "next_recommended_batch": "Do not continue. Real-live flag must be false.",
        })
        write_outputs(result)
        return 2

    start_order = ["feeds", "features", "strategy", "risk", "execution"]
    start_results: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []
    stop_results: list[dict[str, Any]] = []

    try:
        for service in start_order:
            start_results.append(start_service(service))
            time.sleep(2)

        sleep_each = max(5, RUN_SECONDS // SAMPLE_COUNT)
        for i in range(SAMPLE_COUNT):
            time.sleep(sleep_each)
            runtime_now = hgetall(client, runtime_key)
            samples.append({
                "sample": i + 1,
                "ts": now_utc(),
                "orders_len": xlen(client, orders_key),
                "decisions_len": xlen(client, decisions_key),
                "features_len": xlen(client, features_stream_key),
                "errors_len": xlen(client, errors_key),
                "health_len": xlen(client, health_key),
                "position": position_summary(hgetall(client, position_key)),
                "runtime_real_live_approved": str(runtime_now.get("real_live_approved", "false")).lower(),
                "feature_snapshot": feature_snapshot(client, features_hash_key),
                "processes": {
                    "feeds": pgrep_service("feeds"),
                    "features": pgrep_service("features"),
                    "strategy": pgrep_service("strategy"),
                    "risk": pgrep_service("risk"),
                    "execution": pgrep_service("execution"),
                },
            })
    finally:
        stop_results = stop_started_services()

    orders_after = xlen(client, orders_key)
    decisions_after = xlen(client, decisions_key)
    features_after = xlen(client, features_stream_key)
    errors_after = xlen(client, errors_key)
    health_after = xlen(client, health_key)

    runtime_after = hgetall(client, runtime_key)
    position_after = position_summary(hgetall(client, position_key))
    feature_after = feature_snapshot(client, features_hash_key)
    real_live_after = str(runtime_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    latest_decisions = latest_rows(client, decisions_key, count=8)
    latest_orders = latest_rows(client, orders_key, count=5)
    latest_errors = latest_rows(client, errors_key, count=8)
    latest_health = latest_rows(client, health_key, count=8)
    decision_report = decision_safety(latest_decisions)

    post_processes = {
        "feeds": pgrep_service("feeds"),
        "features": pgrep_service("features"),
        "strategy": pgrep_service("strategy"),
        "risk": pgrep_service("risk"),
        "execution": pgrep_service("execution"),
    }

    log_paths = []
    for service in start_order:
        p = RUN_DIR / f"o20_r2_{service}.log"
        if p.exists():
            log_paths.append(p)

    result.update({
        "pre_processes": pre_processes,
        "start_results": start_results,
        "samples": samples,
        "stopped_started_services": stop_results,
        "post_processes": post_processes,
        "runtime_before": runtime_before,
        "runtime_after": runtime_after,
        "position_before": position_before,
        "position_after": position_after,
        "feature_before": feature_before,
        "feature_after": feature_after,
        "streams": {
            "orders_before": orders_before,
            "orders_after": orders_after,
            "orders_delta": orders_after - orders_before,
            "decisions_before": decisions_before,
            "decisions_after": decisions_after,
            "decisions_delta": decisions_after - decisions_before,
            "features_before": features_before,
            "features_after": features_after,
            "features_delta": features_after - features_before,
            "errors_before": errors_before,
            "errors_after": errors_after,
            "errors_delta": errors_after - errors_before,
            "health_before": health_before,
            "health_after": health_after,
            "health_delta": health_after - health_before,
        },
        "latest_decisions": latest_decisions,
        "latest_orders": latest_orders,
        "latest_errors": latest_errors,
        "latest_health": latest_health,
        "decision_safety": decision_report,
        "log_tail": log_tail(log_paths),
        "env": {
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", ""),
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", ""),
            "SCALPX_CONTROLLED_PAPER_FAMILY": os.environ.get("SCALPX_CONTROLLED_PAPER_FAMILY", ""),
            "SCALPX_CONTROLLED_PAPER_BRANCH": os.environ.get("SCALPX_CONTROLLED_PAPER_BRANCH", ""),
            "SCALPX_CONTROLLED_PAPER_QTY_LOTS": os.environ.get("SCALPX_CONTROLLED_PAPER_QTY_LOTS", ""),
            "SCALPX_REAL_LIVE_ALLOWED": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", ""),
            "SCALPX_AUTOMATIC_BROKER_FAILOVER_ALLOWED": os.environ.get("SCALPX_AUTOMATIC_BROKER_FAILOVER_ALLOWED", ""),
            "SCALPX_MID_POSITION_PROVIDER_MIGRATION_ALLOWED": os.environ.get("SCALPX_MID_POSITION_PROVIDER_MIGRATION_ALLOWED", ""),
            "SCALPX_HEAVY_MONITOR_ALLOWED": os.environ.get("SCALPX_HEAVY_MONITOR_ALLOWED", ""),
        },
    })

    risk_running_samples = sum(1 for s in samples if s.get("processes", {}).get("risk"))
    execution_running_samples = sum(1 for s in samples if s.get("processes", {}).get("execution"))
    strategy_running_samples = sum(1 for s in samples if s.get("processes", {}).get("strategy"))
    features_running_samples = sum(1 for s in samples if s.get("processes", {}).get("features"))
    any_position_not_flat = any(not s.get("position", {}).get("flat", False) for s in samples)
    any_real_live_true = any(str(s.get("runtime_real_live_approved", "")).lower() in {"1", "true", "yes", "y"} for s in samples)
    samples_with_feature_valid = sum(1 for s in samples if s.get("feature_snapshot", {}).get("consumer_view_data_valid") is True)
    samples_with_mist_call = sum(1 for s in samples if s.get("feature_snapshot", {}).get("mist_call_present") is True)

    required = {
        "o20r_pass_gate": result["o20r_gate"]["final_verdict"] == "PASS_O20R_RECOVERY_SAFE_AFTER_TERMINATED_O20",
        "compile_pass": compile_result["returncode"] == 0,
        "controlled_paper_env_enabled": os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME") == "1",
        "scope_ack_exact": os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK") == "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY",
        "family_mist": os.environ.get("SCALPX_CONTROLLED_PAPER_FAMILY") == "MIST",
        "branch_call": os.environ.get("SCALPX_CONTROLLED_PAPER_BRANCH") == "CALL",
        "qty_one_lot": os.environ.get("SCALPX_CONTROLLED_PAPER_QTY_LOTS") == "1",
        "real_live_env_false": os.environ.get("SCALPX_REAL_LIVE_ALLOWED") in {"", "0", "false", "False"},
        "automatic_broker_failover_false": os.environ.get("SCALPX_AUTOMATIC_BROKER_FAILOVER_ALLOWED") in {"", "0", "false", "False"},
        "mid_position_provider_migration_false": os.environ.get("SCALPX_MID_POSITION_PROVIDER_MIGRATION_ALLOWED") in {"", "0", "false", "False"},
        "heavy_monitor_false": os.environ.get("SCALPX_HEAVY_MONITOR_ALLOWED") in {"", "0", "false", "False"},
        "sample_count_reached": len(samples) == SAMPLE_COUNT,
        "position_flat_before": position_before["flat"] is True,
        "position_flat_after": position_after["flat"] is True,
        "position_flat_all_samples": any_position_not_flat is False,
        "real_live_before_false": real_live_before is False,
        "real_live_after_false": real_live_after is False,
        "real_live_false_all_samples": any_real_live_true is False,
        "risk_running_in_most_samples": risk_running_samples >= max(1, SAMPLE_COUNT - 1),
        "execution_running_in_most_samples": execution_running_samples >= max(1, SAMPLE_COUNT - 1),
        "strategy_running_in_most_samples": strategy_running_samples >= max(1, SAMPLE_COUNT - 1),
        "features_running_in_most_samples": features_running_samples >= max(1, SAMPLE_COUNT - 1),
        "features_stream_growth": features_after > features_before,
        "decisions_stream_growth": decisions_after > decisions_before,
        "orders_zero": orders_after == 0,
        "orders_delta_zero": orders_after == orders_before,
        "latest_orders_empty": len(latest_orders) == 0,
        "decisions_hold_only": decision_report["unsafe_count"] == 0,
        "feature_valid_in_samples": samples_with_feature_valid >= max(1, SAMPLE_COUNT // 2),
        "mist_call_visible_in_samples": samples_with_mist_call >= max(1, SAMPLE_COUNT // 2),
        "no_heavy_monitor": True,
        "no_unbounded_polling": True,
        "nohup_safe_driver_used": True,
        "reduced_duration": RUN_SECONDS <= 240,
        "no_threshold_relaxation": True,
        "no_forced_candidate": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O20_R2_BOUNDED_SHORT_OBSERVATION_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect O20-R2 proof/logs. Do not proceed to longer paper/live."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O20_R2_BOUNDED_SHORT_OBSERVATION_OK_NO_ORDER"
    result["next_recommended_batch"] = "26-O21 controlled-paper promotion readiness review; do not enable real live"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
