#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys

ALLOWED = {"MIST", "MISB", "MISC", "MISR", "MISO"}

def raw(cmd):
    return subprocess.run(cmd, text=True, capture_output=True).stdout

def parse_xrev(out):
    lines = out.splitlines()
    rows = []
    i = 0
    while i < len(lines):
        sid = lines[i]
        i += 1
        d = {"_stream_id": sid}
        while i + 1 < len(lines) and not re.match(r"^\d+-\d+$", lines[i]):
            d[lines[i]] = lines[i + 1]
            i += 2
        rows.append(d)
    return rows

def strike_from_symbol(symbol):
    m = re.search(r"(\d{5})(CE|PE)$", symbol.upper())
    return m.group(1) if m else ""

rows = parse_xrev(raw(["redis-cli", "--raw", "XREVRANGE", "decisions:mme:stream", "+", "-", "COUNT", "360"]))

for r in rows:
    reason = (r.get("activation_reason") or "").lower()
    action = (r.get("activation_selected_action") or r.get("candidate_action_shadow") or "").upper()
    fam = (r.get("activation_selected_family_id") or r.get("candidate_family_id_shadow") or "").upper()
    side = (r.get("activation_selected_branch_id") or r.get("candidate_branch_id_shadow") or "").upper()
    token = (r.get("candidate_instrument_token_shadow") or r.get("instrument_token") or "").strip()
    symbol = (r.get("candidate_symbol_shadow") or r.get("option_symbol") or r.get("symbol") or "").upper().strip()
    score = r.get("activation_selected_score") or r.get("candidate_score_shadow") or "0.80"
    price = r.get("price") or r.get("candidate_price_shadow") or r.get("option_price") or r.get("limit_price") or "0"
    strike = r.get("strike") or r.get("candidate_strike_shadow") or strike_from_symbol(symbol)
    true_shadow = str(r.get("candidate_true_shadow") or "")

    if (
        reason == "candidate_observed_dry_run"
        and true_shadow == "1"
        and action in {"ENTER_CALL", "ENTER_PUT"}
        and fam in ALLOWED
        and side in {"CALL", "PUT"}
        and token
        and symbol
        and strike
    ):
        seed = "|".join(["CONTROLLED_PAPER_SCOPE_ACK", fam, side, action, token, symbol, "LOTS_1"])
        ack = "ACK_" + hashlib.sha256(seed.encode()).hexdigest()[:20].upper()
        print(json.dumps({
            "classification": "PASS_REAL_OBSERVED_CANDIDATE_FOUND",
            "stream_id": r.get("_stream_id"),
            "decision_id": r.get("decision_id"),
            "family": fam,
            "side": side,
            "action": action,
            "instrument_token": token,
            "option_symbol": symbol,
            "strike": strike,
            "score": score,
            "price": price,
            "ack": ack,
            "activation_reason": reason,
            "candidate_true_shadow": true_shadow,
        }))
        sys.exit(0)

print(json.dumps({"classification": "WAIT_NO_REAL_OBSERVED_CANDIDATE"}))
sys.exit(2)
