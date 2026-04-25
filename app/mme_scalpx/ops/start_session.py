"""
app/mme_scalpx/ops/start_session.py

Frozen-grade startup orchestrator for ScalpX MME.

Purpose
-------
Perform deterministic session startup in a controlled order:

1. validate environment / filesystem / Redis readiness via preflight
2. optionally bootstrap Redis consumer groups
3. start the canonical runtime via either:
   - systemd unit, or
   - direct foreground python module execution

Design rules
------------
- explicit launch mode; no hidden fallback behavior
- preflight first unless explicitly disabled
- optional group bootstrap controlled by env/flag
- no command-stream writes
- no ad hoc shell tricks
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


def _env_bool(name: str, default: bool) -> bool:
    raw = _env(name)
    if raw is None:
        return default
    lowered = raw.lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"invalid boolean for {name}: {raw!r}")


def _run(cmd: List[str], *, replace_process: bool = False) -> int:
    print("RUN", " ".join(cmd))
    if replace_process:
        os.execvp(cmd[0], cmd)
        raise RuntimeError("os.execvp returned unexpectedly")
    completed = subprocess.run(cmd, check=False)
    return int(completed.returncode)


def _python_executable() -> str:
    current = sys.executable.strip()
    if current:
        return current
    return "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python"


def _run_preflight(strict: bool) -> None:
    cmd = [
        _python_executable(),
        "-m",
        "app.mme_scalpx.ops.preflight",
    ]
    if strict:
        cmd.append("--strict")
    rc = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"preflight failed with exit code {rc}")


def _run_bootstrap_groups(start_id: str) -> None:
    cmd = [
        _python_executable(),
        "-m",
        "app.mme_scalpx.ops.bootstrap_groups",
        "--start-id",
        start_id,
    ]
    rc = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"bootstrap_groups failed with exit code {rc}")


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


def _start_via_systemd(*, restart: bool) -> None:
    systemctl = _require_systemctl()
    unit = _env("SCALPX_SYSTEMD_MAIN_UNIT", "scalpx-mme.service")
    if unit is None:
        raise RuntimeError("SCALPX_SYSTEMD_MAIN_UNIT is empty")

    if _systemd_is_active(systemctl, unit):
        if restart:
            rc = _run([systemctl, "restart", unit])
            if rc != 0:
                raise RuntimeError(f"systemctl restart {unit} failed with exit code {rc}")
            return
        print(f"INFO runtime unit already active: {unit}")
        return

    rc = _run([systemctl, "start", unit])
    if rc != 0:
        raise RuntimeError(f"systemctl start {unit} failed with exit code {rc}")


def _start_direct_foreground() -> None:
    cmd = [
        _python_executable(),
        "-m",
        "app.mme_scalpx.main",
    ]
    _run(cmd, replace_process=True)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic startup orchestrator for ScalpX MME."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--systemd",
        action="store_true",
        help="Start the runtime through the systemd main unit.",
    )
    mode.add_argument(
        "--direct",
        action="store_true",
        help="Start the runtime directly in the current foreground process.",
    )

    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip preflight even if env requests it. Use only for controlled troubleshooting.",
    )
    parser.add_argument(
        "--strict-preflight",
        action="store_true",
        help="Treat preflight warnings as failures.",
    )
    parser.add_argument(
        "--bootstrap-groups",
        action="store_true",
        help="Force consumer-group bootstrap before startup.",
    )
    parser.add_argument(
        "--skip-bootstrap-groups",
        action="store_true",
        help="Skip group bootstrap even if env requests it.",
    )
    parser.add_argument(
        "--bootstrap-start-id",
        default="0",
        help="Start ID for bootstrap_groups.py. Default: 0",
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        help="When using --systemd, restart the main unit if already active.",
    )

    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    env_run_preflight = _env_bool("SCALPX_RUN_PREFLIGHT_ON_START", True)
    env_bootstrap_groups = _env_bool("SCALPX_BOOTSTRAP_GROUPS_ON_START", False)

    should_run_preflight = env_run_preflight and not args.skip_preflight
    should_bootstrap_groups = (
        (env_bootstrap_groups or args.bootstrap_groups)
        and not args.skip_bootstrap_groups
    )

    print("START_SESSION")
    print(f"  mode={'systemd' if args.systemd else 'direct'}")
    print(f"  run_preflight={int(should_run_preflight)}")
    print(f"  strict_preflight={int(args.strict_preflight)}")
    print(f"  bootstrap_groups={int(should_bootstrap_groups)}")
    print(f"  bootstrap_start_id={args.bootstrap_start_id!r}")
    print(f"  restart={int(args.restart)}")

    if should_run_preflight:
        _run_preflight(strict=args.strict_preflight)

    if should_bootstrap_groups:
        if args.bootstrap_start_id.strip() == "":
            raise RuntimeError("--bootstrap-start-id must not be empty")
        _run_bootstrap_groups(start_id=args.bootstrap_start_id.strip())

    if args.systemd:
        _start_via_systemd(restart=args.restart)
        print("STARTED via systemd")
        return 0

    _start_direct_foreground()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
