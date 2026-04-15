"""
app/mme_scalpx/integrations/zerodha_feed_adapter.py

Freeze-grade real Zerodha websocket feed adapter for ScalpX MME.

Responsibilities
----------------
- build authenticated KiteTicker from persisted api/token state
- subscribe to canonical runtime instruments
- receive live websocket ticks
- normalize ticks into a deterministic poll()-based bundle
- expose close()/is_connected()/poll() for caller-side control

Non-responsibilities
--------------------
- no Redis publication
- no feature extraction
- no snapshot ownership outside adapter memory
- no order placement
- no runtime supervision
- no composition-root ownership

Notes
-----
- This adapter is transport-real and contract-light.
- It intentionally returns a normalized tick bundle via poll().
- Final feeds.py wiring should happen only after confirming the exact downstream
  poll consumption contract.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from app.mme_scalpx.domain.instruments import RuntimeInstrumentSet
from app.mme_scalpx.integrations.token_store import (
    BrokerApiConfig,
    BrokerTokenState,
    SecretFileFormatError,
    SecretFileMissingError,
    TokenStoreError,
    load_api_config,
    load_token_state,
)

try:
    from kiteconnect import KiteTicker  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "kiteconnect is required by app.mme_scalpx.integrations.zerodha_feed_adapter"
    ) from exc


class ZerodhaFeedAdapterError(RuntimeError):
    """Base adapter error."""


class StartupValidationError(ZerodhaFeedAdapterError):
    """Raised for fail-fast config/session issues."""


class AdapterConnectionError(ZerodhaFeedAdapterError):
    """Raised when websocket connection or subscription fails."""


@dataclass(frozen=True)
class SubscribedInstrument:
    family: str
    instrument_token: int
    tradingsymbol: str
    exchange: str
    segment: str
    kind: str


@dataclass(frozen=True)
class NormalizedTick:
    family: str
    instrument_token: int
    tradingsymbol: str
    exchange: str
    segment: str
    kind: str
    mode: str
    received_at_utc: str
    exchange_timestamp: str | None
    last_price: str | None
    last_traded_quantity: int | None
    average_traded_price: str | None
    volume_traded: int | None
    total_buy_quantity: int | None
    total_sell_quantity: int | None
    ohlc: dict[str, str | None]
    depth: dict[str, list[dict[str, Any]]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "instrument_token": self.instrument_token,
            "tradingsymbol": self.tradingsymbol,
            "exchange": self.exchange,
            "segment": self.segment,
            "kind": self.kind,
            "mode": self.mode,
            "received_at_utc": self.received_at_utc,
            "exchange_timestamp": self.exchange_timestamp,
            "last_price": self.last_price,
            "last_traded_quantity": self.last_traded_quantity,
            "average_traded_price": self.average_traded_price,
            "volume_traded": self.volume_traded,
            "total_buy_quantity": self.total_buy_quantity,
            "total_sell_quantity": self.total_sell_quantity,
            "ohlc": self.ohlc,
            "depth": self.depth,
        }


@dataclass(frozen=True)
class FeedPollBundle:
    received_at_utc: str
    connected: bool
    tick_count: int
    ticks: list[dict[str, Any]]
    by_family: dict[str, dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "received_at_utc": self.received_at_utc,
            "connected": self.connected,
            "tick_count": self.tick_count,
            "ticks": self.ticks,
            "by_family": self.by_family,
        }


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_decimal_string(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return str(Decimal(str(value)))
    except (InvalidOperation, ValueError):
        return str(value)


def validate_api_config_for_zerodha(api: BrokerApiConfig) -> None:
    if api.broker.strip().lower() != "zerodha":
        raise StartupValidationError(
            f"api.json broker must be 'zerodha', got {api.broker!r}"
        )
    if not api.api_key.strip():
        raise StartupValidationError("api.json missing non-empty api_key")


def validate_token_state_for_zerodha(state: BrokerTokenState) -> None:
    if state.broker.strip().lower() != "zerodha":
        raise StartupValidationError(
            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
        )
    if not state.access_token.strip():
        raise StartupValidationError("tokens.json missing non-empty access_token")


def _instrument_token_of(contract: Any) -> int:
    raw = getattr(contract, "instrument_token", "")
    try:
        return int(str(raw))
    except Exception as exc:
        raise StartupValidationError(
            f"invalid instrument_token on runtime contract {getattr(contract, 'tradingsymbol', '?')}: {raw!r}"
        ) from exc


def _subscription_map(runtime_instruments: RuntimeInstrumentSet) -> dict[int, SubscribedInstrument]:
    entries = {
        "future": runtime_instruments.current_future,
        "ce_atm": runtime_instruments.ce_atm,
        "ce_atm1": runtime_instruments.ce_atm1,
        "pe_atm": runtime_instruments.pe_atm,
        "pe_atm1": runtime_instruments.pe_atm1,
    }

    mapping: dict[int, SubscribedInstrument] = {}
    for family, contract in entries.items():
        token = _instrument_token_of(contract)
        mapping[token] = SubscribedInstrument(
            family=family,
            instrument_token=token,
            tradingsymbol=contract.tradingsymbol,
            exchange=contract.exchange.value,
            segment=contract.segment,
            kind=contract.kind.value,
        )
    return mapping


def _normalize_ohlc(raw: Any) -> dict[str, str | None]:
    obj = raw if isinstance(raw, dict) else {}
    return {
        "open": _to_decimal_string(obj.get("open")),
        "high": _to_decimal_string(obj.get("high")),
        "low": _to_decimal_string(obj.get("low")),
        "close": _to_decimal_string(obj.get("close")),
    }


def _normalize_depth(raw: Any) -> dict[str, list[dict[str, Any]]]:
    obj = raw if isinstance(raw, dict) else {}
    depth: dict[str, list[dict[str, Any]]] = {"buy": [], "sell": []}
    for side in ("buy", "sell"):
        rows = obj.get(side)
        if not isinstance(rows, list):
            continue
        norm_rows: list[dict[str, Any]] = []
        for item in rows:
            if not isinstance(item, dict):
                continue
            norm_rows.append(
                {
                    "price": _to_decimal_string(item.get("price")),
                    "quantity": item.get("quantity"),
                    "orders": item.get("orders"),
                }
            )
        depth[side] = norm_rows
    return depth


def _normalize_tick(tick: dict[str, Any], subscribed: SubscribedInstrument) -> NormalizedTick:
    exchange_timestamp = tick.get("exchange_timestamp")
    if isinstance(exchange_timestamp, datetime):
        exchange_timestamp_text = (
            exchange_timestamp.replace(tzinfo=timezone.utc).isoformat()
            if exchange_timestamp.tzinfo is None
            else exchange_timestamp.astimezone(timezone.utc).isoformat()
        )
    else:
        exchange_timestamp_text = str(exchange_timestamp) if exchange_timestamp is not None else None

    return NormalizedTick(
        family=subscribed.family,
        instrument_token=subscribed.instrument_token,
        tradingsymbol=subscribed.tradingsymbol,
        exchange=subscribed.exchange,
        segment=subscribed.segment,
        kind=subscribed.kind,
        mode=str(tick.get("mode", "")),
        received_at_utc=_now_utc_iso(),
        exchange_timestamp=exchange_timestamp_text,
        last_price=_to_decimal_string(tick.get("last_price")),
        last_traded_quantity=tick.get("last_traded_quantity"),
        average_traded_price=_to_decimal_string(tick.get("average_traded_price")),
        volume_traded=tick.get("volume_traded"),
        total_buy_quantity=tick.get("total_buy_quantity"),
        total_sell_quantity=tick.get("total_sell_quantity"),
        ohlc=_normalize_ohlc(tick.get("ohlc")),
        depth=_normalize_depth(tick.get("depth")),
    )


class ZerodhaFeedAdapter:
    """
    Real Zerodha websocket transport adapter with poll()-based consumption.
    """

    def __init__(
        self,
        *,
        runtime_instruments: RuntimeInstrumentSet,
        connect_timeout_s: float = 15.0,
        poll_queue_size: int = 1024,
    ) -> None:
        try:
            api = load_api_config()
            state = load_token_state()
        except (
            SecretFileMissingError,
            SecretFileFormatError,
            TokenStoreError,
        ) as exc:
            raise StartupValidationError(str(exc)) from exc

        validate_api_config_for_zerodha(api)
        validate_token_state_for_zerodha(state)

        self._api = api
        self._state = state
        self._runtime_instruments = runtime_instruments
        self._subscriptions = _subscription_map(runtime_instruments)
        self._tokens = sorted(self._subscriptions.keys())

        self._queue: queue.Queue[FeedPollBundle] = queue.Queue(maxsize=max(1, poll_queue_size))
        self._ticker = KiteTicker(api.api_key, state.access_token)
        self._connect_timeout_s = connect_timeout_s

        self._connected = threading.Event()
        self._failed = threading.Event()
        self._closed = threading.Event()
        self._last_error: str | None = None

        self._ticker.on_connect = self._on_connect
        self._ticker.on_ticks = self._on_ticks
        self._ticker.on_close = self._on_close
        self._ticker.on_error = self._on_error
        self._ticker.on_reconnect = self._on_reconnect
        self._ticker.on_noreconnect = self._on_noreconnect

    @property
    def subscribed_tokens(self) -> list[int]:
        return list(self._tokens)

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def is_connected(self) -> bool:
        return self._connected.is_set() and not self._closed.is_set() and not self._failed.is_set()

    def connect(self) -> None:
        self._ticker.connect(threaded=True)

        deadline = time.time() + self._connect_timeout_s
        while time.time() < deadline:
            if self._connected.is_set():
                return
            if self._failed.is_set():
                raise AdapterConnectionError(self._last_error or "websocket connect failed")
            time.sleep(0.05)

        raise AdapterConnectionError(
            f"websocket connect timeout after {self._connect_timeout_s}s"
        )

    def close(self) -> None:
        self._closed.set()
        try:
            self._ticker.close()
        except Exception:
            pass

    def poll(self, timeout: float = 0.0) -> FeedPollBundle | None:
        """
        Drain and return the latest available normalized bundle.

        Returns None if no bundle is available within timeout.
        """
        try:
            first = self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

        latest = first
        while True:
            try:
                latest = self._queue.get_nowait()
            except queue.Empty:
                break
        return latest

    def _safe_put(self, bundle: FeedPollBundle) -> None:
        try:
            self._queue.put_nowait(bundle)
        except queue.Full:
            try:
                _ = self._queue.get_nowait()
            except queue.Empty:
                pass
            self._queue.put_nowait(bundle)

    def _on_connect(self, ws: Any, response: Any) -> None:
        try:
            ws.subscribe(self._tokens)
            ws.set_mode(ws.MODE_FULL, self._tokens)
            self._connected.set()
        except Exception as exc:
            self._last_error = f"subscription/setup failed: {exc}"
            self._failed.set()

    def _on_ticks(self, ws: Any, ticks: list[dict[str, Any]]) -> None:
        normalized_ticks: list[dict[str, Any]] = []
        by_family: dict[str, dict[str, Any]] = {}

        for tick in ticks:
            try:
                token = int(tick.get("instrument_token"))
            except Exception:
                continue

            subscribed = self._subscriptions.get(token)
            if subscribed is None:
                continue

            normalized = _normalize_tick(tick, subscribed)
            payload = normalized.to_dict()
            normalized_ticks.append(payload)
            by_family[subscribed.family] = payload

        if not normalized_ticks:
            return

        bundle = FeedPollBundle(
            received_at_utc=_now_utc_iso(),
            connected=self.is_connected(),
            tick_count=len(normalized_ticks),
            ticks=normalized_ticks,
            by_family=by_family,
        )
        self._safe_put(bundle)

    def _on_close(self, ws: Any, code: Any, reason: Any) -> None:
        self._closed.set()
        if reason:
            self._last_error = f"closed code={code} reason={reason}"

    def _on_error(self, ws: Any, code: Any, reason: Any) -> None:
        self._last_error = f"error code={code} reason={reason}"
        self._failed.set()

    def _on_reconnect(self, ws: Any, attempts_count: Any) -> None:
        # informational only; leave state intact
        return

    def _on_noreconnect(self, ws: Any) -> None:
        self._last_error = self._last_error or "websocket gave up reconnecting"
        self._failed.set()
