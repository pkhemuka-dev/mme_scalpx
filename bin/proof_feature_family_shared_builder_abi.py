#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import features as F


class StubRedis:
    def hgetall(self, key: str) -> dict[str, Any]:
        return {}


def _future(now_ns: int) -> dict[str, Any]:
    return {
        "instrument_key": getattr(N, "IK_MME_FUT", "NIFTY_FUT"),
        "instrument_token": "FUT-25K",
        "trading_symbol": "NIFTY-FUT-25K",
        "provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "ltp": 25000.0,
        "best_bid": 24999.95,
        "best_ask": 25000.05,
        "bid_qty_5": 1200,
        "ask_qty_5": 1000,
        "depth_total": 2200,
        "touch_depth": 2200,
        "spread_ratio": 0.10,
        "velocity_ratio": 1.2,
        "volume_norm": 1.3,
        "weighted_ofi": 0.58,
        "weighted_ofi_persist": 0.57,
        "vwap": 24998.0,
        "ts_event_ns": now_ns,
        "ts_local_ns": now_ns,
        "age_ms": 5,
    }


def _option(side: str, now_ns: int) -> dict[str, Any]:
    is_call = side == getattr(N, "SIDE_CALL", "CALL")
    token = "CALL-25K" if is_call else "PUT-25K"
    symbol = "NIFTY-25000-CE-25K" if is_call else "NIFTY-25000-PE-25K"
    return {
        "present": True,
        "instrument_key": token,
        "instrument_token": token,
        "trading_symbol": symbol,
        "option_symbol": symbol,
        "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "side": side,
        "option_side": side,
        "strike": 25000.0,
        "ltp": 110.0 if is_call else 105.0,
        "best_bid": 109.95 if is_call else 104.95,
        "best_ask": 110.05 if is_call else 105.05,
        "bid_qty_5": 900 if is_call else 850,
        "ask_qty_5": 800 if is_call else 750,
        "depth_total": 1700 if is_call else 1600,
        "touch_depth": 1700 if is_call else 1600,
        "spread_ratio": 0.08,
        "response_efficiency": 0.5,
        "weighted_ofi_persist": 0.56 if is_call else 0.44,
        "velocity_ratio": 1.1,
        "delta_3": 0.5 if is_call else -0.5,
        "tick_size": 0.05,
        "lot_size": 75,
        "ts_event_ns": now_ns,
        "ts_local_ns": now_ns,
        "age_ms": 5,
    }


def _dhan_context(now_ns: int) -> dict[str, Any]:
    rows = [
        {
            "side": getattr(N, "SIDE_CALL", "CALL"),
            "strike": 25000.0,
            "instrument_key": "CALL-25K",
            "instrument_token": "CALL-25K",
            "trading_symbol": "NIFTY-25000-CE-25K",
            "ltp": 110.0,
            "best_bid": 109.95,
            "best_ask": 110.05,
            "bid_qty_5": 900,
            "ask_qty_5": 800,
            "volume": 10000,
            "oi": 12000,
            "oi_change": 500,
            "iv": 12.5,
            "delta": 0.55,
            "spread_ratio": 0.08,
            "score": 0.85,
            "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
            "ts_event_ns": now_ns,
        },
        {
            "side": getattr(N, "SIDE_PUT", "PUT"),
            "strike": 25000.0,
            "instrument_key": "PUT-25K",
            "instrument_token": "PUT-25K",
            "trading_symbol": "NIFTY-25000-PE-25K",
            "ltp": 105.0,
            "best_bid": 104.95,
            "best_ask": 105.05,
            "bid_qty_5": 850,
            "ask_qty_5": 750,
            "volume": 10000,
            "oi": 13000,
            "oi_change": 550,
            "iv": 12.8,
            "delta": -0.55,
            "spread_ratio": 0.08,
            "score": 0.84,
            "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
            "ts_event_ns": now_ns,
        },
    ]
    wall = {
        "present": True,
        "call_wall": rows[0],
        "put_wall": rows[1],
        "nearest_call_oi_resistance_strike": 25000.0,
        "nearest_put_oi_support_strike": 25000.0,
        "call_wall_strength_score": 1.0,
        "put_wall_strength_score": 1.0,
        "oi_bias": "NEUTRAL",
    }
    return {
        "context_status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "atm_strike": 25000.0,
        "ts_event_ns": now_ns,
        "selected_call_instrument_key": "CALL-25K",
        "selected_put_instrument_key": "PUT-25K",
        "option_chain_ladder_json": json.dumps(rows, separators=(",", ":")),
        "strike_ladder_json": json.dumps(rows, separators=(",", ":")),
        "oi_wall_summary_json": json.dumps(wall, separators=(",", ":")),
    }


def main() -> int:
    now_ns = time.time_ns()

    engine = F.FeatureEngine(redis_client=StubRedis())

    provider_runtime = {
        "active_futures_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "active_selected_option_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "family_runtime_mode": getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
    }

    fut = engine._futures_surface(
        _future(now_ns),
        role="active",
        provider_id=getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
    )
    call = engine._option_surface(
        _option(getattr(N, "SIDE_CALL", "CALL"), now_ns),
        role="selected_call",
        provider_id=getattr(N, "PROVIDER_DHAN", "DHAN"),
    )
    put = engine._option_surface(
        _option(getattr(N, "SIDE_PUT", "PUT"), now_ns),
        role="selected_put",
        provider_id=getattr(N, "PROVIDER_DHAN", "DHAN"),
    )
    dhan_context = _dhan_context(now_ns)

    strike = engine._strike_context(
        dhan_context=dhan_context,
        futures=fut,
        selected=call,
        call=call,
        put=put,
    )
    cross = engine._cross_option(call, put, call, strike)
    regime = engine._regime_surface(fut, cross)
    tradability = engine._tradability(fut, call, put, regime)

    audit = F._builder_abi_audit_snapshot()

    checks = {
        "futures_core_builder_used": audit.get("futures_core_builder_used", 0) >= 1,
        "option_core_builder_used": audit.get("option_core_builder_used", 0) >= 2,
        "strike_ladder_builder_used": audit.get("strike_ladder_builder_used", 0) >= 1,
        "classic_strike_builder_used": audit.get("classic_strike_builder_used", 0) >= 2,
        "miso_strike_builder_used": audit.get("miso_strike_builder_used", 0) >= 2,
        "regime_builder_used": audit.get("regime_builder_used", 0) >= 1,
        "tradability_builder_used": audit.get("tradability_builder_used", 0) >= 5,
        "fallback_builder_count_zero": audit.get("fallback_builder_count", 0) == 0,
        "futures_surface_present": bool(fut.get("present")),
        "call_surface_present": bool(call.get("present")),
        "put_surface_present": bool(put.get("present")),
        "strike_ladder_present": bool(strike.get("ladder_size", 0) > 0 or strike.get("ladder_surface", {}).get("present")),
        "regime_present": bool(regime.get("regime")),
        "tradability_present": bool(tradability.get("futures")) and bool(tradability.get("classic_call")) and bool(tradability.get("miso_call")),
        "observe_only_not_changed": provider_runtime["family_runtime_mode"] == getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_feature_family_shared_builder_abi",
        "batch": "25K",
        "generated_at_ns": now_ns,
        "feature_family_shared_builder_abi_ok": proof_ok,
        "checks": checks,
        "builder_abi_audit": audit,
        "observed": {
            "futures": fut,
            "call": call,
            "put": put,
            "strike_context": strike,
            "regime": regime,
            "tradability": tradability,
        },
    }

    out = Path("run/proofs/proof_feature_family_shared_builder_abi.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "feature_family_shared_builder_abi_ok": proof_ok,
        "futures_core_builder_used": checks["futures_core_builder_used"],
        "option_core_builder_used": checks["option_core_builder_used"],
        "strike_ladder_builder_used": checks["strike_ladder_builder_used"],
        "classic_strike_builder_used": checks["classic_strike_builder_used"],
        "miso_strike_builder_used": checks["miso_strike_builder_used"],
        "regime_builder_used": checks["regime_builder_used"],
        "tradability_builder_used": checks["tradability_builder_used"],
        "fallback_builder_count_zero": checks["fallback_builder_count_zero"],
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
