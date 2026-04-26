from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/miso_surface.py

Canonical MISO feature surface for ScalpX MME.

Purpose
-------
This module OWNS:
- doctrine-specific feature publication support for MISO only
- deterministic CALL / PUT MISO surface derivation from shared-core payloads
- monitored/tradable/shadow strike bundle publication from the strike-ladder seam
- gate-ready booleans for the MISO chain-qualified -> option-burst ->
  futures-aligned/futures-vetoed -> first-target monetization stack
- JSON-friendly branch and family support surfaces for services/features.py

This module DOES NOT own:
- strategy state machine mutation
- entry / exit decisions
- cooldown or re-entry mutation
- provider-routing policy
- Redis I/O

Frozen design law
-----------------
- MISO is option-led, futures-aligned, futures-vetoed.
- Dhan is mandatory for MISO market-data/context architecture.
- Chain data is selection-layer truth only, never sub-second burst trigger truth.
- Live trigger truth may use only selected option live feed, shadow-strike live
  support surfaces, and Nifty futures live feed.
- This module is feature-surface only, not a doctrine leaf or strategy engine.
- Returned surfaces must be deterministic and JSON-friendly plain mappings.
"""

from math import isfinite
from typing import Any, Final, Mapping, Sequence

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.feature_family import miso_microstructure as MISO_MICRO

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

EPSILON: Final[float] = 1e-8

DEFAULT_TARGET_POINTS: Final[float] = 5.0
DEFAULT_HARD_STOP_POINTS: Final[float] = 4.0
DEFAULT_DISASTER_STOP_POINTS: Final[float] = 5.0
DEFAULT_RATCHET_ARM_POINTS: Final[float] = 3.0
DEFAULT_BREAKEVEN_PLUS_POINTS: Final[float] = 0.5
DEFAULT_ENTRY_TIMEOUT_MS: Final[float] = 700.0
DEFAULT_AGGR_WINDOW_MS: Final[float] = 600.0
DEFAULT_TAPE_WINDOW_MS: Final[float] = 600.0
DEFAULT_PERSISTENCE_WINDOW_MS: Final[float] = 600.0
DEFAULT_MAX_HOLD_SEC: Final[float] = 60.0
DEFAULT_EARLY_STALL_SEC: Final[float] = 30.0

DEFAULT_OPTION_BURST_DELTA_MIN: Final[float] = 1.0
DEFAULT_OPTION_BURST_VEL_RATIO_MIN: Final[float] = 1.10
DEFAULT_OPTION_RESPONSE_EFF_MIN: Final[float] = 0.17
DEFAULT_MISO_DEPTH_MIN: Final[int] = 80
DEFAULT_MISO_SPREAD_RATIO_MAX: Final[float] = 1.60
DEFAULT_FUTURES_CONTRADICTION_SCORE_MAX: Final[float] = 1.25
DEFAULT_SHADOW_SUPPORT_MIN: Final[int] = 1
DEFAULT_NEAR_WALL_PENALTY: Final[float] = 0.15
DEFAULT_CONTEXT_SCORE_NEUTRAL: Final[float] = 0.50

__all__ = [
    "build_miso_branch_surface",
    "build_miso_family_surface",
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


def _futures_vwap_alignment_ok(vwap_distance: float, branch_id: str) -> bool:
    return vwap_distance >= 0.0 if branch_id == N.BRANCH_CALL else vwap_distance <= 0.0


def _futures_contradiction_score(
    *,
    futures_direction_score: float,
    futures_vwap_distance: float,
    futures_velocity_ratio: float,
    branch_id: str,
) -> float:
    directional_component = (
        max(-futures_direction_score, 0.0)
        if branch_id == N.BRANCH_CALL
        else max(futures_direction_score, 0.0)
    )
    vwap_component = (
        max(-futures_vwap_distance, 0.0)
        if branch_id == N.BRANCH_CALL
        else max(futures_vwap_distance, 0.0)
    )
    vel_component = max(1.0 - futures_velocity_ratio, 0.0)
    return directional_component + vwap_component + vel_component


def _context_pass(
    runtime_mode: str,
    *,
    futures_ok: bool,
    option_ok: bool,
    strike_bundle_present: bool,
    provider_ready: bool,
) -> bool:
    mode_up = _safe_str(runtime_mode).upper()
    allowed = {
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE_5DEPTH")).upper(),
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED", "DEPTH20_ENHANCED")).upper(),
        "BASE_5DEPTH",
        "DEPTH20_ENHANCED",
    }
    return mode_up in allowed and futures_ok and option_ok and strike_bundle_present and provider_ready


def _shadow_support_count(shadow_rows: Sequence[Mapping[str, Any]] | None) -> int:
    if not isinstance(shadow_rows, Sequence):
        return 0
    return sum(1 for item in shadow_rows if isinstance(item, Mapping))


def _selection_surface_selected(strike_surface: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(_pick(strike_surface, "selected"))


def _selection_surface_monitored(strike_surface: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    value = _pick(strike_surface, "monitored")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _selection_surface_tradable(strike_surface: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    value = _pick(strike_surface, "tradable")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _selection_surface_shadow(strike_surface: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    value = _pick(strike_surface, "shadow")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _context_features(option_surface: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return _as_mapping(_pick(_as_mapping(option_surface), "context_features"))


def _premium_health(option_surface: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return _as_mapping(_pick(_as_mapping(option_surface), "premium_health"))


def _shadow_features(option_surface: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return _as_mapping(
        _coalesce(
            _pick(_as_mapping(option_surface), "shadow_features"),
            _pick(_as_mapping(option_surface), "shadow_surface", "live"),
        )
    )


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
        score -= 0.08 if same_side_wall_strength < 0.60 else 0.15
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
        and _safe_bool(_pick(surface, "strike_bundle_present"), False)
        and _safe_bool(_pick(surface, "aggression_ok"), False)
        and _safe_bool(_pick(surface, "tape_urgency_ok"), False)
        and _safe_bool(_pick(surface, "persistence_ok"), False)
        and _safe_bool(_pick(surface, "live_flow_ok"), False)
        and _safe_bool(_pick(surface, "shadow_support_ok"), False)
        and _safe_bool(_pick(surface, "futures_alignment_ok"), False)
        and _safe_bool(_pick(surface, "futures_veto_clear"), False)
        and _safe_bool(_pick(surface, "context_pass"), False)
        and _safe_bool(_pick(surface, "option_tradability_pass"), False)
        and not _safe_str(_pick(surface, "failed_stage"))
    )


def build_miso_branch_surface(
    *,
    branch_id: str,
    futures_surface: Mapping[str, Any] | None,
    option_surface: Mapping[str, Any] | None,
    strike_surface: Mapping[str, Any] | None,
    tradability_surface: Mapping[str, Any] | None,
    regime_surface: Mapping[str, Any] | None = None,
    runtime_mode_surface: Mapping[str, Any] | None = None,
    thresholds: Mapping[str, Any] | None = None,
    provider_ready: bool = True,
) -> dict[str, Any]:
    """
    Build one MISO branch surface.

    Input contract:
    - futures_surface: shared Dhan futures-core selected_features or equivalent dict
    - option_surface: shared Dhan selected-option family surface or equivalent dict
    - strike_surface: MISO strike-selection surface with selected/monitored/tradable/shadow
    - tradability_surface: shared MISO tradability shell for this branch
    - regime_surface: shared regime surface
    - runtime_mode_surface: MISO runtime-mode surface
    """
    fut = _as_mapping(_pick(_as_mapping(futures_surface), "selected_features") or futures_surface)
    option_map = _as_mapping(option_surface)
    opt = _as_mapping(_pick(option_map, "selected_features") or option_map)
    opt_context = _context_features(option_map)
    opt_premium = _premium_health(option_map)
    opt_shadow = _shadow_features(option_map)

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
            getattr(N, "ENTRY_MODE_DIRECT", "DIRECT"),
        )
    )

    fut_present = _safe_bool(_pick(fut, "present"), False)
    opt_present = _safe_bool(_pick(opt, "present"), False)
    strike_present = _safe_bool(_pick(strike, "present"), False)
    trad_entry_pass = _safe_bool(_pick(trad, "entry_pass"), False)

    fut_ltp = _safe_float(_pick(fut, "ltp"), 0.0)
    fut_delta = _safe_float(_pick(fut, "delta_3"), 0.0)
    fut_velocity_ratio = _safe_float(_pick(fut, "velocity_ratio"), 0.0)
    fut_weighted_ofi = _safe_float(_pick(fut, "weighted_ofi"), 0.0)
    fut_weighted_ofi_persist = _safe_float(_pick(fut, "weighted_ofi_persist"), 0.0)
    fut_vwap_distance = _safe_float(_pick(fut, "vwap_distance"), 0.0)
    fut_volume_norm = _safe_float(_pick(fut, "volume_norm"), 0.0)
    fut_direction_score = _safe_float(_pick(fut, "direction_score", "trend_score"), 0.0)
    fut_event_rate_spike_ratio = _safe_float(_pick(fut, "event_rate_spike_ratio"), 0.0)

    opt_ltp = _safe_float(_pick(opt, "ltp"), 0.0)
    opt_delta = _safe_float(_pick(opt, "delta_3"), 0.0)
    opt_velocity_ratio = _safe_float(_pick(opt, "velocity_ratio"), 0.0)
    opt_weighted_ofi = _safe_float(_pick(opt, "weighted_ofi"), 0.0)
    opt_weighted_ofi_persist = _safe_float(_pick(opt, "weighted_ofi_persist"), 0.0)
    opt_response_eff = _safe_float(_pick(opt, "response_efficiency"), 0.0)
    opt_context_score = _derived_context_score(
        branch_id=branch_id,
        context_surface=opt_context,
    )
    opt_spread_ratio = _safe_float(_pick(opt, "spread_ratio"), 0.0)
    opt_touch_depth = _safe_int(_coalesce(_pick(opt, "touch_depth"), _pick(opt, "depth_total")), 0)
    opt_queue_reload_veto = _safe_bool(
        _coalesce(
            _pick(trad, "queue_reload_veto"),
            _pick(opt, "queue_reload_veto"),
            _pick(opt, "ask_reloaded"),
        ),
        False,
    )
    opt_near_wall = _safe_bool(_pick(opt_context, "same_side_wall_near"), False)
    opt_wall_strength = _safe_float(_pick(opt_context, "same_side_wall_strength_score"), 0.0)
    opt_oi_bias = _safe_str(_pick(opt_context, "oi_bias"), "UNKNOWN")

    selected_strike = _selection_surface_selected(strike)
    monitored_rows = _selection_surface_monitored(strike)
    tradable_rows = _selection_surface_tradable(strike)
    shadow_rows = _selection_surface_shadow(strike)

    selected_strike_value = _safe_float_or_none(_pick(selected_strike, "strike"))
    selected_strike_score = _safe_float(_pick(selected_strike, "selection_score", "strike_score"), 0.0)
    shadow_support = _shadow_support_count(shadow_rows)
    shadow_live_present = _safe_bool(_pick(opt_shadow, "present"), False)

    target_points = _threshold_float(thresholds, "TARGET_POINTS", DEFAULT_TARGET_POINTS)
    hard_stop_points = _threshold_float(thresholds, "HARD_STOP_POINTS", DEFAULT_HARD_STOP_POINTS)
    disaster_stop_points = _threshold_float(thresholds, "DISASTER_STOP_POINTS", DEFAULT_DISASTER_STOP_POINTS)
    ratchet_arm_points = _threshold_float(thresholds, "RATCHET_ARM_POINTS", DEFAULT_RATCHET_ARM_POINTS)
    breakeven_plus_points = _threshold_float(thresholds, "BREAKEVEN_PLUS_POINTS", DEFAULT_BREAKEVEN_PLUS_POINTS)
    entry_timeout_ms = _threshold_float(thresholds, "ENTRY_TIMEOUT_MS", DEFAULT_ENTRY_TIMEOUT_MS)
    aggr_window_ms = _threshold_float(thresholds, "AGGR_WINDOW_MS", DEFAULT_AGGR_WINDOW_MS)
    tape_window_ms = _threshold_float(thresholds, "TAPE_WINDOW_MS", DEFAULT_TAPE_WINDOW_MS)
    persistence_window_ms = _threshold_float(thresholds, "PERSISTENCE_WINDOW_MS", DEFAULT_PERSISTENCE_WINDOW_MS)
    max_hold_sec = _threshold_float(thresholds, "MAX_HOLD_SEC", DEFAULT_MAX_HOLD_SEC)
    early_stall_sec = _threshold_float(thresholds, "EARLY_STALL_SEC", DEFAULT_EARLY_STALL_SEC)

    option_burst_delta_min = _threshold_float(thresholds, "OPTION_BURST_DELTA_MIN", DEFAULT_OPTION_BURST_DELTA_MIN)
    option_burst_vel_ratio_min = _threshold_float(
        thresholds,
        "OPTION_BURST_VEL_RATIO_MIN",
        DEFAULT_OPTION_BURST_VEL_RATIO_MIN,
    )
    option_response_eff_min = _threshold_float(
        thresholds,
        "OPTION_RESPONSE_EFF_MIN",
        DEFAULT_OPTION_RESPONSE_EFF_MIN,
    )
    miso_depth_min = int(_threshold_float(thresholds, "OPT_TOUCH_DEPTH_MIN", DEFAULT_MISO_DEPTH_MIN))
    miso_spread_ratio_max = _threshold_float(
        thresholds,
        "OPT_ENTRY_SPREAD_RATIO_MAX",
        DEFAULT_MISO_SPREAD_RATIO_MAX,
    )
    futures_contradiction_score_max = _threshold_float(
        thresholds,
        "FUTURES_CONTRADICTION_SCORE_MAX",
        DEFAULT_FUTURES_CONTRADICTION_SCORE_MAX,
    )

    strike_bundle_present = strike_present and bool(selected_strike)

    burst_direction_ok = _directional_ok(opt_delta, branch_id)
    response_ok = opt_response_eff >= option_response_eff_min
    spread_ok = opt_spread_ratio <= miso_spread_ratio_max
    depth_ok = opt_touch_depth >= miso_depth_min

    futures_alignment_ok = _futures_vwap_alignment_ok(fut_vwap_distance, branch_id)
    micro = MISO_MICRO.build_miso_microstructure_surface(
        branch_id=branch_id,
        side=side,
        option_features=opt,
        shadow_features=opt_shadow,
        strike_surface=strike,
        selected_strike=selected_strike,
        shadow_rows=shadow_rows,
        thresholds=thresholds,
    )

    aggression_flow_ratio = _safe_float(_pick(micro, "aggressive_flow_ratio"), 0.0)
    speed_of_tape = _safe_float(_pick(micro, "speed_of_tape"), 0.0)
    imbalance_persist_score = _safe_float(_pick(micro, "imbalance_persist_score"), 0.0)
    queue_reload_score = _safe_float(_pick(micro, "queue_reload_score"), 0.0)

    opt_queue_reload_veto = _safe_bool(_pick(micro, "queue_reload_blocked"), False)
    aggression_ok = _safe_bool(_pick(micro, "aggression_ok"), False)
    tape_urgency_ok = _safe_bool(_pick(micro, "tape_speed_ok"), False)
    persistence_ok = _safe_bool(_pick(micro, "imbalance_persist_ok"), False)
    live_flow_ok = _safe_bool(_pick(micro, "live_flow_ok"), False)
    queue_ok = _safe_bool(_pick(micro, "queue_reload_clear"), False)
    shadow_support = _safe_int(_pick(micro, "shadow_support_count"), 0)
    shadow_support_ok = _safe_bool(_pick(micro, "shadow_support_ok"), False)
    burst_event_id = _safe_str(_pick(micro, "burst_event_id")) or None
    burst_event_id_valid = _safe_bool(_pick(micro, "burst_event_id_valid"), False)

    futures_contradiction_score = _futures_contradiction_score(
        futures_direction_score=fut_direction_score,
        futures_vwap_distance=fut_vwap_distance,
        futures_velocity_ratio=fut_velocity_ratio,
        branch_id=branch_id,
    )
    futures_veto_clear = futures_contradiction_score <= futures_contradiction_score_max

    option_tradability_pass = _safe_bool(
        _coalesce(
            _pick(trad, "entry_pass"),
            _pick(option_map, "selected_option_tradability_ok"),
            _pick(opt_premium, "tradability_ok"),
        ),
        False,
    )

    context_pass = _context_pass(
        runtime_mode=runtime_mode,
        futures_ok=fut_present,
        option_ok=opt_present,
        strike_bundle_present=strike_bundle_present,
        provider_ready=provider_ready,
    )

    trigger_ready = (
        opt_present
        and aggression_ok
        and tape_urgency_ok
        and persistence_ok
        and live_flow_ok
        and response_ok
        and spread_ok
        and depth_ok
        and queue_ok
        and shadow_support_ok
        and burst_event_id_valid
    )

    burst_valid = trigger_ready and option_tradability_pass
    entry_eligibility = burst_valid and futures_alignment_ok and futures_veto_clear and context_pass

    oi_bias_alignment = _oi_bias_alignment(branch_id, opt_oi_bias)
    near_wall_penalty = DEFAULT_NEAR_WALL_PENALTY if opt_near_wall and opt_wall_strength >= 0.60 else 0.0

    setup_score = (
        (abs(opt_delta) * 0.12)
        + (opt_velocity_ratio * 0.14)
        + (opt_response_eff * 1.80 * 0.18)
        + (opt_context_score * 0.10)
        + (selected_strike_score * 0.14)
        + (0.10 if persistence_ok else 0.0)
        + (0.10 if shadow_support_ok else 0.0)
        + (0.06 if futures_alignment_ok else 0.0)
        + (0.06 if futures_veto_clear else 0.0)
        - near_wall_penalty
    )

    surface_present = fut_present and opt_present and strike_present
    branch_ready = bool(
        surface_present
        and strike_bundle_present
        and aggression_ok
        and tape_urgency_ok
        and persistence_ok
        and live_flow_ok
        and shadow_support_ok
        and futures_alignment_ok
        and futures_veto_clear
        and context_pass
        and option_tradability_pass
    )

    return {
        "surface_kind": "miso_branch",
        "present": surface_present,
        "branch_ready": branch_ready,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MISO", "MISO")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MISO", "MISO")),
        "branch_id": branch_id,
        "burst_event_id": burst_event_id,
        "burst_event_id_valid": burst_event_id_valid,
        "side": side,
        "regime": regime_label,
        "runtime_mode": runtime_mode,
        "entry_mode_hint": entry_mode_hint,
        "provider_ready": provider_ready,
        "futures_features": fut,
        "primary_features": opt,
        "context_features": opt_context,
        "premium_health": opt_premium,
        "shadow_features": opt_shadow,
        "microstructure": micro,
        "strike_surface": strike,
        "tradability": trad,
        "regime_surface": regime,
        "runtime_mode_surface": mode,
        "strike_bundle_present": strike_bundle_present,
        "selected_strike": selected_strike,
        "selected_strike_value": selected_strike_value,
        "selected_strike_score": selected_strike_score,
        "monitored": monitored_rows,
        "tradable": tradable_rows,
        "shadow": shadow_rows,
        "shadow_support_count": shadow_support,
        "aggressive_flow_ratio": aggression_flow_ratio,
        "speed_of_tape": speed_of_tape,
        "imbalance_persist_score": imbalance_persist_score,
        "queue_reload_score": queue_reload_score,
        "aggression_ok": aggression_ok,
        "tape_speed_ok": tape_urgency_ok,
        "tape_urgency_ok": tape_urgency_ok,
        "imbalance_persist_ok": persistence_ok,
        "persistence_ok": persistence_ok,
        "live_flow_ok": live_flow_ok,
        "response_ok": response_ok,
        "spread_ok": spread_ok,
        "depth_ok": depth_ok,
        "queue_reload_blocked": opt_queue_reload_veto,
        "queue_reload_clear": queue_ok,
        "queue_ok": queue_ok,
        "shadow_support_ok": shadow_support_ok,
        "burst_detected": burst_valid,
        "burst_valid": burst_valid,
        "futures_vwap_align_ok": futures_alignment_ok,
        "futures_alignment_ok": futures_alignment_ok,
        "futures_contradiction_score": futures_contradiction_score,
        "futures_contradiction_blocked": not futures_veto_clear,
        "futures_veto_clear": futures_veto_clear,
        "context_pass": context_pass,
        "option_tradability_pass": option_tradability_pass,
        "entry_eligibility": entry_eligibility,
        "oi_bias_alignment": oi_bias_alignment,
        "near_same_side_wall": opt_near_wall,
        "same_side_wall_strength_score": opt_wall_strength,
        "setup_score": setup_score,
        "risk_shell": {
            "target_points": target_points,
            "hard_stop_points": hard_stop_points,
            "disaster_stop_points": disaster_stop_points,
            "ratchet_arm_points": ratchet_arm_points,
            "breakeven_plus_points": breakeven_plus_points,
            "entry_timeout_ms": entry_timeout_ms,
            "aggr_window_ms": aggr_window_ms,
            "tape_window_ms": tape_window_ms,
            "persistence_window_ms": persistence_window_ms,
            "max_hold_sec": max_hold_sec,
            "early_stall_sec": early_stall_sec,
        },
        "feature_refs": {
            "fut_ltp": fut_ltp,
            "fut_delta": fut_delta,
            "fut_velocity_ratio": fut_velocity_ratio,
            "fut_weighted_ofi": fut_weighted_ofi,
            "fut_weighted_ofi_persist": fut_weighted_ofi_persist,
            "fut_vwap_distance": fut_vwap_distance,
            "fut_volume_norm": fut_volume_norm,
            "fut_direction_score": fut_direction_score,
            "fut_event_rate_spike_ratio": fut_event_rate_spike_ratio,
            "opt_ltp": opt_ltp,
            "opt_delta": opt_delta,
            "opt_velocity_ratio": opt_velocity_ratio,
            "opt_weighted_ofi": opt_weighted_ofi,
            "opt_weighted_ofi_persist": opt_weighted_ofi_persist,
            "opt_response_efficiency": opt_response_eff,
            "opt_context_score": opt_context_score,
            "opt_spread_ratio": opt_spread_ratio,
            "opt_touch_depth": opt_touch_depth,
            "opt_oi_bias": opt_oi_bias,
            "aggressive_flow_ratio": aggression_flow_ratio,
            "speed_of_tape": speed_of_tape,
            "imbalance_persist_score": imbalance_persist_score,
            "queue_reload_score": queue_reload_score,
            "burst_event_id": burst_event_id,
        },
        "passed_stages": tuple(
            stage
            for stage, passed in (
                ("strike_bundle_present", strike_bundle_present),
                ("aggression_inference", aggression_ok),
                ("tape_urgency", tape_urgency_ok),
                ("imbalance_persistence", persistence_ok),
                ("live_flow_confirmation", live_flow_ok),
                ("shadow_strike_support", shadow_support_ok),
                ("futures_vwap_alignment", futures_alignment_ok),
                ("futures_contradiction_veto_clear", futures_veto_clear),
                ("context_pass", context_pass),
                ("option_tradability", option_tradability_pass),
            )
            if passed
        ),
        "failed_stage": (
            ""
            if branch_ready
            else "strike_bundle_present"
            if not strike_bundle_present
            else "aggression_inference"
            if not aggression_ok
            else "tape_urgency"
            if not tape_urgency_ok
            else "imbalance_persistence"
            if not persistence_ok
            else "live_flow_confirmation"
            if not live_flow_ok
            else "shadow_strike_support"
            if not shadow_support_ok
            else "futures_vwap_alignment"
            if not futures_alignment_ok
            else "futures_contradiction_veto_clear"
            if not futures_veto_clear
            else "context_pass"
            if not context_pass
            else "option_tradability"
        ),
    }


def build_miso_family_surface(
    *,
    call_surface: Mapping[str, Any] | None,
    put_surface: Mapping[str, Any] | None,
    runtime_mode_surface: Mapping[str, Any] | None = None,
    regime_surface: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the family-level MISO surface bundle consumed by features.py.

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
        "surface_kind": "miso_family",
        "present": call_present or put_present,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MISO", "MISO")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MISO", "MISO")),
        "runtime_mode": _safe_str(_pick(mode, "runtime_mode"), ""),
        "regime": _safe_str(_pick(regime, "regime"), REGIME_NORMAL),
        "call": call,
        "put": put,
        "call_present": call_present,
        "put_present": put_present,
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
_BATCH9_FAMILY_LC = "miso"
_BATCH9_FAMILY_ID = "MISO"
_BATCH9_ALLOWED_BRANCH_IDS = (N.BRANCH_CALL, N.BRANCH_PUT)

_BATCH9_ORIGINAL_BRANCH_BUILDER = build_miso_branch_surface
_BATCH9_ORIGINAL_FAMILY_BUILDER = build_miso_family_surface


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


def build_miso_branch_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
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


def build_miso_family_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH9_ORIGINAL_FAMILY_BUILDER(*args, **kwargs)
    return _batch9_normalize_family_surface(
        dict(out),
        call_surface=kwargs.get("call_surface"),
        put_surface=kwargs.get("put_surface"),
        runtime_mode_surface=kwargs.get("runtime_mode_surface"),
    )

# ============================================================================
# Batch 26I-R1 — MISO canonical tradability producer overlay
# ============================================================================
#
# Adds direct canonical tradability_pass and clear-side compatibility fields.
# Blocked booleans remain blocker semantics; clear fields are inversions.

_BATCH26IR1_ORIGINAL_BUILD_MISO_BRANCH_SURFACE = build_miso_branch_surface


def _batch26ir1_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "yes", "y", "ok", "pass", "passed", "ready"}:
            return True
        if text in {"0", "false", "no", "n", "fail", "failed", "blocked", "missing", "stale", "unavailable", ""}:
            return False
    return bool(value)


def _batch26ir1_first(mapping: dict[str, object], *keys: str, default: object = None) -> object:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return default


def build_miso_branch_surface(*args, **kwargs):
    out = dict(_BATCH26IR1_ORIGINAL_BUILD_MISO_BRANCH_SURFACE(*args, **kwargs))

    queue_reload_blocked = _batch26ir1_bool(
        _batch26ir1_first(out, "queue_reload_blocked", "queue_reload_veto")
    )
    futures_contradiction_blocked = _batch26ir1_bool(
        _batch26ir1_first(out, "futures_contradiction_blocked", "futures_veto_blocked")
    )

    out.update(
        {
            "tradability_pass": _batch26ir1_bool(
                _batch26ir1_first(out, "tradability_pass", "option_tradability_pass", "selected_option_tradability_ok")
            ),
            "queue_reload_blocked": queue_reload_blocked,
            "queue_clear": not queue_reload_blocked,
            "queue_reload_clear": not queue_reload_blocked,
            "futures_contradiction_blocked": futures_contradiction_blocked,
            "futures_clear": not futures_contradiction_blocked,
        }
    )

    return out
