from __future__ import annotations

"""
app/mme_scalpx/research_capture/enricher.py

Frozen lightweight enrichment layer for the MME research data capture chapter.

Purpose
-------
This module owns cheap, deterministic, broker-agnostic live enrichment applied
after normalization. It adds research-grade lightweight derived metrics to an
already normalized CaptureRecord without introducing heavy analytics or
production-doctrine changes.

Owns
----
- same-instrument history filtering
- lightweight rolling metric computation
- controlled enrichment of CaptureRecord.live_metrics
- sequential enrichment helpers for record streams

Does not own
------------
- broker IO
- Redis IO
- parquet IO
- archive writing
- heavy offline analytics
- production strategy doctrine

Design laws
-----------
- raw record remains the primary truth surface
- enrichment must stay lightweight and deterministic
- heavy research analytics belong offline, not here
- enrichment must preserve the canonical schema and model contracts
- missing inputs should degrade gracefully, not fabricate precision
"""

from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.research_capture.contracts import FieldLayer
from app.mme_scalpx.research_capture.models import CaptureRecord, FieldBundle, RuntimeAuditState


def _ensure_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError("bool is not a valid numeric value here")
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"Expected numeric value, got {type(value).__name__}")


def _safe_mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return mean(values)


def _safe_std(values: Sequence[float]) -> float | None:
    n = len(values)
    if n < 2:
        return None
    avg = sum(values) / n
    variance = sum((x - avg) ** 2 for x in values) / n
    return sqrt(variance)


def _safe_div(numerator: float | int, denominator: float | int, default: float | None = None) -> float | None:
    denominator_f = float(denominator)
    if denominator_f == 0.0:
        return default
    return float(numerator) / denominator_f


def _last_n(values: Sequence[Any], n: int) -> tuple[Any, ...]:
    if n <= 0:
        return ()
    if len(values) <= n:
        return tuple(values)
    return tuple(values[-n:])


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _nearest_history_at_or_before_lookback(
    current_exchange_ts: float,
    history_records: Sequence[CaptureRecord],
    *,
    seconds_lookback: float,
) -> CaptureRecord | None:
    """
    Return the most recent history record that is at least `seconds_lookback`
    older than the current record, or None if unavailable.
    """
    threshold = current_exchange_ts - seconds_lookback
    candidates = [record for record in history_records if record.timing.exchange_ts <= threshold]
    if not candidates:
        return None
    return candidates[-1]


def _matching_history(current: CaptureRecord, history: Sequence[CaptureRecord]) -> tuple[CaptureRecord, ...]:
    """
    Keep only records for the same instrument/session/dataset, sorted by exchange_ts/event_seq.
    """
    filtered = [
        record
        for record in history
        if record.dataset == current.dataset
        and record.timing.session_date == current.timing.session_date
        and record.instrument.instrument_token == current.instrument.instrument_token
    ]
    filtered.sort(key=lambda record: (record.timing.exchange_ts, record.timing.event_seq))
    return tuple(filtered)


def _record_price(record: CaptureRecord) -> float:
    return float(record.market.price if record.market and record.market.price is not None else record.market.ltp)


def _record_volume(record: CaptureRecord) -> int:
    return int(record.market.volume if record.market else 0)


def _record_oi(record: CaptureRecord) -> int | None:
    if record.market is None:
        return None
    return record.market.oi


def _record_best_bid(record: CaptureRecord) -> float | None:
    return None if record.market is None else record.market.best_bid


def _record_best_ask(record: CaptureRecord) -> float | None:
    return None if record.market is None else record.market.best_ask


def _record_best_bid_qty(record: CaptureRecord) -> int | None:
    return None if record.market is None else record.market.best_bid_qty


def _record_best_ask_qty(record: CaptureRecord) -> int | None:
    return None if record.market is None else record.market.best_ask_qty


def _record_sum_bid(record: CaptureRecord) -> int:
    if record.market is None:
        return 0
    return int(sum(record.market.bid_qty))


def _record_sum_ask(record: CaptureRecord) -> int:
    if record.market is None:
        return 0
    return int(sum(record.market.ask_qty))


def _record_depth_notional(record: CaptureRecord, *, side: str, levels: int) -> float:
    if record.market is None:
        return 0.0
    if side == "bid":
        prices = record.market.bid_prices[:levels]
        qtys = record.market.bid_qty[:levels]
    else:
        prices = record.market.ask_prices[:levels]
        qtys = record.market.ask_qty[:levels]
    return float(sum(price * qty for price, qty in zip(prices, qtys)))


def _record_queue_delta(record: CaptureRecord) -> int:
    return _record_sum_bid(record) - _record_sum_ask(record)


def _delta_series_from_cumulative(values: Sequence[int]) -> tuple[int, ...]:
    """
    Convert a cumulative series into non-negative deltas.
    If the series decreases, fall back to zero delta for that step.
    """
    if not values:
        return ()
    deltas: list[int] = []
    prev = values[0]
    for value in values[1:]:
        if value >= prev:
            deltas.append(value - prev)
        else:
            deltas.append(0)
        prev = value
    return tuple(deltas)


def _ema(values: Sequence[float], *, period: int) -> float | None:
    if not values:
        return None
    alpha = 2.0 / (period + 1.0)
    current = values[0]
    for value in values[1:]:
        current = alpha * value + (1.0 - alpha) * current
    return current


def _slope_from_tail(values: Sequence[float], *, tail_points: int) -> float | None:
    if len(values) < max(2, tail_points):
        return None
    tail = _last_n(values, tail_points)
    start = float(tail[0])
    end = float(tail[-1])
    return (end - start) / max(len(tail) - 1, 1)


def _percentile(sorted_values: Sequence[float], q: float) -> float | None:
    if not sorted_values:
        return None
    if q <= 0:
        return float(sorted_values[0])
    if q >= 1:
        return float(sorted_values[-1])
    idx = q * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return float(sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac)


def _make_runtime_audit_with_integrity_flags(
    runtime_audit: RuntimeAuditState,
    integrity_flags: Sequence[str],
) -> RuntimeAuditState:
    """
    Rebuild RuntimeAuditState with updated integrity flags while preserving all other fields.
    """
    deduped_flags: tuple[str, ...] = tuple(dict.fromkeys(str(flag) for flag in integrity_flags))
    return RuntimeAuditState(
        is_stale_tick=runtime_audit.is_stale_tick,
        stale_reason=runtime_audit.stale_reason,
        missing_depth_flag=runtime_audit.missing_depth_flag,
        missing_oi_flag=runtime_audit.missing_oi_flag,
        thin_book=runtime_audit.thin_book,
        book_is_thin=runtime_audit.book_is_thin,
        crossed_book_flag=runtime_audit.crossed_book_flag,
        locked_book_flag=runtime_audit.locked_book_flag,
        integrity_flags=deduped_flags,
        fallback_used_flag=runtime_audit.fallback_used_flag,
        fallback_source=runtime_audit.fallback_source,
        schema_version=runtime_audit.schema_version,
        normalization_version=runtime_audit.normalization_version,
        derived_version=runtime_audit.derived_version,
        calendar_version=runtime_audit.calendar_version,
        heartbeat_status=runtime_audit.heartbeat_status,
        reconnect_count=runtime_audit.reconnect_count,
        last_reconnect_reason=runtime_audit.last_reconnect_reason,
        gpu_fallback=runtime_audit.gpu_fallback,
        cpu_mode_flag=runtime_audit.cpu_mode_flag,
        latency_ns=runtime_audit.latency_ns,
        gap_from_prev_tick_ms=runtime_audit.gap_from_prev_tick_ms,
    )


@dataclass(frozen=True, slots=True)
class EnrichmentConfig:
    """
    Lightweight enrichment settings.

    These are intentionally conservative because this module is not meant to
    perform heavy research analytics.
    """
    nof_ema_period: int = 20
    nof_slope_tail: int = 4
    cvd_slope_short_tail: int = 4
    cvd_slope_medium_tail: int = 6
    cvd_slope_long_tail: int = 11
    bollinger_window: int = 20
    bollinger_std_mult: float = 2.0
    recent_window_records: int = 20
    neutral_nof_low: float = 0.98
    neutral_nof_high: float = 1.02
    vwap_band_pct: float = 0.002
    micro_vol_window: int = 20
    volume_ma_short: int = 10
    volume_ma_long: int = 20
    spike_window_short: int = 5
    spike_window_medium: int = 10
    spike_window_long: int = 20
    option_delta_width_multiplier: float = 10.0

    def __post_init__(self) -> None:
        for name in (
            "nof_ema_period",
            "nof_slope_tail",
            "cvd_slope_short_tail",
            "cvd_slope_medium_tail",
            "cvd_slope_long_tail",
            "bollinger_window",
            "recent_window_records",
            "micro_vol_window",
            "volume_ma_short",
            "volume_ma_long",
            "spike_window_short",
            "spike_window_medium",
            "spike_window_long",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive int")

        for name in ("bollinger_std_mult", "vwap_band_pct", "option_delta_width_multiplier"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive float")

        if not (0.0 < self.neutral_nof_low <= self.neutral_nof_high):
            raise ValueError("neutral NOF bounds are invalid")


DEFAULT_ENRICHMENT_CONFIG = EnrichmentConfig()


def build_lightweight_enrichment_bundle(
    record: CaptureRecord,
    *,
    history: Sequence[CaptureRecord] = (),
    config: EnrichmentConfig = DEFAULT_ENRICHMENT_CONFIG,
) -> FieldBundle:
    """
    Build the lightweight live-derived enrichment bundle for one normalized record.

    Only cheap, deterministic metrics belong here.
    """
    if record.market is None:
        raise ValueError("enrichment requires record.market to be present")

    matching_history = _matching_history(record, history)
    history_plus_current = matching_history + (record,)

    prices = [_record_price(r) for r in history_plus_current]
    current_price = prices[-1]
    current_exchange_ts = record.timing.exchange_ts

    volumes_cumulative = [_record_volume(r) for r in history_plus_current]
    volume_deltas = _delta_series_from_cumulative(volumes_cumulative)

    oi_values = [_record_oi(r) for r in history_plus_current if _record_oi(r) is not None]
    current_oi = _record_oi(record)

    sum_bid = _record_sum_bid(record)
    sum_ask = _record_sum_ask(record)
    current_nof = _safe_div(sum_bid, max(sum_ask, 1), default=0.0)
    nof_series = [
        _safe_div(_record_sum_bid(r), max(_record_sum_ask(r), 1), default=0.0) or 0.0
        for r in history_plus_current
    ]

    queue_delta_series = [_record_queue_delta(r) for r in history_plus_current]
    cvd_series: list[float] = []
    running_cvd = 0.0
    for delta in queue_delta_series:
        running_cvd += float(delta)
        cvd_series.append(running_cvd)

    spreads: list[float] = []
    for r in history_plus_current:
        bid = _record_best_bid(r)
        ask = _record_best_ask(r)
        if bid is not None and ask is not None:
            spreads.append(max(ask - bid, 0.0))
        else:
            spreads.append(0.0)

    current_best_bid = record.market.best_bid
    current_best_ask = record.market.best_ask
    best_bid_qty = record.market.best_bid_qty or 0
    best_ask_qty = record.market.best_ask_qty or 0
    current_spread = spreads[-1]
    current_mid = record.market.mid_price or current_price

    current_record_delta_volume = volume_deltas[-1] if volume_deltas else 0
    delta_volume_series = tuple(volume_deltas)

    current_history_prev = matching_history[-1] if matching_history else None
    record_1s = _nearest_history_at_or_before_lookback(current_exchange_ts, matching_history, seconds_lookback=1.0)
    record_5s = _nearest_history_at_or_before_lookback(current_exchange_ts, matching_history, seconds_lookback=5.0)
    record_1m = _nearest_history_at_or_before_lookback(current_exchange_ts, matching_history, seconds_lookback=60.0)
    record_5m = _nearest_history_at_or_before_lookback(current_exchange_ts, matching_history, seconds_lookback=300.0)

    if record_5m is None and matching_history:
        recent_5m_records = matching_history
    else:
        recent_5m_records = tuple(
            r for r in history_plus_current
            if r.timing.exchange_ts >= current_exchange_ts - 300.0
        )

    session_high = max(prices)
    session_low = min(prices)
    day_open_price = prices[0]
    recent_prices = list(_last_n(prices, config.recent_window_records))
    recent_high = max(recent_prices) if recent_prices else current_price
    recent_low = min(recent_prices) if recent_prices else current_price

    bb_window_prices = list(_last_n(prices, config.bollinger_window))
    bb_mid = _safe_mean(bb_window_prices)
    bb_std = _safe_std(bb_window_prices)
    bb_upper = bb_mid + config.bollinger_std_mult * bb_std if bb_mid is not None and bb_std is not None else None
    bb_lower = bb_mid - config.bollinger_std_mult * bb_std if bb_mid is not None and bb_std is not None else None
    bb_width = (bb_upper - bb_lower) if bb_upper is not None and bb_lower is not None else None
    bb_width_ratio = _safe_div(bb_width, bb_mid, default=None) if bb_width is not None and bb_mid is not None else None

    micro_vol_prices = list(_last_n(prices, config.micro_vol_window))
    micro_std = _safe_std(micro_vol_prices)
    mu_vol_pct = _safe_div(micro_std or 0.0, current_price, default=None)

    # Per-tick price deltas
    prev_price = _record_price(current_history_prev) if current_history_prev is not None else None
    price_delta_1tick = current_price - prev_price if prev_price is not None else None
    price_delta_1s = current_price - _record_price(record_1s) if record_1s is not None else None
    price_delta_5s = current_price - _record_price(record_5s) if record_5s is not None else None

    # Book metrics
    queue_imbalance_l1 = _safe_div(best_bid_qty - best_ask_qty, best_bid_qty + best_ask_qty, default=0.0)
    top5_bid_qty = int(sum(record.market.bid_qty[:5]))
    top5_ask_qty = int(sum(record.market.ask_qty[:5]))
    queue_imbalance_l5 = _safe_div(top5_bid_qty - top5_ask_qty, top5_bid_qty + top5_ask_qty, default=0.0)

    book_pressure_ratio_5 = _safe_div(top5_bid_qty, max(top5_ask_qty, 1), default=0.0)
    book_pressure_ratio_10 = _safe_div(
        sum(record.market.bid_qty[:10]),
        max(sum(record.market.ask_qty[:10]), 1),
        default=0.0,
    )

    top_bid_notional = (current_best_bid or current_price) * best_bid_qty
    top_ask_notional = (current_best_ask or current_price) * best_ask_qty
    book_notional_bid_5 = _record_depth_notional(record, side="bid", levels=5)
    book_notional_ask_5 = _record_depth_notional(record, side="ask", levels=5)
    book_notional_bid_10 = _record_depth_notional(record, side="bid", levels=10)
    book_notional_ask_10 = _record_depth_notional(record, side="ask", levels=10)

    nof_ema20 = _ema(nof_series, period=config.nof_ema_period)
    nof_slope3 = _slope_from_tail(nof_series, tail_points=config.nof_slope_tail)
    cvd = int(cvd_series[-1])
    cvd_slope_3 = _slope_from_tail(cvd_series, tail_points=config.cvd_slope_short_tail)
    cvd_slope_5 = _slope_from_tail(cvd_series, tail_points=config.cvd_slope_medium_tail)
    cvd_slope_10 = _slope_from_tail(cvd_series, tail_points=config.cvd_slope_long_tail)

    trade_through_up = False
    trade_through_down = False
    if current_history_prev is not None:
        prev_best_ask = _record_best_ask(current_history_prev)
        prev_best_bid = _record_best_bid(current_history_prev)
        if prev_best_ask is not None:
            trade_through_up = current_price > prev_best_ask
        if prev_best_bid is not None:
            trade_through_down = current_price < prev_best_bid

    bbid_stepdowns_10 = 0
    bask_stepups_10 = 0
    recent_transitions = _last_n(history_plus_current, 11)
    for prev, curr in zip(recent_transitions[:-1], recent_transitions[1:]):
        prev_bid = _record_best_bid(prev)
        curr_bid = _record_best_bid(curr)
        prev_ask = _record_best_ask(prev)
        curr_ask = _record_best_ask(curr)
        if prev_bid is not None and curr_bid is not None and curr_bid < prev_bid:
            bbid_stepdowns_10 += 1
        if prev_ask is not None and curr_ask is not None and curr_ask > prev_ask:
            bask_stepups_10 += 1

    spread_widening_10 = current_spread > max(_last_n(spreads[:-1], 10), default=current_spread)
    nof_neutral_ticks = sum(
        1 for value in _last_n(nof_series, config.recent_window_records)
        if config.neutral_nof_low <= value <= config.neutral_nof_high
    )

    # VWAP on delta-volume basis when possible; fallback to simple price mean.
    weighted_prices: list[float] = []
    weights: list[float] = []
    for r, delta_volume in zip(history_plus_current[1:], delta_volume_series):
        price = _record_price(r)
        weight = float(delta_volume) if delta_volume > 0 else 1.0
        weighted_prices.append(price * weight)
        weights.append(weight)
    if not weighted_prices:
        vwap = current_price
    else:
        vwap = sum(weighted_prices) / max(sum(weights), 1.0)

    historical_vwaps: list[float] = []
    for end_idx in range(1, len(history_plus_current) + 1):
        partial_records = history_plus_current[:end_idx]
        partial_volumes = [_record_volume(r) for r in partial_records]
        partial_deltas = _delta_series_from_cumulative(partial_volumes)
        partial_prices = []
        partial_weights = []
        for r, delta_volume in zip(partial_records[1:], partial_deltas):
            price = _record_price(r)
            weight = float(delta_volume) if delta_volume > 0 else 1.0
            partial_prices.append(price * weight)
            partial_weights.append(weight)
        if partial_prices:
            historical_vwaps.append(sum(partial_prices) / max(sum(partial_weights), 1.0))
        else:
            historical_vwaps.append(_record_price(partial_records[-1]))

    vwap_dist = current_price - vwap
    vwap_slope = _slope_from_tail(historical_vwaps, tail_points=min(5, len(historical_vwaps)))

    recent_5m_prices = [_record_price(r) for r in recent_5m_records] if recent_5m_records else [current_price]
    recent_high_5m = max(recent_5m_prices)
    recent_low_5m = min(recent_5m_prices)
    price_range_5m = recent_high_5m - recent_low_5m

    # Volume-based metrics
    delta_volume_tail_short = list(_last_n(delta_volume_series, config.volume_ma_short))
    delta_volume_tail_long = list(_last_n(delta_volume_series, config.volume_ma_long))
    vol_ma10 = _safe_mean(delta_volume_tail_short)
    vol_ma20 = _safe_mean(delta_volume_tail_long)
    cum_volume_session = volumes_cumulative[-1]
    cum_notional_session = current_price * cum_volume_session

    vol_delta_1m = None
    vol_delta_5m = None
    relative_volume_1m = None
    relative_volume_5m = None
    if record_1m is not None:
        vol_delta_1m = float(max(_record_volume(record) - _record_volume(record_1m), 0))
    if record_5m is not None:
        vol_delta_5m = float(max(_record_volume(record) - _record_volume(record_5m), 0))

    avg_delta_volume = _safe_mean(delta_volume_tail_long)
    if vol_delta_1m is not None and avg_delta_volume not in (None, 0.0):
        relative_volume_1m = vol_delta_1m / avg_delta_volume
    if vol_delta_5m is not None and avg_delta_volume not in (None, 0.0):
        relative_volume_5m = vol_delta_5m / avg_delta_volume

    volume_std = _safe_std(delta_volume_tail_long)
    if avg_delta_volume is not None and volume_std not in (None, 0.0):
        volume_zscore = (current_record_delta_volume - avg_delta_volume) / volume_std
    else:
        volume_zscore = None

    price_delta_series = []
    for prev, curr in zip(history_plus_current[:-1], history_plus_current[1:]):
        price_delta_series.append(_record_price(curr) - _record_price(prev))

    abs_price_delta_tail_long = [abs(value) for value in _last_n(price_delta_series, config.spike_window_long)]
    spike_threshold = _safe_std(abs_price_delta_tail_long)
    if spike_threshold is None or spike_threshold == 0.0:
        spike_threshold = max(abs(price_delta_1tick or 0.0), 1e-9)

    def _count_spikes(window: int) -> int:
        tail = _last_n(price_delta_series, window)
        return sum(1 for value in tail if abs(value) >= spike_threshold)

    spikes_5 = _count_spikes(config.spike_window_short)
    spikes_10 = _count_spikes(config.spike_window_medium)
    spikes_20 = _count_spikes(config.spike_window_long)

    vpi = None
    if delta_volume_series:
        signed_volume = 0.0
        total_delta_volume = 0.0
        for price_delta, delta_volume in zip(price_delta_series[-len(delta_volume_series):], delta_volume_series):
            signed_volume += _sign(price_delta) * float(delta_volume)
            total_delta_volume += float(delta_volume)
        vpi = _safe_div(signed_volume, total_delta_volume, default=0.0)

    # OI / options metrics
    oi_delta_option = None
    oi_change_1m = None
    oi_change_5m = None
    oi_velocity = None
    if current_oi is not None and current_history_prev is not None and _record_oi(current_history_prev) is not None:
        oi_delta_option = current_oi - int(_record_oi(current_history_prev) or 0)
    if current_oi is not None and record_1m is not None and _record_oi(record_1m) is not None:
        oi_change_1m = current_oi - int(_record_oi(record_1m) or 0)
    if current_oi is not None and record_5m is not None and _record_oi(record_5m) is not None:
        oi_change_5m = current_oi - int(_record_oi(record_5m) or 0)
    if oi_change_1m is not None:
        oi_velocity = oi_change_1m / 60.0

    premium = record.market.ltp
    strike_dist_pts = None
    delta_proxy = None
    gamma_proxy = None
    if record.instrument.strike is not None and record.context is not None and record.context.spot is not None:
        strike_dist_pts = abs(record.context.spot - float(record.instrument.strike))
        strike_step = float(record.instrument.strike_step or 50 or 1)
        width = max(strike_step * config.option_delta_width_multiplier, 1.0)
        distance_ratio = min(strike_dist_pts / width, 1.0)
        atm_strength = 1.0 - distance_ratio
        if record.instrument.option_type == "CE":
            signed_delta = max(0.05, min(0.95, 0.5 + (record.context.spot - float(record.instrument.strike)) / width))
            delta_proxy = signed_delta
        elif record.instrument.option_type == "PE":
            signed_delta = min(-0.05, max(-0.95, -0.5 + (float(record.instrument.strike) - record.context.spot) / width))
            delta_proxy = signed_delta
        gamma_proxy = max(0.0, atm_strength)

    iv_values = [
        r.context.iv
        for r in history_plus_current
        if r.context is not None and r.context.iv is not None
    ]
    iv_rank = None
    if record.context is not None and record.context.iv is not None and iv_values:
        sorted_iv = sorted(iv_values)
        less_or_equal = sum(1 for value in sorted_iv if value <= record.context.iv)
        iv_rank = less_or_equal / len(sorted_iv)

    # Regime / volatility
    if mu_vol_pct is None:
        volatility_bucket = None
    elif mu_vol_pct < 0.0005:
        volatility_bucket = "low"
    elif mu_vol_pct < 0.002:
        volatility_bucket = "medium"
    else:
        volatility_bucket = "high"

    drift = current_price - prices[0]
    drift_abs = abs(drift)
    price_std = _safe_std(prices) or 0.0
    if drift_abs > max(price_std * 1.5, current_price * 0.0005):
        regime = "trend"
    elif price_std > current_price * 0.002:
        regime = "expansion"
    elif nof_neutral_ticks >= max(3, len(_last_n(nof_series, 10)) // 2):
        regime = "mean_reversion"
    else:
        regime = "neutral"

    sign_tail = [_sign(value) for value in _last_n(price_delta_series, 10) if _sign(value) != 0]
    alternating = 0
    for prev_sign, curr_sign in zip(sign_tail[:-1], sign_tail[1:]):
        if prev_sign != curr_sign:
            alternating += 1
    is_choppy = len(sign_tail) >= 4 and alternating >= max(2, len(sign_tail) // 2)

    # Anchor / linkage metrics
    distance_from_session_high = session_high - current_price
    distance_from_session_low = current_price - session_low
    distance_from_day_open = current_price - day_open_price
    distance_from_orb_high = None
    distance_from_orb_low = None
    if record.context is not None and record.context.orb_high is not None:
        distance_from_orb_high = current_price - record.context.orb_high
    if record.context is not None and record.context.orb_low is not None:
        distance_from_orb_low = current_price - record.context.orb_low

    spot_fut_basis = None
    basis_change_1m = None
    fut_opt_sync_gap_ms = None
    near_vwap_band = abs(vwap_dist) <= current_price * config.vwap_band_pct

    if record.context is not None and record.context.spot is not None and record.context.fut_ltp is not None:
        spot_fut_basis = record.context.fut_ltp - record.context.spot
    if record_1m is not None and record.context is not None and record_1m.context is not None:
        if (
            record.context.spot is not None
            and record.context.fut_ltp is not None
            and record_1m.context.spot is not None
            and record_1m.context.fut_ltp is not None
        ):
            current_basis = record.context.fut_ltp - record.context.spot
            prev_basis = record_1m.context.fut_ltp - record_1m.context.spot
            basis_change_1m = current_basis - prev_basis
    if record.context is not None and record.context.fut_ts is not None:
        fut_opt_sync_gap_ms = int(abs(record.timing.exchange_ts - record.context.fut_ts) * 1000.0)

    # Hidden liquidity proxies: keep conservative and cheap.
    iceberg_score = None
    iceberg_50p = None
    iceberg_75p = None
    iceberg_90p = None
    dark_pool = None
    dark_pool_score = None

    if current_history_prev is not None:
        prev_best_bid_qty = _record_best_bid_qty(current_history_prev) or 0
        prev_best_ask_qty = _record_best_ask_qty(current_history_prev) or 0
        qty_change = abs(best_bid_qty - prev_best_bid_qty) + abs(best_ask_qty - prev_best_ask_qty)
        price_stable = abs((price_delta_1tick or 0.0)) <= max(current_price * 0.00005, 1e-9)
        if price_stable and current_spread <= max(current_price * 0.0001, 0.1):
            iceberg_score = float(qty_change)
            dark_pool = _safe_div(qty_change, max(best_bid_qty + best_ask_qty, 1), default=0.0)
            dark_pool_score = dark_pool

    iceberg_series = [
        value
        for value in (
            current_history_prev and (
                abs((_record_best_bid_qty(history_plus_current[idx]) or 0) - (_record_best_bid_qty(history_plus_current[idx - 1]) or 0))
                + abs((_record_best_ask_qty(history_plus_current[idx]) or 0) - (_record_best_ask_qty(history_plus_current[idx - 1]) or 0))
            )
            for idx in range(1, len(history_plus_current))
        )
        if value is not None
    ]
    if iceberg_series:
        sorted_iceberg = sorted(float(value) for value in iceberg_series)
        iceberg_50p = _percentile(sorted_iceberg, 0.50)
        iceberg_75p = _percentile(sorted_iceberg, 0.75)
        iceberg_90p = _percentile(sorted_iceberg, 0.90)
        if iceberg_score is None:
            iceberg_score = float(sorted_iceberg[-1])

    values: dict[str, Any] = dict(record.live_metrics.to_field_map())
    values.update(
        {
            "half_spread": current_spread / 2.0,
            "nof_ema20": nof_ema20,
            "nof_slope3": nof_slope3,
            "queue_imbalance_l1": queue_imbalance_l1,
            "queue_imbalance_l5": queue_imbalance_l5,
            "book_pressure_ratio_5": book_pressure_ratio_5,
            "book_pressure_ratio_10": book_pressure_ratio_10,
            "book_notional_bid_5": book_notional_bid_5,
            "book_notional_ask_5": book_notional_ask_5,
            "book_notional_bid_10": book_notional_bid_10,
            "book_notional_ask_10": book_notional_ask_10,
            "top_bid_notional": top_bid_notional,
            "top_ask_notional": top_ask_notional,
            "cvd": cvd,
            "cvd_slope_3": cvd_slope_3,
            "cvd_slope_5": cvd_slope_5,
            "cvd_slope_10": cvd_slope_10,
            "trade_through_up": trade_through_up,
            "trade_through_down": trade_through_down,
            "bbid_stepdowns_10": bbid_stepdowns_10,
            "bask_stepups_10": bask_stepups_10,
            "spread_widening_10": spread_widening_10,
            "nof_neutral_ticks": nof_neutral_ticks,
            "prev_price": prev_price,
            "price_delta_1tick": price_delta_1tick,
            "price_delta_1s": price_delta_1s,
            "price_delta_5s": price_delta_5s,
            "session_high_so_far": session_high,
            "session_low_so_far": session_low,
            "distance_from_session_high": distance_from_session_high,
            "distance_from_session_low": distance_from_session_low,
            "distance_from_orb_high": distance_from_orb_high,
            "distance_from_orb_low": distance_from_orb_low,
            "distance_from_day_open": distance_from_day_open,
            "vwap": vwap,
            "vwap_dist": vwap_dist,
            "vwap_slope": vwap_slope,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "bb_mid": bb_mid,
            "bb_width": bb_width,
            "bb_width_ratio": bb_width_ratio,
            "recent_swing_high": recent_high,
            "recent_swing_low": recent_low,
            "recent_high_5min": recent_high_5m,
            "recent_low_5min": recent_low_5m,
            "price_range_5m": price_range_5m,
            "vol_ma10": vol_ma10,
            "vol_ma20": vol_ma20,
            "vol_delta_1m": vol_delta_1m,
            "vol_delta_5m": vol_delta_5m,
            "cum_volume_session": cum_volume_session,
            "cum_notional_session": cum_notional_session,
            "trade_count_proxy": len(history_plus_current),
            "relative_volume_1m": relative_volume_1m,
            "relative_volume_5m": relative_volume_5m,
            "volume_zscore": volume_zscore,
            "spikes_5": spikes_5,
            "spikes_10": spikes_10,
            "spikes_20": spikes_20,
            "vpi": vpi,
            "oi_delta_option": oi_delta_option,
            "oi_change_1m": oi_change_1m,
            "oi_change_5m": oi_change_5m,
            "oi_velocity": oi_velocity,
            "premium": premium,
            "strike_dist_pts": strike_dist_pts,
            "delta_proxy": delta_proxy,
            "gamma_proxy": gamma_proxy,
            "iv_rank": iv_rank,
            "mu_vol_pct": mu_vol_pct,
            "regime": regime,
            "is_choppy": is_choppy,
            "volatility_bucket": volatility_bucket,
            "spot_fut_basis": spot_fut_basis,
            "basis_change_1m": basis_change_1m,
            "fut_opt_sync_gap_ms": fut_opt_sync_gap_ms,
            "near_vwap_band": near_vwap_band,
            "iceberg_score": iceberg_score,
            "iceberg_50p": iceberg_50p,
            "iceberg_75p": iceberg_75p,
            "iceberg_90p": iceberg_90p,
            "dark_pool": dark_pool,
            "dark_pool_score": dark_pool_score,
        }
    )

    # Remove None-valued entries before FieldBundle validation.
    values = {key: value for key, value in values.items() if value is not None}

    return FieldBundle(
        values=values,
        allowed_layers=(FieldLayer.LIVE_DERIVED_LIGHTWEIGHT,),
    )


def enrich_record(
    record: CaptureRecord,
    *,
    history: Sequence[CaptureRecord] = (),
    config: EnrichmentConfig = DEFAULT_ENRICHMENT_CONFIG,
) -> CaptureRecord:
    """
    Return a new CaptureRecord with lightweight live metrics enriched.
    """
    enriched_bundle = build_lightweight_enrichment_bundle(
        record,
        history=history,
        config=config,
    )

    integrity_flags = list(record.runtime_audit.integrity_flags)
    if "enriched_lightweight" not in integrity_flags:
        integrity_flags.append("enriched_lightweight")
    runtime_audit = _make_runtime_audit_with_integrity_flags(record.runtime_audit, integrity_flags)

    return CaptureRecord(
        dataset=record.dataset,
        timing=record.timing,
        instrument=record.instrument,
        market=record.market,
        context=record.context,
        session=record.session,
        live_metrics=enriched_bundle,
        runtime_audit=runtime_audit,
        strategy_audit=record.strategy_audit,
        extra_fields=record.extra_fields,
    )


def enrich_records_sequentially(
    records: Sequence[CaptureRecord],
    *,
    config: EnrichmentConfig = DEFAULT_ENRICHMENT_CONFIG,
) -> tuple[CaptureRecord, ...]:
    """
    Enrich a sequence of records using prior matching records as history.

    The input order is preserved.
    """
    enriched_records: list[CaptureRecord] = []
    seen_history: list[CaptureRecord] = []

    for record in records:
        enriched = enrich_record(
            record,
            history=seen_history,
            config=config,
        )
        enriched_records.append(enriched)
        seen_history.append(enriched)

    return tuple(enriched_records)


__all__ = [
    "DEFAULT_ENRICHMENT_CONFIG",
    "EnrichmentConfig",
    "build_lightweight_enrichment_bundle",
    "enrich_record",
    "enrich_records_sequentially",
]

# =============================================================================
# Batch 17 freeze hardening: live-derived metrics are non-authoritative
# =============================================================================

_BATCH17_ENRICHER_NON_AUTHORITATIVE_VERSION = "1"


def batch17_live_derived_non_authoritative_metadata() -> dict[str, Any]:
    return {
        "live_derived_metrics_non_authoritative": True,
        "derived_not_production_used": True,
        "offline_replay_required_for_contract_change": True,
    }
