"""
Fail-closed controlled-paper status publication.

Purpose:
- Publish visible runtime status for controlled-paper gate checks.
- Default is always fail-closed.
- Does not arm paper.
- Does not send orders.
- Does not start risk/execution.
- Does not delete Redis keys.

This module writes only HSET status keys through redis-cli.
"""
from app.mme_scalpx.services.strategy_family.position_exit_manager import normalize_controlled_paper_projected_exit_side

import argparse
import json
import os
import subprocess
import time
from typing import Dict, List, Tuple


SOURCE = "R6_FAIL_CLOSED_STATUS_PUBLICATION"

POSITION_KEY = "state:position:mme"
RISK_KEY = "state:risk"
EXECUTION_KEY = "state:execution"

PAPER_GATE_KEYS = [
    "state:controlled_paper:gate",
    "state:paper_gate:mme",
    "state:paper:mme",
    "state:pstatus:mme",
    "state:route:mme",
]


def _now() -> str:
    return str(time.time())


def fail_closed_payload(reason: str = "CONTROLLED_PAPER_NOT_ARMED") -> Dict[str, Dict[str, str]]:
    ts = _now()

    position = {
        "source": SOURCE,
        "ts_epoch": ts,
        "has_position": "0",
        "position_side": normalize_controlled_paper_projected_exit_side("FLAT"),
        "qty_lots": "0",
        "qty_units": "0",
        "symbol": "",
        "instrument_token": "",
        "avg_price": "0",
    }

    risk = {
        "source": SOURCE,
        "ts_epoch": ts,
        "reason_code": reason,
        "controlled_paper_veto_reason": reason,
        "controlled_paper_entry_veto": "1",
        "veto_entries": "1",
        "position_open": "0",
        "trades_today": "0",
        "day_realized_pnl": "0",
        "max_loss_hit": "0",
        "risk_state": "FAIL_CLOSED",
    }

    execution = {
        "source": SOURCE,
        "ts_epoch": ts,
        "entry_pending": "0",
        "exit_pending": "0",
        "pending_order_json": "",
        "last_error": "",
        "execution_state": "IDLE_FAIL_CLOSED",
        "broker_order_enabled": "0",
        "real_order_enabled": "0",
    }

    paper_gate = {
        "source": SOURCE,
        "ts_epoch": ts,
        "paper_armed": "false",
        "route_allowed": "false",
        "paper_allowed": "false",
        "reason_code": reason,
        "controlled_paper_status": "FAIL_CLOSED",
        "requires_explicit_user_approval": "true",
    }

    payload = {
        POSITION_KEY: position,
        RISK_KEY: risk,
        EXECUTION_KEY: execution,
    }
    for key in PAPER_GATE_KEYS:
        payload[key] = dict(paper_gate)
    return payload


def _hset_cmd(key: str, fields: Dict[str, str]) -> List[str]:
    cmd = ["redis-cli", "HSET", key]
    for k, v in fields.items():
        cmd.extend([str(k), str(v)])
    return cmd


def publish_fail_closed_status(dry_run: bool = True, reason: str = "CONTROLLED_PAPER_NOT_ARMED") -> Dict[str, object]:
    payload = fail_closed_payload(reason=reason)
    commands: List[List[str]] = []
    results: List[Dict[str, object]] = []

    for key, fields in payload.items():
        cmd = _hset_cmd(key, fields)
        commands.append(cmd)
        if dry_run:
            results.append({"key": key, "dry_run": True, "cmd": cmd})
        else:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            results.append({
                "key": key,
                "dry_run": False,
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            })

    return {
        "source": SOURCE,
        "dry_run": dry_run,
        "reason": reason,
        "keys": sorted(payload.keys()),
        "payload": payload,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish fail-closed controlled-paper status.")
    parser.add_argument("--publish", action="store_true", help="Actually write fail-closed status to Redis.")
    parser.add_argument("--reason", default="CONTROLLED_PAPER_NOT_ARMED")
    args = parser.parse_args()

    out = publish_fail_closed_status(dry_run=(not args.publish), reason=args.reason)
    print(json.dumps(out, indent=2, sort_keys=True))

    if args.publish:
        for rec in out["results"]:
            if int(rec.get("returncode", 0)) != 0:
                return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
