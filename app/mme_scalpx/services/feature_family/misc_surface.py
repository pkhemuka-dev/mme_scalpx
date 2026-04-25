from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/misc_surface.py

Canonical MISC feature surface for ScalpX MME.

Purpose
-------
This module OWNS:
- doctrine-specific feature publication support for MISC only
- deterministic CALL / PUT MISC surface derivation from shared-core payloads
- gate-ready booleans for the MISC compression -> breakout -> expansion ->
  retest / hesitation -> resume stack
- JSON-friendly branch and family support surfaces for services/features.py

This module DOES NOT own:
- strategy state machine mutation
- entry / exit decisions
- cooldown or re-entry mutation
- provider-routing policy
- Redis I/O

Frozen design law
-----------------
- MISC remains futures-led and option-confirmed.
- MISC identity is compression box -> directional burst -> monitored shallow
  retest / hesitation -> resume entry.
- ARMED means compression detected plus breakout accepted; RETEST_MONITOR means
  waiting for shallow retest or hesitation-resume.
- This module is feature-surface only, not a strategy engine.
- Returned surfaces must be deterministic and JSON-friendly plain mappings.

Implementation note
-------------------
The current seam does not yet publish a dedicated compression box object, so
this module derives a conservative compression proxy from shared-core futures
and option surfaces and publishes the explicit support facts strategy.py will
later consume.
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

EPSILON: Final[float] = 1e-8

DEFAULT_COMPRESSION_WIDTH_MAX: Final[float] = 12.0
DEFAULT_COMPRESSION_WIDTH_MIN: Final[float] = 0.05
DEFAULT_PREBREAK_PROXIMITY_MAX: Final[float] = 3.0
DEFAULT_BREAKOUT_BUFFER_MIN: Final[float] = 0.20
DEFAULT_BREAKOUT_VEL_RATIO_MIN: Final[float] = 1.15
DEFAULT_BREAKOUT_VOL_NORM_MIN: Final[float] = 1.10
DEFAULT_EVENT_RATE_SPIKE_MIN: Final[float] = 1.20
DEFAULT_CALL_OFI_MIN: Final[float] = 0.52
DEFAULT_CALL_BREAKOUT_OFI_MIN: Final[float] = 0.56
DEFAULT_PUT_BREAKOUT_OFI_MAX: Final[float] = 0.44
DEFAULT_CALL_NOF_MIN: Final[float] = 0.06
DEFAULT_CALL_BREAKOUT_NOF_MIN: Final[float] = 0.08
DEFAULT_PUT_NOF_MAX_BEAR: Final[float] = -0.06
DEFAULT_PUT_BREAKOUT_NOF_MAX_BEAR: Final[float] = -0.08
DEFAULT_MAX_BREAKOUT_EXTENSION_PCT: Final[float] = 18.0
DEFAULT_RETEST_MAX_DEPTH_PCT: Final[float] = 0.10
DEFAULT_RETEST_HOLD_BUFFER: Final[float] = 0.05
DEFAULT_RETEST_VOLUME_RATIO_MAX: Final[float] = 0.75
DEFAULT_RETEST_CALL_OFI_MIN: Final[float] = 0.53
DEFAULT_RETEST_PUT_OFI_MAX: Final[float] = 0.47
DEFAULT_RETEST_CALL_NOF_MIN: Final[float] = 0.05
DEFAULT_RETEST_PUT_NOF_MAX: Final[float] = -0.05
DEFAULT_RESUME_VOL_MIN: Final[float] = 1.10
DEFAULT_RESUME_CALL_OFI_MIN: Final[float] = 0.55
DEFAULT_RESUME_PUT_OFI_MAX: Final[float] = 0.45
DEFAULT_HESITATION_BAND_CALL: Final[float] = 0.03
DEFAULT_HESITATION_BAND_PUT: Final[float] = 0.03
DEFAULT_HESITATION_MIN_SEC: Final[float] = 1.5
DEFAULT_HESITATION_MAX_SEC: Final[float] = 4.0
DEFAULT_HESITATION_CALL_OFI_MIN: Final[float] = 0.52
DEFAULT_HESITATION_PUT_OFI_MAX: Final[float] = 0.48
DEFAULT_HESITATION_CALL_NOF_MIN: Final[float] = 0.04
DEFAULT_HESITATION_PUT_NOF_MAX: Final[float] = -0.04
DEFAULT_PREMIUM_HEALTH_TOLERANCE_POINTS: Final[float] = 1.0
DEFAULT_NEAR_WALL_PENALTY: Final[float] = 0.20
DEFAULT_CONTEXT_SCORE_NEUTRAL: Final[float] = 0.50

__all__ = [
    "build_misc_branch_surface",
    "build_misc_family_surface",
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


def _ofi_ok(value: float, branch_id: str, call_min: float, put_max: float) -> bool:
    return value >= call_min if branch_id == N.BRANCH_CALL else value <= put_max


def _nof_ok(value: float, branch_id: str, call_min: float, put_max: float) -> bool:
    return value >= call_min if branch_id == N.BRANCH_CALL else value <= put_max


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


def _retest_timeout_sec(regime: str, thresholds: Mapping[str, Any] | None) -> float:
    regime_up = _safe_str(regime, REGIME_NORMAL).upper()
    if regime_up == REGIME_LOWVOL:
        return _threshold_float(thresholds, "LOWVOL_RETEST_MAX_TIME_SEC", 10.0)
    if regime_up == REGIME_FAST:
        return _threshold_float(thresholds, "FAST_RETEST_MAX_TIME_SEC", 6.0)
    return _threshold_float(thresholds, "NORMAL_RETEST_MAX_TIME_SEC", 11.0)


def _compression_proxy(
    *,
    fut_ltp: float,
    fut_vwap_distance: float,
    opt_context_score: float,
    fut_spread_ratio: float,
) -> tuple[float, float, float, float]:
    """
    Conservative compression proxy from current shared seam.

    Returns:
    compression_low, compression_high, compression_mid, compression_width
    """
    width = max(abs(fut_vwap_distance) * 0.80, fut_spread_ratio, 0.0) + max(0.0, (1.0 - opt_context_score)) * 0.10
    low = fut_ltp - width
    high = fut_ltp + width
    mid = (low + high) / 2.0
    return low, high, mid, width


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
        and _safe_bool(_pick(surface, "compression_detection"), False)
        and _safe_bool(_pick(surface, "breakout_trigger"), False)
        and _safe_bool(_pick(surface, "breakout_acceptance"), False)
        and _safe_bool(_pick(surface, "retest_monitor_alive"), False)
        and bool(_safe_str(_pick(surface, "retest_type")))
        and _safe_bool(_pick(surface, "resume_confirmed"), False)
        and _safe_bool(_pick(surface, "context_pass"), False)
        and _safe_bool(_pick(surface, "option_tradability_pass"), False)
        and not _safe_str(_pick(surface, "failed_stage"))
    )


def build_misc_branch_surface(
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
    retest_elapsed_sec: float | None = None,
    hesitation_elapsed_sec: float | None = None,
) -> dict[str, Any]:
    """
    Build one MISC branch surface.

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
    fallback = _as_mapping(_pick(_as_mapping(fallback_map), "selected_features") or fallback_map)

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

    fut_ltp = _safe_float(_pick(fut, "ltp"), 0.0)
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
    fut_spread_ratio = _safe_float(_pick(fut, "spread_ratio"), 0.0)
    fut_book_pressure = _safe_float(_pick(fut, "book_pressure"), 0.5)
    fut_nof = _safe_float(_pick(fut, "nof", "nof_3", "net_order_flow", "nof_slope"), fut_delta)

    opt_ltp = _safe_float(_pick(opt, "ltp"), 0.0)
    opt_delta = _safe_float(_pick(opt, "delta_3"), 0.0)
    opt_velocity_ratio = _safe_float(_pick(opt, "velocity_ratio"), 0.0)
    opt_weighted_ofi = _safe_float(_pick(opt, "weighted_ofi"), 0.0)
    opt_response_eff = _safe_float(_pick(opt, "response_efficiency"), 0.0)
    opt_context_score = _derived_context_score(
        branch_id=branch_id,
        context_surface=opt_context,
    )
    opt_near_wall = _safe_bool(_pick(opt_context, "same_side_wall_near"), False)
    opt_wall_strength = _safe_float(_pick(opt_context, "same_side_wall_strength_score"), 0.0)
    opt_oi_bias = _safe_str(_pick(opt_context, "oi_bias"), "UNKNOWN")
    opt_spread_ratio = _safe_float(_pick(opt, "spread_ratio"), 0.0)

    fallback_spread_ratio = _safe_float(_pick(fallback, "spread_ratio"), 999.0)
    fallback_ready = fallback_present and fallback_spread_ratio <= _threshold_float(
        thresholds,
        "FALLBACK_SPREAD_RATIO_MAX",
        1.80,
    )

    compression_ofi_call_min = _threshold_float(thresholds, "COMPRESSION_OFI_CALL_MIN", DEFAULT_CALL_OFI_MIN)
    compression_ofi_put_max = _threshold_float(thresholds, "COMPRESSION_OFI_MAX_BEAR", 0.48)
    breakout_ofi_call_min = _threshold_float(thresholds, "BREAKOUT_OFI_MIN", DEFAULT_CALL_BREAKOUT_OFI_MIN)
    breakout_ofi_put_max = _threshold_float(thresholds, "BREAKOUT_OFI_MAX_BEAR", DEFAULT_PUT_BREAKOUT_OFI_MAX)
    breakout_nof_call_min = _threshold_float(thresholds, "BREAKOUT_NOF_CALL_MIN", DEFAULT_CALL_BREAKOUT_NOF_MIN)
    breakout_nof_put_max = _threshold_float(thresholds, "BREAKOUT_NOF_PUT_MAX_BEAR", DEFAULT_PUT_BREAKOUT_NOF_MAX_BEAR)
    compression_nof_call_min = _threshold_float(thresholds, "NOF_CALL_MIN", DEFAULT_CALL_NOF_MIN)
    compression_nof_put_max = _threshold_float(thresholds, "NOF_PUT_MAX_BEAR", DEFAULT_PUT_NOF_MAX_BEAR)
    breakout_vel_min = _threshold_float(thresholds, "BREAKOUT_VEL_RATIO_MIN", DEFAULT_BREAKOUT_VEL_RATIO_MIN)
    breakout_vol_min = _threshold_float(thresholds, "BREAKOUT_VOL_SPIKE_MIN", DEFAULT_BREAKOUT_VOL_NORM_MIN)
    event_rate_spike_min = _threshold_float(thresholds, "EVENT_RATE_SPIKE_MIN", DEFAULT_EVENT_RATE_SPIKE_MIN)
    breakout_buffer_min = _threshold_float(thresholds, "BREAKOUT_TRIGGER_BUFFER_PCT", DEFAULT_BREAKOUT_BUFFER_MIN)
    compression_width_max = _threshold_float(thresholds, "COMPRESSION_MAX_WIDTH_PCT", DEFAULT_COMPRESSION_WIDTH_MAX)
    compression_width_min = _threshold_float(thresholds, "COMPRESSION_MIN_WIDTH_PCT", DEFAULT_COMPRESSION_WIDTH_MIN)
    prebreak_proximity_tol = _threshold_float(thresholds, "PREBREAK_PROXIMITY_TOLERANCE_PCT", DEFAULT_PREBREAK_PROXIMITY_MAX)
    max_breakout_extension_pct = _threshold_float(thresholds, "MAX_BREAKOUT_EXTENSION_PCT", DEFAULT_MAX_BREAKOUT_EXTENSION_PCT)
    retest_max_depth_pct = _threshold_float(thresholds, "RETEST_MAX_DEPTH_PCT", DEFAULT_RETEST_MAX_DEPTH_PCT)
    retest_hold_buffer = _threshold_float(thresholds, "RETEST_HOLD_BUFFER_PCT", DEFAULT_RETEST_HOLD_BUFFER)
    retest_volume_ratio_max = _threshold_float(thresholds, "RETEST_VOLUME_RATIO_MAX", DEFAULT_RETEST_VOLUME_RATIO_MAX)
    retest_call_ofi_min = _threshold_float(thresholds, "RETEST_OFI_CALL_MIN", DEFAULT_RETEST_CALL_OFI_MIN)
    retest_put_ofi_max = _threshold_float(thresholds, "RETEST_OFI_MAX_BEAR", DEFAULT_RETEST_PUT_OFI_MAX)
    retest_call_nof_min = _threshold_float(thresholds, "RETEST_NOF_CALL_MIN", DEFAULT_RETEST_CALL_NOF_MIN)
    retest_put_nof_max = _threshold_float(thresholds, "RETEST_NOF_PUT_MAX_BEAR", DEFAULT_RETEST_PUT_NOF_MAX)
    resume_vol_min = _threshold_float(thresholds, "RESUME_VOL_MIN", DEFAULT_RESUME_VOL_MIN)
    resume_call_ofi_min = _threshold_float(thresholds, "RESUME_OFI_CALL_MIN", DEFAULT_RESUME_CALL_OFI_MIN)
    resume_put_ofi_max = _threshold_float(thresholds, "RESUME_OFI_MAX_BEAR", DEFAULT_RESUME_PUT_OFI_MAX)
    hesitation_band = _threshold_float(
        thresholds,
        "HESITATION_BAND_CALL_PCT" if bullish else "HESITATION_BAND_PUT_PCT",
        DEFAULT_HESITATION_BAND_CALL if bullish else DEFAULT_HESITATION_BAND_PUT,
    )
    hesitation_min_sec = _threshold_float(thresholds, "HESITATION_MIN_SEC", DEFAULT_HESITATION_MIN_SEC)
    hesitation_max_sec = _threshold_float(thresholds, "HESITATION_MAX_SEC", DEFAULT_HESITATION_MAX_SEC)
    hesitation_call_ofi_min = _threshold_float(thresholds, "HESITATION_CALL_OFI_MIN", DEFAULT_HESITATION_CALL_OFI_MIN)
    hesitation_put_ofi_max = _threshold_float(thresholds, "HESITATION_PUT_OFI_MAX", DEFAULT_HESITATION_PUT_OFI_MAX)
    hesitation_call_nof_min = _threshold_float(thresholds, "HESITATION_CALL_NOF_MIN", DEFAULT_HESITATION_CALL_NOF_MIN)
    hesitation_put_nof_max = _threshold_float(thresholds, "HESITATION_PUT_NOF_MAX", DEFAULT_HESITATION_PUT_NOF_MAX)
    premium_health_tol = _threshold_float(thresholds, "PREMIUM_HEALTH_TOLERANCE_POINTS", DEFAULT_PREMIUM_HEALTH_TOLERANCE_POINTS)

    compression_low, compression_high, compression_mid, compression_width = _compression_proxy(
        fut_ltp=fut_ltp,
        fut_vwap_distance=fut_vwap_distance,
        opt_context_score=opt_context_score,
        fut_spread_ratio=fut_spread_ratio,
    )
    compression_width_pct = 0.0 if abs(compression_mid) <= EPSILON else (compression_width / max(abs(compression_mid), EPSILON)) * 100.0

    if bullish:
        prebreak_distance = max(compression_high - fut_ltp, 0.0)
    else:
        prebreak_distance = max(fut_ltp - compression_low, 0.0)

    compression_valid = compression_width_pct >= compression_width_min and compression_width_pct <= compression_width_max
    prebreak_proximity_ok = prebreak_distance <= prebreak_proximity_tol
    directional_bias_ok = _directional_ok(fut_delta, branch_id) and _directional_ok(fut_ema9_slope, branch_id)
    compression_detection = (
        compression_valid
        and prebreak_proximity_ok
        and directional_bias_ok
        and _ofi_ok(fut_weighted_ofi, branch_id, compression_ofi_call_min, compression_ofi_put_max)
        and _nof_ok(fut_nof, branch_id, compression_nof_call_min, compression_nof_put_max)
    )

    breakout_trigger = (
        compression_detection
        and (
            fut_ltp > (compression_high + breakout_buffer_min)
            if bullish
            else fut_ltp < (compression_low - breakout_buffer_min)
        )
        and _ofi_ok(fut_weighted_ofi, branch_id, breakout_ofi_call_min, breakout_ofi_put_max)
        and _ofi_ok(fut_weighted_ofi_persist, branch_id, breakout_ofi_call_min, breakout_ofi_put_max)
        and _nof_ok(fut_nof, branch_id, breakout_nof_call_min, breakout_nof_put_max)
        and _directional_ok(fut_cvd_delta, branch_id)
        and _directional_ok(fut_delta, branch_id)
        and fut_velocity_ratio >= breakout_vel_min
        and fut_volume_norm >= breakout_vol_min
    )

    breakout_ref = compression_high if bullish else compression_low
    breakout_extension_pct = (
        abs(fut_ltp - breakout_ref) / max(abs(compression_mid), EPSILON)
    ) * 100.0
    breakout_acceptance = (
        breakout_trigger
        and breakout_extension_pct <= max_breakout_extension_pct
        and fut_event_rate_spike_ratio >= event_rate_spike_min
    )

    retest_timeout_sec = _retest_timeout_sec(regime_label, thresholds)
    retest_elapsed = retest_elapsed_sec if retest_elapsed_sec is not None else 0.0
    retest_monitor_alive = (
        breakout_acceptance
        and retest_elapsed <= retest_timeout_sec
        and opt_present
        and _safe_bool(
            _coalesce(
                _pick(trad, "entry_pass"),
                _pick(option_map, "selected_option_tradability_ok"),
                _pick(opt_premium, "tradability_ok"),
            ),
            False,
        )
    )

    premium_health_ok = abs(opt_delta) <= max(abs(fut_delta) + premium_health_tol, premium_health_tol)
    retest_hold_ok = (
        fut_ltp >= breakout_ref * (1.0 - retest_hold_buffer)
        if bullish
        else fut_ltp <= breakout_ref * (1.0 + retest_hold_buffer)
    )
    retest_depth_pct = breakout_extension_pct
    retest_volume_ratio = 0.0 if fut_volume_norm <= EPSILON else min(opt_response_eff / max(fut_volume_norm, EPSILON), 10.0)

    full_retest = (
        retest_monitor_alive
        and retest_hold_ok
        and retest_depth_pct <= retest_max_depth_pct
        and retest_volume_ratio <= retest_volume_ratio_max
        and _ofi_ok(fut_weighted_ofi, branch_id, retest_call_ofi_min, retest_put_ofi_max)
        and _nof_ok(fut_nof, branch_id, retest_call_nof_min, retest_put_nof_max)
        and _directional_ok(fut_cvd_delta, branch_id)
        and premium_health_ok
    )

    hesitation_elapsed = hesitation_elapsed_sec if hesitation_elapsed_sec is not None else 0.0
    hesitation_price_band_ok = abs(fut_ltp - breakout_ref) <= hesitation_band
    hesitation_retest = (
        retest_monitor_alive
        and hesitation_price_band_ok
        and hesitation_elapsed >= hesitation_min_sec
        and hesitation_elapsed <= hesitation_max_sec
        and _ofi_ok(fut_weighted_ofi, branch_id, hesitation_call_ofi_min, hesitation_put_ofi_max)
        and _nof_ok(fut_nof, branch_id, hesitation_call_nof_min, hesitation_put_nof_max)
    )

    retest_type = "FULL_RETEST" if full_retest else "HESITATION" if hesitation_retest else ""
    resume_confirmed = (
        retest_monitor_alive
        and (full_retest or hesitation_retest)
        and _directional_ok(opt_delta, branch_id)
        and _ofi_ok(fut_weighted_ofi, branch_id, resume_call_ofi_min, resume_put_ofi_max)
        and fut_volume_norm >= resume_vol_min
        and opt_velocity_ratio >= 1.0
        and opt_response_eff > 0.0
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

    near_wall_penalty = DEFAULT_NEAR_WALL_PENALTY if opt_near_wall and opt_wall_strength >= 0.60 else 0.0
    oi_bias_alignment = _oi_bias_alignment(branch_id, opt_oi_bias)

    setup_score = (
        (fut_velocity_ratio * 0.15)
        + (fut_volume_norm * 0.10)
        + (opt_response_eff * 1.50 * 0.10)
        + (opt_context_score * 0.10)
        + (0.15 if compression_detection else 0.0)
        + (0.15 if breakout_trigger else 0.0)
        + (0.15 if breakout_acceptance else 0.0)
        + (0.10 if (full_retest or hesitation_retest) else 0.0)
        + (0.15 if resume_confirmed else 0.0)
        - near_wall_penalty
    )

    surface_present = fut_present and opt_present
    branch_ready = bool(
        surface_present
        and compression_detection
        and breakout_trigger
        and breakout_acceptance
        and retest_monitor_alive
        and bool(retest_type)
        and resume_confirmed
        and context_pass
        and option_tradability_pass
    )

    return {
        "surface_kind": "misc",
        "present": surface_present,
        "branch_ready": branch_ready,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MISC", "MISC")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MISC", "MISC")),
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
        "compression_low": compression_low,
        "compression_high": compression_high,
        "compression_mid": compression_mid,
        "compression_width": compression_width,
        "compression_width_pct": compression_width_pct,
        "compression_valid": compression_valid,
        "prebreak_distance": prebreak_distance,
        "prebreak_proximity_ok": prebreak_proximity_ok,
        "directional_bias_ok": directional_bias_ok,
        "compression_detection": compression_detection,
        "breakout_trigger": breakout_trigger,
        "breakout_ref": breakout_ref,
        "breakout_extension_pct": breakout_extension_pct,
        "breakout_acceptance": breakout_acceptance,
        "retest_timeout_sec": retest_timeout_sec,
        "retest_elapsed_sec": retest_elapsed,
        "retest_monitor_alive": retest_monitor_alive,
        "premium_health_ok": premium_health_ok,
        "retest_hold_ok": retest_hold_ok,
        "retest_depth_pct": retest_depth_pct,
        "retest_volume_ratio": retest_volume_ratio,
        "full_retest": full_retest,
        "hesitation_retest": hesitation_retest,
        "retest_type": retest_type,
        "resume_confirmed": resume_confirmed,
        "context_pass": context_pass,
        "option_tradability_pass": option_tradability_pass,
        "fallback_ready": fallback_ready,
        "oi_bias_alignment": oi_bias_alignment,
        "near_same_side_wall": opt_near_wall,
        "same_side_wall_strength_score": opt_wall_strength,
        "setup_score": setup_score,
        "feature_refs": {
            "fut_ltp": fut_ltp,
            "fut_delta": fut_delta,
            "fut_velocity_ratio": fut_velocity_ratio,
            "fut_weighted_ofi": fut_weighted_ofi,
            "fut_weighted_ofi_persist": fut_weighted_ofi_persist,
            "fut_vwap_distance": fut_vwap_distance,
            "fut_volume_norm": fut_volume_norm,
            "fut_event_rate_spike_ratio": fut_event_rate_spike_ratio,
            "fut_direction_score": fut_direction_score,
            "fut_nof": fut_nof,
            "opt_ltp": opt_ltp,
            "opt_delta": opt_delta,
            "opt_velocity_ratio": opt_velocity_ratio,
            "opt_weighted_ofi": opt_weighted_ofi,
            "opt_response_efficiency": opt_response_eff,
            "opt_context_score": opt_context_score,
            "opt_spread_ratio": opt_spread_ratio,
            "opt_oi_bias": opt_oi_bias,
        },
        "passed_stages": tuple(
            stage
            for stage, passed in (
                ("compression_detection", compression_detection),
                ("directional_breakout_trigger", breakout_trigger),
                ("expansion_acceptance", breakout_acceptance),
                ("retest_monitor", retest_monitor_alive),
                ("retest_type_resolution", bool(retest_type)),
                ("resume_confirmation", resume_confirmed),
                ("context_pass", context_pass),
                ("option_tradability", option_tradability_pass),
            )
            if passed
        ),
        "failed_stage": (
            ""
            if branch_ready
            else "compression_detection"
            if not compression_detection
            else "directional_breakout_trigger"
            if not breakout_trigger
            else "expansion_acceptance"
            if not breakout_acceptance
            else "retest_monitor"
            if not retest_monitor_alive
            else "retest_type_resolution"
            if not bool(retest_type)
            else "resume_confirmation"
            if not resume_confirmed
            else "context_pass"
            if not context_pass
            else "option_tradability"
        ),
    }


def build_misc_family_surface(
    *,
    call_surface: Mapping[str, Any] | None,
    put_surface: Mapping[str, Any] | None,
    runtime_mode_surface: Mapping[str, Any] | None = None,
    regime_surface: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the family-level MISC surface bundle consumed by features.py.

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
        "surface_kind": "misc_family",
        "present": call_present or put_present,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MISC", "MISC")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MISC", "MISC")),
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

# =============================================================================
# Batch 9 freeze hardening: doctrine-surface fail-closed guards
# =============================================================================
#
# This module remains feature-surface only. These wrappers enforce publication
# hygiene around branch/family readiness without adding strategy decisions,
# provider routing, Redis I/O, or service behavior.

_BATCH9_SURFACE_HARDENING_VERSION = "1"
_BATCH9_FAMILY_LC = "misc"
_BATCH9_FAMILY_ID = "MISC"
_BATCH9_ALLOWED_BRANCH_IDS = (N.BRANCH_CALL, N.BRANCH_PUT)

_BATCH9_ORIGINAL_BRANCH_BUILDER = build_misc_branch_surface
_BATCH9_ORIGINAL_FAMILY_BUILDER = build_misc_family_surface


def _batch9_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _batch9_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = _batch9_text(value).lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _batch9_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _batch9_pick(mapping: Mapping[str, Any] | None, *keys: str, default: Any = None) -> Any:
    if not isinstance(mapping, Mapping):
        return default
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return default


def _batch9_branch_side(branch_id: str) -> str:
    if branch_id == N.BRANCH_CALL:
        return N.SIDE_CALL
    if branch_id == N.BRANCH_PUT:
        return N.SIDE_PUT
    raise ValueError(f"invalid branch_id for {_BATCH9_FAMILY_ID}: {branch_id!r}")


def _batch9_runtime_mode(
    *,
    runtime_mode_surface: Mapping[str, Any] | None,
    surface: Mapping[str, Any] | None = None,
) -> str:
    return _batch9_text(
        _batch9_pick(surface, "runtime_mode")
        or _batch9_pick(runtime_mode_surface, "runtime_mode", "mode")
        or "",
        "",
    ).upper()


def _batch9_runtime_disabled(mode: str) -> bool:
    disabled = {
        _batch9_text(getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")).upper(),
        "DISABLED",
    }
    return _batch9_text(mode).upper() in disabled


def _batch9_force_not_ready(surface: Mapping[str, Any], reason: str) -> dict[str, Any]:
    out = dict(surface)
    previous_failed_stage = _batch9_text(out.get("failed_stage"))
    out["branch_ready"] = False
    out["eligible"] = False
    out["batch9_freeze_blocked_reason"] = reason
    if previous_failed_stage and previous_failed_stage != reason:
        out["pre_batch9_failed_stage"] = previous_failed_stage
    if reason in {"runtime_disabled", "provider_not_ready"}:
        out["context_pass"] = False
    # Hard publication blocks must be the canonical failed_stage so downstream
    # consumers never confuse an earlier doctrine-stage miss with a runtime /
    # provider hard stop.
    out["failed_stage"] = reason
    return out


def _batch9_branch_ready_truth(surface: Mapping[str, Any]) -> bool:
    return bool(
        _batch9_bool(surface.get("branch_ready"), False)
        and _batch9_bool(surface.get("present"), False)
        and _batch9_bool(surface.get("context_pass"), False)
        and _batch9_bool(surface.get("option_tradability_pass"), False)
        and not _batch9_text(surface.get("failed_stage"))
    )


def _batch9_normalize_branch_surface(
    surface: Mapping[str, Any],
    *,
    branch_id: str,
    runtime_mode_surface: Mapping[str, Any] | None,
    provider_ready: bool,
) -> dict[str, Any]:
    side = _batch9_branch_side(branch_id)
    out = dict(surface)
    out["family_id"] = _batch9_text(out.get("family_id"), _BATCH9_FAMILY_ID)
    out["branch_id"] = branch_id
    out["side"] = side

    mode = _batch9_runtime_mode(runtime_mode_surface=runtime_mode_surface, surface=out)
    if _batch9_runtime_disabled(mode):
        return _batch9_force_not_ready(out, "runtime_disabled")

    if not bool(provider_ready):
        return _batch9_force_not_ready(out, "provider_not_ready")

    if _BATCH9_FAMILY_ID == "MISO" and not _batch9_bool(out.get("strike_bundle_present"), False):
        return _batch9_force_not_ready(out, "strike_bundle_present")

    if not _batch9_branch_ready_truth(out):
        out["branch_ready"] = False
        out["eligible"] = False
        if not _batch9_text(out.get("failed_stage")):
            out["failed_stage"] = "not_ready"
        return out

    out["branch_ready"] = True
    out["eligible"] = True
    out["failed_stage"] = ""
    return out


def build_misc_branch_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    branch_id = kwargs.get("branch_id")
    if branch_id not in _BATCH9_ALLOWED_BRANCH_IDS:
        raise ValueError(f"invalid branch_id for {_BATCH9_FAMILY_ID}: {branch_id!r}")

    out = _BATCH9_ORIGINAL_BRANCH_BUILDER(*args, **kwargs)
    return _batch9_normalize_branch_surface(
        dict(out),
        branch_id=branch_id,
        runtime_mode_surface=kwargs.get("runtime_mode_surface"),
        provider_ready=bool(kwargs.get("provider_ready", True)),
    )


def _batch9_surface_ready(surface: Mapping[str, Any]) -> bool:
    return bool(
        _batch9_bool(surface.get("branch_ready"), False)
        and _batch9_bool(surface.get("present"), False)
        and _batch9_bool(surface.get("context_pass"), False)
        and _batch9_bool(surface.get("option_tradability_pass"), False)
        and not _batch9_text(surface.get("failed_stage"))
    )


def _batch9_score(surface: Mapping[str, Any]) -> float:
    try:
        return float(surface.get("setup_score") or 0.0)
    except Exception:
        return 0.0


def _batch9_ready_dominant_branch(call: Mapping[str, Any], put: Mapping[str, Any]) -> str:
    call_ready = _batch9_surface_ready(call)
    put_ready = _batch9_surface_ready(put)

    if call_ready and put_ready:
        call_score = _batch9_score(call)
        put_score = _batch9_score(put)
        if call_score > put_score:
            return N.BRANCH_CALL
        if put_score > call_score:
            return N.BRANCH_PUT
        return ""
    if call_ready:
        return N.BRANCH_CALL
    if put_ready:
        return N.BRANCH_PUT
    return ""


def _batch9_normalize_family_surface(
    surface: Mapping[str, Any],
    *,
    call_surface: Mapping[str, Any] | None,
    put_surface: Mapping[str, Any] | None,
    runtime_mode_surface: Mapping[str, Any] | None,
) -> dict[str, Any]:
    out = dict(surface)
    call = dict(_batch9_pick(out, "call") or call_surface or {})
    put = dict(_batch9_pick(out, "put") or put_surface or {})

    mode = _batch9_runtime_mode(runtime_mode_surface=runtime_mode_surface, surface=out)
    disabled = _batch9_runtime_disabled(mode)

    call_ready = _batch9_surface_ready(call)
    put_ready = _batch9_surface_ready(put)

    if disabled:
        call_ready = False
        put_ready = False
        out["batch9_freeze_blocked_reason"] = "runtime_disabled"

    if _BATCH9_FAMILY_ID == "MISO":
        chain_context_ready = bool(
            _batch9_bool(out.get("chain_context_ready"), False)
            or _batch9_bool(call.get("strike_bundle_present"), False)
            or _batch9_bool(put.get("strike_bundle_present"), False)
        )
        out["chain_context_ready"] = chain_context_ready
        if not chain_context_ready:
            call_ready = False
            put_ready = False
            out["batch9_freeze_blocked_reason"] = "miso_chain_context_not_ready"

    dominant_ready = _batch9_ready_dominant_branch(call, put) if (call_ready or put_ready) else ""

    out["family_id"] = _batch9_text(out.get("family_id"), _BATCH9_FAMILY_ID)
    out["call"] = call
    out["put"] = put
    out["branches"] = {N.BRANCH_CALL: call, N.BRANCH_PUT: put}
    out["call_ready"] = bool(call_ready)
    out["put_ready"] = bool(put_ready)
    out["eligible"] = bool(call_ready or put_ready)
    out["dominant_ready_branch"] = dominant_ready
    out["dominant_branch"] = dominant_ready if out["eligible"] else ""

    if _BATCH9_FAMILY_ID == "MISO" and not out["eligible"]:
        out["selected_side"] = None
        out["selected_strike"] = None

    return out


def build_misc_family_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH9_ORIGINAL_FAMILY_BUILDER(*args, **kwargs)
    return _batch9_normalize_family_surface(
        dict(out),
        call_surface=kwargs.get("call_surface"),
        put_surface=kwargs.get("put_surface"),
        runtime_mode_surface=kwargs.get("runtime_mode_surface"),
    )
