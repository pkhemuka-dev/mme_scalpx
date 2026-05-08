#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import time
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o4_feed_snapshot_publication.json"

FUT_KEY = "state:snapshot:mme:fut:active"
OPT_KEY = "state:snapshot:mme:opt:selected:active"
DHAN_KEY = "state:context:mme:dhan"
HEALTH_FEEDS_KEY = "health:feeds"
PROVIDER_KEY = "state:provider:runtime"
POSITION_KEY = "state:position:mme"
ORDERS_STREAM = "orders:mme:stream"

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
        and "proof_or_publish_feed_snapshot_state.py" not in x
    ]

def is_flat(pos):
    return (
        pos.get("has_position") == "0"
        and pos.get("position_side") == "FLAT"
        and pos.get("qty_lots") == "0"
        and pos.get("qty_units") == "0"
    )

def jdump(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)

def fail_closed_future(ns):
    return {
        "role": "active",
        "provider_id": "",
        "instrument_key": "",
        "instrument_token": "",
        "trading_symbol": "",
        "ltp": 0.0,
        "best_bid": 0.0,
        "best_ask": 0.0,
        "bid_qty_5": 0,
        "ask_qty_5": 0,
        "depth_total": 0,
        "spread": 0.0,
        "spread_ratio": 0.0,
        "volume": 0,
        "oi": 0,
        "ts_event_ns": 0,
        "ts_local_ns": ns,
        "present": False,
        "fresh": False,
        "stale": True,
        "valid": False,
        "status": "UNAVAILABLE",
        "source": "batch26o4_fail_closed_baseline",
    }

def fail_closed_option(side, ns):
    return {
        "role": f"SELECTED_{side}",
        "side": side,
        "option_side": side,
        "provider_id": "DHAN",
        "instrument_key": "",
        "instrument_token": "",
        "option_token": "",
        "trading_symbol": "",
        "option_symbol": "",
        "strike": None,
        "ltp": None,
        "best_bid": None,
        "best_ask": None,
        "bid_qty_5": None,
        "ask_qty_5": None,
        "depth_total": None,
        "spread": None,
        "spread_ratio": None,
        "volume": None,
        "oi": None,
        "ts_event_ns": 0,
        "ts_local_ns": ns,
        "present": False,
        "fresh": False,
        "stale": True,
        "valid": False,
        "status": "UNAVAILABLE",
        "source": "batch26o4_fail_closed_baseline",
    }

def fail_closed_context(side):
    return {
        "side": side,
        "present": False,
        "fresh": False,
        "stale": True,
        "valid": False,
        "status": "UNAVAILABLE",
        "strike": None,
        "oi": None,
        "oi_change": None,
        "volume": None,
        "iv": None,
    }

def hmset(key, fields):
    args = ["HSET", key]
    for k, v in fields.items():
        args.extend([k, str(v)])
    return rcli(*args, timeout=8)

def required_present():
    fut = hgetall(FUT_KEY)
    opt = hgetall(OPT_KEY)
    dhan = hgetall(DHAN_KEY)
    health = hgetall(HEALTH_FEEDS_KEY)

    return {
        "futures_hash_present": bool(fut),
        "selected_option_hash_present": bool(opt),
        "dhan_context_hash_present": bool(dhan),
        "health_feeds_present": bool(health),
        "future_json_present": "future_json" in fut,
        "selected_call_json_present": "selected_call_json" in opt,
        "selected_put_json_present": "selected_put_json" in opt,
        "option_chain_ladder_json_present": "option_chain_ladder_json" in dhan,
        "strike_ladder_json_present": "strike_ladder_json" in dhan,
        "oi_wall_summary_json_present": "oi_wall_summary_json" in dhan,
        "selected_call_context_json_present": "selected_call_context_json" in dhan,
        "selected_put_context_json_present": "selected_put_context_json" in dhan,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    redis_ping = rcli("PING")
    orders_len = rcli("XLEN", ORDERS_STREAM)["stdout"]
    pos = hgetall(POSITION_KEY)
    provider = hgetall(PROVIDER_KEY)

    risk = pgrep("app.mme_scalpx.main --service risk")
    execution = pgrep("app.mme_scalpx.main --service execution")

    before = required_present()

    safe_to_publish = (
        redis_ping["ok"]
        and redis_ping["stdout"] == "PONG"
        and orders_len == "0"
        and is_flat(pos)
        and bool(provider)
        and len(risk) == 0
        and len(execution) == 0
    )

    write_performed = False
    write_results = {}

    if args.apply and safe_to_publish:
        ns = now_ns()
        future = fail_closed_future(ns)
        call = fail_closed_option("CALL", ns)
        put = fail_closed_option("PUT", ns)

        write_results["futures"] = hmset(FUT_KEY, {
            "future_json": jdump(future),
            "status": "UNAVAILABLE",
            "present": "False",
            "fresh": "False",
            "stale": "True",
            "valid": "False",
            "ts_event_ns": "0",
            "last_update_ns": ns,
        })

        write_results["options"] = hmset(OPT_KEY, {
            "selected_call_json": jdump(call),
            "selected_put_json": jdump(put),
            "status": "UNAVAILABLE",
            "present": "False",
            "fresh": "False",
            "stale": "True",
            "valid": "False",
            "ts_event_ns": "0",
            "last_update_ns": ns,
        })

        write_results["dhan_context"] = hmset(DHAN_KEY, {
            "option_chain_ladder_json": "[]",
            "strike_ladder_json": "[]",
            "oi_wall_summary_json": jdump({
                "present": False,
                "fresh": False,
                "stale": True,
                "valid": False,
                "status": "UNAVAILABLE",
                "oi_wall_ready": False,
                "ladder_size": 0,
            }),
            "selected_call_context_json": jdump(fail_closed_context("CALL")),
            "selected_put_context_json": jdump(fail_closed_context("PUT")),
            "status": "UNAVAILABLE",
            "present": "False",
            "fresh": "False",
            "stale": "True",
            "valid": "False",
            "last_update_ns": ns,
        })

        write_results["health_feeds"] = hmset(HEALTH_FEEDS_KEY, {
            "service_name": "feeds",
            "status": "WARN",
            "reason": "batch26o4_fail_closed_baseline_until_live_feed_updates",
            "ts_event_ns": ns,
            "last_update_ns": ns,
            "real_live_approved": "False",
            "paper_order_approved": "False",
        })

        write_performed = all(v.get("ok") for v in write_results.values())
    elif args.apply and not safe_to_publish:
        write_results["blocked"] = {"ok": False, "reason": "safe_to_publish_false"}
    else:
        write_results["proof_only"] = {"ok": True, "reason": "proof_only"}

    after = required_present()

    proof = {
        "batch": "26O4",
        "name": "feed_snapshot_publication",
        "created_at": now_iso(),
        "apply_requested": args.apply,
        "redis_ping": redis_ping["stdout"],
        "orders_len": orders_len,
        "position_flat": is_flat(pos),
        "provider_runtime_hash_present": bool(provider),
        "risk_process_count": len(risk),
        "execution_process_count": len(execution),
        "before": before,
        "safe_to_publish": safe_to_publish,
        "write_performed": write_performed,
        "write_results": write_results,
        "after": after,
        "real_live_approved": False,
        "paper_order_approved": False,
    }

    proof["futures_hash_present"] = after["futures_hash_present"]
    proof["selected_option_hash_present"] = after["selected_option_hash_present"]
    proof["selected_call_json_present"] = after["selected_call_json_present"]
    proof["selected_put_json_present"] = after["selected_put_json_present"]
    proof["dhan_context_hash_present"] = after["dhan_context_hash_present"]
    proof["health_feeds_present"] = after["health_feeds_present"]

    proof["feed_snapshot_publication_ok"] = (
        proof["redis_ping"] == "PONG"
        and proof["orders_len"] == "0"
        and proof["position_flat"]
        and proof["provider_runtime_hash_present"]
        and proof["risk_process_count"] == 0
        and proof["execution_process_count"] == 0
        and proof["futures_hash_present"]
        and proof["selected_option_hash_present"]
        and proof["selected_call_json_present"]
        and proof["selected_put_json_present"]
        and proof["dhan_context_hash_present"]
        and proof["health_feeds_present"]
    )

    if proof["feed_snapshot_publication_ok"]:
        proof["final_verdict"] = "PASS_FEED_SNAPSHOT_PUBLICATION_OK"
        proof["next_required_batch"] = "Batch 26-O5 stream/key topology reconciliation"
    elif safe_to_publish and not args.apply:
        proof["final_verdict"] = "PARTIAL_SAFE_TO_PUBLISH_RERUN_WITH_APPLY"
        proof["next_required_batch"] = ".venv/bin/python bin/proof_or_publish_feed_snapshot_state.py --apply"
    else:
        proof["final_verdict"] = "FAIL_FEED_SNAPSHOT_PUBLICATION_REVIEW_REQUIRED"
        proof["next_required_batch"] = "Review O4 blockers"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "feed_snapshot_publication_ok": proof["feed_snapshot_publication_ok"],
        "safe_to_publish": proof["safe_to_publish"],
        "write_performed": proof["write_performed"],
        "futures_hash_present": proof["futures_hash_present"],
        "selected_option_hash_present": proof["selected_option_hash_present"],
        "selected_call_json_present": proof["selected_call_json_present"],
        "selected_put_json_present": proof["selected_put_json_present"],
        "dhan_context_hash_present": proof["dhan_context_hash_present"],
        "health_feeds_present": proof["health_feeds_present"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["final_verdict"].startswith(("PASS", "PARTIAL_SAFE")) else 1

if __name__ == "__main__":
    raise SystemExit(main())
