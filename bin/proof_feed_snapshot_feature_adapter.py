#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import features as F


def _member(
    *,
    side: str | None,
    strike: float | None,
    instrument_key: str,
    token: str,
    symbol: str,
    ltp: float,
    bid: float,
    ask: float,
    bid_qty_5: int,
    ask_qty_5: int,
    provider_id: str,
    now_ns: int,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "instrument_key": instrument_key,
        "instrument_token": token,
        "trading_symbol": symbol,
        "ltp": ltp,
        "best_bid": bid,
        "best_ask": ask,
        "bid_qty_5": bid_qty_5,
        "ask_qty_5": ask_qty_5,
        "volume": 10000,
        "provider_id": provider_id,
        "ts_event_ns": now_ns,
    }
    if side is not None:
        out["side"] = side
        out["option_side"] = side
    if strike is not None:
        out["strike"] = strike
    return out


def main() -> int:
    now_ns = time.time_ns()

    future_member = _member(
        side=None,
        strike=None,
        instrument_key="NIFTY-FUT",
        token="FUT-TOKEN",
        symbol="NIFTY-I-FUT",
        ltp=25000.5,
        bid=25000.0,
        ask=25001.0,
        bid_qty_5=1000,
        ask_qty_5=900,
        provider_id=N.PROVIDER_ZERODHA,
        now_ns=now_ns,
    )

    selected_call = _member(
        side="CALL",
        strike=25000.0,
        instrument_key="CALL-ATM-KEY",
        token="CALL-ATM-TOKEN",
        symbol="NIFTY-25000-CE",
        ltp=110.0,
        bid=109.95,
        ask=110.05,
        bid_qty_5=700,
        ask_qty_5=650,
        provider_id=N.PROVIDER_DHAN,
        now_ns=now_ns,
    )

    selected_put = _member(
        side="PUT",
        strike=25000.0,
        instrument_key="PUT-ATM-KEY",
        token="PUT-ATM-TOKEN",
        symbol="NIFTY-25000-PE",
        ltp=105.0,
        bid=104.95,
        ask=105.05,
        bid_qty_5=600,
        ask_qty_5=620,
        provider_id=N.PROVIDER_DHAN,
        now_ns=now_ns,
    )

    feed_hash = {
        "provider_id": N.PROVIDER_DHAN,
        "future_json": json.dumps(future_member, sort_keys=True),
        "selected_call_json": json.dumps(selected_call, sort_keys=True),
        "selected_put_json": json.dumps(selected_put, sort_keys=True),
        "ce_atm_json": json.dumps(selected_call, sort_keys=True),
        "pe_atm_json": json.dumps(selected_put, sort_keys=True),
    }

    engine = F.FeatureEngine(redis_client=None)

    futures_surface = engine._futures_surface(
        feed_hash,
        role="FUTURE",
        provider_id=N.PROVIDER_ZERODHA,
    )
    call_surface, put_surface = engine._split_options(feed_hash)

    checks = {
        "futures_present": futures_surface.get("present") is True,
        "futures_valid": futures_surface.get("valid") is True,
        "futures_depth_total_from_bid_ask_qty_5": futures_surface.get("depth_total") == 1900.0,
        "futures_source_member_is_future_json": futures_surface.get("source_member_key") == "future_json",
        "futures_provider_preserved": futures_surface.get("provider_id") == N.PROVIDER_ZERODHA,
        "call_present": call_surface.get("present") is True,
        "call_valid": call_surface.get("valid") is True,
        "call_side": call_surface.get("side") == "CALL",
        "call_source_member_is_selected_call_json": call_surface.get("source_member_key") == "selected_call_json",
        "call_instrument_key_preserved": call_surface.get("instrument_key") == "CALL-ATM-KEY",
        "call_instrument_token_preserved": call_surface.get("instrument_token") == "CALL-ATM-TOKEN",
        "call_symbol_preserved": call_surface.get("option_symbol") == "NIFTY-25000-CE",
        "call_strike_preserved": call_surface.get("strike") == 25000.0,
        "call_depth_total_from_bid_ask_qty_5": call_surface.get("depth_total") == 1350.0,
        "call_tradability_ok": call_surface.get("tradability_ok") is True,
        "put_present": put_surface.get("present") is True,
        "put_valid": put_surface.get("valid") is True,
        "put_side": put_surface.get("side") == "PUT",
        "put_source_member_is_selected_put_json": put_surface.get("source_member_key") == "selected_put_json",
        "put_instrument_key_preserved": put_surface.get("instrument_key") == "PUT-ATM-KEY",
        "put_instrument_token_preserved": put_surface.get("instrument_token") == "PUT-ATM-TOKEN",
        "put_symbol_preserved": put_surface.get("option_symbol") == "NIFTY-25000-PE",
        "put_strike_preserved": put_surface.get("strike") == 25000.0,
        "put_depth_total_from_bid_ask_qty_5": put_surface.get("depth_total") == 1220.0,
        "put_tradability_ok": put_surface.get("tradability_ok") is True,
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_feed_snapshot_feature_adapter",
        "batch": "25I",
        "generated_at_ns": now_ns,
        "feed_snapshot_feature_adapter_ok": proof_ok,
        "checks": checks,
        "futures_surface": futures_surface,
        "call_surface": call_surface,
        "put_surface": put_surface,
        "feed_hash_keys": sorted(feed_hash.keys()),
    }

    out = Path("run/proofs/proof_feed_snapshot_feature_adapter.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "feed_snapshot_feature_adapter_ok": proof_ok,
        "futures_depth_total": futures_surface.get("depth_total"),
        "call_depth_total": call_surface.get("depth_total"),
        "put_depth_total": put_surface.get("depth_total"),
        "call_instrument_key": call_surface.get("instrument_key"),
        "put_instrument_key": put_surface.get("instrument_key"),
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
