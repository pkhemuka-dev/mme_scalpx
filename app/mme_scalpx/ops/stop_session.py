"""
app/mme_scalpx/ops/stop_session.py

Frozen-grade shutdown orchestrator for ScalpX MME.

Purpose
-------
Perform deterministic session shutdown in a controlled order:

1. optionally publish pause-trading command
2. optionally publish force-flatten command
3. optionally stop the canonical runtime via systemd
4. optionally verify post-stop health snapshot

Design rules
------------
- explicit launch mode; no hidden fallback behavior
- shutdown commands are optional and operator-controlled
- no ad hoc shell tricks
- safe dry-run mode for command publication path
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from typing import List, Optional


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value if value != "" else None


def _python_executable() -> str:
    current = sys.executable.strip()
    if current:
        return current
    return "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python"


def _run(cmd: List[str]) -> int:
    print("RUN", " ".join(cmd))
    completed = subprocess.run(cmd, check=False)
    return int(completed.returncode)


def _publish_command(command_type: str, *, reason: str | None = None, mode: str | None = None, dry_run: bool = False) -> None:
    cmd = [
        _python_executable(),
        "-m",
        "mme_scalpx.ops.ops_cmd",
        command_type,
    ]
    if reason:
        cmd.extend(["--reason", reason])
    if mode:
        cmd.extend(["--mode", mode])
    if dry_run:
        cmd.append("--dry-run")

    rc = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"ops_cmd failed for {command_type} with exit code {rc}")


def _require_systemctl() -> str:
    systemctl = shutil.which("systemctl")
    if systemctl is None:
        raise RuntimeError("systemctl not found on PATH; cannot use --systemd")
    return systemctl


def _systemd_is_active(systemctl: str, unit: str) -> bool:
    completed = subprocess.run(
        [systemctl, "is-active", unit],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def _stop_via_systemd() -> None:
    systemctl = _require_systemctl()
    unit = _env("SCALPX_SYSTEMD_MAIN_UNIT", "scalpx-mme.service")
    if unit is None:
        raise RuntimeError("SCALPX_SYSTEMD_MAIN_UNIT is empty")

    if not _systemd_is_active(systemctl, unit):
        print(f"INFO runtime unit already inactive: {unit}")
        return

    rc = _run([systemctl, "stop", unit])
    if rc != 0:
        raise RuntimeError(f"systemctl stop {unit} failed with exit code {rc}")


def _run_healthcheck(strict: bool) -> None:
    cmd = [
        _python_executable(),
        "-m",
        "mme_scalpx.ops.healthcheck",
    ]
    if strict:
        cmd.append("--strict")
    rc = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"healthcheck failed with exit code {rc}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic shutdown orchestrator for ScalpX MME."
    )

    parser.add_argument(
        "--systemd",
        action="store_true",
        help="Stop the runtime through the systemd main unit.",
    )
    parser.add_argument(
        "--pause-trading",
        action="store_true",
        help="Publish PAUSE_TRADING before shutdown.",
    )
    parser.add_argument(
        "--force-flatten",
        action="store_true",
        help="Publish FORCE_FLATTEN before shutdown.",
    )
    parser.add_argument(
        "--set-exit-only",
        action="store_true",
        help="Publish SET_MODE EXIT_ONLY before shutdown.",
    )
    parser.add_argument(
        "--reason",
        default="session shutdown",
        help="Reason attached to operator commands.",
    )
    parser.add_argument(
        "--dry-run-commands",
        action="store_true",
        help="Dry-run command publication without writing to Redis.",
    )
    parser.add_argument(
        "--healthcheck-after-stop",
        action="store_true",
        help="Run healthcheck after shutdown sequence.",
    )
    parser.add_argument(
        "--strict-healthcheck",
        action="store_true",
        help="Treat post-stop healthcheck warnings as failures.",
    )

    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    print("STOP_SESSION")
    print(f"  systemd={int(args.systemd)}")
    print(f"  pause_trading={int(args.pause_trading)}")
    print(f"  set_exit_only={int(args.set_exit_only)}")
    print(f"  force_flatten={int(args.force_flatten)}")
    print(f"  dry_run_commands={int(args.dry_run_commands)}")
    print(f"  healthcheck_after_stop={int(args.healthcheck_after_stop)}")
    print(f"  strict_healthcheck={int(args.strict_healthcheck)}")

    if args.pause_trading:
        _publish_command(
            "PAUSE_TRADING",
            reason=args.reason,
            dry_run=args.dry_run_commands,
        )

    if args.set_exit_only:
        _publish_command(
            "SET_MODE",
            reason=args.reason,
            mode="EXIT_ONLY",
            dry_run=args.dry_run_commands,
        )

    if args.force_flatten:
        _publish_command(
            "FORCE_FLATTEN",
            reason=args.reason,
            dry_run=args.dry_run_commands,
        )

    if args.systemd:
        _stop_via_systemd()

    if args.healthcheck_after_stop:
        _run_healthcheck(strict=args.strict_healthcheck)

    print("STOP_SESSION_DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
