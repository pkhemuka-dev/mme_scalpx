"""
app/mme_scalpx/integrations/broker_api.py

Canonical broker-adapter integration boundary for ScalpX MME.

Responsibilities
----------------
- define the stable broker adapter contract consumed by runtime services
- provide a null adapter for safe bootstrap/testing paths
- provide a thin real Zerodha-backed adapter wrapper over the authenticated
  KiteConnect REST path

Non-responsibilities
--------------------
- no websocket market data
- no Redis publication
- no runtime supervision
- no composition-root ownership
- no strategy/risk logic
- no position truth ownership (execution remains sole position truth)

Freeze rules
------------
- services must depend on this contract boundary, not broker SDK classes
- Zerodha REST/SDK details stay encapsulated in this file
- this adapter translates broker payloads into stable Python dictionaries
- no hidden order-shape invention beyond explicit validated parameters and
  optional extra_params passthrough
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Protocol, runtime_checkable

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
    from kiteconnect import KiteConnect  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "kiteconnect is required by app.mme_scalpx.integrations.broker_api"
    ) from exc


VERSION = "mme-broker-api-v1-freeze"


class BrokerAdapterError(RuntimeError):
    """Base broker adapter error."""


class BrokerAdapterValidationError(BrokerAdapterError):
    """Raised for config/session/argument validation errors."""


class BrokerAdapterRequestError(BrokerAdapterError):
    """Raised for broker request failures."""


@runtime_checkable
class BrokerAdapter(Protocol):
    """
    Stable broker-adapter contract for runtime service consumption.
    """

    def healthcheck(self) -> dict[str, Any]:
        ...

    def get_order(self, order_id: str) -> dict[str, Any]:
        ...

    def cancel_order(
        self,
        order_id: str,
        *,
        variety: str = "regular",
        parent_order_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def reconcile_position(self) -> dict[str, Any]:
        ...

    def reconcile_open_orders(self) -> dict[str, Any]:
        ...

    def place_entry_order(
        self,
        *,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str = "regular",
        price: Decimal | str | float | int | None = None,
        trigger_price: Decimal | str | float | int | None = None,
        validity: str = "DAY",
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    def place_exit_order(
        self,
        *,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str = "regular",
        price: Decimal | str | float | int | None = None,
        trigger_price: Decimal | str | float | int | None = None,
        validity: str = "DAY",
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class BrokerAdapterInfo:
    adapter_name: str
    version: str
    broker: str
    mode: str


def _decimal_to_str(value: Decimal | str | float | int | None) -> str | None:
    if value is None:
        return None
    try:
        return str(Decimal(str(value)))
    except (InvalidOperation, ValueError) as exc:
        raise BrokerAdapterValidationError(f"invalid decimal-like value: {value!r}") from exc


def _require_non_empty(value: str, *, field_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise BrokerAdapterValidationError(f"{field_name} must be non-empty")
    return text


def _require_positive_int(value: int, *, field_name: str) -> int:
    if int(value) <= 0:
        raise BrokerAdapterValidationError(f"{field_name} must be > 0")
    return int(value)


def _normalize_payload(payload: Any) -> Any:
    if isinstance(payload, Decimal):
        return str(payload)
    if isinstance(payload, list):
        return [_normalize_payload(x) for x in payload]
    if isinstance(payload, tuple):
        return [_normalize_payload(x) for x in payload]
    if isinstance(payload, dict):
        return {str(k): _normalize_payload(v) for k, v in payload.items()}
    return payload


def validate_api_config_for_zerodha(api: BrokerApiConfig) -> None:
    if api.broker.strip().lower() != "zerodha":
        raise BrokerAdapterValidationError(
            f"api.json broker must be 'zerodha', got {api.broker!r}"
        )
    if not api.api_key.strip():
        raise BrokerAdapterValidationError("api.json missing non-empty api_key")


def validate_token_state_for_zerodha(state: BrokerTokenState) -> None:
    if state.broker.strip().lower() != "zerodha":
        raise BrokerAdapterValidationError(
            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
        )
    if not state.access_token.strip():
        raise BrokerAdapterValidationError("tokens.json missing non-empty access_token")


class BaseBrokerAdapter:
    """
    Base convenience implementation for broker adapters.
    """

    def info(self) -> BrokerAdapterInfo:
        return BrokerAdapterInfo(
            adapter_name=self.__class__.__name__,
            version=VERSION,
            broker="unknown",
            mode="base",
        )

    def healthcheck(self) -> dict[str, Any]:
        raise NotImplementedError("healthcheck() not implemented")

    def get_order(self, order_id: str) -> dict[str, Any]:
        raise NotImplementedError("get_order() not implemented")

    def cancel_order(
        self,
        order_id: str,
        *,
        variety: str = "regular",
        parent_order_id: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError("cancel_order() not implemented")

    def reconcile_position(self) -> dict[str, Any]:
        raise NotImplementedError("reconcile_position() not implemented")

    def reconcile_open_orders(self) -> dict[str, Any]:
        raise NotImplementedError("reconcile_open_orders() not implemented")

    def place_entry_order(
        self,
        *,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str = "regular",
        price: Decimal | str | float | int | None = None,
        trigger_price: Decimal | str | float | int | None = None,
        validity: str = "DAY",
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError("place_entry_order() not implemented")

    def place_exit_order(
        self,
        *,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str = "regular",
        price: Decimal | str | float | int | None = None,
        trigger_price: Decimal | str | float | int | None = None,
        validity: str = "DAY",
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError("place_exit_order() not implemented")


class NullBrokerAdapter(BaseBrokerAdapter):
    """
    Safe no-op broker adapter for bootstrap/testing paths.
    """

    def info(self) -> BrokerAdapterInfo:
        return BrokerAdapterInfo(
            adapter_name=self.__class__.__name__,
            version=VERSION,
            broker="none",
            mode="null",
        )

    def healthcheck(self) -> dict[str, Any]:
        return {"ok": False, "broker": "none", "mode": "null"}

    def get_order(self, order_id: str) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "mode": "null",
            "order_id": str(order_id),
            "detail": "null broker adapter",
        }

    def cancel_order(
        self,
        order_id: str,
        *,
        variety: str = "regular",
        parent_order_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "mode": "null",
            "order_id": str(order_id),
            "variety": variety,
            "parent_order_id": parent_order_id,
            "detail": "null broker adapter",
        }

    def reconcile_position(self) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "mode": "null",
            "net": [],
            "day": [],
            "detail": "null broker adapter",
        }

    def reconcile_open_orders(self) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "mode": "null",
            "orders": [],
            "detail": "null broker adapter",
        }

    def place_entry_order(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "mode": "null",
            "intent": "entry",
            "request": _normalize_payload(kwargs),
            "detail": "null broker adapter",
        }

    def place_exit_order(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "mode": "null",
            "intent": "exit",
            "request": _normalize_payload(kwargs),
            "detail": "null broker adapter",
        }


class ZerodhaBrokerAdapter(BaseBrokerAdapter):
    """
    Canonical real broker adapter wrapping authenticated KiteConnect REST methods.
    """

    def __init__(self) -> None:
        try:
            api = load_api_config()
            state = load_token_state()
        except (
            SecretFileMissingError,
            SecretFileFormatError,
            TokenStoreError,
        ) as exc:
            raise BrokerAdapterValidationError(str(exc)) from exc

        validate_api_config_for_zerodha(api)
        validate_token_state_for_zerodha(state)

        self._api = api
        self._state = state
        self._kite = KiteConnect(api_key=api.api_key)
        self._kite.set_access_token(state.access_token)

    def info(self) -> BrokerAdapterInfo:
        return BrokerAdapterInfo(
            adapter_name=self.__class__.__name__,
            version=VERSION,
            broker="zerodha",
            mode="live",
        )

    def _place_order(
        self,
        *,
        intent: str,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str = "regular",
        price: Decimal | str | float | int | None = None,
        trigger_price: Decimal | str | float | int | None = None,
        validity: str = "DAY",
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tradingsymbol = _require_non_empty(tradingsymbol, field_name="tradingsymbol")
        exchange = _require_non_empty(exchange, field_name="exchange").upper()
        transaction_type = _require_non_empty(
            transaction_type, field_name="transaction_type"
        ).upper()
        product = _require_non_empty(product, field_name="product").upper()
        order_type = _require_non_empty(order_type, field_name="order_type").upper()
        variety = _require_non_empty(variety, field_name="variety")
        validity = _require_non_empty(validity, field_name="validity").upper()
        quantity = _require_positive_int(quantity, field_name="quantity")

        params: dict[str, Any] = {
            "variety": variety,
            "exchange": exchange,
            "tradingsymbol": tradingsymbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "product": product,
            "order_type": order_type,
            "validity": validity,
        }

        price_text = _decimal_to_str(price)
        if price_text is not None:
            params["price"] = price_text

        trigger_text = _decimal_to_str(trigger_price)
        if trigger_text is not None:
            params["trigger_price"] = trigger_text

        if tag:
            params["tag"] = str(tag).strip()

        if extra_params:
            if not isinstance(extra_params, dict):
                raise BrokerAdapterValidationError("extra_params must be a dict if provided")
            for key, value in extra_params.items():
                params[str(key)] = value

        try:
            order_id = self._kite.place_order(**params)
        except Exception as exc:
            raise BrokerAdapterRequestError(
                f"place_{intent}_order failed: {exc}"
            ) from exc

        return {
            "ok": True,
            "broker": "zerodha",
            "intent": intent,
            "order_id": str(order_id),
            "request": _normalize_payload(params),
        }

    def healthcheck(self) -> dict[str, Any]:
        try:
            profile = self._kite.profile()
        except Exception as exc:
            raise BrokerAdapterRequestError(f"healthcheck profile() failed: {exc}") from exc

        user_id = None
        if isinstance(profile, dict):
            user_id = str(profile.get("user_id", "")).strip() or None

        return {
            "ok": True,
            "broker": "zerodha",
            "user_id": user_id,
            "profile": _normalize_payload(profile),
        }

    def get_order(self, order_id: str) -> dict[str, Any]:
        order_id = _require_non_empty(order_id, field_name="order_id")
        try:
            orders = self._kite.orders()
        except Exception as exc:
            raise BrokerAdapterRequestError(f"orders() failed during get_order: {exc}") from exc

        if not isinstance(orders, list):
            raise BrokerAdapterRequestError("orders() returned non-list payload")

        matches = [row for row in orders if str(row.get("order_id", "")).strip() == order_id]
        if not matches:
            return {
                "ok": False,
                "broker": "zerodha",
                "order_id": order_id,
                "found": False,
                "order": None,
            }

        return {
            "ok": True,
            "broker": "zerodha",
            "order_id": order_id,
            "found": True,
            "order": _normalize_payload(matches[-1]),
        }

    def cancel_order(
        self,
        order_id: str,
        *,
        variety: str = "regular",
        parent_order_id: str | None = None,
    ) -> dict[str, Any]:
        order_id = _require_non_empty(order_id, field_name="order_id")
        variety = _require_non_empty(variety, field_name="variety")

        params: dict[str, Any] = {
            "variety": variety,
            "order_id": order_id,
        }
        if parent_order_id:
            params["parent_order_id"] = str(parent_order_id).strip()

        try:
            result = self._kite.cancel_order(**params)
        except Exception as exc:
            raise BrokerAdapterRequestError(f"cancel_order failed: {exc}") from exc

        return {
            "ok": True,
            "broker": "zerodha",
            "order_id": order_id,
            "cancel_result": _normalize_payload(result),
            "request": _normalize_payload(params),
        }

    def reconcile_position(self) -> dict[str, Any]:
        try:
            positions = self._kite.positions()
        except Exception as exc:
            raise BrokerAdapterRequestError(f"positions() failed: {exc}") from exc

        if not isinstance(positions, dict):
            raise BrokerAdapterRequestError("positions() returned non-dict payload")

        return {
            "ok": True,
            "broker": "zerodha",
            "net": _normalize_payload(positions.get("net", [])),
            "day": _normalize_payload(positions.get("day", [])),
            "raw": _normalize_payload(positions),
        }

    def reconcile_open_orders(self) -> dict[str, Any]:
        try:
            orders = self._kite.orders()
        except Exception as exc:
            raise BrokerAdapterRequestError(f"orders() failed: {exc}") from exc

        if not isinstance(orders, list):
            raise BrokerAdapterRequestError("orders() returned non-list payload")

        terminal_statuses = {
            "COMPLETE",
            "CANCELLED",
            "REJECTED",
        }
        open_orders = []
        for row in orders:
            if not isinstance(row, dict):
                continue
            status = str(row.get("status", "")).strip().upper()
            if status not in terminal_statuses:
                open_orders.append(row)

        return {
            "ok": True,
            "broker": "zerodha",
            "orders": _normalize_payload(open_orders),
            "count": len(open_orders),
        }

    def place_entry_order(
        self,
        *,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str = "regular",
        price: Decimal | str | float | int | None = None,
        trigger_price: Decimal | str | float | int | None = None,
        validity: str = "DAY",
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._place_order(
            intent="entry",
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            product=product,
            order_type=order_type,
            variety=variety,
            price=price,
            trigger_price=trigger_price,
            validity=validity,
            tag=tag,
            extra_params=extra_params,
        )

    def place_exit_order(
        self,
        *,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str = "regular",
        price: Decimal | str | float | int | None = None,
        trigger_price: Decimal | str | float | int | None = None,
        validity: str = "DAY",
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._place_order(
            intent="exit",
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            product=product,
            order_type=order_type,
            variety=variety,
            price=price,
            trigger_price=trigger_price,
            validity=validity,
            tag=tag,
            extra_params=extra_params,
        )


def build_real_broker_adapter(*, broker: str = "zerodha") -> BrokerAdapter:
    """
    Thin factory for runtime/provider wiring.

    Current proven live implementation:
    - zerodha
    """
    broker_key = str(broker).strip().lower()
    if broker_key == "zerodha":
        return ZerodhaBrokerAdapter()
    raise BrokerAdapterValidationError(f"unsupported real broker adapter broker: {broker!r}")
