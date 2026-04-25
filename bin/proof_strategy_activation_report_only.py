#!/usr/bin/env python3
from __future__ import annotations

"""
Offline proof for strategy.py activation report-only integration.

This proves:
- strategy.py imports activation bridge
- StrategyFamilyConsumerBridge still builds HOLD decision
- qty remains 0
- action remains HOLD
- activation report is attached
- observed doctrine candidate can be reported
- no live promotion occurs
"""

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import strategy
from app.mme_scalpx.services.feature_family import contracts as FF_C
from app.mme_scalpx.services.feature_family import common as FF_H


SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")
BRANCH_CALL = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT = getattr(N, "BRANCH_PUT", "PUT")
PROVIDER_DHAN = getattr(N, "PROVIDER_DHAN", "DHAN")
PROVIDER_ZERODHA = getattr(N, "PROVIDER_ZERODHA", "ZERODHA")


def _family_features_version() -> str:
    return str(
        getattr(
            FF_C,
            "FAMILY_FEATURES_VERSION",
            getattr(FF_C, "FAMILY_FEATURES_PAYLOAD_VERSION", "1.1"),
        )
    )



def _contract_keys_by_markers(*markers: str) -> tuple[str, ...]:
    """
    Find the live FF_C *_KEYS constant matching required marker fields.
    This keeps the proof fixture aligned with contracts.py without hardcoding
    every nested exact-key set.
    """
    wanted = set(markers)
    for name in sorted(dir(FF_C)):
        if not name.endswith("_KEYS"):
            continue
        value = getattr(FF_C, name, None)
        if not isinstance(value, (tuple, list)):
            continue
        keys = tuple(str(k) for k in value)
        if wanted.issubset(set(keys)):
            return keys
    return ()


def _default_contract_value(key: str, *, selected_branch: str, side: str | None = None) -> Any:
    selected_side = SIDE_CALL if selected_branch == BRANCH_CALL else SIDE_PUT

    numeric_defaults = {
        "atm_strike": 22500.0,
        "selected_call_strike": 22500.0,
        "selected_put_strike": 22500.0,
        "futures_ltp": 22525.0,
        "call_ltp": 125.0,
        "put_ltp": 128.0,
        "selected_option_ltp": 125.0 if selected_branch == BRANCH_CALL else 128.0,
        "ltp": 125.0 if side == SIDE_CALL else 128.0 if side == SIDE_PUT else 22525.0,
        "best_bid": 124.95 if side == SIDE_CALL else 127.95 if side == SIDE_PUT else 22524.95,
        "best_ask": 125.05 if side == SIDE_CALL else 128.05 if side == SIDE_PUT else 22525.05,
        "spread": 0.10,
        "spread_ratio": 0.05,
        "depth_total": 2500.0,
        "top5_bid_qty": 1300.0,
        "top5_ask_qty": 1200.0,
        "bid_qty_5": 1300.0,
        "ask_qty_5": 1200.0,
        "ofi_ratio_proxy": 0.30 if selected_branch == BRANCH_CALL else -0.30,
        "ofi_persist_score": 0.30 if selected_branch == BRANCH_CALL else -0.30,
        "microprice": 22525.05,
        "micro_edge": 0.05 if selected_branch == BRANCH_CALL else -0.05,
        "vwap": 22520.0,
        "vwap_dist_pct": 0.02,
        "ema_9": 22522.0,
        "ema_21": 22518.0,
        "ema9_slope": 0.10 if selected_branch == BRANCH_CALL else -0.10,
        "ema21_slope": 0.05 if selected_branch == BRANCH_CALL else -0.05,
        "delta_3": 4.0 if side is None else 1.65 if side == SIDE_CALL else -1.65,
        "vel_3": 1.20,
        "vel_ratio": 1.80,
        "velocity_ratio": 1.80,
        "vol_delta": 100.0,
        "vol_norm": 1.50,
        "range_fast": 6.0,
        "range_slow": 12.0,
        "range_ratio": 0.50,
        "response_efficiency": 0.35,
        "context_score": 0.70,
        "context_iv": 12.5,
        "context_oi": 5000.0,
        "volume": 2500.0,
        "delta_proxy": 0.55 if side == SIDE_CALL else -0.55 if side == SIDE_PUT else 0.0,
        "strike": 22500.0,
        "slippage_estimate": 0.05,
        "cost_estimate": 0.0,
        "net_edge_estimate": 5.0,
        "spread_rupees": 0.10,
        "futures_bias": 1.0 if selected_branch == BRANCH_CALL else -1.0,
        "futures_impulse": 1.0,
        "call_minus_put_ltp": -3.0 if selected_branch == BRANCH_CALL else 3.0,
        "call_put_depth_ratio": 1.0,
        "call_put_spread_ratio": 1.0,
    }

    bool_defaults = {
        "valid": True,
        "sync_ok": True,
        "freshness_ok": True,
        "packet_gap_ok": True,
        "warmup_ok": True,
        "depth_ok": True,
        "above_vwap": selected_branch == BRANCH_CALL,
        "below_vwap": selected_branch == BRANCH_PUT,
        "premium_floor_ok": True,
        "economics_valid": True,
        "options_confirmation": True,
        "liquidity_ok": True,
        "alignment_ok": True,
        "spread_ratio_ok": True,
        "response_efficiency_ok": True,
        "tradability_ok": True,
        "selected_option_present": True,
        "cross_option_ready": True,
    }

    # Contract aliases/defaults for economics and signals blocks.
    numeric_defaults.update(
        {
            "target_points": 5.0,
            "stop_points": 4.0,
            "target_pct": 0.0,
            "stop_pct": 0.0,
            "futures_bias": 1.0 if selected_branch == BRANCH_CALL else -1.0,
            "futures_impulse": 1.0,
            "option_confirmation_score": 1.0,
            "liquidity_score": 1.0,
            "alignment_score": 1.0,
            "four_pillar_score": 1.0,
            "delta_proxy_norm": 1.0 if selected_branch == BRANCH_CALL else -1.0,
        }
    )
    bool_defaults.update(
        {
            "premium_floor_ok": True,
            "economic_viability_ok": True,
            "four_pillar_signal": True,
            "futures_contradiction_flag": False,
            "queue_reload_veto_flag": False,
            "options_confirmation": True,
            "liquidity_ok": True,
            "alignment_ok": True,
            "context_ok": True,
            "tradability_ok": True,
        }
    )

    if key in numeric_defaults:
        return numeric_defaults[key]
    if key in bool_defaults:
        return bool_defaults[key]

    if key == "side":
        return side or selected_side
    if key == "active_branch_hint":
        return selected_branch
    if key == "options_side":
        return selected_side
    if key == "instrument_key":
        return "NIFTY_22500_CE" if side == SIDE_CALL else "NIFTY_22500_PE" if side == SIDE_PUT else "NIFTY_FUT"
    if key == "instrument_token":
        return "TOKEN_22500_CE" if side == SIDE_CALL else "TOKEN_22500_PE" if side == SIDE_PUT else "TOKEN_NIFTY_FUT"
    if key in {"option_symbol", "trading_symbol"}:
        return "NIFTY22500CE" if side == SIDE_CALL else "NIFTY22500PE" if side == SIDE_PUT else "NIFTYFUT"
    if key == "provider_id":
        return PROVIDER_DHAN
    if key == "validity":
        return "OK"
    if key.endswith("_ns"):
        return 1800000000000000000
    if key.endswith("_ms"):
        return 0
    if key == "samples_seen":
        return 24

    return None


def _coerce_exact_keys(
    block: Mapping[str, Any],
    keys: tuple[str, ...],
    *,
    selected_branch: str,
    side: str | None = None,
) -> dict[str, Any]:
    source = dict(block or {})

    # Alias old proof-fixture names into frozen contract names.
    if "velocity_ratio" in source and "vel_ratio" not in source:
        source["vel_ratio"] = source["velocity_ratio"]
    if "nof_slope" in source and "ofi_persist_score" not in source:
        source["ofi_persist_score"] = source["nof_slope"]

    out: dict[str, Any] = {}
    for key in keys:
        out[key] = source.get(
            key,
            _default_contract_value(key, selected_branch=selected_branch, side=side),
        )
    return out


def _normalize_family_features_for_contract(
    family_features: dict[str, Any],
    *,
    selected_branch: str,
) -> dict[str, Any]:
    """
    Normalize the synthetic proof fixture to the exact live FF_C contract keys.
    This is only for the proof harness; production strategy.py still validates
    whatever features.py publishes.
    """
    ff = dict(family_features)

    # Top-level blocks.
    snapshot_keys = _contract_keys_by_markers("valid", "validity", "samples_seen")
    provider_keys = _contract_keys_by_markers("active_futures_provider_id", "execution_provider_status")
    market_keys = _contract_keys_by_markers("atm_strike", "selected_option_ltp", "premium_floor_ok")
    common_keys = _contract_keys_by_markers("regime", "futures", "selected_option", "economics", "signals")
    futures_keys = _contract_keys_by_markers("ltp", "microprice", "delta_3", "range_ratio")
    option_keys = tuple(str(k) for k in getattr(FF_C, "COMMON_OPTION_KEYS", ()))
    selected_option_keys = tuple(str(k) for k in getattr(FF_C, "COMMON_SELECTED_OPTION_KEYS", ()))
    cross_keys = (
        tuple(str(k) for k in getattr(FF_C, "COMMON_CROSS_OPTION_KEYS", ()))
        or _contract_keys_by_markers(
            "call_minus_put_ltp",
            "call_put_depth_ratio",
            "call_put_spread_ratio",
        )
    )
    economics_keys = (
        tuple(str(k) for k in getattr(FF_C, "COMMON_ECONOMICS_KEYS", ()))
        or _contract_keys_by_markers(
            "premium_floor_ok",
            "target_points",
            "stop_points",
            "economic_viability_ok",
        )
    )
    signals_keys = (
        tuple(str(k) for k in getattr(FF_C, "COMMON_SIGNALS_KEYS", ()))
        or _contract_keys_by_markers(
            "futures_bias",
            "options_confirmation",
            "liquidity_ok",
            "alignment_ok",
        )
    )

    if snapshot_keys:
        ff["snapshot"] = _coerce_exact_keys(ff.get("snapshot", {}), snapshot_keys, selected_branch=selected_branch)

    if provider_keys:
        # Provider-runtime values must be contract-valid literals.
        pr = dict(ff.get("provider_runtime", {}))
        pr.setdefault("provider_runtime_mode", "NORMAL")
        pr.setdefault("family_runtime_mode", "OBSERVE_ONLY")
        pr.setdefault("futures_provider_status", "HEALTHY")
        pr.setdefault("selected_option_provider_status", "HEALTHY")
        pr.setdefault("option_context_provider_status", "HEALTHY")
        pr.setdefault("execution_provider_status", "HEALTHY")
        ff["provider_runtime"] = _coerce_exact_keys(pr, provider_keys, selected_branch=selected_branch)

    if market_keys:
        ff["market"] = _coerce_exact_keys(ff.get("market", {}), market_keys, selected_branch=selected_branch)

    common = dict(ff.get("common", {}))
    if futures_keys:
        common["futures"] = _coerce_exact_keys(common.get("futures", {}), futures_keys, selected_branch=selected_branch)

    if option_keys:
        common["call"] = _coerce_exact_keys(
            common.get("call", {}),
            option_keys,
            selected_branch=selected_branch,
            side=SIDE_CALL,
        )
        common["put"] = _coerce_exact_keys(
            common.get("put", {}),
            option_keys,
            selected_branch=selected_branch,
            side=SIDE_PUT,
        )

    if selected_option_keys:
        selected_side = SIDE_CALL if selected_branch == BRANCH_CALL else SIDE_PUT
        common["selected_option"] = _coerce_exact_keys(
            common.get("selected_option", {}),
            selected_option_keys,
            selected_branch=selected_branch,
            side=selected_side,
        )

    if cross_keys:
        cross = dict(common.get("cross_option", {}))
        cross.setdefault("selected_option_present", True)
        cross.setdefault("nearest_call_oi_resistance_strike", 22600.0)
        cross.setdefault("nearest_put_oi_support_strike", 22400.0)
        cross.setdefault("call_wall_distance_pts", 100.0)
        cross.setdefault("put_wall_distance_pts", 100.0)
        cross.setdefault("call_wall_strength_score", 0.40)
        cross.setdefault("put_wall_strength_score", 0.40)
        cross.setdefault("oi_bias", "NEUTRAL")
        common["cross_option"] = _coerce_exact_keys(cross, cross_keys, selected_branch=selected_branch)

    if economics_keys:
        common["economics"] = _coerce_exact_keys(common.get("economics", {}), economics_keys, selected_branch=selected_branch)

    if signals_keys:
        common["signals"] = _coerce_exact_keys(common.get("signals", {}), signals_keys, selected_branch=selected_branch)

    if common_keys:
        # Preserve existing simple scalar fields.
        common.setdefault("regime", "NORMAL")
        common.setdefault("strategy_runtime_mode_classic", "NORMAL")
        common.setdefault("strategy_runtime_mode_miso", "BASE_5DEPTH")
        ff["common"] = _coerce_exact_keys(common, common_keys, selected_branch=selected_branch)
    else:
        ff["common"] = common

    return ff


def _branch_frame(family: str, branch: str) -> dict[str, Any]:
    suffix = "CE" if branch == BRANCH_CALL else "PE"
    side = SIDE_CALL if branch == BRANCH_CALL else SIDE_PUT
    return {
        "family_id": family,
        "branch_id": branch,
        "side": side,
        "eligible": True,
        "tradability_ok": True,
        "instrument_key": f"NIFTY_22500_{suffix}",
        "instrument_token": f"TOKEN_22500_{suffix}",
        "option_symbol": f"NIFTY22500{suffix}",
        "strike": 22500.0,
        "option_price": 125.0 if branch == BRANCH_CALL else 128.0,
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
        "oi_wall_context": {
            "distance_strikes": 2.0,
            "wall_strength": 0.40,
            "supportive": False,
        },
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



def _builder_call(name: str, **available: Any) -> dict[str, Any]:
    """
    Call feature_family.common builder with only accepted kwargs.

    The proof fixture should track the frozen support-shape builders instead
    of hand-writing family support placeholders.
    """
    fn = getattr(FF_H, name, None)
    if not callable(fn):
        return {}

    import inspect

    sig = inspect.signature(fn)
    params = sig.parameters
    accepts_var_kwargs = any(
        p.kind == inspect.Parameter.VAR_KEYWORD
        for p in params.values()
    )

    if accepts_var_kwargs:
        result = fn(**available)
    else:
        kwargs = {
            key: value
            for key, value in available.items()
            if key in params
        }

        # Fill any required missing parameter with safe doctrine-support defaults.
        for key, param in params.items():
            if key in kwargs:
                continue
            if param.default is not inspect.Parameter.empty:
                continue
            kwargs[key] = _support_default(key, available)

        result = fn(**kwargs)

    if isinstance(result, dict):
        return result
    if hasattr(result, "to_dict"):
        out = result.to_dict()
        return dict(out) if isinstance(out, dict) else {}
    return dict(result) if isinstance(result, Mapping) else {}


def _support_default(key: str, available: Mapping[str, Any]) -> Any:
    family = str(available.get("family_id", "")).upper()
    branch = str(available.get("branch_id", "")).upper()
    selected_branch = str(available.get("selected_branch", BRANCH_CALL)).upper()
    selected = branch == selected_branch

    if key in {"family_id"}:
        return family
    if key in {"branch_id"}:
        return branch
    if key in {"side", "selected_side"}:
        return SIDE_CALL if branch == BRANCH_CALL else SIDE_PUT
    if key in {"mode"}:
        return "BASE_5DEPTH"
    if key in {"selected_strike", "strike"}:
        return 22500.0
    if key in {"shadow_call_strike"}:
        return 22550.0
    if key in {"shadow_put_strike"}:
        return 22450.0
    if key in {"retest_type"}:
        return "FULL_RETEST" if branch == BRANCH_CALL else "HESITATION"
    if key in {"active_zone"}:
        return _builder_call("build_misr_active_zone") or {
            "zone_id": "offline-zone",
            "zone_type": "offline",
            "zone_valid": True,
            "quality_score": 0.72,
        }

    lowered = key.lower()

    if lowered.endswith("_score") or lowered.endswith("_ratio"):
        return 0.80 if selected else 0.10
    if lowered.endswith("_points") or lowered.endswith("_pts"):
        return 50.0
    if lowered.endswith("_count"):
        return 1 if selected else 0
    if lowered.endswith("_ns"):
        return 1800000000000000000
    if lowered.endswith("_ms"):
        return 0

    if (
        lowered.endswith("_ok")
        or lowered.endswith("_pass")
        or lowered.endswith("_ready")
        or lowered.endswith("_valid")
        or lowered.endswith("_present")
        or lowered.startswith("has_")
        or lowered.startswith("is_")
        or lowered in {
            "eligible",
            "chain_context_ready",
            "fake_break_triggered",
            "trap_detected",
            "trap_triggered",
            "breakout_triggered",
            "breakout_accepted",
            "resume_confirmed",
            "resume_confirmation_ok",
            "compression_detected",
            "pullback_detected",
            "burst_detected",
            "aggression_ok",
            "tape_speed_ok",
            "imbalance_persist_ok",
            "shadow_strike_support_ok",
        }
    ):
        return bool(selected)

    if lowered in {"micro_trap_blocked", "queue_reload_blocked", "futures_contradiction_blocked"}:
        return False

    if lowered.endswith("_id"):
        return f"offline-{family.lower()}-{branch.lower()}"
    if lowered.endswith("_kind") or lowered.endswith("_type"):
        return "offline"

    return None


def _branch_support_kwargs(family: str, branch: str, *, selected_branch: str) -> dict[str, Any]:
    selected = branch == selected_branch
    side = SIDE_CALL if branch == BRANCH_CALL else SIDE_PUT

    common = {
        "family_id": family,
        "branch_id": branch,
        "selected_branch": selected_branch,
        "side": side,
        "eligible": True,
        "contract_eligible": True,
        "surface_eligible": True,
        "tradability_ok": True,
        "option_tradability_pass": True,
        "context_pass": True,
        "context_score": 0.80,
        "oi_context_score": 0.80,
        "futures_bias_ok": selected,
        "direction_ok": selected,
        "bias_ok": selected,
        "option_confirmation_score": 0.90 if selected else 0.10,
        "option_response_score": 0.90 if selected else 0.10,
        "source_event_id": f"{family.lower()}-{branch.lower()}-offline",
        "surface_kind": f"{family.lower()}_branch",
        "oi_wall_context": {
            "distance_strikes": 2.0,
            "wall_strength": 0.40,
            "supportive": False,
        },
    }

    if family == "MIST":
        common.update({
            "futures_impulse_ok": selected,
            "pullback_detected": selected,
            "resume_confirmed": selected,
            "micro_trap_blocked": False,
            "trend_score": 0.90 if selected else 0.10,
            "pullback_score": 0.90 if selected else 0.10,
            "resume_score": 0.90 if selected else 0.10,
        })

    elif family == "MISB":
        common.update({
            "shelf_valid": selected,
            "shelf_ok": selected,
            "base_valid": selected,
            "breakout_triggered": selected,
            "breakout_trigger_ok": selected,
            "breakout_accepted": selected,
            "breakout_acceptance_ok": selected,
            "breakout_score": 0.90 if selected else 0.10,
        })

    elif family == "MISC":
        common.update({
            "compression_detected": selected,
            "compression_valid": selected,
            "compression_width_ok": selected,
            "compression_cluster_score": 0.80 if selected else 0.10,
            "prebreak_proximity_ok": selected,
            "breakout_trigger_ok": selected,
            "expansion_acceptance_ok": selected,
            "retest_valid": selected and branch == BRANCH_CALL,
            "hesitation_valid": selected and branch == BRANCH_PUT,
            "resume_confirmation_ok": selected,
            "retest_depth_ok": True,
            "retest_type": "FULL_RETEST" if branch == BRANCH_CALL else "HESITATION",
            "compression_score": 0.90 if selected else 0.10,
            "resume_score": 0.90 if selected else 0.10,
        })

    elif family == "MISR":
        common.update({
            "reversal_direction_ok": selected,
            "fake_break_triggered": selected,
            "fake_break_detected": selected,
            "trap_detected": selected,
            "trap_triggered": selected,
            "absorption_pass": selected,
            "absorption_ok": selected,
            "range_reentry_confirmed": selected,
            "reclaim_ok": selected,
            "reclaim_confirmed": selected,
            "flow_flip_confirmed": selected,
            "flow_flip_ok": selected,
            "hold_inside_range_proved": selected,
            "hold_proof_ok": selected,
            "no_mans_land_cleared": selected,
            "zone_clearance_ok": selected,
            "reversal_impulse_confirmed": selected,
            "reversal_impulse_ok": selected,
            "reversal_score": 0.90 if selected else 0.10,
            "trap_score": 0.90 if selected else 0.10,
            "fakeout_score": 0.90 if selected else 0.10,
            "trap_event_id": f"trap-{branch.lower()}",
            "active_zone": {
                "zone_id": "offline-zone",
                "zone_type": "fake_break_reclaim",
                "zone_valid": True,
                "quality_score": 0.72,
            },
        })

    elif family == "MISO":
        common.update({
            "mode": "BASE_5DEPTH",
            "selected_side": selected_branch,
            "selected_strike": 22500.0,
            "shadow_call_strike": 22550.0,
            "shadow_put_strike": 22450.0,
            "chain_context_ready": True,
            "burst_detected": selected,
            "option_burst_detected": selected,
            "burst_ok": selected,
            "aggression_ok": selected,
            "aggressive_flow": selected,
            "aggressive_buy_flow": selected and branch == BRANCH_CALL,
            "aggressive_sell_flow": selected and branch == BRANCH_PUT,
            "tape_speed_ok": selected,
            "speed_of_tape_ok": selected,
            "tape_urgency_ok": selected,
            "imbalance_persist_ok": selected,
            "imbalance_persistence_ok": selected,
            "persistence_ok": selected,
            "shadow_strike_support_ok": True,
            "shadow_support_ok": True,
            "queue_reload_blocked": False,
            "queue_reload_veto": False,
            "futures_vwap_align_ok": selected,
            "futures_alignment_ok": selected,
            "futures_contradiction_blocked": False,
            "tradability_pass": True,
            "burst_score": 0.90 if selected else 0.10,
            "tape_score": 0.90 if selected else 0.10,
            "tradability_score": 0.90,
            "burst_event_id": f"burst-{branch.lower()}",
        })

    return common


def _build_family_supports_for_contract(*, selected_branch: str) -> dict[str, Any]:
    mist_call = _builder_call("build_mist_branch_support", **_branch_support_kwargs("MIST", BRANCH_CALL, selected_branch=selected_branch))
    mist_put = _builder_call("build_mist_branch_support", **_branch_support_kwargs("MIST", BRANCH_PUT, selected_branch=selected_branch))
    misb_call = _builder_call("build_misb_branch_support", **_branch_support_kwargs("MISB", BRANCH_CALL, selected_branch=selected_branch))
    misb_put = _builder_call("build_misb_branch_support", **_branch_support_kwargs("MISB", BRANCH_PUT, selected_branch=selected_branch))
    misc_call = _builder_call("build_misc_branch_support", **_branch_support_kwargs("MISC", BRANCH_CALL, selected_branch=selected_branch))
    misc_put = _builder_call("build_misc_branch_support", **_branch_support_kwargs("MISC", BRANCH_PUT, selected_branch=selected_branch))
    misr_call = _builder_call("build_misr_branch_support", **_branch_support_kwargs("MISR", BRANCH_CALL, selected_branch=selected_branch))
    misr_put = _builder_call("build_misr_branch_support", **_branch_support_kwargs("MISR", BRANCH_PUT, selected_branch=selected_branch))
    miso_call = _builder_call("build_miso_side_support", **_branch_support_kwargs("MISO", BRANCH_CALL, selected_branch=selected_branch))
    miso_put = _builder_call("build_miso_side_support", **_branch_support_kwargs("MISO", BRANCH_PUT, selected_branch=selected_branch))

    active_zone = _builder_call("build_misr_active_zone") or {
        "zone_id": "offline-zone",
        "zone_type": "fake_break_reclaim",
        "zone_valid": True,
        "quality_score": 0.72,
    }

    return _builder_call(
        "build_families_block",
        mist_support=_builder_call("build_mist_family_support", call_support=mist_call, put_support=mist_put),
        misb_support=_builder_call("build_misb_family_support", call_support=misb_call, put_support=misb_put),
        misc_support=_builder_call("build_misc_family_support", call_support=misc_call, put_support=misc_put),
        misr_support=_builder_call("build_misr_family_support", active_zone=active_zone, call_support=misr_call, put_support=misr_put),
        miso_support=_builder_call(
            "build_miso_family_support",
            mode="BASE_5DEPTH",
            chain_context_ready=True,
            selected_side=selected_branch,
            selected_strike=22500.0,
            shadow_call_strike=22550.0,
            shadow_put_strike=22450.0,
            call_support=miso_call,
            put_support=miso_put,
        ),
    )


def _feature_payloads(*, selected_branch: str = BRANCH_CALL) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    families = ("MIST", "MISB", "MISC", "MISR", "MISO")
    branches = (BRANCH_CALL, BRANCH_PUT)
    selected_side = SIDE_CALL if selected_branch == BRANCH_CALL else SIDE_PUT

    family_features = {
        "schema_version": 1,
        "service": "features",
        "family_features_version": _family_features_version(),
        "generated_at_ns": 1800000000000000000,
        "snapshot": {
            "valid": True,
            "validity": "OK",
            "sync_ok": True,
            "freshness_ok": True,
            "packet_gap_ok": True,
            "warmup_ok": True,
            "active_snapshot_ns": 1800000000000000000,
            "futures_snapshot_ns": 1800000000000000000,
            "selected_option_snapshot_ns": 1800000000000000000,
            "dhan_futures_snapshot_ns": 1800000000000000000,
            "dhan_option_snapshot_ns": 1800000000000000000,
            "max_member_age_ms": 0,
            "fut_opt_skew_ms": 0,
            "hard_packet_gap_ms": 0,
            "samples_seen": 24,
        },
        "provider_runtime": {
            "active_futures_provider_id": PROVIDER_DHAN,
            "active_selected_option_provider_id": PROVIDER_DHAN,
            "active_option_context_provider_id": PROVIDER_DHAN,
            "active_execution_provider_id": PROVIDER_ZERODHA,
            "fallback_execution_provider_id": PROVIDER_DHAN,
            "provider_runtime_mode": "NORMAL",
            "family_runtime_mode": "OBSERVE_ONLY",
            "futures_provider_status": "HEALTHY",
            "selected_option_provider_status": "HEALTHY",
            "option_context_provider_status": "HEALTHY",
            "execution_provider_status": "HEALTHY",
        },
        "market": {
            "atm_strike": 22500.0,
            "selected_call_strike": 22500.0,
            "selected_put_strike": 22500.0,
            "active_branch_hint": selected_branch,
            "futures_ltp": 22525.0,
            "call_ltp": 125.0,
            "put_ltp": 128.0,
            "selected_option_ltp": 125.0 if selected_branch == BRANCH_CALL else 128.0,
            "premium_floor_ok": True,
        },
        "common": {
            "regime": "NORMAL",
            "strategy_runtime_mode_classic": "NORMAL",
            "strategy_runtime_mode_miso": "BASE_5DEPTH",
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
            "call": {
                "side": SIDE_CALL,
                "instrument_key": "NIFTY_22500_CE",
                "instrument_token": "TOKEN_22500_CE",
                "option_symbol": "NIFTY22500CE",
                "strike": 22500.0,
                "ltp": 125.0,
                "entry_mode": "ATM",
                "depth_ok": True,
                "tradability_ok": True,
                "response_efficiency": 0.35,
                "delta_3": 1.65,
                "tick_size": 0.05,
            },
            "put": {
                "side": SIDE_PUT,
                "instrument_key": "NIFTY_22500_PE",
                "instrument_token": "TOKEN_22500_PE",
                "option_symbol": "NIFTY22500PE",
                "strike": 22500.0,
                "ltp": 128.0,
                "entry_mode": "ATM",
                "depth_ok": True,
                "tradability_ok": True,
                "response_efficiency": 0.35,
                "delta_3": -1.65,
                "tick_size": 0.05,
            },
            "selected_option": {
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
            },
            "cross_option": {"cross_option_ready": True},
            "economics": {
                "economics_valid": True,
                "spread_rupees": 0.10,
                "slippage_estimate": 0.05,
                "cost_estimate": 0.0,
                "net_edge_estimate": 5.0,
            },
            "signals": {
                "futures_bias": 1.0 if selected_branch == BRANCH_CALL else -1.0,
                "futures_impulse": 1.0,
                "options_confirmation": True,
                "options_side": selected_side,
                "liquidity_ok": True,
                "alignment_ok": True,
            },
        },
        "stage_flags": {
            "data_valid": True,
            "data_quality_ok": True,
            "session_eligible": True,
            "warmup_complete": True,
            "risk_veto_active": False,
            "reconciliation_lock_active": False,
            "active_position_present": False,
            "provider_ready_classic": True,
            "provider_ready_miso": True,
            "dhan_context_fresh": True,
            "selected_option_present": True,
            "futures_present": True,
            "call_present": True,
            "put_present": True,
        },
        "families": _build_family_supports_for_contract(
            selected_branch=selected_branch,
        ),
    }

    family_surfaces = {
        "schema_version": 1,
        "surface_version": "family_surfaces.v1",
        "families": {
            family: {"eligible": True}
            for family in families
        },
        "surfaces_by_branch": {
            f"{family.lower()}_{branch.lower()}": _surface(family, branch, selected_branch=selected_branch)
            for family in families
            for branch in branches
        },
    }

    family_frames = {
        f"{family.lower()}_{branch.lower()}": _branch_frame(family, branch)
        for family in families
        for branch in branches
    }

    family_features = _normalize_family_features_for_contract(
        family_features,
        selected_branch=selected_branch,
    )

    return family_features, family_surfaces, family_frames


def main() -> int:
    now_ns = 1800000000000001234
    family_features, family_surfaces, family_frames = _feature_payloads(selected_branch=BRANCH_CALL)

    view = strategy.build_strategy_consumer_view(
        family_features=family_features,
        family_surfaces=family_surfaces,
        family_frames=family_frames,
        now_ns=now_ns,
    )

    class _NoRedis:
        pass

    bridge = strategy.StrategyFamilyConsumerBridge(redis_client=_NoRedis())
    decision = bridge.build_hold_decision(view, now_ns=now_ns)

    assert decision["action"] == getattr(N, "ACTION_HOLD", "HOLD"), decision
    assert decision["qty"] == 0, decision
    assert decision["hold_only"] == 1, decision
    assert decision["activation_bridge_enabled"] == 1, decision
    assert decision["activation_report_only"] == 1, decision
    assert decision["activation_action"] == getattr(N, "ACTION_HOLD", "HOLD"), decision
    assert decision["activation_promoted"] == 0, decision
    assert decision["activation_safe_to_promote"] == 0, decision
    assert decision["activation_candidate_count"] > 0, decision
    assert decision["activation_selected_family_id"], decision
    assert decision["activation_report_json"], decision

    activation_report = json.loads(decision["activation_report_json"])
    assert activation_report["action"] == getattr(N, "ACTION_HOLD", "HOLD"), activation_report
    assert activation_report["hold"] is True, activation_report
    assert activation_report["promoted"] is False, activation_report
    assert activation_report["safe_to_promote"] is False, activation_report
    assert activation_report["strategy_report_only"] is True, activation_report
    assert activation_report["live_orders_allowed"] is False, activation_report
    assert activation_report["selected"] is not None, activation_report

    diagnostics = json.loads(decision["diagnostics_json"])
    assert diagnostics["activation_bridge_report_only"] is True, diagnostics
    assert diagnostics["doctrine_leaves_observed"] is True, diagnostics
    assert diagnostics["doctrine_leaves_active"] is False, diagnostics
    assert diagnostics["broker_side_effects_allowed"] is False, diagnostics
    assert diagnostics["live_orders_allowed"] is False, diagnostics

    out = {
        "decision": decision,
        "activation_report": activation_report,
        "diagnostics": diagnostics,
    }
    out_path = PROJECT_ROOT / "run/proofs/strategy_activation_report_only.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")

    print("===== STRATEGY ACTIVATION REPORT-ONLY PROOF =====")
    print("decision_action =", decision["action"])
    print("qty =", decision["qty"])
    print("hold_only =", decision["hold_only"])
    print("activation_mode =", decision["activation_mode"])
    print("activation_reason =", decision["activation_reason"])
    print("activation_candidate_count =", decision["activation_candidate_count"])
    print("activation_selected_family_id =", decision["activation_selected_family_id"])
    print("activation_selected_branch_id =", decision["activation_selected_branch_id"])
    print("activation_selected_action =", decision["activation_selected_action"])
    print("activation_promoted =", decision["activation_promoted"])
    print("live_orders_allowed =", activation_report["live_orders_allowed"])
    print("dumped =", out_path.relative_to(PROJECT_ROOT))
    print("strategy activation report-only proof: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
