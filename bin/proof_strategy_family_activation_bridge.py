#!/usr/bin/env python3
from __future__ import annotations

"""
Offline proof for strategy-family activation bridge.

This proof verifies:
- activation bridge imports
- all five doctrine leaves can be consumed
- default mode remains HOLD
- dry-run mode remains HOLD
- paper_armed mode can promote only with explicit allow_candidate_promotion=True
- live orders are never enabled
- unsafe consumer views remain HOLD
- no Redis / broker / execution side effects exist in activation.py
"""

import ast
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family import activation


SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")
BRANCH_CALL = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT = getattr(N, "BRANCH_PUT", "PUT")
PROVIDER_DHAN = getattr(N, "PROVIDER_DHAN", "DHAN")
PROVIDER_ZERODHA = getattr(N, "PROVIDER_ZERODHA", "ZERODHA")


def _branch_frame(family: str, branch: str) -> dict[str, Any]:
    side = SIDE_CALL if branch == BRANCH_CALL else SIDE_PUT
    suffix = "CE" if branch == BRANCH_CALL else "PE"
    price = 125.0 if branch == BRANCH_CALL else 128.0
    return {
        "key": f"{family.lower()}_{branch.lower()}",
        "family_id": family,
        "branch_id": branch,
        "side": side,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": f"NIFTY_22500_{suffix}",
        "instrument_token": f"TOKEN_22500_{suffix}",
        "option_symbol": f"NIFTY22500{suffix}",
        "strike": 22500.0,
        "option_price": price,
        "tick_size": 0.05,
    }


def _surface(family: str, branch: str, *, selected_branch: str) -> dict[str, Any]:
    selected = branch == selected_branch
    side = SIDE_CALL if branch == BRANCH_CALL else SIDE_PUT

    base = {
        "surface_kind": f"{family.lower()}_branch",
        "family_id": family,
        "branch_id": branch,
        "side": side,
        "eligible": True,
        "context_pass": True,
        "option_tradability_pass": True,
        "oi_wall_context": {"distance_strikes": 2.0, "wall_strength": 0.40, "supportive": False},
    }

    if family == "MIST":
        base.update({
            "futures_bias_ok": selected,
            "futures_impulse_ok": selected,
            "pullback_detected": selected,
            "resume_confirmed": selected,
            "micro_trap_blocked": False,
        })
    elif family == "MISB":
        base.update({
            "futures_bias_ok": selected,
            "shelf_valid": selected,
            "breakout_triggered": selected,
            "breakout_accepted": selected,
        })
    elif family == "MISC":
        base.update({
            "compression_detected": selected,
            "compression_width_ok": selected,
            "prebreak_proximity_ok": selected,
            "compression_cluster_score": 0.80,
            "breakout_trigger_ok": selected,
            "expansion_acceptance_ok": selected,
            "retest_valid": selected and branch == BRANCH_CALL,
            "hesitation_valid": selected and branch == BRANCH_PUT,
            "resume_confirmation_ok": selected,
            "retest_depth_ok": True,
        })
    elif family == "MISR":
        base.update({
            "reversal_direction_ok": selected,
            "fake_break_triggered": selected,
            "absorption_pass": selected,
            "range_reentry_confirmed": selected,
            "flow_flip_confirmed": selected,
            "hold_inside_range_proved": selected,
            "no_mans_land_cleared": selected,
            "reversal_impulse_confirmed": selected,
            "trap_event_id": f"trap-{branch.lower()}",
            "active_zone": {"zone_id": "zone-1", "quality_score": 0.72, "zone_valid": True},
        })
    elif family == "MISO":
        base.update({
            "selected_side": selected_branch,
            "selected_strike": 22500.0,
            "chain_context_ready": True,
            "burst_detected": selected,
            "aggression_ok": selected,
            "tape_speed_ok": selected,
            "imbalance_persist_ok": selected,
            "shadow_strike_support_ok": True,
            "queue_reload_blocked": False,
            "futures_vwap_align_ok": selected,
            "futures_contradiction_blocked": False,
            "tradability_pass": True,
            "burst_event_id": f"burst-{branch.lower()}",
        })

    return base


def _activation_view(*, selected_branch: str = BRANCH_CALL, safe: bool = True) -> dict[str, Any]:
    selected_side = SIDE_CALL if selected_branch == BRANCH_CALL else SIDE_PUT
    selected_option = {
        "side": selected_side,
        "instrument_key": "NIFTY_22500_CE" if selected_branch == BRANCH_CALL else "NIFTY_22500_PE",
        "instrument_token": "TOKEN_22500_CE" if selected_branch == BRANCH_CALL else "TOKEN_22500_PE",
        "option_symbol": "NIFTY22500CE" if selected_branch == BRANCH_CALL else "NIFTY22500PE",
        "strike": 22500.0,
        "ltp": 125.0 if selected_branch == BRANCH_CALL else 128.0,
        "entry_mode": "ATM",
        "depth_ok": True,
        "tradability_ok": True,
        "response_efficiency": 0.35,
        "delta_3": 1.65 if selected_branch == BRANCH_CALL else -1.65,
        "tick_size": 0.05,
    }

    call_option = dict(selected_option, side=SIDE_CALL, instrument_key="NIFTY_22500_CE", instrument_token="TOKEN_22500_CE", option_symbol="NIFTY22500CE", ltp=125.0, delta_3=1.65)
    put_option = dict(selected_option, side=SIDE_PUT, instrument_key="NIFTY_22500_PE", instrument_token="TOKEN_22500_PE", option_symbol="NIFTY22500PE", ltp=128.0, delta_3=-1.65)

    families = ("MIST", "MISB", "MISC", "MISR", "MISO")
    branches = (BRANCH_CALL, BRANCH_PUT)

    return {
        "view_version": "strategy-family-consumer-view.v1",
        "safe_to_consume": safe,
        "hold_only": True,
        "action": "HOLD",
        "data_valid": safe,
        "warmup_complete": True,
        "provider_ready_classic": True,
        "provider_ready_miso": True,
        "regime": "NORMAL",
        "stage_flags": {
            "data_valid": safe,
            "data_quality_ok": safe,
            "session_eligible": True,
            "warmup_complete": True,
            "risk_veto_active": False,
            "reconciliation_lock_active": False,
            "active_position_present": False,
            "provider_ready_classic": True,
            "provider_ready_miso": True,
            "dhan_context_fresh": True,
        },
        "provider_runtime": {
            "active_futures_provider_id": PROVIDER_DHAN,
            "active_selected_option_provider_id": PROVIDER_DHAN,
            "active_option_context_provider_id": PROVIDER_DHAN,
            "active_execution_provider_id": PROVIDER_ZERODHA,
            "fallback_execution_provider_id": PROVIDER_DHAN,
            "family_runtime_mode": "OBSERVE_ONLY",
            "classic_runtime_mode": "NORMAL",
            "miso_runtime_mode": "BASE-5DEPTH",
        },
        "common": {
            "regime": "NORMAL",
            "strategy_runtime_mode_classic": "NORMAL",
            "strategy_runtime_mode_miso": "BASE-5DEPTH",
            "futures": {
                "ltp": 22525.0,
                "depth_ok": True,
                "ofi_ratio_proxy": 0.30 if selected_branch == BRANCH_CALL else -0.30,
                "nof_slope": 0.10 if selected_branch == BRANCH_CALL else -0.10,
                "delta_3": 4.0 if selected_branch == BRANCH_CALL else -4.0,
                "velocity_ratio": 1.80,
                "vol_norm": 1.50,
                "above_vwap": selected_branch == BRANCH_CALL,
                "below_vwap": selected_branch == BRANCH_PUT,
            },
            "call": call_option,
            "put": put_option,
            "selected_option": selected_option,
            "cross_option": {"cross_option_ready": True},
        },
        "market": {
            "active_branch_hint": selected_branch,
            "futures_ltp": 22525.0,
            "selected_option_ltp": selected_option["ltp"],
            "premium_floor_ok": True,
        },
        "family_status": {
            family: {
                "family_present": True,
                "eligible": True,
                "contract_eligible": True,
                "surface_eligible": True,
                "mode": "BASE-5DEPTH",
                "chain_context_ready": True,
                "selected_side": selected_branch,
                "selected_strike": 22500.0,
                "shadow_call_strike": 22550.0,
                "shadow_put_strike": 22450.0,
            }
            for family in families
        },
        "branch_frames": {
            f"{family.lower()}_{branch.lower()}": _branch_frame(family, branch)
            for family in families
            for branch in branches
        },
        "family_surfaces": {
            "surfaces_by_branch": {
                f"{family.lower()}_{branch.lower()}": _surface(family, branch, selected_branch=selected_branch)
                for family in families
                for branch in branches
            }
        },
        "shared_core": {
            "oi_wall_context": {
                "call": {"distance_strikes": 2.0, "wall_strength": 0.40, "supportive": False},
                "put": {"distance_strikes": 2.0, "wall_strength": 0.40, "supportive": False},
            }
        },
    }


def _ownership_ast_check() -> None:
    path = PROJECT_ROOT / "app/mme_scalpx/services/strategy_family/activation.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden_imports = ("redis", "broker", "execution")
    forbidden_calls = {
        "hgetall", "hset", "xadd", "xread", "publish",
        "place_order", "send_order", "create_order", "modify_order", "cancel_order",
    }

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(fragment in alias.name.lower() for fragment in forbidden_imports):
                    violations.append(f"forbidden import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").lower()
            if any(fragment in module for fragment in forbidden_imports):
                violations.append(f"forbidden import-from {node.module}")
        elif isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name.lower() in forbidden_calls:
                violations.append(f"forbidden call {name}")

    if violations:
        raise AssertionError(violations)


def main() -> int:
    view = _activation_view(selected_branch=BRANCH_CALL)

    frames = activation.collect_doctrine_evaluations(view)
    assert len(frames) == 10, len(frames)
    assert any(frame.is_candidate for frame in frames), [f.to_dict() for f in frames]

    hold = activation.build_activation_decision(view)
    assert hold.hold is True, hold
    assert hold.promoted is False, hold
    assert hold.action == "HOLD", hold
    assert hold.selected is not None, hold
    assert hold.reason == "candidate_observed_hold_only", hold

    dry = activation.evaluate_activation(view, activation_mode="dry_run")
    assert dry.hold is True, dry
    assert dry.promoted is False, dry
    assert dry.action == "HOLD", dry
    assert dry.selected is not None, dry
    assert dry.reason == "candidate_observed_dry_run", dry

    paper_blocked = activation.evaluate_activation(
        view,
        activation_mode="paper_armed",
        allow_candidate_promotion=False,
    )
    assert paper_blocked.hold is True, paper_blocked
    assert paper_blocked.promoted is False, paper_blocked
    assert paper_blocked.reason == "promotion_not_allowed", paper_blocked

    paper_promoted = activation.evaluate_activation(
        view,
        activation_mode="paper_armed",
        allow_candidate_promotion=True,
    )
    assert paper_promoted.hold is False, paper_promoted
    assert paper_promoted.promoted is True, paper_promoted
    assert paper_promoted.safe_to_promote is True, paper_promoted
    assert paper_promoted.action in {
        getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL"),
        getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT"),
    }, paper_promoted
    assert paper_promoted.metadata.get("live_orders_allowed") is False, paper_promoted

    unsafe = activation.evaluate_activation(
        _activation_view(selected_branch=BRANCH_CALL, safe=False),
        activation_mode="paper_armed",
        allow_candidate_promotion=True,
    )
    assert unsafe.hold is True, unsafe
    assert unsafe.promoted is False, unsafe
    assert unsafe.reason in {"view_not_safe_to_consume", "view_data_invalid"}, unsafe

    object_view = SimpleNamespace(**_activation_view(selected_branch=BRANCH_CALL))
    object_decision = activation.evaluate_activation(object_view, activation_mode="dry_run")
    assert object_decision.hold is True, object_decision
    assert object_decision.selected is not None, object_decision

    put_view = _activation_view(selected_branch=BRANCH_PUT)
    put_decision = activation.evaluate_activation(put_view, activation_mode="dry_run")
    assert put_decision.hold is True, put_decision
    assert put_decision.selected is not None, put_decision

    _ownership_ast_check()

    out = {
        "frame_count": len(frames),
        "candidate_count": len([f for f in frames if f.is_candidate]),
        "blocked_count": len([f for f in frames if f.is_blocked]),
        "no_signal_count": len([f for f in frames if f.is_no_signal]),
        "hold": hold.to_dict(),
        "dry": dry.to_dict(),
        "paper_blocked": paper_blocked.to_dict(),
        "paper_promoted": paper_promoted.to_dict(),
        "unsafe": unsafe.to_dict(),
        "object_decision": object_decision.to_dict(),
        "put_decision": put_decision.to_dict(),
    }

    out_path = PROJECT_ROOT / "run/proofs/strategy_family_activation_bridge.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")

    print("===== STRATEGY FAMILY ACTIVATION BRIDGE PROOF =====")
    print("frame_count =", out["frame_count"])
    print("candidate_count =", out["candidate_count"])
    print("hold_action =", hold.action)
    print("hold_reason =", hold.reason)
    print("dry_action =", dry.action)
    print("dry_reason =", dry.reason)
    print("paper_blocked_reason =", paper_blocked.reason)
    print("paper_promoted =", paper_promoted.promoted)
    print("paper_promoted_action =", paper_promoted.action)
    print("unsafe_hold =", unsafe.hold)
    print("object_view_selected =", object_decision.selected.family_id if object_decision.selected else None)
    print("put_view_selected =", put_decision.selected.family_id if put_decision.selected else None)
    print("ownership_ast = OK")
    print("dumped =", out_path.relative_to(PROJECT_ROOT))
    print("strategy-family activation bridge proof: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
