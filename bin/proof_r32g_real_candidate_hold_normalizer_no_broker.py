
from __future__ import annotations

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


def sh(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def forbidden_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    bad = []
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
    tag, module_s, r32e_dir_s, outdir_s, proof_s = sys.argv[1:]
    module_path = Path(module_s)
    r32e_dir = Path(r32e_dir_s)
    outdir = Path(outdir_s)
    proof_path = Path(proof_s)

    candidates = load_json(r32e_dir / "real_candidates_for_r32d.json") or []
    real_candidates = list(candidates[:20])

    # Negative control: HOLD but not candidate-present/scored. Must remain rejected.
    real_candidates.append({
        "source": "r32g_negative_control",
        "family_id": "NEGATIVE",
        "side": "CALL",
        "action": "HOLD",
        "symbol": "NEGATIVE_CONTROL",
        "qty": 75,
        "price": 1.0,
        "score": 0.0,
    })

    orders_before = sh("redis-cli XLEN orders")
    risk_before = sh("redis-cli XLEN risk")
    execution_before = sh("redis-cli XLEN execution")

    result = run_internal_order_intent_pipeline(
        real_candidates,
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
            real_candidates[:1],
            outdir=outdir / "dangerous_env_should_not_write",
            env={"SCALPX_ENABLE_LIVE": "1"},
        )
    except BrokerTransportHardBlocked:
        dangerous_env_blocked = True

    orders_after = sh("redis-cli XLEN orders")
    risk_after = sh("redis-cli XLEN risk")
    execution_after = sh("redis-cli XLEN execution")

    summary = result["summary"]
    ledgers = result["ledgers"]
    action_norm_count = sum(1 for r in ledgers["candidate_intents"] if r.get("r32g_action_normalized") is True)
    source_hold_count = sum(1 for r in ledgers["candidate_intents"] if r.get("source_action") == "HOLD")
    accepted = summary.get("risk_accept_shadow_count", 0)
    rejected = summary.get("risk_reject_shadow_count", 0)

    safety_ok = (
        orders_before == "0"
        and risk_before == "0"
        and execution_before == "0"
        and orders_after == "0"
        and risk_after == "0"
        and execution_after == "0"
    )

    forbidden = forbidden_calls(module_path)

    pass_ok = (
        safety_ok
        and summary.get("candidate_intent_count") == 21
        and accepted == 20
        and rejected == 1
        and summary.get("execution_sim_filled_count") == 20
        and summary.get("order_intent_recorded_count") == 21
        and summary.get("would_have_order_count") == 20
        and summary.get("real_order_sent_count") == 0
        and summary.get("broker_calls_executed_count") == 0
        and action_norm_count >= 20
        and source_hold_count >= 20
        and dangerous_env_blocked
        and not forbidden
    )

    classification = (
        "PASS_R32G_REAL_R9X_HOLD_CANDIDATES_NORMALIZED_TO_INTERNAL_ENTRY_NO_BROKER_NO_REPLAY_NO_ORDER"
        if pass_ok
        else "REVIEW_R32G_NORMALIZER_SMOKE_FAILED_NO_BROKER_NO_REPLAY_NO_ORDER"
    )

    proof = {
        "tag": tag,
        "classification": classification,
        "r32e_dir": str(r32e_dir),
        "summary": summary,
        "real_candidate_input_count": len(candidates[:20]),
        "total_candidate_input_count": len(real_candidates),
        "r32g_action_normalized_count": action_norm_count,
        "source_hold_count": source_hold_count,
        "dangerous_env_blocked": dangerous_env_blocked,
        "forbidden_broker_call_names_in_module": forbidden,
        "orders_before": orders_before,
        "risk_before": risk_before,
        "execution_before": execution_before,
        "orders_after": orders_after,
        "risk_after": risk_after,
        "execution_after": execution_after,
        "module": str(module_path),
        "outdir": str(outdir),
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
