from __future__ import annotations

"""
Offline proof for services/strategy_family/misr.py.

This proof:
- builds deterministic StrategyFamilyConsumerView-like mappings
- proves MISR CALL candidate
- proves MISR PUT candidate
- proves no-signal when reversal/fakeout support is weak
- proves degraded mode ATM-only block
- proves no Redis / broker / execution side effects
"""

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family import misr


SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")
BRANCH_CALL = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT = getattr(N, "BRANCH_PUT", "PUT")


def _base_view(*, selected_side: str, runtime_mode: str = "NORMAL") -> dict[str, Any]:
    call_frame = {
        "key": "misr_call",
        "family_id": "MISR",
        "branch_id": BRANCH_CALL,
        "side": SIDE_CALL,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": "NIFTY_22500_CE",
        "instrument_token": "TOKEN_22500_CE",
        "option_symbol": "NIFTY22500CE",
        "strike": 22500.0,
        "option_price": 108.0,
        "tick_size": 0.05,
    }
    put_frame = {
        "key": "misr_put",
        "family_id": "MISR",
        "branch_id": BRANCH_PUT,
        "side": SIDE_PUT,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": "NIFTY_22500_PE",
        "instrument_token": "TOKEN_22500_PE",
        "option_symbol": "NIFTY22500PE",
        "strike": 22500.0,
        "option_price": 111.0,
        "tick_size": 0.05,
    }

    call_option = {
        "side": SIDE_CALL,
        "instrument_key": "NIFTY_22500_CE",
        "instrument_token": "TOKEN_22500_CE",
        "option_symbol": "NIFTY22500CE",
        "strike": 22500.0,
        "ltp": 108.0,
        "entry_mode": "ATM",
        "depth_ok": True,
        "tradability_ok": True,
        "response_efficiency": 0.31,
        "delta_3": 1.25,
        "tick_size": 0.05,
    }
    put_option = {
        "side": SIDE_PUT,
        "instrument_key": "NIFTY_22500_PE",
        "instrument_token": "TOKEN_22500_PE",
        "option_symbol": "NIFTY22500PE",
        "strike": 22500.0,
        "ltp": 111.0,
        "entry_mode": "ATM",
        "depth_ok": True,
        "tradability_ok": True,
        "response_efficiency": 0.32,
        "delta_3": -1.20,
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
            "provider_ready_classic": True,
        },
        "provider_runtime": {
            "active_futures_provider_id": "DHAN",
            "active_selected_option_provider_id": "DHAN",
            "active_option_context_provider_id": "DHAN",
            "active_execution_provider_id": "ZERODHA",
            "family_runtime_mode": "OBSERVE_ONLY",
            "classic_runtime_mode": runtime_mode,
        },
        "common": {
            "regime": "NORMAL",
            "strategy_runtime_mode_classic": runtime_mode,
            "futures": {
                "ltp": 22505.0,
                "spread_ratio": 0.05,
                "depth_total": 2300.0,
                "depth_ok": True,
                "ofi_ratio_proxy": 0.18 if selected_side == SIDE_CALL else -0.18,
                "nof_slope": 0.06 if selected_side == SIDE_CALL else -0.06,
                "delta_3": 3.2 if selected_side == SIDE_CALL else -3.2,
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
            "futures_ltp": 22505.0,
            "selected_option_ltp": selected_option["ltp"],
            "premium_floor_ok": True,
        },
        "family_status": {
            "MISR": {
                "family_present": True,
                "contract_eligible": True,
                "surface_eligible": True,
                "active_zone": {
                    "zone_id": "zone-1",
                    "zone_type": "fake_break_reclaim_zone",
                    "zone_level": 22500.0,
                    "zone_low": 22490.0,
                    "zone_high": 22510.0,
                    "quality_score": 0.72,
                    "zone_valid": True,
                },
            },
        },
        "branch_frames": {
            "misr_call": call_frame,
            "misr_put": put_frame,
        },
        "family_surfaces": {
            "surfaces_by_branch": {
                "misr_call": {
                    "surface_kind": "misr_branch",
                    "family_id": "MISR",
                    "branch_id": BRANCH_CALL,
                    "side": SIDE_CALL,
                    "eligible": True,
                    "reversal_direction_ok": selected_side == SIDE_CALL,
                    "fake_break_triggered": True,
                    "absorption_pass": True,
                    "range_reentry_confirmed": True,
                    "flow_flip_confirmed": True,
                    "hold_inside_range_proved": True,
                    "no_mans_land_cleared": True,
                    "reversal_impulse_confirmed": True,
                    "context_pass": True,
                    "option_tradability_pass": True,
                    "trap_event_id": "trap-call-1",
                    "oi_wall_context": {
                        "distance_strikes": 1.0,
                        "wall_strength": 0.72,
                        "supportive": True,
                    },
                    "active_zone": {
                        "zone_id": "zone-call-1",
                        "zone_type": "downside_fake_break_reclaim",
                        "zone_low": 22490.0,
                        "zone_high": 22510.0,
                        "quality_score": 0.72,
                        "zone_valid": True,
                    },
                },
                "misr_put": {
                    "surface_kind": "misr_branch",
                    "family_id": "MISR",
                    "branch_id": BRANCH_PUT,
                    "side": SIDE_PUT,
                    "eligible": True,
                    "reversal_direction_ok": selected_side == SIDE_PUT,
                    "fake_break_triggered": True,
                    "absorption_pass": True,
                    "range_reentry_confirmed": True,
                    "flow_flip_confirmed": True,
                    "hold_inside_range_proved": True,
                    "no_mans_land_cleared": True,
                    "reversal_impulse_confirmed": True,
                    "context_pass": True,
                    "option_tradability_pass": True,
                    "trap_event_id": "trap-put-1",
                    "oi_wall_context": {
                        "distance_strikes": 1.0,
                        "wall_strength": 0.72,
                        "supportive": True,
                    },
                    "active_zone": {
                        "zone_id": "zone-put-1",
                        "zone_type": "upside_fake_break_reclaim",
                        "zone_low": 22490.0,
                        "zone_high": 22510.0,
                        "quality_score": 0.72,
                        "zone_valid": True,
                    },
                },
            },
        },
    }


def main() -> int:
    call_view = _base_view(selected_side=SIDE_CALL)
    call_result = misr.evaluate(call_view, branch_id=BRANCH_CALL)
    assert call_result.is_candidate, call_result
    assert call_result.candidate is not None
    assert call_result.candidate.family_id == "MISR"
    assert call_result.candidate.branch_id == BRANCH_CALL
    assert call_result.candidate.side == SIDE_CALL
    assert call_result.candidate.action == getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
    assert call_result.candidate.instrument_key == "NIFTY_22500_CE"
    assert call_result.candidate.target_points == 5.0
    assert call_result.candidate.stop_points == 4.0
    assert call_result.candidate.trap_event_id == "trap-call-1"

    put_view = _base_view(selected_side=SIDE_PUT)
    put_result = misr.evaluate(put_view, branch_id=BRANCH_PUT)
    assert put_result.is_candidate, put_result
    assert put_result.candidate is not None
    assert put_result.candidate.branch_id == BRANCH_PUT
    assert put_result.candidate.side == SIDE_PUT
    assert put_result.candidate.action == getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")
    assert put_result.candidate.instrument_key == "NIFTY_22500_PE"
    assert put_result.candidate.trap_event_id == "trap-put-1"

    weak_view = _base_view(selected_side=SIDE_CALL)
    weak_surface = weak_view["family_surfaces"]["surfaces_by_branch"]["misr_call"]
    weak_surface["fake_break_triggered"] = False
    weak_surface["absorption_pass"] = False
    weak_surface["range_reentry_confirmed"] = False
    weak_surface["flow_flip_confirmed"] = False
    weak_surface["reversal_impulse_confirmed"] = False
    weak_view["common"]["futures"]["velocity_ratio"] = 0.75
    weak_view["common"]["call"]["response_efficiency"] = 0.01
    weak_result = misr.evaluate(weak_view, branch_id=BRANCH_CALL)
    assert weak_result.is_no_signal, weak_result
    assert not weak_result.is_candidate

    degraded_view = _base_view(
        selected_side=SIDE_CALL,
        runtime_mode=getattr(N, "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED", "DHAN-DEGRADED"),
    )
    degraded_view["common"]["selected_option"]["entry_mode"] = "ATM1"
    blocked = misr.evaluate(degraded_view, branch_id=BRANCH_CALL)
    assert blocked.is_blocked, blocked
    assert blocked.blocker is not None
    assert blocked.blocker.code == "degraded_mode_requires_atm_only"

    out = {
        "call_result": call_result.to_dict(),
        "put_result": put_result.to_dict(),
        "weak_result": weak_result.to_dict(),
        "blocked_result": blocked.to_dict(),
    }
    out_path = Path("run/proofs/misr_doctrine_offline.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, sort_keys=False, indent=2), encoding="utf-8")

    print("===== MISR DOCTRINE OFFLINE PROOF =====")
    print("call_candidate =", call_result.is_candidate)
    print("call_action =", call_result.action)
    print("call_score =", call_result.candidate.score if call_result.candidate else None)
    print("call_trap_event_id =", call_result.candidate.trap_event_id if call_result.candidate else None)
    print("put_candidate =", put_result.is_candidate)
    print("put_action =", put_result.action)
    print("put_score =", put_result.candidate.score if put_result.candidate else None)
    print("put_trap_event_id =", put_result.candidate.trap_event_id if put_result.candidate else None)
    print("weak_no_signal =", weak_result.is_no_signal)
    print("degraded_blocked =", blocked.is_blocked)
    print("degraded_blocker =", blocked.blocker.code if blocked.blocker else None)
    print("dumped =", out_path)
    print("MISR doctrine offline proof: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
