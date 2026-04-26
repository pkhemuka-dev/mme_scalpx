#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import models as M
from app.mme_scalpx.services.feeds import FeedConfig, RawDhanContext, TickNormalizer
from app.mme_scalpx.services import features as F
from app.mme_scalpx.services.feature_family import strike_selection as SS


def _row(
    *,
    side: str,
    strike: float,
    token: str,
    symbol: str,
    oi: int,
    oi_change: int,
    ltp: float,
    bid: float,
    ask: float,
    score: float,
    ts_ns: int,
) -> dict[str, Any]:
    return {
        "side": side,
        "strike": strike,
        "instrument_key": token,
        "instrument_token": token,
        "trading_symbol": symbol,
        "ltp": ltp,
        "best_bid": bid,
        "best_ask": ask,
        "bid_qty_5": 1000,
        "ask_qty_5": 900,
        "volume": 10000,
        "oi": oi,
        "oi_change": oi_change,
        "iv": 12.5,
        "delta": 0.55 if side == N.SIDE_CALL else -0.55,
        "spread_ratio": 0.08,
        "score": score,
        "provider_id": N.PROVIDER_DHAN,
        "ts_event_ns": ts_ns,
    }


def _payload(now_ns: int, *, stale: bool = False) -> dict[str, Any]:
    ts_ns = now_ns - (10_000_000_000 if stale else 50_000_000)

    rows = [
        _row(side=N.SIDE_CALL, strike=25000.0, token="CALL-25000", symbol="NIFTY-25000-CE", oi=9000, oi_change=250, ltp=110.0, bid=109.95, ask=110.05, score=0.85, ts_ns=ts_ns),
        _row(side=N.SIDE_CALL, strike=25050.0, token="CALL-25050", symbol="NIFTY-25050-CE", oi=15000, oi_change=500, ltp=85.0, bid=84.95, ask=85.05, score=0.76, ts_ns=ts_ns),
        _row(side=N.SIDE_PUT, strike=25000.0, token="PUT-25000", symbol="NIFTY-25000-PE", oi=10000, oi_change=300, ltp=105.0, bid=104.95, ask=105.05, score=0.84, ts_ns=ts_ns),
        _row(side=N.SIDE_PUT, strike=24950.0, token="PUT-24950", symbol="NIFTY-24950-PE", oi=16000, oi_change=600, ltp=82.0, bid=81.95, ask=82.05, score=0.78, ts_ns=ts_ns),
    ]

    return {
        "provider_ts_ns": ts_ns,
        "context_status": N.PROVIDER_STATUS_HEALTHY,
        "atm_strike": 25000.0,
        "selected_call_instrument_key": "CALL-25000",
        "selected_put_instrument_key": "PUT-25000",
        "chain_rows": rows,
        "selected_call_score": 0.85,
        "selected_put_score": 0.84,
        "message": "batch25j_proof_stale" if stale else "batch25j_proof_fresh",
    }


def _normalize(payload: dict[str, Any], now_ns: int) -> M.DhanContextState:
    normalizer = TickNormalizer(config=FeedConfig())
    event, state = normalizer.normalize_dhan_context(
        raw=RawDhanContext(
            provider_id=N.PROVIDER_DHAN,
            payload=payload,
            recv_ts_ns=payload["provider_ts_ns"],
        ),
        now_ns=now_ns,
    )
    event.validate()
    state.validate()
    return state


def main() -> int:
    now_ns = time.time_ns()

    fresh_state = _normalize(_payload(now_ns, stale=False), now_ns)
    stale_state = _normalize(_payload(now_ns, stale=True), now_ns)

    fresh_hash = fresh_state.to_dict()
    stale_hash = stale_state.to_dict()

    ladder = json.loads(fresh_hash["option_chain_ladder_json"])
    wall = json.loads(fresh_hash["oi_wall_summary_json"])
    call_ctx = json.loads(fresh_hash["selected_call_context_json"])
    put_ctx = json.loads(fresh_hash["selected_put_context_json"])

    engine = F.FeatureEngine(redis_client=None)
    feature_ladder = engine._ladder(fresh_hash)
    fresh_quality = F._dhan_context_quality(fresh_hash, now_ns)
    stale_quality = F._dhan_context_quality(stale_hash, now_ns)

    strike_rows = SS.normalize_strike_ladder_rows(fresh_hash)
    strike_surface = SS.build_strike_ladder_surface(dhan_context=fresh_hash)

    call_rows = [row for row in ladder if row.get("side") == N.SIDE_CALL]
    put_rows = [row for row in ladder if row.get("side") == N.SIDE_PUT]

    checks = {
        "ladder_size_gt_0": len(ladder) > 0,
        "has_call_rows": bool(call_rows),
        "has_put_rows": bool(put_rows),
        "has_oi_wall": bool(wall.get("oi_wall_ready") and (wall.get("call_wall") or wall.get("put_wall"))),
        "selected_call_context_present": bool(call_ctx.get("instrument_key") and call_ctx.get("trading_symbol")),
        "selected_put_context_present": bool(put_ctx.get("instrument_key") and put_ctx.get("trading_symbol")),
        "state_hash_contains_frozen_json_keys": all(
            key in fresh_hash and fresh_hash[key]
            for key in (
                "option_chain_ladder_json",
                "strike_ladder_json",
                "oi_wall_summary_json",
                "selected_call_context_json",
                "selected_put_context_json",
            )
        ),
        "wall_summary_fields_preserved": all(
            key in fresh_hash and fresh_hash[key] not in (None, "")
            for key in (
                "nearest_call_oi_resistance_strike",
                "nearest_put_oi_support_strike",
                "call_wall_distance_pts",
                "put_wall_distance_pts",
                "call_wall_strength_score",
                "put_wall_strength_score",
                "oi_bias",
            )
        ),
        "features_ladder_reads_frozen_json": len(feature_ladder) == len(ladder),
        "feature_ladder_row_fields_complete": all(
            key in feature_ladder[0]
            for key in (
                "side",
                "strike",
                "instrument_key",
                "instrument_token",
                "trading_symbol",
                "ltp",
                "best_bid",
                "best_ask",
                "bid_qty_5",
                "ask_qty_5",
                "volume",
                "oi",
                "oi_change",
                "iv",
                "delta",
                "spread_ratio",
                "score",
                "provider_id",
                "ts_event_ns",
            )
        ),
        "strike_selection_reads_frozen_json": len(strike_rows) == len(ladder),
        "strike_surface_ladder_present": bool(strike_surface.get("ladder_present")),
        "miso_context_ready_fresh": fresh_quality.get("miso_context_ready") is True,
        "miso_context_ready_stale_false": stale_quality.get("miso_context_ready") is False,
        "stale_context_marked_stale": stale_quality.get("stale") is True,
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_dhan_oi_ladder_persistence",
        "batch": "25J",
        "generated_at_ns": now_ns,
        "dhan_oi_ladder_persistence_ok": proof_ok,
        "checks": checks,
        "fresh_quality": fresh_quality,
        "stale_quality": stale_quality,
        "ladder_size": len(ladder),
        "feature_ladder_size": len(feature_ladder),
        "strike_selection_ladder_size": len(strike_rows),
        "wall_summary": wall,
        "selected_call_context": call_ctx,
        "selected_put_context": put_ctx,
        "sample_ladder_row": ladder[0] if ladder else None,
        "sample_feature_ladder_row": feature_ladder[0] if feature_ladder else None,
        "state_hash_keys": sorted(fresh_hash.keys()),
    }

    out = Path("run/proofs/proof_dhan_oi_ladder_persistence.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "dhan_oi_ladder_persistence_ok": proof_ok,
        "ladder_size": len(ladder),
        "has_call_rows": checks["has_call_rows"],
        "has_put_rows": checks["has_put_rows"],
        "has_oi_wall": checks["has_oi_wall"],
        "miso_context_ready_fresh": checks["miso_context_ready_fresh"],
        "miso_context_ready_stale_false": checks["miso_context_ready_stale_false"],
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
