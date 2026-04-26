from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/miso_microstructure.py

Pure MISO live-option microstructure helpers.

Ownership
---------
This module owns only deterministic computation of MISO microstructure support
facts from already-produced live option/shadow surfaces. It does not read/write
Redis, mutate strategy state, publish decisions, call risk, call execution, or
touch broker APIs.

Freeze law
----------
- No proxy-only MISO burst pass.
- Missing tick/trade rows fail closed.
- Shadow support must come from actual shadow live data, not monitored-row count.
- burst_event_id is deterministic from side, instrument/strike, and burst window.
"""

from math import isfinite
from typing import Any, Final, Mapping, Sequence

EPSILON: Final[float] = 1e-9

DEFAULT_AGGR_WINDOW_MS: Final[float] = 600.0
DEFAULT_TAPE_WINDOW_MS: Final[float] = 600.0
DEFAULT_PERSISTENCE_WINDOW_MS: Final[float] = 600.0
DEFAULT_AGGRESSIVE_FLOW_RATIO_MIN: Final[float] = 0.58
DEFAULT_SPEED_OF_TAPE_MIN: Final[float] = 3.0
DEFAULT_IMBALANCE_PERSIST_MIN: Final[float] = 0.60
DEFAULT_QUEUE_RELOAD_RATIO_MAX: Final[float] = 0.65
DEFAULT_SHADOW_SUPPORT_MIN: Final[int] = 1
DEFAULT_BIN_COUNT: Final[int] = 3


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _pick(mapping: Mapping[str, Any] | None, *keys: str) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _nested(root: Any, *path: str, default: Any = None) -> Any:
    cur = root
    for key in path:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


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
    if text in {"1", "true", "yes", "y", "on", "ok", "pass", "passed"}:
        return True
    if text in {"0", "false", "no", "n", "off", "fail", "failed"}:
        return False
    return default


def _threshold(thresholds: Mapping[str, Any] | None, *keys: str, default: float) -> float:
    mapping = _as_mapping(thresholds)
    for key in keys:
        if key in mapping:
            return _safe_float(mapping.get(key), default)
    return default


def _tick_rows(option_features: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    raw = _as_mapping(option_features.get("raw"))
    micro = _as_mapping(option_features.get("microstructure"))
    candidates = (
        option_features.get("recent_ticks"),
        option_features.get("trade_ticks"),
        option_features.get("tick_buffer"),
        option_features.get("ticks"),
        option_features.get("recent_trade_ticks"),
        micro.get("recent_ticks"),
        micro.get("trade_ticks"),
        raw.get("recent_ticks"),
        raw.get("trade_ticks"),
        raw.get("tick_buffer"),
        raw.get("ticks"),
        raw.get("recent_trade_ticks"),
    )
    out: list[Mapping[str, Any]] = []
    for candidate in candidates:
        for row in _as_sequence(candidate):
            if isinstance(row, Mapping):
                out.append(row)
        if out:
            break
    return tuple(out)


def _row_ts_ms(row: Mapping[str, Any]) -> int:
    for key in (
        "ts_ms",
        "ltt_ms",
        "trade_ts_ms",
        "exchange_ts_ms",
        "local_ts_ms",
        "timestamp_ms",
    ):
        value = _safe_int(row.get(key), 0)
        if value > 0:
            return value

    for key in (
        "ts_event_ns",
        "ltt_ns",
        "last_trade_ts_ns",
        "trade_ts_ns",
        "exchange_ts_ns",
        "local_ts_ns",
        "timestamp_ns",
    ):
        value = _safe_int(row.get(key), 0)
        if value > 0:
            return value // 1_000_000

    return 0


def _row_ltp(row: Mapping[str, Any]) -> float | None:
    return _safe_float_or_none(_pick(row, "ltp", "price", "last_price", "lastPrice"))


def _row_qty(row: Mapping[str, Any]) -> float:
    qty = _safe_float(_pick(row, "ltq", "qty", "quantity", "last_traded_quantity", "lastTradeQty"), 1.0)
    return max(qty, 1.0)


def _row_bid(row: Mapping[str, Any], default: float | None) -> float | None:
    return _safe_float_or_none(_pick(row, "best_bid", "bid", "bestBid", "best_bid_price")) or default


def _row_ask(row: Mapping[str, Any], default: float | None) -> float | None:
    return _safe_float_or_none(_pick(row, "best_ask", "ask", "bestAsk", "best_ask_price")) or default


def _row_bid_qty(row: Mapping[str, Any], default: float | None) -> float | None:
    return _safe_float_or_none(_pick(row, "bid_qty_5", "bid_qty", "best_bid_qty", "bid_quantity")) or default


def _row_ask_qty(row: Mapping[str, Any], default: float | None) -> float | None:
    return _safe_float_or_none(_pick(row, "ask_qty_5", "ask_qty", "best_ask_qty", "ask_quantity")) or default


def _is_call(side: str) -> bool:
    return str(side).strip().upper() in {"CALL", "CE", "C"}


def _direction_sign(side: str) -> int:
    return 1 if _is_call(side) else -1


def _infer_favorable_trade(
    *,
    row: Mapping[str, Any],
    previous_ltp: float | None,
    side: str,
    default_bid: float | None,
    default_ask: float | None,
) -> bool:
    ltp = _row_ltp(row)
    if ltp is None:
        return False

    bid = _row_bid(row, default_bid)
    ask = _row_ask(row, default_ask)
    explicit_side = _safe_str(_pick(row, "aggressor_side", "trade_side", "side")).upper()

    if explicit_side in {"BUY", "B", "ASK", "TAKER_BUY"}:
        buy_aggressive = True
    elif explicit_side in {"SELL", "S", "BID", "TAKER_SELL"}:
        buy_aggressive = False
    elif ask is not None and ltp >= ask - EPSILON:
        buy_aggressive = True
    elif bid is not None and ltp <= bid + EPSILON:
        buy_aggressive = False
    elif previous_ltp is not None:
        buy_aggressive = ltp > previous_ltp + EPSILON
    else:
        buy_aggressive = False

    # CE favorable = buy aggression. PE favorable = sell aggression.
    return buy_aggressive if _is_call(side) else not buy_aggressive


def _window_rows(rows: tuple[Mapping[str, Any], ...], window_ms: float) -> tuple[Mapping[str, Any], ...]:
    stamped = [(row, _row_ts_ms(row)) for row in rows]
    stamped = [(row, ts) for row, ts in stamped if ts > 0]
    if not stamped:
        return ()
    end = max(ts for _, ts in stamped)
    start = end - max(int(window_ms), 1)
    return tuple(row for row, ts in stamped if ts >= start)


def _window_bounds(rows: tuple[Mapping[str, Any], ...]) -> tuple[int, int]:
    stamps = [_row_ts_ms(row) for row in rows if _row_ts_ms(row) > 0]
    if not stamps:
        return (0, 0)
    return (min(stamps), max(stamps))


def _aggression_stats(
    *,
    rows: tuple[Mapping[str, Any], ...],
    side: str,
    default_bid: float | None,
    default_ask: float | None,
) -> dict[str, Any]:
    favorable_qty = 0.0
    unfavorable_qty = 0.0
    favorable_count = 0
    unfavorable_count = 0
    previous_ltp: float | None = None

    for row in rows:
        favorable = _infer_favorable_trade(
            row=row,
            previous_ltp=previous_ltp,
            side=side,
            default_bid=default_bid,
            default_ask=default_ask,
        )
        qty = _row_qty(row)
        if favorable:
            favorable_qty += qty
            favorable_count += 1
        else:
            unfavorable_qty += qty
            unfavorable_count += 1
        ltp = _row_ltp(row)
        if ltp is not None:
            previous_ltp = ltp

    total_qty = favorable_qty + unfavorable_qty
    total_count = favorable_count + unfavorable_count
    ratio = favorable_qty / max(total_qty, EPSILON) if total_qty > 0 else 0.0
    return {
        "favorable_qty": favorable_qty,
        "unfavorable_qty": unfavorable_qty,
        "favorable_count": favorable_count,
        "unfavorable_count": unfavorable_count,
        "total_qty": total_qty,
        "total_count": total_count,
        "aggressive_flow_ratio": ratio,
    }


def _speed_of_tape(rows: tuple[Mapping[str, Any], ...], favorable_count: int, window_ms: float) -> float:
    start, end = _window_bounds(rows)
    elapsed_ms = max(float(end - start), float(window_ms), 1.0)
    return favorable_count / max(elapsed_ms / 1000.0, EPSILON)


def _imbalance_persistence(
    *,
    rows: tuple[Mapping[str, Any], ...],
    side: str,
    default_bid: float | None,
    default_ask: float | None,
    bin_count: int = DEFAULT_BIN_COUNT,
) -> float:
    start, end = _window_bounds(rows)
    if not rows or start <= 0 or end <= start:
        return 0.0

    bins = max(int(bin_count), 1)
    width = max((end - start) / bins, 1.0)
    favorable_bins = 0
    active_bins = 0

    for bin_index in range(bins):
        lo = start + int(bin_index * width)
        hi = start + int((bin_index + 1) * width) if bin_index < bins - 1 else end + 1
        bin_rows = tuple(row for row in rows if lo <= _row_ts_ms(row) < hi)
        if not bin_rows:
            continue
        stats = _aggression_stats(
            rows=bin_rows,
            side=side,
            default_bid=default_bid,
            default_ask=default_ask,
        )
        active_bins += 1
        if stats["aggressive_flow_ratio"] >= 0.50 and stats["favorable_count"] > 0:
            favorable_bins += 1

    if active_bins <= 0:
        return 0.0
    return favorable_bins / active_bins


def _queue_reload_blocked(
    *,
    rows: tuple[Mapping[str, Any], ...],
    side: str,
    option_features: Mapping[str, Any],
    thresholds: Mapping[str, Any] | None,
) -> tuple[bool, float]:
    # Explicit veto flags always win.
    explicit_ask = _safe_bool(_pick(option_features, "ask_reloaded", "queue_reload_veto", "ask_reload_blocked"), False)
    explicit_bid = _safe_bool(_pick(option_features, "bid_reloaded", "bid_reload_blocked"), False)

    if _is_call(side) and explicit_ask:
        return True, 1.0
    if not _is_call(side) and explicit_bid:
        return True, 1.0

    if len(rows) < 2:
        return False, 0.0

    reload_count = 0
    comparable_count = 0

    prev_ask_qty: float | None = None
    prev_bid_qty: float | None = None
    prev_ask: float | None = None
    prev_bid: float | None = None

    default_ask_qty = _safe_float_or_none(_pick(option_features, "ask_qty_5", "ask_qty"))
    default_bid_qty = _safe_float_or_none(_pick(option_features, "bid_qty_5", "bid_qty"))
    default_ask = _safe_float_or_none(_pick(option_features, "best_ask", "ask"))
    default_bid = _safe_float_or_none(_pick(option_features, "best_bid", "bid"))

    for row in rows:
        ask_qty = _row_ask_qty(row, default_ask_qty)
        bid_qty = _row_bid_qty(row, default_bid_qty)
        ask = _row_ask(row, default_ask)
        bid = _row_bid(row, default_bid)

        if _is_call(side):
            if prev_ask_qty is not None and ask_qty is not None and prev_ask is not None and ask is not None:
                comparable_count += 1
                if ask_qty > prev_ask_qty and ask <= prev_ask + EPSILON:
                    reload_count += 1
        else:
            if prev_bid_qty is not None and bid_qty is not None and prev_bid is not None and bid is not None:
                comparable_count += 1
                if bid_qty > prev_bid_qty and bid >= prev_bid - EPSILON:
                    reload_count += 1

        prev_ask_qty = ask_qty
        prev_bid_qty = bid_qty
        prev_ask = ask
        prev_bid = bid

    ratio = reload_count / max(comparable_count, 1)
    max_ratio = _threshold(thresholds, "QUEUE_RELOAD_RATIO_MAX", "MISO_QUEUE_RELOAD_RATIO_MAX", default=DEFAULT_QUEUE_RELOAD_RATIO_MAX)
    return bool(comparable_count > 0 and ratio >= max_ratio), ratio


def _shadow_rows_from_surface(
    *,
    shadow_features: Mapping[str, Any],
    strike_surface: Mapping[str, Any],
    shadow_rows: Sequence[Mapping[str, Any]] | None,
) -> tuple[Mapping[str, Any], ...]:
    out: list[Mapping[str, Any]] = []

    if isinstance(shadow_rows, Sequence) and not isinstance(shadow_rows, (str, bytes, bytearray)):
        out.extend(row for row in shadow_rows if isinstance(row, Mapping))

    shadow_surface = _as_mapping(_pick(shadow_features, "shadow_surface"))
    live = _as_mapping(_pick(shadow_features, "live"))
    if live:
        out.append(live)
    if shadow_features:
        out.append(shadow_features)

    strike_shadow = _pick(strike_surface, "shadow")
    if isinstance(strike_shadow, Sequence) and not isinstance(strike_shadow, (str, bytes, bytearray)):
        out.extend(row for row in strike_shadow if isinstance(row, Mapping))

    # Deduplicate by instrument/strike where possible.
    seen: set[str] = set()
    deduped: list[Mapping[str, Any]] = []
    for row in out:
        key = (
            _safe_str(_pick(row, "instrument_key", "security_id", "token"))
            or _safe_str(_pick(row, "strike"))
            or str(id(row))
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    return tuple(deduped)


def _shadow_support(
    *,
    side: str,
    shadow_features: Mapping[str, Any],
    strike_surface: Mapping[str, Any],
    shadow_rows: Sequence[Mapping[str, Any]] | None,
    thresholds: Mapping[str, Any] | None,
) -> dict[str, Any]:
    rows = _shadow_rows_from_surface(
        shadow_features=shadow_features,
        strike_surface=strike_surface,
        shadow_rows=shadow_rows,
    )
    direction = _direction_sign(side)
    support_count = 0
    live_count = 0

    for row in rows:
        live_present = _safe_bool(_pick(row, "present", "live_present", "fresh"), False)
        has_identity = bool(
            _safe_str(_pick(row, "instrument_key", "security_id", "token", "option_symbol"))
            or _safe_float_or_none(_pick(row, "strike")) is not None
        )
        delta = _safe_float(_pick(row, "delta_3", "opt_delta_3", "price_delta_3"), 0.0)
        ofi = _safe_float(_pick(row, "weighted_ofi_persist", "weighted_ofi", "ofi", "ofi_ratio"), 0.5)
        explicit_support = _safe_bool(_pick(row, "shadow_support_ok", "support_ok", "spillover_support"), False)

        if live_present or has_identity:
            live_count += 1

        directional = (delta * direction) > 0 or (ofi >= 0.50 if _is_call(side) else ofi <= 0.50)
        if explicit_support or ((live_present or has_identity) and directional):
            support_count += 1

    min_support = int(_threshold(thresholds, "SHADOW_SUPPORT_MIN", "MISO_SHADOW_SUPPORT_MIN", default=float(DEFAULT_SHADOW_SUPPORT_MIN)))
    return {
        "shadow_support_count": support_count,
        "shadow_live_count": live_count,
        "shadow_support_ok": bool(support_count >= max(min_support, 1)),
        "shadow_rows_seen": len(rows),
    }


def _burst_event_id(
    *,
    side: str,
    option_features: Mapping[str, Any],
    selected_strike: Mapping[str, Any],
    window_start_ms: int,
    window_end_ms: int,
) -> str | None:
    if window_start_ms <= 0 or window_end_ms <= 0:
        return None

    instrument = (
        _safe_str(_pick(option_features, "instrument_key", "security_id", "token", "option_symbol"))
        or _safe_str(_pick(selected_strike, "instrument_key", "security_id", "token", "option_symbol"))
    )
    strike = (
        _safe_str(_pick(option_features, "strike"))
        or _safe_str(_pick(selected_strike, "strike"))
        or "UNKNOWN_STRIKE"
    )
    if not instrument and strike == "UNKNOWN_STRIKE":
        return None

    return f"MISO|{side.upper()}|{instrument or strike}|{strike}|{int(window_start_ms)}|{int(window_end_ms)}"


def build_miso_microstructure_surface(
    *,
    branch_id: str,
    side: str,
    option_features: Mapping[str, Any],
    shadow_features: Mapping[str, Any] | None = None,
    strike_surface: Mapping[str, Any] | None = None,
    selected_strike: Mapping[str, Any] | None = None,
    shadow_rows: Sequence[Mapping[str, Any]] | None = None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute MISO microstructure facts from live option tick buffers."""
    opt = _as_mapping(option_features)
    shadow = _as_mapping(shadow_features)
    strike = _as_mapping(strike_surface)
    selected = _as_mapping(selected_strike)

    aggr_window_ms = _threshold(thresholds, "AGGR_WINDOW_MS", "MISO_AGGR_WINDOW_MS", default=DEFAULT_AGGR_WINDOW_MS)
    tape_window_ms = _threshold(thresholds, "TAPE_WINDOW_MS", "MISO_TAPE_WINDOW_MS", default=DEFAULT_TAPE_WINDOW_MS)
    persistence_window_ms = _threshold(thresholds, "PERSISTENCE_WINDOW_MS", "MISO_PERSISTENCE_WINDOW_MS", default=DEFAULT_PERSISTENCE_WINDOW_MS)

    flow_ratio_min = _threshold(thresholds, "AGGRESSIVE_FLOW_RATIO_MIN", "MISO_AGGRESSIVE_FLOW_RATIO_MIN", default=DEFAULT_AGGRESSIVE_FLOW_RATIO_MIN)
    speed_min = _threshold(thresholds, "SPEED_OF_TAPE_MIN", "MISO_SPEED_OF_TAPE_MIN", default=DEFAULT_SPEED_OF_TAPE_MIN)
    persist_min = _threshold(thresholds, "IMBALANCE_PERSIST_MIN", "MISO_IMBALANCE_PERSIST_MIN", default=DEFAULT_IMBALANCE_PERSIST_MIN)

    rows = _tick_rows(opt)
    flow_rows = _window_rows(rows, aggr_window_ms)
    tape_rows = _window_rows(rows, tape_window_ms)
    persist_rows = _window_rows(rows, persistence_window_ms)

    default_bid = _safe_float_or_none(_pick(opt, "best_bid", "bid"))
    default_ask = _safe_float_or_none(_pick(opt, "best_ask", "ask"))

    flow_stats = _aggression_stats(
        rows=flow_rows,
        side=side,
        default_bid=default_bid,
        default_ask=default_ask,
    )
    tape_stats = _aggression_stats(
        rows=tape_rows,
        side=side,
        default_bid=default_bid,
        default_ask=default_ask,
    )
    speed = _speed_of_tape(tape_rows, int(tape_stats["favorable_count"]), tape_window_ms)
    persistence_score = _imbalance_persistence(
        rows=persist_rows,
        side=side,
        default_bid=default_bid,
        default_ask=default_ask,
    )
    queue_blocked, queue_score = _queue_reload_blocked(
        rows=flow_rows or rows,
        side=side,
        option_features=opt,
        thresholds=thresholds,
    )
    shadow_support = _shadow_support(
        side=side,
        shadow_features=shadow,
        strike_surface=strike,
        shadow_rows=shadow_rows,
        thresholds=thresholds,
    )

    window_start_ms, window_end_ms = _window_bounds(flow_rows or rows)
    event_id = _burst_event_id(
        side=side,
        option_features=opt,
        selected_strike=selected,
        window_start_ms=window_start_ms,
        window_end_ms=window_end_ms,
    )

    aggression_ok = bool(flow_stats["total_count"] > 0 and flow_stats["aggressive_flow_ratio"] >= flow_ratio_min)
    tape_speed_ok = bool(tape_stats["total_count"] > 0 and speed >= speed_min)
    imbalance_persist_ok = bool(persistence_score >= persist_min)
    live_flow_ok = bool(aggression_ok and flow_stats["favorable_qty"] > 0)

    return {
        "microstructure_present": bool(rows),
        "tick_count": len(rows),
        "aggr_tick_count": len(flow_rows),
        "tape_tick_count": len(tape_rows),
        "persistence_tick_count": len(persist_rows),
        "window_start_ms": window_start_ms,
        "window_end_ms": window_end_ms,
        "aggressive_flow_ratio": float(flow_stats["aggressive_flow_ratio"]),
        "aggressive_flow_qty": float(flow_stats["favorable_qty"]),
        "counter_flow_qty": float(flow_stats["unfavorable_qty"]),
        "aggressive_trade_count": int(flow_stats["favorable_count"]),
        "counter_trade_count": int(flow_stats["unfavorable_count"]),
        "speed_of_tape": float(speed),
        "imbalance_persist_score": float(persistence_score),
        "queue_reload_blocked": bool(queue_blocked),
        "queue_reload_clear": not bool(queue_blocked),
        "queue_reload_score": float(queue_score),
        "shadow_support_count": int(shadow_support["shadow_support_count"]),
        "shadow_live_count": int(shadow_support["shadow_live_count"]),
        "shadow_rows_seen": int(shadow_support["shadow_rows_seen"]),
        "shadow_support_ok": bool(shadow_support["shadow_support_ok"]),
        "aggression_ok": aggression_ok,
        "tape_speed_ok": tape_speed_ok,
        "imbalance_persist_ok": imbalance_persist_ok,
        "live_flow_ok": live_flow_ok,
        "burst_event_id": event_id,
        "burst_event_id_valid": bool(event_id),
    }


__all__ = [
    "build_miso_microstructure_surface",
]
