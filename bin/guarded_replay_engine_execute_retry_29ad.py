#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "etc" / "replay" / "parity" / "guarded_dry_run_cli_contract_repair_29ad.json"

def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    args = cfg["dry_run_args"]
    dry_run = ROOT / "bin" / "guarded_replay_engine_execute_dry_run_29g.py"

    env = os.environ.copy()
    env.update({
        "MME_SCALPX_OFFLINE_ONLY": "1",
        "MME_SCALPX_NO_BROKER_IO": "1",
        "MME_SCALPX_NO_LIVE_REDIS": "1",
        "MME_SCALPX_NO_ORDER_SEND": "1",
        "MME_SCALPX_NO_PAPER_LIVE": "1",
        "SCALPX_REPLAY_GUARDED_DRY_RUN": "1",
        "SCALPX_REPLAY_NO_LIVE_IO": "1",
        "BATCH29AD_WRAPPER": "1",
    })

    cmd = [sys.executable, str(dry_run)] + args
    cp = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=180, env=env)

    out_dir = pathlib.Path(cfg["resolved_roots"]["output_root"])
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "29ad_wrapper_stdout.txt").write_text(cp.stdout, encoding="utf-8")
    (out_dir / "29ad_wrapper_stderr.txt").write_text(cp.stderr, encoding="utf-8")
    (out_dir / "29ad_wrapper_command.json").write_text(json.dumps({
        "cmd": cmd,
        "returncode": cp.returncode,
    }, indent=2), encoding="utf-8")

    sys.stdout.write(cp.stdout)
    sys.stderr.write(cp.stderr)
    return cp.returncode

if __name__ == "__main__":
    raise SystemExit(main())
