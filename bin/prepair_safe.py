#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
PIDFILES = [
    ROOT / "run/live_capture/pfeeds.pid",
    ROOT / "run/live_capture/pfeatures.pid",
    ROOT / "run/live_capture/pstrategy.pid",
]


def sh(cmd: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired as e:
        return 124, f"TIMEOUT: {' '.join(cmd)}: {e}"
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"


def redis(*args: str) -> tuple[int, str]:
    return sh(["redis-cli", "-h", "127.0.0.1", "-p", "6379", *args], timeout=8)


def pids(pattern: str) -> list[int]:
    """Return PIDs whose /proc cmdline contains pattern.

    Avoid pgrep -f because it can match its own shell/pgrep command line.
    """
    vals: list[int] = []
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
        vals.append(pid)
    return sorted(set(vals))


def kill_pattern(pattern: str, label: str, actions: list[dict[str, Any]]) -> None:
    found = pids(pattern)
    for pid in found:
        actions.append({"action": "kill_term", "label": label, "pid": pid})
        sh(["kill", str(pid)], timeout=5)
    time.sleep(3)
    found2 = pids(pattern)
    for pid in found2:
        actions.append({"action": "kill_kill", "label": label, "pid": pid})
        sh(["kill", "-9", str(pid)], timeout=5)


def main() -> int:
    proof: dict[str, Any] = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "prepair_safe.py",
        "scope": "feeds_runtime_hygiene_only",
        "risk_execution_started": False,
        "paper_live_enabled": False,
        "redis_restarted": False,
        "actions": [],
    }
    actions = proof["actions"]

    # Safety: never run if execution process is actually running.
    execution_pids = pids("app.mme_scalpx.main --service execution")
    risk_pids = pids("app.mme_scalpx.main --service risk")
    if execution_pids or risk_pids:
        proof["verdict"] = "REFUSED_EXECUTION_OR_RISK_PROCESS_RUNNING"
        proof["execution_pids"] = execution_pids
        proof["risk_pids"] = risk_pids
        print(json.dumps(proof, indent=2, sort_keys=True))
        return 3

    rc, ping = redis("PING")
    if rc != 0 or ping.strip() != "PONG":
        proof["verdict"] = "REFUSED_REDIS_NOT_HEALTHY"
        proof["redis_ping"] = ping
        print(json.dumps(proof, indent=2, sort_keys=True))
        return 3

    # Stop all MME main processes except do not special-case features/strategy:
    # stale features/strategy are stopped too because this repair is restoring feed-only hygiene.
    kill_pattern("app.mme_scalpx.main", "all_mme_main_processes", actions)

    # Clear stale runtime locks.
    for key in ["lock:feeds", "lock:strategy", "lock:execution"]:
        rc, before = redis("GET", key)
        rc_ttl, ttl = redis("PTTL", key)
        rc_del, deleted = redis("DEL", key)
        actions.append({
            "action": "redis_delete_lock",
            "key": key,
            "before": before,
            "ttl_ms": ttl,
            "deleted": deleted,
        })

    # Remove stale pidfiles.
    for f in PIDFILES:
        if f.exists():
            try:
                raw = f.read_text().strip()
            except Exception:
                raw = ""
            f.unlink(missing_ok=True)
            actions.append({"action": "remove_pidfile", "path": str(f), "old_value": raw})

    # Start feeds only through existing pfeeds helper.
    rc_start, out_start = sh(["bash", "-lc", "source ~/.bashrc >/dev/null 2>&1 || true; pfeeds --force-all"], timeout=60)
    actions.append({"action": "pfeeds_force_all", "returncode": rc_start, "output_tail": out_start[-4000:]})

    # Read back state after repair.
    rc_feed_ps, feed_ps = sh(["bash", "-lc", "ps -ef | grep -E 'app.mme_scalpx.main --service feeds' | grep -v grep || true"])
    rc_exec_ps, exec_ps = sh(["bash", "-lc", "ps -ef | grep -E 'app.mme_scalpx.main --service execution' | grep -v grep || true"])
    rc_lf, lock_feeds = redis("GET", "lock:feeds")
    rc_le, lock_execution = redis("GET", "lock:execution")
    rc_err, err_len = redis("XLEN", "system:errors:stream")

    proof["readback"] = {
        "feed_processes": feed_ps,
        "execution_processes": exec_ps,
        "lock_feeds": lock_feeds,
        "lock_execution": lock_execution,
        "errors_xlen": err_len,
    }

    # Final health one-shot.
    rc_h, out_h = sh([str(ROOT / "bin/phealth_safe.py")], timeout=30)
    proof["post_health_returncode"] = rc_h
    proof["post_health"] = out_h[-8000:]

    proof["verdict"] = "REPAIR_ATTEMPTED"
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if rc_start == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
