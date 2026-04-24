from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/mist_surface.py

Canonical MIST feature surface for ScalpX MME.

Purpose
-------
This module OWNS:
- doctrine-specific feature publication support for MIST only
- deterministic CALL / PUT MIST surface derivation from shared-core payloads
- gate-ready booleans for the MIST trend -> impulse -> pullback -> resume stack
- JSON-friendly branch and family support surfaces for services/features.py

This module DOES NOT own:
- strategy state machine mutation
- entry / exit decisions
- cooldown or re-entry mutation
- provider-routing policy
- Redis I/O

Frozen design law
-----------------
- MIST remains futures-led and option-confirmed.
- features.py owns derived metrics and gate-ready booleans, but not entry/exit decisions.
- strategy.py later consumes the surface and evaluates the exact pipeline:
  futures bias -> futures impulse -> micro trap check -> pullback ->
  resume confirmation -> context pass -> tradability -> entry recheck.
- This module must stay payload-first and doctrine-surface only; it may not
  become a second strategy engine.

Implementation note
-------------------
The current features lane already carries a minimal MIST-style surface using
fields such as trend_score, pullback_depth, resume_support, and
trend_direction_ok. This module turns that direction into a clean reusable
family surface while staying downstream of shared-core payloads.
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

EPSILON: Final[float] = 1e-8

DEFAULT_TREND_SCORE_MIN: Final[float] = 0.15
DEFAULT_PULLBACK_DEPTH_MIN: Final[float] = 0.05
DEFAULT_PULLBACK_DEPTH_MAX: Final[float] = 25.0
DEFAULT_RESUME_VELOCITY_RATIO_MIN: Final[float] = 1.0
DEFAULT_FUTURES_IMPULSE_VELOCITY_MIN: Final[float] = 1.15
DEFAULT_FUTURES_VOL_NORM_MIN: Final[float] = 1.10
DEFAULT_BULL_OFI_MIN: Final[float] = 0.53
DEFAULT_BEAR_OFI_MAX: Final[float] = 0.47
DEFAULT_RESUME_OVERRIDE_OFI_MAX: Final[float] = 0.38
DEFAULT_RESUME_OVERRIDE_VOL_MIN: Final[float] = 1.45
DEFAULT_MICRO_TRAP_DEPTH_MAX: Final[float] = 2.50
DEFAULT_CONTEXT_SCORE_NEUTRAL: Final[float] = 0.50

__all__ = [
    "build_mist_branch_surface",
    "build_mist_family_surface",
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return float(default)
    if not isfinite(number):
        return float(default)
    return float(number)


def _safe_float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except Exception:
        return None
    if not isfinite(number):
        return None
    return float(number)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


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
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _pick(mapping: Mapping[str, Any] | None, *keys: str) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _threshold_float(thresholds: Mapping[str, Any] | None, key: str, default: float) -> float:
    return _safe_float(_pick(thresholds, key), default)


def _branch_side(branch_id: str) -> str:
    return N.SIDE_CALL if branch_id == N.BRANCH_CALL else N.SIDE_PUT


def _directional_ok(value: float, branch_id: str) -> bool:
    return value >= 0.0 if branch_id == N.BRANCH_CALL else value <= 0.0


def _ofi_direction_ok(value: float, branch_id: str, bull_min: float, bear_max: float) -> bool:
    return value >= bull_min if branch_id == N.BRANCH_CALL else value <= bear_max


def _resume_override_ok(
    *,
    weighted_ofi: float,
    volume_norm: float,
    branch_id: str,
    override_ofi_max: float,
    override_vol_min: float,
) -> bool:
    if branch_id == N.BRANCH_CALL:
        return weighted_ofi >= override_ofi_max and volume_norm >= override_vol_min
    return weighted_ofi <= (1.0 - override_ofi_max) and volume_norm >= override_vol_min


def _context_pass(runtime_mode: str, provider_ready: bool) -> bool:
    normalized = _safe_str(runtime_mode).upper()
    disabled = {
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")).upper(),
        "DISABLED",
    }
    degraded = {
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED", "DHAN_DEGRADED")).upper(),
        "DHAN_DEGRADED",
    }
    if normalized in disabled:
        return False
    if normalized in degraded:
        return True
    return provider_ready


def _context_features(option_surface: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return _as_mapping(_pick(_as_mapping(option_surface), "context_features"))


def _premium_health(option_surface: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return _as_mapping(_pick(_as_mapping(option_surface), "premium_health"))


def _oi_bias_alignment(branch_id: str, oi_bias: str) -> bool:
    normalized = _safe_str(oi_bias, "UNKNOWN").upper()
    if normalized in {"UNKNOWN", "NEUTRAL", ""}:
        return True
    if branch_id == N.BRANCH_CALL:
        return normalized == "PUT_SUPPORTIVE"
    return normalized == "CALL_SUPPORTIVE"


def _derived_context_score(
    *,
    branch_id: str,
    context_surface: Mapping[str, Any],
) -> float:
    score = DEFAULT_CONTEXT_SCORE_NEUTRAL

    same_side_wall_near = _safe_bool(_pick(context_surface, "same_side_wall_near"), False)
    same_side_wall_strength = _safe_float(_pick(context_surface, "same_side_wall_strength_score"), 0.0)
    opposing_wall_near = _safe_bool(_pick(context_surface, "opposing_wall_near"), False)
    opposing_wall_strength = _safe_float(_pick(context_surface, "opposing_wall_strength_score"), 0.0)
    oi_bias = _safe_str(_pick(context_surface, "oi_bias"), "UNKNOWN")

    if same_side_wall_near:
        score -= 0.10 if same_side_wall_strength < 0.60 else 0.20
    if opposing_wall_near and opposing_wall_strength >= 0.60:
        score += 0.05
    if _oi_bias_alignment(branch_id, oi_bias):
        score += 0.10
    else:
        score -= 0.10

    return max(0.0, min(score, 1.0))


def _branch_ready(surface: Mapping[str, Any]) -> bool:
    return bool(
        _safe_bool(_pick(surface, "present"), False)
        and _safe_bool(_pick(surface, "futures_bias_ok"), False)
        and _safe_bool(_pick(surface, "futures_impulse_ok"), False)
        and _safe_bool(_pick(surface, "pullback_detected"), False)
        and _safe_bool(_pick(surface, "micro_trap_blocked"), False)
        and _safe_bool(_pick(surface, "resume_support"), False)
        and _safe_bool(_pick(surface, "context_pass"), False)
        and _safe_bool(_pick(surface, "option_tradability_pass"), False)
        and not _safe_str(_pick(surface, "failed_stage"))
    )


def build_mist_branch_surface(
    *,
    branch_id: str,
    futures_surface: Mapping[str, Any] | None,
    option_surface: Mapping[str, Any] | None,
    fallback_option_surface: Mapping[str, Any] | None = None,
    strike_surface: Mapping[str, Any] | None = None,
    tradability_surface: Mapping[str, Any] | None = None,
    regime_surface: Mapping[str, Any] | None = None,
    runtime_mode_surface: Mapping[str, Any] | None = None,
    thresholds: Mapping[str, Any] | None = None,
    provider_ready: bool = True,
) -> dict[str, Any]:
    """
    Build one MIST branch surface.

    Input contract:
    - futures_surface: shared futures-core selected_features or equivalent dict
    - option_surface: shared option-core family surface or equivalent dict
    - fallback_option_surface: alternate live option candidate if present
    - strike_surface: family strike-selection support surface
    - tradability_surface: shared tradability shell for this branch
    - regime_surface: shared regime surface
    - runtime_mode_surface: classic runtime-mode surface
    """
    fut = _as_mapping(_pick(_as_mapping(futures_surface), "selected_features") or futures_surface)
    option_map = _as_mapping(option_surface)
    opt = _as_mapping(_pick(option_map, "selected_features") or option_map)
    opt_context = _context_features(option_map)
    opt_premium = _premium_health(option_map)

    fallback_map = _as_mapping(fallback_option_surface)
    fallback = _as_mapping(_pick(fallback_map, "selected_features") or fallback_map)

    strike = _as_mapping(strike_surface)
    trad = _as_mapping(tradability_surface)
    regime = _as_mapping(regime_surface)
    mode = _as_mapping(runtime_mode_surface)

    side = _branch_side(branch_id)
    bullish = branch_id == N.BRANCH_CALL

    regime_label = _safe_str(_pick(regime, "regime"), REGIME_NORMAL)
    runtime_mode = _safe_str(_pick(mode, "runtime_mode"), "")
    entry_mode_hint = _safe_str(
        _coalesce(
            _pick(opt, "entry_mode"),
            _pick(strike, "selection_mode_hint"),
            getattr(N, "ENTRY_MODE_ATM", "ATM"),
        )
    )

    fut_present = _safe_bool(_pick(fut, "present"), False)
    opt_present = _safe_bool(_pick(opt, "present"), False)
    fallback_present = _safe_bool(_pick(fallback, "present"), False)

    fut_delta = _safe_float(_pick(fut, "delta_3"), 0.0)
    fut_velocity_ratio = _safe_float(_pick(fut, "velocity_ratio"), 0.0)
    fut_weighted_ofi = _safe_float(_pick(fut, "weighted_ofi"), 0.0)
    fut_weighted_ofi_persist = _safe_float(_pick(fut, "weighted_ofi_persist"), 0.0)
    fut_vwap_distance = _safe_float(_pick(fut, "vwap_distance"), 0.0)
    fut_volume_norm = _safe_float(_pick(fut, "volume_norm"), 0.0)
    fut_event_rate_spike_ratio = _safe_float(_pick(fut, "event_rate_spike_ratio"), 0.0)
    fut_direction_score = _safe_float(_pick(fut, "direction_score", "trend_score"), 0.0)
    fut_ema9_slope = _safe_float(_pick(fut, "ema9_slope"), 0.0)
    fut_cvd_delta = _safe_float(_pick(fut, "cvd_delta"), 0.0)

    opt_delta = _safe_float(_pick(opt, "delta_3"), 0.0)
    opt_velocity_ratio = _safe_float(_pick(opt, "velocity_ratio"), 0.0)
    opt_weighted_ofi = _safe_float(_pick(opt, "weighted_ofi"), 0.0)
    opt_response_eff = _safe_float(_pick(opt, "response_efficiency"), 0.0)
    opt_vwap_distance = _safe_float(_pick(opt, "vwap_distance"), 0.0)

    opt_near_wall = _safe_bool(_pick(opt_context, "same_side_wall_near"), False)
    opt_wall_strength = _safe_float(_pick(opt_context, "same_side_wall_strength_score"), 0.0)
    opt_oi_bias = _safe_str(_pick(opt_context, "oi_bias"), "UNKNOWN")
    opt_context_score = _derived_context_score(
        branch_id=branch_id,
        context_surface=opt_context,
    )

    fallback_spread_ratio = _safe_float(_pick(fallback, "spread_ratio"), 999.0)
    fallback_ready = fallback_present and fallback_spread_ratio <= _threshold_float(
        thresholds,
        "FALLBACK_SPREAD_RATIO_MAX",
        1.80,
    )

    pullback_depth = abs(fut_vwap_distance)
    micro_trap_depth = min(abs(opt_vwap_distance), pullback_depth)
    pullback_depth_min = _threshold_float(thresholds, "PULLBACK_DEPTH_MIN", DEFAULT_PULLBACK_DEPTH_MIN)
    pullback_depth_max = _threshold_float(thresholds, "PULLBACK_DEPTH_MAX", DEFAULT_PULLBACK_DEPTH_MAX)

    bull_ofi_min = _threshold_float(thresholds, "FUT_OFI_60S_BULLISH_MIN", DEFAULT_BULL_OFI_MIN)
    bear_ofi_max = _threshold_float(thresholds, "FUT_OFI_60S_BEARISH_MAX", DEFAULT_BEAR_OFI_MAX)
    fut_vel_ratio_min = _threshold_float(thresholds, "FUT_VEL_RATIO_MIN", DEFAULT_FUTURES_IMPULSE_VELOCITY_MIN)
    fut_vol_norm_min = _threshold_float(thresholds, "FUT_VOL_NORM_MIN", DEFAULT_FUTURES_VOL_NORM_MIN)
    resume_velocity_min = _threshold_float(
        thresholds,
        "RESUME_VELOCITY_RATIO_MIN",
        DEFAULT_RESUME_VELOCITY_RATIO_MIN,
    )
    resume_override_ofi_max = _threshold_float(
        thresholds,
        "RESUME_OVERRIDE_OFI_MAX",
        DEFAULT_RESUME_OVERRIDE_OFI_MAX,
    )
    resume_override_vol_min = _threshold_float(
        thresholds,
        "RESUME_OVERRIDE_VOL_MIN",
        DEFAULT_RESUME_OVERRIDE_VOL_MIN,
    )
    trend_score_min = _threshold_float(thresholds, "TREND_SCORE_MIN", DEFAULT_TREND_SCORE_MIN)

    alignment_ok = _directional_ok(fut_delta, branch_id)
    option_confirmation = _directional_ok(opt_delta, branch_id)
    futures_bias_ok = alignment_ok and _directional_ok(fut_ema9_slope, branch_id)
    futures_impulse_ok = (
        futures_bias_ok
        and fut_velocity_ratio >= fut_vel_ratio_min
        and fut_volume_norm >= fut_vol_norm_min
        and _ofi_direction_ok(fut_weighted_ofi_persist, branch_id, bull_ofi_min, bear_ofi_max)
    )

    trend_score = (
        (fut_velocity_ratio * (1.0 if _directional_ok(fut_delta, branch_id) else -1.0))
        + (abs(fut_direction_score) * 0.20)
        + (abs(fut_cvd_delta) * 0.02)
        + (
            (fut_weighted_ofi_persist - 0.50) * 2.0
            if bullish
            else ((0.50 - fut_weighted_ofi_persist) * 2.0)
        )
    )

    pullback_detected = (
        pullback_depth >= pullback_depth_min
        and pullback_depth <= pullback_depth_max
    )

    micro_trap_flag = micro_trap_depth > DEFAULT_MICRO_TRAP_DEPTH_MAX and not option_confirmation
    micro_trap_blocked = not micro_trap_flag

    resume_support = (
        option_confirmation
        and opt_velocity_ratio >= resume_velocity_min
        and opt_response_eff > 0.0
        and (
            _directional_ok(opt_weighted_ofi, branch_id)
            or _resume_override_ok(
                weighted_ofi=opt_weighted_ofi,
                volume_norm=fut_volume_norm,
                branch_id=branch_id,
                override_ofi_max=resume_override_ofi_max,
                override_vol_min=resume_override_vol_min,
            )
        )
    )

    resume_override_pass = _resume_override_ok(
        weighted_ofi=opt_weighted_ofi,
        volume_norm=fut_volume_norm,
        branch_id=branch_id,
        override_ofi_max=resume_override_ofi_max,
        override_vol_min=resume_override_vol_min,
    )

    context_pass = _context_pass(runtime_mode, provider_ready)
    option_tradability_pass = _safe_bool(
        _coalesce(
            _pick(trad, "entry_pass"),
            _pick(option_map, "selected_option_tradability_ok"),
            _pick(opt_premium, "tradability_ok"),
        ),
        False,
    )

    near_wall_penalty = 0.20 if opt_near_wall and opt_wall_strength >= 0.60 else 0.0
    oi_bias_alignment = _oi_bias_alignment(branch_id, opt_oi_bias)

    setup_score = (
        max(trend_score, 0.0) * 0.40
        + (opt_response_eff * 1.50 * 0.20)
        + (fut_velocity_ratio * 0.15)
        + (opt_context_score * 0.10)
        + (0.10 if pullback_detected else 0.0)
        + (0.10 if resume_support else 0.0)
        - near_wall_penalty
    )

    surface_present = fut_present and opt_present
    branch_ready = bool(
        surface_present
        and futures_bias_ok
        and futures_impulse_ok
        and pullback_detected
        and micro_trap_blocked
        and resume_support
        and context_pass
        and option_tradability_pass
    )

    return {
        "surface_kind": "mist",
        "present": surface_present,
        "branch_ready": branch_ready,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MIST", "MIST")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MIST", "MIST")),
        "branch_id": branch_id,
        "side": side,
        "regime": regime_label,
        "runtime_mode": runtime_mode,
        "entry_mode_hint": entry_mode_hint,
        "provider_ready": provider_ready,
        "futures_features": fut,
        "primary_features": opt,
        "context_features": opt_context,
        "premium_health": opt_premium,
        "fallback_features": fallback,
        "strike_surface": strike,
        "tradability": trad,
        "regime_surface": regime,
        "runtime_mode_surface": mode,
        "alignment_ok": alignment_ok,
        "option_confirmation": option_confirmation,
        "futures_bias_ok": futures_bias_ok,
        "futures_impulse_ok": futures_impulse_ok,
        "trend_direction_ok": futures_bias_ok,
        "trend_score": trend_score,
        "trend_score_ok": trend_score >= trend_score_min,
        "pullback_depth": pullback_depth,
        "pullback_detected": pullback_detected,
        "micro_trap_depth": micro_trap_depth,
        "micro_trap_flag": micro_trap_flag,
        "micro_trap_blocked": micro_trap_blocked,
        "resume_support": resume_support,
        "resume_confirmed": resume_support,
        "resume_override_pass": resume_override_pass,
        "context_pass": context_pass,
        "option_tradability_pass": option_tradability_pass,
        "fallback_ready": fallback_ready,
        "oi_bias_alignment": oi_bias_alignment,
        "near_same_side_wall": opt_near_wall,
        "same_side_wall_strength_score": opt_wall_strength,
        "setup_score": setup_score,
        "feature_refs": {
            "fut_delta": fut_delta,
            "fut_velocity_ratio": fut_velocity_ratio,
            "fut_weighted_ofi": fut_weighted_ofi,
            "fut_weighted_ofi_persist": fut_weighted_ofi_persist,
            "fut_vwap_distance": fut_vwap_distance,
            "fut_volume_norm": fut_volume_norm,
            "fut_event_rate_spike_ratio": fut_event_rate_spike_ratio,
            "opt_delta": opt_delta,
            "opt_velocity_ratio": opt_velocity_ratio,
            "opt_weighted_ofi": opt_weighted_ofi,
            "opt_response_efficiency": opt_response_eff,
            "opt_context_score": opt_context_score,
            "opt_oi_bias": opt_oi_bias,
        },
        "passed_stages": tuple(
            stage
            for stage, passed in (
                ("futures_bias", futures_bias_ok),
                ("futures_impulse", futures_impulse_ok),
                ("pullback", pullback_detected),
                ("micro_trap_check", micro_trap_blocked),
                ("resume_confirmation", resume_support),
                ("context_pass", context_pass),
                ("option_tradability", option_tradability_pass),
            )
            if passed
        ),
        "failed_stage": (
            ""
            if branch_ready
            else "futures_bias"
            if not futures_bias_ok
            else "futures_impulse"
            if not futures_impulse_ok
            else "pullback"
            if not pullback_detected
            else "micro_trap_check"
            if not micro_trap_blocked
            else "resume_confirmation"
            if not resume_support
            else "context_pass"
            if not context_pass
            else "option_tradability"
        ),
    }


def build_mist_family_surface(
    *,
    call_surface: Mapping[str, Any] | None,
    put_surface: Mapping[str, Any] | None,
    runtime_mode_surface: Mapping[str, Any] | None = None,
    regime_surface: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the family-level MIST surface bundle consumed by features.py.

    This remains a payload support surface, not a candidate selector.
    """
    call = _as_mapping(call_surface)
    put = _as_mapping(put_surface)
    mode = _as_mapping(runtime_mode_surface)
    regime = _as_mapping(regime_surface)

    call_present = _safe_bool(_pick(call, "present"), False)
    put_present = _safe_bool(_pick(put, "present"), False)

    call_setup_score = _safe_float(_pick(call, "setup_score"), 0.0)
    put_setup_score = _safe_float(_pick(put, "setup_score"), 0.0)

    if call_setup_score > put_setup_score + EPSILON:
        dominant_branch = N.BRANCH_CALL
    elif put_setup_score > call_setup_score + EPSILON:
        dominant_branch = N.BRANCH_PUT
    else:
        dominant_branch = ""

    call_ready = _branch_ready(call)
    put_ready = _branch_ready(put)

    return {
        "surface_kind": "mist_family",
        "present": call_present or put_present,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MIST", "MIST")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MIST", "MIST")),
        "runtime_mode": _safe_str(_pick(mode, "runtime_mode"), ""),
        "regime": _safe_str(_pick(regime, "regime"), REGIME_NORMAL),
        "call": call,
        "put": put,
        "call_present": call_present,
        "put_present": put_present,
        "call_ready": call_ready,
        "put_ready": put_ready,
        "call_setup_score": call_setup_score,
        "put_setup_score": put_setup_score,
        "dominant_branch": dominant_branch,
        "eligible": bool(call_ready or put_ready),
    }
