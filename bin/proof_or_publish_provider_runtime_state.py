#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o3_provider_runtime_publication.json"

PROVIDER_KEY = "state:provider:runtime"
ORDERS_STREAM = "orders:mme:stream"
POSITION_KEY = "state:position:mme"

REQUIRED = [
    "futures_marketdata_provider_id",
    "selected_option_marketdata_provider_id",
    "option_context_provider_id",
    "execution_primary_provider_id",
    "execution_fallback_provider_id",
    "futures_marketdata_status",
    "selected_option_marketdata_status",
    "option_context_status",
    "execution_primary_status",
    "execution_fallback_status",
    "family_runtime_mode",
    "active_futures_provider_id",
    "active_selected_option_provider_id",
    "active_option_context_provider_id",
    "active_execution_provider_id",
    "provider_ready_classic",
    "provider_ready_miso",
    "last_update_ns",
    "ts_event_ns",
]

BASELINE = {
    "futures_marketdata_provider_id": "ZERODHA",
    "selected_option_marketdata_provider_id": "DHAN",
    "option_context_provider_id": "DHAN",
    "execution_primary_provider_id": "ZERODHA",
    "execution_fallback_provider_id": "DHAN",

    "futures_marketdata_status": "UNAVAILABLE",
    "selected_option_marketdata_status": "UNAVAILABLE",
    "option_context_status": "UNAVAILABLE",
    "execution_primary_status": "UNAVAILABLE",
    "execution_fallback_status": "UNAVAILABLE",

    "family_runtime_mode": "OBSERVE_ONLY",
    "failover_mode": "MANUAL",
    "override_mode": "AUTO",
    "transition_reason": "BOOTSTRAP",
    "provider_transition_seq": "0",
    "failover_active": "False",
    "pending_failover": "False",

    "active_futures_provider_id": "ZERODHA",
    "active_selected_option_provider_id": "DHAN",
    "active_option_context_provider_id": "DHAN",
    "active_execution_provider_id": "ZERODHA",
    "fallback_execution_provider_id": "DHAN",

    "provider_runtime_mode": "",
    "futures_provider_status": "UNAVAILABLE",
    "selected_option_provider_status": "UNAVAILABLE",
    "option_context_provider_status": "UNAVAILABLE",
    "execution_provider_status": "UNAVAILABLE",
    "execution_fallback_provider_status": "UNAVAILABLE",

    "provider_ready_classic": "False",
    "provider_ready_miso": "False",
    "provider_runtime_blocked": "True",
    "provider_runtime_block_reason": "fail_closed_baseline_until_live_provider_updates",
    "provider_runtime_missing_keys": "",
    "message": "",
}

def now_ns() -> str:
    return str(time.time_ns())

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

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
    return [
        x for x in out
        if "pgrep -af" not in x
        and "proof_or_publish_provider_runtime_state.py" not in x
    ]

def is_position_flat(d):
    return (
        d.get("has_position") == "0"
        and d.get("position_side") == "FLAT"
        and d.get("qty_lots") == "0"
        and d.get("qty_units") == "0"
    )

def required_missing(d):
    return [k for k in REQUIRED if k not in d or d.get(k) in ("", None)]

def observe_only_or_non_promoted(d):
    mode = str(d.get("family_runtime_mode", ""))
    real_live_allowed = str(d.get("real_live_allowed", "False")).lower() == "true"
    return mode in ("OBSERVE_ONLY", "PAPER_ONLY", "CONTROLLED_PAPER") and not real_live_allowed

def derive_readiness(d):
    classic = (
        d.get("futures_marketdata_status") in ("HEALTHY", "READY")
        and d.get("selected_option_marketdata_status") in ("HEALTHY", "READY")
        and d.get("execution_primary_status") in ("HEALTHY", "READY", "AVAILABLE")
    )
    miso = (
        d.get("selected_option_marketdata_status") in ("HEALTHY", "READY")
        and d.get("option_context_status") in ("HEALTHY", "READY")
        and d.get("execution_primary_status") in ("HEALTHY", "READY", "AVAILABLE")
    )
    return classic, miso

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    redis_ping = rcli("PING")
    orders_len = rcli("XLEN", ORDERS_STREAM)["stdout"]
    position = hgetall(POSITION_KEY)

    risk = pgrep("app.mme_scalpx.main --service risk")
    execution = pgrep("app.mme_scalpx.main --service execution")

    before = hgetall(PROVIDER_KEY)
    before_missing = required_missing(before)

    safe_to_publish = (
        redis_ping["ok"]
        and redis_ping["stdout"] == "PONG"
        and orders_len == "0"
        and is_position_flat(position)
        and len(risk) == 0
        and len(execution) == 0
    )

    write_performed = False
    write_result = {"ok": False, "reason": "not_attempted"}

    if args.apply and safe_to_publish:
        values = dict(BASELINE)

        # Preserve existing provider statuses if a partial runtime already exists.
        for k in before:
            if k in values or k in REQUIRED:
                values[k] = before[k]

        # Force safety invariants.
        values["family_runtime_mode"] = values.get("family_runtime_mode") or "OBSERVE_ONLY"
        if values["family_runtime_mode"] not in ("OBSERVE_ONLY", "PAPER_ONLY", "CONTROLLED_PAPER"):
            values["family_runtime_mode"] = "OBSERVE_ONLY"

        classic, miso = derive_readiness(values)
        values["provider_ready_classic"] = str(bool(classic))
        values["provider_ready_miso"] = str(bool(miso))

        missing_after_fill = [k for k in REQUIRED if k not in values or values.get(k) in ("", None)]
        values["provider_runtime_missing_keys"] = ",".join(missing_after_fill)
        values["provider_runtime_blocked"] = str(bool(missing_after_fill or not (classic or miso)))
        if missing_after_fill:
            values["provider_runtime_block_reason"] = "missing_required_provider_runtime_keys:" + ",".join(missing_after_fill)
        elif not (classic or miso):
            values["provider_runtime_block_reason"] = "providers_not_ready_fail_closed"
        else:
            values["provider_runtime_block_reason"] = ""

        ns = now_ns()
        values["last_update_ns"] = ns
        values["ts_event_ns"] = ns

        redis_args = ["HSET", PROVIDER_KEY]
        for k, v in values.items():
            redis_args.extend([k, str(v)])
        write_result = rcli(*redis_args, timeout=8)
        write_performed = bool(write_result["ok"])
    elif args.apply and not safe_to_publish:
        write_result = {"ok": False, "reason": "safe_to_publish_false"}
    else:
        write_result = {"ok": True, "reason": "proof_only"}

    after = hgetall(PROVIDER_KEY)
    after_missing = required_missing(after)

    proof = {
        "batch": "26O3",
        "name": "provider_runtime_publication",
        "created_at": now_iso(),
        "apply_requested": args.apply,
        "redis_ping": redis_ping["stdout"],
        "orders_len": orders_len,
        "position_flat": is_position_flat(position),
        "risk_process_count": len(risk),
        "execution_process_count": len(execution),
        "before_provider_runtime": before,
        "before_missing_required": before_missing,
        "safe_to_publish": safe_to_publish,
        "write_performed": write_performed,
        "write_result": write_result,
        "after_provider_runtime": after,
        "after_missing_required": after_missing,
        "provider_runtime_hash_present": bool(after),
        "provider_runtime_required_keys_present": len(after_missing) == 0,
        "observe_only_or_non_promoted_mode": observe_only_or_non_promoted(after),
        "provider_ready_classic": after.get("provider_ready_classic"),
        "provider_ready_miso": after.get("provider_ready_miso"),
        "real_live_approved": False,
        "paper_order_approved": False,
    }

    proof["provider_runtime_publication_ok"] = (
        proof["redis_ping"] == "PONG"
        and proof["orders_len"] == "0"
        and proof["position_flat"]
        and proof["risk_process_count"] == 0
        and proof["execution_process_count"] == 0
        and proof["provider_runtime_hash_present"]
        and proof["provider_runtime_required_keys_present"]
        and proof["observe_only_or_non_promoted_mode"]
        and proof["real_live_approved"] is False
    )

    if proof["provider_runtime_publication_ok"]:
        proof["final_verdict"] = "PASS_PROVIDER_RUNTIME_PUBLICATION_OK"
        proof["next_required_batch"] = "Batch 26-O4 feed snapshot publication repair"
    elif safe_to_publish and not args.apply:
        proof["final_verdict"] = "PARTIAL_SAFE_TO_PUBLISH_RERUN_WITH_APPLY"
        proof["next_required_batch"] = ".venv/bin/python bin/proof_or_publish_provider_runtime_state.py --apply"
    else:
        proof["final_verdict"] = "FAIL_PROVIDER_RUNTIME_PUBLICATION_REVIEW_REQUIRED"
        proof["next_required_batch"] = "Review O3 blockers"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "provider_runtime_publication_ok": proof["provider_runtime_publication_ok"],
        "safe_to_publish": proof["safe_to_publish"],
        "write_performed": proof["write_performed"],
        "provider_runtime_hash_present": proof["provider_runtime_hash_present"],
        "provider_runtime_required_keys_present": proof["provider_runtime_required_keys_present"],
        "observe_only_or_non_promoted_mode": proof["observe_only_or_non_promoted_mode"],
        "provider_ready_classic": proof["provider_ready_classic"],
        "provider_ready_miso": proof["provider_ready_miso"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["final_verdict"].startswith(("PASS", "PARTIAL_SAFE")) else 1

if __name__ == "__main__":
    raise SystemExit(main())
