from __future__ import annotations

# R32D proof script. No broker imports and no broker transport calls.

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

from app.mme_scalpx.services.strategy_family.internal_order_intent_pipeline import (
    BrokerTransportHardBlocked,
    InternalPipelineConfig,
    run_internal_order_intent_pipeline,
)


def _sh(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _forbidden_call_names(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    bad: list[str] = []
    forbidden = {"place_order", "send_order", "modify_order", "cancel_order"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr in forbidden:
                bad.append(fn.attr)
            if isinstance(fn, ast.Name) and fn.id in forbidden:
                bad.append(fn.id)
    return sorted(set(bad))


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: proof <tag> <module> <outdir> <proof_json>", file=sys.stderr)
        return 2

    tag, module_s, outdir_s, proof_s = sys.argv[1:]
    module_path = Path(module_s)
    outdir = Path(outdir_s)
    proof_path = Path(proof_s)

    orders_before = _sh("redis-cli XLEN orders")
    risk_before = _sh("redis-cli XLEN risk")
    execution_before = _sh("redis-cli XLEN execution")

    candidates = [
        {
            "source": "r32d_smoke_r9x_like",
            "family_id": "MISB",
            "side": "CALL",
            "action": "ENTRY",
            "symbol": "NIFTY_R32D_CALL_SMOKE",
            "qty": 75,
            "price": 100.0,
            "score": 0.72,
        },
        {
            "source": "r32d_smoke_r9x_like",
            "family_id": "MISB",
            "side": "PUT",
            "action": "ENTRY",
            "symbol": "NIFTY_R32D_PUT_SMOKE",
            "qty": 75,
            "price": 100.0,
            "score": 0.71,
        },
        {
            "source": "r32d_smoke_reject",
            "family_id": "UNKNOWN",
            "side": "",
            "action": "ENTRY",
            "symbol": "",
            "qty": 0,
            "price": 0.0,
            "score": 0.0,
        },
    ]

    result = run_internal_order_intent_pipeline(
        candidates,
        outdir=outdir,
        config=InternalPipelineConfig(default_qty=75, max_qty=75),
        env={
            "SCALPX_OBSERVE_ONLY": "1",
            "SCALPX_ENABLE_LIVE": "",
            "SCALPX_ENABLE_PAPER": "",
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "",
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "",
        },
    )

    dangerous_env_blocked = False
    try:
        run_internal_order_intent_pipeline(
            candidates[:1],
            outdir=outdir / "dangerous_env_should_not_write",
            env={"SCALPX_ENABLE_LIVE": "1"},
        )
    except BrokerTransportHardBlocked:
        dangerous_env_blocked = True

    forbidden_calls = _forbidden_call_names(module_path) + _forbidden_call_names(Path(__file__))

    orders_after = _sh("redis-cli XLEN orders")
    risk_after = _sh("redis-cli XLEN risk")
    execution_after = _sh("redis-cli XLEN execution")

    summary = result["summary"]

    safety_ok = (
        orders_before == "0"
        and risk_before == "0"
        and execution_before == "0"
        and orders_after == "0"
        and risk_after == "0"
        and execution_after == "0"
    )

    pass_ok = (
        safety_ok
        and summary["candidate_intent_count"] == 3
        and summary["risk_accept_shadow_count"] == 2
        and summary["risk_reject_shadow_count"] == 1
        and summary["execution_sim_filled_count"] == 2
        and summary["order_intent_recorded_count"] == 3
        and summary["would_have_order_count"] == 2
        and summary["real_order_sent_count"] == 0
        and summary["broker_calls_executed_count"] == 0
        and dangerous_env_blocked
        and not forbidden_calls
    )

    classification = (
        "PASS_R32D_INTERNAL_ORDER_INTENT_PIPELINE_PATCHED_AND_SMOKED_BROKER_HARD_BLOCKED_NO_ORDER"
        if pass_ok
        else "REVIEW_R32D_INTERNAL_PIPELINE_SMOKE_OR_SAFETY_FAILED_NO_ORDER"
    )

    proof = {
        "tag": tag,
        "classification": classification,
        "summary": summary,
        "dangerous_env_blocked": dangerous_env_blocked,
        "forbidden_broker_call_names_in_new_code": forbidden_calls,
        "orders_before": orders_before,
        "risk_before": risk_before,
        "execution_before": execution_before,
        "orders_after": orders_after,
        "risk_after": risk_after,
        "execution_after": execution_after,
        "outdir": str(outdir),
        "module": str(module_path),
        "proof_script": str(Path(__file__)),
        "patch_applied": True,
        "replay_started": False,
        "broker_order_attempted": False,
        "risk_service_started": False,
        "execution_service_started": False,
        "redis_delete_attempted": False,
        "lock_delete_attempted": False,
    }

    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if pass_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
