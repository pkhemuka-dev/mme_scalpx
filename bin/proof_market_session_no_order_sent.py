#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time

from _batch25v_market_observation_common import (
    build_all_static_guard_report,
    proof_path,
    redis_client,
    stream_len_contract,
    stream_recent_contract,
    write_proof,
)


def _action_from_row(row: dict) -> str:
    fields = dict(row.get("fields") or {})
    action = str(fields.get("action") or "").upper()
    if action:
        return action
    payload = fields.get("payload_json")
    if payload:
        try:
            parsed = json.loads(payload)
            return str(parsed.get("action") or "").upper()
        except Exception:
            return ""
    return ""


def main() -> int:
    client = redis_client()
    observe_seconds = int(os.getenv("BATCH25V_OBSERVE_SECONDS", "60"))
    static_guard = build_all_static_guard_report()

    order_const, order_key, order_len_before = stream_len_contract(
        client,
        "STREAM_ORDERS_MME",
        "STREAM_ORDERS",
        "STREAM_ORDER_EVENTS",
    )
    decision_const, decision_key, decision_len_before = stream_len_contract(
        client,
        "STREAM_DECISIONS_MME",
        "STREAM_DECISIONS",
        "STREAM_STRATEGY_DECISIONS",
    )

    time.sleep(observe_seconds)

    _oc2, _ok2, order_len_after = stream_len_contract(
        client,
        "STREAM_ORDERS_MME",
        "STREAM_ORDERS",
        "STREAM_ORDER_EVENTS",
    )
    _dc2, _dk2, decision_len_after = stream_len_contract(
        client,
        "STREAM_DECISIONS_MME",
        "STREAM_DECISIONS",
        "STREAM_STRATEGY_DECISIONS",
    )
    _dc3, _dk3, recent_decisions = stream_recent_contract(
        client,
        "STREAM_DECISIONS_MME",
        "STREAM_DECISIONS",
        "STREAM_STRATEGY_DECISIONS",
        count=20,
    )

    actions = [_action_from_row(row) for row in recent_decisions]
    non_hold_actions = [action for action in actions if action and action != "HOLD"]

    checks = {
        "observation_window_seconds_positive": observe_seconds > 0,
        "execution_sends_no_order": order_len_after == order_len_before,
        "strategy_decisions_observed": decision_len_after >= decision_len_before and decision_len_after > 0,
        "execution_receives_hold_only_recently": not non_hold_actions,
        "producer_consumer_static_guard_ok": bool(static_guard.get("ok")),
    }

    ok = all(checks.values())

    proof = {
        "proof_name": "proof_market_session_no_order_sent",
        "batch": "25V/26I",
        "generated_at_ns": time.time_ns(),
        "market_session_no_order_sent_ok": ok,
        "observation_seconds": observe_seconds,
        "streams": {
            "orders": {
                "constant": order_const,
                "key": order_key,
                "len_before": order_len_before,
                "len_after": order_len_after,
            },
            "decisions": {
                "constant": decision_const,
                "key": decision_key,
                "len_before": decision_len_before,
                "len_after": decision_len_after,
                "recent_actions": actions,
                "non_hold_actions": non_hold_actions,
            },
        },
        "checks": checks,
        "static_guard_report": static_guard,
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    out = proof_path("proof_market_session_no_order_sent.json")
    write_proof(out, proof)
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
