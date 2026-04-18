from __future__ import annotations

"""
app/mme_scalpx/research_capture/models.py

Frozen typed model layer for the MME research data capture chapter.

Purpose
-------
This module defines the canonical in-memory models used by the research capture
subsystem. It provides typed component models for the stable parts of the
capture surface, contract-validated field bundles for wider metric packs, and
session/archive manifest models.

Owns
----
- immutable typed models for capture records and archive/session metadata
- contract-aware validation of field names and values
- canonical record assembly for archive-ready rows
- dataset-specific validation rules for futures ticks, option ticks,
  signal-audit rows, and runtime-audit rows

Does not own
------------
- broker IO
- Redis IO
- Parquet IO
- runtime orchestration
- replay logic
- production strategy doctrine

Design laws
-----------
- recorded != strategy-approved
- derived != production-used
- researched != contract-changed
- stable surfaces should be typed; broader evolving metric packs may remain
  contract-validated field bundles
- model validation must be deterministic and side-effect free
"""

from dataclasses import dataclass, field, fields as dataclass_fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from app.mme_scalpx.research_capture.contracts import (
    ARCHIVE_OUTPUT_FILENAMES,
    CHAPTER_NAME,
    CONSTITUTION_NAME,
    FIELD_NAMES,
    FIELD_SPECS_BY_NAME,
    MANIFEST_REQUIRED_KEYS,
    PRIMARY_PARTITIONS,
    SCHEMA_NAME,
    SCHEMA_STATUS,
    SCHEMA_VERSION,
    SECONDARY_PARTITIONS,
    SESSION_FILE_FILENAMES,
    FieldGroup,
    FieldLayer,
)


def _utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp with timezone information."""
    return datetime.now(timezone.utc).isoformat()


def _freeze_mapping(values: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Return an immutable shallow copy of the supplied mapping."""
    if values is None:
        return MappingProxyType({})
    return MappingProxyType(dict(values))


def _freeze_str_sequence(values: Sequence[str] | None) -> tuple[str, ...]:
    """Return an immutable tuple of strings."""
    if values is None:
        return ()
    return tuple(values)


def _freeze_partition_sequence(values: Sequence[str] | None) -> tuple[str, ...]:
    """Return an immutable tuple of partition column names."""
    if values is None:
        return ()
    return tuple(values)


def _is_non_bool_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_real_number(value: Any) -> bool:
    return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)


def _validate_sequence_items(
    *,
    field_name: str,
    value: Any,
    item_type: str,
) -> None:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name}: expected list/tuple, got {type(value).__name__}")

    for index, item in enumerate(value):
        if item_type == "float":
            if not _is_real_number(item):
                raise TypeError(
                    f"{field_name}[{index}]: expected float-compatible number, got {type(item).__name__}"
                )
        elif item_type == "int":
            if not _is_non_bool_int(item):
                raise TypeError(f"{field_name}[{index}]: expected int, got {type(item).__name__}")
        elif item_type == "str":
            if not isinstance(item, str):
                raise TypeError(f"{field_name}[{index}]: expected str, got {type(item).__name__}")
        else:
            raise ValueError(f"{field_name}: unsupported item_type validator {item_type!r}")


def validate_capture_value_against_contract(name: str, value: Any) -> None:
    """
    Validate one field value against the frozen field contract.

    None is allowed for all fields at the model layer because recommended and
    optional fields may legitimately be absent. Record-level validation decides
    which fields are mandatory for a specific dataset.
    """
    try:
        spec = FIELD_SPECS_BY_NAME[name]
    except KeyError as exc:
        raise KeyError(f"Unknown research-capture field: {name}") from exc

    if value is None:
        return

    dtype = spec.dtype
    if dtype == "str":
        if not isinstance(value, str):
            raise TypeError(f"{name}: expected str, got {type(value).__name__}")
    elif dtype == "str_or_int":
        if not (isinstance(value, str) or _is_non_bool_int(value)):
            raise TypeError(f"{name}: expected str_or_int, got {type(value).__name__}")
    elif dtype == "int":
        if not _is_non_bool_int(value):
            raise TypeError(f"{name}: expected int, got {type(value).__name__}")
    elif dtype == "float":
        if not _is_real_number(value):
            raise TypeError(f"{name}: expected float-compatible number, got {type(value).__name__}")
    elif dtype == "bool":
        if not isinstance(value, bool):
            raise TypeError(f"{name}: expected bool, got {type(value).__name__}")
    elif dtype == "json_list_float":
        _validate_sequence_items(field_name=name, value=value, item_type="float")
    elif dtype == "json_list_int":
        _validate_sequence_items(field_name=name, value=value, item_type="int")
    elif dtype == "json_list_str":
        _validate_sequence_items(field_name=name, value=value, item_type="str")
    else:
        raise ValueError(f"{name}: unsupported contract dtype {dtype!r}")

    if spec.allowed_values:
        if isinstance(value, (list, tuple)):
            invalid = [item for item in value if item not in spec.allowed_values]
            if invalid:
                raise ValueError(f"{name}: values not allowed by contract: {invalid!r}")
        else:
            if value not in spec.allowed_values:
                raise ValueError(
                    f"{name}: value {value!r} not allowed by contract {spec.allowed_values!r}"
                )


def _validate_bundle_fields(
    *,
    values: Mapping[str, Any],
    allowed_layers: Sequence[FieldLayer] | None = None,
    allowed_groups: Sequence[FieldGroup] | None = None,
) -> Mapping[str, Any]:
    frozen = _freeze_mapping(values)
    layer_set = set(allowed_layers or ())
    group_set = set(allowed_groups or ())
    seen: set[str] = set()

    for name, value in frozen.items():
        if name in seen:
            raise ValueError(f"Duplicate bundle field: {name}")
        seen.add(name)

        spec = FIELD_SPECS_BY_NAME.get(name)
        if spec is None:
            raise KeyError(f"Unknown research-capture field in bundle: {name}")

        if layer_set and spec.layer not in layer_set:
            allowed = ", ".join(layer.value for layer in layer_set)
            raise ValueError(f"{name}: field layer {spec.layer.value} not allowed in bundle [{allowed}]")

        if group_set and spec.group not in group_set:
            allowed = ", ".join(group.value for group in group_set)
            raise ValueError(f"{name}: field group {spec.group.value} not allowed in bundle [{allowed}]")

        validate_capture_value_against_contract(name, value)

    return frozen


def _merge_field_maps(*maps: Mapping[str, Any]) -> dict[str, Any]:
    """
    Merge canonical field maps and reject conflicting duplicate assignments.
    """
    merged: dict[str, Any] = {}
    for mapping in maps:
        for name, value in mapping.items():
            if name in merged and merged[name] != value:
                raise ValueError(
                    f"Conflicting values for canonical field {name!r}: "
                    f"{merged[name]!r} != {value!r}"
                )
            merged[name] = value
    return merged


def _dataclass_to_field_map(instance: Any, *, include_none: bool = False) -> dict[str, Any]:
    """
    Convert a dataclass instance into a canonical field map, skipping private and
    non-canonical attributes.
    """
    result: dict[str, Any] = {}
    for dataclass_field in dataclass_fields(instance):
        name = dataclass_field.name
        if name.startswith("_"):
            continue
        if name not in FIELD_SPECS_BY_NAME:
            continue
        value = getattr(instance, name)
        if value is None and not include_none:
            continue
        if isinstance(value, tuple) and FIELD_SPECS_BY_NAME[name].dtype.startswith("json_list_"):
            result[name] = list(value)
        else:
            result[name] = value
    return result


@dataclass(frozen=True, slots=True)
class FieldBundle:
    """
    Immutable contract-validated bundle of canonical fields.

    This is used for wider, more change-prone metric surfaces where a dedicated
    typed dataclass for every field would be brittle.
    """

    values: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    allowed_layers: tuple[FieldLayer, ...] = ()
    allowed_groups: tuple[FieldGroup, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            _validate_bundle_fields(
                values=self.values,
                allowed_layers=self.allowed_layers,
                allowed_groups=self.allowed_groups,
            ),
        )
        object.__setattr__(self, "allowed_layers", tuple(self.allowed_layers))
        object.__setattr__(self, "allowed_groups", tuple(self.allowed_groups))

    def to_field_map(self) -> dict[str, Any]:
        return dict(self.values)

    @classmethod
    def empty(
        cls,
        *,
        allowed_layers: Sequence[FieldLayer],
        allowed_groups: Sequence[FieldGroup] = (),
    ) -> "FieldBundle":
        return cls(
            values=MappingProxyType({}),
            allowed_layers=tuple(allowed_layers),
            allowed_groups=tuple(allowed_groups),
        )


@dataclass(frozen=True, slots=True)
class TimingIdentity:
    session_date: str
    exchange_ts: float
    recv_ts_ns: int
    process_ts_ns: int
    event_seq: int
    source_ts_ns: int | None = None
    snapshot_id: str | None = None
    processed_ts: float | None = None
    network_time: float | None = None

    def __post_init__(self) -> None:
        if not self.session_date:
            raise ValueError("session_date must be non-empty")
        if not _is_real_number(self.exchange_ts):
            raise TypeError("exchange_ts must be float-compatible")
        if not _is_non_bool_int(self.recv_ts_ns):
            raise TypeError("recv_ts_ns must be int")
        if not _is_non_bool_int(self.process_ts_ns):
            raise TypeError("process_ts_ns must be int")
        if not _is_non_bool_int(self.event_seq):
            raise TypeError("event_seq must be int")
        if self.source_ts_ns is not None and not _is_non_bool_int(self.source_ts_ns):
            raise TypeError("source_ts_ns must be int or None")
        if self.snapshot_id is not None and not isinstance(self.snapshot_id, str):
            raise TypeError("snapshot_id must be str or None")
        if self.processed_ts is not None and not _is_real_number(self.processed_ts):
            raise TypeError("processed_ts must be float-compatible or None")
        if self.network_time is not None and not _is_real_number(self.network_time):
            raise TypeError("network_time must be float-compatible or None")

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        return _dataclass_to_field_map(self, include_none=include_none)


@dataclass(frozen=True, slots=True)
class InstrumentIdentity:
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

        if not (isinstance(self.instrument_token, str) or _is_non_bool_int(self.instrument_token)):
            raise TypeError("instrument_token must be str or int")
        if not _is_real_number(self.tick_size):
            raise TypeError("tick_size must be float-compatible")
        if not _is_non_bool_int(self.lot_size):
            raise TypeError("lot_size must be int")
        if self.symbol is not None and not isinstance(self.symbol, str):
            raise TypeError("symbol must be str or None")
        if self.symbol_token is not None and not isinstance(self.symbol_token, str):
            raise TypeError("symbol_token must be str or None")
        if self.contract_name is not None and not isinstance(self.contract_name, str):
            raise TypeError("contract_name must be str or None")
        if self.underlying_token is not None and not (
            isinstance(self.underlying_token, str) or _is_non_bool_int(self.underlying_token)
        ):
            raise TypeError("underlying_token must be str, int, or None")
        if self.strike is not None and not _is_non_bool_int(self.strike):
            raise TypeError("strike must be int or None")
        if self.freeze_qty is not None and not _is_non_bool_int(self.freeze_qty):
            raise TypeError("freeze_qty must be int or None")
        if self.strike_step is not None and not _is_non_bool_int(self.strike_step):
            raise TypeError("strike_step must be int or None")

        for field_name in ("option_type", "expiry", "expiry_type", "moneyness_bucket"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{field_name} must be str or None")

        for name, value in self.to_field_map(include_none=False).items():
            validate_capture_value_against_contract(name, value)

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        field_map = _dataclass_to_field_map(self, include_none=include_none)
        if "option_type" not in field_map and include_none:
            field_map["option_type"] = None
        return field_map


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    ltp: float
    volume: int
    price: float | None = None
    oi: int | None = None
    best_bid: float | None = None
    best_ask: float | None = None
    best_bid_qty: int | None = None
    best_ask_qty: int | None = None
    bid_prices: tuple[float, ...] = ()
    bid_qty: tuple[int, ...] = ()
    ask_prices: tuple[float, ...] = ()
    ask_qty: tuple[int, ...] = ()
    depth_levels_present_bid: int | None = None
    depth_levels_present_ask: int | None = None
    mid_price: float | None = None
    microprice: float | None = None

    def __post_init__(self) -> None:
        if not _is_real_number(self.ltp):
            raise TypeError("ltp must be float-compatible")
        if not _is_non_bool_int(self.volume):
            raise TypeError("volume must be int")
        if self.price is not None and not _is_real_number(self.price):
            raise TypeError("price must be float-compatible or None")
        if self.oi is not None and not _is_non_bool_int(self.oi):
            raise TypeError("oi must be int or None")

        for name in ("best_bid", "best_ask", "mid_price", "microprice"):
            value = getattr(self, name)
            if value is not None and not _is_real_number(value):
                raise TypeError(f"{name} must be float-compatible or None")

        for name in ("best_bid_qty", "best_ask_qty", "depth_levels_present_bid", "depth_levels_present_ask"):
            value = getattr(self, name)
            if value is not None and not _is_non_bool_int(value):
                raise TypeError(f"{name} must be int or None")

        object.__setattr__(self, "bid_prices", tuple(self.bid_prices))
        object.__setattr__(self, "bid_qty", tuple(self.bid_qty))
        object.__setattr__(self, "ask_prices", tuple(self.ask_prices))
        object.__setattr__(self, "ask_qty", tuple(self.ask_qty))

        _validate_sequence_items(field_name="bid_prices", value=self.bid_prices, item_type="float")
        _validate_sequence_items(field_name="bid_qty", value=self.bid_qty, item_type="int")
        _validate_sequence_items(field_name="ask_prices", value=self.ask_prices, item_type="float")
        _validate_sequence_items(field_name="ask_qty", value=self.ask_qty, item_type="int")

        if len(self.bid_prices) != len(self.bid_qty):
            raise ValueError("bid_prices and bid_qty lengths must match")
        if len(self.ask_prices) != len(self.ask_qty):
            raise ValueError("ask_prices and ask_qty lengths must match")

        for name, value in self.to_field_map(include_none=False).items():
            validate_capture_value_against_contract(name, value)

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        return _dataclass_to_field_map(self, include_none=include_none)


@dataclass(frozen=True, slots=True)
class ContextAnchors:
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

    def __post_init__(self) -> None:
        for name in ("spot_symbol", "fut_symbol"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be str or None")
        for name in (
            "spot",
            "spot_ts",
            "fut_ltp",
            "fut_ts",
            "vix",
            "vix_ts",
            "pcr",
            "iv",
            "atm_iv",
            "orb_high",
            "orb_low",
            "orb_ts",
        ):
            value = getattr(self, name)
            if value is not None and not _is_real_number(value):
                raise TypeError(f"{name} must be float-compatible or None")
        if self.fut_vol is not None and not _is_non_bool_int(self.fut_vol):
            raise TypeError("fut_vol must be int or None")

        for name, value in self.to_field_map(include_none=False).items():
            validate_capture_value_against_contract(name, value)

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        return _dataclass_to_field_map(self, include_none=include_none)


@dataclass(frozen=True, slots=True)
class SessionContext:
    is_expiry: bool
    dte: int
    market_open: str | None = None
    market_close: str | None = None
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

    def __post_init__(self) -> None:
        if not isinstance(self.is_expiry, bool):
            raise TypeError("is_expiry must be bool")
        if not _is_non_bool_int(self.dte):
            raise TypeError("dte must be int")
        for name in ("market_open", "market_close"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be str or None")
        if self.days_to_expiry_exact is not None and not _is_real_number(self.days_to_expiry_exact):
            raise TypeError("days_to_expiry_exact must be float-compatible or None")
        for name in ("is_current_week", "is_next_week", "is_monthly_expiry", "expiry_week_flag"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, bool):
                raise TypeError(f"{name} must be bool or None")
        if self.trading_minute_index is not None and not _is_non_bool_int(self.trading_minute_index):
            raise TypeError("trading_minute_index must be int or None")
        if not isinstance(self.is_preopen, bool):
            raise TypeError("is_preopen must be bool")
        if not isinstance(self.is_postclose, bool):
            raise TypeError("is_postclose must be bool")
        if self.weekday is not None and not _is_non_bool_int(self.weekday):
            raise TypeError("weekday must be int or None")
        if self.month is not None and not _is_non_bool_int(self.month):
            raise TypeError("month must be int or None")

        for name, value in self.to_field_map(include_none=False).items():
            validate_capture_value_against_contract(name, value)

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        return _dataclass_to_field_map(self, include_none=include_none)


@dataclass(frozen=True, slots=True)
class RuntimeAuditState:
    is_stale_tick: bool
    missing_depth_flag: bool
    missing_oi_flag: bool
    thin_book: bool
    integrity_flags: tuple[str, ...] = ()
    stale_reason: str | None = None
    book_is_thin: bool | None = None
    crossed_book_flag: bool | None = None
    locked_book_flag: bool | None = None
    fallback_used_flag: bool | None = None
    fallback_source: str | None = None
    schema_version: str = SCHEMA_VERSION
    normalization_version: str | None = None
    derived_version: str | None = None
    calendar_version: str | None = None
    heartbeat_status: str | None = None
    reconnect_count: int | None = None
    last_reconnect_reason: str | None = None
    gpu_fallback: bool | None = None
    cpu_mode_flag: bool | None = None
    latency_ns: int | None = None
    gap_from_prev_tick_ms: int | None = None

    def __post_init__(self) -> None:
        for name in ("is_stale_tick", "missing_depth_flag", "missing_oi_flag", "thin_book"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be bool")

        object.__setattr__(self, "integrity_flags", tuple(self.integrity_flags))
        _validate_sequence_items(field_name="integrity_flags", value=self.integrity_flags, item_type="str")

        for name in (
            "book_is_thin",
            "crossed_book_flag",
            "locked_book_flag",
            "fallback_used_flag",
            "gpu_fallback",
            "cpu_mode_flag",
        ):
            value = getattr(self, name)
            if value is not None and not isinstance(value, bool):
                raise TypeError(f"{name} must be bool or None")

        for name in (
            "stale_reason",
            "fallback_source",
            "schema_version",
            "normalization_version",
            "derived_version",
            "calendar_version",
            "heartbeat_status",
            "last_reconnect_reason",
        ):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be str or None")

        for name in ("reconnect_count", "latency_ns", "gap_from_prev_tick_ms"):
            value = getattr(self, name)
            if value is not None and not _is_non_bool_int(value):
                raise TypeError(f"{name} must be int or None")

        for name, value in self.to_field_map(include_none=False).items():
            validate_capture_value_against_contract(name, value)

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        return _dataclass_to_field_map(self, include_none=include_none)


@dataclass(frozen=True, slots=True)
class StrategyAuditState:
    candidate_id: str | None = None
    candidate_stage: str | None = None
    candidate_side: str | None = None
    candidate_score: float | None = None
    blocker_mask: str | None = None
    blocker_primary: str | None = None
    blocker_chain: str | None = None
    entry_window_open_flag: bool | None = None
    regime_gate_flag: bool | None = None
    context_gate_flag: bool | None = None
    confirmation_gate_flag: bool | None = None
    risk_gate_flag: bool | None = None
    hold_against: int | None = None
    invalid_secs: int | None = None
    strategy_id: str | None = None
    decision_id: str | None = None
    decision_action: str | None = None
    execution_mode: str | None = None
    ack_type: str | None = None
    order_id: str | None = None
    trade_id: str | None = None
    position_side: str | None = None
    entry_mode: str | None = None
    exit_reason: str | None = None

    def __post_init__(self) -> None:
        for name, value in self.to_field_map(include_none=False).items():
            validate_capture_value_against_contract(name, value)

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        return _dataclass_to_field_map(self, include_none=include_none)


class CaptureDatasetName(str, Enum):
    TICKS_FUT = "ticks_fut"
    TICKS_OPT = "ticks_opt"
    SIGNALS_AUDIT = "signals_audit"
    RUNTIME_AUDIT = "runtime_audit"

    @property
    def archive_filename(self) -> str:
        return ARCHIVE_OUTPUT_FILENAMES[self.value]


_COMMON_RECORD_REQUIRED_FIELDS: tuple[str, ...] = (
    "session_date",
    "exchange_ts",
    "recv_ts_ns",
    "process_ts_ns",
    "event_seq",
    "instrument_token",
    "tradingsymbol",
    "instrument_type",
    "schema_version",
)

_TICK_MARKET_REQUIRED_FIELDS: tuple[str, ...] = (
    "ltp",
    "volume",
    "best_bid",
    "best_ask",
    "bid_prices",
    "bid_qty",
    "ask_prices",
    "ask_qty",
)

_TICK_AUDIT_REQUIRED_FIELDS: tuple[str, ...] = (
    "spread",
    "spread_pct",
    "nof",
    "is_stale_tick",
    "missing_depth_flag",
    "missing_oi_flag",
    "thin_book",
    "integrity_flags",
)


@dataclass(frozen=True, slots=True)
class CaptureRecord:
    """
    Canonical archive-ready capture record assembled from typed components.

    The record intentionally keeps stable core surfaces typed while allowing
    broader metric families to be supplied via contract-validated field bundles.
    """

    dataset: CaptureDatasetName
    timing: TimingIdentity
    instrument: InstrumentIdentity
    market: MarketSnapshot | None = None
    context: ContextAnchors | None = None
    session: SessionContext | None = None
    live_metrics: FieldBundle = field(
        default_factory=lambda: FieldBundle.empty(allowed_layers=(FieldLayer.LIVE_DERIVED_LIGHTWEIGHT,))
    )
    runtime_audit: RuntimeAuditState | None = None
    strategy_audit: StrategyAuditState | None = None
    extra_fields: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "extra_fields",
            _validate_bundle_fields(
                values=self.extra_fields,
                allowed_layers=(FieldLayer.RAW_RECOMMENDED, FieldLayer.LIVE_DERIVED_LIGHTWEIGHT),
            ),
        )

        if self.dataset in {CaptureDatasetName.TICKS_FUT, CaptureDatasetName.TICKS_OPT} and self.market is None:
            raise ValueError(f"{self.dataset.value}: market snapshot is required for tick datasets")
        if self.runtime_audit is None:
            raise ValueError("runtime_audit is required for all capture records")

        field_map = self.to_field_map(include_none=False)
        missing = [name for name in self.required_fields() if name not in field_map]
        if missing:
            raise ValueError(f"{self.dataset.value}: missing required fields {missing}")

        if self.dataset is CaptureDatasetName.TICKS_FUT:
            if self.instrument.instrument_type != "FUT":
                raise ValueError("ticks_fut dataset requires instrument_type='FUT'")
            if self.instrument.expiry is None:
                raise ValueError("ticks_fut dataset requires expiry")
        elif self.dataset is CaptureDatasetName.TICKS_OPT:
            if self.instrument.instrument_type not in {"CE", "PE"}:
                raise ValueError("ticks_opt dataset requires instrument_type in {'CE','PE'}")
            if self.instrument.option_type not in {"CE", "PE"}:
                raise ValueError("ticks_opt dataset requires option_type in {'CE','PE'}")
            if self.instrument.strike is None:
                raise ValueError("ticks_opt dataset requires strike")
            if self.instrument.expiry is None:
                raise ValueError("ticks_opt dataset requires expiry")

        if self.dataset in {CaptureDatasetName.TICKS_FUT, CaptureDatasetName.TICKS_OPT}:
            if not self.runtime_audit.missing_depth_flag:
                if self.market is None:
                    raise ValueError("tick dataset missing market snapshot")
                if not self.market.bid_prices or not self.market.ask_prices:
                    raise ValueError("depth arrays required when missing_depth_flag is False")
                if self.market.best_bid is None or self.market.best_ask is None:
                    raise ValueError("best_bid and best_ask required when missing_depth_flag is False")

    def required_fields(self) -> tuple[str, ...]:
        required = list(_COMMON_RECORD_REQUIRED_FIELDS)
        if self.dataset in {CaptureDatasetName.TICKS_FUT, CaptureDatasetName.TICKS_OPT}:
            required.extend(_TICK_MARKET_REQUIRED_FIELDS)
            required.extend(_TICK_AUDIT_REQUIRED_FIELDS)
        return tuple(required)

    def to_field_map(self, *, include_none: bool = False) -> dict[str, Any]:
        maps: list[Mapping[str, Any]] = [
            self.timing.to_field_map(include_none=include_none),
            self.instrument.to_field_map(include_none=include_none),
        ]
        if self.market is not None:
            maps.append(self.market.to_field_map(include_none=include_none))
        if self.context is not None:
            maps.append(self.context.to_field_map(include_none=include_none))
        if self.session is not None:
            maps.append(self.session.to_field_map(include_none=include_none))
        maps.append(self.live_metrics.to_field_map())
        if self.runtime_audit is not None:
            maps.append(self.runtime_audit.to_field_map(include_none=include_none))
        if self.strategy_audit is not None:
            maps.append(self.strategy_audit.to_field_map(include_none=include_none))
        maps.append(self.extra_fields)

        merged = _merge_field_maps(*maps)
        ordered: dict[str, Any] = {}
        for field_name in FIELD_NAMES:
            if field_name in merged:
                ordered[field_name] = merged[field_name]
            elif include_none:
                ordered[field_name] = None
        return ordered

    def to_archive_row(self, *, include_none: bool = False) -> dict[str, Any]:
        return self.to_field_map(include_none=include_none)

    def partition_values(self) -> Mapping[str, Any]:
        row = self.to_field_map(include_none=False)
        partition_names = PRIMARY_PARTITIONS + SECONDARY_PARTITIONS
        return MappingProxyType({name: row.get(name) for name in partition_names})

    def get(self, field_name: str, default: Any = None) -> Any:
        row = self.to_field_map(include_none=False)
        return row.get(field_name, default)

    def require(self, field_name: str) -> Any:
        row = self.to_field_map(include_none=False)
        if field_name not in row:
            raise KeyError(f"{self.dataset.value}: missing required field {field_name!r}")
        return row[field_name]


@dataclass(frozen=True, slots=True)
class SourceAvailability:
    """
    Manifest-ready source availability summary.

    sources:
        bool flags, presence markers, or human-readable status strings keyed by source name.
    counts:
        optional numeric counters keyed by source name.
    """
    sources: Mapping[str, Any]
    counts: Mapping[str, int] = field(default_factory=lambda: MappingProxyType({}))
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "sources", _freeze_mapping(self.sources))
        object.__setattr__(self, "counts", _freeze_mapping(self.counts))
        object.__setattr__(self, "notes", _freeze_str_sequence(self.notes))
        if not self.sources:
            raise ValueError("SourceAvailability.sources must be non-empty")
        for key, value in self.sources.items():
            if not isinstance(key, str) or not key:
                raise ValueError("SourceAvailability source names must be non-empty strings")
            if not isinstance(value, (bool, str, int)):
                raise TypeError("SourceAvailability source values must be bool, str, or int")
        for key, value in self.counts.items():
            if not isinstance(key, str) or not key:
                raise ValueError("SourceAvailability count names must be non-empty strings")
            if not _is_non_bool_int(value):
                raise TypeError("SourceAvailability count values must be int")
        for note in self.notes:
            if not isinstance(note, str):
                raise TypeError("SourceAvailability notes must be strings")

    def to_dict(self) -> dict[str, Any]:
        return {
            "sources": dict(self.sources),
            "counts": dict(self.counts),
            "notes": list(self.notes),
        }


@dataclass(frozen=True, slots=True)
class IntegritySummary:
    """
    Manifest-ready integrity summary for one captured session.
    """
    total_records: int
    dataset_row_counts: Mapping[str, int]
    stale_tick_count: int = 0
    missing_depth_count: int = 0
    missing_oi_count: int = 0
    thin_book_count: int = 0
    integrity_flag_counts: Mapping[str, int] = field(default_factory=lambda: MappingProxyType({}))
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not _is_non_bool_int(self.total_records):
            raise TypeError("total_records must be int")
        object.__setattr__(self, "dataset_row_counts", _freeze_mapping(self.dataset_row_counts))
        object.__setattr__(self, "integrity_flag_counts", _freeze_mapping(self.integrity_flag_counts))
        object.__setattr__(self, "warnings", _freeze_str_sequence(self.warnings))
        object.__setattr__(self, "errors", _freeze_str_sequence(self.errors))

        for name in ("stale_tick_count", "missing_depth_count", "missing_oi_count", "thin_book_count"):
            value = getattr(self, name)
            if not _is_non_bool_int(value):
                raise TypeError(f"{name} must be int")

        for key, value in self.dataset_row_counts.items():
            if not isinstance(key, str) or not key:
                raise ValueError("dataset_row_counts keys must be non-empty strings")
            if not _is_non_bool_int(value):
                raise TypeError("dataset_row_counts values must be int")

        for key, value in self.integrity_flag_counts.items():
            if not isinstance(key, str) or not key:
                raise ValueError("integrity_flag_counts keys must be non-empty strings")
            if not _is_non_bool_int(value):
                raise TypeError("integrity_flag_counts values must be int")

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_records": self.total_records,
            "dataset_row_counts": dict(self.dataset_row_counts),
            "stale_tick_count": self.stale_tick_count,
            "missing_depth_count": self.missing_depth_count,
            "missing_oi_count": self.missing_oi_count,
            "thin_book_count": self.thin_book_count,
            "integrity_flag_counts": dict(self.integrity_flag_counts),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True, slots=True)
class CaptureArchiveOutput:
    """
    Description of one materialized archive output for a session.
    """
    dataset: CaptureDatasetName
    row_count: int
    file_name: str | None = None
    partition_columns: tuple[str, ...] = field(
        default_factory=lambda: tuple(PRIMARY_PARTITIONS + SECONDARY_PARTITIONS)
    )
    bytes_written: int | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not _is_non_bool_int(self.row_count):
            raise TypeError("row_count must be int")
        if self.file_name is not None and not isinstance(self.file_name, str):
            raise TypeError("file_name must be str or None")
        if self.bytes_written is not None and not _is_non_bool_int(self.bytes_written):
            raise TypeError("bytes_written must be int or None")
        object.__setattr__(self, "partition_columns", _freeze_partition_sequence(self.partition_columns))
        object.__setattr__(self, "notes", _freeze_str_sequence(self.notes))

        if not self.partition_columns:
            raise ValueError("partition_columns must be non-empty")
        for column in self.partition_columns:
            if column not in FIELD_SPECS_BY_NAME:
                raise KeyError(f"Unknown partition column: {column}")

        if self.file_name is None:
            object.__setattr__(self, "file_name", self.dataset.archive_filename)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset.value,
            "file_name": self.file_name,
            "row_count": self.row_count,
            "partition_columns": list(self.partition_columns),
            "bytes_written": self.bytes_written,
            "notes": list(self.notes),
        }


@dataclass(frozen=True, slots=True)
class CaptureSessionManifest:
    """
    Top-level session manifest for one research-capture archive session.
    """
    session_date: str
    source_availability: SourceAvailability
    integrity_summary: IntegritySummary
    archive_outputs: tuple[CaptureArchiveOutput, ...]
    created_at: str = field(default_factory=_utc_now_iso)
    schema_name: str = SCHEMA_NAME
    schema_version: str = SCHEMA_VERSION
    constitution_name: str = CONSTITUTION_NAME
    chapter: str = CHAPTER_NAME
    status: str = SCHEMA_STATUS
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.session_date, str) or not self.session_date:
            raise ValueError("session_date must be non-empty str")
        if not isinstance(self.created_at, str) or not self.created_at:
            raise ValueError("created_at must be non-empty str")
        if not isinstance(self.schema_name, str) or not self.schema_name:
            raise ValueError("schema_name must be non-empty str")
        if not isinstance(self.schema_version, str) or not self.schema_version:
            raise ValueError("schema_version must be non-empty str")
        if not isinstance(self.constitution_name, str) or not self.constitution_name:
            raise ValueError("constitution_name must be non-empty str")
        if not isinstance(self.chapter, str) or not self.chapter:
            raise ValueError("chapter must be non-empty str")
        if not isinstance(self.status, str) or not self.status:
            raise ValueError("status must be non-empty str")

        object.__setattr__(self, "archive_outputs", tuple(self.archive_outputs))
        object.__setattr__(self, "notes", _freeze_str_sequence(self.notes))

        if not self.archive_outputs:
            raise ValueError("archive_outputs must be non-empty")
        dataset_names = [output.dataset.value for output in self.archive_outputs]
        if len(dataset_names) != len(set(dataset_names)):
            raise ValueError("archive_outputs contain duplicate dataset entries")

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "constitution_name": self.constitution_name,
            "chapter": self.chapter,
            "session_date": self.session_date,
            "created_at": self.created_at,
            "status": self.status,
            "source_availability": self.source_availability.to_dict(),
            "integrity_summary": self.integrity_summary.to_dict(),
            "archive_outputs": [output.to_dict() for output in self.archive_outputs],
            "session_files": dict(SESSION_FILE_FILENAMES),
            "notes": list(self.notes),
        }
        missing = [key for key in MANIFEST_REQUIRED_KEYS if key not in payload]
        if missing:
            raise ValueError(f"manifest payload missing required keys: {missing}")
        return payload


def canonicalize_archive_row(values: Mapping[str, Any], *, include_none: bool = False) -> dict[str, Any]:
    """
    Return a canonical archive row ordered according to the frozen contract.
    """
    validated = _validate_bundle_fields(values=values)
    ordered: dict[str, Any] = {}
    for field_name in FIELD_NAMES:
        if field_name in validated:
            ordered[field_name] = validated[field_name]
        elif include_none:
            ordered[field_name] = None
    return ordered


__all__ = [
    "CaptureArchiveOutput",
    "CaptureDatasetName",
    "CaptureRecord",
    "CaptureSessionManifest",
    "ContextAnchors",
    "FieldBundle",
    "InstrumentIdentity",
    "IntegritySummary",
    "MarketSnapshot",
    "RuntimeAuditState",
    "SessionContext",
    "SourceAvailability",
    "StrategyAuditState",
    "TimingIdentity",
    "canonicalize_archive_row",
    "validate_capture_value_against_contract",
]