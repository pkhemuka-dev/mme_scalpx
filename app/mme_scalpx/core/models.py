"""
app/mme_scalpx/core/models.py

Canonical typed schema models for ScalpX MME.

Purpose
-------
This module OWNS:
- canonical typed models for stream payloads
- canonical typed models for latest-state hash payloads
- strict validation of field values and schema invariants
- deterministic model <-> mapping conversion
- model registry for codec/transport dispatch
- shared schema-level vocabularies that are not Redis naming contracts

This module DOES NOT own:
- Redis naming contracts
- runtime settings loading
- wire serialization / JSON encoding
- Redis client lifecycle
- strategy implementation logic
- exchange session/holiday policy
- startup/bootstrap composition

Core design rules
-----------------
- core.names is the single source of truth for symbolic constants and allowed
  cross-module enums that belong to the naming surface.
- core.validators owns low-level scalar/type validation primitives.
- core.codec serializes; models.py validates and structures.
- Stream/event payload models may be nested and expressive.
- Latest-state hash models must remain flat/simple for stable hash transport.
- Canonical transport time unit is epoch nanoseconds.
- Field names must use explicit unit suffixes such as *_ns or *_ms.
- Validation failures must be explicit and deterministic.
- EventEnvelope.payload is always a mapping, never None.
- ClockSnapshot is an internal runtime artifact and must never leak into wire
  payloads.
"""

from __future__ import annotations

from dataclasses import MISSING, dataclass, field, fields
from types import MappingProxyType
from typing import Any, ClassVar, Final, Mapping, Sequence, TypeVar, get_args, get_origin

from app.mme_scalpx.core import names
from app.mme_scalpx.core.clock import ClockSnapshot
from app.mme_scalpx.core.validators import (
    ValidationError,
    optional_non_empty_str,
    require,
    require_bool,
    require_float,
    require_int,
    require_literal,
    require_mapping,
    require_non_empty_str,
    require_sequence_of_str,
)

# ============================================================================
# Exceptions
# ============================================================================


class ModelError(ValueError):
    """Base error for schema/model failures."""


class ModelValidationError(ModelError):
    """Raised when input data or model invariants are invalid."""


# ============================================================================
# Local wrappers around shared validators
# ============================================================================


def _wrap_validation(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        if isinstance(exc, ModelValidationError):
            raise
        if isinstance(exc, ValidationError):
            raise ModelValidationError(str(exc)) from exc
        raise ModelValidationError(str(exc)) from exc


def _require(condition: bool, message: str) -> None:
    _wrap_validation(require, condition, message)


def _require_non_empty_str(value: str, field_name: str) -> str:
    return _wrap_validation(require_non_empty_str, value, field_name=field_name)


def _optional_non_empty_str(value: str | None, field_name: str) -> str | None:
    return _wrap_validation(optional_non_empty_str, value, field_name=field_name)


def _require_bool(value: bool, field_name: str) -> bool:
    return _wrap_validation(require_bool, value, field_name=field_name)


def _require_int(
    value: int,
    field_name: str,
    *,
    min_value: int | None = None,
) -> int:
    return _wrap_validation(
        require_int,
        value,
        field_name=field_name,
        min_value=min_value,
    )


def _require_float(
    value: float | int,
    field_name: str,
    *,
    min_value: float | None = None,
) -> float:
    return _wrap_validation(
        require_float,
        value,
        field_name=field_name,
        min_value=min_value,
    )


def _require_mapping(value: Mapping[str, Any], field_name: str) -> dict[str, Any]:
    return _wrap_validation(require_mapping, value, field_name=field_name)


def _require_str_sequence(value: Sequence[str], field_name: str) -> tuple[str, ...]:
    return _wrap_validation(require_sequence_of_str, value, field_name=field_name)


def _require_literal(
    value: str,
    field_name: str,
    *,
    allowed: Sequence[str],
) -> str:
    return _wrap_validation(
        require_literal,
        value,
        field_name=field_name,
        allowed=allowed,
    )


# ============================================================================
# Shared canonical literal sets
# ============================================================================

T = TypeVar("T", bound="SchemaBase")


ALLOWED_ENTRY_MODES: Final[tuple[str, ...]] = tuple(names.ALLOWED_ENTRY_MODES)
ALLOWED_OPTION_SIDES: Final[tuple[str, ...]] = (
    names.SIDE_CALL,
    names.SIDE_PUT,
)
ALLOWED_POSITION_SIDES: Final[tuple[str, ...]] = tuple(names.ALLOWED_POSITION_SIDES)
ALLOWED_ACTIONS: Final[tuple[str, ...]] = (
    names.ACTION_ENTER_CALL,
    names.ACTION_ENTER_PUT,
    names.ACTION_EXIT,
    names.ACTION_HOLD,
    names.ACTION_BLOCK,
)
ALLOWED_POSITION_EFFECTS: Final[tuple[str, ...]] = tuple(names.ALLOWED_POSITION_EFFECTS)
ALLOWED_HEALTH_STATUSES: Final[tuple[str, ...]] = tuple(names.ALLOWED_HEALTH_STATUSES)
ALLOWED_ERROR_SEVERITIES: Final[tuple[str, ...]] = tuple(names.ALLOWED_ERROR_SEVERITIES)
ALLOWED_EXECUTION_MODES: Final[tuple[str, ...]] = tuple(names.ALLOWED_EXECUTION_MODES)
ALLOWED_STRATEGY_MODES: Final[tuple[str, ...]] = tuple(names.ALLOWED_STRATEGY_MODES)
ALLOWED_SYSTEM_STATES: Final[tuple[str, ...]] = tuple(names.ALLOWED_SYSTEM_STATES)
ALLOWED_ACK_TYPES: Final[tuple[str, ...]] = tuple(names.ALLOWED_ACK_TYPES)

ALLOWED_STRATEGY_FAMILY_IDS: Final[tuple[str, ...]] = tuple(names.ALLOWED_STRATEGY_FAMILY_IDS)
ALLOWED_DOCTRINE_IDS: Final[tuple[str, ...]] = tuple(names.ALLOWED_DOCTRINE_IDS)
ALLOWED_BRANCH_IDS: Final[tuple[str, ...]] = tuple(names.ALLOWED_BRANCH_IDS)
ALLOWED_STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(
    names.ALLOWED_STRATEGY_RUNTIME_MODES
)
ALLOWED_FAMILY_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(
    names.ALLOWED_FAMILY_RUNTIME_MODES
)
ALLOWED_PROVIDER_IDS: Final[tuple[str, ...]] = tuple(names.ALLOWED_PROVIDER_IDS)
ALLOWED_PROVIDER_ROLES: Final[tuple[str, ...]] = tuple(names.ALLOWED_PROVIDER_ROLES)
ALLOWED_PROVIDER_STATUSES: Final[tuple[str, ...]] = tuple(
    names.ALLOWED_PROVIDER_STATUSES
)
ALLOWED_PROVIDER_FAILOVER_MODES: Final[tuple[str, ...]] = tuple(
    names.ALLOWED_PROVIDER_FAILOVER_MODES
)
ALLOWED_PROVIDER_OVERRIDE_MODES: Final[tuple[str, ...]] = tuple(
    names.ALLOWED_PROVIDER_OVERRIDE_MODES
)
ALLOWED_PROVIDER_TRANSITION_REASONS: Final[tuple[str, ...]] = tuple(
    names.ALLOWED_PROVIDER_TRANSITION_REASONS
)
ALLOWED_CONTROL_MODES: Final[tuple[str, ...]] = tuple(names.ALLOWED_CONTROL_MODES)

MISO_ALLOWED_STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = (
    names.STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
    names.STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED,
    names.STRATEGY_RUNTIME_MODE_DISABLED,
)
NON_MISO_ALLOWED_STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = (
    names.STRATEGY_RUNTIME_MODE_NORMAL,
    names.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
    names.STRATEGY_RUNTIME_MODE_DISABLED,
)

ALLOWED_OPERATOR_MODE_VALUES: Final[tuple[str, ...]] = tuple(
    dict.fromkeys(
        (
            *ALLOWED_CONTROL_MODES,
            *ALLOWED_EXECUTION_MODES,
            *ALLOWED_STRATEGY_MODES,
            *ALLOWED_STRATEGY_RUNTIME_MODES,
            *ALLOWED_FAMILY_RUNTIME_MODES,
        )
    )
)

ALLOWED_COMMAND_TYPES: Final[tuple[str, ...]] = tuple(names.ALLOWED_COMMAND_TYPES)


# ============================================================================
# Shared schema-level vocabularies
#
# These are model-owned because they describe payload/status semantics rather
# than Redis naming contracts. Services may import these, but must not redefine
# parallel versions locally.
# ============================================================================


class InstrumentRole:
    FUTURES = "FUTURES"
    CE_ATM = "CE_ATM"
    CE_ATM1 = "CE_ATM1"
    PE_ATM = "PE_ATM"
    PE_ATM1 = "PE_ATM1"


ALLOWED_INSTRUMENT_ROLES: Final[tuple[str, ...]] = (
    InstrumentRole.FUTURES,
    InstrumentRole.CE_ATM,
    InstrumentRole.CE_ATM1,
    InstrumentRole.PE_ATM,
    InstrumentRole.PE_ATM1,
)


class TickValidity:
    OK: Final[str] = "OK"
    MISSING_LTP: Final[str] = "MISSING_LTP"
    NON_POSITIVE_LTP: Final[str] = "NON_POSITIVE_LTP"
    NEGATIVE_QUANTITY: Final[str] = "NEGATIVE_QUANTITY"
    INCOMPLETE_QUOTE: Final[str] = "INCOMPLETE_QUOTE"
    BAD_TICK_SIZE: Final[str] = "BAD_TICK_SIZE"
    NON_POSITIVE_SPREAD: Final[str] = "NON_POSITIVE_SPREAD"
    ANOMALY_CLAMPED: Final[str] = "ANOMALY_CLAMPED"
    STALE: Final[str] = "STALE"
    MALFORMED: Final[str] = "MALFORMED"


ALLOWED_TICK_VALIDITY: Final[tuple[str, ...]] = (
    TickValidity.OK,
    TickValidity.MISSING_LTP,
    TickValidity.NON_POSITIVE_LTP,
    TickValidity.NEGATIVE_QUANTITY,
    TickValidity.INCOMPLETE_QUOTE,
    TickValidity.BAD_TICK_SIZE,
    TickValidity.NON_POSITIVE_SPREAD,
    TickValidity.ANOMALY_CLAMPED,
    TickValidity.STALE,
    TickValidity.MALFORMED,
)


class SnapshotValidity:
    OK: Final[str] = "OK"
    INCOMPLETE: Final[str] = "INCOMPLETE"
    INVALID_MEMBER: Final[str] = "INVALID_MEMBER"
    UNSYNCED: Final[str] = "UNSYNCED"
    STALE: Final[str] = "STALE"


ALLOWED_SNAPSHOT_VALIDITY: Final[tuple[str, ...]] = (
    SnapshotValidity.OK,
    SnapshotValidity.INCOMPLETE,
    SnapshotValidity.INVALID_MEMBER,
    SnapshotValidity.UNSYNCED,
    SnapshotValidity.STALE,
)


class StrategyRegime:
    LOWVOL: Final[str] = "LOWVOL"
    NORMAL: Final[str] = "NORMAL"
    FAST: Final[str] = "FAST"


ALLOWED_STRATEGY_REGIMES: Final[tuple[str, ...]] = (
    StrategyRegime.LOWVOL,
    StrategyRegime.NORMAL,
    StrategyRegime.FAST,
)


class RetestType:
    NONE: Final[str] = "NONE"
    FULL_RETEST: Final[str] = "FULL_RETEST"
    HESITATION: Final[str] = "HESITATION"


ALLOWED_RETEST_TYPES: Final[tuple[str, ...]] = (
    RetestType.NONE,
    RetestType.FULL_RETEST,
    RetestType.HESITATION,
)




def _validate_strategy_runtime_mode_for_family(
    strategy_family_id: str | None,
    strategy_runtime_mode: str | None,
    *,
    field_name: str,
) -> None:
    if strategy_family_id is None or strategy_runtime_mode is None:
        return

    _require_literal(
        strategy_family_id,
        f"{field_name}.strategy_family_id",
        allowed=ALLOWED_STRATEGY_FAMILY_IDS,
    )
    _require_literal(
        strategy_runtime_mode,
        field_name,
        allowed=ALLOWED_STRATEGY_RUNTIME_MODES,
    )

    if strategy_family_id == names.STRATEGY_FAMILY_MISO:
        _require(
            strategy_runtime_mode in MISO_ALLOWED_STRATEGY_RUNTIME_MODES,
            f"{field_name}={strategy_runtime_mode!r} is invalid for MISO",
        )
        return

    _require(
        strategy_runtime_mode in NON_MISO_ALLOWED_STRATEGY_RUNTIME_MODES,
        f"{field_name}={strategy_runtime_mode!r} is invalid for non-MISO family",
    )


def _validate_family_doctrine_pair(
    strategy_family_id: str | None,
    doctrine_id: str | None,
) -> None:
    if strategy_family_id is not None:
        _require_literal(
            strategy_family_id,
            "strategy_family_id",
            allowed=ALLOWED_STRATEGY_FAMILY_IDS,
        )
    if doctrine_id is not None:
        _require_literal(
            doctrine_id,
            "doctrine_id",
            allowed=ALLOWED_DOCTRINE_IDS,
        )
    if strategy_family_id is not None and doctrine_id is not None:
        _require(
            strategy_family_id == doctrine_id,
            "strategy_family_id and doctrine_id must match in the frozen family surface",
        )


def _validate_branch_side_pair(branch_id: str | None, side: str | None) -> None:
    if branch_id is not None:
        _require_literal(branch_id, "branch_id", allowed=ALLOWED_BRANCH_IDS)
    if side is not None:
        _require_literal(side, "side", allowed=ALLOWED_OPTION_SIDES)
    if branch_id is not None and side is not None:
        _require(
            branch_id == side,
            "branch_id and side must match when both are provided",
        )


# ============================================================================
# Annotation coercion helpers
# ============================================================================


def _is_optional_annotation(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin is None:
        return False
    args = get_args(annotation)
    return len(args) == 2 and type(None) in args


def _unwrap_optional_annotation(annotation: Any) -> Any:
    return next(arg for arg in get_args(annotation) if arg is not type(None))


def _is_schema_subclass(value: Any) -> bool:
    return isinstance(value, type) and issubclass(value, SchemaBase)


def _coerce_value(annotation: Any, value: Any, *, field_name: str) -> Any:
    if value is None:
        if _is_optional_annotation(annotation):
            return None
        return None

    if _is_optional_annotation(annotation):
        annotation = _unwrap_optional_annotation(annotation)

    origin = get_origin(annotation)

    if annotation is Any:
        return value

    if origin is None:
        if _is_schema_subclass(annotation):
            if isinstance(value, annotation):
                return value
            if not isinstance(value, Mapping):
                raise ModelValidationError(
                    f"{field_name} must be mapping or {annotation.__name__}, "
                    f"got {type(value).__name__}"
                )
            return annotation.from_mapping(value)
        return value

    if origin is tuple:
        args = get_args(annotation)
        if len(args) == 2 and args[1] is Ellipsis:
            item_type = args[0]
            if not isinstance(value, Sequence) or isinstance(
                value,
                (str, bytes, bytearray),
            ):
                raise ModelValidationError(
                    f"{field_name} must be sequence, got {type(value).__name__}"
                )
            return tuple(
                _coerce_value(item_type, item, field_name=f"{field_name}[]")
                for item in value
            )

    if origin is list:
        (item_type,) = get_args(annotation)
        if not isinstance(value, Sequence) or isinstance(
            value,
            (str, bytes, bytearray),
        ):
            raise ModelValidationError(
                f"{field_name} must be sequence, got {type(value).__name__}"
            )
        return [
            _coerce_value(item_type, item, field_name=f"{field_name}[]")
            for item in value
        ]

    if origin in (dict, Mapping):
        key_type, value_type = get_args(annotation)
        if not isinstance(value, Mapping):
            raise ModelValidationError(
                f"{field_name} must be mapping, got {type(value).__name__}"
            )
        out: dict[Any, Any] = {}
        for key, item in value.items():
            coerced_key = _coerce_value(
                key_type,
                key,
                field_name=f"{field_name}.key",
            )
            coerced_value = _coerce_value(
                value_type,
                item,
                field_name=f"{field_name}[{coerced_key!r}]",
            )
            out[coerced_key] = coerced_value
        return out

    return value


def _plain_value(value: Any) -> Any:
    if isinstance(value, SchemaBase):
        return value.to_dict()

    if isinstance(value, ClockSnapshot):
        raise ModelValidationError(
            "ClockSnapshot is an internal runtime object and must not appear "
            "inside model payload serialization"
        )

    if isinstance(value, tuple):
        return [_plain_value(item) for item in value]

    if isinstance(value, list):
        return [_plain_value(item) for item in value]

    if isinstance(value, Mapping):
        return {str(k): _plain_value(v) for k, v in value.items()}

    return value


# ============================================================================
# Base schema model
# ============================================================================


@dataclass(frozen=True, slots=True)
class SchemaBase:
    """Base class for all canonical MME schema models."""

    _TYPE: ClassVar[str] = "schema_base"

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Override in subclasses to enforce invariants."""

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for dc_field in fields(self):
            out[dc_field.name] = _plain_value(getattr(self, dc_field.name))
        return out

    def to_mapping(self) -> dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_mapping(cls: type[T], raw: Mapping[str, Any]) -> T:
        if not isinstance(raw, Mapping):
            raise ModelValidationError(
                f"{cls.__name__}.from_mapping() requires mapping, "
                f"got {type(raw).__name__}"
            )

        known = {dc_field.name: dc_field for dc_field in fields(cls)}
        raw_keys = set(raw.keys())
        known_keys = set(known.keys())

        extra = raw_keys - known_keys
        if extra:
            raise ModelValidationError(
                f"{cls.__name__} received unknown fields: "
                f"{', '.join(sorted(map(str, extra)))}"
            )

        kwargs: dict[str, Any] = {}
        for field_name, dc_field in known.items():
            if field_name in raw:
                kwargs[field_name] = _coerce_value(
                    dc_field.type,
                    raw[field_name],
                    field_name=f"{cls.__name__}.{field_name}",
                )
                continue

            if dc_field.default is not MISSING:
                continue
            if hasattr(dc_field, "default_factory") and dc_field.default_factory is not MISSING:
                continue

            raise ModelValidationError(
                f"{cls.__name__} missing required field: {field_name}"
            )

        return cls(**kwargs)

    @classmethod
    def from_dict(cls: type[T], raw: Mapping[str, Any]) -> T:
        return cls.from_mapping(raw)


# ============================================================================
# Transport envelope
# ============================================================================


@dataclass(frozen=True, slots=True)
class EventEnvelope(SchemaBase):
    envelope_type: str
    schema_version: int = names.DEFAULT_SCHEMA_VERSION
    ts_event_ns: int = 0
    ts_ingest_ns: int = 0
    producer: str = ""
    correlation_id: str | None = None
    stream: str | None = None
    replay: bool = False
    payload: Mapping[str, Any] = field(default_factory=dict)

    _TYPE: ClassVar[str] = "event_envelope"

    def validate(self) -> None:
        _require_non_empty_str(self.envelope_type, "envelope_type")
        _require_int(self.schema_version, "schema_version", min_value=1)
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_int(self.ts_ingest_ns, "ts_ingest_ns", min_value=0)
        _require_non_empty_str(self.producer, "producer")
        if self.correlation_id is not None:
            _optional_non_empty_str(self.correlation_id, "correlation_id")
        if self.stream is not None:
            _optional_non_empty_str(self.stream, "stream")
        _require_bool(self.replay, "replay")

        payload = _require_mapping(self.payload, "payload")
        plain_payload = {str(k): _plain_value(v) for k, v in payload.items()}
        object.__setattr__(self, "payload", plain_payload)


# ============================================================================
# Feed / market data models
# Shared wire truth between feeds and downstream consumers.
# ============================================================================


@dataclass(frozen=True, slots=True)
class BookLevel(SchemaBase):
    price: float
    quantity: int
    orders: int | None = None

    _TYPE: ClassVar[str] = "book_level"

    def validate(self) -> None:
        _require_float(self.price, "price", min_value=0.0)
        _require_int(self.quantity, "quantity", min_value=0)
        if self.orders is not None:
            _require_int(self.orders, "orders", min_value=0)



@dataclass(frozen=True, slots=True)
class FeedTick(SchemaBase):
    instrument_key: str
    instrument_role: str
    ts_event_ns: int
    provider_id: str | None = None
    provider_role: str | None = None
    exchange: str | None = None
    instrument_token: str | None = None
    trading_symbol: str | None = None
    ts_provider_ns: int | None = None
    ts_recv_ns: int | None = None
    seq_no: int | None = None
    ltp: float | None = None
    last_qty: int | None = None
    volume: int | None = None
    oi: int | None = None
    bid: float | None = None
    ask: float | None = None
    bid_qty: int | None = None
    ask_qty: int | None = None
    bids: tuple[BookLevel, ...] = ()
    asks: tuple[BookLevel, ...] = ()
    option_side: str | None = None
    strike: float | None = None
    expiry: str | None = None
    tick_validity: str = TickValidity.OK
    reject_reason: str | None = None
    is_selected_option: bool = False
    is_shadow_option: bool = False

    _TYPE: ClassVar[str] = "feed_tick"

    def validate(self) -> None:
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_literal(
            self.instrument_role,
            "instrument_role",
            allowed=ALLOWED_INSTRUMENT_ROLES,
        )
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        if self.provider_id is not None:
            _require_literal(
                self.provider_id,
                "provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.provider_role is not None:
            _require_literal(
                self.provider_role,
                "provider_role",
                allowed=ALLOWED_PROVIDER_ROLES,
            )
        if self.exchange is not None:
            _optional_non_empty_str(self.exchange, "exchange")
        if self.instrument_token is not None:
            _optional_non_empty_str(self.instrument_token, "instrument_token")
        if self.trading_symbol is not None:
            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
        if self.ts_provider_ns is not None:
            _require_int(self.ts_provider_ns, "ts_provider_ns", min_value=0)
        if self.ts_recv_ns is not None:
            _require_int(self.ts_recv_ns, "ts_recv_ns", min_value=0)
        if self.seq_no is not None:
            _require_int(self.seq_no, "seq_no", min_value=0)
        if self.ltp is not None:
            _require_float(self.ltp, "ltp", min_value=0.0)
        if self.last_qty is not None:
            _require_int(self.last_qty, "last_qty", min_value=0)
        if self.volume is not None:
            _require_int(self.volume, "volume", min_value=0)
        if self.oi is not None:
            _require_int(self.oi, "oi", min_value=0)
        if self.bid is not None:
            _require_float(self.bid, "bid", min_value=0.0)
        if self.ask is not None:
            _require_float(self.ask, "ask", min_value=0.0)
        if self.bid_qty is not None:
            _require_int(self.bid_qty, "bid_qty", min_value=0)
        if self.ask_qty is not None:
            _require_int(self.ask_qty, "ask_qty", min_value=0)
        if self.option_side is not None:
            _require_literal(
                self.option_side,
                "option_side",
                allowed=ALLOWED_OPTION_SIDES,
            )
        if self.strike is not None:
            _require_float(self.strike, "strike", min_value=0.0)
        if self.expiry is not None:
            _optional_non_empty_str(self.expiry, "expiry")
        _require_literal(
            self.tick_validity,
            "tick_validity",
            allowed=ALLOWED_TICK_VALIDITY,
        )
        if self.reject_reason is not None:
            _optional_non_empty_str(self.reject_reason, "reject_reason")
        _require_bool(self.is_selected_option, "is_selected_option")
        _require_bool(self.is_shadow_option, "is_shadow_option")
        if self.bid is not None and self.ask is not None:
            _require(self.ask >= self.bid, "ask must be >= bid")
        if self.is_shadow_option:
            _require(
                self.option_side is not None,
                "shadow option ticks require option_side",
            )


@dataclass(frozen=True, slots=True)
class FuturesSnapshot(SchemaBase):
    instrument_key: str
    ts_event_ns: int
    ltp: float
    provider_id: str | None = None
    provider_role: str | None = None
    instrument_token: str | None = None
    trading_symbol: str | None = None
    ts_provider_ns: int | None = None
    ts_recv_ns: int | None = None
    last_qty: int | None = None
    volume: int | None = None
    oi: int | None = None
    bid: float | None = None
    ask: float | None = None
    bid_qty: int | None = None
    ask_qty: int | None = None
    bids: tuple[BookLevel, ...] = ()
    asks: tuple[BookLevel, ...] = ()
    seq_no: int | None = None

    _TYPE: ClassVar[str] = "futures_snapshot"

    def validate(self) -> None:
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_float(self.ltp, "ltp", min_value=0.0)
        if self.provider_id is not None:
            _require_literal(
                self.provider_id,
                "provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.provider_role is not None:
            _require_literal(
                self.provider_role,
                "provider_role",
                allowed=ALLOWED_PROVIDER_ROLES,
            )
        if self.instrument_token is not None:
            _optional_non_empty_str(self.instrument_token, "instrument_token")
        if self.trading_symbol is not None:
            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
        if self.ts_provider_ns is not None:
            _require_int(self.ts_provider_ns, "ts_provider_ns", min_value=0)
        if self.ts_recv_ns is not None:
            _require_int(self.ts_recv_ns, "ts_recv_ns", min_value=0)
        if self.last_qty is not None:
            _require_int(self.last_qty, "last_qty", min_value=0)
        if self.volume is not None:
            _require_int(self.volume, "volume", min_value=0)
        if self.oi is not None:
            _require_int(self.oi, "oi", min_value=0)
        if self.bid is not None:
            _require_float(self.bid, "bid", min_value=0.0)
        if self.ask is not None:
            _require_float(self.ask, "ask", min_value=0.0)
        if self.bid_qty is not None:
            _require_int(self.bid_qty, "bid_qty", min_value=0)
        if self.ask_qty is not None:
            _require_int(self.ask_qty, "ask_qty", min_value=0)
        if self.seq_no is not None:
            _require_int(self.seq_no, "seq_no", min_value=0)
        if self.bid is not None and self.ask is not None:
            _require(self.ask >= self.bid, "ask must be >= bid")


@dataclass(frozen=True, slots=True)
class OptionSnapshot(SchemaBase):
    instrument_key: str
    ts_event_ns: int
    option_side: str
    strike: float
    expiry: str | None
    ltp: float
    provider_id: str | None = None
    provider_role: str | None = None
    instrument_token: str | None = None
    trading_symbol: str | None = None
    ts_provider_ns: int | None = None
    ts_recv_ns: int | None = None
    last_qty: int | None = None
    volume: int | None = None
    oi: int | None = None
    bid: float | None = None
    ask: float | None = None
    bid_qty: int | None = None
    ask_qty: int | None = None
    bids: tuple[BookLevel, ...] = ()
    asks: tuple[BookLevel, ...] = ()
    delta_proxy: float | None = None
    seq_no: int | None = None
    is_selected_option: bool = False
    is_shadow_option: bool = False

    _TYPE: ClassVar[str] = "option_snapshot"

    def validate(self) -> None:
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_literal(
            self.option_side,
            "option_side",
            allowed=ALLOWED_OPTION_SIDES,
        )
        _require_float(self.strike, "strike", min_value=0.0)
        if self.expiry is not None:
            _optional_non_empty_str(self.expiry, "expiry")
        _require_float(self.ltp, "ltp", min_value=0.0)
        if self.provider_id is not None:
            _require_literal(
                self.provider_id,
                "provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.provider_role is not None:
            _require_literal(
                self.provider_role,
                "provider_role",
                allowed=ALLOWED_PROVIDER_ROLES,
            )
        if self.instrument_token is not None:
            _optional_non_empty_str(self.instrument_token, "instrument_token")
        if self.trading_symbol is not None:
            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
        if self.ts_provider_ns is not None:
            _require_int(self.ts_provider_ns, "ts_provider_ns", min_value=0)
        if self.ts_recv_ns is not None:
            _require_int(self.ts_recv_ns, "ts_recv_ns", min_value=0)
        if self.last_qty is not None:
            _require_int(self.last_qty, "last_qty", min_value=0)
        if self.volume is not None:
            _require_int(self.volume, "volume", min_value=0)
        if self.oi is not None:
            _require_int(self.oi, "oi", min_value=0)
        if self.bid is not None:
            _require_float(self.bid, "bid", min_value=0.0)
        if self.ask is not None:
            _require_float(self.ask, "ask", min_value=0.0)
        if self.bid_qty is not None:
            _require_int(self.bid_qty, "bid_qty", min_value=0)
        if self.ask_qty is not None:
            _require_int(self.ask_qty, "ask_qty", min_value=0)
        if self.delta_proxy is not None:
            _require_float(self.delta_proxy, "delta_proxy")
        if self.seq_no is not None:
            _require_int(self.seq_no, "seq_no", min_value=0)
        _require_bool(self.is_selected_option, "is_selected_option")
        _require_bool(self.is_shadow_option, "is_shadow_option")
        if self.bid is not None and self.ask is not None:
            _require(self.ask >= self.bid, "ask must be >= bid")

@dataclass(frozen=True, slots=True)
class SnapshotMember(SchemaBase):
    role: str
    instrument_token: str
    trading_symbol: str
    ts_event_ns: int
    ltp: float
    best_bid: float = 0.0
    best_ask: float = 0.0
    bid_qty_5: int = 0
    ask_qty_5: int = 0
    spread: float = 0.0
    spread_ticks: float = 0.0
    age_ms: int = 0
    tick_size: float = 0.0
    lot_size: int = 0
    strike: float | None = None
    validity: str = TickValidity.OK

    _TYPE: ClassVar[str] = "snapshot_member"

    def validate(self) -> None:
        _require_literal(
            self.role,
            "role",
            allowed=ALLOWED_INSTRUMENT_ROLES,
        )
        _require_non_empty_str(self.instrument_token, "instrument_token")
        _require_non_empty_str(self.trading_symbol, "trading_symbol")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_float(self.ltp, "ltp", min_value=0.0)
        _require_float(self.best_bid, "best_bid", min_value=0.0)
        _require_float(self.best_ask, "best_ask", min_value=0.0)
        _require_int(self.bid_qty_5, "bid_qty_5", min_value=0)
        _require_int(self.ask_qty_5, "ask_qty_5", min_value=0)
        _require_float(self.spread, "spread", min_value=0.0)
        _require_float(self.spread_ticks, "spread_ticks", min_value=0.0)
        _require_int(self.age_ms, "age_ms", min_value=0)
        _require_float(self.tick_size, "tick_size", min_value=0.0)
        _require_int(self.lot_size, "lot_size", min_value=0)
        if self.strike is not None:
            _require_float(self.strike, "strike", min_value=0.0)
        _require_literal(
            self.validity,
            "validity",
            allowed=ALLOWED_TICK_VALIDITY,
        )
        if self.best_ask > 0.0 and self.best_bid > 0.0:
            _require(self.best_ask >= self.best_bid, "best_ask must be >= best_bid")


@dataclass(frozen=True, slots=True)
class SnapshotFrame(SchemaBase):
    frame_id: str
    selection_version: str
    ts_frame_ns: int
    ts_min_member_ns: int
    ts_max_member_ns: int
    ts_span_ms: int
    validity: str
    validity_reason: str | None = None
    sync_ok: bool = False
    stale_mask: tuple[str, ...] = ()
    future: SnapshotMember | None = None
    ce_atm: SnapshotMember | None = None
    ce_atm1: SnapshotMember | None = None
    pe_atm: SnapshotMember | None = None
    pe_atm1: SnapshotMember | None = None

    _TYPE: ClassVar[str] = "snapshot_frame"

    def validate(self) -> None:
        _require_non_empty_str(self.frame_id, "frame_id")
        _require_non_empty_str(self.selection_version, "selection_version")
        _require_int(self.ts_frame_ns, "ts_frame_ns", min_value=0)
        _require_int(self.ts_min_member_ns, "ts_min_member_ns", min_value=0)
        _require_int(self.ts_max_member_ns, "ts_max_member_ns", min_value=0)
        _require_int(self.ts_span_ms, "ts_span_ms", min_value=0)
        _require_literal(
            self.validity,
            "validity",
            allowed=ALLOWED_SNAPSHOT_VALIDITY,
        )
        if self.validity_reason is not None:
            _optional_non_empty_str(self.validity_reason, "validity_reason")
        _require_bool(self.sync_ok, "sync_ok")
        object.__setattr__(self, "stale_mask", _require_str_sequence(self.stale_mask, "stale_mask"))
        _require(
            self.ts_max_member_ns >= self.ts_min_member_ns,
            "ts_max_member_ns must be >= ts_min_member_ns",
        )


# ============================================================================
# Feature / signal models
# ============================================================================


@dataclass(frozen=True, slots=True)
class EconomicViability(SchemaBase):
    is_viable: bool
    spread_bps: float | None = None
    spread_rupees: float | None = None
    expected_slippage_rupees: float | None = None
    expected_total_cost_rupees: float | None = None
    blocker_code: str | None = None
    blocker_message: str | None = None

    _TYPE: ClassVar[str] = "economic_viability"

    def validate(self) -> None:
        _require_bool(self.is_viable, "is_viable")
        if self.spread_bps is not None:
            _require_float(self.spread_bps, "spread_bps", min_value=0.0)
        if self.spread_rupees is not None:
            _require_float(self.spread_rupees, "spread_rupees", min_value=0.0)
        if self.expected_slippage_rupees is not None:
            _require_float(
                self.expected_slippage_rupees,
                "expected_slippage_rupees",
                min_value=0.0,
            )
        if self.expected_total_cost_rupees is not None:
            _require_float(
                self.expected_total_cost_rupees,
                "expected_total_cost_rupees",
                min_value=0.0,
            )
        if self.blocker_code is not None:
            _optional_non_empty_str(self.blocker_code, "blocker_code")
        if self.blocker_message is not None:
            _optional_non_empty_str(self.blocker_message, "blocker_message")


@dataclass(frozen=True, slots=True)
class FourPillarSignal(SchemaBase):
    futures_bias: float
    futures_impulse: float
    options_confirmation: bool
    options_side: str | None = None
    liquidity_ok: bool = True
    alignment_ok: bool = True

    _TYPE: ClassVar[str] = "four_pillar_signal"

    def validate(self) -> None:
        _require_float(self.futures_bias, "futures_bias")
        _require_float(self.futures_impulse, "futures_impulse")
        _require_bool(self.options_confirmation, "options_confirmation")
        _require_bool(self.liquidity_ok, "liquidity_ok")
        _require_bool(self.alignment_ok, "alignment_ok")
        if self.options_side is not None:
            _require_literal(
                self.options_side,
                "options_side",
                allowed=ALLOWED_OPTION_SIDES,
            )


@dataclass(frozen=True, slots=True)
class DeltaProxyNormalization(SchemaBase):
    option_side: str
    strike: float
    delta_proxy: float
    normalized_signal_strength: float | None = None

    _TYPE: ClassVar[str] = "delta_proxy_normalization"

    def validate(self) -> None:
        _require_literal(
            self.option_side,
            "option_side",
            allowed=ALLOWED_OPTION_SIDES,
        )
        _require_float(self.strike, "strike", min_value=0.0)
        _require_float(self.delta_proxy, "delta_proxy")
        if self.normalized_signal_strength is not None:
            _require_float(
                self.normalized_signal_strength,
                "normalized_signal_strength",
            )


@dataclass(frozen=True, slots=True)
class MistTrendSurface(SchemaBase):
    pullback_depth_pct: float | None = None
    micro_trap_flag: bool = False
    resume_override_pass: bool = False
    fut_ladder_accel_call: bool = False
    fut_ladder_accel_put: bool = False
    fut_ofi_ratio_5s: float | None = None
    fut_ofi_ratio_60s: float | None = None

    _TYPE: ClassVar[str] = "mist_trend_surface"

    def validate(self) -> None:
        if self.pullback_depth_pct is not None:
            _require_float(self.pullback_depth_pct, "pullback_depth_pct", min_value=0.0)
        _require_bool(self.micro_trap_flag, "micro_trap_flag")
        _require_bool(self.resume_override_pass, "resume_override_pass")
        _require_bool(self.fut_ladder_accel_call, "fut_ladder_accel_call")
        _require_bool(self.fut_ladder_accel_put, "fut_ladder_accel_put")
        if self.fut_ofi_ratio_5s is not None:
            _require_float(self.fut_ofi_ratio_5s, "fut_ofi_ratio_5s", min_value=0.0)
        if self.fut_ofi_ratio_60s is not None:
            _require_float(self.fut_ofi_ratio_60s, "fut_ofi_ratio_60s", min_value=0.0)


@dataclass(frozen=True, slots=True)
class MisbBreakoutSurface(SchemaBase):
    breakout_shelf_high: float | None = None
    breakout_shelf_low: float | None = None
    breakout_shelf_mid: float | None = None
    breakout_shelf_width_pct: float | None = None
    breakout_shelf_valid: bool = False
    breakout_ref_high: float | None = None
    breakout_ref_low: float | None = None
    breakout_pretrigger_ok_call: bool = False
    breakout_pretrigger_ok_put: bool = False
    breakout_trigger_call: bool = False
    breakout_trigger_put: bool = False
    breakout_acceptance_call: bool = False
    breakout_acceptance_put: bool = False
    fut_ladder_accel_call: bool = False
    fut_ladder_accel_put: bool = False
    ce_delta_3: float | None = None
    pe_delta_3: float | None = None
    ce_response_eff: float | None = None
    pe_response_eff: float | None = None
    ce_spread_ratio: float | None = None
    pe_spread_ratio: float | None = None
    ce_depth_total: int | None = None
    pe_depth_total: int | None = None
    impact_depth_fraction_call: float | None = None
    impact_depth_fraction_put: float | None = None
    context_pass_call: bool = False
    context_pass_put: bool = False
    tradability_pass_call: bool = False
    tradability_pass_put: bool = False

    _TYPE: ClassVar[str] = "misb_breakout_surface"

    def validate(self) -> None:
        for field_name in (
            "breakout_shelf_high",
            "breakout_shelf_low",
            "breakout_shelf_mid",
            "breakout_shelf_width_pct",
            "breakout_ref_high",
            "breakout_ref_low",
            "ce_delta_3",
            "pe_delta_3",
            "ce_response_eff",
            "pe_response_eff",
            "ce_spread_ratio",
            "pe_spread_ratio",
            "impact_depth_fraction_call",
            "impact_depth_fraction_put",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name)
        for field_name in ("ce_depth_total", "pe_depth_total"):
            value = getattr(self, field_name)
            if value is not None:
                _require_int(value, field_name, min_value=0)
        for field_name in (
            "breakout_shelf_valid",
            "breakout_pretrigger_ok_call",
            "breakout_pretrigger_ok_put",
            "breakout_trigger_call",
            "breakout_trigger_put",
            "breakout_acceptance_call",
            "breakout_acceptance_put",
            "fut_ladder_accel_call",
            "fut_ladder_accel_put",
            "context_pass_call",
            "context_pass_put",
            "tradability_pass_call",
            "tradability_pass_put",
        ):
            _require_bool(getattr(self, field_name), field_name)
        if self.breakout_shelf_high is not None and self.breakout_shelf_low is not None:
            _require(
                self.breakout_shelf_high >= self.breakout_shelf_low,
                "breakout_shelf_high must be >= breakout_shelf_low",
            )


@dataclass(frozen=True, slots=True)
class MiscCompressionRetestSurface(SchemaBase):
    compression_high: float | None = None
    compression_low: float | None = None
    compression_width_pct: float | None = None
    compression_valid: bool = False
    breakout_extension_pct: float | None = None
    retest_low: float | None = None
    retest_high: float | None = None
    retest_volume_ratio: float | None = None
    hesitation_duration_sec: float | None = None
    retest_type: str = RetestType.NONE
    resume_confirmation_pass: bool = False

    _TYPE: ClassVar[str] = "misc_compression_retest_surface"

    def validate(self) -> None:
        for field_name in (
            "compression_high",
            "compression_low",
            "compression_width_pct",
            "breakout_extension_pct",
            "retest_low",
            "retest_high",
            "retest_volume_ratio",
            "hesitation_duration_sec",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name, min_value=0.0)
        _require_bool(self.compression_valid, "compression_valid")
        _require_literal(
            self.retest_type,
            "retest_type",
            allowed=ALLOWED_RETEST_TYPES,
        )
        _require_bool(self.resume_confirmation_pass, "resume_confirmation_pass")
        if self.compression_high is not None and self.compression_low is not None:
            _require(
                self.compression_high >= self.compression_low,
                "compression_high must be >= compression_low",
            )
        if self.retest_high is not None and self.retest_low is not None:
            _require(
                self.retest_high >= self.retest_low,
                "retest_high must be >= retest_low",
            )


@dataclass(frozen=True, slots=True)
class MisrTrapSurface(SchemaBase):
    active_zone_id: str | None = None
    zone_type: str | None = None
    trap_zone_level: float | None = None
    trap_event_id: str | None = None
    fake_break_extreme: float | None = None
    break_efficiency_ratio: float | None = None
    ladder_absorption_score: float | None = None
    range_reentry_ts_ns: int | None = None
    reclaim_volume_ratio: float | None = None
    hold_inside_range_proof_pass: bool = False
    no_mans_land_displacement_pass: bool = False
    flow_flip_confirmation_pass: bool = False
    reversal_impulse_confirmation_pass: bool = False

    _TYPE: ClassVar[str] = "misr_trap_surface"

    def validate(self) -> None:
        for field_name in ("active_zone_id", "zone_type", "trap_event_id"):
            value = getattr(self, field_name)
            if value is not None:
                _optional_non_empty_str(value, field_name)
        for field_name in (
            "trap_zone_level",
            "fake_break_extreme",
            "break_efficiency_ratio",
            "ladder_absorption_score",
            "reclaim_volume_ratio",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name)
        if self.range_reentry_ts_ns is not None:
            _require_int(self.range_reentry_ts_ns, "range_reentry_ts_ns", min_value=0)
        for field_name in (
            "hold_inside_range_proof_pass",
            "no_mans_land_displacement_pass",
            "flow_flip_confirmation_pass",
            "reversal_impulse_confirmation_pass",
        ):
            _require_bool(getattr(self, field_name), field_name)


@dataclass(frozen=True, slots=True)
class MisoMicrostructureSurface(SchemaBase):
    burst_event_id: str | None = None
    opt_aggr_buy_qty_window: int = 0
    opt_aggr_sell_qty_window: int = 0
    call_flow_ratio: float | None = None
    put_flow_ratio: float | None = None
    call_tape_speed: float | None = None
    put_tape_speed: float | None = None
    opt_book_imbalance: float | None = None
    ask_reload_veto: bool = False
    bid_reload_veto: bool = False
    shadow_call_support_pass: bool = False
    shadow_put_support_pass: bool = False
    imbalance_persistence_pass: bool = False
    futures_veto_pass: bool = False
    vwap_gate_pass: bool = False
    opt_touch_depth: int | None = None
    fut_touch_depth: int | None = None

    _TYPE: ClassVar[str] = "miso_microstructure_surface"

    def validate(self) -> None:
        if self.burst_event_id is not None:
            _optional_non_empty_str(self.burst_event_id, "burst_event_id")
        _require_int(self.opt_aggr_buy_qty_window, "opt_aggr_buy_qty_window", min_value=0)
        _require_int(self.opt_aggr_sell_qty_window, "opt_aggr_sell_qty_window", min_value=0)
        for field_name in ("call_flow_ratio", "put_flow_ratio", "call_tape_speed", "put_tape_speed"):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name, min_value=0.0)
        if self.opt_book_imbalance is not None:
            _require_float(self.opt_book_imbalance, "opt_book_imbalance", min_value=0.0)
            _require(self.opt_book_imbalance <= 1.0, "opt_book_imbalance must be <= 1.0")
        for field_name in (
            "ask_reload_veto",
            "bid_reload_veto",
            "shadow_call_support_pass",
            "shadow_put_support_pass",
            "imbalance_persistence_pass",
            "futures_veto_pass",
            "vwap_gate_pass",
        ):
            _require_bool(getattr(self, field_name), field_name)
        if self.opt_touch_depth is not None:
            _require_int(self.opt_touch_depth, "opt_touch_depth", min_value=0)
        if self.fut_touch_depth is not None:
            _require_int(self.fut_touch_depth, "fut_touch_depth", min_value=0)


@dataclass(frozen=True, slots=True)
class FeatureFrame(SchemaBase):
    ts_event_ns: int
    instrument_key: str
    system_state: str
    strategy_mode: str
    frame_valid: bool
    warmup_complete: bool
    futures_snapshot: FuturesSnapshot
    strategy_family_id: str | None = None
    doctrine_id: str | None = None
    branch_id: str | None = None
    strategy_runtime_mode: str | None = None
    family_runtime_mode: str | None = None
    active_futures_provider_id: str | None = None
    active_selected_option_provider_id: str | None = None
    active_option_context_provider_id: str | None = None
    current_regime: str | None = None
    snapshot_frame: SnapshotFrame | None = None
    economic_viability: EconomicViability | None = None
    four_pillar: FourPillarSignal | None = None
    delta_proxy_normalization: DeltaProxyNormalization | None = None
    mist_trend: MistTrendSurface | None = None
    misb_breakout: MisbBreakoutSurface | None = None
    misc_compression_retest: MiscCompressionRetestSurface | None = None
    misr_trap: MisrTrapSurface | None = None
    miso_microstructure: MisoMicrostructureSurface | None = None
    entry_mode_hint: str | None = None
    explain: str | None = None
    tags: tuple[str, ...] = ()

    _TYPE: ClassVar[str] = "feature_frame"

    def validate(self) -> None:
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_literal(
            self.system_state,
            "system_state",
            allowed=ALLOWED_SYSTEM_STATES,
        )
        _require_literal(
            self.strategy_mode,
            "strategy_mode",
            allowed=ALLOWED_STRATEGY_MODES,
        )
        _require_bool(self.frame_valid, "frame_valid")
        _require_bool(self.warmup_complete, "warmup_complete")
        _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)
        if self.branch_id is not None:
            _require_literal(
                self.branch_id,
                "branch_id",
                allowed=ALLOWED_BRANCH_IDS,
            )
        if self.strategy_runtime_mode is not None:
            _validate_strategy_runtime_mode_for_family(
                self.strategy_family_id,
                self.strategy_runtime_mode,
                field_name="strategy_runtime_mode",
            )
        if self.family_runtime_mode is not None:
            _require_literal(
                self.family_runtime_mode,
                "family_runtime_mode",
                allowed=ALLOWED_FAMILY_RUNTIME_MODES,
            )
        if self.active_futures_provider_id is not None:
            _require_literal(
                self.active_futures_provider_id,
                "active_futures_provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.active_selected_option_provider_id is not None:
            _require_literal(
                self.active_selected_option_provider_id,
                "active_selected_option_provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.active_option_context_provider_id is not None:
            _require_literal(
                self.active_option_context_provider_id,
                "active_option_context_provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.current_regime is not None:
            _require_literal(
                self.current_regime,
                "current_regime",
                allowed=ALLOWED_STRATEGY_REGIMES,
            )
        if self.entry_mode_hint is not None:
            _require_literal(
                self.entry_mode_hint,
                "entry_mode_hint",
                allowed=ALLOWED_ENTRY_MODES,
            )
        if self.explain is not None:
            _optional_non_empty_str(self.explain, "explain")
        object.__setattr__(self, "tags", _require_str_sequence(self.tags, "tags"))

        if self.mist_trend is not None:
            _require(
                self.strategy_family_id in (None, names.STRATEGY_FAMILY_MIST),
                "mist_trend surface is valid only for MIST or unspecified family",
            )
        if self.misb_breakout is not None:
            _require(
                self.strategy_family_id in (None, names.STRATEGY_FAMILY_MISB),
                "misb_breakout surface is valid only for MISB or unspecified family",
            )
        if self.misc_compression_retest is not None:
            _require(
                self.strategy_family_id in (None, names.STRATEGY_FAMILY_MISC),
                "misc_compression_retest surface is valid only for MISC or unspecified family",
            )
        if self.misr_trap is not None:
            _require(
                self.strategy_family_id in (None, names.STRATEGY_FAMILY_MISR),
                "misr_trap surface is valid only for MISR or unspecified family",
            )
        if self.miso_microstructure is not None:
            _require(
                self.strategy_family_id in (None, names.STRATEGY_FAMILY_MISO),
                "miso_microstructure surface is valid only for MISO or unspecified family",
            )


@dataclass(frozen=True, slots=True)
class StopPlan(SchemaBase):
    stop_price: float | None = None
    stop_points: float | None = None
    time_stop_seconds: int | None = None
    adverse_exit_seconds: int | None = None

    _TYPE: ClassVar[str] = "stop_plan"

    def validate(self) -> None:
        if self.stop_price is not None:
            _require_float(self.stop_price, "stop_price", min_value=0.0)
        if self.stop_points is not None:
            _require_float(self.stop_points, "stop_points", min_value=0.0)
        if self.time_stop_seconds is not None:
            _require_int(self.time_stop_seconds, "time_stop_seconds", min_value=0)
        if self.adverse_exit_seconds is not None:
            _require_int(
                self.adverse_exit_seconds,
                "adverse_exit_seconds",
                min_value=0,
            )


@dataclass(frozen=True, slots=True)
class TargetPlan(SchemaBase):
    target_price: float | None = None
    target_points: float | None = None
    trail_after_points: float | None = None
    trail_step_points: float | None = None

    _TYPE: ClassVar[str] = "target_plan"

    def validate(self) -> None:
        if self.target_price is not None:
            _require_float(self.target_price, "target_price", min_value=0.0)
        if self.target_points is not None:
            _require_float(self.target_points, "target_points", min_value=0.0)
        if self.trail_after_points is not None:
            _require_float(
                self.trail_after_points,
                "trail_after_points",
                min_value=0.0,
            )
        if self.trail_step_points is not None:
            _require_float(
                self.trail_step_points,
                "trail_step_points",
                min_value=0.0,
            )



@dataclass(frozen=True, slots=True)
class StrategyDecision(SchemaBase):
    decision_id: str
    ts_event_ns: int
    ts_expiry_ns: int | None
    action: str
    side: str
    position_effect: str
    quantity_lots: int
    instrument_key: str | None = None
    strategy_family_id: str | None = None
    doctrine_id: str | None = None
    branch_id: str | None = None
    family_runtime_mode: str | None = None
    strategy_runtime_mode: str | None = None
    source_event_id: str | None = None
    trap_event_id: str | None = None
    burst_event_id: str | None = None
    active_futures_provider_id: str | None = None
    active_selected_option_provider_id: str | None = None
    active_option_context_provider_id: str | None = None
    entry_mode: str = names.ENTRY_MODE_UNKNOWN
    strategy_mode: str = names.STRATEGY_AUTO
    system_state: str = names.STATE_IDLE
    explain: str | None = None
    blocker_code: str | None = None
    blocker_message: str | None = None
    stop_plan: StopPlan | None = None
    target_plan: TargetPlan | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    _TYPE: ClassVar[str] = "strategy_decision"

    def validate(self) -> None:
        _require_non_empty_str(self.decision_id, "decision_id")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        if self.ts_expiry_ns is not None:
            _require_int(self.ts_expiry_ns, "ts_expiry_ns", min_value=0)
            _require(
                self.ts_expiry_ns >= self.ts_event_ns,
                "ts_expiry_ns must be >= ts_event_ns",
            )

        _require_literal(self.action, "action", allowed=ALLOWED_ACTIONS)
        _require_literal(self.side, "side", allowed=ALLOWED_OPTION_SIDES)
        _require_literal(
            self.position_effect,
            "position_effect",
            allowed=ALLOWED_POSITION_EFFECTS,
        )
        _require_int(self.quantity_lots, "quantity_lots", min_value=0)
        _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)
        _validate_branch_side_pair(self.branch_id, self.side)

        if self.family_runtime_mode is not None:
            _require_literal(
                self.family_runtime_mode,
                "family_runtime_mode",
                allowed=ALLOWED_FAMILY_RUNTIME_MODES,
            )
        if self.strategy_runtime_mode is not None:
            _validate_strategy_runtime_mode_for_family(
                self.strategy_family_id,
                self.strategy_runtime_mode,
                field_name="strategy_runtime_mode",
            )
        for field_name in (
            "source_event_id",
            "trap_event_id",
            "burst_event_id",
            "instrument_key",
            "explain",
            "blocker_code",
            "blocker_message",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _optional_non_empty_str(value, field_name)
        for field_name in (
            "active_futures_provider_id",
            "active_selected_option_provider_id",
            "active_option_context_provider_id",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_literal(
                    value,
                    field_name,
                    allowed=ALLOWED_PROVIDER_IDS,
                )
        _require_literal(
            self.entry_mode,
            "entry_mode",
            allowed=ALLOWED_ENTRY_MODES,
        )
        _require_literal(
            self.strategy_mode,
            "strategy_mode",
            allowed=ALLOWED_STRATEGY_MODES,
        )
        _require_literal(
            self.system_state,
            "system_state",
            allowed=ALLOWED_SYSTEM_STATES,
        )

        metadata = _require_mapping(self.metadata, "metadata")
        metadata = {str(k): _plain_value(v) for k, v in metadata.items()}
        object.__setattr__(self, "metadata", metadata)

        if self.action in (names.ACTION_ENTER_CALL, names.ACTION_ENTER_PUT):
            _require(
                self.position_effect == names.POSITION_EFFECT_OPEN,
                "entry actions require position_effect OPEN",
            )
            _require(
                self.quantity_lots > 0,
                "entry actions require quantity_lots > 0",
            )
            _require(
                bool(self.instrument_key),
                "entry actions require non-empty instrument_key",
            )
            expected_branch = names.BRANCH_CALL if self.action == names.ACTION_ENTER_CALL else names.BRANCH_PUT
            _require(
                self.side == expected_branch,
                "entry action side must match CALL/PUT action",
            )
            if self.branch_id is not None:
                _require(
                    self.branch_id == expected_branch,
                    "branch_id must match CALL/PUT entry action",
                )

        if self.action == names.ACTION_EXIT:
            _require(
                self.position_effect in (
                    names.POSITION_EFFECT_CLOSE,
                    names.POSITION_EFFECT_REDUCE,
                    names.POSITION_EFFECT_FLATTEN,
                ),
                "EXIT requires CLOSE / REDUCE / FLATTEN position_effect",
            )

        if self.action in (names.ACTION_HOLD, names.ACTION_BLOCK):
            _require(
                self.position_effect == names.POSITION_EFFECT_NONE,
                "HOLD/BLOCK require position_effect NONE",
            )


@dataclass(frozen=True, slots=True)
class OperatorCommand(SchemaBase):
    """
    Canonical operator/runtime command payload for STREAM_CMD_MME.
    """

    command_type: str
    ts_event_ns: int
    producer: str
    correlation_id: str | None = None
    mode: str | None = None
    reason: str | None = None
    params: Mapping[str, Any] = field(default_factory=dict)

    _TYPE: ClassVar[str] = "operator_command"

    def validate(self) -> None:
        _require_literal(
            self.command_type,
            "command_type",
            allowed=ALLOWED_COMMAND_TYPES,
        )
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.producer, "producer")

        if self.correlation_id is not None:
            _optional_non_empty_str(self.correlation_id, "correlation_id")
        if self.mode is not None:
            _require_literal(
                self.mode,
                "mode",
                allowed=ALLOWED_OPERATOR_MODE_VALUES,
            )
        if self.reason is not None:
            _optional_non_empty_str(self.reason, "reason")

        params = _require_mapping(self.params, "params")
        params = {str(k): _plain_value(v) for k, v in params.items()}
        object.__setattr__(self, "params", params)

        if self.command_type == names.CMD_SET_MODE:
            _require(
                self.mode is not None and self.mode.strip() != "",
                "CMD_SET_MODE requires non-empty mode",
            )

@dataclass(frozen=True, slots=True)
class DecisionAck(SchemaBase):
    decision_id: str
    ack_type: str
    ts_event_ns: int
    service: str
    message: str | None = None
    order_id: str | None = None
    trade_id: str | None = None
    entry_mode: str | None = None

    _TYPE: ClassVar[str] = "decision_ack"

    def validate(self) -> None:
        _require_non_empty_str(self.decision_id, "decision_id")
        _require_literal(
            self.ack_type,
            "ack_type",
            allowed=ALLOWED_ACK_TYPES,
        )
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.service, "service")
        if self.message is not None:
            _optional_non_empty_str(self.message, "message")
        if self.order_id is not None:
            _optional_non_empty_str(self.order_id, "order_id")
        if self.trade_id is not None:
            _optional_non_empty_str(self.trade_id, "trade_id")
        if self.entry_mode is not None:
            _require_literal(
                self.entry_mode,
                "entry_mode",
                allowed=ALLOWED_ENTRY_MODES,
            )


@dataclass(frozen=True, slots=True)
class OrderIntent(SchemaBase):
    order_id: str
    decision_id: str
    ts_event_ns: int
    instrument_key: str
    side: str
    quantity_lots: int
    order_type: str
    entry_mode: str = names.ENTRY_MODE_UNKNOWN
    price: float | None = None
    stop_price: float | None = None
    tif: str | None = None
    broker_order_id: str | None = None

    _TYPE: ClassVar[str] = "order_intent"

    def validate(self) -> None:
        _require_non_empty_str(self.order_id, "order_id")
        _require_non_empty_str(self.decision_id, "decision_id")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_literal(self.side, "side", allowed=ALLOWED_OPTION_SIDES)
        _require_int(self.quantity_lots, "quantity_lots", min_value=1)
        _require_non_empty_str(self.order_type, "order_type")
        _require_literal(
            self.entry_mode,
            "entry_mode",
            allowed=ALLOWED_ENTRY_MODES,
        )
        if self.price is not None:
            _require_float(self.price, "price", min_value=0.0)
        if self.stop_price is not None:
            _require_float(self.stop_price, "stop_price", min_value=0.0)
        if self.tif is not None:
            _optional_non_empty_str(self.tif, "tif")
        if self.broker_order_id is not None:
            _optional_non_empty_str(self.broker_order_id, "broker_order_id")


@dataclass(frozen=True, slots=True)
class PendingOrderState(SchemaBase):
    order_id: str
    decision_id: str
    ts_event_ns: int
    instrument_key: str
    side: str
    quantity_lots: int
    entry_mode: str
    order_type: str
    broker_order_id: str | None = None
    broker_status: str | None = None
    price: float | None = None
    stop_price: float | None = None

    _TYPE: ClassVar[str] = "pending_order_state"

    def validate(self) -> None:
        _require_non_empty_str(self.order_id, "order_id")
        _require_non_empty_str(self.decision_id, "decision_id")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_literal(self.side, "side", allowed=ALLOWED_OPTION_SIDES)
        _require_int(self.quantity_lots, "quantity_lots", min_value=1)
        _require_literal(
            self.entry_mode,
            "entry_mode",
            allowed=ALLOWED_ENTRY_MODES,
        )
        _require_non_empty_str(self.order_type, "order_type")
        if self.broker_order_id is not None:
            _optional_non_empty_str(self.broker_order_id, "broker_order_id")
        if self.broker_status is not None:
            _optional_non_empty_str(self.broker_status, "broker_status")
        if self.price is not None:
            _require_float(self.price, "price", min_value=0.0)
        if self.stop_price is not None:
            _require_float(self.stop_price, "stop_price", min_value=0.0)


@dataclass(frozen=True, slots=True)
class TradeFill(SchemaBase):
    trade_id: str
    order_id: str
    decision_id: str | None
    ts_event_ns: int
    instrument_key: str
    side: str
    quantity_lots: int
    fill_price: float
    entry_mode: str
    position_effect: str
    exit_reason: str | None = None
    realized_pnl_rupees: float | None = None

    _TYPE: ClassVar[str] = "trade_fill"

    def validate(self) -> None:
        _require_non_empty_str(self.trade_id, "trade_id")
        _require_non_empty_str(self.order_id, "order_id")
        if self.decision_id is not None:
            _optional_non_empty_str(self.decision_id, "decision_id")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_literal(self.side, "side", allowed=ALLOWED_OPTION_SIDES)
        _require_int(self.quantity_lots, "quantity_lots", min_value=1)
        _require_float(self.fill_price, "fill_price", min_value=0.0)
        _require_literal(
            self.entry_mode,
            "entry_mode",
            allowed=ALLOWED_ENTRY_MODES,
        )
        _require_literal(
            self.position_effect,
            "position_effect",
            allowed=ALLOWED_POSITION_EFFECTS,
        )
        if self.exit_reason is not None:
            _optional_non_empty_str(self.exit_reason, "exit_reason")
        if self.realized_pnl_rupees is not None:
            _require_float(self.realized_pnl_rupees, "realized_pnl_rupees")


@dataclass(frozen=True, slots=True)
class TradeLedgerRow(SchemaBase):
    trade_id: str
    order_id: str
    decision_id: str | None
    ts_event_ns: int
    instrument_key: str
    side: str
    quantity_lots: int
    entry_mode: str
    position_effect: str
    fill_price: float
    realized_pnl_rupees: float | None = None
    exit_reason: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    _TYPE: ClassVar[str] = "trade_ledger_row"

    def validate(self) -> None:
        _require_non_empty_str(self.trade_id, "trade_id")
        _require_non_empty_str(self.order_id, "order_id")
        if self.decision_id is not None:
            _optional_non_empty_str(self.decision_id, "decision_id")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_literal(self.side, "side", allowed=ALLOWED_OPTION_SIDES)
        _require_int(self.quantity_lots, "quantity_lots", min_value=1)
        _require_literal(
            self.entry_mode,
            "entry_mode",
            allowed=ALLOWED_ENTRY_MODES,
        )
        _require_literal(
            self.position_effect,
            "position_effect",
            allowed=ALLOWED_POSITION_EFFECTS,
        )
        _require_float(self.fill_price, "fill_price", min_value=0.0)
        if self.realized_pnl_rupees is not None:
            _require_float(self.realized_pnl_rupees, "realized_pnl_rupees")
        if self.exit_reason is not None:
            _optional_non_empty_str(self.exit_reason, "exit_reason")
        metadata = _require_mapping(self.metadata, "metadata")
        metadata = {str(k): _plain_value(v) for k, v in metadata.items()}
        object.__setattr__(self, "metadata", metadata)



@dataclass(frozen=True, slots=True)
class FuturesSnapshotState(SchemaBase):
    instrument_key: str
    ts_event_ns: int
    provider_id: str | None = None
    provider_role: str | None = None
    instrument_token: str | None = None
    trading_symbol: str | None = None
    seq_no: int | None = None
    ltp: float = 0.0
    last_qty: int | None = None
    volume: int | None = None
    oi: int | None = None
    bid: float | None = None
    ask: float | None = None
    bid_qty: int | None = None
    ask_qty: int | None = None
    bid_qty_5: int | None = None
    ask_qty_5: int | None = None
    tick_validity: str = TickValidity.OK
    last_update_ns: int = 0
    is_active_provider_snapshot: bool = False

    _TYPE: ClassVar[str] = "futures_snapshot_state"

    def validate(self) -> None:
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        if self.provider_id is not None:
            _require_literal(self.provider_id, "provider_id", allowed=ALLOWED_PROVIDER_IDS)
        if self.provider_role is not None:
            _require_literal(
                self.provider_role,
                "provider_role",
                allowed=ALLOWED_PROVIDER_ROLES,
            )
        if self.instrument_token is not None:
            _optional_non_empty_str(self.instrument_token, "instrument_token")
        if self.trading_symbol is not None:
            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
        if self.seq_no is not None:
            _require_int(self.seq_no, "seq_no", min_value=0)
        _require_float(self.ltp, "ltp", min_value=0.0)
        if self.last_qty is not None:
            _require_int(self.last_qty, "last_qty", min_value=0)
        if self.volume is not None:
            _require_int(self.volume, "volume", min_value=0)
        if self.oi is not None:
            _require_int(self.oi, "oi", min_value=0)
        if self.bid is not None:
            _require_float(self.bid, "bid", min_value=0.0)
        if self.ask is not None:
            _require_float(self.ask, "ask", min_value=0.0)
        if self.bid_qty is not None:
            _require_int(self.bid_qty, "bid_qty", min_value=0)
        if self.ask_qty is not None:
            _require_int(self.ask_qty, "ask_qty", min_value=0)
        if self.bid_qty_5 is not None:
            _require_int(self.bid_qty_5, "bid_qty_5", min_value=0)
        if self.ask_qty_5 is not None:
            _require_int(self.ask_qty_5, "ask_qty_5", min_value=0)
        _require_literal(self.tick_validity, "tick_validity", allowed=ALLOWED_TICK_VALIDITY)
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)
        _require_bool(self.is_active_provider_snapshot, "is_active_provider_snapshot")
        if self.bid is not None and self.ask is not None:
            _require(self.ask >= self.bid, "ask must be >= bid")


@dataclass(frozen=True, slots=True)
class OptionSnapshotState(SchemaBase):
    instrument_key: str
    ts_event_ns: int
    option_side: str
    strike: float
    expiry: str | None = None
    provider_id: str | None = None
    provider_role: str | None = None
    instrument_token: str | None = None
    trading_symbol: str | None = None
    seq_no: int | None = None
    ltp: float = 0.0
    last_qty: int | None = None
    volume: int | None = None
    oi: int | None = None
    bid: float | None = None
    ask: float | None = None
    bid_qty: int | None = None
    ask_qty: int | None = None
    bid_qty_5: int | None = None
    ask_qty_5: int | None = None
    delta_proxy: float | None = None
    tick_validity: str = TickValidity.OK
    last_update_ns: int = 0
    is_active_provider_snapshot: bool = False
    is_selected_option: bool = False

    _TYPE: ClassVar[str] = "option_snapshot_state"

    def validate(self) -> None:
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_literal(self.option_side, "option_side", allowed=ALLOWED_OPTION_SIDES)
        _require_float(self.strike, "strike", min_value=0.0)
        if self.expiry is not None:
            _optional_non_empty_str(self.expiry, "expiry")
        if self.provider_id is not None:
            _require_literal(self.provider_id, "provider_id", allowed=ALLOWED_PROVIDER_IDS)
        if self.provider_role is not None:
            _require_literal(
                self.provider_role,
                "provider_role",
                allowed=ALLOWED_PROVIDER_ROLES,
            )
        if self.instrument_token is not None:
            _optional_non_empty_str(self.instrument_token, "instrument_token")
        if self.trading_symbol is not None:
            _optional_non_empty_str(self.trading_symbol, "trading_symbol")
        if self.seq_no is not None:
            _require_int(self.seq_no, "seq_no", min_value=0)
        _require_float(self.ltp, "ltp", min_value=0.0)
        if self.last_qty is not None:
            _require_int(self.last_qty, "last_qty", min_value=0)
        if self.volume is not None:
            _require_int(self.volume, "volume", min_value=0)
        if self.oi is not None:
            _require_int(self.oi, "oi", min_value=0)
        if self.bid is not None:
            _require_float(self.bid, "bid", min_value=0.0)
        if self.ask is not None:
            _require_float(self.ask, "ask", min_value=0.0)
        if self.bid_qty is not None:
            _require_int(self.bid_qty, "bid_qty", min_value=0)
        if self.ask_qty is not None:
            _require_int(self.ask_qty, "ask_qty", min_value=0)
        if self.bid_qty_5 is not None:
            _require_int(self.bid_qty_5, "bid_qty_5", min_value=0)
        if self.ask_qty_5 is not None:
            _require_int(self.ask_qty_5, "ask_qty_5", min_value=0)
        if self.delta_proxy is not None:
            _require_float(self.delta_proxy, "delta_proxy")
        _require_literal(self.tick_validity, "tick_validity", allowed=ALLOWED_TICK_VALIDITY)
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)
        _require_bool(self.is_active_provider_snapshot, "is_active_provider_snapshot")
        _require_bool(self.is_selected_option, "is_selected_option")
        if self.bid is not None and self.ask is not None:
            _require(self.ask >= self.bid, "ask must be >= bid")


@dataclass(frozen=True, slots=True)
class DhanStrikeScoreComponents(SchemaBase):
    spread_score: float | None = None
    depth_score: float | None = None
    volume_score: float | None = None
    oi_score: float | None = None
    iv_score: float | None = None
    delta_score: float | None = None
    gamma_score: float | None = None
    iv_sanity_score: float | None = None

    _TYPE: ClassVar[str] = "dhan_strike_score_components"

    def validate(self) -> None:
        for field_name in (
            "spread_score",
            "depth_score",
            "volume_score",
            "oi_score",
            "iv_score",
            "delta_score",
            "gamma_score",
            "iv_sanity_score",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name, min_value=0.0)
                _require(value <= 1.0, f"{field_name} must be <= 1.0")


@dataclass(frozen=True, slots=True)
class DhanContextEvent(SchemaBase):
    ts_event_ns: int
    provider_id: str = names.PROVIDER_DHAN
    context_status: str = names.PROVIDER_STATUS_HEALTHY
    atm_strike: float | None = None
    selected_call_instrument_key: str | None = None
    selected_put_instrument_key: str | None = None
    selected_call_score: float | None = None
    selected_put_score: float | None = None
    selected_call_delta: float | None = None
    selected_put_delta: float | None = None
    selected_call_authoritative_delta: float | None = None
    selected_put_authoritative_delta: float | None = None
    selected_call_gamma: float | None = None
    selected_put_gamma: float | None = None
    selected_call_theta: float | None = None
    selected_put_theta: float | None = None
    selected_call_vega: float | None = None
    selected_put_vega: float | None = None
    selected_call_iv: float | None = None
    selected_put_iv: float | None = None
    selected_call_iv_change_1m_pct: float | None = None
    selected_put_iv_change_1m_pct: float | None = None
    selected_call_oi: int | None = None
    selected_put_oi: int | None = None
    selected_call_oi_change: int | None = None
    selected_put_oi_change: int | None = None
    selected_call_volume: int | None = None
    selected_put_volume: int | None = None
    selected_call_cross_strike_spread_rank: float | None = None
    selected_put_cross_strike_spread_rank: float | None = None
    selected_call_cross_strike_volume_rank: float | None = None
    selected_put_cross_strike_volume_rank: float | None = None
    selected_call_score_components: DhanStrikeScoreComponents | None = None
    selected_put_score_components: DhanStrikeScoreComponents | None = None
    message: str | None = None

    _TYPE: ClassVar[str] = "dhan_context_event"

    def validate(self) -> None:
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_literal(self.provider_id, "provider_id", allowed=ALLOWED_PROVIDER_IDS)
        _require(
            self.provider_id == names.PROVIDER_DHAN,
            "DhanContextEvent.provider_id must be DHAN",
        )
        _require_literal(
            self.context_status,
            "context_status",
            allowed=ALLOWED_PROVIDER_STATUSES,
        )
        if self.atm_strike is not None:
            _require_float(self.atm_strike, "atm_strike", min_value=0.0)
        for field_name in ("selected_call_instrument_key", "selected_put_instrument_key", "message"):
            value = getattr(self, field_name)
            if value is not None:
                _optional_non_empty_str(value, field_name)
        for field_name in (
            "selected_call_score",
            "selected_put_score",
            "selected_call_delta",
            "selected_put_delta",
            "selected_call_authoritative_delta",
            "selected_put_authoritative_delta",
            "selected_call_gamma",
            "selected_put_gamma",
            "selected_call_theta",
            "selected_put_theta",
            "selected_call_vega",
            "selected_put_vega",
            "selected_call_iv",
            "selected_put_iv",
            "selected_call_iv_change_1m_pct",
            "selected_put_iv_change_1m_pct",
            "selected_call_cross_strike_spread_rank",
            "selected_put_cross_strike_spread_rank",
            "selected_call_cross_strike_volume_rank",
            "selected_put_cross_strike_volume_rank",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name)
        for field_name in (
            "selected_call_oi",
            "selected_put_oi",
            "selected_call_oi_change",
            "selected_put_oi_change",
            "selected_call_volume",
            "selected_put_volume",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_int(value, field_name, min_value=0)


@dataclass(frozen=True, slots=True)
class DhanContextState(SchemaBase):
    ts_event_ns: int
    provider_id: str = names.PROVIDER_DHAN
    context_status: str = names.PROVIDER_STATUS_HEALTHY
    atm_strike: float | None = None
    selected_call_instrument_key: str | None = None
    selected_put_instrument_key: str | None = None
    selected_call_score: float | None = None
    selected_put_score: float | None = None
    selected_call_delta: float | None = None
    selected_put_delta: float | None = None
    selected_call_authoritative_delta: float | None = None
    selected_put_authoritative_delta: float | None = None
    selected_call_gamma: float | None = None
    selected_put_gamma: float | None = None
    selected_call_theta: float | None = None
    selected_put_theta: float | None = None
    selected_call_vega: float | None = None
    selected_put_vega: float | None = None
    selected_call_iv: float | None = None
    selected_put_iv: float | None = None
    selected_call_iv_change_1m_pct: float | None = None
    selected_put_iv_change_1m_pct: float | None = None
    selected_call_oi: int | None = None
    selected_put_oi: int | None = None
    selected_call_oi_change: int | None = None
    selected_put_oi_change: int | None = None
    selected_call_volume: int | None = None
    selected_put_volume: int | None = None
    selected_call_cross_strike_spread_rank: float | None = None
    selected_put_cross_strike_spread_rank: float | None = None
    selected_call_cross_strike_volume_rank: float | None = None
    selected_put_cross_strike_volume_rank: float | None = None
    selected_call_spread_score: float | None = None
    selected_put_spread_score: float | None = None
    selected_call_depth_score: float | None = None
    selected_put_depth_score: float | None = None
    selected_call_volume_score: float | None = None
    selected_put_volume_score: float | None = None
    selected_call_oi_score: float | None = None
    selected_put_oi_score: float | None = None
    selected_call_iv_score: float | None = None
    selected_put_iv_score: float | None = None
    selected_call_delta_score: float | None = None
    selected_put_delta_score: float | None = None
    selected_call_gamma_score: float | None = None
    selected_put_gamma_score: float | None = None
    selected_call_iv_sanity_score: float | None = None
    selected_put_iv_sanity_score: float | None = None
    last_update_ns: int = 0
    message: str | None = None

    _TYPE: ClassVar[str] = "dhan_context_state"

    def validate(self) -> None:
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_literal(self.provider_id, "provider_id", allowed=ALLOWED_PROVIDER_IDS)
        _require(
            self.provider_id == names.PROVIDER_DHAN,
            "DhanContextState.provider_id must be DHAN",
        )
        _require_literal(
            self.context_status,
            "context_status",
            allowed=ALLOWED_PROVIDER_STATUSES,
        )
        if self.atm_strike is not None:
            _require_float(self.atm_strike, "atm_strike", min_value=0.0)
        for field_name in ("selected_call_instrument_key", "selected_put_instrument_key", "message"):
            value = getattr(self, field_name)
            if value is not None:
                _optional_non_empty_str(value, field_name)
        for field_name in (
            "selected_call_score",
            "selected_put_score",
            "selected_call_delta",
            "selected_put_delta",
            "selected_call_authoritative_delta",
            "selected_put_authoritative_delta",
            "selected_call_gamma",
            "selected_put_gamma",
            "selected_call_theta",
            "selected_put_theta",
            "selected_call_vega",
            "selected_put_vega",
            "selected_call_iv",
            "selected_put_iv",
            "selected_call_iv_change_1m_pct",
            "selected_put_iv_change_1m_pct",
            "selected_call_cross_strike_spread_rank",
            "selected_put_cross_strike_spread_rank",
            "selected_call_cross_strike_volume_rank",
            "selected_put_cross_strike_volume_rank",
            "selected_call_spread_score",
            "selected_put_spread_score",
            "selected_call_depth_score",
            "selected_put_depth_score",
            "selected_call_volume_score",
            "selected_put_volume_score",
            "selected_call_oi_score",
            "selected_put_oi_score",
            "selected_call_iv_score",
            "selected_put_iv_score",
            "selected_call_delta_score",
            "selected_put_delta_score",
            "selected_call_gamma_score",
            "selected_put_gamma_score",
            "selected_call_iv_sanity_score",
            "selected_put_iv_sanity_score",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name)
        for field_name in (
            "selected_call_oi",
            "selected_put_oi",
            "selected_call_oi_change",
            "selected_put_oi_change",
            "selected_call_volume",
            "selected_put_volume",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_int(value, field_name, min_value=0)
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)
@dataclass(frozen=True, slots=True)
class ProviderHealthState(SchemaBase):
    provider_id: str
    status: str
    role: str | None = None
    authenticated: bool | None = None
    stale: bool = False
    marketdata_healthy: bool | None = None
    execution_healthy: bool | None = None
    lag_ms: int | None = None
    last_update_ns: int = 0
    message: str | None = None

    _TYPE: ClassVar[str] = "provider_health_state"

    def validate(self) -> None:
        _require_literal(self.provider_id, "provider_id", allowed=ALLOWED_PROVIDER_IDS)
        _require_literal(self.status, "status", allowed=ALLOWED_PROVIDER_STATUSES)
        if self.role is not None:
            _require_literal(self.role, "role", allowed=ALLOWED_PROVIDER_ROLES)
        if self.authenticated is not None:
            _require_bool(self.authenticated, "authenticated")
        _require_bool(self.stale, "stale")
        if self.marketdata_healthy is not None:
            _require_bool(self.marketdata_healthy, "marketdata_healthy")
        if self.execution_healthy is not None:
            _require_bool(self.execution_healthy, "execution_healthy")
        if self.lag_ms is not None:
            _require_int(self.lag_ms, "lag_ms", min_value=0)
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)
        if self.message is not None:
            _optional_non_empty_str(self.message, "message")


@dataclass(frozen=True, slots=True)
class ProviderRuntimeState(SchemaBase):
    ts_event_ns: int
    futures_marketdata_provider_id: str
    selected_option_marketdata_provider_id: str
    option_context_provider_id: str
    execution_primary_provider_id: str
    execution_fallback_provider_id: str
    futures_marketdata_status: str = names.PROVIDER_STATUS_HEALTHY
    selected_option_marketdata_status: str = names.PROVIDER_STATUS_HEALTHY
    option_context_status: str = names.PROVIDER_STATUS_HEALTHY
    execution_primary_status: str = names.PROVIDER_STATUS_HEALTHY
    execution_fallback_status: str = names.PROVIDER_STATUS_HEALTHY
    family_runtime_mode: str = names.FAMILY_RUNTIME_MODE_OBSERVE_ONLY
    failover_mode: str = names.PROVIDER_FAILOVER_MODE_MANUAL
    override_mode: str = names.PROVIDER_OVERRIDE_MODE_AUTO
    transition_reason: str = names.PROVIDER_TRANSITION_REASON_BOOTSTRAP
    provider_transition_seq: int = 0
    failover_active: bool = False
    pending_failover: bool = False
    last_update_ns: int = 0
    message: str | None = None

    _TYPE: ClassVar[str] = "provider_runtime_state"

    def validate(self) -> None:
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        for field_name in (
            "futures_marketdata_provider_id",
            "selected_option_marketdata_provider_id",
            "option_context_provider_id",
            "execution_primary_provider_id",
            "execution_fallback_provider_id",
        ):
            _require_literal(
                getattr(self, field_name),
                field_name,
                allowed=ALLOWED_PROVIDER_IDS,
            )
        for field_name in (
            "futures_marketdata_status",
            "selected_option_marketdata_status",
            "option_context_status",
            "execution_primary_status",
            "execution_fallback_status",
        ):
            _require_literal(
                getattr(self, field_name),
                field_name,
                allowed=ALLOWED_PROVIDER_STATUSES,
            )
        _require_literal(
            self.family_runtime_mode,
            "family_runtime_mode",
            allowed=ALLOWED_FAMILY_RUNTIME_MODES,
        )
        _require_literal(
            self.failover_mode,
            "failover_mode",
            allowed=ALLOWED_PROVIDER_FAILOVER_MODES,
        )
        _require_literal(
            self.override_mode,
            "override_mode",
            allowed=ALLOWED_PROVIDER_OVERRIDE_MODES,
        )
        _require_literal(
            self.transition_reason,
            "transition_reason",
            allowed=ALLOWED_PROVIDER_TRANSITION_REASONS,
        )
        _require_int(
            self.provider_transition_seq,
            "provider_transition_seq",
            min_value=0,
        )
        _require_bool(self.failover_active, "failover_active")
        _require_bool(self.pending_failover, "pending_failover")
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)
        if self.message is not None:
            _optional_non_empty_str(self.message, "message")


@dataclass(frozen=True, slots=True)
class ProviderTransitionEvent(SchemaBase):
    ts_event_ns: int
    role: str
    to_provider_id: str
    reason: str
    from_provider_id: str | None = None
    previous_status: str | None = None
    new_status: str | None = None
    family_runtime_mode: str | None = None
    failover_mode: str | None = None
    override_mode: str | None = None
    message: str | None = None

    _TYPE: ClassVar[str] = "provider_transition_event"

    def validate(self) -> None:
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_literal(self.role, "role", allowed=ALLOWED_PROVIDER_ROLES)
        _require_literal(
            self.to_provider_id,
            "to_provider_id",
            allowed=ALLOWED_PROVIDER_IDS,
        )
        _require_literal(
            self.reason,
            "reason",
            allowed=ALLOWED_PROVIDER_TRANSITION_REASONS,
        )
        if self.from_provider_id is not None:
            _require_literal(
                self.from_provider_id,
                "from_provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.previous_status is not None:
            _require_literal(
                self.previous_status,
                "previous_status",
                allowed=ALLOWED_PROVIDER_STATUSES,
            )
        if self.new_status is not None:
            _require_literal(
                self.new_status,
                "new_status",
                allowed=ALLOWED_PROVIDER_STATUSES,
            )
        if self.family_runtime_mode is not None:
            _require_literal(
                self.family_runtime_mode,
                "family_runtime_mode",
                allowed=ALLOWED_FAMILY_RUNTIME_MODES,
            )
        if self.failover_mode is not None:
            _require_literal(
                self.failover_mode,
                "failover_mode",
                allowed=ALLOWED_PROVIDER_FAILOVER_MODES,
            )
        if self.override_mode is not None:
            _require_literal(
                self.override_mode,
                "override_mode",
                allowed=ALLOWED_PROVIDER_OVERRIDE_MODES,
            )
        if self.message is not None:
            _optional_non_empty_str(self.message, "message")


@dataclass(frozen=True, slots=True)
class RuntimeModeState(SchemaBase):
    family_runtime_mode: str
    strategy_runtime_mode: str | None = None
    strategy_family_id: str | None = None
    doctrine_id: str | None = None
    branch_id: str | None = None
    last_update_ns: int = 0
    message: str | None = None

    _TYPE: ClassVar[str] = "runtime_mode_state"

    def validate(self) -> None:
        _require_literal(
            self.family_runtime_mode,
            "family_runtime_mode",
            allowed=ALLOWED_FAMILY_RUNTIME_MODES,
        )
        _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)
        if self.branch_id is not None:
            _require_literal(self.branch_id, "branch_id", allowed=ALLOWED_BRANCH_IDS)
        if self.strategy_runtime_mode is not None:
            _validate_strategy_runtime_mode_for_family(
                self.strategy_family_id,
                self.strategy_runtime_mode,
                field_name="strategy_runtime_mode",
            )
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)
        if self.message is not None:
            _optional_non_empty_str(self.message, "message")


# ============================================================================
# Latest-state hash models
# These MUST remain flat for stable hash transport and restart safety.
# ============================================================================



@dataclass(frozen=True, slots=True)
class PositionState(SchemaBase):
    """
    Canonical flat position truth.

    This is the single shared position-state contract to be used by:
    - execution hash writes
    - strategy position reads
    - monitor reads
    - report reconstruction assistance
    """

    has_position: bool
    position_side: str
    instrument_key: str | None = None
    entry_option_symbol: str | None = None
    qty_lots: int = 0
    lot_size: int | None = None
    qty_units: int | None = None
    avg_price: float | None = None
    mark_price: float | None = None
    entry_ts_ns: int | None = None
    update_ts_ns: int = 0
    decision_id: str | None = None
    order_id: str | None = None
    trade_id: str | None = None
    entry_mode: str | None = None
    strategy_family_id: str | None = None
    doctrine_id: str | None = None
    branch_id: str | None = None
    realized_pnl_day: float = 0.0
    unrealized_pnl: float | None = None
    broker_position_id: str | None = None

    _TYPE: ClassVar[str] = "position_state"

    def validate(self) -> None:
        _require_bool(self.has_position, "has_position")
        _require_literal(
            self.position_side,
            "position_side",
            allowed=ALLOWED_POSITION_SIDES,
        )
        if self.instrument_key is not None:
            _optional_non_empty_str(self.instrument_key, "instrument_key")
        if self.entry_option_symbol is not None:
            _optional_non_empty_str(self.entry_option_symbol, "entry_option_symbol")
        _require_int(self.qty_lots, "qty_lots", min_value=0)
        if self.lot_size is not None:
            _require_int(self.lot_size, "lot_size", min_value=1)
        if self.qty_units is not None:
            _require_int(self.qty_units, "qty_units", min_value=0)
        if self.avg_price is not None:
            _require_float(self.avg_price, "avg_price", min_value=0.0)
        if self.mark_price is not None:
            _require_float(self.mark_price, "mark_price", min_value=0.0)
        if self.entry_ts_ns is not None:
            _require_int(self.entry_ts_ns, "entry_ts_ns", min_value=0)
        _require_int(self.update_ts_ns, "update_ts_ns", min_value=0)
        if self.decision_id is not None:
            _optional_non_empty_str(self.decision_id, "decision_id")
        if self.order_id is not None:
            _optional_non_empty_str(self.order_id, "order_id")
        if self.trade_id is not None:
            _optional_non_empty_str(self.trade_id, "trade_id")
        if self.entry_mode is not None:
            _require_literal(
                self.entry_mode,
                "entry_mode",
                allowed=ALLOWED_ENTRY_MODES,
            )
        _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)
        if self.branch_id is not None:
            _require_literal(self.branch_id, "branch_id", allowed=ALLOWED_BRANCH_IDS)
        _require_float(self.realized_pnl_day, "realized_pnl_day")
        if self.unrealized_pnl is not None:
            _require_float(self.unrealized_pnl, "unrealized_pnl")
        if self.broker_position_id is not None:
            _optional_non_empty_str(self.broker_position_id, "broker_position_id")

        if self.has_position:
            _require(
                self.position_side in (
                    names.POSITION_SIDE_LONG_CALL,
                    names.POSITION_SIDE_LONG_PUT,
                ),
                "open position must use LONG_CALL or LONG_PUT",
            )
            _require(self.qty_lots > 0, "open position must have qty_lots > 0")
            _require(
                self.instrument_key is not None,
                "open position requires instrument_key",
            )
            _require(self.avg_price is not None, "open position requires avg_price")
            _require(self.entry_ts_ns is not None, "open position requires entry_ts_ns")
        else:
            _require(
                self.position_side == names.POSITION_SIDE_FLAT,
                "flat position must use position_side FLAT",
            )
            _require(self.qty_lots == 0, "flat position must have qty_lots == 0")


@dataclass(frozen=True, slots=True)
class ExecutionState(SchemaBase):
    execution_mode: str
    entry_pending: bool
    exit_pending: bool
    family_runtime_mode: str | None = None
    strategy_runtime_mode: str | None = None
    execution_primary_provider_id: str | None = None
    execution_fallback_provider_id: str | None = None
    lock_owner: str | None = None
    pending_order_id: str | None = None
    pending_decision_id: str | None = None
    pending_entry_mode: str | None = None
    last_decision_id: str | None = None
    last_order_id: str | None = None
    last_trade_id: str | None = None
    last_ack_type: str | None = None
    last_update_ns: int = 0

    _TYPE: ClassVar[str] = "execution_state"

    def validate(self) -> None:
        _require_literal(
            self.execution_mode,
            "execution_mode",
            allowed=ALLOWED_EXECUTION_MODES,
        )
        _require_bool(self.entry_pending, "entry_pending")
        _require_bool(self.exit_pending, "exit_pending")
        if self.family_runtime_mode is not None:
            _require_literal(
                self.family_runtime_mode,
                "family_runtime_mode",
                allowed=ALLOWED_FAMILY_RUNTIME_MODES,
            )
        if self.strategy_runtime_mode is not None:
            _require_literal(
                self.strategy_runtime_mode,
                "strategy_runtime_mode",
                allowed=ALLOWED_STRATEGY_RUNTIME_MODES,
            )
        if self.execution_primary_provider_id is not None:
            _require_literal(
                self.execution_primary_provider_id,
                "execution_primary_provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.execution_fallback_provider_id is not None:
            _require_literal(
                self.execution_fallback_provider_id,
                "execution_fallback_provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.lock_owner is not None:
            _optional_non_empty_str(self.lock_owner, "lock_owner")
        if self.pending_order_id is not None:
            _optional_non_empty_str(self.pending_order_id, "pending_order_id")
        if self.pending_decision_id is not None:
            _optional_non_empty_str(self.pending_decision_id, "pending_decision_id")
        if self.pending_entry_mode is not None:
            _require_literal(
                self.pending_entry_mode,
                "pending_entry_mode",
                allowed=ALLOWED_ENTRY_MODES,
            )
        if self.last_decision_id is not None:
            _optional_non_empty_str(self.last_decision_id, "last_decision_id")
        if self.last_order_id is not None:
            _optional_non_empty_str(self.last_order_id, "last_order_id")
        if self.last_trade_id is not None:
            _optional_non_empty_str(self.last_trade_id, "last_trade_id")
        if self.last_ack_type is not None:
            _require_literal(
                self.last_ack_type,
                "last_ack_type",
                allowed=ALLOWED_ACK_TYPES,
            )
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)

@dataclass(frozen=True, slots=True)
class RiskState(SchemaBase):
    veto_entries: bool
    cooldown_active: bool
    cooldown_until_ns: int | None = None
    daily_stop_hit: bool = False
    max_loss_hit: bool = False
    max_trades_hit: bool = False
    risk_heartbeat_stale: bool = False
    max_new_lots: int = 1
    day_realized_pnl: float = 0.0
    trades_today: int = 0
    reason_code: str | None = None
    reason_message: str | None = None
    last_update_ns: int = 0

    _TYPE: ClassVar[str] = "risk_state"

    def validate(self) -> None:
        _require_bool(self.veto_entries, "veto_entries")
        _require_bool(self.cooldown_active, "cooldown_active")
        if self.cooldown_until_ns is not None:
            _require_int(self.cooldown_until_ns, "cooldown_until_ns", min_value=0)
        _require_bool(self.daily_stop_hit, "daily_stop_hit")
        _require_bool(self.max_loss_hit, "max_loss_hit")
        _require_bool(self.max_trades_hit, "max_trades_hit")
        _require_bool(self.risk_heartbeat_stale, "risk_heartbeat_stale")
        _require_int(self.max_new_lots, "max_new_lots", min_value=0)
        _require_float(self.day_realized_pnl, "day_realized_pnl")
        _require_int(self.trades_today, "trades_today", min_value=0)
        if self.reason_code is not None:
            _optional_non_empty_str(self.reason_code, "reason_code")
        if self.reason_message is not None:
            _optional_non_empty_str(self.reason_message, "reason_message")
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)

        if self.cooldown_active:
            _require(
                self.cooldown_until_ns is not None,
                "cooldown_active=True requires cooldown_until_ns",
            )



@dataclass(frozen=True, slots=True)
class FeatureState(SchemaBase):
    ts_event_ns: int
    instrument_key: str
    frame_valid: bool
    warmup_complete: bool
    strategy_mode: str
    system_state: str
    strategy_family_id: str | None = None
    doctrine_id: str | None = None
    branch_id: str | None = None
    strategy_runtime_mode: str | None = None
    family_runtime_mode: str | None = None
    explain: str | None = None

    _TYPE: ClassVar[str] = "feature_state"

    def validate(self) -> None:
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.instrument_key, "instrument_key")
        _require_bool(self.frame_valid, "frame_valid")
        _require_bool(self.warmup_complete, "warmup_complete")
        _require_literal(
            self.strategy_mode,
            "strategy_mode",
            allowed=ALLOWED_STRATEGY_MODES,
        )
        _require_literal(
            self.system_state,
            "system_state",
            allowed=ALLOWED_SYSTEM_STATES,
        )
        _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)
        if self.branch_id is not None:
            _require_literal(self.branch_id, "branch_id", allowed=ALLOWED_BRANCH_IDS)
        if self.strategy_runtime_mode is not None:
            _validate_strategy_runtime_mode_for_family(
                self.strategy_family_id,
                self.strategy_runtime_mode,
                field_name="strategy_runtime_mode",
            )
        if self.family_runtime_mode is not None:
            _require_literal(
                self.family_runtime_mode,
                "family_runtime_mode",
                allowed=ALLOWED_FAMILY_RUNTIME_MODES,
            )
        if self.explain is not None:
            _optional_non_empty_str(self.explain, "explain")


@dataclass(frozen=True, slots=True)
class StrategyState(SchemaBase):
    system_state: str
    strategy_mode: str
    waiting_on_execution: bool = False
    strategy_family_id: str | None = None
    doctrine_id: str | None = None
    branch_id: str | None = None
    family_runtime_mode: str | None = None
    strategy_runtime_mode: str | None = None
    current_regime: str | None = None
    active_futures_provider_id: str | None = None
    active_selected_option_provider_id: str | None = None
    active_option_context_provider_id: str | None = None
    active_execution_primary_provider_id: str | None = None
    active_execution_fallback_provider_id: str | None = None
    current_setup_id: str | None = None
    current_event_id: str | None = None
    current_leg_id: str | None = None
    trap_event_id: str | None = None
    burst_event_id: str | None = None
    selected_instrument_key: str | None = None
    selected_strike: float | None = None
    armed_since_ns: int | None = None
    retest_monitor_since_ns: int | None = None
    entry_pending_since_ns: int | None = None
    entry_ts_ns: int | None = None
    entry_price: float | None = None
    hard_target_price: float | None = None
    hard_stop_price: float | None = None
    proof_deadline_ns: int | None = None
    stage1_deadline_ns: int | None = None
    cooldown_until_ns: int | None = None
    highest_profit_points: float | None = None
    highest_profit_ts_ns: int | None = None
    highest_profit_price: float | None = None
    highest_fut_price: float | None = None
    lowest_fut_price: float | None = None
    breakout_ref_high_at_entry: float | None = None
    breakout_ref_low_at_entry: float | None = None
    retest_low_at_entry: float | None = None
    retest_high_at_entry: float | None = None
    entry_ce_depth_total: int | None = None
    entry_pe_depth_total: int | None = None
    entry_ce_spread_ratio: float | None = None
    entry_pe_spread_ratio: float | None = None
    primary_entry_done_in_current_leg: bool = False
    reentry_count_in_current_leg: int = 0
    last_exit_reason: str | None = None
    last_exit_pnl_points: float | None = None
    post_exit_high_fut: float | None = None
    post_exit_low_fut: float | None = None
    last_decision_id: str | None = None
    last_signal_side: str | None = None
    last_entry_mode: str | None = None
    blocker_code: str | None = None
    blocker_message: str | None = None
    last_update_ns: int = 0

    _TYPE: ClassVar[str] = "strategy_state"

    def validate(self) -> None:
        _require_literal(
            self.system_state,
            "system_state",
            allowed=ALLOWED_SYSTEM_STATES,
        )
        _require_literal(
            self.strategy_mode,
            "strategy_mode",
            allowed=ALLOWED_STRATEGY_MODES,
        )
        _require_bool(self.waiting_on_execution, "waiting_on_execution")
        _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)
        if self.branch_id is not None:
            _require_literal(self.branch_id, "branch_id", allowed=ALLOWED_BRANCH_IDS)
        if self.family_runtime_mode is not None:
            _require_literal(
                self.family_runtime_mode,
                "family_runtime_mode",
                allowed=ALLOWED_FAMILY_RUNTIME_MODES,
            )
        if self.strategy_runtime_mode is not None:
            _validate_strategy_runtime_mode_for_family(
                self.strategy_family_id,
                self.strategy_runtime_mode,
                field_name="strategy_runtime_mode",
            )
        if self.current_regime is not None:
            _require_literal(
                self.current_regime,
                "current_regime",
                allowed=ALLOWED_STRATEGY_REGIMES,
            )
        for field_name in (
            "active_futures_provider_id",
            "active_selected_option_provider_id",
            "active_option_context_provider_id",
            "active_execution_primary_provider_id",
            "active_execution_fallback_provider_id",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_literal(value, field_name, allowed=ALLOWED_PROVIDER_IDS)
        for field_name in (
            "current_setup_id",
            "current_event_id",
            "current_leg_id",
            "trap_event_id",
            "burst_event_id",
            "selected_instrument_key",
            "last_decision_id",
            "last_exit_reason",
            "blocker_code",
            "blocker_message",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _optional_non_empty_str(value, field_name)
        for field_name in (
            "armed_since_ns",
            "retest_monitor_since_ns",
            "entry_pending_since_ns",
            "entry_ts_ns",
            "proof_deadline_ns",
            "stage1_deadline_ns",
            "cooldown_until_ns",
            "highest_profit_ts_ns",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_int(value, field_name, min_value=0)
        for field_name in (
            "selected_strike",
            "entry_price",
            "hard_target_price",
            "hard_stop_price",
            "highest_profit_points",
            "highest_profit_price",
            "highest_fut_price",
            "lowest_fut_price",
            "breakout_ref_high_at_entry",
            "breakout_ref_low_at_entry",
            "retest_low_at_entry",
            "retest_high_at_entry",
            "entry_ce_spread_ratio",
            "entry_pe_spread_ratio",
            "last_exit_pnl_points",
            "post_exit_high_fut",
            "post_exit_low_fut",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_float(value, field_name)
        for field_name in ("entry_ce_depth_total", "entry_pe_depth_total"):
            value = getattr(self, field_name)
            if value is not None:
                _require_int(value, field_name, min_value=0)
        _require_bool(
            self.primary_entry_done_in_current_leg,
            "primary_entry_done_in_current_leg",
        )
        _require_int(
            self.reentry_count_in_current_leg,
            "reentry_count_in_current_leg",
            min_value=0,
        )
        if self.last_signal_side is not None:
            _require_literal(
                self.last_signal_side,
                "last_signal_side",
                allowed=ALLOWED_OPTION_SIDES,
            )
        if self.last_entry_mode is not None:
            _require_literal(
                self.last_entry_mode,
                "last_entry_mode",
                allowed=ALLOWED_ENTRY_MODES,
            )
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)

        if self.system_state == names.STATE_RETEST_MONITOR:
            _require(
                self.retest_monitor_since_ns is not None,
                "RETEST_MONITOR state requires retest_monitor_since_ns",
            )
        if self.system_state == names.STATE_ARMED:
            _require(
                self.armed_since_ns is not None,
                "ARMED state requires armed_since_ns",
            )
        if self.burst_event_id is not None:
            _require(
                self.strategy_family_id in (None, names.STRATEGY_FAMILY_MISO),
                "burst_event_id is valid only for MISO or unspecified family",
            )
        if self.trap_event_id is not None:
            _require(
                self.strategy_family_id in (None, names.STRATEGY_FAMILY_MISR),
                "trap_event_id is valid only for MISR or unspecified family",
            )
@dataclass(frozen=True, slots=True)
class LoginState(SchemaBase):
    broker_name: str
    authenticated: bool
    provider_id: str | None = None
    account_id: str | None = None
    session_expires_ns: int | None = None
    last_refresh_ns: int | None = None
    message: str | None = None

    _TYPE: ClassVar[str] = "login_state"

    def validate(self) -> None:
        _require_non_empty_str(self.broker_name, "broker_name")
        _require_bool(self.authenticated, "authenticated")
        if self.provider_id is not None:
            _require_literal(
                self.provider_id,
                "provider_id",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        if self.account_id is not None:
            _optional_non_empty_str(self.account_id, "account_id")
        if self.session_expires_ns is not None:
            _require_int(self.session_expires_ns, "session_expires_ns", min_value=0)
        if self.last_refresh_ns is not None:
            _require_int(self.last_refresh_ns, "last_refresh_ns", min_value=0)
        if self.message is not None:
            _optional_non_empty_str(self.message, "message")

@dataclass(frozen=True, slots=True)
class ReportState(SchemaBase):
    last_report_ns: int | None = None
    last_ledger_id: str | None = None
    history_limit: int = 0
    last_update_ns: int = 0

    _TYPE: ClassVar[str] = "report_state"

    def validate(self) -> None:
        if self.last_report_ns is not None:
            _require_int(self.last_report_ns, "last_report_ns", min_value=0)
        if self.last_ledger_id is not None:
            _optional_non_empty_str(self.last_ledger_id, "last_ledger_id")
        _require_int(self.history_limit, "history_limit", min_value=0)
        _require_int(self.last_update_ns, "last_update_ns", min_value=0)


# ============================================================================
# Reporting / analytics models
# ============================================================================


@dataclass(frozen=True, slots=True)
class ReportTradeRow(SchemaBase):
    trade_id: str
    ts_entry_ns: int | None = None
    ts_exit_ns: int | None = None
    instrument_key: str | None = None
    option_side: str | None = None
    entry_mode: str | None = None
    position_side: str | None = None
    entry_price: float | None = None
    exit_price: float | None = None
    quantity_lots: int = 0
    realized_pnl_rupees: float | None = None
    exit_reason: str | None = None
    decision_id: str | None = None
    order_id: str | None = None

    _TYPE: ClassVar[str] = "report_trade_row"

    def validate(self) -> None:
        _require_non_empty_str(self.trade_id, "trade_id")
        if self.ts_entry_ns is not None:
            _require_int(self.ts_entry_ns, "ts_entry_ns", min_value=0)
        if self.ts_exit_ns is not None:
            _require_int(self.ts_exit_ns, "ts_exit_ns", min_value=0)
        if self.ts_entry_ns is not None and self.ts_exit_ns is not None:
            _require(self.ts_exit_ns >= self.ts_entry_ns, "ts_exit_ns must be >= ts_entry_ns")
        if self.instrument_key is not None:
            _optional_non_empty_str(self.instrument_key, "instrument_key")
        if self.option_side is not None:
            _require_literal(
                self.option_side,
                "option_side",
                allowed=ALLOWED_OPTION_SIDES,
            )
        if self.entry_mode is not None:
            _require_literal(
                self.entry_mode,
                "entry_mode",
                allowed=ALLOWED_ENTRY_MODES,
            )
        if self.position_side is not None:
            _require_literal(
                self.position_side,
                "position_side",
                allowed=ALLOWED_POSITION_SIDES,
            )
        if self.entry_price is not None:
            _require_float(self.entry_price, "entry_price", min_value=0.0)
        if self.exit_price is not None:
            _require_float(self.exit_price, "exit_price", min_value=0.0)
        _require_int(self.quantity_lots, "quantity_lots", min_value=0)
        if self.realized_pnl_rupees is not None:
            _require_float(self.realized_pnl_rupees, "realized_pnl_rupees")
        if self.exit_reason is not None:
            _optional_non_empty_str(self.exit_reason, "exit_reason")
        if self.decision_id is not None:
            _optional_non_empty_str(self.decision_id, "decision_id")
        if self.order_id is not None:
            _optional_non_empty_str(self.order_id, "order_id")


# ============================================================================
# Operational / observability models
# ============================================================================


@dataclass(frozen=True, slots=True)
class Heartbeat(SchemaBase):
    service: str
    instance_id: str
    ts_event_ns: int
    status: str
    message: str | None = None

    _TYPE: ClassVar[str] = "heartbeat"

    def validate(self) -> None:
        _require_non_empty_str(self.service, "service")
        _require_non_empty_str(self.instance_id, "instance_id")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_literal(
            self.status,
            "status",
            allowed=ALLOWED_HEALTH_STATUSES,
        )
        if self.message is not None:
            _optional_non_empty_str(self.message, "message")



@dataclass(frozen=True, slots=True)
class ErrorEvent(SchemaBase):
    error_id: str
    ts_event_ns: int
    service: str
    severity: str
    code: str
    message: str
    correlation_id: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    _TYPE: ClassVar[str] = "error_event"

    def validate(self) -> None:
        _require_non_empty_str(self.error_id, "error_id")
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        _require_non_empty_str(self.service, "service")
        _require_literal(
            self.severity,
            "severity",
            allowed=ALLOWED_ERROR_SEVERITIES,
        )
        _require_non_empty_str(self.code, "code")
        _require_non_empty_str(self.message, "message")
        if self.correlation_id is not None:
            _optional_non_empty_str(self.correlation_id, "correlation_id")
        details = _require_mapping(self.details, "details")
        details = {str(k): _plain_value(v) for k, v in details.items()}
        object.__setattr__(self, "details", details)

# ============================================================================
# Registry / helpers
# ============================================================================


MODEL_REGISTRY: Final[Mapping[str, type[SchemaBase]]] = MappingProxyType(
    {
        cls._TYPE: cls
        for cls in (
            EventEnvelope,
            BookLevel,
            FeedTick,
            FuturesSnapshot,
            OptionSnapshot,
            SnapshotMember,
            SnapshotFrame,
            EconomicViability,
            FourPillarSignal,
            DeltaProxyNormalization,
            MistTrendSurface,
            MisbBreakoutSurface,
            MiscCompressionRetestSurface,
            MisrTrapSurface,
            MisoMicrostructureSurface,
            FeatureFrame,
            StopPlan,
            TargetPlan,
            StrategyDecision,
            OperatorCommand,
            DecisionAck,
            OrderIntent,
            PendingOrderState,
            TradeFill,
            TradeLedgerRow,
            FuturesSnapshotState,
            OptionSnapshotState,
            DhanStrikeScoreComponents,
            DhanContextEvent,
            DhanContextState,
            ProviderHealthState,
            ProviderRuntimeState,
            ProviderTransitionEvent,
            RuntimeModeState,
            PositionState,
            ExecutionState,
            RiskState,
            FeatureState,
            StrategyState,
            LoginState,
            ReportState,
            ReportTradeRow,
            Heartbeat,
            ErrorEvent,
        )
    }
)


def model_from_type(type_name: str, raw: Mapping[str, Any]) -> SchemaBase:
    normalized = _require_non_empty_str(type_name, "type_name")
    model_cls = MODEL_REGISTRY.get(normalized)
    if model_cls is None:
        raise ModelValidationError(f"unknown model type: {normalized!r}")
    return model_cls.from_mapping(raw)


def validate_payload(model_cls: type[T], raw: Mapping[str, Any]) -> T:
    return model_cls.from_mapping(raw)



__all__ = [
    "ALLOWED_ACK_TYPES",
    "ALLOWED_ACTIONS",
    "ALLOWED_BRANCH_IDS",
    "ALLOWED_COMMAND_TYPES",
    "ALLOWED_CONTROL_MODES",
    "ALLOWED_DOCTRINE_IDS",
    "ALLOWED_ENTRY_MODES",
    "ALLOWED_ERROR_SEVERITIES",
    "ALLOWED_EXECUTION_MODES",
    "ALLOWED_FAMILY_RUNTIME_MODES",
    "ALLOWED_HEALTH_STATUSES",
    "ALLOWED_INSTRUMENT_ROLES",
    "ALLOWED_OPTION_SIDES",
    "ALLOWED_POSITION_EFFECTS",
    "ALLOWED_POSITION_SIDES",
    "ALLOWED_PROVIDER_FAILOVER_MODES",
    "ALLOWED_PROVIDER_IDS",
    "ALLOWED_PROVIDER_OVERRIDE_MODES",
    "ALLOWED_PROVIDER_ROLES",
    "ALLOWED_PROVIDER_STATUSES",
    "ALLOWED_PROVIDER_TRANSITION_REASONS",
    "ALLOWED_RETEST_TYPES",
    "ALLOWED_SNAPSHOT_VALIDITY",
    "ALLOWED_STRATEGY_FAMILY_IDS",
    "ALLOWED_STRATEGY_MODES",
    "ALLOWED_STRATEGY_REGIMES",
    "ALLOWED_STRATEGY_RUNTIME_MODES",
    "ALLOWED_SYSTEM_STATES",
    "ALLOWED_TICK_VALIDITY",
    "BookLevel",
    "DecisionAck",
    "DeltaProxyNormalization",
    "DhanContextEvent",
    "DhanContextState",
    "DhanStrikeScoreComponents",
    "EconomicViability",
    "ErrorEvent",
    "EventEnvelope",
    "ExecutionState",
    "FeatureFrame",
    "FeatureState",
    "FeedTick",
    "FourPillarSignal",
    "FuturesSnapshot",
    "FuturesSnapshotState",
    "Heartbeat",
    "InstrumentRole",
    "LoginState",
    "MisbBreakoutSurface",
    "MiscCompressionRetestSurface",
    "MISO_ALLOWED_STRATEGY_RUNTIME_MODES",
    "MisoMicrostructureSurface",
    "MistTrendSurface",
    "MODEL_REGISTRY",
    "ModelError",
    "ModelValidationError",
    "MisrTrapSurface",
    "NON_MISO_ALLOWED_STRATEGY_RUNTIME_MODES",
    "OptionSnapshot",
    "OptionSnapshotState",
    "OperatorCommand",
    "OrderIntent",
    "PendingOrderState",
    "PositionState",
    "ProviderHealthState",
    "ProviderRuntimeState",
    "ProviderTransitionEvent",
    "ReportState",
    "ReportTradeRow",
    "RetestType",
    "RiskState",
    "RuntimeModeState",
    "SchemaBase",
    "SnapshotFrame",
    "SnapshotMember",
    "SnapshotValidity",
    "StopPlan",
    "StrategyDecision",
    "StrategyRegime",
    "StrategyState",
    "TargetPlan",
    "TickValidity",
    "TradeFill",
    "TradeLedgerRow",
    "model_from_type",
    "validate_payload",
]
