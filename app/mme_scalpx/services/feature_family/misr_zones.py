from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/misr_zones.py

Deterministic MISR trap-zone registry helper.

Ownership
---------
This module owns only pure construction of MISR zone rows from already-produced
feature inputs. It does not read/write Redis, mutate state, place orders, or
decide strategy entries.

Freeze law
----------
- ORB_HIGH / ORB_LOW / SWING_HIGH / SWING_LOW zones may be produced only from
  explicit upstream fields.
- Missing ORB/swing source fields produce no zone. No LTP-based invented zone.
- Returned rows match misr_surface.TrapZone-compatible dictionaries.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final, Mapping, Sequence

ZONE_ORB_HIGH: Final[str] = "ORB_HIGH"
ZONE_ORB_LOW: Final[str] = "ORB_LOW"
ZONE_SWING_HIGH: Final[str] = "SWING_HIGH"
ZONE_SWING_LOW: Final[str] = "SWING_LOW"

DEFAULT_ZONE_WIDTH_POINTS: Final[float] = 0.10
DEFAULT_ZONE_QUALITY: Final[float] = 0.50
DEFAULT_ZONE_LIFETIME_MS: Final[int] = 90 * 60 * 1000


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _pick(mapping: Mapping[str, Any] | None, *keys: str) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


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


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _selected_futures(futures_surface: Mapping[str, Any] | None) -> Mapping[str, Any]:
    surface = _as_mapping(futures_surface)
    selected = _as_mapping(_pick(surface, "selected_features"))
    return selected or surface


def _source_map(shared_core: Mapping[str, Any] | None, futures_surface: Mapping[str, Any] | None) -> Mapping[str, Any]:
    shared = _as_mapping(shared_core)
    fut = _selected_futures(futures_surface)

    candidates: list[Mapping[str, Any]] = [
        _as_mapping(_pick(shared, "misr_zone_sources")),
        _as_mapping(_pick(shared, "misr_zones")),
        _as_mapping(_pick(shared, "trap_zones")),
        _as_mapping(_pick(shared, "orb")),
        _as_mapping(_pick(shared, "range_context")),
        fut,
    ]

    merged: dict[str, Any] = {}
    for candidate in candidates:
        merged.update(candidate)
    return merged


def _now_ms(source: Mapping[str, Any]) -> int:
    explicit = _safe_int(_pick(source, "now_ts_ms", "ts_ms", "local_ts_ms"), 0)
    if explicit > 0:
        return explicit

    ts_event_ns = _safe_int(_pick(source, "ts_event_ns", "event_ts_ns"), 0)
    if ts_event_ns > 0:
        return ts_event_ns // 1_000_000

    return 0


def _zone_id(zone_type: str, level: float, source_end_ts_ms: int) -> str:
    return f"{zone_type}|{round(float(level), 4):.4f}|{int(source_end_ts_ms)}"


def _make_zone(
    *,
    zone_type: str,
    level: float,
    width_points: float,
    source_start_ts_ms: int,
    source_end_ts_ms: int,
    quality_score: float,
    valid_from_ts: int,
    expires_ts: int,
) -> dict[str, Any]:
    width = max(float(width_points), DEFAULT_ZONE_WIDTH_POINTS)
    half = width / 2.0

    if zone_type in {ZONE_ORB_HIGH, ZONE_SWING_HIGH}:
        zone_low = level - half
        zone_high = level
        side_bias = "UPSIDE_TRAP"
        trap_zone_level = zone_high
    else:
        zone_low = level
        zone_high = level + half
        side_bias = "DOWNSIDE_TRAP"
        trap_zone_level = zone_low

    return {
        "zone_id": _zone_id(zone_type, trap_zone_level, source_end_ts_ms),
        "zone_type": zone_type,
        "side_bias": side_bias,
        "zone_level": trap_zone_level,
        "trap_zone_level": trap_zone_level,
        "zone_low": zone_low,
        "zone_high": zone_high,
        "zone_width_ticks": width,
        "source_window_start_ts": int(source_start_ts_ms),
        "source_window_end_ts": int(source_end_ts_ms),
        "quality_score": max(0.0, min(float(quality_score), 1.0)),
        "valid_from_ts": int(valid_from_ts),
        "expires_ts": int(expires_ts),
        "broken_flag": False,
        "sweep_count": 0,
        "last_test_ts": 0,
    }


def _append_zone_from_level(
    rows: list[dict[str, Any]],
    *,
    source: Mapping[str, Any],
    zone_type: str,
    level_keys: tuple[str, ...],
    source_start_keys: tuple[str, ...],
    source_end_keys: tuple[str, ...],
    quality_keys: tuple[str, ...],
    width_keys: tuple[str, ...],
) -> None:
    level = _safe_float_or_none(_pick(source, *level_keys))
    if level is None or level <= 0.0:
        return

    now_ms = _now_ms(source)
    source_end = _safe_int(_pick(source, *source_end_keys), now_ms)
    source_start = _safe_int(_pick(source, *source_start_keys), source_end)
    if source_end <= 0:
        return

    quality = _safe_float(_pick(source, *quality_keys), DEFAULT_ZONE_QUALITY)
    width = _safe_float(_pick(source, *width_keys), DEFAULT_ZONE_WIDTH_POINTS)
    valid_from = _safe_int(_pick(source, "valid_from_ts", "valid_from_ts_ms"), source_end)
    expires = _safe_int(
        _pick(source, "expires_ts", "expires_ts_ms"),
        source_end + DEFAULT_ZONE_LIFETIME_MS,
    )

    rows.append(
        _make_zone(
            zone_type=zone_type,
            level=level,
            width_points=width,
            source_start_ts_ms=source_start,
            source_end_ts_ms=source_end,
            quality_score=quality,
            valid_from_ts=valid_from,
            expires_ts=expires,
        )
    )


def build_deterministic_misr_zone_registry(
    *,
    shared_core: Mapping[str, Any] | None,
    futures_surface: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], ...]:
    """Build deterministic MISR trap zones from explicit upstream fields.

    Required explicit source fields may come from shared_core or futures selected
    features. The helper does not invent zones from current LTP.
    """
    source = _source_map(shared_core, futures_surface)
    rows: list[dict[str, Any]] = []

    _append_zone_from_level(
        rows,
        source=source,
        zone_type=ZONE_ORB_HIGH,
        level_keys=("orb_high", "orb_high_level", "ORB_HIGH", "session_orb_high"),
        source_start_keys=("orb_start_ts_ms", "orb_window_start_ts_ms", "source_window_start_ts"),
        source_end_keys=("orb_end_ts_ms", "orb_window_end_ts_ms", "source_window_end_ts"),
        quality_keys=("orb_quality_score", "zone_quality_score", "quality_score"),
        width_keys=("orb_zone_width_points", "zone_width_points", "zone_width_ticks"),
    )
    _append_zone_from_level(
        rows,
        source=source,
        zone_type=ZONE_ORB_LOW,
        level_keys=("orb_low", "orb_low_level", "ORB_LOW", "session_orb_low"),
        source_start_keys=("orb_start_ts_ms", "orb_window_start_ts_ms", "source_window_start_ts"),
        source_end_keys=("orb_end_ts_ms", "orb_window_end_ts_ms", "source_window_end_ts"),
        quality_keys=("orb_quality_score", "zone_quality_score", "quality_score"),
        width_keys=("orb_zone_width_points", "zone_width_points", "zone_width_ticks"),
    )
    _append_zone_from_level(
        rows,
        source=source,
        zone_type=ZONE_SWING_HIGH,
        level_keys=("swing_high", "confirmed_swing_high", "nearest_swing_high"),
        source_start_keys=("swing_high_start_ts_ms", "swing_window_start_ts_ms", "source_window_start_ts"),
        source_end_keys=("swing_high_ts_ms", "swing_high_end_ts_ms", "source_window_end_ts"),
        quality_keys=("swing_high_quality_score", "swing_quality_score", "quality_score"),
        width_keys=("swing_zone_width_points", "zone_width_points", "zone_width_ticks"),
    )
    _append_zone_from_level(
        rows,
        source=source,
        zone_type=ZONE_SWING_LOW,
        level_keys=("swing_low", "confirmed_swing_low", "nearest_swing_low"),
        source_start_keys=("swing_low_start_ts_ms", "swing_window_start_ts_ms", "source_window_start_ts"),
        source_end_keys=("swing_low_ts_ms", "swing_low_end_ts_ms", "source_window_end_ts"),
        quality_keys=("swing_low_quality_score", "swing_quality_score", "quality_score"),
        width_keys=("swing_zone_width_points", "zone_width_points", "zone_width_ticks"),
    )

    # Deterministic prune: latest per type, then stable type order.
    by_type: dict[str, dict[str, Any]] = {}
    for row in rows:
        zone_type = _safe_str(row.get("zone_type"))
        current = by_type.get(zone_type)
        if current is None:
            by_type[zone_type] = row
            continue
        current_key = (
            _safe_int(current.get("valid_from_ts")),
            _safe_int(current.get("source_window_end_ts")),
            _safe_float(current.get("quality_score")),
            _safe_str(current.get("zone_id")),
        )
        row_key = (
            _safe_int(row.get("valid_from_ts")),
            _safe_int(row.get("source_window_end_ts")),
            _safe_float(row.get("quality_score")),
            _safe_str(row.get("zone_id")),
        )
        if row_key > current_key:
            by_type[zone_type] = row

    order = (ZONE_ORB_HIGH, ZONE_ORB_LOW, ZONE_SWING_HIGH, ZONE_SWING_LOW)
    return tuple(by_type[z] for z in order if z in by_type)


__all__ = [
    "ZONE_ORB_HIGH",
    "ZONE_ORB_LOW",
    "ZONE_SWING_HIGH",
    "ZONE_SWING_LOW",
    "build_deterministic_misr_zone_registry",
]
