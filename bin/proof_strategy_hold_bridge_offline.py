from __future__ import annotations

"""
Offline proof for app/mme_scalpx/services/strategy.py HOLD-only bridge.
"""

import json
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.features import FeatureEngine, _json_dump as features_json_dump
from app.mme_scalpx.services.strategy import (
    ACTION_HOLD,
    HASH_FEATURES,
    StrategyFamilyConsumerBridge,
)
from app.mme_scalpx.services.feature_family import contracts as C


PROVIDER_DHAN = getattr(N, "PROVIDER_DHAN", "DHAN")
PROVIDER_ZERODHA = getattr(N, "PROVIDER_ZERODHA", "ZERODHA")
SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")

KEY_PROVIDER_RUNTIME = getattr(N, "HASH_STATE_PROVIDER_RUNTIME", N.HASH_STATE_PROVIDER_RUNTIME)
KEY_DHAN_CONTEXT = N.HASH_STATE_DHAN_CONTEXT
KEY_FUT_ACTIVE = getattr(
    N,
    "HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE",
    getattr(N, "HASH_STATE_SNAPSHOT_MME_FUT", N.HASH_STATE_SNAPSHOT_MME_FUT),
)
KEY_OPT_ACTIVE = getattr(
    N,
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE",
    getattr(N, "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED", N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED),
)
KEY_FUT_DHAN = getattr(N, "HASH_STATE_SNAPSHOT_MME_FUT_DHAN", N.HASH_STATE_SNAPSHOT_MME_FUT_DHAN)
KEY_OPT_DHAN = getattr(N, "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN", N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN)


class DummyRedis:
    def __init__(self) -> None:
        self.hashes: dict[str, dict[str, Any]] = {}
        self.streams: dict[str, list[dict[str, Any]]] = {}

    def hgetall(self, key: str) -> dict[str, Any]:
        return dict(self.hashes.get(key, {}))

    def hset(self, key: str, mapping: Mapping[str, Any]) -> None:
        self.hashes[key] = dict(mapping)

    def xadd(self, name: str, fields: Mapping[str, Any], maxlen: int | None = None, approximate: bool = True) -> str:
        self.streams.setdefault(name, []).append(dict(fields))
        return f"{len(self.streams[name])}-0"

    def pexpire(self, key: str, ttl_ms: int) -> None:
        return None


def _seed_market(redis: DummyRedis) -> None:
    ts = 1_800_000_000_000_000_000
    ladder = [
        {"strike": 22500, "side": SIDE_CALL, "ltp": 110, "bid": 109.95, "ask": 110.05, "oi": 120000, "volume": 1500},
        {"strike": 22550, "side": SIDE_CALL, "ltp": 82, "bid": 81.95, "ask": 82.05, "oi": 190000, "volume": 2200},
        {"strike": 22500, "side": SIDE_PUT, "ltp": 92, "bid": 91.95, "ask": 92.05, "oi": 100000, "volume": 1400},
        {"strike": 22450, "side": SIDE_PUT, "ltp": 76, "bid": 75.95, "ask": 76.05, "oi": 170000, "volume": 2000},
    ]

    redis.hashes.update(
        {
            KEY_PROVIDER_RUNTIME: {
                "active_futures_provider_id": PROVIDER_DHAN,
                "active_selected_option_provider_id": PROVIDER_DHAN,
                "active_option_context_provider_id": PROVIDER_DHAN,
                "active_execution_provider_id": PROVIDER_ZERODHA,
                "fallback_execution_provider_id": PROVIDER_DHAN,
                "provider_runtime_mode": "NORMAL",
                "family_runtime_mode": getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
            },
            KEY_FUT_ACTIVE: {
                "instrument_key": getattr(N, "IK_MME_FUT", "NIFTY_FUT"),
                "instrument_token": "NIFTY_FUT_TOKEN",
                "trading_symbol": "NIFTY_FUT",
                "provider_id": PROVIDER_DHAN,
                "ltp": "22520",
                "bid": "22519.95",
                "ask": "22520.05",
                "bid_qty": "1300",
                "ask_qty": "850",
                "vwap": "22500",
                "delta_3": "4.0",
                "velocity_ratio": "1.45",
                "vol_norm": "1.25",
                "nof_slope": "0.08",
                "ts_event_ns": str(ts),
                "ts_recv_ns": str(ts),
            },
            KEY_OPT_ACTIVE: {
                "instrument_key": "NIFTY_22500_CE",
                "instrument_token": "TOKEN_22500_CE",
                "trading_symbol": "NIFTY22500CE",
                "provider_id": PROVIDER_DHAN,
                "option_side": SIDE_CALL,
                "side": SIDE_CALL,
                "strike": "22500",
                "ltp": "110",
                "bid": "109.95",
                "ask": "110.05",
                "bid_qty": "700",
                "ask_qty": "620",
                "oi": "120000",
                "volume": "5000",
                "response_efficiency": "0.24",
                "delta_3": "1.2",
                "velocity_ratio": "1.35",
                "tick_size": "0.05",
                "lot_size": "50",
                "ts_event_ns": str(ts),
                "ts_recv_ns": str(ts),
            },
            KEY_FUT_DHAN: {
                "instrument_key": getattr(N, "IK_MME_FUT", "NIFTY_FUT"),
                "instrument_token": "NIFTY_FUT_TOKEN",
                "trading_symbol": "NIFTY_FUT",
                "provider_id": PROVIDER_DHAN,
                "ltp": "22520",
                "bid": "22519.95",
                "ask": "22520.05",
                "bid_qty": "1300",
                "ask_qty": "850",
                "vwap": "22500",
                "ts_event_ns": str(ts),
                "ts_recv_ns": str(ts),
            },
            KEY_OPT_DHAN: {
                "instrument_key": "NIFTY_22500_CE",
                "instrument_token": "TOKEN_22500_CE",
                "trading_symbol": "NIFTY22500CE",
                "provider_id": PROVIDER_DHAN,
                "option_side": SIDE_CALL,
                "side": SIDE_CALL,
                "strike": "22500",
                "ltp": "110",
                "bid": "109.95",
                "ask": "110.05",
                "bid_qty": "700",
                "ask_qty": "620",
                "oi": "120000",
                "volume": "5000",
                "response_efficiency": "0.24",
                "ts_event_ns": str(ts),
                "ts_recv_ns": str(ts),
            },
            KEY_DHAN_CONTEXT: {
                "provider_id": PROVIDER_DHAN,
                "atm_strike": "22500",
                "depth20_ready": "1",
                "strike_ladder": json.dumps(ladder),
                "oi_bias": "CALL_WALL_DOMINANT",
            },
        }
    )


def _publish_feature_hash(redis: DummyRedis) -> None:
    payload = FeatureEngine(redis_client=redis).build_payload(now_ns=1_800_000_000_000_000_000)
    family_features = payload["family_features"]
    C.validate_family_features_payload(family_features)

    redis.hset(
        HASH_FEATURES,
        {
            "frame_id": payload["frame_id"],
            "frame_ts_ns": str(payload["frame_ts_ns"]),
            "family_features_version": family_features["family_features_version"],
            "family_features_json": features_json_dump(family_features),
            "family_surfaces_json": features_json_dump(payload["family_surfaces"]),
            "family_frames_json": features_json_dump(payload["family_frames"]),
            "payload_json": features_json_dump(payload),
        },
    )


def main() -> int:
    redis = DummyRedis()
    _seed_market(redis)
    _publish_feature_hash(redis)

    bridge = StrategyFamilyConsumerBridge(redis_client=redis)
    bundle = bridge.read_feature_bundle()
    view = bridge.build_consumer_view(bundle, now_ns=1_800_000_000_000_000_100)
    decision = bridge.build_hold_decision(view, now_ns=1_800_000_000_000_000_200)

    assert view.safe_to_consume is True
    assert view.hold_only is True
    assert view.action == ACTION_HOLD
    assert decision["action"] == ACTION_HOLD
    assert int(decision["qty"]) == 0
    assert int(decision["hold_only"]) == 1
    assert tuple(view.family_status.keys()) == C.FAMILY_IDS
    assert len(view.branch_frames) == len(C.FAMILY_IDS) * len(C.BRANCH_IDS)
    assert "consumer_view_json" in decision
    assert "diagnostics_json" in decision

    out = {
        "view": view.to_dict(),
        "decision": decision,
        "family_ids": tuple(view.family_status.keys()),
        "branch_frame_count": len(view.branch_frames),
    }
    out_path = Path("run/proofs/strategy_hold_bridge_offline.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, sort_keys=False, indent=2), encoding="utf-8")

    print("===== STRATEGY HOLD BRIDGE OFFLINE PROOF =====")
    print("safe_to_consume =", view.safe_to_consume)
    print("hold_only =", view.hold_only)
    print("action =", decision["action"])
    print("qty =", decision["qty"])
    print("family_ids =", tuple(view.family_status.keys()))
    print("branch_frame_count =", len(view.branch_frames))
    print("dumped =", out_path)
    print("strategy HOLD bridge offline proof: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
