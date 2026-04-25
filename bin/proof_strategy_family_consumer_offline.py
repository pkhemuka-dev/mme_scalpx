from __future__ import annotations

"""
bin/proof_strategy_family_consumer_offline.py

Offline proof for the next seam after features.py:

features.py family_features payload
    -> strategy consumer bridge readiness

This script does NOT modify strategy.py.
This script does NOT generate trade decisions.
This script does NOT place orders.

It proves:
- family_features is contract-valid
- family_surfaces exists
- family_frames exists
- strategy-consumable stage flags exist
- provider runtime exists
- all five families are readable
- all CALL/PUT branch frames are readable
- consumer can derive a safe HOLD-only diagnostic view
"""

import json
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.features import FeatureEngine, _json_dump
from app.mme_scalpx.services.feature_family import contracts as C


FAMILY_IDS = tuple(C.FAMILY_IDS)
BRANCH_IDS = tuple(C.BRANCH_IDS)

SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")
PROVIDER_DHAN = getattr(N, "PROVIDER_DHAN", "DHAN")
PROVIDER_ZERODHA = getattr(N, "PROVIDER_ZERODHA", "ZERODHA")

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
KEY_OPT_DHAN = getattr(
    N,
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN",
    N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
)


class DummyRedis:
    def __init__(self, store: Mapping[str, Mapping[str, Any]]):
        self.store = {k: dict(v) for k, v in store.items()}

    def hgetall(self, key: str) -> dict[str, Any]:
        return dict(self.store.get(key, {}))


def _seed_store() -> dict[str, dict[str, Any]]:
    ts = 1_800_000_000_000_000_000
    ladder = [
        {"strike": 22500, "side": SIDE_CALL, "ltp": 110, "bid": 109.95, "ask": 110.05, "oi": 120000, "volume": 1500},
        {"strike": 22550, "side": SIDE_CALL, "ltp": 82, "bid": 81.95, "ask": 82.05, "oi": 190000, "volume": 2200},
        {"strike": 22500, "side": SIDE_PUT, "ltp": 92, "bid": 91.95, "ask": 92.05, "oi": 100000, "volume": 1400},
        {"strike": 22450, "side": SIDE_PUT, "ltp": 76, "bid": 75.95, "ask": 76.05, "oi": 170000, "volume": 2000},
    ]

    return {
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


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _strategy_consumer_view(
    *,
    family_features: Mapping[str, Any],
    family_surfaces: Mapping[str, Any],
    family_frames: Mapping[str, Any],
) -> dict[str, Any]:
    """
    HOLD-only diagnostic extraction that strategy.py can later mirror.

    This deliberately does not make entry/exit decisions.
    """
    C.validate_family_features_payload(family_features)

    stage_flags = family_features["stage_flags"]
    provider_runtime = family_features["provider_runtime"]
    common = family_features["common"]
    families = family_features["families"]

    family_status: dict[str, Any] = {}
    for family_id in FAMILY_IDS:
        family_payload = families[family_id]
        surface_payload = family_surfaces["families"][family_id]

        family_status[family_id] = {
            "family_present": True,
            "contract_eligible": bool(family_payload.get("eligible", False)),
            "surface_eligible": bool(surface_payload.get("eligible", False)),
            "surface_keys": tuple(surface_payload.keys()),
        }

    branch_frames: dict[str, Any] = {}
    for family_id in FAMILY_IDS:
        for branch_id in BRANCH_IDS:
            key = f"{family_id.lower()}_{branch_id.lower()}"
            frame = family_frames[key]
            branch_frames[key] = {
                "present": True,
                "family_id": frame.get("family_id"),
                "branch_id": frame.get("branch_id"),
                "side": frame.get("side"),
                "eligible": bool(frame.get("eligible", False)),
                "tradability_ok": bool(frame.get("tradability_ok", False)),
                "instrument_key": frame.get("instrument_key"),
                "strike": frame.get("strike"),
            }

    strategy_safe_to_consume = bool(
        stage_flags
        and provider_runtime
        and common
        and family_status
        and branch_frames
    )

    return {
        "strategy_action": getattr(N, "ACTION_HOLD", "HOLD"),
        "reason": "offline_consumer_bridge_diagnostic_only",
        "strategy_safe_to_consume": strategy_safe_to_consume,
        "data_valid": bool(stage_flags.get("data_valid", False)),
        "warmup_complete": bool(stage_flags.get("warmup_complete", False)),
        "provider_ready_classic": bool(stage_flags.get("provider_ready_classic", False)),
        "provider_ready_miso": bool(stage_flags.get("provider_ready_miso", False)),
        "regime": common.get("regime"),
        "selected_option": common.get("selected_option") or common.get("selected_call") or {},
        "family_status": family_status,
        "branch_frames": branch_frames,
    }


def main() -> int:
    engine = FeatureEngine(redis_client=DummyRedis(_seed_store()))
    payload = engine.build_payload(now_ns=1_800_000_000_000_000_000)

    family_features = payload["family_features"]
    family_surfaces = payload["family_surfaces"]
    family_frames = payload["family_frames"]

    C.validate_family_features_payload(family_features)
    roundtrip = json.loads(_json_dump(family_features))
    C.validate_family_features_payload(roundtrip)

    view = _strategy_consumer_view(
        family_features=family_features,
        family_surfaces=family_surfaces,
        family_frames=family_frames,
    )

    _require(view["strategy_action"] == getattr(N, "ACTION_HOLD", "HOLD"), "consumer view must be HOLD-only")
    _require(view["strategy_safe_to_consume"], "strategy consumer view is not safe")
    _require(view["data_valid"], "data_valid false")
    _require(view["warmup_complete"], "warmup_complete false")
    _require(tuple(view["family_status"].keys()) == FAMILY_IDS, "family_status IDs mismatch")

    for family_id in FAMILY_IDS:
        _require(view["family_status"][family_id]["family_present"], f"missing family {family_id}")

    for family_id in FAMILY_IDS:
        for branch_id in BRANCH_IDS:
            key = f"{family_id.lower()}_{branch_id.lower()}"
            _require(key in view["branch_frames"], f"missing branch frame {key}")
            _require(view["branch_frames"][key]["present"], f"branch frame not present {key}")

    out_path = Path("run/proofs/strategy_family_consumer_offline.json")
    out_path.write_text(
        json.dumps(
            {
                "consumer_view": view,
                "family_features_top_keys": tuple(family_features.keys()),
                "family_ids": tuple(family_features["families"].keys()),
                "family_surface_ids": tuple(family_surfaces["families"].keys()),
                "family_frame_ids": tuple(family_frames.keys()),
            },
            ensure_ascii=False,
            sort_keys=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("===== STRATEGY FAMILY CONSUMER OFFLINE PROOF =====")
    print("strategy_action =", view["strategy_action"])
    print("strategy_safe_to_consume =", view["strategy_safe_to_consume"])
    print("data_valid =", view["data_valid"])
    print("warmup_complete =", view["warmup_complete"])
    print("provider_ready_classic =", view["provider_ready_classic"])
    print("provider_ready_miso =", view["provider_ready_miso"])
    print("regime =", view["regime"])
    print("family_ids =", tuple(view["family_status"].keys()))
    print("branch_frame_count =", len(view["branch_frames"]))
    print("dumped =", out_path)
    print("strategy family consumer offline proof: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
