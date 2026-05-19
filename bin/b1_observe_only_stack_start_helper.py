#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shlex
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED_APPROVAL = (
    "I APPROVE B1 OBSERVE-ONLY STACK START HELPER EXECUTE: "
    "NO PAPER, NO LIVE, NO BROKER ORDER, NO REPLAY, NO PNL, "
    "START FEATURES/STRATEGY/RISK/EXECUTION OBSERVE-ONLY ONLY"
)

FORBIDDEN_ENV_KEYS = [
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
    "SCALPX_REAL_LIVE_ALLOWED",
    "SCALPX_ALLOW_REAL_LIVE",
    "SCALPX_ALLOW_BROKER_ORDERS",
    "SCALPX_PAPER_ARMED",
    "SCALPX_ENABLE_PAPER",
    "SCALPX_ENABLE_LIVE",
]

STREAMS = {
    "features": "features:mme:stream",
    "decisions": "decisions:mme:stream",
    "risk": "risk:mme:stream",
    "execution": "execution:mme:stream",
    "orders": "orders:mme:stream",
}

DEFAULT_SERVICES = ["features", "strategy", "risk", "execution"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str], timeout: int = 90, env: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-12000:],
            "stderr": proc.stderr[-12000:],
            "ok": proc.returncode == 0,
            "timeout": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": cmd,
            "returncode": 124,
            "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-12000:] if isinstance(exc.stderr, str) else "",
            "ok": False,
            "timeout": True,
        }


def redis_raw(args: list[str]) -> str:
    proc = run_cmd(["redis-cli", "--raw"] + args, timeout=20)
    return proc["stdout"].strip() if proc["ok"] else ""


def xlen(key: str) -> int:
    try:
        return int(redis_raw(["XLEN", key]) or 0)
    except Exception:
        return 0


def stream_snapshot() -> dict[str, int]:
    return {label: xlen(key) for label, key in STREAMS.items()}


def process_snapshot() -> dict[str, Any]:
    proc = run_cmd(
        [
            "bash",
            "-lc",
            "ps -eo pid,ppid,etime,args | grep -E 'app\\.mme_scalpx\\.main|b1_observe_only_stack_start_helper|mme-(features|strategy|risk|execution)' | grep -v grep || true",
        ],
        timeout=20,
    )
    return {
        "ok": proc["ok"],
        "stdout": proc["stdout"],
        "matching_line_count": len([line for line in proc["stdout"].splitlines() if line.strip()]),
    }


def env_report() -> dict[str, Any]:
    values = {k: os.environ.get(k) for k in ["SCALPX_OBSERVE_ONLY"] + FORBIDDEN_ENV_KEYS}
    safe = values.get("SCALPX_OBSERVE_ONLY") == "1" and all(values.get(k) in (None, "") for k in FORBIDDEN_ENV_KEYS)
    return {"values": values, "safe": safe}


def _service_env(service: str) -> dict[str, str]:
    env = os.environ.copy()
    env["SCALPX_OBSERVE_ONLY"] = "1"
    for key in FORBIDDEN_ENV_KEYS:
        env.pop(key, None)

    if service == "execution":
        env["SCALPX_B1_EXECUTION_SHADOW_NO_BROKER"] = "1"
    else:
        env.pop("SCALPX_B1_EXECUTION_SHADOW_NO_BROKER", None)

    if service in {"risk", "execution"}:
        env["SCALPX_B1_OBSERVE_ONLY_LIFECYCLE_PUBLISH"] = "1"
    else:
        env.pop("SCALPX_B1_OBSERVE_ONLY_LIFECYCLE_PUBLISH", None)

    return env


def build_service_commands(services: list[str]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for service in services:
        cmd = [sys.executable, "-m", "app.mme_scalpx.main", "--service", service]
        commands.append(
            {
                "service": service,
                "cmd": cmd,
                "cmd_shell": " ".join(shlex.quote(x) for x in cmd),
                "env_overrides": (
                    {"SCALPX_OBSERVE_ONLY": "1", "SCALPX_B1_EXECUTION_SHADOW_NO_BROKER": "1"}
                    if service == "execution"
                    else {"SCALPX_OBSERVE_ONLY": "1"}
                ),
            }
        )
    return commands


def choose_command(services: list[str]) -> dict[str, Any]:
    commands = build_service_commands(services)
    help_probe = run_cmd([sys.executable, "-m", "app.mme_scalpx.main", "--help"], timeout=25)
    return {
        "selected_commands": commands,
        "selected_command_shells": [item["cmd_shell"] for item in commands],
        "selected_command_shell": " ; ".join(item["cmd_shell"] for item in commands),
        "uses_repeated_service_arg": False,
        "help_probe": help_probe,
        "hints": {
            "selection_reason": "B1A-R32 uses one subprocess per singular --service value; observe-only enforced by env",
            "removed_unsupported_args": ["--observe-only", "--services", "repeated --service in one command"],
            "uses_repeated_service_arg": False,
        },
    }


def _tail_pipe(proc: subprocess.Popen[str], stream_name: str) -> str:
    pipe = getattr(proc, stream_name)
    if pipe is None:
        return ""
    try:
        return pipe.read()[-12000:]
    except Exception as exc:
        return f"<{stream_name}_read_error:{type(exc).__name__}:{exc}>"


def execute_service_plan(command_plan: dict[str, Any], wait_seconds: int) -> dict[str, Any]:
    started: list[dict[str, Any]] = []
    processes: list[tuple[str, subprocess.Popen[str]]] = []

    for item in command_plan["selected_commands"]:
        service = str(item["service"])
        cmd = list(item["cmd"])
        env = _service_env(service)
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                start_new_session=True,
            )
            processes.append((service, proc))
            started.append(
                {
                    "service": service,
                    "cmd": cmd,
                    "cmd_shell": item["cmd_shell"],
                    "pid": proc.pid,
                    "started": True,
                    "env_overrides": item["env_overrides"],
                }
            )
        except Exception as exc:
            started.append(
                {
                    "service": service,
                    "cmd": cmd,
                    "cmd_shell": item["cmd_shell"],
                    "pid": None,
                    "started": False,
                    "error": repr(exc),
                    "env_overrides": item["env_overrides"],
                }
            )

    time.sleep(max(1, wait_seconds))

    before_terminate: list[dict[str, Any]] = []
    for service, proc in processes:
        before_terminate.append(
            {
                "service": service,
                "pid": proc.pid,
                "returncode_before_terminate": proc.poll(),
                "running_before_terminate": proc.poll() is None,
            }
        )

    for service, proc in processes:
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass

    time.sleep(2)

    final_results: list[dict[str, Any]] = []
    for service, proc in processes:
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except Exception:
            stdout, stderr = "", ""
        final_results.append(
            {
                "service": service,
                "pid": proc.pid,
                "returncode": proc.returncode,
                "stdout": (stdout or "")[-12000:],
                "stderr": (stderr or "")[-12000:],
                "was_running_before_terminate": any(
                    item["service"] == service and item["running_before_terminate"]
                    for item in before_terminate
                ),
            }
        )

    return {
        "started": started,
        "before_terminate": before_terminate,
        "final_results": final_results,
        "any_start_error": any(not item.get("started") for item in started),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded observe-only stack start helper for B1 lifecycle capture.")
    parser.add_argument("--dry-run", action="store_true", help="Plan only. Does not start anything.")
    parser.add_argument("--execute", action="store_true", help="Execute selected start command only with exact approval.")
    parser.add_argument("--approval-text", default="", help="Exact required approval text for execute mode.")
    parser.add_argument("--wait-seconds", type=int, default=45)
    parser.add_argument("--services", default="features,strategy,risk,execution")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()

    if args.execute and args.dry_run:
        raise SystemExit("--execute and --dry-run are mutually exclusive")

    services = [x.strip() for x in args.services.split(",") if x.strip()] or DEFAULT_SERVICES

    before = stream_snapshot()
    orders_before = before.get("orders", 0)
    env = env_report()
    command_plan = choose_command(services)

    report: dict[str, Any] = {
        "created_at_utc": now_utc(),
        "mode": "execute" if args.execute else "dry_run",
        "services": services,
        "env_report": env,
        "before_xlens": before,
        "orders_before": orders_before,
        "command_plan": command_plan,
        "process_snapshot_before": process_snapshot(),
        "safety_contract": {
            "no_replay": True,
            "no_pnl": True,
            "no_paper_live": True,
            "no_broker_order": True,
            "observe_only_required": True,
            "no_fake_candidate_generation": True,
            "no_fake_risk_approval": True,
            "no_fake_execution_rows": True,
        },
    }

    if not env["safe"]:
        report["classification"] = "ABORT_ENV_NOT_SAFE"
        exit_code = 2
    elif args.execute and args.approval_text != REQUIRED_APPROVAL:
        report["classification"] = "ABORT_MISSING_EXACT_APPROVAL"
        exit_code = 3
    elif not args.execute:
        report["classification"] = "DRY_RUN_ONLY_NO_SERVICE_START"
        report["execute_command_for_future"] = command_plan["selected_command_shell"]
        report["after_xlens"] = stream_snapshot()
        report["orders_delta"] = report["after_xlens"].get("orders", 0) - orders_before
        exit_code = 0
    else:
        execute_result = execute_service_plan(command_plan, args.wait_seconds)
        after = stream_snapshot()
        orders_after = after.get("orders", 0)
        report.update(
            {
                "execute_result": execute_result,
                "after_xlens": after,
                "growth": {k: after.get(k, 0) - before.get(k, 0) for k in STREAMS},
                "orders_after": orders_after,
                "orders_delta": orders_after - orders_before,
                "process_snapshot_after": process_snapshot(),
            }
        )

        if orders_after - orders_before != 0:
            report["classification"] = "CRITICAL_ABORT_ORDER_STREAM_CHANGED"
            exit_code = 4
        elif execute_result.get("any_start_error"):
            report["classification"] = "START_PROCESS_LAUNCH_FAILED_ZERO_ORDER"
            exit_code = 5
        elif after.get("risk", 0) > 0 and after.get("execution", 0) > 0:
            report["classification"] = "RISK_EXECUTION_STREAMS_PRESENT"
            exit_code = 0
        else:
            report["classification"] = "STARTED_OR_ATTEMPTED_BUT_LIFECYCLE_STREAMS_NOT_CONFIRMED"
            exit_code = 6

    if args.json_out:
        pathlib.Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.json_out).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(
        json.dumps(
            {
                "classification": report.get("classification"),
                "mode": report.get("mode"),
                "env_safe": env["safe"],
                "before_xlens": before,
                "after_xlens": report.get("after_xlens"),
                "orders_delta": report.get("orders_delta"),
                "execute_command_for_future": report.get("execute_command_for_future"),
                "selection_reason": command_plan["hints"].get("selection_reason"),
                "uses_repeated_service_arg": command_plan.get("uses_repeated_service_arg"),
            },
            indent=2,
            sort_keys=True,
        )
    )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
