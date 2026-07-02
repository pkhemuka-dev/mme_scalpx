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
from typing import Any, Final, Mapping, Sequence

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
DEFAULT_HOLD_PROOF_BAND_POINTS: Final[float] = 0.10
DEFAULT_NO_MANS_LAND_POINTS: Final[float] = 0.15
DEFAULT_REVERSAL_VEL_RATIO_MIN: Final[float] = 1.05
DEFAULT_REVERSAL_RESPONSE_EFF_MIN: Final[float] = 0.15
DEFAULT_FLOW_FLIP_CALL_MIN: Final[float] = 0.54
DEFAULT_FLOW_FLIP_PUT_MAX: Final[float] = 0.46
DEFAULT_ZONE_QUALITY_MIN: Final[float] = 0.10
DEFAULT_NEAR_WALL_PENALTY: Final[float] = 0.20
DEFAULT_CONTEXT_SCORE_NEUTRAL: Final[float] = 0.50

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
    return "DOWNSIDE_TRAP" if branch_id == N.BRANCH_CALL else "UPSIDE_TRAP"


def _directional_ok(value: float, branch_id: str) -> bool:
    return value >= 0.0 if branch_id == N.BRANCH_CALL else value <= 0.0


def _ofi_ok(value: float, branch_id: str, call_min: float, put_max: float) -> bool:
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
        and _safe_bool(_pick(surface, "active_zone_valid"), False)
        and _safe_bool(_pick(surface, "fake_break"), False)
        and _safe_bool(_pick(surface, "absorption"), False)
        and _safe_bool(_pick(surface, "range_reentry"), False)
        and _safe_bool(_pick(surface, "flow_flip"), False)
        and _safe_bool(_pick(surface, "hold_proof"), False)
        and _safe_bool(_pick(surface, "no_mans_land_cleared"), False)
        and _safe_bool(_pick(surface, "reversal_impulse"), False)
        and _safe_bool(_pick(surface, "context_pass"), False)
        and _safe_bool(_pick(surface, "option_tradability_pass"), False)
        and not _safe_str(_pick(surface, "failed_stage"))
    )


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
    hold_proof_elapsed_sec: float | None = None,
) -> dict[str, Any]:
    """
    Build one MISR branch surface.

    This is a feature support surface only. It publishes the ordered trap-reversal
    facts strategy.py will later consume.
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
    zones = _as_mapping(zone_registry_surface)

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
    hold_proof_band_points = _threshold_float(
        thresholds,
        "HOLD_PROOF_BAND_POINTS",
        DEFAULT_HOLD_PROOF_BAND_POINTS,
    )
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
    fb_start_ms = _safe_int(
        fake_break_start_ts_ms
        or _pick(fut, "fake_break_start_ts_ms", "trap_event_start_ts_ms", "break_start_ts_ms"),
        0,
    )
    fb_extreme_ms = _safe_int(
        fake_break_extreme_ts_ms
        or _pick(fut, "fake_break_extreme_ts_ms", "trap_event_extreme_ts_ms", "break_extreme_ts_ms"),
        0,
    )

    if bullish:
        fake_break_distance = max(trap_zone_level - fut_ltp, 0.0)
        inside_range = fut_ltp >= (zone_low + range_reentry_buffer_points) if zone_present else False
        no_mans_land_cleared = fut_ltp >= (zone_high + no_mans_land_points) if zone_present else False
    else:
        fake_break_distance = max(fut_ltp - trap_zone_level, 0.0)
        inside_range = fut_ltp <= (zone_high - range_reentry_buffer_points) if zone_present else False
        no_mans_land_cleared = fut_ltp <= (zone_low - no_mans_land_points) if zone_present else False

    fake_break_timestamps_valid = bool(fb_start_ms > 0 and fb_extreme_ms > 0)
    fake_break = (
        active_zone_valid
        and fake_break_timestamps_valid
        and fake_break_distance >= fake_break_min_points
        and _directional_ok(-fut_delta, branch_id)
    )

    absorption_elapsed_sec = max((fb_extreme_ms - fb_start_ms) / 1000.0, 0.0)
    absorption = (
        fake_break
        and absorption_elapsed_sec <= absorption_window_sec
        and _ofi_ok(fut_weighted_ofi, branch_id, absorption_call_ofi_min, absorption_put_ofi_max)
        and _ofi_ok(fut_weighted_ofi_persist, branch_id, absorption_call_ofi_min, absorption_put_ofi_max)
        and fut_volume_norm > 0.0
    )

    range_reentry = absorption and inside_range
    flow_flip = _ofi_ok(opt_weighted_ofi, branch_id, flow_flip_call_min, flow_flip_put_max) and _directional_ok(opt_delta, branch_id)

    hold_elapsed_sec = _safe_float(hold_proof_elapsed_sec, 0.0)
    hold_inside_band = abs(fut_ltp - trap_zone_level) <= max(abs(zone_high - zone_low), hold_proof_band_points)
    hold_proof = (
        range_reentry
        and hold_elapsed_sec >= hold_proof_sec
        and hold_inside_band
        and _directional_ok(fut_ema9_slope, branch_id)
    )

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
    branch_ready = bool(
        surface_present
        and active_zone_valid
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

    return {
        "surface_kind": "misr_branch",
        "present": surface_present,
        "branch_ready": branch_ready,
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
        "context_features": opt_context,
        "premium_health": opt_premium,
        "fallback_features": fallback,
        "strike_surface": strike,
        "tradability": trad,
        "regime_surface": regime,
        "runtime_mode_surface": mode,
        "active_zone": active_zone_map,
        "active_zone_valid": active_zone_valid,
        "trap_zone_level": trap_zone_level,
        "fake_break_distance": fake_break_distance,
        "fake_break_start_ts_ms": fb_start_ms,
        "fake_break_extreme_ts_ms": fb_extreme_ms,
        "fake_break_timestamps_valid": fake_break_timestamps_valid,
        "fake_break": fake_break,
        "absorption": absorption,
        "absorption_elapsed_sec": absorption_elapsed_sec,
        "range_reentry": range_reentry,
        "flow_flip": flow_flip,
        "hold_proof": hold_proof,
        "hold_proof_elapsed_sec": hold_elapsed_sec,
        "hold_inside_band": hold_inside_band,
        "no_mans_land_cleared": no_mans_land_cleared,
        "reversal_impulse": reversal_impulse,
        "trap_event_id": trap_event_id,
        "trap_event_id_valid": trap_event_id is not None,
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
            if branch_ready
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

    call_ready = _branch_ready(call)
    put_ready = _branch_ready(put)

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
_BATCH9_FAMILY_LC = "misr"
_BATCH9_FAMILY_ID = "MISR"
_BATCH9_ALLOWED_BRANCH_IDS = (N.BRANCH_CALL, N.BRANCH_PUT)

_BATCH9_ORIGINAL_BRANCH_BUILDER = build_misr_branch_surface
_BATCH9_ORIGINAL_FAMILY_BUILDER = build_misr_family_surface


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


def build_misr_branch_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
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


def build_misr_family_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH9_ORIGINAL_FAMILY_BUILDER(*args, **kwargs)
    return _batch9_normalize_family_surface(
        dict(out),
        call_surface=kwargs.get("call_surface"),
        put_surface=kwargs.get("put_surface"),
        runtime_mode_surface=kwargs.get("runtime_mode_surface"),
    )

# ============================================================================
# Batch 26I-R1 — MISR canonical producer completion overlay
# ============================================================================
#
# Post-processes MISR branch output so the Batch 26I proof layer sees direct
# canonical producers on every branch surface. This is fail-closed: missing
# source facts remain False/empty, not guessed True.

_BATCH26IR1_ORIGINAL_BUILD_MISR_BRANCH_SURFACE = build_misr_branch_surface


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


def build_misr_branch_surface(*args, **kwargs):
    out = dict(_BATCH26IR1_ORIGINAL_BUILD_MISR_BRANCH_SURFACE(*args, **kwargs))

    active_zone = _batch26ir1_first(out, "active_zone", "zone", "trap_zone", default={})
    trap_event_id = str(_batch26ir1_first(out, "trap_event_id", "source_event_id", default="") or "")

    out.update(
        {
            "active_zone": active_zone,
            "active_zone_valid": _batch26ir1_bool(
                _batch26ir1_first(out, "active_zone_valid", "zone_valid", "active_zone_ready")
            ),
            "trap_event_id": trap_event_id,
            "fake_break_triggered": _batch26ir1_bool(
                _batch26ir1_first(out, "fake_break_triggered", "fake_break_valid", "fake_break_detected", "fake_break")
            ),
            "absorption_pass": _batch26ir1_bool(
                _batch26ir1_first(out, "absorption_pass", "absorption_ok", "absorption_confirmed")
            ),
            "range_reentry_confirmed": _batch26ir1_bool(
                _batch26ir1_first(out, "range_reentry_confirmed", "range_reentry_ok", "reentry_confirmed")
            ),
            "flow_flip_confirmed": _batch26ir1_bool(
                _batch26ir1_first(out, "flow_flip_confirmed", "flow_flip_ok", "flow_reversal_confirmed")
            ),
            "hold_inside_range_proved": _batch26ir1_bool(
                _batch26ir1_first(out, "hold_inside_range_proved", "hold_inside_range_ok", "range_hold_ok")
            ),
            "no_mans_land_cleared": _batch26ir1_bool(
                _batch26ir1_first(out, "no_mans_land_cleared", "no_mans_land_clear", "nml_cleared")
            ),
            "reversal_impulse_confirmed": _batch26ir1_bool(
                _batch26ir1_first(out, "reversal_impulse_confirmed", "reversal_impulse_ok", "impulse_confirmed")
            ),
            "option_tradability_pass": _batch26ir1_bool(
                _batch26ir1_first(out, "option_tradability_pass", "tradability_pass", "selected_option_tradability_ok")
            ),
        }
    )

    return out
