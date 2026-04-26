from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/option_core.py

Shared deterministic option-surface core for ScalpX MME feature-family.

Purpose
-------
This module OWNS:
- shared selected-option live-book math used by all family feature surfaces
- deterministic premium-health / tradability support derivation
- Dhan slow-context extraction for selected CALL / PUT
- JSON-friendly selected-option / shadow-option support payload builders
- side-neutral helper surfaces consumed later by:
  - mist_surface.py
  - misb_surface.py
  - misc_surface.py
  - misr_surface.py
  - miso_surface.py

This module DOES NOT own:
- provider selection / failover policy
- strike-ladder ownership or candidate ranking
- doctrine-specific pass/fail decisions
- sub-second burst timing logic
- strategy state-machine decisions
- Redis reads/writes
- broker execution truth

Frozen design law
-----------------
- Classic families remain futures-led and option-confirmed.
- MISO remains option-led, but this module still does not own burst logic.
- Selected live option book remains tradability truth for classic families.
- Dhan OI / IV / delta / gamma / theta / vega remain slow context only.
- This module may derive support surfaces, but may not emit doctrine decisions.
- Outputs are deterministic, JSON-friendly plain mappings.
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

from . import strike_selection as SS

EPSILON: Final[float] = 1e-8

DEFAULT_PREMIUM_FLOOR_MIN: Final[float] = 1.0
DEFAULT_DEPTH_TOTAL_MIN: Final[int] = 1
DEFAULT_SPREAD_RATIO_MAX: Final[float] = 1.0
DEFAULT_RESPONSE_EFFICIENCY_MIN: Final[float] = 0.0

OPTION_SIDE_IDS: Final[tuple[str, ...]] = (
    N.SIDE_CALL,
    N.SIDE_PUT,
)

_CONTEXT_FIELD_SUFFIXES: Final[tuple[str, ...]] = (
    "instrument_key",
    "score",
    "delta",
    "authoritative_delta",
    "gamma",
    "theta",
    "vega",
    "iv",
    "iv_change_1m_pct",
    "oi",
    "oi_change",
    "volume",
    "cross_strike_spread_rank",
    "cross_strike_volume_rank",
    "spread_score",
    "depth_score",
    "volume_score",
    "oi_score",
    "iv_score",
    "delta_score",
    "gamma_score",
    "iv_sanity_score",
)

_STRIKE_KEYS: Final[tuple[str, ...]] = (
    "strike",
    "strike_price",
    "selected_strike",
)
_INSTRUMENT_KEY_KEYS: Final[tuple[str, ...]] = (
    "instrument_key",
    "selected_instrument_key",
    "security_id",
)
_INSTRUMENT_TOKEN_KEYS: Final[tuple[str, ...]] = (
    "instrument_token",
    "security_id",
    "token",
)
_OPTION_SYMBOL_KEYS: Final[tuple[str, ...]] = (
    "option_symbol",
    "trading_symbol",
    "symbol",
)
_LTP_KEYS: Final[tuple[str, ...]] = (
    "ltp",
    "last_price",
    "last_traded_price",
    "price",
)
_BID_KEYS: Final[tuple[str, ...]] = (
    "best_bid",
    "bid",
    "bid_price",
)
_ASK_KEYS: Final[tuple[str, ...]] = (
    "best_ask",
    "ask",
    "ask_price",
)
_BID_QTY_KEYS: Final[tuple[str, ...]] = (
    "bid_qty_5",
    "bid_qty",
    "best_bid_qty",
    "bid_quantity",
)
_ASK_QTY_KEYS: Final[tuple[str, ...]] = (
    "ask_qty_5",
    "ask_qty",
    "best_ask_qty",
    "ask_quantity",
)
_VOLUME_KEYS: Final[tuple[str, ...]] = (
    "volume",
    "traded_volume",
)
_OI_KEYS: Final[tuple[str, ...]] = (
    "oi",
    "open_interest",
)
_DELTA_PROXY_KEYS: Final[tuple[str, ...]] = (
    "delta_proxy",
    "delta",
)
_SPREAD_KEYS: Final[tuple[str, ...]] = (
    "spread",
    "option_spread",
)
_SPREAD_RATIO_KEYS: Final[tuple[str, ...]] = (
    "spread_ratio",
    "option_spread_ratio",
)
_SPREAD_TICKS_KEYS: Final[tuple[str, ...]] = (
    "spread_ticks",
    "option_spread_ticks",
)
_DEPTH_TOTAL_KEYS: Final[tuple[str, ...]] = (
    "depth_total",
    "touch_depth",
    "option_touch_depth",
)
_RESPONSE_EFFICIENCY_KEYS: Final[tuple[str, ...]] = (
    "response_efficiency",
    "response_eff",
    "option_response_efficiency",
)
_IMPACT_DEPTH_KEYS: Final[tuple[str, ...]] = (
    "impact_depth_fraction_one_lot",
    "impact_depth_fraction",
)
_DELTA_3_KEYS: Final[tuple[str, ...]] = (
    "delta_3",
    "option_delta_3",
)
_VELOCITY_RATIO_KEYS: Final[tuple[str, ...]] = (
    "velocity_ratio",
    "option_velocity_ratio",
)
_WEIGHTED_OFI_KEYS: Final[tuple[str, ...]] = (
    "weighted_ofi_persist",
    "ofi_persist",
    "option_ofi_persist",
)
_PACKET_GAP_KEYS: Final[tuple[str, ...]] = (
    "packet_gap_ms",
    "age_ms",
)
_TICK_SIZE_KEYS: Final[tuple[str, ...]] = (
    "tick_size",
    "option_tick_size",
)
_LOT_SIZE_KEYS: Final[tuple[str, ...]] = (
    "lot_size",
    "option_lot_size",
)
_PROVIDER_ID_KEYS: Final[tuple[str, ...]] = (
    "provider_id",
    "marketdata_provider_id",
)
_ENTRY_MODE_KEYS: Final[tuple[str, ...]] = (
    "entry_mode",
    "mode_hint",
)


class OptionCoreError(ValueError):
    """Raised when option-core inputs are invalid or internally inconsistent."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OptionCoreError(message)


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


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        out = float(value)
    except Exception:
        return default
    if not isfinite(out):
        return default
    return out


def _safe_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    try:
        return int(float(value))
    except Exception:
        return default


def _pick(mapping: Mapping[str, Any] | None, keys: tuple[str, ...]) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _copy_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    return dict(value)


def _normalize_side(side: Any) -> str:
    normalized = _safe_str(side).upper()
    _require(
        normalized in OPTION_SIDE_IDS,
        f"side must be one of {OPTION_SIDE_IDS!r}, got {normalized!r}",
    )
    return normalized


def context_prefix_for_side(side: Any) -> str:
    normalized_side = _normalize_side(side)
    return "selected_call" if normalized_side == N.SIDE_CALL else "selected_put"


def opposing_side(side: Any) -> str:
    normalized_side = _normalize_side(side)
    return N.SIDE_PUT if normalized_side == N.SIDE_CALL else N.SIDE_CALL


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _rounded(value: float | None, ndigits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), ndigits)


def _safe_ratio(
    numer: float | int | None,
    denom: float | int | None,
    default: float | None = None,
) -> float | None:
    num = _safe_float(numer, None)
    den = _safe_float(denom, None)
    if num is None or den is None:
        return default
    if abs(den) <= EPSILON:
        return default
    return num / den


def _spread(best_bid: Any, best_ask: Any) -> float | None:
    bid = _safe_float(best_bid, None)
    ask = _safe_float(best_ask, None)
    if bid is None or ask is None:
        return None
    if ask < bid:
        return None
    return ask - bid


def _mid(best_bid: Any, best_ask: Any, ltp: Any = None) -> float | None:
    bid = _safe_float(best_bid, None)
    ask = _safe_float(best_ask, None)
    if bid is not None and ask is not None and ask >= bid:
        return (bid + ask) / 2.0
    return _safe_float(ltp, None)


def _spread_ratio(best_bid: Any, best_ask: Any, ltp: Any = None) -> float | None:
    spread = _spread(best_bid, best_ask)
    mid = _mid(best_bid, best_ask, ltp)
    if spread is None or mid is None or mid <= EPSILON:
        return None
    return spread / mid


def _spread_ticks(
    *,
    best_bid: Any,
    best_ask: Any,
    tick_size: Any,
) -> float | None:
    spread = _spread(best_bid, best_ask)
    tick = _safe_float(tick_size, None)
    if spread is None or tick is None or tick <= EPSILON:
        return None
    return spread / tick


def _touch_depth(bid_qty: Any, ask_qty: Any) -> int | None:
    bid = _safe_int(bid_qty, None)
    ask = _safe_int(ask_qty, None)
    if bid is None and ask is None:
        return None
    return max((bid or 0) + (ask or 0), 0)


def _impact_depth_fraction_one_lot(
    *,
    lot_size: Any,
    depth_total: Any,
) -> float | None:
    lots = _safe_int(lot_size, None)
    depth = _safe_int(depth_total, None)
    if lots is None or depth is None or depth <= 0:
        return None
    return lots / max(depth, 1)


def _response_efficiency(
    *,
    delta_3: Any,
    best_bid: Any,
    best_ask: Any,
    tick_size: Any,
    depth_total: Any,
    lot_size: Any,
) -> float | None:
    move = abs(_safe_float(delta_3, 0.0) or 0.0)
    if move <= EPSILON:
        return 0.0

    spread = _spread(best_bid, best_ask)
    tick = _safe_float(tick_size, None)
    denominator = None
    if spread is not None and spread > EPSILON:
        denominator = spread
    elif tick is not None and tick > EPSILON:
        denominator = tick

    if denominator is None:
        return None

    raw_eff = move / denominator
    impact_fraction = _impact_depth_fraction_one_lot(
        lot_size=lot_size,
        depth_total=depth_total,
    )
    if impact_fraction is None:
        return raw_eff
    depth_penalty = max(impact_fraction, EPSILON)
    return raw_eff / depth_penalty


def _weighted_ofi_proxy(
    *,
    bid_qty: Any,
    ask_qty: Any,
) -> float | None:
    bid = _safe_float(bid_qty, None)
    ask = _safe_float(ask_qty, None)
    if bid is None and ask is None:
        return None
    total = (bid or 0.0) + (ask or 0.0)
    if total <= EPSILON:
        return None
    return (bid or 0.0) / total


def _velocity_ratio_proxy(
    *,
    delta_3: Any,
    tick_size: Any,
) -> float | None:
    move = abs(_safe_float(delta_3, 0.0) or 0.0)
    tick = _safe_float(tick_size, None)
    if tick is None or tick <= EPSILON:
        return None
    return move / tick


# Batch 26G V2 — exact timestamp integer parser.
def _batch26g_exact_int(value: Any, default: int | None = None) -> int | None:
    """Parse integer-like values without float precision loss.

    Nanosecond timestamps exceed precise float integer range. Do not route
    ltt_ns / trade_ts_ns through int(float(value)).
    """
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip()
    if not text:
        return default
    if "." in text:
        # Only accept decimal strings by truncating after decimal point without
        # converting the full nanosecond value through float.
        text = text.split(".", 1)[0]
    try:
        return int(text)
    except Exception:
        return default


def build_live_option_surface(
    *,
    side: str,
    live_source: Mapping[str, Any] | None,
    provider_id: str | None = None,
    strike: Any = None,
    instrument_key: str | None = None,
    instrument_token: str | None = None,
    option_symbol: str | None = None,
    tick_size: Any = None,
    lot_size: Any = None,
    entry_mode: str | None = None,
    delta_3: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    response_efficiency: Any = None,
    impact_depth_fraction_one_lot: Any = None,
    packet_gap_ms: Any = None,
    ask_reloaded: Any = None,
    bid_reloaded: Any = None,
) -> dict[str, Any]:
    normalized_side = _normalize_side(side)
    source = _copy_mapping(live_source)

    resolved_instrument_key = _safe_str(
        _coalesce(
            instrument_key,
            _pick(source, _INSTRUMENT_KEY_KEYS),
        )
    ) or None
    resolved_instrument_token = _safe_str(
        _coalesce(
            instrument_token,
            _pick(source, _INSTRUMENT_TOKEN_KEYS),
        )
    ) or None
    resolved_option_symbol = _safe_str(
        _coalesce(
            option_symbol,
            _pick(source, _OPTION_SYMBOL_KEYS),
        )
    ) or None
    resolved_provider_id = _safe_str(
        _coalesce(
            provider_id,
            _pick(source, _PROVIDER_ID_KEYS),
        )
    ) or None

    ltp = _safe_float(_coalesce(_pick(source, _LTP_KEYS)), None)
    best_bid = _safe_float(_coalesce(_pick(source, _BID_KEYS)), None)
    best_ask = _safe_float(_coalesce(_pick(source, _ASK_KEYS)), None)
    bid_qty = _safe_int(_coalesce(_pick(source, _BID_QTY_KEYS)), None)
    ask_qty = _safe_int(_coalesce(_pick(source, _ASK_QTY_KEYS)), None)

    resolved_tick_size = _safe_float(
        _coalesce(
            tick_size,
            _pick(source, _TICK_SIZE_KEYS),
        ),
        None,
    )
    resolved_lot_size = _safe_int(
        _coalesce(
            lot_size,
            _pick(source, _LOT_SIZE_KEYS),
        ),
        None,
    )

    depth_total = _safe_int(
        _coalesce(
            _pick(source, _DEPTH_TOTAL_KEYS),
            _touch_depth(bid_qty, ask_qty),
        ),
        None,
    )
    spread = _safe_float(
        _coalesce(
            _pick(source, _SPREAD_KEYS),
            _spread(best_bid, best_ask),
        ),
        None,
    )
    spread_ratio = _safe_float(
        _coalesce(
            _pick(source, _SPREAD_RATIO_KEYS),
            _spread_ratio(best_bid, best_ask, ltp),
        ),
        None,
    )
    spread_ticks = _safe_float(
        _coalesce(
            _pick(source, _SPREAD_TICKS_KEYS),
            _spread_ticks(best_bid=best_bid, best_ask=best_ask, tick_size=resolved_tick_size),
        ),
        None,
    )

    resolved_delta_3 = _safe_float(
        _coalesce(
            delta_3,
            _pick(source, _DELTA_3_KEYS),
        ),
        None,
    )
    resolved_velocity_ratio = _safe_float(
        _coalesce(
            velocity_ratio,
            _pick(source, _VELOCITY_RATIO_KEYS),
            _velocity_ratio_proxy(delta_3=resolved_delta_3, tick_size=resolved_tick_size),
        ),
        None,
    )
    resolved_weighted_ofi = _safe_float(
        _coalesce(
            weighted_ofi_persist,
            _pick(source, _WEIGHTED_OFI_KEYS),
            _weighted_ofi_proxy(bid_qty=bid_qty, ask_qty=ask_qty),
        ),
        None,
    )
    resolved_response_efficiency = _safe_float(
        _coalesce(
            response_efficiency,
            _pick(source, _RESPONSE_EFFICIENCY_KEYS),
            _response_efficiency(
                delta_3=resolved_delta_3,
                best_bid=best_bid,
                best_ask=best_ask,
                tick_size=resolved_tick_size,
                depth_total=depth_total,
                lot_size=resolved_lot_size,
            ),
        ),
        None,
    )
    resolved_impact_depth_fraction = _safe_float(
        _coalesce(
            impact_depth_fraction_one_lot,
            _pick(source, _IMPACT_DEPTH_KEYS),
            _impact_depth_fraction_one_lot(lot_size=resolved_lot_size, depth_total=depth_total),
        ),
        None,
    )

    resolved_strike = _safe_float(
        _coalesce(
            strike,
            _pick(source, _STRIKE_KEYS),
        ),
        None,
    )
    resolved_packet_gap_ms = _safe_int(
        _coalesce(
            packet_gap_ms,
            _pick(source, _PACKET_GAP_KEYS),
        ),
        None,
    )
    resolved_entry_mode = _safe_str(
        _coalesce(
            entry_mode,
            _pick(source, _ENTRY_MODE_KEYS),
        )
    ) or None

    present = bool(
        resolved_instrument_key
        or resolved_option_symbol
        or resolved_strike is not None
        or ltp is not None
    )

    return {
        "present": present,
        "side": normalized_side,
        "provider_id": resolved_provider_id,
        "instrument_key": resolved_instrument_key,
        "instrument_token": resolved_instrument_token,
        "option_symbol": resolved_option_symbol,
        "strike": resolved_strike,
        "entry_mode": resolved_entry_mode,
        "ltp": ltp,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid": _mid(best_bid, best_ask, ltp),
        "spread": spread,
        "spread_ratio": spread_ratio,
        "spread_ticks": spread_ticks,
        "bid_qty_5": bid_qty,
        "ask_qty_5": ask_qty,
        "depth_total": depth_total,
        "volume": _safe_int(_coalesce(_pick(source, _VOLUME_KEYS)), None),
        "ltq": _safe_int(_coalesce(_pick(source, ("ltq", "last_traded_quantity", "lastTradeQty", "qty", "quantity"))), None),
        "ltt_ns": _batch26g_exact_int(_coalesce(_pick(source, ("ltt_ns", "last_trade_ts_ns", "trade_ts_ns", "ltt"))), None),
        "recent_ticks": _coalesce(_pick(source, ("recent_ticks", "trade_ticks", "tick_buffer", "ticks", "recent_trade_ticks")), ()),
        "trade_ticks": _coalesce(_pick(source, ("trade_ticks", "recent_ticks", "tick_buffer", "ticks", "recent_trade_ticks")), ()),
        "oi": _safe_int(_coalesce(_pick(source, _OI_KEYS)), None),
        "delta_proxy": _safe_float(
            _coalesce(_pick(source, _DELTA_PROXY_KEYS)),
            None,
        ),
        "tick_size": resolved_tick_size,
        "lot_size": resolved_lot_size,
        "delta_3": resolved_delta_3,
        "velocity_ratio": resolved_velocity_ratio,
        "weighted_ofi_persist": resolved_weighted_ofi,
        "response_efficiency": resolved_response_efficiency,
        "impact_depth_fraction_one_lot": resolved_impact_depth_fraction,
        "packet_gap_ms": resolved_packet_gap_ms,
        "ask_reloaded": _safe_bool(ask_reloaded if ask_reloaded is not None else source.get("ask_reloaded")),
        "bid_reloaded": _safe_bool(bid_reloaded if bid_reloaded is not None else source.get("bid_reloaded")),
        "raw": source,
    }


def build_premium_health_surface(
    *,
    ltp: Any,
    spread_ratio: Any,
    depth_total: Any,
    response_efficiency: Any,
    premium_floor_min: float = DEFAULT_PREMIUM_FLOOR_MIN,
    depth_total_min: int = DEFAULT_DEPTH_TOTAL_MIN,
    spread_ratio_max: float = DEFAULT_SPREAD_RATIO_MAX,
    response_efficiency_min: float = DEFAULT_RESPONSE_EFFICIENCY_MIN,
) -> dict[str, Any]:
    premium = _safe_float(ltp, None)
    spread_ratio_value = _safe_float(spread_ratio, None)
    depth_total_value = _safe_int(depth_total, None)
    response_eff_value = _safe_float(response_efficiency, None)

    premium_floor_ok = bool(
        premium is not None and premium >= max(float(premium_floor_min), 0.0)
    )
    depth_ok = bool(
        depth_total_value is not None and depth_total_value >= max(int(depth_total_min), 0)
    )
    spread_ratio_ok = bool(
        spread_ratio_value is not None and spread_ratio_value <= max(float(spread_ratio_max), 0.0)
    )
    response_efficiency_ok = bool(
        response_eff_value is not None
        and response_eff_value >= float(response_efficiency_min)
    )

    return {
        "premium_floor_min": float(premium_floor_min),
        "depth_total_min": int(depth_total_min),
        "spread_ratio_max": float(spread_ratio_max),
        "response_efficiency_min": float(response_efficiency_min),
        "premium_floor_ok": premium_floor_ok,
        "depth_ok": depth_ok,
        "spread_ratio_ok": spread_ratio_ok,
        "response_efficiency_ok": response_efficiency_ok,
        "tradability_ok": bool(
            premium_floor_ok
            and depth_ok
            and spread_ratio_ok
            and response_efficiency_ok
        ),
    }


def build_option_context_surface(
    *,
    side: str,
    dhan_context: Mapping[str, Any] | None,
    strike_surface: Mapping[str, Any] | None = None,
    oi_wall_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_side = _normalize_side(side)
    prefix = context_prefix_for_side(normalized_side)
    raw_context = _copy_mapping(dhan_context)

    wall_summary = (
        _copy_mapping(oi_wall_summary)
        if isinstance(oi_wall_summary, Mapping)
        else SS.build_oi_wall_summary(dhan_context=raw_context)
    )

    if normalized_side == N.SIDE_CALL:
        same_side_wall = wall_summary.get("call_wall")
        opposing_wall = wall_summary.get("put_wall")
    else:
        same_side_wall = wall_summary.get("put_wall")
        opposing_wall = wall_summary.get("call_wall")

    selected_strike_surface = _copy_mapping(strike_surface)
    if not selected_strike_surface and raw_context:
        if normalized_side in OPTION_SIDE_IDS:
            selected_strike_surface = SS.build_classic_strike_surface(
                dhan_context=raw_context,
                side=normalized_side,
            )

    surface: dict[str, Any] = {
        "context_present": bool(raw_context),
        "context_status": _safe_str(raw_context.get("context_status")) or None,
        "instrument_key": _safe_str(raw_context.get(f"{prefix}_instrument_key")) or None,
        "oi_bias": _safe_str(wall_summary.get("oi_bias")) or None,
        "oi_bias_score": _safe_float(wall_summary.get("oi_bias_score"), None),
        "same_side_wall": same_side_wall if isinstance(same_side_wall, Mapping) else None,
        "opposing_wall": opposing_wall if isinstance(opposing_wall, Mapping) else None,
        "same_side_wall_near": _safe_bool(
            same_side_wall.get("near_wall") if isinstance(same_side_wall, Mapping) else False
        ),
        "opposing_wall_near": _safe_bool(
            opposing_wall.get("near_wall") if isinstance(opposing_wall, Mapping) else False
        ),
        "same_side_wall_strength_score": _safe_float(
            same_side_wall.get("wall_strength_score") if isinstance(same_side_wall, Mapping) else None,
            None,
        ),
        "opposing_wall_strength_score": _safe_float(
            opposing_wall.get("wall_strength_score") if isinstance(opposing_wall, Mapping) else None,
            None,
        ),
        "selected_strike_surface": selected_strike_surface or None,
        "oi_wall_summary": wall_summary if wall_summary else None,
    }

    for suffix in _CONTEXT_FIELD_SUFFIXES:
        surface[suffix] = raw_context.get(f"{prefix}_{suffix}")

    return surface


def build_shadow_option_surface(
    *,
    side: str,
    live_source: Mapping[str, Any] | None,
    provider_id: str | None = None,
    strike: Any = None,
    instrument_key: str | None = None,
    instrument_token: str | None = None,
    option_symbol: str | None = None,
    tick_size: Any = None,
    lot_size: Any = None,
    delta_3: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    packet_gap_ms: Any = None,
) -> dict[str, Any]:
    live_surface = build_live_option_surface(
        side=side,
        live_source=live_source,
        provider_id=provider_id,
        strike=strike,
        instrument_key=instrument_key,
        instrument_token=instrument_token,
        option_symbol=option_symbol,
        tick_size=tick_size,
        lot_size=lot_size,
        delta_3=delta_3,
        velocity_ratio=velocity_ratio,
        weighted_ofi_persist=weighted_ofi_persist,
        packet_gap_ms=packet_gap_ms,
        entry_mode=N.ENTRY_MODE_DIRECT,
    )
    return {
        "present": bool(live_surface.get("present")),
        "side": _normalize_side(side),
        "live": live_surface,
        "shadow_support_ready": bool(live_surface.get("present")),
    }


def build_classic_option_surface(
    *,
    side: str,
    selected_live_source: Mapping[str, Any] | None,
    dhan_context: Mapping[str, Any] | None = None,
    strike_surface: Mapping[str, Any] | None = None,
    oi_wall_summary: Mapping[str, Any] | None = None,
    provider_id: str | None = None,
    tick_size: Any = None,
    lot_size: Any = None,
    premium_floor_min: float = DEFAULT_PREMIUM_FLOOR_MIN,
    depth_total_min: int = DEFAULT_DEPTH_TOTAL_MIN,
    spread_ratio_max: float = DEFAULT_SPREAD_RATIO_MAX,
    response_efficiency_min: float = DEFAULT_RESPONSE_EFFICIENCY_MIN,
    delta_3: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    response_efficiency: Any = None,
    impact_depth_fraction_one_lot: Any = None,
    packet_gap_ms: Any = None,
) -> dict[str, Any]:
    normalized_side = _normalize_side(side)

    selected_strike_surface = _copy_mapping(strike_surface)
    if not selected_strike_surface and isinstance(dhan_context, Mapping):
        selected_strike_surface = SS.build_classic_strike_surface(
            dhan_context=dhan_context,
            side=normalized_side,
        )

    selected_live = build_live_option_surface(
        side=normalized_side,
        live_source=selected_live_source,
        provider_id=provider_id,
        tick_size=tick_size,
        lot_size=lot_size,
        delta_3=delta_3,
        velocity_ratio=velocity_ratio,
        weighted_ofi_persist=weighted_ofi_persist,
        response_efficiency=response_efficiency,
        impact_depth_fraction_one_lot=impact_depth_fraction_one_lot,
        packet_gap_ms=packet_gap_ms,
        strike=_coalesce(
            selected_strike_surface.get("selected", {}).get("strike")
            if isinstance(selected_strike_surface.get("selected"), Mapping)
            else None,
            selected_strike_surface.get("selected_strike"),
        ),
        instrument_key=_coalesce(
            selected_strike_surface.get("selected", {}).get("instrument_key")
            if isinstance(selected_strike_surface.get("selected"), Mapping)
            else None,
            selected_strike_surface.get("selected_instrument_key"),
        ),
        entry_mode=_coalesce(
            N.ENTRY_MODE_ATM,
            selected_strike_surface.get("selection_mode_hint"),
        ),
    )

    premium_health = build_premium_health_surface(
        ltp=selected_live.get("ltp"),
        spread_ratio=selected_live.get("spread_ratio"),
        depth_total=selected_live.get("depth_total"),
        response_efficiency=selected_live.get("response_efficiency"),
        premium_floor_min=premium_floor_min,
        depth_total_min=depth_total_min,
        spread_ratio_max=spread_ratio_max,
        response_efficiency_min=response_efficiency_min,
    )

    context_surface = build_option_context_surface(
        side=normalized_side,
        dhan_context=dhan_context,
        strike_surface=selected_strike_surface,
        oi_wall_summary=oi_wall_summary,
    )

    return {
        "surface_kind": "classic_option_surface",
        "present": bool(selected_live.get("present")),
        "side": normalized_side,
        "selected_features": selected_live,
        "premium_health": premium_health,
        "context_features": context_surface,
        "strike_surface": selected_strike_surface or None,
        "selected_option_present": bool(selected_live.get("present")),
        "selected_option_tradability_ok": bool(premium_health.get("tradability_ok")),
    }


def build_miso_option_surface(
    *,
    side: str,
    selected_live_source: Mapping[str, Any] | None,
    shadow_live_source: Mapping[str, Any] | None = None,
    dhan_context: Mapping[str, Any] | None = None,
    strike_surface: Mapping[str, Any] | None = None,
    oi_wall_summary: Mapping[str, Any] | None = None,
    provider_id: str | None = None,
    tick_size: Any = None,
    lot_size: Any = None,
    premium_floor_min: float = DEFAULT_PREMIUM_FLOOR_MIN,
    depth_total_min: int = DEFAULT_DEPTH_TOTAL_MIN,
    spread_ratio_max: float = DEFAULT_SPREAD_RATIO_MAX,
    response_efficiency_min: float = DEFAULT_RESPONSE_EFFICIENCY_MIN,
    delta_3: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    response_efficiency: Any = None,
    impact_depth_fraction_one_lot: Any = None,
    packet_gap_ms: Any = None,
    shadow_delta_3: Any = None,
    shadow_velocity_ratio: Any = None,
    shadow_weighted_ofi_persist: Any = None,
    shadow_packet_gap_ms: Any = None,
) -> dict[str, Any]:
    normalized_side = _normalize_side(side)

    selected_strike_surface = _copy_mapping(strike_surface)
    if not selected_strike_surface and isinstance(dhan_context, Mapping):
        selected_strike_surface = SS.build_miso_strike_surface(
            dhan_context=dhan_context,
            side=normalized_side,
        )

    selected_live = build_live_option_surface(
        side=normalized_side,
        live_source=selected_live_source,
        provider_id=provider_id or N.PROVIDER_DHAN,
        tick_size=tick_size,
        lot_size=lot_size,
        delta_3=delta_3,
        velocity_ratio=velocity_ratio,
        weighted_ofi_persist=weighted_ofi_persist,
        response_efficiency=response_efficiency,
        impact_depth_fraction_one_lot=impact_depth_fraction_one_lot,
        packet_gap_ms=packet_gap_ms,
        strike=_coalesce(
            selected_strike_surface.get("selected", {}).get("strike")
            if isinstance(selected_strike_surface.get("selected"), Mapping)
            else None,
            selected_strike_surface.get("selected_strike"),
        ),
        instrument_key=_coalesce(
            selected_strike_surface.get("selected", {}).get("instrument_key")
            if isinstance(selected_strike_surface.get("selected"), Mapping)
            else None,
            selected_strike_surface.get("selected_instrument_key"),
        ),
        entry_mode=N.ENTRY_MODE_DIRECT,
    )

    premium_health = build_premium_health_surface(
        ltp=selected_live.get("ltp"),
        spread_ratio=selected_live.get("spread_ratio"),
        depth_total=selected_live.get("depth_total"),
        response_efficiency=selected_live.get("response_efficiency"),
        premium_floor_min=premium_floor_min,
        depth_total_min=depth_total_min,
        spread_ratio_max=spread_ratio_max,
        response_efficiency_min=response_efficiency_min,
    )

    context_surface = build_option_context_surface(
        side=normalized_side,
        dhan_context=dhan_context,
        strike_surface=selected_strike_surface,
        oi_wall_summary=oi_wall_summary,
    )

    shadow_surface = build_shadow_option_surface(
        side=normalized_side,
        live_source=shadow_live_source,
        provider_id=provider_id or N.PROVIDER_DHAN,
        tick_size=tick_size,
        lot_size=lot_size,
        delta_3=shadow_delta_3,
        velocity_ratio=shadow_velocity_ratio,
        weighted_ofi_persist=shadow_weighted_ofi_persist,
        packet_gap_ms=shadow_packet_gap_ms,
    )

    return {
        "surface_kind": "miso_option_surface",
        "present": bool(selected_live.get("present")),
        "side": normalized_side,
        "selected_features": selected_live,
        "shadow_features": shadow_surface.get("live"),
        "shadow_surface": shadow_surface,
        "premium_health": premium_health,
        "context_features": context_surface,
        "strike_surface": selected_strike_surface or None,
        "selected_option_present": bool(selected_live.get("present")),
        "selected_option_tradability_ok": bool(premium_health.get("tradability_ok")),
    }


__all__ = [
    "OptionCoreError",
    "OPTION_SIDE_IDS",
    "DEFAULT_PREMIUM_FLOOR_MIN",
    "DEFAULT_DEPTH_TOTAL_MIN",
    "DEFAULT_SPREAD_RATIO_MAX",
    "DEFAULT_RESPONSE_EFFICIENCY_MIN",
    "build_live_option_surface",
    "build_premium_health_surface",
    "build_option_context_surface",
    "build_shadow_option_surface",
    "build_classic_option_surface",
    "build_miso_option_surface",
    "context_prefix_for_side",
    "opposing_side",
]

# ===== BATCH8_SHARED_CORE_GUARDS START =====
# Batch 8 freeze-final guard:
# selected live option presence must come from live quote/book truth, not from
# Dhan slow-context strike metadata alone.
#
# Compatibility law:
# option_core._pick() takes a tuple of keys, not variadic keys.

_BATCH8_ORIGINAL_BUILD_LIVE_OPTION_SURFACE = build_live_option_surface


def _batch8_pick(mapping: Mapping[str, Any] | None, *keys: str) -> Any:
    return _pick(mapping, tuple(keys))


def _batch8_option_identity_present(surface: Mapping[str, Any]) -> bool:
    return bool(
        _safe_str(_pick(surface, _INSTRUMENT_KEY_KEYS))
        or _safe_str(_pick(surface, _OPTION_SYMBOL_KEYS))
        or (_safe_int(_pick(surface, _INSTRUMENT_TOKEN_KEYS), 0) or 0) > 0
    )


def _batch8_option_timestamp_present(surface: Mapping[str, Any]) -> bool:
    return bool(
        (_safe_int(_batch8_pick(surface, "ts_event_ns", "exchange_ts_ns", "timestamp_ns"), 0) or 0) > 0
        or (_safe_int(_batch8_pick(surface, "ts_local_ns", "received_ts_ns", "local_ts_ns"), 0) or 0) > 0
        or _safe_bool(_batch8_pick(surface, "timestamp_present", "timestamp_ok"), False)
    )


def build_live_option_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH8_ORIGINAL_BUILD_LIVE_OPTION_SURFACE(*args, **kwargs)
    live_source = _copy_mapping(kwargs.get("live_source"))

    identity_present = _batch8_option_identity_present(live_source) or _batch8_option_identity_present(out)

    ltp = _safe_float(_batch8_pick(out, "ltp"), None)
    best_bid = _safe_float(_batch8_pick(out, "best_bid", "bid"), None)
    best_ask = _safe_float(_batch8_pick(out, "best_ask", "ask"), None)

    quote_present = bool(ltp is not None and ltp > EPSILON)
    book_present = bool(
        best_bid is not None
        and best_ask is not None
        and best_bid > EPSILON
        and best_ask > EPSILON
        and best_ask >= best_bid
    )
    timestamp_present = _batch8_option_timestamp_present(live_source) or _batch8_option_timestamp_present(out)
    live_present = bool(identity_present and (quote_present or book_present))
    stale = bool(_safe_bool(_batch8_pick(out, "stale"), False) or not timestamp_present)

    out["metadata_present"] = bool(identity_present)
    out["quote_present"] = bool(quote_present)
    out["book_present"] = bool(book_present)
    out["timestamp_present"] = bool(timestamp_present)
    out["live_present"] = bool(live_present)
    out["fresh"] = bool(live_present and timestamp_present and not stale)
    out["stale"] = bool(stale)
    out["present"] = bool(live_present)
    if not out["present"]:
        out["tradability_ok"] = False
    return out
# ===== BATCH8_SHARED_CORE_GUARDS END =====
