from __future__ import annotations

"""
app/mme_scalpx/integrations/broker_api.py

Freeze-grade broker adapter contract and provider-aware execution seam for ScalpX MME.

Purpose
-------
This module OWNS:
- broker adapter protocol surface consumed by execution/bootstrap
- normalized order / cancel / position / open-order adapter behavior
- broker-auth attachment for execution-capable adapters
- provider-aware adapter metadata and capability truth
- canonical open-orders normalization to list[Mapping[str, Any]] | None
- compatibility builder surface for bootstrap_provider.py

This module DOES NOT own:
- broker login/session lifecycle policy
- provider-runtime role resolution
- websocket lifecycle / live feed handling
- strategy logic
- Redis IO
- main.py composition
- Dhan market-data orchestration

Important contract laws
-----------------------
- execution.py remains the sole broker-truth owner.
- broker_api.py is an integration seam only.
- reconcile_open_orders() must return only:
  - None
  - list[Mapping[str, Any]]
  Never a wrapper dict.
- auth/session truth is consumed from broker_auth.py.
- this module stays model-light to avoid drift with the parallel core.models lane.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol, Sequence, runtime_checkable

from app.mme_scalpx.core import names
from app.mme_scalpx.core.validators import (
    ValidationError,
    require_bool,
    require_int,
    require_literal,
    require_mapping,
    require_non_empty_str,
)
from app.mme_scalpx.integrations.broker_auth import (
    BrokerAuthManager,
    BrokerAuthSnapshot,
    BrokerSessionUnavailableError,
)

VERSION = "mme-broker-api-freeze-v2"

# ============================================================================
# Compatibility fallbacks against frozen names surfaces
# ============================================================================

_ALLOWED_PROVIDER_IDS: tuple[str, ...] = tuple(
    getattr(
        names,
        "ALLOWED_PROVIDER_IDS",
        getattr(
            names,
            "PROVIDER_IDS",
            (
                names.PROVIDER_ZERODHA,
                names.PROVIDER_DHAN,
            ),
        ),
    )
)

PROVIDER_ZERODHA = getattr(names, "PROVIDER_ZERODHA", "ZERODHA")
PROVIDER_DHAN = getattr(names, "PROVIDER_DHAN", "DHAN")

# ============================================================================
# Exceptions
# ============================================================================


class BrokerAdapterError(RuntimeError):
    """Base error for broker-adapter failures."""


class BrokerAdapterValidationError(BrokerAdapterError):
    """Raised when broker-adapter config or inputs are invalid."""


class BrokerAdapterAuthError(BrokerAdapterError):
    """Raised when broker-auth/session is unavailable for an adapter call."""


class BrokerAdapterRequestError(BrokerAdapterError):
    """Raised when a broker transport request fails or returns invalid data."""


class BrokerAdapterUnavailableError(BrokerAdapterError):
    """Raised when no usable transport client is configured."""


# ============================================================================
# Shared validator wrappers
# ============================================================================


def _wrap_validation(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        if isinstance(exc, BrokerAdapterValidationError):
            raise
        if isinstance(exc, ValidationError):
            raise BrokerAdapterValidationError(str(exc)) from exc
        raise BrokerAdapterValidationError(str(exc)) from exc


def _require_non_empty(value: str, *, field_name: str) -> str:
    return _wrap_validation(require_non_empty_str, value, field_name=field_name)


def _require_bool(value: bool, *, field_name: str) -> bool:
    return _wrap_validation(require_bool, value, field_name=field_name)


def _require_int(
    value: int,
    *,
    field_name: str,
    min_value: int | None = None,
) -> int:
    return _wrap_validation(
        require_int,
        value,
        field_name=field_name,
        min_value=min_value,
    )


def _require_literal(
    value: str,
    *,
    field_name: str,
    allowed: Sequence[str],
) -> str:
    return _wrap_validation(
        require_literal,
        value,
        field_name=field_name,
        allowed=allowed,
    )


def _require_mapping(
    value: Mapping[str, object],
    *,
    field_name: str,
) -> dict[str, object]:
    return _wrap_validation(require_mapping, value, field_name=field_name)


def _freeze_mapping(data: Mapping[str, Any] | None) -> Mapping[str, Any]:
    raw = {} if data is None else dict(data)
    return MappingProxyType(raw)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_now() -> str:
    return _utc_now().isoformat()


def _provider_code(provider_id: str) -> str:
    provider_id = _require_literal(
        provider_id,
        field_name="provider_id",
        allowed=_ALLOWED_PROVIDER_IDS,
    )
    return provider_id.strip().lower()


def _normalize_payload(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc).isoformat()
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, Mapping):
        return {str(k): _normalize_payload(v) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_payload(item) for item in value]
    return str(value)


def _coerce_order_price(
    value: Decimal | str | float | int | None,
    *,
    field_name: str,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise BrokerAdapterValidationError(f"{field_name} must be numeric or None")
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    text = _require_non_empty(str(value), field_name=field_name)
    try:
        return float(text)
    except ValueError as exc:
        raise BrokerAdapterValidationError(
            f"{field_name} must be numeric-like, got {value!r}"
        ) from exc


def _normalize_mapping_list(
    payload: Sequence[Any],
    *,
    field_name: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    bad_types: list[str] = []
    for item in payload:
        if not isinstance(item, Mapping):
            bad_types.append(type(item).__name__)
            continue
        out.append({str(k): _normalize_payload(v) for k, v in item.items()})
    if bad_types:
        raise BrokerAdapterRequestError(
            f"{field_name} contains non-mapping items: {bad_types!r}"
        )
    return out


# ============================================================================
# Public protocols
# ============================================================================


@runtime_checkable
class BrokerTransportClient(Protocol):
    """Protocol for provider-specific execution/order reconciliation transport."""

    def healthcheck(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        ...

    def get_order(
        self,
        order_id: str,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        ...

    def place_order(
        self,
        payload: Mapping[str, Any],
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        ...

    def cancel_order(
        self,
        order_id: str,
        payload: Mapping[str, Any] | None = None,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        ...

    def reconcile_positions(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        ...

    def reconcile_open_orders(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        ...


@runtime_checkable
class BrokerAdapter(Protocol):
    """Canonical adapter surface consumed by bootstrap and execution."""

    def info(self) -> "BrokerAdapterInfo":
        ...

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

    def reconcile_open_orders(self) -> list[Mapping[str, Any]] | None:
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


# ============================================================================
# Public value objects
# ============================================================================


@dataclass(frozen=True, slots=True)
class BrokerAdapterInfo:
    adapter_name: str
    version: str
    provider_id: str
    broker: str
    mode: str
    requires_auth: bool
    execution_supported: bool
    transport_configured: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "adapter_name",
            _require_non_empty(self.adapter_name, field_name="adapter_name"),
        )
        object.__setattr__(
            self,
            "version",
            _require_non_empty(self.version, field_name="version"),
        )
        object.__setattr__(
            self,
            "provider_id",
            _require_literal(
                self.provider_id,
                field_name="provider_id",
                allowed=_ALLOWED_PROVIDER_IDS,
            ),
        )
        object.__setattr__(
            self,
            "broker",
            _require_non_empty(self.broker, field_name="broker"),
        )
        object.__setattr__(
            self,
            "mode",
            _require_non_empty(self.mode, field_name="mode"),
        )
        object.__setattr__(
            self,
            "requires_auth",
            _require_bool(self.requires_auth, field_name="requires_auth"),
        )
        object.__setattr__(
            self,
            "execution_supported",
            _require_bool(self.execution_supported, field_name="execution_supported"),
        )
        object.__setattr__(
            self,
            "transport_configured",
            _require_bool(self.transport_configured, field_name="transport_configured"),
        )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_name": self.adapter_name,
            "version": self.version,
            "provider_id": self.provider_id,
            "broker": self.broker,
            "mode": self.mode,
            "requires_auth": self.requires_auth,
            "execution_supported": self.execution_supported,
            "transport_configured": self.transport_configured,
            "metadata": dict(self.metadata),
        }


# ============================================================================
# Generic callable transport
# ============================================================================


@dataclass(frozen=True, slots=True)
class CallableBrokerTransportClient:
    """
    Thin callable-based transport for tests, bootstrap shims, or composition.

    Each callable receives keyword arguments exactly as documented by the
    BrokerTransportClient protocol.
    """

    healthcheck_fn: Callable[..., Any] | None = None
    get_order_fn: Callable[..., Any] | None = None
    place_order_fn: Callable[..., Any] | None = None
    cancel_order_fn: Callable[..., Any] | None = None
    reconcile_positions_fn: Callable[..., Any] | None = None
    reconcile_open_orders_fn: Callable[..., Any] | None = None

    def healthcheck(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        if self.healthcheck_fn is None:
            return {"ok": True, "provider_id": provider_id, "mode": "callable"}
        return self.healthcheck_fn(access_token=access_token, provider_id=provider_id)

    def get_order(
        self,
        order_id: str,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        if self.get_order_fn is None:
            raise BrokerAdapterUnavailableError("get_order_fn not configured")
        return self.get_order_fn(
            order_id,
            access_token=access_token,
            provider_id=provider_id,
        )

    def place_order(
        self,
        payload: Mapping[str, Any],
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        if self.place_order_fn is None:
            raise BrokerAdapterUnavailableError("place_order_fn not configured")
        return self.place_order_fn(
            payload,
            access_token=access_token,
            provider_id=provider_id,
        )

    def cancel_order(
        self,
        order_id: str,
        payload: Mapping[str, Any] | None = None,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        if self.cancel_order_fn is None:
            raise BrokerAdapterUnavailableError("cancel_order_fn not configured")
        return self.cancel_order_fn(
            order_id,
            payload,
            access_token=access_token,
            provider_id=provider_id,
        )

    def reconcile_positions(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        if self.reconcile_positions_fn is None:
            raise BrokerAdapterUnavailableError("reconcile_positions_fn not configured")
        return self.reconcile_positions_fn(
            access_token=access_token,
            provider_id=provider_id,
        )

    def reconcile_open_orders(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        if self.reconcile_open_orders_fn is None:
            raise BrokerAdapterUnavailableError(
                "reconcile_open_orders_fn not configured"
            )
        return self.reconcile_open_orders_fn(
            access_token=access_token,
            provider_id=provider_id,
        )


# ============================================================================
# Convenience zerodha transport wrapper
# ============================================================================


@dataclass(frozen=True, slots=True)
class KiteTransportClient:
    """
    Thin wrapper around a kite-like client.

    Required methods on the supplied object:
    - orders()
    - positions()
    - place_order(**payload)
    - cancel_order(order_id=..., variety=..., parent_order_id=...)
    Optional:
    - order_history(order_id)
    - profile()

    This wrapper deliberately does not instantiate KiteConnect itself.
    Composition remains external.
    """

    kite: Any

    def healthcheck(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        if hasattr(self.kite, "profile"):
            return self.kite.profile()
        return {"ok": True, "provider_id": provider_id, "mode": "kite-wrapper"}

    def get_order(
        self,
        order_id: str,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        order_id = _require_non_empty(order_id, field_name="order_id")
        if hasattr(self.kite, "order_history"):
            return self.kite.order_history(order_id)
        if hasattr(self.kite, "orders"):
            orders = self.kite.orders()
            if isinstance(orders, list):
                for row in orders:
                    if isinstance(row, Mapping) and str(row.get("order_id", "")).strip() == order_id:
                        return row
            return None
        raise BrokerAdapterUnavailableError(
            "kite client exposes neither order_history() nor orders()"
        )

    def place_order(
        self,
        payload: Mapping[str, Any],
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        result = self.kite.place_order(**dict(payload))
        if isinstance(result, Mapping):
            return result
        return {"order_id": result}

    def cancel_order(
        self,
        order_id: str,
        payload: Mapping[str, Any] | None = None,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        kwargs = dict(payload or {})
        kwargs.setdefault("order_id", order_id)
        result = self.kite.cancel_order(**kwargs)
        if isinstance(result, Mapping):
            return result
        return {"order_id": order_id, "cancel_result": result}

    def reconcile_positions(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        return self.kite.positions()

    def reconcile_open_orders(
        self,
        *,
        access_token: str | None = None,
        provider_id: str | None = None,
    ) -> Any:
        return self.kite.orders()


# ============================================================================
# Base broker adapter
# ============================================================================


@dataclass(slots=True)
class BaseBrokerAdapter:
    provider_id: str
    broker: str
    mode: str = "base"
    transport_client: BrokerTransportClient | None = None
    auth_manager: BrokerAuthManager | None = None
    requires_auth: bool = False
    default_exchange: str = "NFO"
    default_product: str = "NRML"
    default_variety: str = "regular"
    default_validity: str = "DAY"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.provider_id = _require_literal(
            self.provider_id,
            field_name="provider_id",
            allowed=_ALLOWED_PROVIDER_IDS,
        )
        self.broker = _require_non_empty(self.broker, field_name="broker")
        self.mode = _require_non_empty(self.mode, field_name="mode")
        self.requires_auth = _require_bool(
            self.requires_auth,
            field_name="requires_auth",
        )
        self.default_exchange = _require_non_empty(
            self.default_exchange,
            field_name="default_exchange",
        ).upper()
        self.default_product = _require_non_empty(
            self.default_product,
            field_name="default_product",
        ).upper()
        self.default_variety = _require_non_empty(
            self.default_variety,
            field_name="default_variety",
        )
        self.default_validity = _require_non_empty(
            self.default_validity,
            field_name="default_validity",
        ).upper()
        self.metadata = _freeze_mapping(self.metadata)

    # ------------------------------------------------------------------
    # Public adapter API
    # ------------------------------------------------------------------

    def info(self) -> BrokerAdapterInfo:
        return BrokerAdapterInfo(
            adapter_name=self.__class__.__name__,
            version=VERSION,
            provider_id=self.provider_id,
            broker=self.broker,
            mode=self.mode,
            requires_auth=self.requires_auth,
            execution_supported=True,
            transport_configured=self.transport_client is not None,
            metadata=self.metadata,
        )

    def healthcheck(self) -> dict[str, Any]:
        auth_snapshot = self._auth_snapshot()
        if self.transport_client is None:
            return {
                "ok": False,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "mode": self.mode,
                "auth": None if auth_snapshot is None else auth_snapshot.to_dict(),
                "detail": "broker transport client not configured",
                "ts": _iso_now(),
            }

        try:
            raw = self.transport_client.healthcheck(
                access_token=self._transport_access_token(require_for_call=False),
                provider_id=self.provider_id,
            )
            raw_mapping = (
                dict(raw) if isinstance(raw, Mapping) else {"raw": _normalize_payload(raw)}
            )
            return {
                "ok": True,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "mode": self.mode,
                "auth": None if auth_snapshot is None else auth_snapshot.to_dict(),
                "raw": _normalize_payload(raw_mapping),
                "ts": _iso_now(),
            }
        except Exception as exc:
            return {
                "ok": False,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "mode": self.mode,
                "auth": None if auth_snapshot is None else auth_snapshot.to_dict(),
                "detail": str(exc),
                "ts": _iso_now(),
            }

    def get_order(self, order_id: str) -> dict[str, Any]:
        order_id = _require_non_empty(order_id, field_name="order_id")
        transport = self._require_transport()
        try:
            raw = transport.get_order(
                order_id,
                access_token=self._transport_access_token(),
                provider_id=self.provider_id,
            )
        except Exception as exc:
            raise BrokerAdapterRequestError(f"get_order() failed: {exc}") from exc

        if raw is None:
            return {
                "ok": False,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "order_id": order_id,
                "detail": "order not found",
            }

        if isinstance(raw, Mapping):
            return self._augment_response(
                raw,
                intent="get_order",
                request={"order_id": order_id},
            )

        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
            return {
                "ok": True,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "order_id": order_id,
                "history": _normalize_payload(list(raw)),
                "raw": _normalize_payload(list(raw)),
            }

        return {
            "ok": True,
            "broker": self.broker,
            "provider_id": self.provider_id,
            "order_id": order_id,
            "raw": _normalize_payload(raw),
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
        payload: dict[str, Any] = {"variety": variety}
        if parent_order_id is not None:
            payload["parent_order_id"] = _require_non_empty(
                parent_order_id,
                field_name="parent_order_id",
            )

        transport = self._require_transport()
        try:
            raw = transport.cancel_order(
                order_id,
                payload,
                access_token=self._transport_access_token(),
                provider_id=self.provider_id,
            )
        except Exception as exc:
            raise BrokerAdapterRequestError(f"cancel_order() failed: {exc}") from exc

        if isinstance(raw, Mapping):
            return self._augment_response(
                raw,
                intent="cancel_order",
                request={"order_id": order_id, **payload},
            )
        return {
            "ok": True,
            "broker": self.broker,
            "provider_id": self.provider_id,
            "intent": "cancel_order",
            "request": _normalize_payload({"order_id": order_id, **payload}),
            "raw": _normalize_payload(raw),
        }

    def reconcile_position(self) -> dict[str, Any]:
        transport = self._require_transport()
        try:
            raw = transport.reconcile_positions(
                access_token=self._transport_access_token(),
                provider_id=self.provider_id,
            )
        except Exception as exc:
            raise BrokerAdapterRequestError(
                f"reconcile_position() failed: {exc}"
            ) from exc

        return self._normalize_position_payload(raw)

    def reconcile_open_orders(self) -> list[Mapping[str, Any]] | None:
        transport = self._require_transport()
        try:
            raw = transport.reconcile_open_orders(
                access_token=self._transport_access_token(),
                provider_id=self.provider_id,
            )
        except Exception as exc:
            raise BrokerAdapterRequestError(
                f"reconcile_open_orders() failed: {exc}"
            ) from exc

        return self._normalize_open_orders_payload(raw)

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
        return self._place_order_common(
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
        return self._place_order_common(
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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_snapshot(self) -> BrokerAuthSnapshot | None:
        if self.auth_manager is None:
            return None
        return self.auth_manager.snapshot()

    def _transport_access_token(self, *, require_for_call: bool = True) -> str | None:
        if self.auth_manager is None:
            if self.requires_auth and require_for_call:
                raise BrokerAdapterAuthError(
                    f"{self.__class__.__name__} requires broker auth but auth_manager is not configured"
                )
            return None

        try:
            return self.auth_manager.get_access_token(ensure_authenticated=True)
        except BrokerSessionUnavailableError as exc:
            if self.requires_auth and require_for_call:
                raise BrokerAdapterAuthError(str(exc)) from exc
            return None

    def _require_transport(self) -> BrokerTransportClient:
        if self.transport_client is None:
            raise BrokerAdapterUnavailableError(
                f"{self.__class__.__name__} transport client not configured"
            )
        return self.transport_client

    def _place_order_common(
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
        payload = self._build_order_payload(
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
        transport = self._require_transport()

        try:
            raw = transport.place_order(
                payload,
                access_token=self._transport_access_token(),
                provider_id=self.provider_id,
            )
        except Exception as exc:
            raise BrokerAdapterRequestError(
                f"place_{intent}_order() failed: {exc}"
            ) from exc

        if isinstance(raw, Mapping):
            return self._augment_response(raw, intent=intent, request=payload)

        return {
            "ok": True,
            "broker": self.broker,
            "provider_id": self.provider_id,
            "intent": intent,
            "request": _normalize_payload(payload),
            "raw": _normalize_payload(raw),
        }

    def _build_order_payload(
        self,
        *,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        variety: str,
        price: Decimal | str | float | int | None,
        trigger_price: Decimal | str | float | int | None,
        validity: str,
        tag: str | None,
        extra_params: dict[str, Any] | None,
    ) -> dict[str, Any]:
        tradingsymbol = _require_non_empty(tradingsymbol, field_name="tradingsymbol")
        exchange = _require_non_empty(exchange, field_name="exchange").upper()
        transaction_type = _require_non_empty(
            transaction_type,
            field_name="transaction_type",
        ).upper()
        quantity = _require_int(quantity, field_name="quantity", min_value=1)
        product = _require_non_empty(product, field_name="product").upper()
        order_type = _require_non_empty(order_type, field_name="order_type").upper()
        variety = _require_non_empty(variety, field_name="variety")
        validity = _require_non_empty(validity, field_name="validity").upper()

        payload: dict[str, Any] = {
            "tradingsymbol": tradingsymbol,
            "exchange": exchange,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "product": product,
            "order_type": order_type,
            "variety": variety,
            "validity": validity,
        }

        normalized_price = _coerce_order_price(price, field_name="price")
        normalized_trigger = _coerce_order_price(
            trigger_price,
            field_name="trigger_price",
        )
        if normalized_price is not None:
            payload["price"] = normalized_price
        if normalized_trigger is not None:
            payload["trigger_price"] = normalized_trigger
        if tag is not None:
            payload["tag"] = _require_non_empty(tag, field_name="tag")
        if extra_params is not None:
            payload.update({str(k): v for k, v in extra_params.items()})
        return payload

    def _augment_response(
        self,
        raw: Mapping[str, Any],
        *,
        intent: str,
        request: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {str(k): _normalize_payload(v) for k, v in raw.items()}
        payload.setdefault("ok", True)
        payload.setdefault("broker", self.broker)
        payload.setdefault("provider_id", self.provider_id)
        payload.setdefault("intent", intent)
        if request is not None:
            payload.setdefault("request", _normalize_payload(dict(request)))
        payload.setdefault("raw", _normalize_payload(dict(raw)))
        return payload

    def _normalize_position_payload(self, raw: Any) -> dict[str, Any]:
        if raw is None:
            return {
                "ok": True,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "net": [],
                "day": [],
                "raw": None,
            }

        if isinstance(raw, Mapping):
            net = raw.get("net", [])
            day = raw.get("day", [])
            if net is None:
                net = []
            if day is None:
                day = []
            if not isinstance(net, list):
                raise BrokerAdapterRequestError(
                    f"positions payload field 'net' must be list, got {type(net).__name__}"
                )
            if not isinstance(day, list):
                raise BrokerAdapterRequestError(
                    f"positions payload field 'day' must be list, got {type(day).__name__}"
                )
            return {
                "ok": True,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "net": _normalize_mapping_list(net, field_name="positions.net"),
                "day": _normalize_mapping_list(day, field_name="positions.day"),
                "raw": _normalize_payload(dict(raw)),
            }

        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
            normalized = _normalize_mapping_list(list(raw), field_name="positions")
            return {
                "ok": True,
                "broker": self.broker,
                "provider_id": self.provider_id,
                "net": normalized,
                "day": [],
                "raw": _normalize_payload(list(raw)),
            }

        raise BrokerAdapterRequestError(
            f"positions payload must be mapping or list, got {type(raw).__name__}"
        )

    def _normalize_open_orders_payload(self, raw: Any) -> list[Mapping[str, Any]] | None:
        if raw is None:
            return None

        orders_payload: Any = raw
        if isinstance(raw, Mapping):
            orders_payload = raw.get("orders", [])

        if orders_payload is None:
            return []

        if not isinstance(orders_payload, list):
            raise BrokerAdapterRequestError(
                "open orders payload must be None, list, or wrapper mapping containing list field 'orders'"
            )

        normalized = _normalize_mapping_list(
            orders_payload,
            field_name="open_orders",
        )
        return list(normalized)

    def _filter_open_orders_by_terminal_status(
        self,
        rows: list[Mapping[str, Any]] | None,
        *,
        terminal_statuses: frozenset[str],
    ) -> list[Mapping[str, Any]] | None:
        if rows is None:
            return None
        out: list[Mapping[str, Any]] = []
        for row in rows:
            status = str(row.get("status", "")).strip().upper()
            if status in terminal_statuses:
                continue
            out.append(row)
        return out


# ============================================================================
# Null adapter
# ============================================================================


@dataclass(slots=True)
class NullBrokerAdapter(BaseBrokerAdapter):
    provider_id: str = PROVIDER_ZERODHA
    broker: str = "none"
    mode: str = "null"
    transport_client: BrokerTransportClient | None = None
    auth_manager: BrokerAuthManager | None = None
    requires_auth: bool = False
    default_exchange: str = "NFO"
    default_product: str = "NRML"
    default_variety: str = "regular"
    default_validity: str = "DAY"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def healthcheck(self) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "provider_id": self.provider_id,
            "mode": "null",
            "detail": "null broker adapter",
            "ts": _iso_now(),
        }

    def get_order(self, order_id: str) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "provider_id": self.provider_id,
            "order_id": order_id,
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
            "provider_id": self.provider_id,
            "order_id": order_id,
            "detail": "null broker adapter",
        }

    def reconcile_position(self) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "provider_id": self.provider_id,
            "net": [],
            "day": [],
            "detail": "null broker adapter",
        }

    def reconcile_open_orders(self) -> list[Mapping[str, Any]] | None:
        return []

    def place_entry_order(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "provider_id": self.provider_id,
            "intent": "entry",
            "request": _normalize_payload(kwargs),
            "detail": "null broker adapter",
        }

    def place_exit_order(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "broker": "none",
            "provider_id": self.provider_id,
            "intent": "exit",
            "request": _normalize_payload(kwargs),
            "detail": "null broker adapter",
        }


# ============================================================================
# Provider-specific execution adapters
# ============================================================================


@dataclass(slots=True)
class ZerodhaBrokerAdapter(BaseBrokerAdapter):
    provider_id: str = PROVIDER_ZERODHA
    broker: str = "zerodha"
    mode: str = "zerodha"
    transport_client: BrokerTransportClient | None = None
    auth_manager: BrokerAuthManager | None = None
    requires_auth: bool = True
    default_exchange: str = "NFO"
    default_product: str = "NRML"
    default_variety: str = "regular"
    default_validity: str = "DAY"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    _TERMINAL_ORDER_STATUSES: frozenset[str] = frozenset(
        {
            "COMPLETE",
            "CANCELLED",
            "REJECTED",
        }
    )

    def reconcile_open_orders(self) -> list[Mapping[str, Any]] | None:
        rows = BaseBrokerAdapter.reconcile_open_orders(self)
        return self._filter_open_orders_by_terminal_status(
            rows,
            terminal_statuses=self._TERMINAL_ORDER_STATUSES,
        )


@dataclass(slots=True)
class DhanBrokerAdapter(BaseBrokerAdapter):
    provider_id: str = PROVIDER_DHAN
    broker: str = "dhan"
    mode: str = "dhan"
    transport_client: BrokerTransportClient | None = None
    auth_manager: BrokerAuthManager | None = None
    requires_auth: bool = True
    default_exchange: str = "NFO"
    default_product: str = "NRML"
    default_variety: str = "regular"
    default_validity: str = "DAY"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    _TERMINAL_ORDER_STATUSES: frozenset[str] = frozenset(
        {
            "TRADED",
            "COMPLETE",
            "CANCELLED",
            "REJECTED",
            "EXPIRED",
        }
    )

    def reconcile_open_orders(self) -> list[Mapping[str, Any]] | None:
        rows = BaseBrokerAdapter.reconcile_open_orders(self)
        return self._filter_open_orders_by_terminal_status(
            rows,
            terminal_statuses=self._TERMINAL_ORDER_STATUSES,
        )


# ============================================================================
# Builders
# ============================================================================


def build_null_broker_adapter(
    *,
    provider_id: str = PROVIDER_ZERODHA,
    reason: str | None = None,
) -> NullBrokerAdapter:
    metadata: dict[str, Any] = {}
    if reason:
        metadata["reason"] = reason
    return NullBrokerAdapter(provider_id=provider_id, metadata=metadata)


def build_real_broker_adapter(
    broker: str = "zerodha",
    *,
    transport_client: BrokerTransportClient | None = None,
    auth_manager: BrokerAuthManager | None = None,
    requires_auth: bool | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> BrokerAdapter:
    """
    Compatibility builder used by bootstrap_provider.py and future composition.

    Important:
    - It preserves the historical builder shape: build_real_broker_adapter(broker="zerodha")
    - It does not invent hidden vendor bootstrap assumptions.
    - If no transport_client is supplied yet, it still returns the correct
      provider-specific adapter class with explicit unavailable transport truth.
    """

    broker_norm = _require_non_empty(broker, field_name="broker").strip().lower()
    metadata = dict(metadata or {})

    if broker_norm == "zerodha":
        return ZerodhaBrokerAdapter(
            transport_client=transport_client,
            auth_manager=auth_manager,
            requires_auth=True if requires_auth is None else bool(requires_auth),
            metadata=metadata,
        )

    if broker_norm == "dhan":
        return DhanBrokerAdapter(
            transport_client=transport_client,
            auth_manager=auth_manager,
            requires_auth=True if requires_auth is None else bool(requires_auth),
            metadata=metadata,
        )

    raise BrokerAdapterValidationError(f"unsupported broker: {broker!r}")


__all__ = [
    "BaseBrokerAdapter",
    "BrokerAdapter",
    "BrokerAdapterAuthError",
    "BrokerAdapterError",
    "BrokerAdapterInfo",
    "BrokerAdapterRequestError",
    "BrokerAdapterUnavailableError",
    "BrokerAdapterValidationError",
    "BrokerTransportClient",
    "CallableBrokerTransportClient",
    "DhanBrokerAdapter",
    "KiteTransportClient",
    "NullBrokerAdapter",
    "ZerodhaBrokerAdapter",
    "build_null_broker_adapter",
    "build_real_broker_adapter",
]
