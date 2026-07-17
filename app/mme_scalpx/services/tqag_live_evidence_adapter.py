"""Pure TQAG live-evidence adapter.

This module converts existing live/candidate/read-only surfaces into TQAG
quality booleans. It performs no Redis writes, starts no services, and has no
broker transport.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class TQAGLiveEvidence:
    quote_fresh: bool
    bid_qty_valid: bool
    ask_qty_valid: bool
    spread_acceptable: bool
    instrument_lock_valid: bool
    option_symbol_stable: bool
    underlying_option_aligned: bool
    no_chase: bool
    edge_after_cost_positive: bool
    timeframe_complete: bool
    data_gap_present: bool
    reasons: tuple[str, ...]

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"1", "true", "yes", "y", "pass", "ok"}:
        return True
    if text in {"0", "false", "no", "n", "fail"}:
        return False
    return default


def _json_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text or text[0] not in "[{":
        return value
    try:
        return json.loads(text)
    except Exception:
        return value


def _first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", "null", "None"):
            return value
    return None


def derive_tqag_live_evidence(
    *,
    selected_option: Mapping[str, Any],
    candidate: Mapping[str, Any] | None = None,
    provider_runtime: Mapping[str, Any] | None = None,
    now_ns: int | None = None,
    max_quote_age_ms: float = 2500.0,
    min_bid_qty: int = 1,
    min_ask_qty: int = 1,
    max_spread_ratio: float = 1.6,
    max_spread_points: float = 1.25,
    min_edge_points_after_cost: float = 1.0,
) -> TQAGLiveEvidence:
    candidate = candidate or {}
    provider_runtime = provider_runtime or {}
    now_ns = now_ns or time.time_ns()
    reasons: list[str] = []

    bid_qty = _int(
        _first_nonempty(
            selected_option.get("bid_qty"),
            selected_option.get("bid_qty_5"),
            selected_option.get("best_bid_qty"),
        )
    )
    ask_qty = _int(
        _first_nonempty(
            selected_option.get("ask_qty"),
            selected_option.get("ask_qty_5"),
            selected_option.get("best_ask_qty"),
        )
    )

    bids = _json_value(selected_option.get("bids"))
    asks = _json_value(selected_option.get("asks"))

    if bid_qty <= 0 and isinstance(bids, list) and bids:
        bid_qty = _int(bids[0].get("quantity") if isinstance(bids[0], dict) else 0)

    if ask_qty <= 0 and isinstance(asks, list) and asks:
        ask_qty = _int(asks[0].get("quantity") if isinstance(asks[0], dict) else 0)

    best_bid = _float(
        _first_nonempty(
            selected_option.get("best_bid"),
            selected_option.get("bid"),
            selected_option.get("bid_price"),
        )
    )
    best_ask = _float(
        _first_nonempty(
            selected_option.get("best_ask"),
            selected_option.get("ask"),
            selected_option.get("ask_price"),
        )
    )

    if best_bid <= 0 and isinstance(bids, list) and bids:
        best_bid = _float(bids[0].get("price") if isinstance(bids[0], dict) else 0.0)

    if best_ask <= 0 and isinstance(asks, list) and asks:
        best_ask = _float(asks[0].get("price") if isinstance(asks[0], dict) else 0.0)

    ltp = _float(
        _first_nonempty(
            selected_option.get("ltp"),
            selected_option.get("last_price"),
            selected_option.get("price"),
        )
    )

    mid = (best_bid + best_ask) / 2.0 if best_bid > 0 and best_ask > 0 else ltp
    spread_points = max(0.0, best_ask - best_bid) if best_bid > 0 and best_ask > 0 else 0.0
    spread_ratio = _float(selected_option.get("spread_ratio"), 0.0)

    if spread_ratio <= 0 and mid > 0 and spread_points > 0:
        # Percent-like ratio, matching older surfaces that use small numeric ratios.
        spread_ratio = (spread_points / mid) * 100.0

    ts_ns = _int(
        _first_nonempty(
            selected_option.get("ts_event_ns"),
            selected_option.get("ts_local_ns"),
            selected_option.get("ts_ns"),
            selected_option.get("ltt_ns"),
            candidate.get("ts_ns"),
        )
    )

    age_ms = ((now_ns - ts_ns) / 1_000_000.0) if ts_ns > 0 else 999999999.0

    symbol = str(
        _first_nonempty(
            selected_option.get("trading_symbol"),
            selected_option.get("option_symbol"),
            selected_option.get("symbol"),
            candidate.get("symbol"),
            candidate.get("candidate_symbol_shadow"),
        )
        or ""
    ).strip()

    token = str(
        _first_nonempty(
            selected_option.get("instrument_token"),
            selected_option.get("option_token"),
            selected_option.get("token"),
            candidate.get("token"),
            candidate.get("candidate_instrument_token_shadow"),
        )
        or ""
    ).strip()

    provider_ok = _bool(
        _first_nonempty(
            provider_runtime.get("provider_ready_classic"),
            provider_runtime.get("selected_option_provider_ready"),
            provider_runtime.get("futures_marketdata_status") == "HEALTHY",
        ),
        default=False,
    )

    candidate_symbol = str(
        _first_nonempty(
            candidate.get("symbol"),
            candidate.get("candidate_symbol_shadow"),
            symbol,
        )
        or ""
    ).strip()

    quote_fresh = ts_ns > 0 and age_ms <= max_quote_age_ms
    bid_qty_valid = bid_qty >= min_bid_qty
    ask_qty_valid = ask_qty >= min_ask_qty
    spread_acceptable = (
        best_bid > 0
        and best_ask > 0
        and best_ask >= best_bid
        and (
            (spread_ratio > 0 and spread_ratio <= max_spread_ratio)
            or spread_points <= max_spread_points
        )
    )
    instrument_lock_valid = bool(symbol and token)
    option_symbol_stable = bool(symbol and candidate_symbol and symbol == candidate_symbol)

    # These remain strict unless explicit surfaces already publish a pass.
    underlying_option_aligned = _bool(
        _first_nonempty(
            candidate.get("underlying_option_aligned"),
            candidate.get("futures_alignment_ok"),
            candidate.get("futures_vwap_align_ok"),
        ),
        default=False,
    )

    no_chase = _bool(candidate.get("no_chase"), default=False)

    expected_move_points = _float(
        _first_nonempty(
            candidate.get("expected_move_points"),
            candidate.get("expected_net_edge_points"),
            candidate.get("target_points"),
        )
    )
    breakeven_points = _float(
        _first_nonempty(
            candidate.get("conservative_breakeven_points"),
            candidate.get("breakeven_points"),
        )
    )
    edge_after_cost_positive = (
        _bool(candidate.get("edge_after_cost_positive"), default=False)
        or (
            expected_move_points > 0
            and breakeven_points > 0
            and expected_move_points > breakeven_points + min_edge_points_after_cost
        )
    )

    timeframe_complete = _bool(
        _first_nonempty(
            candidate.get("timeframe_complete"),
            candidate.get("micro_observation_complete"),
            candidate.get("instrument_lock_state") == "MICRO_OBSERVATION_COMPLETE",
        ),
        default=False,
    )

    data_gap_present = not (
        provider_ok
        and quote_fresh
        and bid_qty_valid
        and ask_qty_valid
        and spread_acceptable
        and instrument_lock_valid
        and option_symbol_stable
    )

    checks = {
        "QUOTE_FRESH": quote_fresh,
        "BID_QTY_VALID": bid_qty_valid,
        "ASK_QTY_VALID": ask_qty_valid,
        "SPREAD_ACCEPTABLE": spread_acceptable,
        "INSTRUMENT_LOCK_VALID": instrument_lock_valid,
        "OPTION_SYMBOL_STABLE": option_symbol_stable,
        "UNDERLYING_OPTION_ALIGNED": underlying_option_aligned,
        "NO_CHASE": no_chase,
        "EDGE_AFTER_COST_POSITIVE": edge_after_cost_positive,
        "TIMEFRAME_COMPLETE": timeframe_complete,
    }

    for name, ok in checks.items():
        if not ok:
            reasons.append(name)

    if data_gap_present:
        reasons.append("DATA_GAP_PRESENT")

    return TQAGLiveEvidence(
        quote_fresh=quote_fresh,
        bid_qty_valid=bid_qty_valid,
        ask_qty_valid=ask_qty_valid,
        spread_acceptable=spread_acceptable,
        instrument_lock_valid=instrument_lock_valid,
        option_symbol_stable=option_symbol_stable,
        underlying_option_aligned=underlying_option_aligned,
        no_chase=no_chase,
        edge_after_cost_positive=edge_after_cost_positive,
        timeframe_complete=timeframe_complete,
        data_gap_present=data_gap_present,
        reasons=tuple(reasons),
    )
