from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/misr_surface.py

Canonical MISR feature surface for ScalpX MME.

Purpose
-------
This module OWNS:
- doctrine-specific feature publication support for MISR only
- deterministic CALL / PUT MISR surface derivation from shared-core payloads
- trap-zone registry normalization and nearest-zone branch selection
- gate-ready booleans for the MISR fake-break -> absorption -> range re-entry ->
  hold-proof -> no-man's-land -> reversal-impulse stack
- deterministic trap_event_id derivation support surface
- JSON-friendly branch and family support surfaces for services/features.py

This module DOES NOT own:
- strategy state machine mutation
- entry / exit decisions
- cooldown or re-entry mutation
- provider-routing policy
- Redis I/O

Frozen design law
-----------------
- MISR remains futures-led and option-confirmed.
- Features lane owns trap-zone registry construction, ORB/swing zone computation,
  zone validity, zone expiry, zone pruning, and nearest-zone selection surface.
- Strategy lane later owns trap-event detection, fake-break qualification,
  absorption validation, range re-entry confirmation, hold-proof, no-man's-land
  displacement, reversal-impulse confirmation, and event consumption.
- This module is therefore a feature-surface publisher, not a doctrine leaf.
- Returned surfaces must be deterministic and JSON-friendly plain mappings.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final, Iterable, Mapping, Sequence

from app.mme_scalpx.core import names as N

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

ZONE_ORB_HIGH: Final[str] = "ORB_HIGH"
ZONE_ORB_LOW: Final[str] = "ORB_LOW"
ZONE_SWING_HIGH: Final[str] = "SWING_HIGH"
ZONE_SWING_LOW: Final[str] = "SWING_LOW"

EPSILON: Final[float] = 1e-8

DEFAULT_ZONE_MAX_COUNT: Final[int] = 4
DEFAULT_FAKE_BREAK_MIN_POINTS: Final[float] = 0.20
DEFAULT_ABSORPTION_WINDOW_SEC: Final[float] = 2.0
DEFAULT_ABSORPTION_OFI_CALL_MIN: Final[float] = 0.53
DEFAULT_ABSORPTION_OFI_PUT_MAX: Final[float] = 0.47
DEFAULT_RANGE_REENTRY_BUFFER_POINTS: Final[float] = 0.05
DEFAULT_HOLD_PROOF_SEC: Final[float] = 0.80
DEFAULT_NO_MANS_LAND_POINTS: Final[float] = 0.15
DEFAULT_REVERSAL_VEL_RATIO_MIN: Final[float] = 1.05
DEFAULT_REVERSAL_RESPONSE_EFF_MIN: Final[float] = 0.15
DEFAULT_FLOW_FLIP_CALL_MIN: Final[float] = 0.54
DEFAULT_FLOW_FLIP_PUT_MAX: Final[float] = 0.46
DEFAULT_ZONE_QUALITY_MIN: Final[float] = 0.10
DEFAULT_NEAR_WALL_PENALTY: Final[float] = 0.20

__all__ = [
    "TrapZone",
    "build_misr_branch_surface",
    "build_misr_family_surface",
    "build_misr_zone_registry_surface",
]


@dataclass(frozen=True, slots=True)
class TrapZone:
    zone_id: str
    zone_type: str
    side_bias: str
    trap_zone_level: float
    zone_low: float
    zone_high: float
    zone_width_ticks: float
    source_window_start_ts: int
    source_window_end_ts: int
    quality_score: float
    valid_from_ts: int
    expires_ts: int
    broken_flag: bool
    sweep_count: int
    last_test_ts: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "zone_type": self.zone_type,
            "side_bias": self.side_bias,
            "trap_zone_level": self.trap_zone_level,
            "zone_low": self.zone_low,
            "zone_high": self.zone_high,
            "zone_width_ticks": self.zone_width_ticks,
            "source_window_start_ts": self.source_window_start_ts,
            "source_window_end_ts": self.source_window_end_ts,
            "quality_score": self.quality_score,
            "valid_from_ts": self.valid_from_ts,
            "expires_ts": self.expires_ts,
            "broken_flag": self.broken_flag,
            "sweep_count": self.sweep_count,
            "last_test_ts": self.last_test_ts,
        }


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


def _branch_zone_side(branch_id: str) -> str:
    # CALL looks for downside trap candidate; PUT looks for upside trap candidate.
    return "DOWNSIDE_TRAP" if branch_id == N.BRANCH_CALL else "UPSIDE_TRAP"


def _directional_ok(value: float, branch_id: str) -> bool:
    return value >= 0.0 if branch_id == N.BRANCH_CALL else value <= 0.0


def _ofi_ok(value: float, branch_id: str, call_min: float, put_max: float) -> bool:
    return value >= call_min if branch_id == N.BRANCH_CALL else value <= put_max


def _context_pass(runtime_mode: str, provider_ready: bool) -> bool:
    degraded = {
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED", "DHAN_DEGRADED")).upper(),
        "DHAN_DEGRADED",
    }
    return _safe_str(runtime_mode).upper() in degraded or provider_ready


def _zone_side_bias(zone_type: str) -> str:
    if zone_type in {ZONE_ORB_LOW, ZONE_SWING_LOW}:
        return "DOWNSIDE_TRAP"
    if zone_type in {ZONE_ORB_HIGH, ZONE_SWING_HIGH}:
        return "UPSIDE_TRAP"
    return ""


def _derive_trap_zone_level(
    *,
    zone_type: str,
    zone_low: float,
    zone_high: float,
    zone_level: float | None,
) -> float:
    if zone_type == ZONE_ORB_LOW:
        return zone_low
    if zone_type == ZONE_ORB_HIGH:
        return zone_high
    if zone_type in {ZONE_SWING_LOW, ZONE_SWING_HIGH} and zone_level is not None:
        return zone_level
    return zone_low if zone_type == ZONE_SWING_LOW else zone_high


def _normalize_zone_rows(zone_registry: Any) -> tuple[TrapZone, ...]:
    rows: list[TrapZone] = []
    if isinstance(zone_registry, Mapping):
        maybe_rows = _pick(zone_registry, "zones", "rows", "active_zones", "registry")
        if isinstance(maybe_rows, Sequence) and not isinstance(maybe_rows, (str, bytes)):
            zone_rows = maybe_rows
        else:
            zone_rows = ()
    elif isinstance(zone_registry, Sequence) and not isinstance(zone_registry, (str, bytes)):
        zone_rows = zone_registry
    else:
        zone_rows = ()

    for raw in zone_rows:
        row = _as_mapping(raw)
        zone_type = _safe_str(_pick(row, "zone_type")).upper()
        if zone_type not in {ZONE_ORB_HIGH, ZONE_ORB_LOW, ZONE_SWING_HIGH, ZONE_SWING_LOW}:
            continue

        zone_id = _safe_str(_pick(row, "zone_id"))
        if not zone_id:
            continue

        zone_low = _safe_float(_pick(row, "zone_low"), 0.0)
        zone_high = _safe_float(_pick(row, "zone_high"), 0.0)
        if zone_high < zone_low:
            zone_low, zone_high = zone_high, zone_low

        zone = TrapZone(
            zone_id=zone_id,
            zone_type=zone_type,
            side_bias=_safe_str(_pick(row, "side_bias"), _zone_side_bias(zone_type)),
            trap_zone_level=_derive_trap_zone_level(
                zone_type=zone_type,
                zone_low=zone_low,
                zone_high=zone_high,
                zone_level=_safe_float_or_none(_pick(row, "zone_level", "trap_zone_level")),
            ),
            zone_low=zone_low,
            zone_high=zone_high,
            zone_width_ticks=max(_safe_float(_pick(row, "zone_width_ticks"), zone_high - zone_low), 0.0),
            source_window_start_ts=_safe_int(_pick(row, "source_window_start_ts")),
            source_window_end_ts=_safe_int(_pick(row, "source_window_end_ts")),
            quality_score=_safe_float(_pick(row, "quality_score"), 0.0),
            valid_from_ts=_safe_int(_pick(row, "valid_from_ts")),
            expires_ts=_safe_int(_pick(row, "expires_ts")),
            broken_flag=_safe_bool(_pick(row, "broken_flag"), False),
            sweep_count=_safe_int(_pick(row, "sweep_count"), 0),
            last_test_ts=_safe_int(_pick(row, "last_test_ts")),
        )
        rows.append(zone)

    # pruning law: at most latest ORB_HIGH, latest ORB_LOW, nearest valid SWING_HIGH, nearest valid SWING_LOW
    grouped: dict[str, list[TrapZone]] = {
        ZONE_ORB_HIGH: [],
        ZONE_ORB_LOW: [],
        ZONE_SWING_HIGH: [],
        ZONE_SWING_LOW: [],
    }
    for zone in rows:
        grouped[zone.zone_type].append(zone)

    pruned: list[TrapZone] = []
    for zone_type, items in grouped.items():
        if not items:
            continue
        items.sort(key=lambda z: (z.valid_from_ts, z.source_window_end_ts, z.quality_score))
        pruned.append(items[-1])

    pruned.sort(key=lambda z: (z.zone_type, z.valid_from_ts, z.zone_id))
    return tuple(pruned[:DEFAULT_ZONE_MAX_COUNT])


def _active_zone_for_branch(
    *,
    zones: Sequence[TrapZone],
    branch_id: str,
    fut_ltp: float,
    now_ts_ms: int,
    quality_min: float,
) -> TrapZone | None:
    desired_side = _branch_zone_side(branch_id)
    eligible: list[TrapZone] = []
    for zone in zones:
        if zone.side_bias != desired_side:
            continue
        if zone.broken_flag:
            continue
        if zone.quality_score < quality_min:
            continue
        if zone.valid_from_ts > 0 and now_ts_ms < zone.valid_from_ts:
            continue
        if zone.expires_ts > 0 and now_ts_ms > zone.expires_ts:
            continue
        eligible.append(zone)

    if not eligible:
        return None

    eligible.sort(
        key=lambda z: (
            abs(fut_ltp - z.trap_zone_level),
            -z.quality_score,
            -z.valid_from_ts,
            z.zone_id,
        )
    )
    return eligible[0]


def build_misr_zone_registry_surface(
    *,
    zone_registry: Any,
    futures_surface: Mapping[str, Any] | None = None,
    now_ts_ms: int | None = None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    fut = _as_mapping(_pick(_as_mapping(futures_surface), "selected_features") or futures_surface)
    fut_ltp = _safe_float(_pick(fut, "ltp"), 0.0)
    ts_now = int(now_ts_ms or _safe_int(_pick(fut, "ts_event_ns"), 0) // 1_000_000)
    quality_min = _threshold_float(thresholds, "ZONE_QUALITY_MIN", DEFAULT_ZONE_QUALITY_MIN)

    zones = _normalize_zone_rows(zone_registry)
    active_call = _active_zone_for_branch(
        zones=zones,
        branch_id=N.BRANCH_CALL,
        fut_ltp=fut_ltp,
        now_ts_ms=ts_now,
        quality_min=quality_min,
    )
    active_put = _active_zone_for_branch(
        zones=zones,
        branch_id=N.BRANCH_PUT,
        fut_ltp=fut_ltp,
        now_ts_ms=ts_now,
        quality_min=quality_min,
    )

    return {
        "present": bool(zones),
        "zones": tuple(zone.to_dict() for zone in zones),
        "zone_count": len(zones),
        "active_call_zone": None if active_call is None else active_call.to_dict(),
        "active_put_zone": None if active_put is None else active_put.to_dict(),
    }


def _build_trap_event_id(
    *,
    branch_id: str,
    active_zone_id: str,
    fake_break_start_ts_ms: int,
    fake_break_extreme_ts_ms: int,
) -> str | None:
    branch_side = "CALL" if branch_id == N.BRANCH_CALL else "PUT"
    if not active_zone_id or fake_break_start_ts_ms <= 0 or fake_break_extreme_ts_ms <= 0:
        return None
    return f"{branch_side}|{active_zone_id}|{fake_break_start_ts_ms}|{fake_break_extreme_ts_ms}"


def build_misr_branch_surface(
    *,
    branch_id: str,
    futures_surface: Mapping[str, Any] | None,
    option_surface: Mapping[str, Any] | None,
    fallback_option_surface: Mapping[str, Any] | None = None,
    strike_surface: Mapping[str, Any] | None = None,
    tradability_surface: Mapping[str, Any] | None = None,
    regime_surface: Mapping[str, Any] | None = None,
    runtime_mode_surface: Mapping[str, Any] | None = None,
    zone_registry_surface: Mapping[str, Any] | None = None,
    thresholds: Mapping[str, Any] | None = None,
    provider_ready: bool = True,
    now_ts_ms: int | None = None,
    fake_break_start_ts_ms: int | None = None,
    fake_break_extreme_ts_ms: int | None = None,
) -> dict[str, Any]:
    """
    Build one MISR branch surface.

    This is a feature support surface only. It publishes the ordered trap-reversal
    facts strategy.py will later consume.
    """
    fut = _as_mapping(_pick(_as_mapping(futures_surface), "selected_features") or futures_surface)
    opt = _as_mapping(_pick(_as_mapping(option_surface), "selected_features") or option_surface)
    fallback = _as_mapping(_pick(_as_mapping(fallback_option_surface), "selected_features") or fallback_option_surface)
    strike = _as_mapping(strike_surface)
    trad = _as_mapping(tradability_surface)
    regime = _as_mapping(regime_surface)
    mode = _as_mapping(runtime_mode_surface)
    zones = _as_mapping(zone_registry_surface)

    side = _branch_side(branch_id)
    bullish = branch_id == N.BRANCH_CALL

    regime_label = _safe_str(_pick(regime, "regime"), REGIME_NORMAL)
    runtime_mode = _safe_str(_pick(mode, "runtime_mode"), "")
    entry_mode_hint = _safe_str(
        _coalesce(
            _pick(opt, "entry_mode_hint"),
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
    fut_direction_score = _safe_float(_pick(fut, "direction_score"), 0.0)
    fut_ema9_slope = _safe_float(_pick(fut, "ema9_slope"), 0.0)
    fut_cvd_delta = _safe_float(_pick(fut, "cvd_delta"), 0.0)
    fut_spread_ratio = _safe_float(_pick(fut, "spread_ratio"), 0.0)
    fut_book_pressure = _safe_float(_pick(fut, "book_pressure"), 0.5)

    opt_delta = _safe_float(_pick(opt, "delta_3"), 0.0)
    opt_velocity_ratio = _safe_float(_pick(opt, "velocity_ratio"), 0.0)
    opt_weighted_ofi = _safe_float(_pick(opt, "weighted_ofi"), 0.0)
    opt_response_eff = _safe_float(_pick(opt, "response_efficiency"), 0.0)
    opt_context_score = _safe_float(_pick(opt, "context_score"), 0.0)
    opt_near_wall = _safe_bool(_pick(opt, "near_same_side_wall"), False)
    opt_wall_strength = _safe_float(_pick(opt, "same_side_wall_strength_score"), 0.0)
    opt_oi_bias = _safe_str(_pick(opt, "oi_bias"), "UNKNOWN")
    opt_spread_ratio = _safe_float(_pick(opt, "spread_ratio"), 0.0)

    fallback_spread_ratio = _safe_float(_pick(fallback, "spread_ratio"), 999.0)
    fallback_ready = fallback_present and fallback_spread_ratio <= _threshold_float(
        thresholds,
        "FALLBACK_SPREAD_RATIO_MAX",
        1.80,
    )

    active_zone_map = _as_mapping(
        _pick(zones, "active_call_zone") if branch_id == N.BRANCH_CALL else _pick(zones, "active_put_zone")
    )
    active_zone_id = _safe_str(_pick(active_zone_map, "zone_id"))
    trap_zone_level = _safe_float(_pick(active_zone_map, "trap_zone_level"), 0.0)
    zone_low = _safe_float(_pick(active_zone_map, "zone_low"), trap_zone_level)
    zone_high = _safe_float(_pick(active_zone_map, "zone_high"), trap_zone_level)
    zone_quality = _safe_float(_pick(active_zone_map, "quality_score"), 0.0)
    zone_present = bool(active_zone_map)
    zone_quality_min = _threshold_float(thresholds, "ZONE_QUALITY_MIN", DEFAULT_ZONE_QUALITY_MIN)
    active_zone_valid = zone_present and zone_quality >= zone_quality_min

    fake_break_min_points = _threshold_float(thresholds, "FAKE_BREAK_MIN_POINTS", DEFAULT_FAKE_BREAK_MIN_POINTS)
    absorption_window_sec = _threshold_float(thresholds, "ABSORPTION_WINDOW_SEC", DEFAULT_ABSORPTION_WINDOW_SEC)
    absorption_call_ofi_min = _threshold_float(thresholds, "ABSORPTION_OFI_CALL_MIN", DEFAULT_ABSORPTION_OFI_CALL_MIN)
    absorption_put_ofi_max = _threshold_float(thresholds, "ABSORPTION_OFI_MAX_BEAR", DEFAULT_ABSORPTION_OFI_PUT_MAX)
    range_reentry_buffer_points = _threshold_float(
        thresholds,
        "RANGE_REENTRY_BUFFER_POINTS",
        DEFAULT_RANGE_REENTRY_BUFFER_POINTS,
    )
    hold_proof_sec = _threshold_float(thresholds, "HOLD_PROOF_SEC", DEFAULT_HOLD_PROOF_SEC)
    no_mans_land_points = _threshold_float(thresholds, "NO_MANS_LAND_POINTS", DEFAULT_NO_MANS_LAND_POINTS)
    reversal_vel_ratio_min = _threshold_float(thresholds, "REVERSAL_VEL_RATIO_MIN", DEFAULT_REVERSAL_VEL_RATIO_MIN)
    reversal_response_eff_min = _threshold_float(
        thresholds,
        "REVERSAL_RESPONSE_EFF_MIN",
        DEFAULT_REVERSAL_RESPONSE_EFF_MIN,
    )
    flow_flip_call_min = _threshold_float(thresholds, "FLOW_FLIP_CALL_MIN", DEFAULT_FLOW_FLIP_CALL_MIN)
    flow_flip_put_max = _threshold_float(thresholds, "FLOW_FLIP_MAX_BEAR", DEFAULT_FLOW_FLIP_PUT_MAX)

    ts_now_ms = int(now_ts_ms or (_safe_int(_pick(fut, "ts_event_ns"), 0) // 1_000_000))
    fb_start_ms = int(fake_break_start_ts_ms or ts_now_ms)
    fb_extreme_ms = int(fake_break_extreme_ts_ms or ts_now_ms)

    if bullish:
        fake_break_distance = max(trap_zone_level - fut_ltp, 0.0)
        inside_range = fut_ltp >= (zone_low + range_reentry_buffer_points) if zone_present else False
        no_mans_land_cleared = fut_ltp >= (zone_high + no_mans_land_points) if zone_present else False
    else:
        fake_break_distance = max(fut_ltp - trap_zone_level, 0.0)
        inside_range = fut_ltp <= (zone_high - range_reentry_buffer_points) if zone_present else False
        no_mans_land_cleared = fut_ltp <= (zone_low - no_mans_land_points) if zone_present else False

    fake_break = (
        active_zone_valid
        and fake_break_distance >= fake_break_min_points
        and (_directional_ok(-fut_delta, branch_id))
    )

    absorption = (
        fake_break
        and _ofi_ok(fut_weighted_ofi, branch_id, absorption_call_ofi_min, absorption_put_ofi_max)
        and _ofi_ok(fut_weighted_ofi_persist, branch_id, absorption_call_ofi_min, absorption_put_ofi_max)
        and fut_volume_norm > 0.0
    )

    range_reentry = absorption and inside_range
    flow_flip = _ofi_ok(opt_weighted_ofi, branch_id, flow_flip_call_min, flow_flip_put_max) and _directional_ok(opt_delta, branch_id)
    hold_proof = range_reentry and abs(fut_vwap_distance) <= max(abs(zone_high - zone_low), hold_proof_sec) and _directional_ok(fut_ema9_slope, branch_id)
    reversal_impulse = (
        hold_proof
        and no_mans_land_cleared
        and flow_flip
        and opt_velocity_ratio >= reversal_vel_ratio_min
        and opt_response_eff >= reversal_response_eff_min
        and _directional_ok(fut_cvd_delta, branch_id)
    )

    trap_event_id = _build_trap_event_id(
        branch_id=branch_id,
        active_zone_id=active_zone_id,
        fake_break_start_ts_ms=fb_start_ms,
        fake_break_extreme_ts_ms=fb_extreme_ms,
    )

    context_pass = _context_pass(runtime_mode, provider_ready)
    option_tradability_pass = _safe_bool(_pick(trad, "entry_pass"), False)

    near_wall_penalty = DEFAULT_NEAR_WALL_PENALTY if opt_near_wall and opt_wall_strength >= 0.60 else 0.0
    oi_bias_alignment = (
        opt_oi_bias == ("CALL_SUPPORTIVE" if bullish else "PUT_SUPPORTIVE")
        or opt_oi_bias in {"NEUTRAL", "UNKNOWN"}
    )

    setup_score = (
        (zone_quality * 0.20)
        + (opt_context_score * 0.10)
        + (fut_velocity_ratio * 0.10)
        + (opt_response_eff * 1.50 * 0.15)
        + (0.15 if fake_break else 0.0)
        + (0.10 if absorption else 0.0)
        + (0.10 if range_reentry else 0.0)
        + (0.10 if hold_proof else 0.0)
        + (0.15 if reversal_impulse else 0.0)
        - near_wall_penalty
    )

    surface_present = fut_present and opt_present and zone_present

    return {
        "surface_kind": "misr",
        "present": surface_present,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MISR", "MISR")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MISR", "MISR")),
        "branch_id": branch_id,
        "side": side,
        "regime": regime_label,
        "runtime_mode": runtime_mode,
        "entry_mode_hint": entry_mode_hint,
        "provider_ready": provider_ready,
        "futures_features": fut,
        "primary_features": opt,
        "fallback_features": fallback,
        "strike_surface": strike,
        "tradability": trad,
        "regime_surface": regime,
        "runtime_mode_surface": mode,
        "active_zone": active_zone_map,
        "active_zone_valid": active_zone_valid,
        "trap_zone_level": trap_zone_level,
        "fake_break_distance": fake_break_distance,
        "fake_break": fake_break,
        "absorption": absorption,
        "range_reentry": range_reentry,
        "flow_flip": flow_flip,
        "hold_proof": hold_proof,
        "no_mans_land_cleared": no_mans_land_cleared,
        "reversal_impulse": reversal_impulse,
        "trap_event_id": trap_event_id,
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
            "fut_book_pressure": fut_book_pressure,
            "opt_delta": opt_delta,
            "opt_velocity_ratio": opt_velocity_ratio,
            "opt_weighted_ofi": opt_weighted_ofi,
            "opt_response_efficiency": opt_response_eff,
            "opt_context_score": opt_context_score,
            "opt_spread_ratio": opt_spread_ratio,
            "opt_oi_bias": opt_oi_bias,
            "zone_quality": zone_quality,
            "absorption_window_sec": absorption_window_sec,
        },
        "passed_stages": tuple(
            stage
            for stage, passed in (
                ("active_trap_zone_selection", active_zone_valid),
                ("fake_break_trigger", fake_break),
                ("absorption_signature_pass", absorption),
                ("range_reentry_confirmation", range_reentry),
                ("flow_flip_confirmation", flow_flip),
                ("hold_inside_range_proof", hold_proof),
                ("no_mans_land_displacement", no_mans_land_cleared),
                ("reversal_impulse_confirmation", reversal_impulse),
                ("context_pass", context_pass),
                ("option_tradability", option_tradability_pass),
            )
            if passed
        ),
        "failed_stage": (
            ""
            if (
                active_zone_valid
                and fake_break
                and absorption
                and range_reentry
                and flow_flip
                and hold_proof
                and no_mans_land_cleared
                and reversal_impulse
                and context_pass
                and option_tradability_pass
            )
            else "active_trap_zone_selection"
            if not active_zone_valid
            else "fake_break_trigger"
            if not fake_break
            else "absorption_signature_pass"
            if not absorption
            else "range_reentry_confirmation"
            if not range_reentry
            else "flow_flip_confirmation"
            if not flow_flip
            else "hold_inside_range_proof"
            if not hold_proof
            else "no_mans_land_displacement"
            if not no_mans_land_cleared
            else "reversal_impulse_confirmation"
            if not reversal_impulse
            else "context_pass"
            if not context_pass
            else "option_tradability"
        ),
    }


def build_misr_family_surface(
    *,
    call_surface: Mapping[str, Any] | None,
    put_surface: Mapping[str, Any] | None,
    zone_registry_surface: Mapping[str, Any] | None = None,
    runtime_mode_surface: Mapping[str, Any] | None = None,
    regime_surface: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the family-level MISR surface bundle consumed by features.py.

    This remains a payload support surface, not a candidate selector.
    """
    call = _as_mapping(call_surface)
    put = _as_mapping(put_surface)
    zones = _as_mapping(zone_registry_surface)
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

    return {
        "surface_kind": "misr_family",
        "present": call_present or put_present,
        "family_id": _safe_str(getattr(N, "STRATEGY_FAMILY_MISR", "MISR")),
        "doctrine_id": _safe_str(getattr(N, "DOCTRINE_MISR", "MISR")),
        "runtime_mode": _safe_str(_pick(mode, "runtime_mode"), ""),
        "regime": _safe_str(_pick(regime, "regime"), REGIME_NORMAL),
        "zone_registry": zones,
        "call": call,
        "put": put,
        "call_present": call_present,
        "put_present": put_present,
        "call_setup_score": call_setup_score,
        "put_setup_score": put_setup_score,
        "dominant_branch": dominant_branch,
        "eligible": bool(
            (_safe_bool(_pick(call, "context_pass"), False) and _safe_bool(_pick(call, "option_tradability_pass"), False))
            or (_safe_bool(_pick(put, "context_pass"), False) and _safe_bool(_pick(put, "option_tradability_pass"), False))
        ),
    }
