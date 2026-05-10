#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
WATCH_DIR = ROOT / "run/watchdog"
WATCH_DIR.mkdir(parents=True, exist_ok=True)


def sh(cmd: list[str], timeout: int = 40) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired as e:
        return 124, f"TIMEOUT: {' '.join(cmd)}: {e}"
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"


def run_once(repair: bool) -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rc, out = sh([str(ROOT / "bin/phealth_safe.py")], timeout=35)
    event = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "health_returncode": rc,
        "repair_enabled": repair,
        "health_raw": out,
        "repair_attempted": False,
        "repair_returncode": None,
        "repair_raw": None,
    }

    verdict = "UNKNOWN"
    safe = False
    try:
        payload = json.loads(out)
        verdict = payload.get("verdict", "UNKNOWN")
        safe = bool(payload.get("safe_to_autorepair"))
    except Exception:
        pass

    event["health_verdict"] = verdict
    event["safe_to_autorepair"] = safe

    if verdict == "GREEN":
        event["final_verdict"] = "GREEN_NO_ACTION"
        path = WATCH_DIR / f"watchdog_{stamp}_green.json"
        path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n")
        print(json.dumps(event, indent=2, sort_keys=True))
        return 0

    if repair and safe:
        rc_r, out_r = sh([str(ROOT / "bin/prepair_safe.py")], timeout=120)
        event["repair_attempted"] = True
        event["repair_returncode"] = rc_r
        event["repair_raw"] = out_r
        event["final_verdict"] = "REPAIR_ATTEMPTED"
        path = WATCH_DIR / f"watchdog_{stamp}_repair.json"
        path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n")
        print(json.dumps(event, indent=2, sort_keys=True))
        return 0 if rc_r == 0 else 2

    event["final_verdict"] = "OPERATOR_REQUIRED"
    path = WATCH_DIR / f"watchdog_{stamp}_operator_required.json"
    path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n")
    print(json.dumps(event, indent=2, sort_keys=True))
    return 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="Run one check/repair pass and exit")
    ap.add_argument("--repair-safe", action="store_true", help="Allow bounded feed-only repair")
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--max-loops", type=int, default=0)
    args = ap.parse_args()

    if args.once:
        return run_once(repair=args.repair_safe)

    loops = 0
    while True:
        run_once(repair=args.repair_safe)
        loops += 1
        if args.max_loops and loops >= args.max_loops:
            return 0
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
