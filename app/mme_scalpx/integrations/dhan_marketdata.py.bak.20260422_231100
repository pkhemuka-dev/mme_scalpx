from __future__ import annotations

"""
app/mme_scalpx/integrations/dhan_marketdata.py

Freeze-grade Dhan market-data contract for ScalpX MME.

Purpose
-------
This module OWNS:
- Dhan market-data config loading from etc/brokers/dhan.yaml-style config
- Dhan auth/session attachment for market-data lanes
- option-context (chain/context) lane normalization and freshness truth
- live futures lane normalization and freshness truth
- live selected-option lane normalization and freshness truth
- optional shadow-option cache for monitored strikes
- explicit stale / unavailable / auth-failed lane truth
- model-light public snapshots and health payloads for downstream services

This module DOES NOT own:
- Redis IO / stream publishing
- provider-runtime role resolution
- strategy logic
- feature computation
- execution / order placement
- websocket supervision policy
- main.py composition
- typed core.models surfaces under the parallel models lane

Core laws
---------
- Dhan chain/context is a slower context lane.
- Dhan live option and live futures are trigger/feed lanes.
- No silent stale defaults.
- This file is intentionally model-light and self-contained.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from types import MappingProxyType
from typing import Any, Mapping, MutableMapping, Protocol, Sequence
import math

try:  # pragma: no cover - optional dependency at import time
    import yaml
except Exception:  # pragma: no cover
    yaml = None

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
                getattr(names, "PROVIDER_ZERODHA", "ZERODHA"),
                getattr(names, "PROVIDER_DHAN", "DHAN"),
            ),
        ),
    )
)

_PROVIDER_DHAN: str = getattr(names, "PROVIDER_DHAN", "DHAN")

_ROLE_FUTURES: str = getattr(
    names,
    "PROVIDER_ROLE_FUTURES_MARKETDATA",
    "futures_marketdata",
)
_ROLE_SELECTED_OPTION: str = getattr(
    names,
    "PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA",
    "selected_option_marketdata",
)
_ROLE_OPTION_CONTEXT: str = getattr(
    names,
    "PROVIDER_ROLE_OPTION_CONTEXT",
    "option_context",
)

_STATUS_HEALTHY: str = getattr(names, "PROVIDER_STATUS_HEALTHY", "HEALTHY")
_STATUS_DEGRADED: str = getattr(names, "PROVIDER_STATUS_DEGRADED", "DEGRADED")
_STATUS_STALE: str = getattr(names, "PROVIDER_STATUS_STALE", "STALE")
_STATUS_AUTH_FAILED: str = getattr(names, "PROVIDER_STATUS_AUTH_FAILED", "AUTH_FAILED")
_STATUS_UNAVAILABLE: str = getattr(names, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
_STATUS_DISABLED: str = getattr(names, "PROVIDER_STATUS_DISABLED", "DISABLED")

_ALLOWED_STATUSES: tuple[str, ...] = (
    _STATUS_HEALTHY,
    _STATUS_DEGRADED,
    _STATUS_STALE,
    _STATUS_AUTH_FAILED,
    _STATUS_UNAVAILABLE,
    _STATUS_DISABLED,
)

_ALLOWED_DEPTH_MODES: tuple[str, ...] = (
    "TOP5",
    "TOP20",
    "TOP20_ENHANCED",
)

_ALLOWED_LIVE_LANE_ROLES: tuple[str, ...] = (
    _ROLE_FUTURES,
    _ROLE_SELECTED_OPTION,
)

# ============================================================================
# Exceptions
# ============================================================================


class DhanMarketdataError(RuntimeError):
    """Base error for Dhan market-data contract failures."""


class DhanMarketdataValidationError(DhanMarketdataError):
    """Raised when config or input data is invalid."""


class DhanMarketdataAuthError(DhanMarketdataError):
    """Raised when Dhan auth/session is unavailable for market-data use."""


class DhanMarketdataUnavailableError(DhanMarketdataError):
    """Raised when a required Dhan lane is unavailable or disabled."""


# ============================================================================
# Shared validator wrappers
# ============================================================================


def _wrap_validation(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        if isinstance(exc, DhanMarketdataValidationError):
            raise
        if isinstance(exc, ValidationError):
            raise DhanMarketdataValidationError(str(exc)) from exc
        raise DhanMarketdataValidationError(str(exc)) from exc


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


def _freeze_tuple_of_mappings(rows: Sequence[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    return tuple(_freeze_mapping(row) for row in rows)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_from_ns(value_ns: int | None) -> str | None:
    if value_ns is None:
        return None
    return datetime.fromtimestamp(
        value_ns / 1_000_000_000,
        tz=timezone.utc,
    ).isoformat()


def _now_ns() -> int:
    return int(_utc_now().timestamp() * 1_000_000_000)


def _normalize_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc).isoformat()
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, Mapping):
        return {str(k): _normalize_scalar(v) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_scalar(item) for item in value]
    return str(value)


def _pick(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _coerce_str(value: Any, *, field_name: str, allow_none: bool = True) -> str | None:
    if value is None:
        if allow_none:
            return None
        raise DhanMarketdataValidationError(f"{field_name} may not be None")
    text = str(value).strip()
    if not text:
        if allow_none:
            return None
        raise DhanMarketdataValidationError(f"{field_name} may not be blank")
    return text


def _coerce_float(value: Any, *, field_name: str, allow_none: bool = True) -> float | None:
    if value is None or value == "":
        if allow_none:
            return None
        raise DhanMarketdataValidationError(f"{field_name} may not be None")
    if isinstance(value, bool):
        raise DhanMarketdataValidationError(f"{field_name} must be numeric, got bool")
    try:
        result = float(value)
    except Exception as exc:
        raise DhanMarketdataValidationError(f"{field_name} must be numeric") from exc
    if math.isnan(result) or math.isinf(result):
        if allow_none:
            return None
        raise DhanMarketdataValidationError(f"{field_name} must be finite")
    return result


def _coerce_int(value: Any, *, field_name: str, allow_none: bool = True) -> int | None:
    if value is None or value == "":
        if allow_none:
            return None
        raise DhanMarketdataValidationError(f"{field_name} may not be None")
    if isinstance(value, bool):
        raise DhanMarketdataValidationError(f"{field_name} must be integer, got bool")
    try:
        result = int(value)
    except Exception as exc:
        raise DhanMarketdataValidationError(f"{field_name} must be integer") from exc
    return result


def _coerce_ns(value: Any, *, field_name: str, allow_none: bool = True) -> int | None:
    if value is None or value == "":
        if allow_none:
            return None
        raise DhanMarketdataValidationError(f"{field_name} may not be None")
    if isinstance(value, int):
        return _require_int(value, field_name=field_name, min_value=0)
    if isinstance(value, float):
        return _require_int(int(value), field_name=field_name, min_value=0)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.timestamp() * 1_000_000_000)
    text = str(value).strip()
    if not text:
        if allow_none:
            return None
        raise DhanMarketdataValidationError(f"{field_name} may not be blank")
    if text.isdigit():
        return _require_int(int(text), field_name=field_name, min_value=0)
    for suffix in ("Z", "+00:00"):
        if text.endswith(suffix) or "T" in text:
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                break
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp() * 1_000_000_000)
    raise DhanMarketdataValidationError(f"{field_name} must be epoch-ns or ISO datetime")


def _normalize_role(role: str) -> str:
    return _require_literal(
        role,
        field_name="role",
        allowed=(_ROLE_FUTURES, _ROLE_SELECTED_OPTION, _ROLE_OPTION_CONTEXT),
    )


def _normalize_depth_rows(rows: Any, *, side_name: str) -> tuple[Mapping[str, Any], ...]:
    if rows is None:
        return ()
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
        raise DhanMarketdataValidationError(
            f"{side_name} depth rows must be a sequence of mappings"
        )

    out: list[Mapping[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise DhanMarketdataValidationError(
                f"{side_name}[{index}] must be a mapping"
            )
        price = _coerce_float(
            _pick(row, "price", "p"),
            field_name=f"{side_name}[{index}].price",
            allow_none=True,
        )
        quantity = _coerce_int(
            _pick(row, "quantity", "qty", "q"),
            field_name=f"{side_name}[{index}].quantity",
            allow_none=True,
        )
        orders = _coerce_int(
            _pick(row, "orders", "order_count", "count"),
            field_name=f"{side_name}[{index}].orders",
            allow_none=True,
        )
        out.append(
            {
                "price": price,
                "quantity": quantity,
                "orders": orders,
            }
        )
    return _freeze_tuple_of_mappings(out)


def _normalize_metadata(raw: Mapping[str, Any], *, exclude: Sequence[str]) -> Mapping[str, Any]:
    excluded = set(exclude)
    kept = {
        str(k): _normalize_scalar(v)
        for k, v in raw.items()
        if k not in excluded
    }
    return _freeze_mapping(kept)


def _lane_status_message(
    *,
    role: str,
    status: str,
    age_ms: int | None,
    last_error: str | None,
) -> str:
    base = f"{role} status={status}"
    if age_ms is not None:
        base += f" age_ms={age_ms}"
    if last_error:
        base += f" last_error={last_error}"
    return base


# ============================================================================
# Public protocols
# ============================================================================


class DhanContextClient(Protocol):
    """Optional external client protocol for fetching chain/context snapshots."""

    def fetch_chain_snapshot(self, *, access_token: str | None = None) -> Any:
        ...


class DhanLiveFeedClient(Protocol):
    """Optional external live feed protocol for futures/options tick subscription."""

    def subscribe(self, instrument_keys: Sequence[str]) -> Any:
        ...

    def unsubscribe(self, instrument_keys: Sequence[str]) -> Any:
        ...


# ============================================================================
# Public value objects
# ============================================================================


@dataclass(frozen=True, slots=True)
class DhanMarketdataConfig:
    provider_id: str = _PROVIDER_DHAN
    enabled: bool = True
    auth_required: bool = True

    futures_marketdata_enabled: bool = True
    selected_option_marketdata_enabled: bool = True
    option_context_enabled: bool = True

    futures_stale_after_ms: int = 1500
    futures_dead_after_ms: int = 5000
    selected_option_stale_after_ms: int = 1200
    selected_option_dead_after_ms: int = 4000
    option_context_stale_after_ms: int = 5000
    option_context_dead_after_ms: int = 15000

    selected_option_depth_mode: str = "TOP20_ENHANCED"
    selected_option_base_depth_mode: str = "TOP5"
    futures_depth_mode: str = "TOP20_ENHANCED"

    chain_snapshot_required: bool = True
    chain_snapshot_refresh_ms: int = 1000
    context_refresh_ms: int = 1000

    config_revision: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_id",
            _require_literal(
                self.provider_id,
                field_name="provider_id",
                allowed=_ALLOWED_PROVIDER_IDS,
            ),
        )
        object.__setattr__(self, "enabled", _require_bool(self.enabled, field_name="enabled"))
        object.__setattr__(
            self,
            "auth_required",
            _require_bool(self.auth_required, field_name="auth_required"),
        )

        for field_name in (
            "futures_marketdata_enabled",
            "selected_option_marketdata_enabled",
            "option_context_enabled",
            "chain_snapshot_required",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_bool(getattr(self, field_name), field_name=field_name),
            )

        for field_name in (
            "futures_stale_after_ms",
            "futures_dead_after_ms",
            "selected_option_stale_after_ms",
            "selected_option_dead_after_ms",
            "option_context_stale_after_ms",
            "option_context_dead_after_ms",
            "chain_snapshot_refresh_ms",
            "context_refresh_ms",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_int(getattr(self, field_name), field_name=field_name, min_value=0),
            )

        if self.config_revision is not None:
            object.__setattr__(
                self,
                "config_revision",
                _require_non_empty(self.config_revision, field_name="config_revision"),
            )

        object.__setattr__(
            self,
            "selected_option_depth_mode",
            _require_literal(
                self.selected_option_depth_mode,
                field_name="selected_option_depth_mode",
                allowed=_ALLOWED_DEPTH_MODES,
            ),
        )
        object.__setattr__(
            self,
            "selected_option_base_depth_mode",
            _require_literal(
                self.selected_option_base_depth_mode,
                field_name="selected_option_base_depth_mode",
                allowed=_ALLOWED_DEPTH_MODES,
            ),
        )
        object.__setattr__(
            self,
            "futures_depth_mode",
            _require_literal(
                self.futures_depth_mode,
                field_name="futures_depth_mode",
                allowed=_ALLOWED_DEPTH_MODES,
            ),
        )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def from_provider_mapping(
        cls,
        raw: Mapping[str, object],
    ) -> "DhanMarketdataConfig":
        data = _require_mapping(raw, field_name="raw")
        capabilities = (
            _require_mapping(data.get("capabilities", {}), field_name="capabilities")
            if isinstance(data.get("capabilities", {}), Mapping)
            else {}
        )
        health_contract = (
            _require_mapping(data.get("health_contract", {}), field_name="health_contract")
            if isinstance(data.get("health_contract", {}), Mapping)
            else {}
        )
        transport_contract = (
            _require_mapping(data.get("transport_contract", {}), field_name="transport_contract")
            if isinstance(data.get("transport_contract", {}), Mapping)
            else {}
        )
        stale_after_ms = (
            _require_mapping(health_contract.get("stale_after_ms", {}), field_name="stale_after_ms")
            if isinstance(health_contract.get("stale_after_ms", {}), Mapping)
            else {}
        )
        dead_after_ms = (
            _require_mapping(health_contract.get("dead_after_ms", {}), field_name="dead_after_ms")
            if isinstance(health_contract.get("dead_after_ms", {}), Mapping)
            else {}
        )

        def _cap_enabled(cap_name: str, default: bool) -> bool:
            cap = capabilities.get(cap_name, {})
            if isinstance(cap, Mapping):
                return bool(cap.get("enabled", default))
            return default

        return cls(
            provider_id=str(data.get("provider_id", _PROVIDER_DHAN)),
            enabled=bool(data.get("enabled", True)),
            auth_required=bool(health_contract.get("auth_required", True)),
            futures_marketdata_enabled=_cap_enabled("futures_marketdata", True),
            selected_option_marketdata_enabled=_cap_enabled("selected_option_marketdata", True),
            option_context_enabled=_cap_enabled("option_context", True),
            futures_stale_after_ms=int(stale_after_ms.get("futures_marketdata", 1500)),
            futures_dead_after_ms=int(dead_after_ms.get("futures_marketdata", 5000)),
            selected_option_stale_after_ms=int(stale_after_ms.get("selected_option_marketdata", 1200)),
            selected_option_dead_after_ms=int(dead_after_ms.get("selected_option_marketdata", 4000)),
            option_context_stale_after_ms=int(stale_after_ms.get("option_context", 5000)),
            option_context_dead_after_ms=int(dead_after_ms.get("option_context", 15000)),
            selected_option_depth_mode=str(
                transport_contract.get("selected_option_depth_mode", "TOP20_ENHANCED")
            ),
            selected_option_base_depth_mode=str(
                transport_contract.get("selected_option_base_depth_mode", "TOP5")
            ),
            futures_depth_mode=str(
                transport_contract.get("futures_depth_mode", "TOP20_ENHANCED")
            ),
            chain_snapshot_required=bool(
                transport_contract.get("chain_snapshot_required", True)
            ),
            chain_snapshot_refresh_ms=int(
                transport_contract.get("chain_snapshot_refresh_ms", 1000)
            ),
            context_refresh_ms=int(
                transport_contract.get("context_refresh_ms", 1000)
            ),
            config_revision=(
                str(data["config_revision"]) if data.get("config_revision") is not None else None
            ),
            metadata={
                "source": "provider_mapping",
            },
        )

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> "DhanMarketdataConfig":
        if yaml is None:
            raise DhanMarketdataValidationError(
                "PyYAML is required to load Dhan marketdata config from YAML"
            )
        candidate = Path(path)
        if not candidate.exists():
            raise DhanMarketdataValidationError(f"config file not found: {candidate}")
        loaded = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, Mapping):
            raise DhanMarketdataValidationError(
                f"config root must be a mapping: {candidate}"
            )
        return cls.from_provider_mapping(loaded)


@dataclass(frozen=True, slots=True)
class DhanLiveTick:
    provider_id: str
    role: str
    instrument_key: str
    symbol: str | None
    local_ts_ns: int
    ltt_ns: int | None
    ltp: float | None
    ltq: int | None
    best_bid: float | None
    best_ask: float | None
    volume: int | None
    oi: int | None
    bids: tuple[Mapping[str, Any], ...] = ()
    asks: tuple[Mapping[str, Any], ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
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
            "role",
            _require_literal(
                self.role,
                field_name="role",
                allowed=_ALLOWED_LIVE_LANE_ROLES,
            ),
        )
        object.__setattr__(
            self,
            "instrument_key",
            _require_non_empty(self.instrument_key, field_name="instrument_key"),
        )
        object.__setattr__(
            self,
            "local_ts_ns",
            _require_int(self.local_ts_ns, field_name="local_ts_ns", min_value=0),
        )
        if self.symbol is not None:
            object.__setattr__(
                self,
                "symbol",
                _require_non_empty(self.symbol, field_name="symbol"),
            )
        if self.ltt_ns is not None:
            object.__setattr__(
                self,
                "ltt_ns",
                _require_int(self.ltt_ns, field_name="ltt_ns", min_value=0),
            )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "role": self.role,
            "instrument_key": self.instrument_key,
            "symbol": self.symbol,
            "local_ts_ns": self.local_ts_ns,
            "local_ts_iso": _iso_from_ns(self.local_ts_ns),
            "ltt_ns": self.ltt_ns,
            "ltt_iso": _iso_from_ns(self.ltt_ns),
            "ltp": self.ltp,
            "ltq": self.ltq,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "volume": self.volume,
            "oi": self.oi,
            "bids": [dict(row) for row in self.bids],
            "asks": [dict(row) for row in self.asks],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class DhanContextRow:
    symbol: str | None
    option_type: str | None
    strike: float | None
    expiry: str | None
    token: str | None
    ltp: float | None
    bid: float | None
    ask: float | None
    volume: int | None
    oi: int | None
    iv: float | None
    delta: float | None
    gamma: float | None
    theta: float | None
    vega: float | None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.symbol is not None:
            object.__setattr__(
                self,
                "symbol",
                _require_non_empty(self.symbol, field_name="symbol"),
            )
        if self.option_type is not None:
            object.__setattr__(
                self,
                "option_type",
                _require_non_empty(self.option_type, field_name="option_type"),
            )
        if self.expiry is not None:
            object.__setattr__(
                self,
                "expiry",
                _require_non_empty(self.expiry, field_name="expiry"),
            )
        if self.token is not None:
            object.__setattr__(
                self,
                "token",
                _require_non_empty(self.token, field_name="token"),
            )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "option_type": self.option_type,
            "strike": self.strike,
            "expiry": self.expiry,
            "token": self.token,
            "ltp": self.ltp,
            "bid": self.bid,
            "ask": self.ask,
            "volume": self.volume,
            "oi": self.oi,
            "iv": self.iv,
            "delta": self.delta,
            "gamma": self.gamma,
            "theta": self.theta,
            "vega": self.vega,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class DhanContextSnapshot:
    provider_id: str
    local_ts_ns: int
    chain_rows: tuple[DhanContextRow, ...]
    monitored_symbols: tuple[str, ...]
    chain_row_count: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
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
            "local_ts_ns",
            _require_int(self.local_ts_ns, field_name="local_ts_ns", min_value=0),
        )
        object.__setattr__(
            self,
            "chain_row_count",
            _require_int(self.chain_row_count, field_name="chain_row_count", min_value=0),
        )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "local_ts_ns": self.local_ts_ns,
            "local_ts_iso": _iso_from_ns(self.local_ts_ns),
            "chain_row_count": self.chain_row_count,
            "monitored_symbols": list(self.monitored_symbols),
            "chain_rows": [row.to_dict() for row in self.chain_rows],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class DhanLaneHealth:
    provider_id: str
    role: str
    enabled: bool
    auth_required: bool
    authenticated: bool
    status: str
    last_update_ns: int | None
    age_ms: int | None
    stale_after_ms: int
    dead_after_ms: int
    last_error: str | None = None
    last_error_ns: int | None = None
    message: str | None = None

    def __post_init__(self) -> None:
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
            "role",
            _require_literal(
                self.role,
                field_name="role",
                allowed=(_ROLE_FUTURES, _ROLE_SELECTED_OPTION, _ROLE_OPTION_CONTEXT),
            ),
        )
        object.__setattr__(self, "enabled", _require_bool(self.enabled, field_name="enabled"))
        object.__setattr__(
            self,
            "auth_required",
            _require_bool(self.auth_required, field_name="auth_required"),
        )
        object.__setattr__(
            self,
            "authenticated",
            _require_bool(self.authenticated, field_name="authenticated"),
        )
        object.__setattr__(
            self,
            "status",
            _require_literal(
                self.status,
                field_name="status",
                allowed=_ALLOWED_STATUSES,
            ),
        )
        if self.last_update_ns is not None:
            object.__setattr__(
                self,
                "last_update_ns",
                _require_int(self.last_update_ns, field_name="last_update_ns", min_value=0),
            )
        if self.age_ms is not None:
            object.__setattr__(
                self,
                "age_ms",
                _require_int(self.age_ms, field_name="age_ms", min_value=0),
            )
        object.__setattr__(
            self,
            "stale_after_ms",
            _require_int(self.stale_after_ms, field_name="stale_after_ms", min_value=0),
        )
        object.__setattr__(
            self,
            "dead_after_ms",
            _require_int(self.dead_after_ms, field_name="dead_after_ms", min_value=0),
        )
        if self.last_error is not None:
            object.__setattr__(
                self,
                "last_error",
                _require_non_empty(self.last_error, field_name="last_error"),
            )
        if self.last_error_ns is not None:
            object.__setattr__(
                self,
                "last_error_ns",
                _require_int(self.last_error_ns, field_name="last_error_ns", min_value=0),
            )
        if self.message is not None:
            object.__setattr__(
                self,
                "message",
                _require_non_empty(self.message, field_name="message"),
            )

    @property
    def marketdata_healthy(self) -> bool:
        return self.status in (_STATUS_HEALTHY, _STATUS_DEGRADED, _STATUS_STALE)

    @property
    def stale(self) -> bool:
        return self.status == _STATUS_STALE

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "role": self.role,
            "enabled": self.enabled,
            "auth_required": self.auth_required,
            "authenticated": self.authenticated,
            "status": self.status,
            "last_update_ns": self.last_update_ns,
            "last_update_iso": _iso_from_ns(self.last_update_ns),
            "age_ms": self.age_ms,
            "stale_after_ms": self.stale_after_ms,
            "dead_after_ms": self.dead_after_ms,
            "last_error": self.last_error,
            "last_error_ns": self.last_error_ns,
            "last_error_iso": _iso_from_ns(self.last_error_ns),
            "message": self.message,
            "marketdata_healthy": self.marketdata_healthy,
            "stale": self.stale,
        }

    def to_provider_health_payload(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "role": self.role,
            "status": self.status,
            "authenticated": self.authenticated,
            "marketdata_healthy": self.marketdata_healthy,
            "stale": self.stale,
            "last_success_ns": self.last_update_ns,
            "last_error": self.last_error,
            "last_error_ns": self.last_error_ns,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class DhanMarketdataSnapshot:
    provider_id: str
    config_revision: str | None
    computed_at_ns: int
    auth_snapshot: Mapping[str, Any] | None
    futures_tick: DhanLiveTick | None
    selected_option_tick: DhanLiveTick | None
    shadow_option_ticks: Mapping[str, Mapping[str, Any]]
    context_snapshot: DhanContextSnapshot | None
    futures_health: DhanLaneHealth
    selected_option_health: DhanLaneHealth
    option_context_health: DhanLaneHealth
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
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
            "computed_at_ns",
            _require_int(self.computed_at_ns, field_name="computed_at_ns", min_value=0),
        )
        if self.config_revision is not None:
            object.__setattr__(
                self,
                "config_revision",
                _require_non_empty(self.config_revision, field_name="config_revision"),
            )
        object.__setattr__(self, "shadow_option_ticks", _freeze_mapping(self.shadow_option_ticks))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "config_revision": self.config_revision,
            "computed_at_ns": self.computed_at_ns,
            "computed_at_iso": _iso_from_ns(self.computed_at_ns),
            "auth_snapshot": dict(self.auth_snapshot) if self.auth_snapshot is not None else None,
            "futures_tick": None if self.futures_tick is None else self.futures_tick.to_dict(),
            "selected_option_tick": (
                None if self.selected_option_tick is None else self.selected_option_tick.to_dict()
            ),
            "shadow_option_ticks": {
                k: dict(v) for k, v in self.shadow_option_ticks.items()
            },
            "context_snapshot": (
                None if self.context_snapshot is None else self.context_snapshot.to_dict()
            ),
            "futures_health": self.futures_health.to_dict(),
            "selected_option_health": self.selected_option_health.to_dict(),
            "option_context_health": self.option_context_health.to_dict(),
            "metadata": dict(self.metadata),
        }


# ============================================================================
# Internal mutable lane state
# ============================================================================


@dataclass(slots=True)
class _LaneState:
    last_update_ns: int | None = None
    last_error: str | None = None
    last_error_ns: int | None = None
    sequence_no: int = 0
    snapshot_obj: Any = None

    def mark_success(self, *, ts_ns: int, snapshot_obj: Any) -> None:
        self.last_update_ns = ts_ns
        self.last_error = None
        self.last_error_ns = None
        self.sequence_no += 1
        self.snapshot_obj = snapshot_obj

    def mark_error(self, *, ts_ns: int, error: str) -> None:
        self.last_error = error
        self.last_error_ns = ts_ns
        self.sequence_no += 1


# ============================================================================
# Main manager
# ============================================================================


class DhanMarketdataManager:
    """
    Freeze-grade in-memory Dhan market-data state manager.

    Intended usage:
    - main/feeds composition builds one manager
    - auth/session comes from BrokerAuthManager
    - live lanes call ingest_* methods
    - downstream services consume snapshot()/build_public_health_payload()
    """

    def __init__(
        self,
        *,
        config: DhanMarketdataConfig,
        auth_manager: BrokerAuthManager | None = None,
        context_client: DhanContextClient | None = None,
        live_feed_client: DhanLiveFeedClient | None = None,
    ) -> None:
        if not isinstance(config, DhanMarketdataConfig):
            raise DhanMarketdataValidationError(
                f"config must be DhanMarketdataConfig, got {type(config).__name__}"
            )
        self._config = config
        self._auth_manager = auth_manager
        self._context_client = context_client
        self._live_feed_client = live_feed_client
        self._lock = RLock()

        self._futures_lane = _LaneState()
        self._selected_option_lane = _LaneState()
        self._context_lane = _LaneState()

        self._selected_option_instrument_key: str | None = None
        self._shadow_option_ticks: dict[str, DhanLiveTick] = {}

    @property
    def config(self) -> DhanMarketdataConfig:
        return self._config

    @property
    def auth_manager(self) -> BrokerAuthManager | None:
        return self._auth_manager

    @classmethod
    def from_yaml_file(
        cls,
        path: str | Path,
        *,
        auth_manager: BrokerAuthManager | None = None,
        context_client: DhanContextClient | None = None,
        live_feed_client: DhanLiveFeedClient | None = None,
    ) -> "DhanMarketdataManager":
        return cls(
            config=DhanMarketdataConfig.from_yaml_file(path),
            auth_manager=auth_manager,
            context_client=context_client,
            live_feed_client=live_feed_client,
        )

    # ------------------------------------------------------------------
    # Auth/session helpers
    # ------------------------------------------------------------------

    def auth_snapshot(self) -> BrokerAuthSnapshot | None:
        if self._auth_manager is None:
            return None
        return self._auth_manager.snapshot()

    def ensure_authenticated(self) -> BrokerAuthSnapshot | None:
        if not self._config.enabled:
            raise DhanMarketdataUnavailableError("Dhan marketdata is disabled by config")
        if not self._config.auth_required:
            return self.auth_snapshot()
        if self._auth_manager is None:
            raise DhanMarketdataAuthError(
                "Dhan marketdata requires auth but auth_manager is not configured"
            )
        try:
            return self._auth_manager.ensure_authenticated()
        except BrokerSessionUnavailableError as exc:
            raise DhanMarketdataAuthError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Context lane
    # ------------------------------------------------------------------

    def refresh_context_from_client(self, *, ts_event_ns: int | None = None) -> DhanContextSnapshot:
        if self._context_client is None:
            raise DhanMarketdataUnavailableError("context_client is not configured")
        self.ensure_authenticated()
        raw = self._context_client.fetch_chain_snapshot(
            access_token=self._auth_token_or_none(),
        )
        return self.ingest_context_snapshot(raw, ts_event_ns=ts_event_ns)

    def ingest_context_snapshot(
        self,
        raw_snapshot: Any,
        *,
        ts_event_ns: int | None = None,
    ) -> DhanContextSnapshot:
        with self._lock:
            self._require_enabled_lane(_ROLE_OPTION_CONTEXT)

            now_ns = _coerce_ns(
                ts_event_ns if ts_event_ns is not None else _now_ns(),
                field_name="ts_event_ns",
                allow_none=False,
            )
            snapshot = self._normalize_context_snapshot(raw_snapshot, ts_event_ns=now_ns)
            self._context_lane.mark_success(ts_ns=now_ns, snapshot_obj=snapshot)
            return snapshot

    # ------------------------------------------------------------------
    # Live futures / option lanes
    # ------------------------------------------------------------------

    def ingest_futures_tick(
        self,
        raw_tick: Any,
        *,
        instrument_key: str | None = None,
        symbol: str | None = None,
        ts_event_ns: int | None = None,
    ) -> DhanLiveTick:
        with self._lock:
            self._require_enabled_lane(_ROLE_FUTURES)
            now_ns = _coerce_ns(
                ts_event_ns if ts_event_ns is not None else _now_ns(),
                field_name="ts_event_ns",
                allow_none=False,
            )
            tick = self._normalize_live_tick(
                raw_tick,
                role=_ROLE_FUTURES,
                instrument_key=instrument_key,
                symbol=symbol,
                ts_event_ns=now_ns,
            )
            self._futures_lane.mark_success(ts_ns=now_ns, snapshot_obj=tick)
            return tick

    def bind_selected_option(self, instrument_key: str | None) -> None:
        with self._lock:
            if instrument_key is None:
                self._selected_option_instrument_key = None
                return
            self._selected_option_instrument_key = _require_non_empty(
                instrument_key,
                field_name="instrument_key",
            )

    def ingest_selected_option_tick(
        self,
        raw_tick: Any,
        *,
        instrument_key: str | None = None,
        symbol: str | None = None,
        ts_event_ns: int | None = None,
    ) -> DhanLiveTick:
        with self._lock:
            self._require_enabled_lane(_ROLE_SELECTED_OPTION)
            now_ns = _coerce_ns(
                ts_event_ns if ts_event_ns is not None else _now_ns(),
                field_name="ts_event_ns",
                allow_none=False,
            )
            resolved_instrument_key = instrument_key or self._selected_option_instrument_key
            tick = self._normalize_live_tick(
                raw_tick,
                role=_ROLE_SELECTED_OPTION,
                instrument_key=resolved_instrument_key,
                symbol=symbol,
                ts_event_ns=now_ns,
            )
            self._selected_option_lane.mark_success(ts_ns=now_ns, snapshot_obj=tick)
            self._selected_option_instrument_key = tick.instrument_key
            if tick.instrument_key in self._shadow_option_ticks:
                del self._shadow_option_ticks[tick.instrument_key]
            return tick

    def ingest_shadow_option_tick(
        self,
        raw_tick: Any,
        *,
        instrument_key: str,
        symbol: str | None = None,
        ts_event_ns: int | None = None,
    ) -> DhanLiveTick:
        with self._lock:
            self._require_enabled_lane(_ROLE_SELECTED_OPTION)
            now_ns = _coerce_ns(
                ts_event_ns if ts_event_ns is not None else _now_ns(),
                field_name="ts_event_ns",
                allow_none=False,
            )
            tick = self._normalize_live_tick(
                raw_tick,
                role=_ROLE_SELECTED_OPTION,
                instrument_key=instrument_key,
                symbol=symbol,
                ts_event_ns=now_ns,
            )
            self._shadow_option_ticks[tick.instrument_key] = tick
            return tick

    def clear_shadow_option(self, instrument_key: str) -> None:
        with self._lock:
            key = _require_non_empty(instrument_key, field_name="instrument_key")
            self._shadow_option_ticks.pop(key, None)

    def subscribe_live_instruments(self, instrument_keys: Sequence[str]) -> Any:
        if self._live_feed_client is None:
            raise DhanMarketdataUnavailableError("live_feed_client is not configured")
        cleaned = [
            _require_non_empty(str(item), field_name="instrument_key")
            for item in instrument_keys
        ]
        return self._live_feed_client.subscribe(cleaned)

    def unsubscribe_live_instruments(self, instrument_keys: Sequence[str]) -> Any:
        if self._live_feed_client is None:
            raise DhanMarketdataUnavailableError("live_feed_client is not configured")
        cleaned = [
            _require_non_empty(str(item), field_name="instrument_key")
            for item in instrument_keys
        ]
        return self._live_feed_client.unsubscribe(cleaned)

    # ------------------------------------------------------------------
    # Health / snapshot
    # ------------------------------------------------------------------

    def lane_health(self, role: str, *, now_ns: int | None = None) -> DhanLaneHealth:
        with self._lock:
            return self._lane_health_locked(
                role=_normalize_role(role),
                now_ns=_coerce_ns(
                    now_ns if now_ns is not None else _now_ns(),
                    field_name="now_ns",
                    allow_none=False,
                ),
            )

    def snapshot(self, *, now_ns: int | None = None) -> DhanMarketdataSnapshot:
        with self._lock:
            resolved_now_ns = _coerce_ns(
                now_ns if now_ns is not None else _now_ns(),
                field_name="now_ns",
                allow_none=False,
            )
            auth_snapshot = self.auth_snapshot()
            futures_health = self._lane_health_locked(role=_ROLE_FUTURES, now_ns=resolved_now_ns)
            selected_health = self._lane_health_locked(
                role=_ROLE_SELECTED_OPTION,
                now_ns=resolved_now_ns,
            )
            context_health = self._lane_health_locked(
                role=_ROLE_OPTION_CONTEXT,
                now_ns=resolved_now_ns,
            )
            return DhanMarketdataSnapshot(
                provider_id=self._config.provider_id,
                config_revision=self._config.config_revision,
                computed_at_ns=resolved_now_ns,
                auth_snapshot=None if auth_snapshot is None else auth_snapshot.to_dict(),
                futures_tick=self._futures_lane.snapshot_obj,
                selected_option_tick=self._selected_option_lane.snapshot_obj,
                shadow_option_ticks={
                    key: tick.to_dict()
                    for key, tick in self._shadow_option_ticks.items()
                },
                context_snapshot=self._context_lane.snapshot_obj,
                futures_health=futures_health,
                selected_option_health=selected_health,
                option_context_health=context_health,
                metadata={
                    "selected_option_instrument_key": self._selected_option_instrument_key,
                    "shadow_option_count": len(self._shadow_option_ticks),
                },
            )

    def build_public_health_payload(self, *, now_ns: int | None = None) -> dict[str, Any]:
        snap = self.snapshot(now_ns=now_ns)
        return {
            "provider_id": snap.provider_id,
            "config_revision": snap.config_revision,
            "computed_at_ns": snap.computed_at_ns,
            "computed_at_iso": _iso_from_ns(snap.computed_at_ns),
            "auth": snap.auth_snapshot,
            "futures_marketdata": snap.futures_health.to_dict(),
            "selected_option_marketdata": snap.selected_option_health.to_dict(),
            "option_context": snap.option_context_health.to_dict(),
            "selected_option_instrument_key": snap.metadata.get("selected_option_instrument_key"),
            "shadow_option_count": snap.metadata.get("shadow_option_count"),
        }

    def build_provider_health_payloads(self, *, now_ns: int | None = None) -> dict[str, dict[str, Any]]:
        snap = self.snapshot(now_ns=now_ns)
        return {
            _ROLE_FUTURES: snap.futures_health.to_provider_health_payload(),
            _ROLE_SELECTED_OPTION: snap.selected_option_health.to_provider_health_payload(),
            _ROLE_OPTION_CONTEXT: snap.option_context_health.to_provider_health_payload(),
        }

    # ------------------------------------------------------------------
    # Error surfaces
    # ------------------------------------------------------------------

    def mark_lane_error(
        self,
        *,
        role: str,
        error: str,
        ts_event_ns: int | None = None,
    ) -> None:
        with self._lock:
            normalized_role = _normalize_role(role)
            message = _require_non_empty(error, field_name="error")
            now_ns = _coerce_ns(
                ts_event_ns if ts_event_ns is not None else _now_ns(),
                field_name="ts_event_ns",
                allow_none=False,
            )
            lane = self._lane_state_for_role(normalized_role)
            lane.mark_error(ts_ns=now_ns, error=message)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_token_or_none(self) -> str | None:
        if self._auth_manager is None:
            return None
        try:
            return self._auth_manager.get_access_token(ensure_authenticated=True)
        except BrokerSessionUnavailableError as exc:
            raise DhanMarketdataAuthError(str(exc)) from exc

    def _require_enabled_lane(self, role: str) -> None:
        if not self._config.enabled:
            raise DhanMarketdataUnavailableError("Dhan marketdata is disabled by config")

        enabled = {
            _ROLE_FUTURES: self._config.futures_marketdata_enabled,
            _ROLE_SELECTED_OPTION: self._config.selected_option_marketdata_enabled,
            _ROLE_OPTION_CONTEXT: self._config.option_context_enabled,
        }[role]
        if not enabled:
            raise DhanMarketdataUnavailableError(f"{role} is disabled by config")

        if self._config.auth_required:
            auth = self.auth_snapshot()
            if auth is None or not auth.authenticated:
                raise DhanMarketdataAuthError(
                    f"{role} requires authenticated Dhan session"
                )

    def _normalize_live_tick(
        self,
        raw_tick: Any,
        *,
        role: str,
        instrument_key: str | None,
        symbol: str | None,
        ts_event_ns: int,
    ) -> DhanLiveTick:
        if not isinstance(raw_tick, Mapping):
            raise DhanMarketdataValidationError(
                f"{role} raw tick must be a mapping"
            )
        raw = {str(k): v for k, v in raw_tick.items()}

        resolved_instrument_key = (
            instrument_key
            or _coerce_str(
                _pick(
                    raw,
                    "instrument_key",
                    "instrument",
                    "security_id",
                    "securityId",
                    "token",
                    "instrument_token",
                ),
                field_name="instrument_key",
                allow_none=True,
            )
        )
        if resolved_instrument_key is None:
            raise DhanMarketdataValidationError(
                f"{role} tick missing instrument_key/security_id/token"
            )

        resolved_symbol = symbol or _coerce_str(
            _pick(raw, "symbol", "trading_symbol", "tradingsymbol"),
            field_name="symbol",
            allow_none=True,
        )
        local_ts_ns = _coerce_ns(
            _pick(raw, "local_ts_ns", "ts_event_ns", "ts_ns", "timestamp_ns", "exchange_ts_ns"),
            field_name="local_ts_ns",
            allow_none=True,
        ) or ts_event_ns
        ltt_ns = _coerce_ns(
            _pick(raw, "ltt_ns", "last_trade_ts_ns", "trade_ts_ns", "ltt"),
            field_name="ltt_ns",
            allow_none=True,
        )

        bids = _normalize_depth_rows(
            _pick(raw, "bids", "buy_depth", "buyDepth", "bid_depth"),
            side_name="bids",
        )
        asks = _normalize_depth_rows(
            _pick(raw, "asks", "sell_depth", "sellDepth", "ask_depth"),
            side_name="asks",
        )

        best_bid = _coerce_float(
            _pick(raw, "best_bid", "bestBid", "bid", "best_bid_price"),
            field_name="best_bid",
            allow_none=True,
        )
        if best_bid is None and len(bids) > 0:
            best_bid = _coerce_float(bids[0].get("price"), field_name="bids[0].price", allow_none=True)

        best_ask = _coerce_float(
            _pick(raw, "best_ask", "bestAsk", "ask", "best_ask_price"),
            field_name="best_ask",
            allow_none=True,
        )
        if best_ask is None and len(asks) > 0:
            best_ask = _coerce_float(asks[0].get("price"), field_name="asks[0].price", allow_none=True)

        ltp = _coerce_float(
            _pick(raw, "ltp", "last_price", "lastPrice", "price"),
            field_name="ltp",
            allow_none=True,
        )
        ltq = _coerce_int(
            _pick(raw, "ltq", "last_traded_quantity", "lastTradeQty"),
            field_name="ltq",
            allow_none=True,
        )
        volume = _coerce_int(
            _pick(raw, "volume", "traded_volume", "totalVolume"),
            field_name="volume",
            allow_none=True,
        )
        oi = _coerce_int(
            _pick(raw, "oi", "open_interest", "openInterest"),
            field_name="oi",
            allow_none=True,
        )

        metadata = _normalize_metadata(
            raw,
            exclude=(
                "instrument_key",
                "instrument",
                "security_id",
                "securityId",
                "token",
                "instrument_token",
                "symbol",
                "trading_symbol",
                "tradingsymbol",
                "local_ts_ns",
                "ts_event_ns",
                "ts_ns",
                "timestamp_ns",
                "exchange_ts_ns",
                "ltt_ns",
                "last_trade_ts_ns",
                "trade_ts_ns",
                "ltt",
                "best_bid",
                "bestBid",
                "bid",
                "best_bid_price",
                "best_ask",
                "bestAsk",
                "ask",
                "best_ask_price",
                "ltp",
                "last_price",
                "lastPrice",
                "price",
                "ltq",
                "last_traded_quantity",
                "lastTradeQty",
                "volume",
                "traded_volume",
                "totalVolume",
                "oi",
                "open_interest",
                "openInterest",
                "bids",
                "buy_depth",
                "buyDepth",
                "bid_depth",
                "asks",
                "sell_depth",
                "sellDepth",
                "ask_depth",
            ),
        )

        return DhanLiveTick(
            provider_id=self._config.provider_id,
            role=role,
            instrument_key=resolved_instrument_key,
            symbol=resolved_symbol,
            local_ts_ns=local_ts_ns,
            ltt_ns=ltt_ns,
            ltp=ltp,
            ltq=ltq,
            best_bid=best_bid,
            best_ask=best_ask,
            volume=volume,
            oi=oi,
            bids=bids,
            asks=asks,
            metadata=metadata,
        )

    def _normalize_context_snapshot(
        self,
        raw_snapshot: Any,
        *,
        ts_event_ns: int,
    ) -> DhanContextSnapshot:
        rows_payload: Any
        metadata: dict[str, Any] = {}

        if isinstance(raw_snapshot, Mapping):
            raw_mapping = {str(k): v for k, v in raw_snapshot.items()}
            rows_payload = _pick(
                raw_mapping,
                "rows",
                "chain_rows",
                "chain",
                "data",
                "options",
                "records",
            )
            if rows_payload is None:
                if any(k in raw_mapping for k in ("symbol", "strike", "strikePrice", "token")):
                    rows_payload = [raw_mapping]
                else:
                    rows_payload = []
            metadata = {
                "source_keys": sorted(raw_mapping.keys()),
            }
        elif isinstance(raw_snapshot, Sequence) and not isinstance(
            raw_snapshot,
            (str, bytes, bytearray),
        ):
            rows_payload = list(raw_snapshot)
            metadata = {
                "source": "sequence",
            }
        else:
            raise DhanMarketdataValidationError(
                "raw context snapshot must be mapping or sequence"
            )

        if not isinstance(rows_payload, Sequence) or isinstance(
            rows_payload,
            (str, bytes, bytearray),
        ):
            raise DhanMarketdataValidationError(
                "context rows payload must be a sequence"
            )

        rows: list[DhanContextRow] = []
        monitored_symbols: list[str] = []

        for index, row in enumerate(rows_payload):
            if not isinstance(row, Mapping):
                raise DhanMarketdataValidationError(
                    f"context row[{index}] must be a mapping"
                )
            raw_row = {str(k): v for k, v in row.items()}

            symbol = _coerce_str(
                _pick(raw_row, "symbol", "trading_symbol", "tradingsymbol"),
                field_name=f"context_row[{index}].symbol",
                allow_none=True,
            )
            option_type = _coerce_str(
                _pick(raw_row, "option_type", "optionType", "right"),
                field_name=f"context_row[{index}].option_type",
                allow_none=True,
            )
            strike = _coerce_float(
                _pick(raw_row, "strike", "strikePrice", "strike_price"),
                field_name=f"context_row[{index}].strike",
                allow_none=True,
            )
            expiry = _coerce_str(
                _pick(raw_row, "expiry", "expiry_date", "expiryDate"),
                field_name=f"context_row[{index}].expiry",
                allow_none=True,
            )
            token = _coerce_str(
                _pick(raw_row, "token", "security_id", "securityId", "instrument_key"),
                field_name=f"context_row[{index}].token",
                allow_none=True,
            )
            ltp = _coerce_float(
                _pick(raw_row, "ltp", "last_price", "price"),
                field_name=f"context_row[{index}].ltp",
                allow_none=True,
            )
            bid = _coerce_float(
                _pick(raw_row, "bid", "best_bid", "bestBid"),
                field_name=f"context_row[{index}].bid",
                allow_none=True,
            )
            ask = _coerce_float(
                _pick(raw_row, "ask", "best_ask", "bestAsk"),
                field_name=f"context_row[{index}].ask",
                allow_none=True,
            )
            volume = _coerce_int(
                _pick(raw_row, "volume", "traded_volume", "totalVolume"),
                field_name=f"context_row[{index}].volume",
                allow_none=True,
            )
            oi = _coerce_int(
                _pick(raw_row, "oi", "open_interest", "openInterest"),
                field_name=f"context_row[{index}].oi",
                allow_none=True,
            )
            iv = _coerce_float(
                _pick(raw_row, "iv", "implied_volatility", "impliedVolatility"),
                field_name=f"context_row[{index}].iv",
                allow_none=True,
            )
            delta = _coerce_float(
                _pick(raw_row, "delta"),
                field_name=f"context_row[{index}].delta",
                allow_none=True,
            )
            gamma = _coerce_float(
                _pick(raw_row, "gamma"),
                field_name=f"context_row[{index}].gamma",
                allow_none=True,
            )
            theta = _coerce_float(
                _pick(raw_row, "theta"),
                field_name=f"context_row[{index}].theta",
                allow_none=True,
            )
            vega = _coerce_float(
                _pick(raw_row, "vega"),
                field_name=f"context_row[{index}].vega",
                allow_none=True,
            )

            if symbol is not None:
                monitored_symbols.append(symbol)

            row_metadata = _normalize_metadata(
                raw_row,
                exclude=(
                    "symbol",
                    "trading_symbol",
                    "tradingsymbol",
                    "option_type",
                    "optionType",
                    "right",
                    "strike",
                    "strikePrice",
                    "strike_price",
                    "expiry",
                    "expiry_date",
                    "expiryDate",
                    "token",
                    "security_id",
                    "securityId",
                    "instrument_key",
                    "ltp",
                    "last_price",
                    "price",
                    "bid",
                    "best_bid",
                    "bestBid",
                    "ask",
                    "best_ask",
                    "bestAsk",
                    "volume",
                    "traded_volume",
                    "totalVolume",
                    "oi",
                    "open_interest",
                    "openInterest",
                    "iv",
                    "implied_volatility",
                    "impliedVolatility",
                    "delta",
                    "gamma",
                    "theta",
                    "vega",
                ),
            )

            rows.append(
                DhanContextRow(
                    symbol=symbol,
                    option_type=option_type,
                    strike=strike,
                    expiry=expiry,
                    token=token,
                    ltp=ltp,
                    bid=bid,
                    ask=ask,
                    volume=volume,
                    oi=oi,
                    iv=iv,
                    delta=delta,
                    gamma=gamma,
                    theta=theta,
                    vega=vega,
                    metadata=row_metadata,
                )
            )

        dedup_monitored_symbols = tuple(dict.fromkeys(monitored_symbols))

        return DhanContextSnapshot(
            provider_id=self._config.provider_id,
            local_ts_ns=ts_event_ns,
            chain_rows=tuple(rows),
            monitored_symbols=dedup_monitored_symbols,
            chain_row_count=len(rows),
            metadata=_freeze_mapping(metadata),
        )

    def _lane_state_for_role(self, role: str) -> _LaneState:
        if role == _ROLE_FUTURES:
            return self._futures_lane
        if role == _ROLE_SELECTED_OPTION:
            return self._selected_option_lane
        if role == _ROLE_OPTION_CONTEXT:
            return self._context_lane
        raise DhanMarketdataValidationError(f"unknown role: {role!r}")

    def _lane_config_for_role(self, role: str) -> tuple[bool, int, int]:
        if role == _ROLE_FUTURES:
            return (
                self._config.futures_marketdata_enabled,
                self._config.futures_stale_after_ms,
                self._config.futures_dead_after_ms,
            )
        if role == _ROLE_SELECTED_OPTION:
            return (
                self._config.selected_option_marketdata_enabled,
                self._config.selected_option_stale_after_ms,
                self._config.selected_option_dead_after_ms,
            )
        if role == _ROLE_OPTION_CONTEXT:
            return (
                self._config.option_context_enabled,
                self._config.option_context_stale_after_ms,
                self._config.option_context_dead_after_ms,
            )
        raise DhanMarketdataValidationError(f"unknown role: {role!r}")

    def _lane_health_locked(self, *, role: str, now_ns: int) -> DhanLaneHealth:
        enabled_by_lane, stale_after_ms, dead_after_ms = self._lane_config_for_role(role)
        lane = self._lane_state_for_role(role)

        enabled = self._config.enabled and enabled_by_lane
        auth_required = self._config.auth_required
        auth_snapshot = self.auth_snapshot()
        authenticated = (
            True
            if not auth_required
            else bool(auth_snapshot.authenticated) if auth_snapshot is not None else False
        )

        if not self._config.enabled:
            status = _STATUS_DISABLED
            age_ms = None
        elif not enabled_by_lane:
            status = _STATUS_DISABLED
            age_ms = None
        elif auth_required and not authenticated:
            status = _STATUS_AUTH_FAILED
            age_ms = None
        elif lane.last_update_ns is None:
            status = _STATUS_UNAVAILABLE
            age_ms = None
        else:
            age_ms = int(max(now_ns - lane.last_update_ns, 0) / 1_000_000)
            if age_ms > dead_after_ms:
                status = _STATUS_UNAVAILABLE
            elif age_ms > stale_after_ms:
                status = _STATUS_STALE
            elif lane.last_error is not None:
                status = _STATUS_DEGRADED
            else:
                status = _STATUS_HEALTHY

        return DhanLaneHealth(
            provider_id=self._config.provider_id,
            role=role,
            enabled=enabled,
            auth_required=auth_required,
            authenticated=authenticated,
            status=status,
            last_update_ns=lane.last_update_ns,
            age_ms=age_ms,
            stale_after_ms=stale_after_ms,
            dead_after_ms=dead_after_ms,
            last_error=lane.last_error,
            last_error_ns=lane.last_error_ns,
            message=_lane_status_message(
                role=role,
                status=status,
                age_ms=age_ms,
                last_error=lane.last_error,
            ),
        )


__all__ = [
    "DhanContextClient",
    "DhanContextRow",
    "DhanContextSnapshot",
    "DhanLaneHealth",
    "DhanLiveFeedClient",
    "DhanLiveTick",
    "DhanMarketdataConfig",
    "DhanMarketdataError",
    "DhanMarketdataAuthError",
    "DhanMarketdataManager",
    "DhanMarketdataSnapshot",
    "DhanMarketdataUnavailableError",
    "DhanMarketdataValidationError",
]
