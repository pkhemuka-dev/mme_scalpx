from __future__ import annotations

import os
import time
from collections import OrderedDict

from app.mme_scalpx.integrations.bootstrap_provider import build_bootstrap_result

ROLE_ORDER = ["future", "ce_atm", "ce_atm1", "pe_atm", "pe_atm1"]

def short_symbol(s: str, n: int = 18) -> str:
    return (s or "")[:n]

def fmt(v) -> str:
    if v is None:
        return "-"
    return str(v)

def ladder_to_text(rows):
    if not isinstance(rows, list):
        return "-"
    out = []
    for i, row in enumerate(rows[:5], start=1):
        if not isinstance(row, dict):
            continue
        out.append(f"{i}:{fmt(row.get('price'))}@{fmt(row.get('quantity'))}")
    return " | ".join(out) if out else "-"

r = build_bootstrap_result()
adapter = r.payload["feed_adapter"]
ri = r.payload["runtime_instruments"]

token_to_role = {
    str(ri.current_future.instrument_token): "future",
    str(ri.ce_atm.instrument_token): "ce_atm",
    str(ri.ce_atm1.instrument_token): "ce_atm1",
    str(ri.pe_atm.instrument_token): "pe_atm",
    str(ri.pe_atm1.instrument_token): "pe_atm1",
}

token_to_symbol = {
    str(ri.current_future.instrument_token): ri.current_future.tradingsymbol,
    str(ri.ce_atm.instrument_token): ri.ce_atm.tradingsymbol,
    str(ri.ce_atm1.instrument_token): ri.ce_atm1.tradingsymbol,
    str(ri.pe_atm.instrument_token): ri.pe_atm.tradingsymbol,
    str(ri.pe_atm1.instrument_token): ri.pe_atm1.tradingsymbol,
}

latest = OrderedDict((role, {}) for role in ROLE_ORDER)

print("Starting live depth witness... Ctrl+C to stop.")
while True:
    polled = adapter.poll()
    if polled is None:
        polled = []

    for item in polled:
        token = str(item.get("instrument_token", "")).strip()
        payload = item.get("payload") or {}
        role = token_to_role.get(token)
        if role is None:
            continue
        latest[role] = payload

    os.system("clear")
    print("=== SCALPX MME — LIVE 5-LEG DEPTH WITNESS ===\n")

    for role in ROLE_ORDER:
        p = latest.get(role) or {}
        depth = p.get("depth") or {}
        buy = depth.get("buy") if isinstance(depth, dict) else []
        sell = depth.get("sell") if isinstance(depth, dict) else []

        symbol = token_to_symbol.get(str(p.get("instrument_token", "")), "-")

        print(f"[{role.upper()}]")
        print(f"SYMBOL : {short_symbol(symbol, 24)}")
        print(f"LTP    : {fmt(p.get('ltp') or p.get('last_price'))}")
        print(f"BID    : {fmt(p.get('best_bid') or p.get('bid'))}")
        print(f"ASK    : {fmt(p.get('best_ask') or p.get('ask'))}")
        print(f"BIDS   : {ladder_to_text(buy)}")
        print(f"ASKS   : {ladder_to_text(sell)}")
        print()

    time.sleep(1)
