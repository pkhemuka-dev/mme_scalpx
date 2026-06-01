#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

PROJECT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
RECORDER = PROJECT / "bin" / "b1_profit_live_durable_capture.py"

STREAMS = {
    "fut": "ticks:mme:fut:zerodha:stream",
    "opt": "ticks:mme:opt:selected:zerodha:stream",
    "features": "features:mme:stream",
    "decisions": "decisions:mme:stream",
}

STOP = False


def stop(*_: object) -> None:
    global STOP
    STOP = True


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sh(cmd: str) -> str:
    return subprocess.getoutput(cmd).strip()


def run(cmd: list[str], *, env: dict[str, str] | None = None, stdout: Any = subprocess.DEVNULL) -> subprocess.Popen[Any]:
    return subprocess.Popen(
        cmd,
        cwd=str(PROJECT),
        env=env,
        stdout=stdout,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def xlen(stream: str) -> int:
    try:
        return int(sh(f"redis-cli XLEN {stream} 2>/dev/null") or "-1")
    except Exception:
        return -1


def latest_id(stream: str) -> str | None:
    out = sh(f"redis-cli XREVRANGE {stream} + - COUNT 1 2>/dev/null | head -1 | tr -d '\"'")
    return out or None


def age_ms(stream: str) -> int | None:
    sid = latest_id(stream)
    if not sid:
        return None
    try:
        return int(time.time() * 1000) - int(sid.split("-")[0])
    except Exception:
        return None


def pcnt(pattern: str) -> int:
    try:
        return int(sh(f"(pgrep -af \"{pattern}\" 2>/dev/null || true) | grep -v grep | wc -l | tr -d ' '") or "0")
    except Exception:
        return 0


def pids(pattern: str) -> list[int]:
    out = sh(f"(pgrep -af \"{pattern}\" 2>/dev/null || true) | grep -v grep | awk '{{print $1}}'")
    ids: list[int] = []
    for part in out.split():
        try:
            ids.append(int(part))
        except Exception:
            pass
    return ids


def safety_state() -> dict[str, Any]:
    return {
        "orders": xlen("orders:mme:stream"),
        "risk": xlen("risk:mme:stream"),
        "execution": xlen("execution:mme:stream"),
        "risk_pids": pcnt("app\\.mme_scalpx\\.main --service risk"),
        "execution_pids": pcnt("app\\.mme_scalpx\\.main --service execution"),
    }


def safety_clean() -> bool:
    s = safety_state()
    return s["orders"] == 0 and s["risk"] == 0 and s["execution"] == 0 and s["risk_pids"] == 0 and s["execution_pids"] == 0


def service_counts() -> dict[str, int]:
    return {
        "feeds_service": pcnt("app\\.mme_scalpx\\.main --service feeds"),
        "features": pcnt("app\\.mme_scalpx\\.main --service features"),
        "strategy": pcnt("app\\.mme_scalpx\\.main --service strategy"),
        "generic_main": pcnt("app\\.mme_scalpx\\.main$"),
        "recorder": pcnt("bin/b1_profit_live_durable_capture.py"),
    }


def freshness() -> dict[str, Any]:
    return {k: {"stream": v, "latest_id": latest_id(v), "age_ms": age_ms(v)} for k, v in STREAMS.items()}


def env_safe() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT) + ":" + env.get("PYTHONPATH", "")
    env["SCALPX_OBSERVE_ONLY"] = "1"
    env["MME_RUNTIME_MODE"] = "live"
    for k in [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_ALLOW_REAL_LIVE",
        "SCALPX_ALLOW_BROKER_ORDERS",
        "SCALPX_PAPER_ARMED",
        "SCALPX_ENABLE_PAPER",
        "SCALPX_ENABLE_LIVE",
    ]:
        env.pop(k, None)
    return env


def append_jsonl(path: pathlib.Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def start_recorder(outdir: pathlib.Path, action_mode: str, actions: list[str]) -> None:
    if service_counts()["recorder"] > 0:
        return

    actions.append("recorder_missing")
    if action_mode != "apply":
        actions.append("plan_start_recorder")
        return

    rec_outdir = outdir / "durable_capture"
    rec_outdir.mkdir(parents=True, exist_ok=True)
    log = rec_outdir / "recorder.log"
    f = log.open("ab")
    proc = run([
        sys.executable,
        str(RECORDER),
        "--outdir",
        str(rec_outdir),
        "--no-backfill",
    ], env=env_safe(), stdout=f)
    (rec_outdir / "recorder.pid").write_text(str(proc.pid))
    actions.append(f"started_recorder_pid_{proc.pid}")


def start_features_strategy_if_missing(outdir: pathlib.Path, action_mode: str, actions: list[str]) -> None:
    counts = service_counts()
    pybin = str(PROJECT / ".venv" / "bin" / "python")
    if not pathlib.Path(pybin).exists():
        pybin = sys.executable

    if counts["features"] == 0:
        actions.append("features_missing")
        if action_mode == "apply":
            log = (outdir / "features_supervisor_start.log").open("ab")
            proc = run([pybin, "-m", "app.mme_scalpx.main", "--service", "features", "--skip-group-bootstrap"], env=env_safe(), stdout=log)
            actions.append(f"started_features_pid_{proc.pid}")
        else:
            actions.append("plan_start_features")

    if counts["strategy"] == 0:
        actions.append("strategy_missing")
        if action_mode == "apply":
            log = (outdir / "strategy_supervisor_start.log").open("ab")
            proc = run([pybin, "-m", "app.mme_scalpx.main", "--service", "strategy", "--skip-group-bootstrap"], env=env_safe(), stdout=log)
            actions.append(f"started_strategy_pid_{proc.pid}")
        else:
            actions.append("plan_start_strategy")


def start_feeds_if_stale(outdir: pathlib.Path, action_mode: str, stale_after_ms: int, actions: list[str]) -> None:
    fr = freshness()
    fut_stale = fr["fut"]["age_ms"] is None or fr["fut"]["age_ms"] > stale_after_ms
    opt_stale = fr["opt"]["age_ms"] is None or fr["opt"]["age_ms"] > stale_after_ms

    if not fut_stale and not opt_stale:
        return

    actions.append(f"feed_stale_fut={fr['fut']['age_ms']}_opt={fr['opt']['age_ms']}")

    if action_mode != "apply":
        actions.append("plan_start_feeds")
        return

    pybin = str(PROJECT / ".venv" / "bin" / "python")
    if not pathlib.Path(pybin).exists():
        pybin = sys.executable

    log = (outdir / "feeds_supervisor_start.log").open("ab")
    proc = run([
        pybin,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        "feeds",
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ], env=env_safe(), stdout=log)
    actions.append(f"started_feeds_pid_{proc.pid}")


def status(outdir: pathlib.Path, action_mode: str) -> dict[str, Any]:
    return {
        "ts_utc": utc_now(),
        "action_mode": action_mode,
        "safety": safety_state(),
        "service_counts": service_counts(),
        "freshness": freshness(),
        "provider": {
            "mode": sh("redis-cli HGET state:provider:runtime family_runtime_mode 2>/dev/null || true"),
            "futures_status": sh("redis-cli HGET state:provider:runtime futures_marketdata_status 2>/dev/null || true"),
            "selected_status": sh("redis-cli HGET state:provider:runtime selected_option_marketdata_status 2>/dev/null || true"),
            "context_status": sh("redis-cli HGET state:provider:runtime option_context_status 2>/dev/null || true"),
        },
        "outdir": str(outdir),
        "read_only_safety": {
            "risk_start_allowed": False,
            "execution_start_allowed": False,
            "order_allowed": False,
            "redis_delete_allowed": False,
        },
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", required=True)
    p.add_argument("--action-mode", choices=["plan", "apply"], default="plan")
    p.add_argument("--once", action="store_true")
    p.add_argument("--interval-sec", type=int, default=15)
    p.add_argument("--stale-after-ms", type=int, default=30000)
    p.add_argument("--duration-sec", type=int, default=0)
    p.add_argument("--self-test", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        print(json.dumps({
            "self_test": True,
            "action_modes": ["plan", "apply"],
            "starts_allowed": ["feeds", "features", "strategy", "durable_recorder"],
            "starts_forbidden": ["risk", "execution", "orders"],
            "redis_delete_allowed": False,
        }, indent=2, sort_keys=True))
        return 0

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    start = time.time()

    while not STOP:
        actions: list[str] = []
        st = status(outdir, args.action_mode)

        if not safety_clean():
            actions.append("safety_not_clean_no_actions")
        else:
            start_recorder(outdir, args.action_mode, actions)
            start_features_strategy_if_missing(outdir, args.action_mode, actions)
            start_feeds_if_stale(outdir, args.action_mode, args.stale_after_ms, actions)

        st["actions"] = actions
        st["post_action_service_counts"] = service_counts()
        st["post_action_freshness"] = freshness()

        append_jsonl(outdir / "supervisor_events.jsonl", st)
        (outdir / "supervisor_state.json").write_text(json.dumps(st, indent=2, sort_keys=True), encoding="utf-8")

        if args.once:
            break
        if args.duration_sec and time.time() - start >= args.duration_sec:
            break
        time.sleep(args.interval_sec)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
