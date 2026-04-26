#!/usr/bin/env python3
from __future__ import annotations

import json
import time

from _batch25v_market_observation_common import (
    depth_from,
    hgetall_contract,
    member_from_json,
    option_present,
    proof_path,
    redis_client,
    safe_float,
    write_proof,
)


def main() -> int:
    client = redis_client()

    fut_const, fut_key, futures = hgetall_contract(
        client,
        "HASH_STATE_FUTURES_SNAPSHOT",
        "HASH_FUT_ACTIVE",
        "HASH_STATE_ACTIVE_FUTURES",
        "HASH_STATE_FUTURE_SNAPSHOT",
    )
    opt_const, opt_key, options = hgetall_contract(
        client,
        "HASH_STATE_SELECTED_OPTION_SNAPSHOT",
        "HASH_OPT_ACTIVE",
        "HASH_STATE_ACTIVE_SELECTED_OPTION",
        "HASH_STATE_DHAN_SELECTED_OPTION",
    )
    dhan_const, dhan_key, dhan_context = hgetall_contract(
        client,
        "HASH_STATE_DHAN_CONTEXT",
        "HASH_DHAN_CONTEXT",
        "HASH_STATE_OPTION_CONTEXT",
    )

    future_member = member_from_json(futures, "future_json")
    if not future_member:
        future_member = dict(futures)

    call_member = member_from_json(options, "selected_call_json")
    put_member = member_from_json(options, "selected_put_json")

    futures_depth = depth_from(futures) or depth_from(future_member)
    call_depth = depth_from(call_member)
    put_depth = depth_from(put_member)

    checks = {
        "futures_hash_present": bool(futures),
        "future_json_or_top_level_present": bool(future_member),
        "futures_ltp_present": safe_float(future_member.get("ltp"), 0.0) > 0.0,
        "futures_depth_consumed": futures_depth > 0.0,
        "missing_futures_data_not_considered_valid": not (not future_member and safe_float(future_member.get("ltp"), 0.0) > 0.0),
        "selected_option_hash_present": bool(options),
        "selected_call_json_present": bool(call_member),
        "selected_put_json_present": bool(put_member),
        "selected_call_present_during_market": option_present(call_member),
        "selected_put_present_during_market": option_present(put_member),
        "missing_call_data_not_considered_valid": not (not call_member and option_present(call_member)),
        "missing_put_data_not_considered_valid": not (not put_member and option_present(put_member)),
        "option_call_depth_consumed": call_depth > 0.0,
        "option_put_depth_consumed": put_depth > 0.0,
        "dhan_context_hash_present": bool(dhan_context),
    }

    ok = all(checks.values())

    proof = {
        "proof_name": "proof_market_session_feed_snapshot",
        "batch": "25V/26I",
        "generated_at_ns": time.time_ns(),
        "market_session_feed_snapshot_ok": ok,
        "hashes": {
            "futures": {"constant": fut_const, "key": fut_key},
            "options": {"constant": opt_const, "key": opt_key},
            "dhan_context": {"constant": dhan_const, "key": dhan_key},
        },
        "checks": checks,
        "observed": {
            "futures_depth_total": futures_depth,
            "call_depth_total": call_depth,
            "put_depth_total": put_depth,
            "future_member": future_member,
            "call_member": call_member,
            "put_member": put_member,
            "dhan_context_keys": sorted(dhan_context.keys()),
        },
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    out = proof_path("proof_market_session_feed_snapshot.json")
    write_proof(out, proof)
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
