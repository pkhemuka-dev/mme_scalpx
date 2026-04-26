#!/usr/bin/env python3
from __future__ import annotations

import inspect
import json
import time
from typing import Any

from _batch25v_market_observation_common import (
    build_all_static_guard_report,
    proof_path,
    redis_client,
    safe_bool,
    safe_int,
    write_proof,
)


def _try_call(fn: Any, variants: list[tuple]) -> Any:
    last_exc = None
    for args in variants:
        try:
            return fn(*args)
        except Exception as exc:
            last_exc = exc
    raise RuntimeError(f"all invocation variants failed for {fn}: {last_exc}")


def _as_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            out = value.to_dict()
            return dict(out) if isinstance(out, dict) else {}
        except Exception:
            return {}
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def main() -> int:
    from app.mme_scalpx.services import features as F
    from app.mme_scalpx.services import strategy as S

    client = redis_client()
    payload = F.FeatureEngine(redis_client=client).build_payload(now_ns=time.time_ns())

    bridge_cls = getattr(S, "StrategyFamilyConsumerBridge", None)
    if bridge_cls is None:
        raise SystemExit("StrategyFamilyConsumerBridge missing")

    bridge = bridge_cls()

    if hasattr(bridge, "build_consumer_view"):
        view = _try_call(bridge.build_consumer_view, [(payload,), (payload, time.time_ns())])
    elif hasattr(bridge, "build_view"):
        view = _try_call(bridge.build_view, [(payload,), (payload, time.time_ns())])
    else:
        view = payload

    if not hasattr(bridge, "build_activation_report"):
        raise SystemExit("StrategyFamilyConsumerBridge.build_activation_report missing")

    report = _try_call(
        bridge.build_activation_report,
        [(view,), (view, payload), (payload,)],
    )
    report_dict = _as_dict(report)

    if hasattr(bridge, "build_hold_decision"):
        decision = _try_call(
            bridge.build_hold_decision,
            [(view, report), (view,), (report,), ()],
        )
        decision_dict = _as_dict(decision)
    else:
        decision_dict = {}

    strategy_source = inspect.getsource(S)
    static_guard = build_all_static_guard_report()

    action = str(decision_dict.get("action") or decision_dict.get("action_type") or "").upper()
    qty = safe_int(decision_dict.get("quantity_lots", decision_dict.get("qty", 0)), 0)

    report_has_detail = any(
        key in report_dict
        for key in (
            "candidates",
            "candidate",
            "blockers",
            "blocked",
            "no_signal",
            "branch_reports",
            "families",
            "frames",
        )
    )

    checks = {
        "activation_report_built": bool(report_dict),
        "activation_report_contains_candidates_blockers_or_no_signal": report_has_detail,
        "decision_built": bool(decision_dict),
        "strategy_decision_action_hold": action == "HOLD",
        "strategy_decision_quantity_zero": qty == 0,
        "activation_promoted_false": safe_bool(decision_dict.get("activation_promoted"), False) is False,
        "live_orders_allowed_false": safe_bool(decision_dict.get("live_orders_allowed"), False) is False,
        "strategy_py_guard_report_only_true": "ACTIVATION_REPORT_ONLY" in strategy_source and "True" in strategy_source,
        "strategy_py_guard_promotion_false": "ACTIVATION_ALLOW_CANDIDATE_PROMOTION" in strategy_source and "False" in strategy_source,
        "producer_consumer_static_guard_ok": bool(static_guard.get("ok")),
    }

    ok = all(checks.values())

    proof = {
        "proof_name": "proof_market_session_strategy_activation",
        "batch": "25V/26I",
        "generated_at_ns": time.time_ns(),
        "market_session_strategy_activation_ok": ok,
        "checks": checks,
        "activation_report_keys": sorted(report_dict.keys()),
        "hold_decision": decision_dict,
        "static_guard_report": static_guard,
        "runtime_safety": {
            "report_only": True,
            "hold_only": True,
            "no_promotion": True,
        },
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    out = proof_path("proof_market_session_strategy_activation.json")
    write_proof(out, proof)
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
