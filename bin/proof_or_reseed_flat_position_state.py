#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o2_position_flat_reseed_guard.json"

POSITION_KEY = "state:position:mme"
ORDERS_STREAM = "orders:mme:stream"

FLAT_FIELDS = {
    "has_position": "0",
    "position_side": "FLAT",
    "qty_lots": "0",
    "qty_units": "0",
    "avg_price": "",
    "entry_ts_ns": "",
    "entry_option_symbol": "",
    "entry_option_token": "",
    "entry_strike": "",
    "entry_mode": "",
    "decision_id": "",
    "broker_order_id": "",
    "mark_price": "",
    "realized_pnl_day": "0",
}

def cmd(args, timeout=5):
    try:
        cp = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "ok": cp.returncode == 0,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
            "returncode": cp.returncode,
        }
    except Exception as exc:
        return {"ok": False, "stdout": "", "stderr": repr(exc), "returncode": -1}

def rcli(*args, timeout=5):
    return cmd(["redis-cli", *args], timeout=timeout)

def hgetall(key):
    raw = rcli("HGETALL", key)["stdout"].splitlines()
    d = {}
    for i in range(0, len(raw) - 1, 2):
        d[raw[i]] = raw[i + 1]
    return d

def pgrep(pattern):
    out = cmd(["bash", "-lc", f"pgrep -af {pattern!r} || true"])["stdout"].splitlines()
    return [x for x in out if "pgrep -af" not in x and "proof_or_reseed_flat_position_state.py" not in x]

def is_flat(d):
    return (
        d.get("has_position") == "0"
        and d.get("position_side") == "FLAT"
        and d.get("qty_lots") == "0"
        and d.get("qty_units") == "0"
    )

def main():
    apply = "--apply" in sys.argv

    redis_ping = rcli("PING")
    orders_len = rcli("XLEN", ORDERS_STREAM)["stdout"]
    before = hgetall(POSITION_KEY)

    risk = pgrep("app.mme_scalpx.main --service risk")
    execution = pgrep("app.mme_scalpx.main --service execution")

    latest_order = cmd(
        ["bash", "-lc", f"redis-cli XREVRANGE {ORDERS_STREAM!r} + - COUNT 1 | sed -n '1,80p'"],
        timeout=5,
    )["stdout"]

    before_flat = is_flat(before)
    before_empty = not bool(before)

    suspicious_before = {
        k: before.get(k, "")
        for k in ["broker_order_id", "decision_id", "entry_option_symbol", "entry_option_token", "entry_strike"]
        if before.get(k, "")
    }

    safe_to_reseed = (
        redis_ping["ok"]
        and redis_ping["stdout"] == "PONG"
        and orders_len == "0"
        and not latest_order.strip()
        and len(risk) == 0
        and len(execution) == 0
        and not suspicious_before
        and (before_empty or before_flat)
    )

    write_performed = False
    write_result = {"ok": False, "reason": "not_attempted"}

    if apply and safe_to_reseed and (before_empty or not before_flat):
        args = ["HSET", POSITION_KEY]
        for k, v in FLAT_FIELDS.items():
            args.extend([k, v])
        write_result = rcli(*args)
        write_performed = bool(write_result["ok"])
    elif apply and before_flat:
        write_result = {"ok": True, "reason": "already_flat"}
    elif not apply:
        write_result = {"ok": True, "reason": "proof_only"}

    after = hgetall(POSITION_KEY)
    after_flat = is_flat(after)

    proof = {
        "batch": "26O2",
        "name": "position_flat_reseed_guard",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "apply_requested": apply,
        "redis_ping": redis_ping["stdout"],
        "orders_len": orders_len,
        "latest_order_empty": not bool(latest_order.strip()),
        "risk_process_count": len(risk),
        "execution_process_count": len(execution),
        "before_position": before,
        "before_empty": before_empty,
        "before_flat": before_flat,
        "suspicious_before": suspicious_before,
        "safe_to_reseed": safe_to_reseed,
        "write_performed": write_performed,
        "write_result": write_result,
        "after_position": after,
        "position_hash_present": bool(after),
        "position_flat": after_flat,
        "orders_zero": orders_len == "0",
        "real_live_approved": False,
        "paper_order_approved": False,
    }

    proof["position_flat_guard_ok"] = (
        proof["redis_ping"] == "PONG"
        and proof["orders_zero"]
        and proof["latest_order_empty"]
        and proof["risk_process_count"] == 0
        and proof["execution_process_count"] == 0
        and proof["position_hash_present"]
        and proof["position_flat"]
    )

    if proof["position_flat_guard_ok"]:
        proof["final_verdict"] = "PASS_POSITION_FLAT_GUARD_OK"
        proof["next_required_batch"] = "Batch 26-O3 provider runtime publication repair"
    elif safe_to_reseed and not apply:
        proof["final_verdict"] = "PARTIAL_SAFE_TO_RESEED_RERUN_WITH_APPLY"
        proof["next_required_batch"] = "Run: .venv/bin/python bin/proof_or_reseed_flat_position_state.py --apply"
    else:
        proof["final_verdict"] = "FAIL_POSITION_FLAT_GUARD_REVIEW_REQUIRED"
        proof["next_required_batch"] = "Review blockers before proceeding"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "position_flat_guard_ok": proof["position_flat_guard_ok"],
        "safe_to_reseed": proof["safe_to_reseed"],
        "write_performed": proof["write_performed"],
        "orders_zero": proof["orders_zero"],
        "position_hash_present": proof["position_hash_present"],
        "position_flat": proof["position_flat"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["final_verdict"].startswith(("PASS", "PARTIAL_SAFE")) else 1

if __name__ == "__main__":
    raise SystemExit(main())
