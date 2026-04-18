from __future__ import annotations

"""
app/mme_scalpx/research_capture/normalizer.py

Frozen normalization layer for the MME research data capture chapter.

Purpose
-------
This module owns broker-aware normalization from raw broker payloads into the
canonical research-capture models. It is the bridge between broker-specific
wire shapes and the broker-agnostic archive schema.

Owns
----
- broker-aware raw payload extraction for Zerodha and Dhan
- normalization context and static instrument-reference validation
- canonical TimingIdentity / InstrumentIdentity / MarketSnapshot construction
- canonical ContextAnchors / SessionContext / RuntimeAuditState construction
- minimal mandatory live metrics required by the frozen model layer
- high-level normalize_* entrypoints producing CaptureRecord

Does not own
------------
- broker connections or subscriptions
- Redis IO
- parquet IO
- archive writing
- heavy derived analytics
- production strategy doctrine

Design laws
-----------
- normalization must be deterministic and side-effect free
- raw broker/source provenance must remain explicit
- normalized records must remain broker-agnostic at the archive schema level
- raw first, minimal required live metrics second, heavy analytics later
- no silent strategy/doctrine changes inside normalization
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Mapping, Sequence
import re

from app.mme_scalpx.research_capture.contracts import FieldLayer, SCHEMA_VERSION
from app.mme_scalpx.research_capture.models import (
    CaptureDatasetName,
    CaptureRecord,
    ContextAnchors,
    FieldBundle,
    InstrumentIdentity,
    MarketSnapshot,
    RuntimeAuditState,
    SessionContext,
    StrategyAuditState,
    TimingIdentity,
)

_BROKER_ZERODHA = "zerodha"
_BROKER_DHAN = "dhan"
_BROKER_GENERIC = "generic"

_MISSING = object()
_OPTION_TYPE_RE = re.compile(r"(CE|PE)$", re.IGNORECASE)
_STRIKE_RE = re.compile(r"(\d+)(CE|PE)$", re.IGNORECASE)


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _first_present(mapping: Mapping[str, Any], *paths: Sequence[str] | str, default: Any = None) -> Any:
    for path in paths:
        path_tuple = (path,) if isinstance(path, str) else tuple(path)
        current: Any = mapping
        ok = True
        for key in path_tuple:
            if not isinstance(current, Mapping) or key not in current:
                ok = False
                break
            current = current[key]
        if ok:
            return current
    return default


def _coerce_int(value: Any, *, default: int | None = None) -> int | None:
    if value is None:
        return default
    if isinstance(value, bool):
        raise TypeError("bool cannot be coerced to int here")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        return int(float(stripped))
    raise TypeError(f"Cannot coerce {type(value).__name__} to int")


def _coerce_float(value: Any, *, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, bool):
        raise TypeError("bool cannot be coerced to float here")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        return float(stripped)
    raise TypeError(f"Cannot coerce {type(value).__name__} to float")


def _coerce_bool(value: Any, *, default: bool | None = None) -> bool | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if not lowered:
            return default
        if lowered in {"1", "true", "yes", "y"}:
            return True
        if lowered in {"0", "false", "no", "n"}:
            return False
    raise TypeError(f"Cannot coerce {type(value).__name__} to bool")


def _coerce_date_str(value: Any, *, default: str | None = None) -> str | None:
    if value is None:
        return default
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        stripped = stripped.replace("/", "-")
        if "T" in stripped:
            return stripped.split("T", 1)[0]
        if " " in stripped and len(stripped) >= 10:
            return stripped[:10]
        return stripped
    raise TypeError(f"Cannot coerce {type(value).__name__} to date string")


def _coerce_epoch_seconds(value: Any, *, default: float | None = None) -> float | None:
    """
    Normalize a timestamp-like value into epoch seconds.
    """
    if value is None:
        return default

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        numeric = float(value)
        if numeric > 1e18:   # ns
            return numeric / 1e9
        if numeric > 1e15:   # us
            return numeric / 1e6
        if numeric > 1e12:   # ms
            return numeric / 1e3
        return numeric

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        try:
            return _coerce_epoch_seconds(float(stripped), default=default)
        except ValueError:
            pass
        parsed = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()

    raise TypeError(f"Cannot coerce {type(value).__name__} to epoch seconds")


def _coerce_epoch_ns(value: Any, *, default: int | None = None) -> int | None:
    seconds = _coerce_epoch_seconds(value, default=None)
    if seconds is None:
        return default
    return int(seconds * 1_000_000_000)


def _parse_option_type_from_symbol(tradingsymbol: str | None) -> str | None:
    if not tradingsymbol:
        return None
    match = _OPTION_TYPE_RE.search(tradingsymbol)
    return match.group(1).upper() if match else None


def _parse_strike_from_symbol(tradingsymbol: str | None) -> int | None:
    if not tradingsymbol:
        return None
    match = _STRIKE_RE.search(tradingsymbol)
    if not match:
        return None
    return int(match.group(1))


def _normalize_depth_side(levels: Any, *, side: str) -> tuple[tuple[float, ...], tuple[int, ...]]:
    """
    Normalize broker depth levels into canonical ordered tuples.

    buy  -> descending by price
    sell -> ascending by price
    """
    if levels is None:
        return (), ()
    if not isinstance(levels, (list, tuple)):
        return (), ()

    parsed: list[tuple[float, int]] = []
    for level in levels:
        level_map = _mapping(level)
        if not level_map:
            continue
        price = _coerce_float(
            _first_present(
                level_map,
                "price",
                "bid_price",
                "ask_price",
                "bestBidPrice",
                "bestAskPrice",
            ),
            default=None,
        )
        qty = _coerce_int(
            _first_present(
                level_map,
                "quantity",
                "qty",
                "orders",
                "bid_quantity",
                "ask_quantity",
                "bestBidQuantity",
                "bestAskQuantity",
            ),
            default=0,
        )
        if price is None:
            continue
        parsed.append((price, 0 if qty is None else qty))

    reverse = side == "buy"
    parsed.sort(key=lambda item: item[0], reverse=reverse)

    prices = tuple(item[0] for item in parsed)
    qtys = tuple(item[1] for item in parsed)
    return prices, qtys


def _synthesize_top_book(
    *,
    ltp: float,
    best_bid: float | None,
    best_ask: float | None,
    best_bid_qty: int | None,
    best_ask_qty: int | None,
) -> tuple[float, float, int, int, tuple[float, ...], tuple[int, ...], tuple[float, ...], tuple[int, ...]]:
    """
    Build a conservative synthetic top book when true depth is unavailable.
    """
    bid = ltp if best_bid is None else best_bid
    ask = ltp if best_ask is None else best_ask
    bid_qty = 0 if best_bid_qty is None else best_bid_qty
    ask_qty = 0 if best_ask_qty is None else best_ask_qty

    bid_prices = (bid,)
    bid_qtys = (bid_qty,)
    ask_prices = (ask,)
    ask_qtys = (ask_qty,)
    return bid, ask, bid_qty, ask_qty, bid_prices, bid_qtys, ask_prices, ask_qtys


@dataclass(frozen=True, slots=True)
class InstrumentReference:
    """
    Static reference surface required to normalize a broker payload.
    """
    broker_name: str
    exchange: str
    exchange_segment: str
    instrument_token: str | int
    tradingsymbol: str
    instrument_type: str
    symbol_root: str
    underlying_symbol: str
    tick_size: float
    lot_size: int
    symbol: str | None = None
    symbol_token: str | None = None
    contract_name: str | None = None
    underlying_token: str | int | None = None
    option_type: str | None = None
    strike: int | None = None
    expiry: str | None = None
    expiry_type: str | None = None
    freeze_qty: int | None = None
    strike_step: int | None = None
    moneyness_bucket: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "broker_name",
            "exchange",
            "exchange_segment",
            "tradingsymbol",
            "instrument_type",
            "symbol_root",
            "underlying_symbol",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty str")

        if not isinstance(self.instrument_token, (str, int)) or isinstance(self.instrument_token, bool):
            raise TypeError("instrument_token must be str or int")
        if not isinstance(self.tick_size, (int, float)) or isinstance(self.tick_size, bool):
            raise TypeError("tick_size must be numeric")
        if not isinstance(self.lot_size, int) or isinstance(self.lot_size, bool):
            raise TypeError("lot_size must be int")
        if self.strike is not None and (not isinstance(self.strike, int) or isinstance(self.strike, bool)):
            raise TypeError("strike must be int or None")
        if self.freeze_qty is not None and (not isinstance(self.freeze_qty, int) or isinstance(self.freeze_qty, bool)):
            raise TypeError("freeze_qty must be int or None")
        if self.strike_step is not None and (not isinstance(self.strike_step, int) or isinstance(self.strike_step, bool)):
            raise TypeError("strike_step must be int or None")

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, Any],
        *,
        broker_name: str,
        raw_payload: Mapping[str, Any] | None = None,
    ) -> "InstrumentReference":
        raw = {} if raw_payload is None else dict(raw_payload)
        ref = dict(mapping)

        tradingsymbol = _first_present(
            ref,
            "tradingsymbol",
            "trading_symbol",
            "tradingSymbol",
            default=_first_present(raw, "tradingsymbol", "trading_symbol", "tradingSymbol", "symbol"),
        )
        instrument_type = _first_present(
            ref,
            "instrument_type",
            "segment_type",
            default=None,
        )
        option_type = _first_present(ref, "option_type", default=_parse_option_type_from_symbol(tradingsymbol))
        strike = _coerce_int(_first_present(ref, "strike", default=_parse_strike_from_symbol(tradingsymbol)), default=None)

        expiry = _coerce_date_str(_first_present(ref, "expiry", "expiry_date"), default=None)
        expiry_type = _first_present(ref, "expiry_type", default=None)

        instrument_token = _first_present(
            ref,
            "instrument_token",
            "token",
            "security_id",
            default=_first_present(raw, "instrument_token", "token", "security_id", "securityId"),
        )
        if instrument_token is None:
            raise ValueError("instrument_reference requires instrument_token")

        if tradingsymbol is None:
            raise ValueError("instrument_reference requires tradingsymbol")

        if instrument_type is None:
            instrument_type = option_type if option_type in {"CE", "PE"} else "FUT"

        return cls(
            broker_name=broker_name,
            exchange=str(_first_present(ref, "exchange", default="NFO")),
            exchange_segment=str(_first_present(ref, "exchange_segment", "segment", default="NFO")),
            instrument_token=instrument_token,
            tradingsymbol=str(tradingsymbol),
            symbol=_first_present(ref, "symbol", "full_symbol"),
            symbol_token=_first_present(ref, "symbol_token"),
            contract_name=_first_present(ref, "contract_name"),
            instrument_type=str(instrument_type),
            symbol_root=str(_first_present(ref, "symbol_root", "root_symbol", default=_first_present(ref, "underlying_symbol", default="UNKNOWN"))),
            underlying_symbol=str(_first_present(ref, "underlying_symbol", default="UNKNOWN")),
            underlying_token=_first_present(ref, "underlying_token"),
            option_type=None if option_type is None else str(option_type).upper(),
            strike=strike,
            expiry=expiry,
            expiry_type=None if expiry_type is None else str(expiry_type),
            tick_size=float(_coerce_float(_first_present(ref, "tick_size", default=0.05), default=0.05)),
            lot_size=int(_coerce_int(_first_present(ref, "lot_size", default=1), default=1)),
            freeze_qty=_coerce_int(_first_present(ref, "freeze_qty"), default=None),
            strike_step=_coerce_int(_first_present(ref, "strike_step"), default=None),
            moneyness_bucket=_first_present(ref, "moneyness_bucket"),
        )


@dataclass(frozen=True, slots=True)
class NormalizationContext:
    """
    Runtime normalization context shared across one raw payload normalization.
    """
    session_date: str
    recv_ts_ns: int
    process_ts_ns: int
    event_seq: int
    source_ts_ns: int | None = None
    snapshot_id: str | None = None
    processed_ts: float | None = None
    network_time: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.session_date, str) or not self.session_date:
            raise ValueError("session_date must be a non-empty str")
        for name in ("recv_ts_ns", "process_ts_ns", "event_seq"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be int")
        if self.source_ts_ns is not None and (not isinstance(self.source_ts_ns, int) or isinstance(self.source_ts_ns, bool)):
            raise TypeError("source_ts_ns must be int or None")
        if self.snapshot_id is not None and not isinstance(self.snapshot_id, str):
            raise TypeError("snapshot_id must be str or None")
        if self.processed_ts is not None and not isinstance(self.processed_ts, (int, float)):
            raise TypeError("processed_ts must be numeric or None")
        if self.network_time is not None and not isinstance(self.network_time, (int, float)):
            raise TypeError("network_time must be numeric or None")

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "NormalizationContext":
        session_date = _coerce_date_str(_first_present(mapping, "session_date"), default=None)
        if session_date is None:
            raise ValueError("NormalizationContext requires session_date")

        recv_ts_ns = _coerce_int(_first_present(mapping, "recv_ts_ns"), default=None)
        process_ts_ns = _coerce_int(_first_present(mapping, "process_ts_ns"), default=None)
        event_seq = _coerce_int(_first_present(mapping, "event_seq"), default=None)

        if recv_ts_ns is None or process_ts_ns is None or event_seq is None:
            raise ValueError("NormalizationContext requires recv_ts_ns, process_ts_ns, and event_seq")

        return cls(
            session_date=session_date,
            recv_ts_ns=recv_ts_ns,
            process_ts_ns=process_ts_ns,
            event_seq=event_seq,
            source_ts_ns=_coerce_int(_first_present(mapping, "source_ts_ns"), default=None),
            snapshot_id=_first_present(mapping, "snapshot_id"),
            processed_ts=_coerce_float(_first_present(mapping, "processed_ts"), default=None),
            network_time=_coerce_float(_first_present(mapping, "network_time"), default=None),
        )


@dataclass(frozen=True, slots=True)
class AnchorContextInput:
    spot_symbol: str | None = None
    spot: float | None = None
    spot_ts: float | None = None
    fut_symbol: str | None = None
    fut_ltp: float | None = None
    fut_vol: int | None = None
    fut_ts: float | None = None
    vix: float | None = None
    vix_ts: float | None = None
    pcr: float | None = None
    iv: float | None = None
    atm_iv: float | None = None
    orb_high: float | None = None
    orb_low: float | None = None
    orb_ts: float | None = None

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "AnchorContextInput":
        return cls(
            spot_symbol=_first_present(mapping, "spot_symbol"),
            spot=_coerce_float(_first_present(mapping, "spot"), default=None),
            spot_ts=_coerce_epoch_seconds(_first_present(mapping, "spot_ts"), default=None),
            fut_symbol=_first_present(mapping, "fut_symbol"),
            fut_ltp=_coerce_float(_first_present(mapping, "fut_ltp"), default=None),
            fut_vol=_coerce_int(_first_present(mapping, "fut_vol"), default=None),
            fut_ts=_coerce_epoch_seconds(_first_present(mapping, "fut_ts"), default=None),
            vix=_coerce_float(_first_present(mapping, "vix"), default=None),
            vix_ts=_coerce_epoch_seconds(_first_present(mapping, "vix_ts"), default=None),
            pcr=_coerce_float(_first_present(mapping, "pcr"), default=None),
            iv=_coerce_float(_first_present(mapping, "iv"), default=None),
            atm_iv=_coerce_float(_first_present(mapping, "atm_iv"), default=None),
            orb_high=_coerce_float(_first_present(mapping, "orb_high"), default=None),
            orb_low=_coerce_float(_first_present(mapping, "orb_low"), default=None),
            orb_ts=_coerce_epoch_seconds(_first_present(mapping, "orb_ts"), default=None),
        )

    def to_models_context(self) -> ContextAnchors:
        return ContextAnchors(
            spot_symbol=self.spot_symbol,
            spot=self.spot,
            spot_ts=self.spot_ts,
            fut_symbol=self.fut_symbol,
            fut_ltp=self.fut_ltp,
            fut_vol=self.fut_vol,
            fut_ts=self.fut_ts,
            vix=self.vix,
            vix_ts=self.vix_ts,
            pcr=self.pcr,
            iv=self.iv,
            atm_iv=self.atm_iv,
            orb_high=self.orb_high,
            orb_low=self.orb_low,
            orb_ts=self.orb_ts,
        )


@dataclass(frozen=True, slots=True)
class SessionMetadataInput:
    market_open: str | None = None
    market_close: str | None = None
    is_expiry: bool | None = None
    dte: int | None = None
    days_to_expiry_exact: float | None = None
    is_current_week: bool | None = None
    is_next_week: bool | None = None
    is_monthly_expiry: bool | None = None
    trading_minute_index: int | None = None
    is_preopen: bool = False
    is_postclose: bool = False
    weekday: int | None = None
    month: int | None = None
    expiry_week_flag: bool | None = None

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "SessionMetadataInput":
        return cls(
            market_open=_first_present(mapping, "market_open"),
            market_close=_first_present(mapping, "market_close"),
            is_expiry=_coerce_bool(_first_present(mapping, "is_expiry"), default=None),
            dte=_coerce_int(_first_present(mapping, "dte"), default=None),
            days_to_expiry_exact=_coerce_float(_first_present(mapping, "days_to_expiry_exact"), default=None),
            is_current_week=_coerce_bool(_first_present(mapping, "is_current_week"), default=None),
            is_next_week=_coerce_bool(_first_present(mapping, "is_next_week"), default=None),
            is_monthly_expiry=_coerce_bool(_first_present(mapping, "is_monthly_expiry"), default=None),
            trading_minute_index=_coerce_int(_first_present(mapping, "trading_minute_index"), default=None),
            is_preopen=_coerce_bool(_first_present(mapping, "is_preopen"), default=False) or False,
            is_postclose=_coerce_bool(_first_present(mapping, "is_postclose"), default=False) or False,
            weekday=_coerce_int(_first_present(mapping, "weekday"), default=None),
            month=_coerce_int(_first_present(mapping, "month"), default=None),
            expiry_week_flag=_coerce_bool(_first_present(mapping, "expiry_week_flag"), default=None),
        )

    def to_models_context(
        self,
        *,
        session_date: str,
        instrument_reference: InstrumentReference,
    ) -> SessionContext:
        session_dt = datetime.fromisoformat(session_date).date()

        expiry_dt = None
        if instrument_reference.expiry is not None:
            expiry_dt = datetime.fromisoformat(instrument_reference.expiry).date()

        dte = self.dte
        if dte is None:
            dte = 0 if expiry_dt is None else (expiry_dt - session_dt).days

        is_expiry = self.is_expiry
        if is_expiry is None:
            is_expiry = dte <= 0

        days_to_expiry_exact = self.days_to_expiry_exact
        if days_to_expiry_exact is None and expiry_dt is not None:
            days_to_expiry_exact = float(dte)

        is_current_week = self.is_current_week
        if is_current_week is None:
            is_current_week = instrument_reference.expiry_type == "weekly"

        is_next_week = self.is_next_week
        if is_next_week is None:
            is_next_week = False

        is_monthly_expiry = self.is_monthly_expiry
        if is_monthly_expiry is None:
            is_monthly_expiry = instrument_reference.expiry_type == "monthly"

        weekday = self.weekday if self.weekday is not None else session_dt.isoweekday()
        month = self.month if self.month is not None else session_dt.month

        expiry_week_flag = self.expiry_week_flag
        if expiry_week_flag is None:
            expiry_week_flag = bool(is_current_week or is_monthly_expiry)

        return SessionContext(
            market_open=self.market_open,
            market_close=self.market_close,
            is_expiry=is_expiry,
            dte=dte,
            days_to_expiry_exact=days_to_expiry_exact,
            is_current_week=is_current_week,
            is_next_week=is_next_week,
            is_monthly_expiry=is_monthly_expiry,
            trading_minute_index=self.trading_minute_index,
            is_preopen=self.is_preopen,
            is_postclose=self.is_postclose,
            weekday=weekday,
            month=month,
            expiry_week_flag=expiry_week_flag,
        )


@dataclass(frozen=True, slots=True)
class RuntimeAuditInput:
    stale_reason: str | None = None
    fallback_used_flag: bool | None = None
    fallback_source: str | None = None
    normalization_version: str | None = "v1"
    derived_version: str | None = "v1_minimal"
    calendar_version: str | None = None
    heartbeat_status: str | None = None
    reconnect_count: int | None = None
    last_reconnect_reason: str | None = None
    gpu_fallback: bool | None = None
    cpu_mode_flag: bool | None = None
    latency_ns: int | None = None
    gap_from_prev_tick_ms: int | None = None
    additional_integrity_flags: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "RuntimeAuditInput":
        flags = _first_present(mapping, "additional_integrity_flags", default=())
        if not isinstance(flags, (tuple, list)):
            raise TypeError("additional_integrity_flags must be a tuple/list of strings")
        return cls(
            stale_reason=_first_present(mapping, "stale_reason"),
            fallback_used_flag=_coerce_bool(_first_present(mapping, "fallback_used_flag"), default=None),
            fallback_source=_first_present(mapping, "fallback_source"),
            normalization_version=_first_present(mapping, "normalization_version", default="v1"),
            derived_version=_first_present(mapping, "derived_version", default="v1_minimal"),
            calendar_version=_first_present(mapping, "calendar_version"),
            heartbeat_status=_first_present(mapping, "heartbeat_status"),
            reconnect_count=_coerce_int(_first_present(mapping, "reconnect_count"), default=None),
            last_reconnect_reason=_first_present(mapping, "last_reconnect_reason"),
            gpu_fallback=_coerce_bool(_first_present(mapping, "gpu_fallback"), default=None),
            cpu_mode_flag=_coerce_bool(_first_present(mapping, "cpu_mode_flag"), default=None),
            latency_ns=_coerce_int(_first_present(mapping, "latency_ns"), default=None),
            gap_from_prev_tick_ms=_coerce_int(_first_present(mapping, "gap_from_prev_tick_ms"), default=None),
            additional_integrity_flags=tuple(str(flag) for flag in flags),
        )

    def to_models_state(
        self,
        *,
        is_stale_tick: bool,
        missing_depth_flag: bool,
        missing_oi_flag: bool,
        thin_book: bool,
        integrity_flags: Sequence[str],
    ) -> RuntimeAuditState:
        return RuntimeAuditState(
            is_stale_tick=is_stale_tick,
            stale_reason=self.stale_reason,
            missing_depth_flag=missing_depth_flag,
            missing_oi_flag=missing_oi_flag,
            thin_book=thin_book,
            book_is_thin=thin_book,
            crossed_book_flag=False,
            locked_book_flag=False,
            integrity_flags=tuple(integrity_flags),
            fallback_used_flag=self.fallback_used_flag,
            fallback_source=self.fallback_source,
            schema_version=SCHEMA_VERSION,
            normalization_version=self.normalization_version,
            derived_version=self.derived_version,
            calendar_version=self.calendar_version,
            heartbeat_status=self.heartbeat_status,
            reconnect_count=self.reconnect_count,
            last_reconnect_reason=self.last_reconnect_reason,
            gpu_fallback=self.gpu_fallback,
            cpu_mode_flag=self.cpu_mode_flag,
            latency_ns=self.latency_ns,
            gap_from_prev_tick_ms=self.gap_from_prev_tick_ms,
        )


def _extract_zerodha_market_payload(raw_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    raw = dict(raw_payload)
    depth = _mapping(_first_present(raw, "depth", default={}))

    buy_prices, buy_qty = _normalize_depth_side(_first_present(depth, "buy", "bids", default=()), side="buy")
    sell_prices, sell_qty = _normalize_depth_side(_first_present(depth, "sell", "asks", default=()), side="sell")

    return {
        "exchange_ts": _coerce_epoch_seconds(
            _first_present(
                raw,
                "exchange_timestamp",
                "timestamp",
                "last_trade_time",
                default=None,
            ),
            default=None,
        ),
        "source_ts_ns": _coerce_epoch_ns(
            _first_present(
                raw,
                "exchange_timestamp",
                "timestamp",
                "last_trade_time",
                default=None,
            ),
            default=None,
        ),
        "ltp": _coerce_float(_first_present(raw, "last_price", "ltp", "price", "close"), default=None),
        "volume": _coerce_int(_first_present(raw, "volume_traded", "volume", "volume_traded_today"), default=0),
        "oi": _coerce_int(_first_present(raw, "oi", "open_interest"), default=None),
        "best_bid": _coerce_float(_first_present(raw, "best_bid", default=buy_prices[0] if buy_prices else None), default=None),
        "best_ask": _coerce_float(_first_present(raw, "best_ask", default=sell_prices[0] if sell_prices else None), default=None),
        "best_bid_qty": _coerce_int(_first_present(raw, "best_bid_qty", default=buy_qty[0] if buy_qty else None), default=None),
        "best_ask_qty": _coerce_int(_first_present(raw, "best_ask_qty", default=sell_qty[0] if sell_qty else None), default=None),
        "bid_prices": buy_prices,
        "bid_qty": buy_qty,
        "ask_prices": sell_prices,
        "ask_qty": sell_qty,
    }


def _extract_dhan_market_payload(raw_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    raw = dict(raw_payload)
    depth = _mapping(_first_present(raw, "depth", "marketDepth", default={}))

    buy_prices, buy_qty = _normalize_depth_side(
        _first_present(depth, "buy", "bids", "bestBid", default=()),
        side="buy",
    )
    sell_prices, sell_qty = _normalize_depth_side(
        _first_present(depth, "sell", "asks", "bestAsk", default=()),
        side="sell",
    )

    return {
        "exchange_ts": _coerce_epoch_seconds(
            _first_present(
                raw,
                "exchangeTime",
                "exchange_time",
                "timestamp",
                "lastTradeTime",
                default=None,
            ),
            default=None,
        ),
        "source_ts_ns": _coerce_epoch_ns(
            _first_present(
                raw,
                "exchangeTime",
                "exchange_time",
                "timestamp",
                "lastTradeTime",
                default=None,
            ),
            default=None,
        ),
        "ltp": _coerce_float(_first_present(raw, "LTP", "ltp", "lastPrice", "price", "close"), default=None),
        "volume": _coerce_int(_first_present(raw, "volume", "tradedVolume"), default=0),
        "oi": _coerce_int(_first_present(raw, "OI", "oi", "openInterest"), default=None),
        "best_bid": _coerce_float(
            _first_present(raw, "bestBidPrice", "best_bid", default=buy_prices[0] if buy_prices else None),
            default=None,
        ),
        "best_ask": _coerce_float(
            _first_present(raw, "bestAskPrice", "best_ask", default=sell_prices[0] if sell_prices else None),
            default=None,
        ),
        "best_bid_qty": _coerce_int(
            _first_present(raw, "bestBidQuantity", "best_bid_qty", default=buy_qty[0] if buy_qty else None),
            default=None,
        ),
        "best_ask_qty": _coerce_int(
            _first_present(raw, "bestAskQuantity", "best_ask_qty", default=sell_qty[0] if sell_qty else None),
            default=None,
        ),
        "bid_prices": buy_prices,
        "bid_qty": buy_qty,
        "ask_prices": sell_prices,
        "ask_qty": sell_qty,
    }


def _extract_generic_market_payload(raw_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    raw = dict(raw_payload)
    depth = _mapping(_first_present(raw, "depth", "marketDepth", default={}))

    buy_prices, buy_qty = _normalize_depth_side(
        _first_present(depth, "buy", "bids", default=()),
        side="buy",
    )
    sell_prices, sell_qty = _normalize_depth_side(
        _first_present(depth, "sell", "asks", default=()),
        side="sell",
    )

    return {
        "exchange_ts": _coerce_epoch_seconds(
            _first_present(raw, "exchange_timestamp", "exchangeTime", "timestamp", default=None),
            default=None,
        ),
        "source_ts_ns": _coerce_epoch_ns(
            _first_present(raw, "exchange_timestamp", "exchangeTime", "timestamp", default=None),
            default=None,
        ),
        "ltp": _coerce_float(_first_present(raw, "ltp", "last_price", "LTP", "price", "close"), default=None),
        "volume": _coerce_int(_first_present(raw, "volume", "volume_traded"), default=0),
        "oi": _coerce_int(_first_present(raw, "oi", "OI", "open_interest"), default=None),
        "best_bid": _coerce_float(_first_present(raw, "best_bid", "bestBidPrice", default=buy_prices[0] if buy_prices else None), default=None),
        "best_ask": _coerce_float(_first_present(raw, "best_ask", "bestAskPrice", default=sell_prices[0] if sell_prices else None), default=None),
        "best_bid_qty": _coerce_int(_first_present(raw, "best_bid_qty", "bestBidQuantity", default=buy_qty[0] if buy_qty else None), default=None),
        "best_ask_qty": _coerce_int(_first_present(raw, "best_ask_qty", "bestAskQuantity", default=sell_qty[0] if sell_qty else None), default=None),
        "bid_prices": buy_prices,
        "bid_qty": buy_qty,
        "ask_prices": sell_prices,
        "ask_qty": sell_qty,
    }


def normalize_raw_market_payload(
    *,
    broker_name: str,
    raw_payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Extract broker-aware market fields from the raw payload.
    """
    broker = broker_name.strip().lower()
    if broker == _BROKER_ZERODHA:
        return _extract_zerodha_market_payload(raw_payload)
    if broker == _BROKER_DHAN:
        return _extract_dhan_market_payload(raw_payload)
    return _extract_generic_market_payload(raw_payload)


def _dataset_from_instrument_type(instrument_type: str) -> CaptureDatasetName:
    upper = instrument_type.upper()
    if upper == "FUT":
        return CaptureDatasetName.TICKS_FUT
    if upper in {"CE", "PE"}:
        return CaptureDatasetName.TICKS_OPT
    raise ValueError(f"Unsupported instrument_type for capture normalization: {instrument_type!r}")


def _build_market_snapshot(market_payload: Mapping[str, Any]) -> tuple[MarketSnapshot, bool, bool, tuple[str, ...]]:
    ltp = _coerce_float(_first_present(market_payload, "ltp"), default=None)
    if ltp is None:
        raise ValueError("raw payload normalization requires ltp/last price")

    volume = _coerce_int(_first_present(market_payload, "volume"), default=0)
    if volume is None:
        volume = 0

    oi = _coerce_int(_first_present(market_payload, "oi"), default=None)
    missing_oi_flag = oi is None

    bid_prices = tuple(_first_present(market_payload, "bid_prices", default=()))
    bid_qty = tuple(_first_present(market_payload, "bid_qty", default=()))
    ask_prices = tuple(_first_present(market_payload, "ask_prices", default=()))
    ask_qty = tuple(_first_present(market_payload, "ask_qty", default=()))

    best_bid = _coerce_float(_first_present(market_payload, "best_bid"), default=None)
    best_ask = _coerce_float(_first_present(market_payload, "best_ask"), default=None)
    best_bid_qty = _coerce_int(_first_present(market_payload, "best_bid_qty"), default=None)
    best_ask_qty = _coerce_int(_first_present(market_payload, "best_ask_qty"), default=None)

    missing_depth_flag = not (bid_prices and ask_prices)
    integrity_flags: list[str] = []

    if missing_depth_flag:
        integrity_flags.append("missing_depth")
        (
            best_bid,
            best_ask,
            best_bid_qty,
            best_ask_qty,
            bid_prices,
            bid_qty,
            ask_prices,
            ask_qty,
        ) = _synthesize_top_book(
            ltp=ltp,
            best_bid=best_bid,
            best_ask=best_ask,
            best_bid_qty=best_bid_qty,
            best_ask_qty=best_ask_qty,
        )
        integrity_flags.append("synthetic_top_book")
    else:
        if best_bid is None:
            best_bid = bid_prices[0]
        if best_ask is None:
            best_ask = ask_prices[0]
        if best_bid_qty is None:
            best_bid_qty = bid_qty[0]
        if best_ask_qty is None:
            best_ask_qty = ask_qty[0]

    depth_levels_present_bid = len(bid_prices)
    depth_levels_present_ask = len(ask_prices)
    thin_book = depth_levels_present_bid <= 1 or depth_levels_present_ask <= 1 or sum(bid_qty) == 0 or sum(ask_qty) == 0
    if thin_book:
        integrity_flags.append("thin_book")
    if missing_oi_flag:
        integrity_flags.append("missing_oi")
    if not integrity_flags:
        integrity_flags.append("ok")

    snapshot = MarketSnapshot(
        ltp=ltp,
        volume=volume,
        price=_coerce_float(_first_present(market_payload, "price"), default=ltp),
        oi=oi,
        best_bid=best_bid,
        best_ask=best_ask,
        best_bid_qty=best_bid_qty,
        best_ask_qty=best_ask_qty,
        bid_prices=bid_prices,
        bid_qty=bid_qty,
        ask_prices=ask_prices,
        ask_qty=ask_qty,
        depth_levels_present_bid=depth_levels_present_bid,
        depth_levels_present_ask=depth_levels_present_ask,
        mid_price=(best_bid + best_ask) / 2.0 if best_bid is not None and best_ask is not None else ltp,
        microprice=((best_ask * (best_bid_qty or 0)) + (best_bid * (best_ask_qty or 0))) / max((best_bid_qty or 0) + (best_ask_qty or 0), 1)
        if best_bid is not None and best_ask is not None
        else ltp,
    )
    return snapshot, missing_depth_flag, thin_book, tuple(integrity_flags)


def _build_minimal_live_metrics(snapshot: MarketSnapshot) -> FieldBundle:
    spread = max((snapshot.best_ask or snapshot.ltp) - (snapshot.best_bid or snapshot.ltp), 0.0)
    denominator = snapshot.best_bid if snapshot.best_bid not in (None, 0.0) else snapshot.ltp if snapshot.ltp != 0 else 1.0
    spread_pct = spread / denominator
    sum_bid = sum(snapshot.bid_qty)
    sum_ask = sum(snapshot.ask_qty)
    nof = float(sum_bid) / float(max(sum_ask, 1))

    return FieldBundle(
        values={
            "spread": spread,
            "spread_pct": spread_pct,
            "sum_bid": sum_bid,
            "sum_ask": sum_ask,
            "nof": nof,
        },
        allowed_layers=(FieldLayer.LIVE_DERIVED_LIGHTWEIGHT,),
    )


def _build_strategy_audit_state(value: StrategyAuditState | Mapping[str, Any] | None) -> StrategyAuditState | None:
    if value is None:
        return None
    if isinstance(value, StrategyAuditState):
        return value
    if not isinstance(value, Mapping):
        raise TypeError("strategy_audit must be StrategyAuditState, Mapping, or None")
    return StrategyAuditState(**dict(value))


def normalize_broker_payload(
    *,
    broker_name: str,
    raw_payload: Mapping[str, Any],
    instrument_reference: InstrumentReference | Mapping[str, Any],
    normalization_context: NormalizationContext | Mapping[str, Any],
    anchor_context: AnchorContextInput | Mapping[str, Any] | None = None,
    session_metadata: SessionMetadataInput | Mapping[str, Any] | None = None,
    runtime_audit: RuntimeAuditInput | Mapping[str, Any] | None = None,
    strategy_audit: StrategyAuditState | Mapping[str, Any] | None = None,
) -> CaptureRecord:
    """
    Normalize one broker-aware raw payload into a canonical CaptureRecord.
    """
    broker = broker_name.strip().lower()
    if broker not in {_BROKER_ZERODHA, _BROKER_DHAN, _BROKER_GENERIC}:
        broker = _BROKER_GENERIC

    instrument_ref = (
        instrument_reference
        if isinstance(instrument_reference, InstrumentReference)
        else InstrumentReference.from_mapping(instrument_reference, broker_name=broker, raw_payload=raw_payload)
    )

    context = (
        normalization_context
        if isinstance(normalization_context, NormalizationContext)
        else NormalizationContext.from_mapping(normalization_context)
    )

    anchors = (
        AnchorContextInput()
        if anchor_context is None
        else anchor_context
        if isinstance(anchor_context, AnchorContextInput)
        else AnchorContextInput.from_mapping(anchor_context)
    )

    session_input = (
        SessionMetadataInput()
        if session_metadata is None
        else session_metadata
        if isinstance(session_metadata, SessionMetadataInput)
        else SessionMetadataInput.from_mapping(session_metadata)
    )

    runtime_input = (
        RuntimeAuditInput()
        if runtime_audit is None
        else runtime_audit
        if isinstance(runtime_audit, RuntimeAuditInput)
        else RuntimeAuditInput.from_mapping(runtime_audit)
    )

    market_payload = normalize_raw_market_payload(
        broker_name=broker,
        raw_payload=raw_payload,
    )

    source_ts_ns = context.source_ts_ns
    if source_ts_ns is None:
        source_ts_ns = _coerce_int(_first_present(market_payload, "source_ts_ns"), default=None)

    exchange_ts = _coerce_float(_first_present(market_payload, "exchange_ts"), default=None)
    if exchange_ts is None:
        if source_ts_ns is not None:
            exchange_ts = source_ts_ns / 1_000_000_000.0
        else:
            exchange_ts = context.recv_ts_ns / 1_000_000_000.0

    processed_ts = context.processed_ts if context.processed_ts is not None else context.process_ts_ns / 1_000_000_000.0
    network_time = context.network_time if context.network_time is not None else context.recv_ts_ns / 1_000_000_000.0

    timing = TimingIdentity(
        session_date=context.session_date,
        exchange_ts=exchange_ts,
        source_ts_ns=source_ts_ns,
        recv_ts_ns=context.recv_ts_ns,
        process_ts_ns=context.process_ts_ns,
        event_seq=context.event_seq,
        snapshot_id=context.snapshot_id,
        processed_ts=processed_ts,
        network_time=network_time,
    )

    instrument = InstrumentIdentity(
        broker_name=instrument_ref.broker_name,
        exchange=instrument_ref.exchange,
        exchange_segment=instrument_ref.exchange_segment,
        instrument_token=instrument_ref.instrument_token,
        tradingsymbol=instrument_ref.tradingsymbol,
        symbol=instrument_ref.symbol,
        symbol_token=instrument_ref.symbol_token,
        contract_name=instrument_ref.contract_name,
        instrument_type=instrument_ref.instrument_type,
        symbol_root=instrument_ref.symbol_root,
        underlying_symbol=instrument_ref.underlying_symbol,
        underlying_token=instrument_ref.underlying_token,
        option_type=instrument_ref.option_type,
        strike=instrument_ref.strike,
        expiry=instrument_ref.expiry,
        expiry_type=instrument_ref.expiry_type,
        tick_size=instrument_ref.tick_size,
        lot_size=instrument_ref.lot_size,
        freeze_qty=instrument_ref.freeze_qty,
        strike_step=instrument_ref.strike_step,
        moneyness_bucket=instrument_ref.moneyness_bucket,
    )

    market_snapshot, missing_depth_flag, thin_book, integrity_flags = _build_market_snapshot(market_payload)
    live_metrics = _build_minimal_live_metrics(market_snapshot)

    latency_ns = runtime_input.latency_ns
    if latency_ns is None and network_time is not None:
        latency_ns = int((network_time - exchange_ts) * 1_000_000_000)

    runtime_state = runtime_input.to_models_state(
        is_stale_tick=False,
        missing_depth_flag=missing_depth_flag,
        missing_oi_flag=market_snapshot.oi is None,
        thin_book=thin_book,
        integrity_flags=tuple(dict.fromkeys((*integrity_flags, *runtime_input.additional_integrity_flags))),
    )
    if latency_ns is not None or runtime_input.gap_from_prev_tick_ms is not None:
        runtime_state = RuntimeAuditState(
            is_stale_tick=runtime_state.is_stale_tick,
            stale_reason=runtime_state.stale_reason,
            missing_depth_flag=runtime_state.missing_depth_flag,
            missing_oi_flag=runtime_state.missing_oi_flag,
            thin_book=runtime_state.thin_book,
            book_is_thin=runtime_state.book_is_thin,
            crossed_book_flag=runtime_state.crossed_book_flag,
            locked_book_flag=runtime_state.locked_book_flag,
            integrity_flags=runtime_state.integrity_flags,
            fallback_used_flag=runtime_state.fallback_used_flag,
            fallback_source=runtime_state.fallback_source,
            schema_version=runtime_state.schema_version,
            normalization_version=runtime_state.normalization_version,
            derived_version=runtime_state.derived_version,
            calendar_version=runtime_state.calendar_version,
            heartbeat_status=runtime_state.heartbeat_status,
            reconnect_count=runtime_state.reconnect_count,
            last_reconnect_reason=runtime_state.last_reconnect_reason,
            gpu_fallback=runtime_state.gpu_fallback,
            cpu_mode_flag=runtime_state.cpu_mode_flag,
            latency_ns=latency_ns,
            gap_from_prev_tick_ms=runtime_input.gap_from_prev_tick_ms,
        )

    dataset = _dataset_from_instrument_type(instrument_ref.instrument_type)

    return CaptureRecord(
        dataset=dataset,
        timing=timing,
        instrument=instrument,
        market=market_snapshot,
        context=anchors.to_models_context(),
        session=session_input.to_models_context(
            session_date=context.session_date,
            instrument_reference=instrument_ref,
        ),
        live_metrics=live_metrics,
        runtime_audit=runtime_state,
        strategy_audit=_build_strategy_audit_state(strategy_audit),
    )


def normalize_zerodha_tick(
    *,
    raw_payload: Mapping[str, Any],
    instrument_reference: InstrumentReference | Mapping[str, Any],
    normalization_context: NormalizationContext | Mapping[str, Any],
    anchor_context: AnchorContextInput | Mapping[str, Any] | None = None,
    session_metadata: SessionMetadataInput | Mapping[str, Any] | None = None,
    runtime_audit: RuntimeAuditInput | Mapping[str, Any] | None = None,
    strategy_audit: StrategyAuditState | Mapping[str, Any] | None = None,
) -> CaptureRecord:
    """
    Normalize one Zerodha payload into a canonical CaptureRecord.
    """
    return normalize_broker_payload(
        broker_name=_BROKER_ZERODHA,
        raw_payload=raw_payload,
        instrument_reference=instrument_reference,
        normalization_context=normalization_context,
        anchor_context=anchor_context,
        session_metadata=session_metadata,
        runtime_audit=runtime_audit,
        strategy_audit=strategy_audit,
    )


def normalize_dhan_tick(
    *,
    raw_payload: Mapping[str, Any],
    instrument_reference: InstrumentReference | Mapping[str, Any],
    normalization_context: NormalizationContext | Mapping[str, Any],
    anchor_context: AnchorContextInput | Mapping[str, Any] | None = None,
    session_metadata: SessionMetadataInput | Mapping[str, Any] | None = None,
    runtime_audit: RuntimeAuditInput | Mapping[str, Any] | None = None,
    strategy_audit: StrategyAuditState | Mapping[str, Any] | None = None,
) -> CaptureRecord:
    """
    Normalize one Dhan payload into a canonical CaptureRecord.
    """
    return normalize_broker_payload(
        broker_name=_BROKER_DHAN,
        raw_payload=raw_payload,
        instrument_reference=instrument_reference,
        normalization_context=normalization_context,
        anchor_context=anchor_context,
        session_metadata=session_metadata,
        runtime_audit=runtime_audit,
        strategy_audit=strategy_audit,
    )


__all__ = [
    "AnchorContextInput",
    "InstrumentReference",
    "NormalizationContext",
    "RuntimeAuditInput",
    "SessionMetadataInput",
    "normalize_broker_payload",
    "normalize_dhan_tick",
    "normalize_raw_market_payload",
    "normalize_zerodha_tick",
]