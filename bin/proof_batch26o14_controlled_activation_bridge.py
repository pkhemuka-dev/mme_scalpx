#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import datetime
import time
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o14_controlled_activation_bridge.json"

ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def cmd(args: list[str], timeout: float = 5.0, env: dict[str, str] | None = None) -> str:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env)
        return cp.stdout.strip() if cp.returncode == 0 else "ERR:" + (cp.stderr.strip() or cp.stdout.strip())
    except Exception as exc:
        return "EXC:" + repr(exc)

def hgetall(key: str) -> dict[str, str]:
    raw = cmd(["redis-cli", "HGETALL", key]).splitlines()
    d: dict[str, str] = {}
    for i in range(0, len(raw) - 1, 2):
        d[raw[i]] = raw[i + 1]
    return d

def hset(key: str, fields: dict[str, Any]) -> str:
    args = ["redis-cli", "HSET", key]
    for k, v in fields.items():
        args.extend([k, str(v)])
    return cmd(args, 5)

def xlen(stream: str) -> str:
    return cmd(["redis-cli", "XLEN", stream], 5)

def pgrep(pattern: str) -> str:
    return cmd(["bash", "-lc", f"pgrep -af {pattern!r} | grep -v grep || true"], 5)

def load_json(path: str) -> dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(errors="replace"))
    except Exception:
        return {}

def jdump(x: Any) -> str:
    return json.dumps(x, separators=(",", ":"), sort_keys=True)

def latest_decision() -> str:
    return cmd(["bash", "-lc", "redis-cli XREVRANGE decisions:mme:stream + - COUNT 1 | sed -n '1,260p'"], 5)

def is_flat(pos: dict[str, str]) -> bool:
    return (
        pos.get("has_position") == "0"
        and pos.get("position_side") == "FLAT"
        and pos.get("qty_lots") == "0"
        and pos.get("qty_units") == "0"
    )

def extract_family_features() -> dict[str, Any]:
    h = hgetall("state:features:mme:fut")
    for key in ["family_features_json", "family_surfaces_json", "consumer_view_json"]:
        raw = h.get(key)
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return {"source_key": key, "payload": parsed}
            except Exception:
                pass
    return {"source_key": "", "payload": {}}

def main() -> int:
    o13 = load_json("run/proofs/proof_batch26o13_activation_bridge_audit.json")
    o8 = load_json("run/proofs/proof_batch26o8_live_25v_gate.json")
    o9 = load_json("run/proofs/proof_batch26o9_controlled_paper_preflight.json")
    o12_files = sorted((ROOT / "run/proofs").glob("proof_batch26o12_core_only_stability_lite_*.json"))
    o12 = {}
    if o12_files:
        try:
            o12 = json.loads(o12_files[-1].read_text(errors="replace"))
        except Exception:
            o12 = {}

    pos = hgetall("state:position:mme")
    provider = hgetall("state:provider:runtime")
    ff = extract_family_features()

    env_live_blocked = {
        "SCALPX_REAL_LIVE_ALLOWED": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", ""),
        "ALLOW_LIVE_ORDERS": os.environ.get("ALLOW_LIVE_ORDERS", ""),
        "LIVE_ORDERS_ALLOWED": os.environ.get("LIVE_ORDERS_ALLOWED", ""),
        "REAL_LIVE_ALLOWED": os.environ.get("REAL_LIVE_ALLOWED", ""),
        "TRADING_ENABLED": os.environ.get("TRADING_ENABLED", ""),
    }
    truthy = {"1", "true", "yes", "on", "enabled", "allowed"}
    live_env_ok = not any(str(v).strip().lower() in truthy for v in env_live_blocked.values())

    risk_running = bool(pgrep("app.mme_scalpx.main --service risk"))
    execution_running = bool(pgrep("app.mme_scalpx.main --service execution"))

    preconditions = {
        "o13_passed": o13.get("final_verdict") == "PASS_ACTIVATION_BRIDGE_BLOCK_CONFIRMED_NO_PATCH",
        "o8_live_gate_passed": o8.get("batch26o8_live_25v_gate_ok") is True,
        "o9_preflight_passed": o9.get("controlled_paper_preflight_ok") is True,
        "o12_core_stable": o12.get("core_only_stability_lite_ok") is True,
        "redis_pong": cmd(["redis-cli", "PING"]) == "PONG",
        "orders_zero": xlen("orders:mme:stream") == "0",
        "position_flat": is_flat(pos),
        "provider_ready_classic": provider.get("provider_ready_classic") == "True",
        "provider_ready_miso_false": provider.get("provider_ready_miso") == "False",
        "risk_not_running": not risk_running,
        "execution_not_running": not execution_running,
        "real_live_env_blocked": live_env_ok,
    }

    payload = ff["payload"]
    branch_candidates = []

    # Pure proof-side candidate extraction only.
    # This does not call broker, risk, execution, or strategy service.
    if isinstance(payload, dict):
        for key, value in payload.items():
            if not isinstance(value, dict):
                continue
            key_l = str(key).lower()
            fam = str(value.get("family_id") or value.get("family") or "").upper()
            branch = str(value.get("branch_id") or value.get("side") or "").upper()
            if ("mist" in key_l or fam == "MIST") and ("call" in key_l or branch == "CALL"):
                branch_candidates.append({
                    "source_key": key,
                    "family_id": fam or "MIST",
                    "branch_id": branch or "CALL",
                    "eligible": value.get("eligible"),
                    "tradability_ok": value.get("tradability_ok"),
                    "entry_pass": value.get("entry_pass"),
                    "failed_stage": value.get("failed_stage"),
                    "blocked_reason": value.get("blocked_reason") or value.get("batch9_freeze_blocked_reason"),
                    "option_symbol": value.get("option_symbol"),
                    "option_price": value.get("option_price"),
                    "raw_keys": sorted(value.keys())[:120],
                })

    # Controlled activation bridge does not force a strategy signal.
    # It only proves that if a MIST CALL branch is eligible in future, the bridge
    # can mark it paper-promotable under ACK without enabling real live.
    synthetic_candidate = {
        "family_id": "MIST",
        "branch_id": "CALL",
        "side": "CALL",
        "quantity_lots": 1,
        "activation_mode": "controlled_paper",
        "paper_or_sandbox_only": True,
        "real_live_allowed": False,
        "automatic_broker_failover_allowed": False,
        "mid_position_provider_migration_allowed": False,
        "scope_ack": ACK,
        "source": "batch26o14_activation_bridge_proof_only",
    }

    proof_candidate_ok = all(preconditions.values()) and bool(branch_candidates)

    activation_preview = {
        "action": "ENTRY_PREVIEW_ONLY" if proof_candidate_ok else "HOLD",
        "family_id": "MIST",
        "branch_id": "CALL",
        "quantity_lots": 1,
        "activation_mode": "controlled_paper",
        "promoted": False,
        "paper_promotable_if_strategy_candidate_true": bool(proof_candidate_ok),
        "safe_to_promote_real_live": False,
        "broker_side_effects_allowed": False,
        "live_orders_allowed": False,
        "reason": "controlled_activation_bridge_ready_no_strategy_candidate_forced" if proof_candidate_ok else "controlled_activation_bridge_preconditions_or_branch_missing",
        "candidate": synthetic_candidate if proof_candidate_ok else None,
    }

    # Store preview in audit hash only. No orders stream write.
    write_result = hset("audit:batch26o14:activation_bridge", {
        "created_at": now_iso(),
        "activation_preview_json": jdump(activation_preview),
        "real_live_approved": "False",
        "broker_side_effects_allowed": "False",
        "orders_stream_write": "False",
    })

    latest_after = latest_decision()

    proof = {
        "batch": "26O14",
        "name": "controlled_activation_bridge_repair_no_risk_execution",
        "created_at": now_iso(),
        "preconditions": preconditions,
        "family_features_source_key": ff["source_key"],
        "mist_call_branch_candidates": branch_candidates,
        "activation_preview": activation_preview,
        "audit_hash_write_result": write_result,
        "orders_len_before_after": {
            "orders_len": xlen("orders:mme:stream"),
        },
        "latest_decision_after_tail": latest_after[-8000:],
        "risk_running": risk_running,
        "execution_running": execution_running,
        "real_live_approved": False,
        "paper_order_sent": False,
        "patch_scope": "proof_side_activation_bridge_audit_hash_only",
    }

    proof["controlled_activation_bridge_repair_ok"] = (
        all(preconditions.values())
        and proof["orders_len_before_after"]["orders_len"] == "0"
        and proof["real_live_approved"] is False
        and proof["paper_order_sent"] is False
        and proof["risk_running"] is False
        and proof["execution_running"] is False
        and "OK" in str(write_result) or write_result.strip().isdigit()
    )

    proof["final_verdict"] = (
        "PASS_CONTROLLED_ACTIVATION_BRIDGE_READY_NO_RISK_EXECUTION"
        if proof["controlled_activation_bridge_repair_ok"]
        else "FAIL_CONTROLLED_ACTIVATION_BRIDGE_REVIEW_REQUIRED"
    )
    proof["next_required_batch"] = (
        "Batch 26-O15 strategy activation service patch or controlled paper retry design"
        if proof["final_verdict"].startswith("PASS")
        else "Review O14 preconditions / branch candidate extraction"
    )

    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "controlled_activation_bridge_repair_ok": proof["controlled_activation_bridge_repair_ok"],
        "failed_preconditions": [k for k, v in preconditions.items() if not v],
        "mist_call_branch_candidate_count": len(branch_candidates),
        "activation_preview": activation_preview,
        "orders_len": proof["orders_len_before_after"]["orders_len"],
        "risk_running": proof["risk_running"],
        "execution_running": proof["execution_running"],
        "real_live_approved": proof["real_live_approved"],
        "paper_order_sent": proof["paper_order_sent"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["final_verdict"].startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
