"""
app/mme_scalpx/integrations/feed_adapter.py

Canonical feed-adapter integration boundary for ScalpX MME.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable

from app.mme_scalpx.domain.instruments import RuntimeInstrumentSet
from app.mme_scalpx.integrations.zerodha_feed_adapter import (
    FeedPollBundle,
    ZerodhaFeedAdapter,
)

VERSION = "mme-feed-adapter-v1-freeze"


def _to_epoch_ns(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        iv = int(value)
        return iv if iv > 0 else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.isdigit():
            iv = int(text)
            return iv if iv > 0 else None
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    elif isinstance(value, datetime):
        dt = value
    else:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return int(dt.timestamp() * 1_000_000_000)


def _to_feeds_payload(tick: dict[str, Any]) -> dict[str, Any]:
    depth = tick.get("depth") if isinstance(tick, dict) else {}
    if not isinstance(depth, dict):
        depth = {}

    buy = depth.get("buy")
    sell = depth.get("sell")
    best_buy = buy[0] if isinstance(buy, list) and buy else {}
    best_sell = sell[0] if isinstance(sell, list) and sell else {}

    if not isinstance(best_buy, dict):
        best_buy = {}
    if not isinstance(best_sell, dict):
        best_sell = {}

    return {
        "instrument_token": tick.get("instrument_token"),
        "last_price": tick.get("last_price"),
        "ltp": tick.get("last_price"),
        "best_bid": best_buy.get("price"),
        "best_ask": best_sell.get("price"),
        "best_bid_qty": best_buy.get("quantity"),
        "best_ask_qty": best_sell.get("quantity"),
        "bid_qty": best_buy.get("quantity"),
        "ask_qty": best_sell.get("quantity"),
        "exchange_ts_ns": _to_epoch_ns(tick.get("exchange_timestamp")),
        "depth": tick.get("depth"),
        "ohlc": tick.get("ohlc"),
        "volume_traded": tick.get("volume_traded"),
        "last_traded_quantity": tick.get("last_traded_quantity"),
        "total_buy_quantity": tick.get("total_buy_quantity"),
        "total_sell_quantity": tick.get("total_sell_quantity"),
        "mode": tick.get("mode"),
    }


class FeedAdapterError(RuntimeError):
    """Base feed adapter error."""


class FeedAdapterValidationError(FeedAdapterError):
    """Raised when adapter construction or usage is invalid."""


@runtime_checkable
class FeedAdapter(Protocol):
    def connect(self) -> None: ...
    def close(self) -> None: ...
    def is_connected(self) -> bool: ...
    def poll(self, timeout: float = 0.0) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class FeedAdapterInfo:
    adapter_name: str
    version: str
    broker: str
    mode: str


class BaseFeedAdapter:
    def info(self) -> FeedAdapterInfo:
        return FeedAdapterInfo(
            adapter_name=self.__class__.__name__,
            version=VERSION,
            broker="unknown",
            mode="base",
        )

    def connect(self) -> None:
        raise NotImplementedError("connect() not implemented")

    def close(self) -> None:
        raise NotImplementedError("close() not implemented")

    def is_connected(self) -> bool:
        raise NotImplementedError("is_connected() not implemented")

    def poll(self, timeout: float = 0.0) -> list[dict[str, Any]]:
        raise NotImplementedError("poll() not implemented")


class NullFeedAdapter(BaseFeedAdapter):
    def __init__(self) -> None:
        self._connected = False

    def info(self) -> FeedAdapterInfo:
        return FeedAdapterInfo(
            adapter_name=self.__class__.__name__,
            version=VERSION,
            broker="none",
            mode="null",
        )

    def connect(self) -> None:
        self._connected = False

    def close(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return False

    def poll(self, timeout: float = 0.0) -> list[dict[str, Any]]:
        return []


class ZerodhaLiveFeedAdapter(BaseFeedAdapter):
    def __init__(
        self,
        *,
        runtime_instruments: RuntimeInstrumentSet,
        connect_timeout_s: float = 15.0,
        poll_queue_size: int = 1024,
    ) -> None:
        if runtime_instruments is None:
            raise FeedAdapterValidationError("runtime_instruments must be provided")

        self._runtime_instruments = runtime_instruments
        self._transport = ZerodhaFeedAdapter(
            runtime_instruments=runtime_instruments,
            connect_timeout_s=connect_timeout_s,
            poll_queue_size=poll_queue_size,
        )
        self._connect_attempted = False

    def info(self) -> FeedAdapterInfo:
        return FeedAdapterInfo(
            adapter_name=self.__class__.__name__,
            version=VERSION,
            broker="zerodha",
            mode="live",
        )

    @property
    def runtime_instruments(self) -> RuntimeInstrumentSet:
        return self._runtime_instruments

    @property
    def subscribed_tokens(self) -> list[int]:
        return self._transport.subscribed_tokens

    @property
    def last_error(self) -> str | None:
        return self._transport.last_error

    def connect(self) -> None:
        self._transport.connect()
        self._connect_attempted = True

    def close(self) -> None:
        self._transport.close()

    def is_connected(self) -> bool:
        return self._transport.is_connected()

    def poll(self, timeout: float = 0.0) -> list[dict[str, Any]]:
        if not self.is_connected() and not self._connect_attempted:
            self.connect()

        bundle = self._transport.poll(timeout=timeout)

        if bundle is None:
            return []

        if isinstance(bundle, FeedPollBundle):
            ticks = bundle.ticks
        elif hasattr(bundle, "to_dict"):
            obj = bundle.to_dict()
            ticks = obj.get("ticks", [])
        elif isinstance(bundle, dict):
            ticks = bundle.get("ticks", [])
        else:
            raise FeedAdapterValidationError(
                f"unexpected transport poll bundle type: {type(bundle)!r}"
            )

        out: list[dict[str, Any]] = []
        for tick in ticks:
            if not isinstance(tick, dict):
                continue
            instrument_token = tick.get("instrument_token")
            if instrument_token is None:
                continue
            out.append(
                {
                    "instrument_token": str(instrument_token),
                    "payload": _to_feeds_payload(tick),
                    "provider": "ZERODHA",
                }
            )
        return out


def build_real_feed_adapter(
    *,
    runtime_instruments: RuntimeInstrumentSet,
    broker: str = "zerodha",
) -> FeedAdapter:
    broker_key = str(broker).strip().lower()
    if broker_key == "zerodha":
        return ZerodhaLiveFeedAdapter(runtime_instruments=runtime_instruments)
    raise FeedAdapterValidationError(f"unsupported real feed adapter broker: {broker!r}")
