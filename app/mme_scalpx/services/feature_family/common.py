from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/common.py

Frozen contract-safe helper builders for ScalpX MME family-feature publication.

Purpose
-------
This module OWNS:
- pure deterministic helpers for building contract-valid family_features payloads
- exact-key subtree construction aligned with feature_family.contracts
- compatibility helper names used by services/features.py and proof scripts

This module DOES NOT own:
- Redis I/O
- service loops
- provider selection / failover policy
- strategy decisions
- doctrine state machines
- cooldown / proof / execution logic

Freeze fix
----------
The previous helper emitted payload_source/payload_version/legacy/metadata while
contracts.py required the exact canonical payload keys:
schema_version, service, family_features_version, generated_at_ns, snapshot,
provider_runtime, market, common, stage_flags, families.

This file now makes common.py subordinate to contracts.py with no top-level
contract drift.
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.feature_family import contracts as C


EPSILON: Final[float] = 1e-8

OPTION_SIDE_CALL: Final[str] = N.SIDE_CALL
OPTION_SIDE_PUT: Final[str] = N.SIDE_PUT
OPTION_SIDE_IDS: Final[tuple[str, ...]] = (
    OPTION_SIDE_CALL,
    OPTION_SIDE_PUT,
)


class FeatureFamilyCommonError(ValueError):
    """Raised when feature-family helper inputs are invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FeatureFamilyCommonError(message)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = _safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "available"}:
        return True
    if text in {"0", "false", "no", "n", "off", "unavailable"}:
        return False
    return default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None or isinstance(value, bool):
        return default
    try:
        text = _safe_str(value)
        return int(float(text)) if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "" or isinstance(value, bool):
        return default
    try:
        out = float(value)
    except Exception:
        return default
    return out if isfinite(out) else default


def _mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _literal_or_none(value: Any, allowed: tuple[str, ...]) -> str | None:
    text = _safe_str(value)
    if not text:
        return None
    _require(text in allowed, f"{text!r} must be one of {allowed!r}")
    return text


def _provider_id(value: Any, default: str | None = None) -> str | None:
    return _literal_or_none(_safe_str(value, default or ""), C.ALLOWED_PROVIDER_IDS)


def _provider_status(value: Any, default: str | None = None) -> str | None:
    fallback = default or getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
    return _literal_or_none(_safe_str(value, fallback), C.ALLOWED_PROVIDER_STATUSES)


def _family_runtime_mode(value: Any) -> str:
    default = getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only")
    text = _safe_str(value, default)
    _require(text in C.ALLOWED_FAMILY_RUNTIME_MODES, f"invalid family runtime mode {text!r}")
    return text


def _classic_runtime_mode(value: Any) -> str:
    if value is None or not _safe_str(value):
        return getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
    text = _safe_str(value)
    if text not in C.CLASSIC_ALLOWED_STRATEGY_RUNTIME_MODES:
        text = getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
    return text


def _miso_runtime_mode(value: Any) -> str:
    if value is None or not _safe_str(value):
        return getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
    text = _safe_str(value)
    if text not in C.MISO_ALLOWED_STRATEGY_RUNTIME_MODES:
        text = getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
    return text


def _regime(value: Any) -> str:
    text = _safe_str(value, C.REGIME_NORMAL).upper()
    return text if text in C.ALLOWED_REGIMES else C.REGIME_NORMAL


def derive_provider_ready_classic(
    *,
    active_futures_provider_id: Any,
    active_selected_option_provider_id: Any,
    strategy_runtime_mode: Any,
    futures_provider_status: Any = None,
    selected_option_provider_status: Any = None,
) -> bool:
    allowed_statuses = {
        getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        getattr(N, "PROVIDER_STATUS_DEGRADED", "DEGRADED"),
        getattr(N, "PROVIDER_STATUS_FAILOVER_ACTIVE", "FAILOVER_ACTIVE"),
    }
    return bool(
        _provider_id(active_futures_provider_id)
        and _provider_id(active_selected_option_provider_id)
        and _classic_runtime_mode(strategy_runtime_mode)
        != getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
        and _provider_status(futures_provider_status) in allowed_statuses
        and _provider_status(selected_option_provider_status) in allowed_statuses
    )


def derive_provider_ready_miso(
    *,
    active_futures_provider_id: Any,
    active_selected_option_provider_id: Any,
    active_option_context_provider_id: Any,
    strategy_runtime_mode: Any,
    futures_provider_status: Any = None,
    selected_option_provider_status: Any = None,
    option_context_provider_status: Any = None,
    dhan_context_ready: bool = False,
) -> bool:
    allowed_statuses = {
        getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        getattr(N, "PROVIDER_STATUS_DEGRADED", "DEGRADED"),
        getattr(N, "PROVIDER_STATUS_FAILOVER_ACTIVE", "FAILOVER_ACTIVE"),
    }
    return bool(
        _provider_id(active_futures_provider_id) == N.PROVIDER_DHAN
        and _provider_id(active_selected_option_provider_id) == N.PROVIDER_DHAN
        and _provider_id(active_option_context_provider_id) == N.PROVIDER_DHAN
        and _miso_runtime_mode(strategy_runtime_mode)
        != getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")
        and _provider_status(futures_provider_status) in allowed_statuses
        and _provider_status(selected_option_provider_status) in allowed_statuses
        and _provider_status(option_context_provider_status) in allowed_statuses
        and bool(dhan_context_ready)
    )


def derive_selected_option_present(*, call_present: bool, put_present: bool) -> bool:
    return bool(call_present or put_present)


def derive_common_premium_floor_ok(premium: Any, *, premium_floor: float) -> bool:
    return (_safe_float(premium, 0.0) or 0.0) >= max(float(premium_floor), 0.0)


def derive_depth_ok(depth_total: Any, *, depth_min: int) -> bool:
    return _safe_int(depth_total, 0) >= max(int(depth_min), 0)


def derive_spread_ratio_ok(spread_ratio: Any, *, spread_ratio_max: float) -> bool:
    ratio = _safe_float(spread_ratio, None)
    return bool(ratio is not None and ratio <= max(float(spread_ratio_max), 0.0))


def derive_response_efficiency_ok(response_efficiency: Any, *, response_efficiency_min: float) -> bool:
    return (_safe_float(response_efficiency, 0.0) or 0.0) >= float(response_efficiency_min)


def derive_tradability_ok(
    *,
    premium_floor_ok: bool,
    depth_ok: bool,
    spread_ratio_ok: bool,
    response_efficiency_ok: bool,
) -> bool:
    return bool(premium_floor_ok and depth_ok and spread_ratio_ok and response_efficiency_ok)


def derive_selected_option_tradability_ok(
    *,
    premium: Any,
    premium_floor: float,
    depth_total: Any,
    depth_min: int,
    spread_ratio: Any,
    spread_ratio_max: float,
    response_efficiency: Any,
    response_efficiency_min: float,
) -> bool:
    return derive_tradability_ok(
        premium_floor_ok=derive_common_premium_floor_ok(premium, premium_floor=premium_floor),
        depth_ok=derive_depth_ok(depth_total, depth_min=depth_min),
        spread_ratio_ok=derive_spread_ratio_ok(spread_ratio, spread_ratio_max=spread_ratio_max),
        response_efficiency_ok=derive_response_efficiency_ok(
            response_efficiency,
            response_efficiency_min=response_efficiency_min,
        ),
    )


def build_snapshot_block(
    *,
    valid: bool | None = None,
    snapshot_valid: bool | None = None,
    validity: str | None = None,
    snapshot_validity: str | None = None,
    sync_ok: bool | None = None,
    snapshot_sync_ok: bool | None = None,
    freshness_ok: bool = True,
    packet_gap_ok: bool = True,
    warmup_ok: bool | None = None,
    warmup_complete: bool | None = None,
    active_snapshot_ns: Any = None,
    futures_snapshot_ns: Any = None,
    selected_option_snapshot_ns: Any = None,
    dhan_futures_snapshot_ns: Any = None,
    dhan_option_snapshot_ns: Any = None,
    max_member_age_ms: Any = None,
    fut_opt_skew_ms: Any = None,
    hard_packet_gap_ms: Any = None,
    samples_seen: Any = 1,
    **_: Any,
) -> dict[str, Any]:
    resolved_valid = bool(snapshot_valid if snapshot_valid is not None else valid)
    return {
        "valid": resolved_valid,
        "validity": _safe_str(snapshot_validity or validity, "VALID" if resolved_valid else "INVALID"),
        "sync_ok": bool(snapshot_sync_ok if snapshot_sync_ok is not None else sync_ok if sync_ok is not None else resolved_valid),
        "freshness_ok": bool(freshness_ok),
        "packet_gap_ok": bool(packet_gap_ok),
        "warmup_ok": bool(warmup_complete if warmup_complete is not None else warmup_ok if warmup_ok is not None else True),
        "active_snapshot_ns": _safe_int(active_snapshot_ns, 0) or None,
        "futures_snapshot_ns": _safe_int(futures_snapshot_ns, 0) or None,
        "selected_option_snapshot_ns": _safe_int(selected_option_snapshot_ns, 0) or None,
        "dhan_futures_snapshot_ns": _safe_int(dhan_futures_snapshot_ns, 0) or None,
        "dhan_option_snapshot_ns": _safe_int(dhan_option_snapshot_ns, 0) or None,
        "max_member_age_ms": _safe_int(max_member_age_ms, 0) or None,
        "fut_opt_skew_ms": _safe_int(fut_opt_skew_ms, 0) or None,
        "hard_packet_gap_ms": _safe_int(hard_packet_gap_ms, 0) or None,
        "samples_seen": max(_safe_int(samples_seen, 1), 1),
    }


def build_provider_runtime_block(
    *,
    active_futures_provider_id: Any = None,
    active_selected_option_provider_id: Any = None,
    active_option_context_provider_id: Any = None,
    active_execution_provider_id: Any = None,
    execution_primary_provider_id: Any = None,
    fallback_execution_provider_id: Any = None,
    execution_fallback_provider_id: Any = None,
    provider_runtime_mode: Any = None,
    family_runtime_mode: Any = None,
    futures_provider_status: Any = None,
    selected_option_provider_status: Any = None,
    option_context_provider_status: Any = None,
    execution_provider_status: Any = None,
    **_: Any,
) -> dict[str, Any]:
    return {
        "active_futures_provider_id": _provider_id(active_futures_provider_id, None),
        "active_selected_option_provider_id": _provider_id(active_selected_option_provider_id, None),
        "active_option_context_provider_id": _provider_id(active_option_context_provider_id, None),
        "active_execution_provider_id": _provider_id(active_execution_provider_id or execution_primary_provider_id, None),
        "fallback_execution_provider_id": _provider_id(fallback_execution_provider_id or execution_fallback_provider_id, None),
        "provider_runtime_mode": _safe_str(provider_runtime_mode) or None,
        "family_runtime_mode": _family_runtime_mode(family_runtime_mode),
        "futures_provider_status": _provider_status(futures_provider_status),
        "selected_option_provider_status": _provider_status(selected_option_provider_status),
        "option_context_provider_status": _provider_status(option_context_provider_status),
        "execution_provider_status": _provider_status(execution_provider_status),
    }


def build_market_block(
    *,
    atm_strike: Any = None,
    selected_call_strike: Any = None,
    selected_put_strike: Any = None,
    active_branch_hint: Any = None,
    futures_ltp: Any = None,
    call_ltp: Any = None,
    put_ltp: Any = None,
    selected_option_ltp: Any = None,
    premium_floor_ok: bool = False,
    **_: Any,
) -> dict[str, Any]:
    return {
        "atm_strike": _safe_float(atm_strike, None),
        "selected_call_strike": _safe_float(selected_call_strike, None),
        "selected_put_strike": _safe_float(selected_put_strike, None),
        "active_branch_hint": _safe_str(active_branch_hint) or None,
        "futures_ltp": _safe_float(futures_ltp, None),
        "call_ltp": _safe_float(call_ltp, None),
        "put_ltp": _safe_float(put_ltp, None),
        "selected_option_ltp": _safe_float(selected_option_ltp, None),
        "premium_floor_ok": bool(premium_floor_ok),
    }


def build_common_futures_block(**kwargs: Any) -> dict[str, Any]:
    return {
        "ltp": _safe_float(kwargs.get("ltp"), None),
        "spread": _safe_float(kwargs.get("spread"), None),
        "spread_ratio": _safe_float(kwargs.get("spread_ratio"), None),
        "depth_total": _safe_int(kwargs.get("depth_total"), 0) or None,
        "depth_ok": _safe_bool(kwargs.get("depth_ok"), False),
        "top5_bid_qty": _safe_int(kwargs.get("top5_bid_qty", kwargs.get("bid_qty_5")), 0) or None,
        "top5_ask_qty": _safe_int(kwargs.get("top5_ask_qty", kwargs.get("ask_qty_5")), 0) or None,
        "ofi_ratio_proxy": _safe_float(kwargs.get("ofi_ratio_proxy", kwargs.get("weighted_ofi_persist")), None),
        "ofi_persist_score": _safe_float(kwargs.get("ofi_persist_score", kwargs.get("weighted_ofi_persist")), None),
        "microprice": _safe_float(kwargs.get("microprice"), None),
        "micro_edge": _safe_float(kwargs.get("micro_edge"), None),
        "vwap": _safe_float(kwargs.get("vwap"), None),
        "vwap_dist_pct": _safe_float(kwargs.get("vwap_dist_pct", kwargs.get("vwap_distance_ratio")), None),
        "ema_9": _safe_float(kwargs.get("ema_9"), None),
        "ema_21": _safe_float(kwargs.get("ema_21"), None),
        "ema9_slope": _safe_float(kwargs.get("ema9_slope"), None),
        "ema21_slope": _safe_float(kwargs.get("ema21_slope"), None),
        "delta_3": _safe_float(kwargs.get("delta_3"), None),
        "vel_3": _safe_float(kwargs.get("vel_3"), None),
        "vel_ratio": _safe_float(kwargs.get("vel_ratio", kwargs.get("velocity_ratio")), None),
        "vol_delta": _safe_float(kwargs.get("vol_delta"), None),
        "vol_norm": _safe_float(kwargs.get("vol_norm"), None),
        "range_fast": _safe_float(kwargs.get("range_fast"), None),
        "range_slow": _safe_float(kwargs.get("range_slow"), None),
        "range_ratio": _safe_float(kwargs.get("range_ratio"), None),
        "above_vwap": _safe_bool(kwargs.get("above_vwap"), False),
        "below_vwap": _safe_bool(kwargs.get("below_vwap"), False),
    }


def build_common_option_block(*, side: str | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "ltp": _safe_float(kwargs.get("ltp"), None),
        "spread": _safe_float(kwargs.get("spread"), None),
        "spread_ratio": _safe_float(kwargs.get("spread_ratio"), None),
        "depth_total": _safe_int(kwargs.get("depth_total"), 0) or None,
        "depth_ok": _safe_bool(kwargs.get("depth_ok"), False),
        "top5_bid_qty": _safe_int(kwargs.get("top5_bid_qty", kwargs.get("bid_qty_5")), 0) or None,
        "top5_ask_qty": _safe_int(kwargs.get("top5_ask_qty", kwargs.get("ask_qty_5")), 0) or None,
        "ofi_ratio_proxy": _safe_float(kwargs.get("ofi_ratio_proxy", kwargs.get("weighted_ofi_persist")), None),
        "microprice": _safe_float(kwargs.get("microprice"), None),
        "micro_edge": _safe_float(kwargs.get("micro_edge"), None),
        "delta_3": _safe_float(kwargs.get("delta_3"), None),
        "response_efficiency": _safe_float(kwargs.get("response_efficiency"), None),
        "tradability_ok": _safe_bool(kwargs.get("tradability_ok"), False),
        "tick_size": _safe_float(kwargs.get("tick_size"), None),
        "lot_size": _safe_int(kwargs.get("lot_size"), 0) or None,
        "strike": _safe_float(kwargs.get("strike"), None),
    }


def build_selected_option_block(*, side: str | None = None, **kwargs: Any) -> dict[str, Any]:
    base = build_common_option_block(side=side, **kwargs)
    return {
        "side": _safe_str(side or kwargs.get("side")) or None,
        "ltp": base["ltp"],
        "spread": base["spread"],
        "spread_ratio": base["spread_ratio"],
        "depth_total": base["depth_total"],
        "depth_ok": base["depth_ok"],
        "ofi_ratio_proxy": base["ofi_ratio_proxy"],
        "microprice": base["microprice"],
        "micro_edge": base["micro_edge"],
        "delta_3": base["delta_3"],
        "response_efficiency": base["response_efficiency"],
        "tradability_ok": base["tradability_ok"],
    }


def build_cross_option_block(
    *,
    call_features: Mapping[str, Any] | None = None,
    put_features: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    call = _mapping(call_features)
    put = _mapping(put_features)
    call_ltp = _safe_float(call.get("ltp"), None)
    put_ltp = _safe_float(put.get("ltp"), None)
    call_depth = _safe_float(call.get("depth_total"), None)
    put_depth = _safe_float(put.get("depth_total"), None)
    call_spread = _safe_float(call.get("spread_ratio"), None)
    put_spread = _safe_float(put.get("spread_ratio"), None)

    return {
        "call_minus_put_ltp": None if call_ltp is None or put_ltp is None else call_ltp - put_ltp,
        "call_put_depth_ratio": None if not put_depth else (call_depth or 0.0) / put_depth,
        "call_put_spread_ratio": None if not put_spread else (call_spread or 0.0) / put_spread,
    }


def build_economics_block(
    *,
    premium_floor_ok: bool = False,
    target_points: Any = None,
    stop_points: Any = None,
    target_pct: Any = None,
    stop_pct: Any = None,
    economic_viability_ok: bool | None = None,
    economics_valid: bool | None = None,
    **_: Any,
) -> dict[str, Any]:
    viable = economic_viability_ok if economic_viability_ok is not None else economics_valid
    return {
        "premium_floor_ok": bool(premium_floor_ok),
        "target_points": _safe_float(target_points, None),
        "stop_points": _safe_float(stop_points, None),
        "target_pct": _safe_float(target_pct, None),
        "stop_pct": _safe_float(stop_pct, None),
        "economic_viability_ok": bool(viable),
    }


def build_signals_block(**kwargs: Any) -> dict[str, Any]:
    return {
        "four_pillar_signal": _safe_str(kwargs.get("four_pillar_signal")) or None,
        "four_pillar_score": _safe_float(kwargs.get("four_pillar_score"), None),
        "delta_proxy_norm": _safe_float(kwargs.get("delta_proxy_norm"), None),
        "futures_contradiction_flag": _safe_bool(kwargs.get("futures_contradiction_flag"), False),
        "queue_reload_veto_flag": _safe_bool(kwargs.get("queue_reload_veto_flag"), False),
    }


def build_common_block(
    *,
    regime: str = C.REGIME_NORMAL,
    strategy_runtime_mode_classic: Any = None,
    strategy_runtime_mode_miso: Any = None,
    futures: Mapping[str, Any] | None = None,
    futures_features: Mapping[str, Any] | None = None,
    call: Mapping[str, Any] | None = None,
    selected_call: Mapping[str, Any] | None = None,
    put: Mapping[str, Any] | None = None,
    selected_put: Mapping[str, Any] | None = None,
    selected_option: Mapping[str, Any] | None = None,
    cross_option: Mapping[str, Any] | None = None,
    economics: Mapping[str, Any] | None = None,
    signals: Mapping[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    call_block = dict(call or selected_call or {})
    put_block = dict(put or selected_put or {})
    return {
        "regime": _regime(regime),
        "strategy_runtime_mode_classic": _classic_runtime_mode(strategy_runtime_mode_classic),
        "strategy_runtime_mode_miso": _miso_runtime_mode(strategy_runtime_mode_miso),
        "futures": dict(futures or futures_features or build_common_futures_block()),
        "call": call_block or build_common_option_block(side=N.SIDE_CALL),
        "put": put_block or build_common_option_block(side=N.SIDE_PUT),
        "selected_option": dict(selected_option or build_selected_option_block(side=None)),
        "cross_option": dict(cross_option or build_cross_option_block(call_features=call_block, put_features=put_block)),
        "economics": dict(economics or build_economics_block()),
        "signals": dict(signals or build_signals_block()),
    }


def build_stage_flags_block(
    *,
    data_valid: bool = False,
    data_quality_ok: bool = False,
    session_eligible: bool = True,
    warmup_complete: bool = True,
    risk_veto_active: bool = False,
    reconciliation_lock_active: bool = False,
    active_position_present: bool = False,
    provider_ready_classic: bool = False,
    provider_ready_miso: bool = False,
    dhan_context_fresh: bool = False,
    selected_option_present: bool = False,
    futures_present: bool = False,
    call_present: bool = False,
    put_present: bool = False,
    **_: Any,
) -> dict[str, Any]:
    return {
        "data_valid": bool(data_valid),
        "data_quality_ok": bool(data_quality_ok),
        "session_eligible": bool(session_eligible),
        "warmup_complete": bool(warmup_complete),
        "risk_veto_active": bool(risk_veto_active),
        "reconciliation_lock_active": bool(reconciliation_lock_active),
        "active_position_present": bool(active_position_present),
        "provider_ready_classic": bool(provider_ready_classic),
        "provider_ready_miso": bool(provider_ready_miso),
        "dhan_context_fresh": bool(dhan_context_fresh),
        "selected_option_present": bool(selected_option_present),
        "futures_present": bool(futures_present),
        "call_present": bool(call_present),
        "put_present": bool(put_present),
    }


def derive_stage_flags(**kwargs: Any) -> dict[str, Any]:
    return build_stage_flags_block(**kwargs)


def build_mist_branch_support(**kwargs: Any) -> dict[str, Any]:
    return {
        "futures_bias_ok": _safe_bool(kwargs.get("futures_bias_ok", kwargs.get("trend_direction_ok")), False),
        "futures_impulse_ok": _safe_bool(kwargs.get("futures_impulse_ok", kwargs.get("resume_support")), False),
        "pullback_detected": _safe_bool(kwargs.get("pullback_detected"), False),
        "resume_confirmed": _safe_bool(kwargs.get("resume_confirmed", kwargs.get("resume_support")), False),
        "micro_trap_blocked": _safe_bool(kwargs.get("micro_trap_blocked", kwargs.get("micro_trap_present")), False),
        "context_pass": _safe_bool(kwargs.get("context_pass"), False),
        "option_tradability_pass": _safe_bool(kwargs.get("option_tradability_pass"), False),
    }


def build_misb_branch_support(**kwargs: Any) -> dict[str, Any]:
    return {
        "futures_bias_ok": _safe_bool(kwargs.get("futures_bias_ok"), False),
        "shelf_valid": _safe_bool(kwargs.get("shelf_valid"), False),
        "breakout_triggered": _safe_bool(kwargs.get("breakout_triggered", kwargs.get("breakout_trigger_ok")), False),
        "breakout_accepted": _safe_bool(kwargs.get("breakout_accepted", kwargs.get("breakout_acceptance_ok")), False),
        "context_pass": _safe_bool(kwargs.get("context_pass"), False),
        "option_tradability_pass": _safe_bool(kwargs.get("option_tradability_pass"), False),
    }


def build_misc_branch_support(**kwargs: Any) -> dict[str, Any]:
    return {
        "compression_detected": _safe_bool(kwargs.get("compression_detected"), False),
        "directional_breakout_triggered": _safe_bool(kwargs.get("directional_breakout_triggered", kwargs.get("breakout_trigger_ok")), False),
        "expansion_accepted": _safe_bool(kwargs.get("expansion_accepted", kwargs.get("expansion_acceptance_ok")), False),
        "retest_monitor_active": _safe_bool(kwargs.get("retest_monitor_active", kwargs.get("retest_valid")), False),
        "retest_type": _safe_str(kwargs.get("retest_type")) or None,
        "resume_confirmed": _safe_bool(kwargs.get("resume_confirmed", kwargs.get("resume_confirmation_ok")), False),
        "context_pass": _safe_bool(kwargs.get("context_pass"), False),
        "option_tradability_pass": _safe_bool(kwargs.get("option_tradability_pass"), False),
    }


def build_misr_active_zone(**kwargs: Any) -> dict[str, Any]:
    return {
        "zone_id": _safe_str(kwargs.get("zone_id")) or None,
        "zone_type": _safe_str(kwargs.get("zone_type")) or None,
        "zone_level": _safe_float(kwargs.get("zone_level", kwargs.get("zone_mid")), None),
        "zone_low": _safe_float(kwargs.get("zone_low"), None),
        "zone_high": _safe_float(kwargs.get("zone_high"), None),
        "quality_score": _safe_float(kwargs.get("quality_score"), None),
        "expires_ts_ns": _safe_int(kwargs.get("expires_ts_ns"), 0) or None,
    }


def build_misr_branch_support(**kwargs: Any) -> dict[str, Any]:
    return {
        "fake_break_triggered": _safe_bool(kwargs.get("fake_break_triggered", kwargs.get("fake_break_detected")), False),
        "absorption_pass": _safe_bool(kwargs.get("absorption_pass", kwargs.get("absorption_ok")), False),
        "range_reentry_confirmed": _safe_bool(kwargs.get("range_reentry_confirmed", kwargs.get("reclaim_ok")), False),
        "flow_flip_confirmed": _safe_bool(kwargs.get("flow_flip_confirmed"), False),
        "hold_inside_range_proved": _safe_bool(kwargs.get("hold_inside_range_proved", kwargs.get("hold_proof_ok")), False),
        "no_mans_land_cleared": _safe_bool(kwargs.get("no_mans_land_cleared"), False),
        "reversal_impulse_confirmed": _safe_bool(kwargs.get("reversal_impulse_confirmed", kwargs.get("reversal_impulse_ok")), False),
        "context_pass": _safe_bool(kwargs.get("context_pass"), False),
        "option_tradability_pass": _safe_bool(kwargs.get("option_tradability_pass"), False),
    }


def build_miso_side_support(**kwargs: Any) -> dict[str, Any]:
    return {
        "burst_detected": _safe_bool(kwargs.get("burst_detected", kwargs.get("aggressive_flow")), False),
        "aggression_ok": _safe_bool(kwargs.get("aggression_ok", kwargs.get("aggressive_flow")), False),
        "tape_speed_ok": _safe_bool(kwargs.get("tape_speed_ok"), False),
        "imbalance_persist_ok": _safe_bool(kwargs.get("imbalance_persist_ok"), False),
        "queue_reload_blocked": _safe_bool(kwargs.get("queue_reload_blocked", kwargs.get("queue_reload_veto")), False),
        "futures_vwap_align_ok": _safe_bool(kwargs.get("futures_vwap_align_ok", kwargs.get("futures_vwap_alignment_ok")), False),
        "futures_contradiction_blocked": _safe_bool(kwargs.get("futures_contradiction_blocked", kwargs.get("futures_contradiction_veto")), False),
        "tradability_pass": _safe_bool(kwargs.get("tradability_pass"), False),
    }


def build_mist_family_support(*, call_support: Mapping[str, Any], put_support: Mapping[str, Any], eligible: bool | None = None, **_: Any) -> dict[str, Any]:
    call = dict(call_support)
    put = dict(put_support)
    return {"eligible": bool(eligible if eligible is not None else any(call.values()) or any(put.values())), "branches": {C.BRANCH_CALL: call, C.BRANCH_PUT: put}}


def build_misb_family_support(*, call_support: Mapping[str, Any], put_support: Mapping[str, Any], eligible: bool | None = None, **_: Any) -> dict[str, Any]:
    call = dict(call_support)
    put = dict(put_support)
    return {"eligible": bool(eligible if eligible is not None else any(call.values()) or any(put.values())), "branches": {C.BRANCH_CALL: call, C.BRANCH_PUT: put}}


def build_misc_family_support(*, call_support: Mapping[str, Any], put_support: Mapping[str, Any], eligible: bool | None = None, **_: Any) -> dict[str, Any]:
    call = dict(call_support)
    put = dict(put_support)
    return {"eligible": bool(eligible if eligible is not None else any(v for v in call.values() if isinstance(v, bool)) or any(v for v in put.values() if isinstance(v, bool))), "branches": {C.BRANCH_CALL: call, C.BRANCH_PUT: put}}


def build_misr_family_support(
    *,
    call_support: Mapping[str, Any],
    put_support: Mapping[str, Any],
    active_zone: Mapping[str, Any] | None = None,
    eligible: bool | None = None,
    **_: Any,
) -> dict[str, Any]:
    call = dict(call_support)
    put = dict(put_support)
    return {
        "eligible": bool(eligible if eligible is not None else any(call.values()) or any(put.values())),
        "active_zone": dict(active_zone or build_misr_active_zone()),
        "branches": {C.BRANCH_CALL: call, C.BRANCH_PUT: put},
    }


def build_miso_family_support(
    *,
    call_support: Mapping[str, Any],
    put_support: Mapping[str, Any],
    eligible: bool | None = None,
    mode: Any = None,
    chain_context_ready: bool = False,
    selected_side: Any = None,
    selected_strike: Any = None,
    shadow_call_strike: Any = None,
    shadow_put_strike: Any = None,
    **_: Any,
) -> dict[str, Any]:
    call = dict(call_support)
    put = dict(put_support)
    return {
        "eligible": bool(eligible if eligible is not None else any(call.values()) or any(put.values())),
        "mode": _safe_str(mode) or None,
        "chain_context_ready": bool(chain_context_ready),
        "selected_side": _safe_str(selected_side) or None,
        "selected_strike": _safe_float(selected_strike, None),
        "shadow_call_strike": _safe_float(shadow_call_strike, None),
        "shadow_put_strike": _safe_float(shadow_put_strike, None),
        "call_support": call,
        "put_support": put,
    }


def build_families_block(
    *,
    mist_support: Mapping[str, Any],
    misb_support: Mapping[str, Any],
    misc_support: Mapping[str, Any],
    misr_support: Mapping[str, Any],
    miso_support: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        C.FAMILY_ID_MIST: dict(mist_support),
        C.FAMILY_ID_MISB: dict(misb_support),
        C.FAMILY_ID_MISC: dict(misc_support),
        C.FAMILY_ID_MISR: dict(misr_support),
        C.FAMILY_ID_MISO: dict(miso_support),
    }


def build_family_features_payload(
    *,
    snapshot: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
    market: Mapping[str, Any] | None = None,
    common: Mapping[str, Any],
    stage_flags: Mapping[str, Any],
    families: Mapping[str, Any],
    schema_version: int | None = None,
    service: str | None = None,
    family_features_version: str | None = None,
    generated_at_ns: int | None = None,
    payload_source: str | None = None,
    payload_version: str | None = None,
    legacy: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the exact contracts.py family_features payload.

    Compatibility note:
    payload_source, payload_version, legacy, and metadata are accepted to avoid
    breaking older call sites, but they are intentionally not emitted because
    contracts.py forbids top-level drift.
    """
    payload = {
        "schema_version": int(schema_version or getattr(N, "DEFAULT_SCHEMA_VERSION", 1)),
        "service": _safe_str(service, getattr(N, "SERVICE_FEATURES", "features")),
        "family_features_version": _safe_str(
            family_features_version or payload_version,
            C.FAMILY_FEATURES_VERSION,
        ),
        "generated_at_ns": max(_safe_int(generated_at_ns, 0), 0),
        "snapshot": dict(snapshot),
        "provider_runtime": dict(provider_runtime),
        "market": dict(market or C.build_empty_market_block()),
        "common": dict(common),
        "stage_flags": dict(stage_flags),
        "families": dict(families),
    }
    C.validate_family_features_payload(payload)
    return payload


def build_publishable_family_features_payload(
    *,
    snapshot: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
    market: Mapping[str, Any] | None = None,
    common: Mapping[str, Any],
    stage_flags: Mapping[str, Any],
    families: Mapping[str, Any],
    schema_version: int | None = None,
    service: str | None = None,
    family_features_version: str | None = None,
    generated_at_ns: int | None = None,
    payload_source: str | None = None,
    payload_version: str | None = None,
    legacy: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = build_family_features_payload(
        snapshot=snapshot,
        provider_runtime=provider_runtime,
        market=market,
        common=common,
        stage_flags=stage_flags,
        families=families,
        schema_version=schema_version,
        service=service,
        family_features_version=family_features_version,
        generated_at_ns=generated_at_ns,
        payload_source=payload_source,
        payload_version=payload_version,
        legacy=legacy,
        metadata=metadata,
    )
    C.validate_publishable_family_features_payload(payload)
    return payload


__all__ = [
    "FeatureFamilyCommonError",
    "EPSILON",
    "OPTION_SIDE_CALL",
    "OPTION_SIDE_PUT",
    "OPTION_SIDE_IDS",
    "build_snapshot_block",
    "build_provider_runtime_block",
    "build_market_block",
    "build_common_futures_block",
    "build_common_option_block",
    "build_selected_option_block",
    "build_cross_option_block",
    "build_economics_block",
    "build_signals_block",
    "build_common_block",
    "build_stage_flags_block",
    "build_mist_branch_support",
    "build_misb_branch_support",
    "build_misc_branch_support",
    "build_misr_active_zone",
    "build_misr_branch_support",
    "build_miso_side_support",
    "build_mist_family_support",
    "build_misb_family_support",
    "build_misc_family_support",
    "build_misr_family_support",
    "build_miso_family_support",
    "build_families_block",
    "build_family_features_payload",
    "build_publishable_family_features_payload",
    "derive_provider_ready_classic",
    "derive_provider_ready_miso",
    "derive_selected_option_present",
    "derive_common_premium_floor_ok",
    "derive_depth_ok",
    "derive_spread_ratio_ok",
    "derive_response_efficiency_ok",
    "derive_tradability_ok",
    "derive_selected_option_tradability_ok",
    "derive_stage_flags",
]
