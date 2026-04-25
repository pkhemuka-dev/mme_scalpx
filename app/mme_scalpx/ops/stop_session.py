#!/usr/bin/env python3
from __future__ import annotations

"""
ops/stop_session.py

Deterministic shutdown orchestrator for ScalpX MME.

Batch 15 freeze rule
--------------------
CMD_SET_MODE accepts control modes only. execution-only mode is not a control mode and is
not published by this tool.
"""

import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional


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


def _run(cmd: list[str]) -> int:
    print("RUN", " ".join(cmd))
    completed = subprocess.run(cmd, check=False)
    return int(completed.returncode)


def _publish_command(
    command_type: str,
    *,
    reason: str | None = None,
    mode: str | None = None,
    dry_run: bool = False,
) -> None:
    cmd = [
        _python_executable(),
        "-m",
        "app.mme_scalpx.ops.ops_cmd",
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
        "app.mme_scalpx.ops.healthcheck",
    ]
    if strict:
        cmd.append("--strict")
    rc = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"healthcheck failed with exit code {rc}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic shutdown orchestrator for ScalpX MME."
    )
    parser.add_argument("--systemd", action="store_true")
    parser.add_argument("--pause-trading", action="store_true")
    parser.add_argument("--force-flatten", action="store_true")
    parser.add_argument(
        "--set-safe-mode",
        action="store_true",
        help="Publish SET_MODE SAFE before stopping.",
    )
    parser.add_argument("--verify-health", action="store_true")
    parser.add_argument("--strict-health", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reason", default="operator_stop_session")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.pause_trading:
        _publish_command("PAUSE_TRADING", reason=args.reason, dry_run=args.dry_run)

    if args.force_flatten:
        _publish_command("FORCE_FLATTEN", reason=args.reason, dry_run=args.dry_run)

    if args.set_safe_mode:
        _publish_command("SET_MODE", mode="SAFE", reason=args.reason, dry_run=args.dry_run)

    if args.systemd:
        if args.dry_run:
            print("DRY_RUN     systemd stop skipped")
        else:
            _stop_via_systemd()

    if args.verify_health:
        _run_healthcheck(strict=bool(args.strict_health))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
