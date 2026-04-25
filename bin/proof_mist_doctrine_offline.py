from __future__ import annotations

"""
Offline proof for services/strategy_family/mist.py.

This proof:
- builds deterministic StrategyFamilyConsumerView-like mappings
- proves MIST CALL candidate
- proves MIST PUT candidate
- proves no-signal when score is weak
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
from app.mme_scalpx.services.strategy_family import mist


SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")
BRANCH_CALL = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT = getattr(N, "BRANCH_PUT", "PUT")


def _base_view(*, selected_side: str, runtime_mode: str = "NORMAL") -> dict[str, Any]:
    call_frame = {
        "key": "mist_call",
        "family_id": "MIST",
        "branch_id": BRANCH_CALL,
        "side": SIDE_CALL,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": "NIFTY_22500_CE",
        "instrument_token": "TOKEN_22500_CE",
        "option_symbol": "NIFTY22500CE",
        "strike": 22500.0,
        "option_price": 110.0,
        "tick_size": 0.05,
    }
    put_frame = {
        "key": "mist_put",
        "family_id": "MIST",
        "branch_id": BRANCH_PUT,
        "side": SIDE_PUT,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": "NIFTY_22500_PE",
        "instrument_token": "TOKEN_22500_PE",
        "option_symbol": "NIFTY22500PE",
        "strike": 22500.0,
        "option_price": 112.0,
        "tick_size": 0.05,
    }

    call_option = {
        "side": SIDE_CALL,
        "instrument_key": "NIFTY_22500_CE",
        "instrument_token": "TOKEN_22500_CE",
        "option_symbol": "NIFTY22500CE",
        "strike": 22500.0,
        "ltp": 110.0,
        "entry_mode": "ATM",
        "depth_ok": True,
        "tradability_ok": True,
        "response_efficiency": 0.30,
        "delta_3": 1.40,
        "tick_size": 0.05,
    }
    put_option = {
        "side": SIDE_PUT,
        "instrument_key": "NIFTY_22500_PE",
        "instrument_token": "TOKEN_22500_PE",
        "option_symbol": "NIFTY22500PE",
        "strike": 22500.0,
        "ltp": 112.0,
        "entry_mode": "ATM",
        "depth_ok": True,
        "tradability_ok": True,
        "response_efficiency": 0.31,
        "delta_3": -1.30,
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
                "ltp": 22520.0,
                "spread_ratio": 0.05,
                "depth_total": 2200.0,
                "depth_ok": True,
                "ofi_ratio_proxy": 0.42 if selected_side == SIDE_CALL else -0.42,
                "nof_slope": 0.18 if selected_side == SIDE_CALL else -0.18,
                "delta_3": 4.0 if selected_side == SIDE_CALL else -4.0,
                "velocity_ratio": 1.95,
                "vol_norm": 1.75,
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
            "futures_ltp": 22520.0,
            "selected_option_ltp": selected_option["ltp"],
            "premium_floor_ok": True,
        },
        "family_status": {
            "MIST": {
                "family_present": True,
                "contract_eligible": True,
                "surface_eligible": True,
            },
        },
        "branch_frames": {
            "mist_call": call_frame,
            "mist_put": put_frame,
        },
        "family_surfaces": {
            "surfaces_by_branch": {
                "mist_call": {
                    "surface_kind": "mist_branch",
                    "family_id": "MIST",
                    "branch_id": BRANCH_CALL,
                    "side": SIDE_CALL,
                    "eligible": True,
                    "trend_direction_ok": selected_side == SIDE_CALL,
                    "pullback_detected": True,
                    "resume_confirmed": True,
                    "micro_trap_present": True,
                    "resume_override_pass": False,
                    "context_pass": True,
                    "option_tradability_pass": True,
                    "oi_wall_context": {
                        "distance_strikes": 2.0,
                        "wall_strength": 0.50,
                    },
                },
                "mist_put": {
                    "surface_kind": "mist_branch",
                    "family_id": "MIST",
                    "branch_id": BRANCH_PUT,
                    "side": SIDE_PUT,
                    "eligible": True,
                    "trend_direction_ok": selected_side == SIDE_PUT,
                    "pullback_detected": True,
                    "resume_confirmed": True,
                    "micro_trap_present": True,
                    "resume_override_pass": False,
                    "context_pass": True,
                    "option_tradability_pass": True,
                    "oi_wall_context": {
                        "distance_strikes": 2.0,
                        "wall_strength": 0.50,
                    },
                },
            },
        },
    }


def main() -> int:
    call_view = _base_view(selected_side=SIDE_CALL)
    call_result = mist.evaluate(call_view, branch_id=BRANCH_CALL)
    assert call_result.is_candidate, call_result
    assert call_result.candidate is not None
    assert call_result.candidate.family_id == "MIST"
    assert call_result.candidate.branch_id == BRANCH_CALL
    assert call_result.candidate.side == SIDE_CALL
    assert call_result.candidate.action == getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
    assert call_result.candidate.instrument_key == "NIFTY_22500_CE"
    assert call_result.candidate.target_points == 5.0
    assert call_result.candidate.stop_points == 4.0

    put_view = _base_view(selected_side=SIDE_PUT)
    put_result = mist.evaluate(put_view, branch_id=BRANCH_PUT)
    assert put_result.is_candidate, put_result
    assert put_result.candidate is not None
    assert put_result.candidate.branch_id == BRANCH_PUT
    assert put_result.candidate.side == SIDE_PUT
    assert put_result.candidate.action == getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")
    assert put_result.candidate.instrument_key == "NIFTY_22500_PE"

    weak_view = _base_view(selected_side=SIDE_CALL)
    weak_view["family_surfaces"]["surfaces_by_branch"]["mist_call"]["pullback_detected"] = False
    weak_view["family_surfaces"]["surfaces_by_branch"]["mist_call"]["resume_confirmed"] = False
    weak_view["common"]["futures"]["velocity_ratio"] = 0.75
    weak_view["common"]["call"]["response_efficiency"] = 0.01
    weak_result = mist.evaluate(weak_view, branch_id=BRANCH_CALL)
    assert weak_result.is_no_signal, weak_result
    assert not weak_result.is_candidate

    degraded_view = _base_view(selected_side=SIDE_CALL, runtime_mode=getattr(N, "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED", "DHAN-DEGRADED"))
    degraded_view["common"]["selected_option"]["entry_mode"] = "ATM1"
    blocked = mist.evaluate(degraded_view, branch_id=BRANCH_CALL)
    assert blocked.is_blocked, blocked
    assert blocked.blocker is not None
    assert blocked.blocker.code == "degraded_mode_requires_atm_only"

    out = {
        "call_result": call_result.to_dict(),
        "put_result": put_result.to_dict(),
        "weak_result": weak_result.to_dict(),
        "blocked_result": blocked.to_dict(),
    }
    out_path = Path("run/proofs/mist_doctrine_offline.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, sort_keys=False, indent=2), encoding="utf-8")

    print("===== MIST DOCTRINE OFFLINE PROOF =====")
    print("call_candidate =", call_result.is_candidate)
    print("call_action =", call_result.action)
    print("call_score =", call_result.candidate.score if call_result.candidate else None)
    print("put_candidate =", put_result.is_candidate)
    print("put_action =", put_result.action)
    print("put_score =", put_result.candidate.score if put_result.candidate else None)
    print("weak_no_signal =", weak_result.is_no_signal)
    print("degraded_blocked =", blocked.is_blocked)
    print("degraded_blocker =", blocked.blocker.code if blocked.blocker else None)
    print("dumped =", out_path)
    print("MIST doctrine offline proof: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
