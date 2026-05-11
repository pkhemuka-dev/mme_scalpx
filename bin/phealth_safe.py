#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
PIDFILE = ROOT / "run/live_capture/pfeeds.pid"

SAFE_TO_AUTOREPAIR_REASONS = {
    "NO_FEEDS_PROCESS",
    "DUPLICATE_FEEDS_PROCESS",
    "PIDFILE_PROCESS_MISSING",
    "PIDFILE_LOCK_OWNER_MISMATCH",
    "FEEDS_PROCESS_LOCK_OWNER_MISMATCH",
    "FEEDS_LOCK_REFRESH_FAILED_LOG",
    "STALE_EXECUTION_LOCK",
    "ERROR_STREAM_ADVANCED_WITH_LOCK_MISMATCH",
}

UNSAFE_REASONS = {
    "REDIS_UNAVAILABLE",
    "REDIS_LOADING",
    "REDIS_BLOCKED_CLIENTS",
    "EXECUTION_PROCESS_RUNNING",
    "RISK_PROCESS_RUNNING",
    "ORDERS_STREAM_NONZERO",
    "PAPER_OR_LIVE_ENABLED",
}


def sh(cmd: list[str], timeout: int = 8) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired as e:
        return 124, f"TIMEOUT: {' '.join(cmd)}: {e}"
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"


def ps_lines(pattern: str) -> list[str]:
    rc, out = sh(["bash", "-lc", f"ps -ef | grep -E {pattern!r} | grep -v grep || true"])
    return [ln for ln in out.splitlines() if ln.strip()]


def pids_for(pattern: str) -> list[int]:
    """Return PIDs whose /proc cmdline contains pattern.

    Avoid pgrep -f because it can match its own shell/pgrep command line,
    producing false feeds/features/strategy/risk/execution positives.
    """
    matches: list[int] = []
    proc = Path("/proc")
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        try:
            raw = (entry / "cmdline").read_bytes()
        except Exception:
            continue
        if not raw:
            continue
        cmdline = raw.replace(b"\x00", b" ").decode("utf-8", "replace").strip()
        if pattern not in cmdline:
            continue
        if "phealth_safe.py" in cmdline or "pwatch_safe.py" in cmdline or "prepair_safe.py" in cmdline:
            continue
        if "pgrep -f" in cmdline:
            continue
        matches.append(pid)
    return sorted(set(matches))


def redis_cmd(*args: str, timeout: int = 5) -> tuple[int, str]:
    return sh(["redis-cli", "-h", "127.0.0.1", "-p", "6379", *args], timeout=timeout)


def parse_info(section: str) -> dict[str, str]:
    rc, out = redis_cmd("INFO", section)
    if rc != 0:
        return {}
    d: dict[str, str] = {}
    for line in out.splitlines():
        if ":" in line and not line.startswith("#"):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d



def env_enabled(value: str | None) -> bool:
    """Interpret environment feature flags safely.

    Empty, 0, false, no, off, none are disabled.
    Only explicit truthy values are enabled.
    """
    if value is None:
        return False
    v = str(value).strip().lower()
    if v in {"", "0", "false", "no", "off", "none", "null"}:
        return False
    return v in {"1", "true", "yes", "on", "enabled", "enable"}


def read_pidfile() -> int | None:
    try:
        raw = PIDFILE.read_text().strip()
        if raw:
            return int(raw)
    except Exception:
        return None
    return None


def pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    return Path(f"/proc/{pid}").exists()


def get_redis_key(key: str) -> str | None:
    rc, out = redis_cmd("GET", key)
    if rc != 0:
        return None
    out = out.strip()
    if out == "":
        return None
    return out


def get_redis_pttl(key: str) -> int | None:
    rc, out = redis_cmd("PTTL", key)
    try:
        return int(out.strip())
    except Exception:
        return None


def pid_from_lock(value: str | None) -> int | None:
    if not value:
        return None
    m = re.search(r":(\d+)$", value)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def stream_last_id(stream: str) -> str | None:
    rc, out = redis_cmd("XREVRANGE", stream, "+", "-", "COUNT", "1")
    if rc != 0 or not out:
        return None
    for line in out.splitlines():
        line = line.strip()
        if re.match(r"^\d+-\d+$", line):
            return line
    # redis-cli often prints "1) \"177...-0\""
    m = re.search(r"(\d{10,}-\d+)", out)
    return m.group(1) if m else None


def stream_xlen(stream: str) -> int | None:
    rc, out = redis_cmd("XLEN", stream)
    try:
        return int(out.strip())
    except Exception:
        return None



def latest_pfeeds_log_contains(pattern: str) -> bool:
    try:
        logs = sorted((ROOT / "run/live_capture").glob("pfeeds_live_raw_capture_*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not logs:
            return False
        latest = logs[0]
        data = latest.read_bytes()[-120000:].decode("utf-8", "replace")
        return pattern in data
    except Exception:
        return False


@dataclass
class Health:
    observed_at_utc: str
    verdict: str
    reasons: list[str]
    safe_to_autorepair: bool
    operator_required: bool
    redis: dict[str, Any]
    processes: dict[str, Any]
    locks: dict[str, Any]
    streams: dict[str, Any]
    safety: dict[str, Any]


def main() -> int:
    reasons: list[str] = []

    # Redis health
    rc, ping = redis_cmd("PING")
    redis_ok = (rc == 0 and ping.strip() == "PONG")
    if not redis_ok:
        reasons.append("REDIS_UNAVAILABLE")

    persistence = parse_info("persistence") if redis_ok else {}
    memory = parse_info("memory") if redis_ok else {}
    clients = parse_info("clients") if redis_ok else {}

    loading = persistence.get("loading")
    blocked_clients = clients.get("blocked_clients")
    used_memory = int(memory.get("used_memory", "0") or 0)
    maxmemory = int(memory.get("maxmemory", "0") or 0)
    memory_ratio = (used_memory / maxmemory) if maxmemory else 0.0

    if redis_ok and loading != "0":
        reasons.append("REDIS_LOADING")
    if redis_ok and blocked_clients not in (None, "0"):
        reasons.append("REDIS_BLOCKED_CLIENTS")
    if redis_ok and maxmemory and memory_ratio >= 0.90:
        reasons.append("REDIS_MEMORY_HIGH")

    # Process state
    feed_pids = pids_for("app.mme_scalpx.main --service feeds")
    feature_pids = pids_for("app.mme_scalpx.main --service features")
    strategy_pids = pids_for("app.mme_scalpx.main --service strategy")
    risk_pids = pids_for("app.mme_scalpx.main --service risk")
    execution_pids = pids_for("app.mme_scalpx.main --service execution")
    generic_main_pids = [
        p for p in pids_for("app.mme_scalpx.main")
        if p not in set(feed_pids + feature_pids + strategy_pids + risk_pids + execution_pids)
    ]

    if len(feed_pids) == 0:
        reasons.append("NO_FEEDS_PROCESS")
    if len(feed_pids) > 1:
        reasons.append("DUPLICATE_FEEDS_PROCESS")
    if risk_pids:
        reasons.append("RISK_PROCESS_RUNNING")
    if execution_pids:
        reasons.append("EXECUTION_PROCESS_RUNNING")

    # Locks
    lock_feeds = get_redis_key("lock:feeds") if redis_ok else None
    lock_strategy = get_redis_key("lock:strategy") if redis_ok else None
    lock_execution = get_redis_key("lock:execution") if redis_ok else None
    lock_feeds_pid = pid_from_lock(lock_feeds)
    lock_execution_pid = pid_from_lock(lock_execution)
    pidfile_pid = read_pidfile()
    pidfile_alive = pid_alive(pidfile_pid)

    if pidfile_pid and not pidfile_alive:
        reasons.append("PIDFILE_PROCESS_MISSING")

    if feed_pids and lock_feeds_pid and lock_feeds_pid not in feed_pids:
        reasons.append("FEEDS_PROCESS_LOCK_OWNER_MISMATCH")

    if pidfile_pid and lock_feeds_pid and pidfile_pid != lock_feeds_pid:
        reasons.append("PIDFILE_LOCK_OWNER_MISMATCH")

    if lock_execution and not execution_pids:
        reasons.append("STALE_EXECUTION_LOCK")

    if latest_pfeeds_log_contains("feeds singleton lock refresh failed"):
        reasons.append("FEEDS_LOCK_REFRESH_FAILED_LOG")

    # Streams / safety
    stream_names = {
        "fut_zerodha": "ticks:mme:fut:zerodha:stream",
        "fut_dhan": "ticks:mme:fut:dhan:stream",
        "opt_selected_zerodha": "ticks:mme:opt:selected:zerodha:stream",
        "opt_selected_dhan": "ticks:mme:opt:selected:dhan:stream",
        "opt_context_dhan": "ticks:mme:opt:context:dhan:stream",
        "errors": "system:errors:stream",
        "orders": "orders:mme:stream",
    }

    before = {}
    after = {}
    if redis_ok:
        for label, stream in stream_names.items():
            before[label] = {"last_id": stream_last_id(stream), "xlen": stream_xlen(stream)}
        time.sleep(5)
        for label, stream in stream_names.items():
            after[label] = {"last_id": stream_last_id(stream), "xlen": stream_xlen(stream)}

    errors_advanced = bool(redis_ok and before.get("errors", {}).get("last_id") != after.get("errors", {}).get("last_id"))
    if errors_advanced and any(r in reasons for r in ["FEEDS_PROCESS_LOCK_OWNER_MISMATCH", "PIDFILE_LOCK_OWNER_MISMATCH", "DUPLICATE_FEEDS_PROCESS"]):
        reasons.append("ERROR_STREAM_ADVANCED_WITH_LOCK_MISMATCH")

    orders_xlen = after.get("orders", {}).get("xlen")
    if isinstance(orders_xlen, int) and orders_xlen > 0:
        reasons.append("ORDERS_STREAM_NONZERO")

    # Env/safety posture
    unsafe_env = {}
    for k in [
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_ALLOW_REAL_LIVE",
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
    ]:
        unsafe_env[k] = os.environ.get(k, "")

    if (
        env_enabled(unsafe_env.get("SCALPX_REAL_LIVE_ALLOWED"))
        or env_enabled(unsafe_env.get("SCALPX_ALLOW_REAL_LIVE"))
        or env_enabled(unsafe_env.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"))
    ):
        reasons.append("PAPER_OR_LIVE_ENABLED")

    hard_unsafe = any(r in UNSAFE_REASONS for r in reasons)
    repairable = any(r in SAFE_TO_AUTOREPAIR_REASONS for r in reasons)
    safe_to_autorepair = repairable and not hard_unsafe

    if not reasons:
        verdict = "GREEN"
    elif safe_to_autorepair:
        verdict = "FAIL_SAFE_REPAIRABLE"
    else:
        verdict = "FAIL_OPERATOR_REQUIRED"

    health = Health(
        observed_at_utc=datetime.now(timezone.utc).isoformat(),
        verdict=verdict,
        reasons=sorted(set(reasons)),
        safe_to_autorepair=safe_to_autorepair,
        operator_required=(verdict == "FAIL_OPERATOR_REQUIRED"),
        redis={
            "ping": ping.strip() if rc == 0 else None,
            "loading": loading,
            "blocked_clients": blocked_clients,
            "used_memory": used_memory,
            "maxmemory": maxmemory,
            "memory_ratio": memory_ratio,
        },
        processes={
            "feeds": feed_pids,
            "features": feature_pids,
            "strategy": strategy_pids,
            "risk": risk_pids,
            "execution": execution_pids,
            "generic_main": generic_main_pids,
            "pidfile_pid": pidfile_pid,
            "pidfile_alive": pidfile_alive,
        },
        locks={
            "lock_feeds": lock_feeds,
            "lock_feeds_pid": lock_feeds_pid,
            "lock_feeds_ttl_ms": get_redis_pttl("lock:feeds") if redis_ok else None,
            "lock_strategy": lock_strategy,
            "lock_execution": lock_execution,
            "lock_execution_pid": lock_execution_pid,
            "lock_execution_ttl_ms": get_redis_pttl("lock:execution") if redis_ok else None,
        },
        streams={
            "before": before,
            "after": after,
            "errors_advanced": errors_advanced,
        },
        safety={
            "orders_xlen": orders_xlen,
            "unsafe_env": unsafe_env,
            "risk_execution_auto_start_forbidden": True,
            "paper_live_forbidden": True,
        },
    )

    print(json.dumps(asdict(health), indent=2, sort_keys=True))
    return 0 if verdict == "GREEN" else (2 if safe_to_autorepair else 3)


if __name__ == "__main__":
    raise SystemExit(main())
