from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/futures_core.py

Canonical shared futures-feature core for ScalpX MME.

Purpose
-------
This module OWNS:
- deterministic normalization of futures feature surfaces
- shared futures directional / velocity / flow helper derivation
- active-provider futures feature assembly for classic MIS doctrines
- Dhan futures feature assembly for MISO and provider-aware comparisons
- cross-futures comparison helpers for features.py publication

This module DOES NOT own:
- provider-routing policy
- option tradability truth
- strike selection
- OI wall / cross-strike context
- regime classification
- doctrine-specific entry / exit logic
- Redis I/O

Frozen design law
-----------------
- Futures own primary directional truth for classic MIS doctrines.
- For MISO, futures remain alignment / tolerance / veto truth only.
- This module is shared feature core only; it must stay doctrine-neutral.
- Returned surfaces must be deterministic, JSON-friendly plain mappings.
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

EPSILON: Final[float] = 1e-8
DEFAULT_STALE_THRESHOLD_MS: Final[float] = 1_000.0
DEFAULT_SPREAD_RATIO_CAP: Final[float] = 1.0
DEFAULT_TOUCH_DEPTH_MIN: Final[int] = 1
DEFAULT_DIRECTIONAL_NEUTRAL_BAND: Final[float] = 0.05
DEFAULT_CONTEXT_SCORE_NEUTRAL: Final[float] = 0.50

__all__ = [
    "build_active_futures_surface",
    "build_cross_futures_surface",
    "build_dhan_futures_surface",
    "build_futures_surface",
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


def _safe_int_or_none(value: Any) -> int | None:
    try:
        return int(float(value))
    except Exception:
        return None


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


def _spread_from_surface(surface: Mapping[str, Any]) -> float:
    spread = _safe_float_or_none(_pick(surface, "spread"))
    if spread is not None:
        return max(spread, 0.0)
    ask = _safe_float_or_none(_pick(surface, "best_ask", "ask"))
    bid = _safe_float_or_none(_pick(surface, "best_bid", "bid"))
    if ask is None or bid is None:
        return 0.0
    return max(ask - bid, 0.0)


def _mid_from_surface(surface: Mapping[str, Any]) -> float:
    mid = _safe_float_or_none(_pick(surface, "mid_price", "mid"))
    if mid is not None and mid > EPSILON:
        return mid
    ask = _safe_float_or_none(_pick(surface, "best_ask", "ask"))
    bid = _safe_float_or_none(_pick(surface, "best_bid", "bid"))
    if ask is not None and bid is not None and (ask + bid) > EPSILON:
        return max((ask + bid) / 2.0, EPSILON)
    ltp = _safe_float_or_none(_pick(surface, "ltp", "last_price", "price"))
    if ltp is not None and ltp > EPSILON:
        return ltp
    return EPSILON


def _spread_ratio_from_surface(surface: Mapping[str, Any]) -> float:
    ratio = _safe_float_or_none(_pick(surface, "spread_ratio"))
    if ratio is not None:
        return max(ratio, 0.0)
    spread = _spread_from_surface(surface)
    mid = _mid_from_surface(surface)
    return max(spread / max(mid, EPSILON), 0.0)


def _bid_qty_5_from_surface(surface: Mapping[str, Any]) -> int:
    return max(
        _safe_int(
            _pick(
                surface,
                "bid_qty_5",
                "best_bid_qty",
                "bid_qty",
            ),
            0,
        ),
        0,
    )


def _ask_qty_5_from_surface(surface: Mapping[str, Any]) -> int:
    return max(
        _safe_int(
            _pick(
                surface,
                "ask_qty_5",
                "best_ask_qty",
                "ask_qty",
            ),
            0,
        ),
        0,
    )


def _touch_depth_from_surface(surface: Mapping[str, Any]) -> int:
    direct = _safe_int(_pick(surface, "touch_depth", "depth_total"), 0)
    if direct > 0:
        return direct
    bid_qty = _bid_qty_5_from_surface(surface)
    ask_qty = _ask_qty_5_from_surface(surface)
    return max(bid_qty + ask_qty, 0)


def _signed_delta(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "delta_3", "price_delta_3", "ltp_delta_3"), 0.0)


def _velocity_ratio(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "velocity_ratio", "ltp_velocity_ratio"), 0.0)


def _weighted_ofi(surface: Mapping[str, Any]) -> float:
    return _safe_float(
        _pick(surface, "weighted_ofi", "wofi", "ofi_weighted", "order_flow_imbalance"),
        0.0,
    )


def _weighted_ofi_persist(surface: Mapping[str, Any]) -> float:
    return _safe_float(
        _pick(surface, "weighted_ofi_persist", "wofi_persist", "ofi_persist"),
        0.0,
    )


def _book_pressure(surface: Mapping[str, Any]) -> float:
    return _safe_float(
        _pick(surface, "book_pressure", "imbalance_ratio", "queue_imbalance"),
        0.5,
    )


def _vwap_distance(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "vwap_distance", "dist_from_vwap"), 0.0)


def _vwap_distance_ratio(surface: Mapping[str, Any]) -> float:
    explicit = _safe_float_or_none(_pick(surface, "vwap_distance_ratio"))
    if explicit is not None:
        return explicit
    vwap_distance = _vwap_distance(surface)
    ltp = _safe_float_or_none(_pick(surface, "ltp", "last_price", "price"))
    if ltp is None or abs(ltp) <= EPSILON:
        return 0.0
    return vwap_distance / max(abs(ltp), EPSILON)


def _ema9_slope(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "ema9_slope", "ema_9_slope"), 0.0)


def _ema21_slope(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "ema21_slope", "ema_21_slope"), 0.0)


def _event_rate_spike(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "event_rate_spike_ratio", "event_rate_ratio"), 0.0)


def _volume_norm(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "volume_norm", "normalized_volume"), 0.0)


def _cvd_delta(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "cvd_delta", "cvd_3", "cvd_change"), 0.0)


def _nof_slope(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "nof_slope", "wofi_slope", "ofi_slope"), 0.0)


def _trend_score(
    *,
    delta_3: float,
    weighted_ofi: float,
    book_pressure: float,
    vwap_distance: float,
    ema9_slope: float,
    cvd_delta: float,
) -> float:
    return (
        (delta_3 * 0.35)
        + (weighted_ofi * 4.0 * 0.20)
        + ((book_pressure - 0.5) * 2.0 * 0.15)
        + (vwap_distance * 0.10)
        + (ema9_slope * 0.10)
        + (cvd_delta * 0.10)
    )


def _direction_label(direction_score: float) -> str:
    if direction_score > DEFAULT_DIRECTIONAL_NEUTRAL_BAND:
        return "BULLISH"
    if direction_score < -DEFAULT_DIRECTIONAL_NEUTRAL_BAND:
        return "BEARISH"
    return "NEUTRAL"


def _context_score(
    *,
    present: bool,
    spread_ratio: float,
    touch_depth: int,
    weighted_ofi: float,
    velocity_ratio: float,
    stale: bool,
) -> float:
    score = DEFAULT_CONTEXT_SCORE_NEUTRAL
    if present:
        score += 0.10
    if not stale:
        score += 0.10
    if spread_ratio <= 0.05:
        score += 0.10
    if touch_depth >= 200:
        score += 0.10
    if abs(weighted_ofi) > 0.0:
        score += 0.05
    if velocity_ratio > 0.0:
        score += 0.05
    return max(0.0, min(score, 1.0))


def build_futures_surface(
    *,
    futures_surface: Mapping[str, Any] | None,
    runtime_mode: str = "",
    source_label: str = "",
    role_label: str = "",
) -> dict[str, Any]:
    surface = _as_mapping(futures_surface)

    present = bool(surface) and _safe_bool(_pick(surface, "present"), True)
    instrument_key = _safe_str(
        _pick(surface, "instrument_key", "ik", "security_id"),
        "",
    )
    instrument_token = _safe_str(
        _pick(surface, "instrument_token", "token", "security_id"),
        "",
    )
    provider_id = _safe_str(
        _pick(surface, "provider_id", "marketdata_provider_id"),
        "",
    )

    ltp = _safe_float(_pick(surface, "ltp", "last_price", "price"), 0.0)
    best_bid = _safe_float(_pick(surface, "best_bid", "bid"), 0.0)
    best_ask = _safe_float(_pick(surface, "best_ask", "ask"), 0.0)
    spread = _spread_from_surface(surface)
    spread_ratio = _spread_ratio_from_surface(surface)
    mid_price = _mid_from_surface(surface)

    bid_qty_5 = _bid_qty_5_from_surface(surface)
    ask_qty_5 = _ask_qty_5_from_surface(surface)
    touch_depth = _touch_depth_from_surface(surface)
    depth_total = touch_depth

    delta_3 = _signed_delta(surface)
    velocity_ratio = _velocity_ratio(surface)
    weighted_ofi = _weighted_ofi(surface)
    weighted_ofi_persist = _weighted_ofi_persist(surface)
    book_pressure = _book_pressure(surface)
    vwap_distance = _vwap_distance(surface)
    vwap_distance_ratio = _vwap_distance_ratio(surface)
    ema9_slope = _ema9_slope(surface)
    ema21_slope = _ema21_slope(surface)
    event_rate_spike_ratio = _event_rate_spike(surface)
    volume_norm = _volume_norm(surface)
    cvd_delta = _cvd_delta(surface)
    nof_slope = _nof_slope(surface)

    stale = _safe_bool(_pick(surface, "stale"), False)
    ts_event_ns = _safe_int(_pick(surface, "ts_event_ns", "event_ts_ns", "ts_ns"), 0)
    ts_local_ns = _safe_int(_pick(surface, "ts_local_ns", "local_ts_ns"), 0)
    age_ms = _safe_float_or_none(_pick(surface, "age_ms"))
    if age_ms is None and ts_event_ns > 0 and ts_local_ns > 0:
        age_ms = max((ts_local_ns - ts_event_ns) / 1_000_000.0, 0.0)
    if age_ms is None:
        age_ms = 0.0

    stale = stale or (age_ms > DEFAULT_STALE_THRESHOLD_MS)

    trend_score = _trend_score(
        delta_3=delta_3,
        weighted_ofi=weighted_ofi,
        book_pressure=book_pressure,
        vwap_distance=vwap_distance,
        ema9_slope=ema9_slope,
        cvd_delta=cvd_delta,
    )
    direction_score = trend_score

    direction_label = _direction_label(direction_score)
    bullish_flow_ok = direction_score > DEFAULT_DIRECTIONAL_NEUTRAL_BAND
    bearish_flow_ok = direction_score < -DEFAULT_DIRECTIONAL_NEUTRAL_BAND

    vwap_alignment_call = vwap_distance >= -DEFAULT_DIRECTIONAL_NEUTRAL_BAND
    vwap_alignment_put = vwap_distance <= DEFAULT_DIRECTIONAL_NEUTRAL_BAND

    contradiction_score_call = max(-direction_score, 0.0)
    contradiction_score_put = max(direction_score, 0.0)

    context_score = _context_score(
        present=present,
        spread_ratio=spread_ratio,
        touch_depth=touch_depth,
        weighted_ofi=weighted_ofi,
        velocity_ratio=velocity_ratio,
        stale=stale,
    )

    return {
        "present": present,
        "runtime_mode": runtime_mode,
        "source_label": source_label,
        "role_label": role_label,
        "instrument_key": instrument_key or None,
        "instrument_token": instrument_token or None,
        "provider_id": provider_id or None,
        "ltp": ltp,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "bid_qty_5": bid_qty_5,
        "ask_qty_5": ask_qty_5,
        "mid_price": mid_price,
        "spread": spread,
        "spread_ratio": spread_ratio,
        "touch_depth": touch_depth,
        "depth_total": depth_total,
        "delta_3": delta_3,
        "velocity_ratio": velocity_ratio,
        "weighted_ofi": weighted_ofi,
        "weighted_ofi_persist": weighted_ofi_persist,
        "book_pressure": book_pressure,
        "vwap_distance": vwap_distance,
        "vwap_distance_ratio": vwap_distance_ratio,
        "ema9_slope": ema9_slope,
        "ema21_slope": ema21_slope,
        "event_rate_spike_ratio": event_rate_spike_ratio,
        "volume_norm": volume_norm,
        "cvd_delta": cvd_delta,
        "nof_slope": nof_slope,
        "trend_score": trend_score,
        "stale": stale,
        "age_ms": age_ms,
        "ts_event_ns": ts_event_ns,
        "ts_local_ns": ts_local_ns,
        "direction_score": direction_score,
        "direction_label": direction_label,
        "bullish_flow_ok": bullish_flow_ok,
        "bearish_flow_ok": bearish_flow_ok,
        "vwap_alignment_call": vwap_alignment_call,
        "vwap_alignment_put": vwap_alignment_put,
        "contradiction_score_call": contradiction_score_call,
        "contradiction_score_put": contradiction_score_put,
        "liquidity_ok": (touch_depth >= DEFAULT_TOUCH_DEPTH_MIN) and (spread_ratio <= DEFAULT_SPREAD_RATIO_CAP),
        "context_score": context_score,
    }


def build_active_futures_surface(
    *,
    active_surface: Mapping[str, Any] | None,
    runtime_mode: str = "",
) -> dict[str, Any]:
    selected = build_futures_surface(
        futures_surface=active_surface,
        runtime_mode=runtime_mode,
        source_label="active_futures",
        role_label="classic_directional_truth",
    )
    return {
        "present": bool(selected.get("present")),
        "runtime_mode": runtime_mode,
        "selected_features": selected,
        "selected_source_label": "active_futures",
    }


def build_dhan_futures_surface(
    *,
    dhan_surface: Mapping[str, Any] | None,
    runtime_mode: str = "",
) -> dict[str, Any]:
    selected = build_futures_surface(
        futures_surface=dhan_surface,
        runtime_mode=runtime_mode,
        source_label="dhan_futures",
        role_label="miso_alignment_veto_truth",
    )
    return {
        "present": bool(selected.get("present")),
        "runtime_mode": runtime_mode,
        "selected_features": selected,
        "selected_source_label": "dhan_futures",
    }


def build_cross_futures_surface(
    *,
    active_surface: Mapping[str, Any] | None = None,
    dhan_surface: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    active = _as_mapping(_pick(_as_mapping(active_surface), "selected_features") or active_surface)
    dhan = _as_mapping(_pick(_as_mapping(dhan_surface), "selected_features") or dhan_surface)

    active_present = bool(active.get("present"))
    dhan_present = bool(dhan.get("present"))

    active_direction_score = _safe_float(active.get("direction_score"), 0.0)
    dhan_direction_score = _safe_float(dhan.get("direction_score"), 0.0)
    active_velocity_ratio = _safe_float(active.get("velocity_ratio"), 0.0)
    dhan_velocity_ratio = _safe_float(dhan.get("velocity_ratio"), 0.0)

    direction_delta = dhan_direction_score - active_direction_score
    velocity_delta = dhan_velocity_ratio - active_velocity_ratio

    agreement = (
        active_present
        and dhan_present
        and (
            (_safe_str(active.get("direction_label")) == _safe_str(dhan.get("direction_label")))
            or (
                _safe_str(active.get("direction_label")) == "NEUTRAL"
                and _safe_str(dhan.get("direction_label")) == "NEUTRAL"
            )
        )
    )

    return {
        "present": active_present or dhan_present,
        "active_present": active_present,
        "dhan_present": dhan_present,
        "active_provider_id": _safe_str(active.get("provider_id")) or None,
        "dhan_provider_id": _safe_str(dhan.get("provider_id")) or None,
        "active_direction_label": _safe_str(active.get("direction_label")),
        "dhan_direction_label": _safe_str(dhan.get("direction_label")),
        "active_direction_score": active_direction_score,
        "dhan_direction_score": dhan_direction_score,
        "direction_delta": direction_delta,
        "active_velocity_ratio": active_velocity_ratio,
        "dhan_velocity_ratio": dhan_velocity_ratio,
        "velocity_delta": velocity_delta,
        "direction_agreement": agreement,
        "provider_divergence_score": abs(direction_delta) + abs(velocity_delta),
    }
