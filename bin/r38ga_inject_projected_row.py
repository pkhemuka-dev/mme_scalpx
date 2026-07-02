#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import time

def raw(cmd):
    return subprocess.run(cmd, text=True, capture_output=True).stdout.strip()

family = os.environ["SCALPX_CONTROLLED_PAPER_FAMILY"].strip().upper()
side = os.environ["SCALPX_CONTROLLED_PAPER_SIDE"].strip().upper()
action = os.environ["SCALPX_CONTROLLED_PAPER_ACTION"].strip().upper()
token = os.environ["SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN"].strip()
symbol = os.environ["SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL"].strip().upper()
strike = os.environ["SCALPX_CONTROLLED_PAPER_STRIKE"].strip()
score = os.environ.get("SCALPX_CONTROLLED_PAPER_SCORE") or "0.80"
price = os.environ.get("SCALPX_CONTROLLED_PAPER_PRICE") or "0"
ack = os.environ["SCALPX_CONTROLLED_PAPER_SCOPE_ACK"].strip()

seed = "|".join(["CONTROLLED_PAPER_SCOPE_ACK", family, side, action, token, symbol, "LOTS_1"])
expected = "ACK_" + hashlib.sha256(seed.encode()).hexdigest()[:20].upper()
if ack != expected:
    raise SystemExit(f"ACK_MISMATCH_NO_WRITE expected={expected} got={ack}")

for s in ["orders:mme:stream", "risk:mme:stream", "execution:mme:stream", "trades:ledger:stream", "cmd:mme:stream"]:
    v = raw(["redis-cli", "XLEN", s]).splitlines()[-1].replace("(integer) ", "").strip()
    if v != "0":
        raise SystemExit(f"PROTECTED_STREAM_NOT_ZERO_BEFORE_INJECT:{s}={v}")

veto = raw(["redis-cli", "HGET", "state:risk", "veto_entries"]).strip()
maxlots = raw(["redis-cli", "HGET", "state:risk", "max_new_lots"]).strip()
if veto != "0" or int(maxlots or "0") < 1:
    raise SystemExit(f"RISK_GATE_NOT_OPEN_BEFORE_INJECT:veto={veto}:maxlots={maxlots}")

try:
    price_f = float(price)
except Exception:
    price_f = 0.0
if price_f <= 0:
    price_f = 1.0

try:
    score_f = float(score)
except Exception:
    score_f = 0.80

ts = time.time_ns()
decision_id = f"r38ga-risk-open-one-event-{ts}"

metadata = {
    "option_symbol": symbol,
    "option_token": token,
    "strike": strike,
    "limit_price": str(price_f),
    "price": str(price_f),
    "entry_price": str(price_f),
    "quantity_lots": 1,
    "qty_lots": 1,
    "qty": 1,
    "side": side,
    "branch_id": side,
    "family_id": family,
    "strategy_family_id": family,
    "entry_mode": "DIRECT",
    "reason_code": "r38ga_risk_open_one_event_exact_scope_1lot",
    "confidence": score_f,
    "provider_id": "ZERODHA",
    "position_effect": "OPEN",
    "entry_position_effect": "OPEN",
    "controlled_paper_scope_ack": ack,
    "r38ga_risk_open_one_event": 1,
}

payload_json = {
    "schema_version": "r38ga_risk_open_one_event_projected_v1",
    "service": "strategy",
    "decision_id": decision_id,
    "ts_ns": ts,
    "ts_event_ns": ts,
    "action": action,
    "side": side,
    "branch_id": side,
    "strategy_family_id": family,
    "doctrine_id": family,
    "family_id": family,
    "instrument_key": token,
    "instrument_token": token,
    "quantity_lots": 1,
    "qty": 1,
    "position_effect": "OPEN",
    "entry_position_effect": "OPEN",
    "entry_mode": "DIRECT",
    "system_state": "OK",
    "reason_code": "r38ga_risk_open_one_event_exact_scope_1lot",
    "confidence": score_f,
    "metadata": metadata,
    "activation_mode": "controlled_paper_projection",
    "activation_action": action,
    "activation_promoted": 1,
    "activation_safe_to_promote": 1,
    "activation_selected_family_id": family,
    "activation_selected_branch_id": side,
    "activation_selected_action": action,
    "activation_selected_score": score,
    "candidate_true_shadow": 1,
    "candidate_present_shadow": 1,
    "candidate_family_id_shadow": family,
    "candidate_branch_id_shadow": side,
    "candidate_action_shadow": action,
    "candidate_symbol_shadow": symbol,
    "candidate_instrument_token_shadow": token,
    "safe_to_consume": 1,
    "data_valid": 1,
    "warmup_complete": 1,
    "broker_calls_executed_shadow": 0,
    "real_order_sent_shadow": 0,
    "redis_trading_stream_write_attempted_shadow": 0,
    "r38ee_strategy_to_runtime_paper_bridge": "projected_activation_selected_exact_scope_1lot",
    "r38ee_projection_attempted": 1,
    "r38ee_projection_projected": 1,
    "r38ee_scope_allowed": 1,
    "r38ga_no_broker_live": 1,
    "r38ga_stop_after_one": 1,
}

flat = {
    "decision_id": decision_id,
    "ts_ns": str(ts),
    "ts_event_ns": str(ts),
    "action": action,
    "reason_code": "r38ga_risk_open_one_event_exact_scope_1lot",
    "entry_mode": "DIRECT",
    "payload_json": json.dumps(payload_json, separators=(",", ":"), sort_keys=True),
    "side": side,
    "instrument_key": token,
    "instrument_token": token,
    "quantity_lots": "1",
    "position_effect": "OPEN",
    "entry_position_effect": "OPEN",
    "option_symbol": symbol,
    "option_token": token,
    "strike": strike,
    "limit_price": str(price_f),
    "r38ee_strategy_to_runtime_paper_bridge": "projected_activation_selected_exact_scope_1lot",
    "r38ga_risk_open_one_event": "1",
    "r38ga_no_broker_live": "1",
    "r38ga_stop_after_one": "1",
}

cmd = ["redis-cli", "XADD", "decisions:mme:stream", "*"]
for k, v in flat.items():
    cmd += [k, str(v)]

out = raw(cmd)
print(json.dumps({
    "classification": "PASS_R38GA_ROW_WRITTEN",
    "xadd_id": out,
    "decision_id": decision_id,
    "family": family,
    "side": side,
    "action": action,
    "symbol": symbol,
    "token": token,
    "option_symbol": symbol,
    "option_token": token,
    "instrument_key": token,
    "instrument_token": token,
    "strike": strike,
    "limit_price": price_f,
    "requested_limit_price": price_f,
    "r38ja_injector_canonical_summary_fields": 1,
}))
