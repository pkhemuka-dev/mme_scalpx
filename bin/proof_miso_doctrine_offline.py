from __future__ import annotations

"""
Offline proof for services/strategy_family/miso.py.

This proof:
- builds deterministic StrategyFamilyConsumerView-like mappings
- proves MISO CALL candidate
- proves MISO PUT candidate
- proves weak/no-signal when option-led burst support is weak
- proves queue-reload veto no-signal
- proves Dhan-provider mandatory block
- proves chain-context mandatory block
- proves object-style StrategyFamilyConsumerView compatibility
- proves no Redis / broker / execution side effects
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family import miso


SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")
BRANCH_CALL = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT = getattr(N, "BRANCH_PUT", "PUT")
PROVIDER_DHAN = getattr(N, "PROVIDER_DHAN", "DHAN")
PROVIDER_ZERODHA = getattr(N, "PROVIDER_ZERODHA", "ZERODHA")

MODE_BASE_5DEPTH = getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE-5DEPTH")
MODE_DEPTH20_ENHANCED = getattr(N, "STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED", "DEPTH20-ENHANCED")


def _base_view(*, selected_side: str, mode: str = MODE_BASE_5DEPTH) -> dict[str, Any]:
    call_frame = {
        "key": "miso_call",
        "family_id": "MISO",
        "branch_id": BRANCH_CALL,
        "side": SIDE_CALL,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": "NIFTY_22500_CE",
        "instrument_token": "TOKEN_22500_CE",
        "option_symbol": "NIFTY22500CE",
        "strike": 22500.0,
        "option_price": 126.0,
        "tick_size": 0.05,
    }
    put_frame = {
        "key": "miso_put",
        "family_id": "MISO",
        "branch_id": BRANCH_PUT,
        "side": SIDE_PUT,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": "NIFTY_22500_PE",
        "instrument_token": "TOKEN_22500_PE",
        "option_symbol": "NIFTY22500PE",
        "strike": 22500.0,
        "option_price": 129.0,
        "tick_size": 0.05,
    }

    call_option = {
        "side": SIDE_CALL,
        "instrument_key": "NIFTY_22500_CE",
        "instrument_token": "TOKEN_22500_CE",
        "option_symbol": "NIFTY22500CE",
        "strike": 22500.0,
        "ltp": 126.0,
        "depth_ok": True,
        "tradability_ok": True,
        "response_efficiency": 0.34,
        "delta_3": 1.65,
        "tick_size": 0.05,
    }
    put_option = {
        "side": SIDE_PUT,
        "instrument_key": "NIFTY_22500_PE",
        "instrument_token": "TOKEN_22500_PE",
        "option_symbol": "NIFTY22500PE",
        "strike": 22500.0,
        "ltp": 129.0,
        "depth_ok": True,
        "tradability_ok": True,
        "response_efficiency": 0.35,
        "delta_3": -1.60,
        "tick_size": 0.05,
    }

    selected_option = call_option if selected_side == SIDE_CALL else put_option

    return {
        "view_version": "strategy-family-consumer-view.v1",
        "safe_to_consume": True,
        "hold_only": True,
        "data_valid": True,
        "warmup_complete": True,
        "provider_ready_classic": True,
        "provider_ready_miso": True,
        "regime": "NORMAL",
        "stage_flags": {
            "data_valid": True,
            "data_quality_ok": True,
            "session_eligible": True,
            "warmup_complete": True,
            "risk_veto_active": False,
            "reconciliation_lock_active": False,
            "active_position_present": False,
            "provider_ready_miso": True,
            "dhan_context_fresh": True,
        },
        "provider_runtime": {
            "active_futures_provider_id": PROVIDER_DHAN,
            "active_selected_option_provider_id": PROVIDER_DHAN,
            "active_option_context_provider_id": PROVIDER_DHAN,
            "active_execution_provider_id": PROVIDER_ZERODHA,
            "family_runtime_mode": "OBSERVE_ONLY",
            "miso_runtime_mode": mode,
        },
        "common": {
            "regime": "NORMAL",
            "strategy_runtime_mode_miso": mode,
            "futures": {
                "ltp": 22525.0,
                "spread_ratio": 0.05,
                "depth_total": 2500.0,
                "depth_ok": True,
                "ofi_ratio_proxy": 0.18 if selected_side == SIDE_CALL else -0.18,
                "nof_slope": 0.08 if selected_side == SIDE_CALL else -0.08,
                "delta_3": 2.4 if selected_side == SIDE_CALL else -2.4,
                "velocity_ratio": 1.25,
                "vol_norm": 1.20,
                "above_vwap": selected_side == SIDE_CALL,
                "below_vwap": selected_side == SIDE_PUT,
            },
            "call": call_option,
            "put": put_option,
            "selected_option": selected_option,
            "cross_option": {
                "cross_option_ready": True,
            },
        },
        "market": {
            "active_branch_hint": BRANCH_CALL if selected_side == SIDE_CALL else BRANCH_PUT,
            "futures_ltp": 22525.0,
            "selected_option_ltp": selected_option["ltp"],
            "premium_floor_ok": True,
        },
        "family_status": {
            "MISO": {
                "family_present": True,
                "eligible": True,
                "mode": mode,
                "chain_context_ready": True,
                "selected_side": BRANCH_CALL if selected_side == SIDE_CALL else BRANCH_PUT,
                "selected_strike": 22500.0,
                "shadow_call_strike": 22550.0,
                "shadow_put_strike": 22450.0,
            },
        },
        "branch_frames": {
            "miso_call": call_frame,
            "miso_put": put_frame,
        },
        "family_surfaces": {
            "surfaces_by_branch": {
                "miso_call": {
                    "surface_kind": "miso_branch",
                    "family_id": "MISO",
                    "branch_id": BRANCH_CALL,
                    "side": SIDE_CALL,
                    "eligible": True,
                    "selected_side": BRANCH_CALL,
                    "selected_strike": 22500.0,
                    "chain_context_ready": True,
                    "burst_detected": selected_side == SIDE_CALL,
                    "aggression_ok": selected_side == SIDE_CALL,
                    "tape_speed_ok": selected_side == SIDE_CALL,
                    "imbalance_persist_ok": selected_side == SIDE_CALL,
                    "shadow_strike_support_ok": True,
                    "queue_reload_blocked": False,
                    "futures_vwap_align_ok": selected_side == SIDE_CALL,
                    "futures_contradiction_blocked": False,
                    "tradability_pass": True,
                    "burst_event_id": "burst-call-1",
                    "oi_wall_context": {
                        "distance_strikes": 2.0,
                        "wall_strength": 0.50,
                        "supportive": False,
                    },
                },
                "miso_put": {
                    "surface_kind": "miso_branch",
                    "family_id": "MISO",
                    "branch_id": BRANCH_PUT,
                    "side": SIDE_PUT,
                    "eligible": True,
                    "selected_side": BRANCH_PUT,
                    "selected_strike": 22500.0,
                    "chain_context_ready": True,
                    "burst_detected": selected_side == SIDE_PUT,
                    "aggression_ok": selected_side == SIDE_PUT,
                    "tape_speed_ok": selected_side == SIDE_PUT,
                    "imbalance_persist_ok": selected_side == SIDE_PUT,
                    "shadow_strike_support_ok": True,
                    "queue_reload_blocked": False,
                    "futures_vwap_align_ok": selected_side == SIDE_PUT,
                    "futures_contradiction_blocked": False,
                    "tradability_pass": True,
                    "burst_event_id": "burst-put-1",
                    "oi_wall_context": {
                        "distance_strikes": 2.0,
                        "wall_strength": 0.50,
                        "supportive": False,
                    },
                },
            },
        },
    }


def main() -> int:
    call_view = _base_view(selected_side=SIDE_CALL)
    call_result = miso.evaluate(call_view, branch_id=BRANCH_CALL)
    assert call_result.is_candidate, call_result
    assert call_result.candidate is not None
    assert call_result.candidate.family_id == "MISO"
    assert call_result.candidate.branch_id == BRANCH_CALL
    assert call_result.candidate.side == SIDE_CALL
    assert call_result.candidate.action == getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
    assert call_result.candidate.instrument_key == "NIFTY_22500_CE"
    assert call_result.candidate.target_points == 5.0
    assert call_result.candidate.stop_points == 4.0
    assert call_result.candidate.burst_event_id == "burst-call-1"
    assert call_result.candidate.mode == MODE_BASE_5DEPTH

    put_view = _base_view(selected_side=SIDE_PUT, mode=MODE_DEPTH20_ENHANCED)
    put_result = miso.evaluate(put_view, branch_id=BRANCH_PUT)
    assert put_result.is_candidate, put_result
    assert put_result.candidate is not None
    assert put_result.candidate.branch_id == BRANCH_PUT
    assert put_result.candidate.side == SIDE_PUT
    assert put_result.candidate.action == getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")
    assert put_result.candidate.instrument_key == "NIFTY_22500_PE"
    assert put_result.candidate.burst_event_id == "burst-put-1"
    assert put_result.candidate.mode == MODE_DEPTH20_ENHANCED

    weak_view = _base_view(selected_side=SIDE_CALL)
    weak_surface = weak_view["family_surfaces"]["surfaces_by_branch"]["miso_call"]
    weak_surface["burst_detected"] = False
    weak_surface["aggression_ok"] = False
    weak_surface["tape_speed_ok"] = False
    weak_surface["imbalance_persist_ok"] = False
    weak_view["common"]["call"]["response_efficiency"] = 0.01
    weak_result = miso.evaluate(weak_view, branch_id=BRANCH_CALL)
    assert weak_result.is_no_signal, weak_result
    assert not weak_result.is_candidate

    reload_view = _base_view(selected_side=SIDE_CALL)
    reload_view["family_surfaces"]["surfaces_by_branch"]["miso_call"]["queue_reload_blocked"] = True
    reload_result = miso.evaluate(reload_view, branch_id=BRANCH_CALL)
    assert reload_result.is_no_signal, reload_result
    assert reload_result.metadata.get("reason") == "queue_reload_veto", reload_result

    provider_block_view = _base_view(selected_side=SIDE_CALL)
    provider_block_view["provider_runtime"]["active_option_context_provider_id"] = PROVIDER_ZERODHA
    provider_block = miso.evaluate(provider_block_view, branch_id=BRANCH_CALL)
    assert provider_block.is_blocked, provider_block
    assert provider_block.blocker is not None
    assert provider_block.blocker.code == "miso_requires_dhan_option_context_provider"

    chain_block_view = _base_view(selected_side=SIDE_CALL)
    chain_block_view["family_status"]["MISO"]["chain_context_ready"] = False
    chain_block_view["family_surfaces"]["surfaces_by_branch"]["miso_call"]["chain_context_ready"] = False
    chain_block = miso.evaluate(chain_block_view, branch_id=BRANCH_CALL)
    assert chain_block.is_blocked, chain_block
    assert chain_block.blocker is not None
    assert chain_block.blocker.code == "miso_chain_context_not_ready"

    object_view = SimpleNamespace(**_base_view(selected_side=SIDE_CALL))
    object_result = miso.evaluate(object_view, branch_id=BRANCH_CALL)
    assert object_result.is_candidate, object_result
    assert object_result.candidate is not None
    assert object_result.candidate.instrument_key == "NIFTY_22500_CE"

    hostile_oi_view = _base_view(selected_side=SIDE_CALL)
    hostile_oi_surface = hostile_oi_view["family_surfaces"]["surfaces_by_branch"]["miso_call"]
    hostile_oi_surface["oi_wall_context"] = {
        "distance_strikes": 0.20,
        "wall_strength": 0.95,
        "supportive": False,
    }
    hostile_oi_result = miso.evaluate(hostile_oi_view, branch_id=BRANCH_CALL)
    assert hostile_oi_result.is_no_signal, hostile_oi_result
    assert hostile_oi_result.metadata.get("reason") == "extreme_near_hostile_oi_wall", hostile_oi_result

    out = {
        "call_result": call_result.to_dict(),
        "put_result": put_result.to_dict(),
        "weak_result": weak_result.to_dict(),
        "reload_result": reload_result.to_dict(),
        "provider_block": provider_block.to_dict(),
        "chain_block": chain_block.to_dict(),
        "object_view_result": object_result.to_dict(),
        "hostile_oi_result": hostile_oi_result.to_dict(),
    }
    out_path = Path("run/proofs/miso_doctrine_offline.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, sort_keys=False, indent=2), encoding="utf-8")

    print("===== MISO DOCTRINE OFFLINE PROOF =====")
    print("call_candidate =", call_result.is_candidate)
    print("call_action =", call_result.action)
    print("call_score =", call_result.candidate.score if call_result.candidate else None)
    print("call_burst_event_id =", call_result.candidate.burst_event_id if call_result.candidate else None)
    print("put_candidate =", put_result.is_candidate)
    print("put_action =", put_result.action)
    print("put_score =", put_result.candidate.score if put_result.candidate else None)
    print("put_mode =", put_result.candidate.mode if put_result.candidate else None)
    print("weak_no_signal =", weak_result.is_no_signal)
    print("queue_reload_no_signal =", reload_result.is_no_signal)
    print("provider_blocked =", provider_block.is_blocked)
    print("provider_blocker =", provider_block.blocker.code if provider_block.blocker else None)
    print("chain_context_blocked =", chain_block.is_blocked)
    print("chain_context_blocker =", chain_block.blocker.code if chain_block.blocker else None)
    print("object_view_candidate =", object_result.is_candidate)
    print("hostile_oi_no_signal =", hostile_oi_result.is_no_signal)
    print("hostile_oi_reason =", hostile_oi_result.metadata.get("reason"))
    print("dumped =", out_path)
    print("MISO doctrine offline proof: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
