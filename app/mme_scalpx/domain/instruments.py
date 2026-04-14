# app/mme_scalpx/domain/instruments.py
"""
ScalpX MME - pure domain-layer instrument identity and deterministic runtime contract selection.

Role
----
This module is the sole domain owner of:
- instrument master loading
- contract metadata normalization
- current future discovery
- option expiry selection
- deterministic ATM / ATM+1 CE/PE selection
- runtime instrument-set construction

This module is NOT:
- a runtime service
- a daemon loop
- a heartbeat publisher
- a Redis owner
- a supervisor
- a composition root

Project-tree contract
---------------------
This file must remain at:
    app/mme_scalpx/domain/instruments.py

Ownership contract
------------------
This module owns only:
- instrument master loading
- deterministic contract selection
- runtime instrument-set construction

This module must not own:
- heartbeat loop
- service supervision
- Redis lifecycle
- runtime daemon loop

System-wide freeze rule
-----------------------
No downstream service may re-resolve:
- ATM
- ATM+1
- strike step
- tick size

outside this domain contract.

If selected instrument state must be published to Redis, that publication must
be performed by a thin caller/service boundary. This file must not be converted
into a runtime service for that purpose.

Replay / restart safety
-----------------------
Selection is deterministic and depends only on:
- explicit source metadata
- explicit `now`
- explicit `underlying_ltp`
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

LOGGER = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
EPSILON = Decimal("1e-12")
DEFAULT_SELECTION_VERSION = "mme-instruments-v1"


# =============================================================================
# Exceptions
# =============================================================================


class InstrumentsError(RuntimeError):
    """Base error for instrument metadata failures."""


class InstrumentLoadError(InstrumentsError):
    """Raised when the instrument master source cannot be loaded."""


class InstrumentValidationError(InstrumentsError):
    """Raised when normalized contract metadata is invalid."""


class InstrumentNotFoundError(InstrumentsError):
    """Raised when a required contract cannot be resolved."""


class MetadataStaleError(InstrumentsError):
    """Raised when metadata freshness rules are violated."""


class AmbiguousInstrumentError(InstrumentsError):
    """Raised when multiple equally valid contracts match a deterministic request."""


# =============================================================================
# Enums
# =============================================================================


class InstrumentKind(str, Enum):
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    SPOT = "SPOT"
    UNKNOWN = "UNKNOWN"


class OptionRight(str, Enum):
    CALL = "CE"
    PUT = "PE"


class Exchange(str, Enum):
    NFO = "NFO"
    NSE = "NSE"
    BFO = "BFO"
    UNKNOWN = "UNKNOWN"


class SourceFormat(str, Enum):
    CSV = "csv"
    JSON = "json"


# =============================================================================
# Utility helpers
# =============================================================================


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_path(value: str | Path) -> Path:
    path = value if isinstance(value, Path) else Path(value)
    return path.expanduser().resolve()


def _normalize_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_upper(value: Any) -> str:
    return _normalize_str(value).upper()


def _normalize_lower(value: Any) -> str:
    return _normalize_str(value).lower()


def _safe_int(value: Any, *, field_name: str, default: int | None = None) -> int:
    text = _normalize_str(value)
    if text == "":
        if default is None:
            raise InstrumentValidationError(f"missing integer field: {field_name}")
        return default
    try:
        return int(Decimal(text))
    except (InvalidOperation, ValueError) as exc:
        raise InstrumentValidationError(
            f"invalid integer field {field_name!r}: {value!r}"
        ) from exc


def _to_decimal(
    value: Any,
    *,
    field_name: str,
    allow_empty: bool = False,
) -> Decimal | None:
    text = _normalize_str(value)
    if text == "":
        if allow_empty:
            return None
        raise InstrumentValidationError(f"missing decimal field: {field_name}")
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise InstrumentValidationError(
            f"invalid decimal field {field_name!r}: {value!r}"
        ) from exc


def _to_date(
    value: Any,
    *,
    field_name: str,
    allow_empty: bool = False,
) -> date | None:
    text = _normalize_str(value)
    if text == "":
        if allow_empty:
            return None
        raise InstrumentValidationError(f"missing date field: {field_name}")

    patterns = (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    )
    for pat in patterns:
        try:
            return datetime.strptime(text, pat).date()
        except ValueError:
            continue

    if len(text) == 8 and text.isdigit():
        try:
            return datetime.strptime(text, "%Y%m%d").date()
        except ValueError:
            pass

    raise InstrumentValidationError(f"invalid date field {field_name!r}: {value!r}")


def _decimal_is_positive(value: Decimal | None) -> bool:
    return value is not None and value > EPSILON


def _quantize(value: Decimal, tick: Decimal) -> Decimal:
    if tick <= EPSILON:
        raise InstrumentValidationError(f"tick_size must be positive, got {tick}")
    units = (value / tick).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return units * tick


def _is_tick_aligned(value: Decimal, tick: Decimal) -> bool:
    if tick <= EPSILON:
        return False
    quantized = _quantize(value, tick)
    tolerance = max(EPSILON, tick / Decimal("1000"))
    return abs(quantized - value) <= tolerance


def _month_end(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1) - timedelta(days=1)
    return date(d.year, d.month + 1, 1) - timedelta(days=1)


def _is_last_thursday(d: date) -> bool:
    if d.weekday() != 3:
        return False
    return d + timedelta(days=7) > _month_end(d)


def _is_probable_weekly_expiry(d: date) -> bool:
    return d.weekday() == 3 and not _is_last_thursday(d)


def _is_probable_monthly_expiry(d: date) -> bool:
    return _is_last_thursday(d)


def _round_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= EPSILON:
        raise InstrumentValidationError(f"invalid strike_step: {step}")
    units = (value / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return units * step


def _infer_strike_step(strikes: Sequence[Decimal]) -> Decimal:
    unique = sorted({x for x in strikes if x is not None})
    if len(unique) < 2:
        raise InstrumentValidationError("cannot infer strike_step from fewer than 2 strikes")

    diffs: list[Decimal] = []
    prev = unique[0]
    for cur in unique[1:]:
        diff = cur - prev
        if diff > EPSILON:
            diffs.append(diff)
        prev = cur

    if not diffs:
        raise InstrumentValidationError("cannot infer positive strike_step from chain")

    step = min(diffs)
    if step <= EPSILON:
        raise InstrumentValidationError(f"invalid inferred strike_step: {step}")
    return step


def _iter_json_records(payload: Any) -> Iterator[Mapping[str, Any]]:
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, Mapping):
                yield item
        return

    if isinstance(payload, Mapping):
        for key in ("data", "instruments", "records", "items", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, Mapping):
                        yield item
                return
        yield payload
        return

    raise InstrumentLoadError(f"unsupported JSON payload type: {type(payload)!r}")


# =============================================================================
# Data contracts
# =============================================================================


@dataclass(frozen=True, slots=True)
class SourceMeta:
    source_path: Path
    source_format: SourceFormat
    loaded_at: datetime
    source_updated_at: datetime | None = None
    record_count: int = 0


@dataclass(frozen=True, slots=True)
class InstrumentConfig:
    """
    Broker-agnostic configuration for instrument-master loading and selection.
    """

    source_path: Path | str
    source_format: str | SourceFormat = SourceFormat.CSV

    underlying_symbol: str = "NIFTY"
    future_root: str = "NIFTY"
    option_root: str = "NIFTY"

    selection_version: str = DEFAULT_SELECTION_VERSION

    freshness_max_age: timedelta = timedelta(days=7)
    option_expiry_days_guard: int = 9

    require_weekly_options: bool = True
    allow_monthly_fallback: bool = True

    strike_step_override: Decimal | None = None

    market_close_ist: time = time(15, 30)

    field_map: Mapping[str, str] = field(default_factory=dict)

    allowed_derivative_exchanges: tuple[Exchange, ...] = (Exchange.NFO, Exchange.BFO)

    enforce_tick_alignment: bool = True

    def __post_init__(self) -> None:
        if not _normalize_upper(self.underlying_symbol):
            raise InstrumentValidationError("underlying_symbol must be non-empty")
        if not _normalize_upper(self.future_root):
            raise InstrumentValidationError("future_root must be non-empty")
        if not _normalize_upper(self.option_root):
            raise InstrumentValidationError("option_root must be non-empty")
        if self.freshness_max_age <= timedelta(0):
            raise InstrumentValidationError("freshness_max_age must be positive")
        if self.option_expiry_days_guard < 0:
            raise InstrumentValidationError("option_expiry_days_guard must be >= 0")
        if self.strike_step_override is not None and self.strike_step_override <= EPSILON:
            raise InstrumentValidationError("strike_step_override must be positive")
        if not self.allowed_derivative_exchanges:
            raise InstrumentValidationError("allowed_derivative_exchanges must be non-empty")

    def normalized_source_format(self) -> SourceFormat:
        if isinstance(self.source_format, SourceFormat):
            return self.source_format
        text = _normalize_lower(self.source_format)
        if text == "csv":
            return SourceFormat.CSV
        if text == "json":
            return SourceFormat.JSON
        raise InstrumentValidationError(f"unsupported source_format: {self.source_format!r}")

    @property
    def source_path_resolved(self) -> Path:
        return _ensure_path(self.source_path)


@dataclass(frozen=True, slots=True)
class ContractMetadata:
    """
    Canonical instrument identity and static contract metadata.
    """

    instrument_token: str
    tradingsymbol: str
    exchange: Exchange
    segment: str

    underlying: str
    kind: InstrumentKind

    expiry: date | None
    strike: Decimal | None
    option_right: OptionRight | None

    tick_size: Decimal
    lot_size: int

    broker: str
    isin: str | None = None
    display_name: str | None = None
    series: str | None = None

    raw_symbol: str | None = None
    source_row_index: int | None = None

    def __post_init__(self) -> None:
        if not self.instrument_token:
            raise InstrumentValidationError("instrument_token must be non-empty")
        if not self.tradingsymbol:
            raise InstrumentValidationError("tradingsymbol must be non-empty")
        if not self.underlying:
            raise InstrumentValidationError(
                f"underlying must be non-empty for {self.tradingsymbol!r}"
            )
        if not _decimal_is_positive(self.tick_size):
            raise InstrumentValidationError(
                f"tick_size must be positive for {self.tradingsymbol!r}: {self.tick_size!r}"
            )
        if self.lot_size <= 0:
            raise InstrumentValidationError(
                f"lot_size must be positive for {self.tradingsymbol!r}: {self.lot_size!r}"
            )

        if self.kind is InstrumentKind.FUTURE:
            if self.expiry is None:
                raise InstrumentValidationError(
                    f"future contract missing expiry: {self.tradingsymbol!r}"
                )
            if self.option_right is not None:
                raise InstrumentValidationError(
                    f"future cannot have option_right: {self.tradingsymbol!r}"
                )

        if self.kind is InstrumentKind.OPTION:
            if self.expiry is None:
                raise InstrumentValidationError(
                    f"option contract missing expiry: {self.tradingsymbol!r}"
                )
            if self.strike is None or self.strike <= EPSILON:
                raise InstrumentValidationError(
                    f"option contract missing/invalid strike: {self.tradingsymbol!r}"
                )
            if self.option_right is None:
                raise InstrumentValidationError(
                    f"option contract missing option_right: {self.tradingsymbol!r}"
                )

    @property
    def is_weekly_option(self) -> bool:
        return (
            self.kind is InstrumentKind.OPTION
            and self.expiry is not None
            and _is_probable_weekly_expiry(self.expiry)
        )

    @property
    def is_monthly_option(self) -> bool:
        return (
            self.kind is InstrumentKind.OPTION
            and self.expiry is not None
            and _is_probable_monthly_expiry(self.expiry)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "instrument_token": self.instrument_token,
            "tradingsymbol": self.tradingsymbol,
            "exchange": self.exchange.value,
            "segment": self.segment,
            "underlying": self.underlying,
            "kind": self.kind.value,
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "strike": str(self.strike) if self.strike is not None else None,
            "option_right": self.option_right.value if self.option_right else None,
            "tick_size": str(self.tick_size),
            "lot_size": self.lot_size,
            "broker": self.broker,
            "isin": self.isin,
            "display_name": self.display_name,
            "series": self.series,
            "raw_symbol": self.raw_symbol,
            "source_row_index": self.source_row_index,
        }


@dataclass(frozen=True, slots=True)
class SelectedOptionPair:
    """
    Deterministic ATM / ATM+1 selection for one side.
    """

    side: OptionRight
    expiry: date
    strike_step: Decimal
    underlying_reference: Decimal

    atm: ContractMetadata
    atm1: ContractMetadata

    def __post_init__(self) -> None:
        if self.atm.kind is not InstrumentKind.OPTION:
            raise InstrumentValidationError("atm contract must be an option")
        if self.atm1.kind is not InstrumentKind.OPTION:
            raise InstrumentValidationError("atm1 contract must be an option")
        if self.atm.option_right is not self.side:
            raise InstrumentValidationError("atm option_right does not match side")
        if self.atm1.option_right is not self.side:
            raise InstrumentValidationError("atm1 option_right does not match side")
        if self.atm.expiry != self.expiry or self.atm1.expiry != self.expiry:
            raise InstrumentValidationError("pair expiry mismatch")
        if self.atm.strike is None or self.atm1.strike is None:
            raise InstrumentValidationError("pair strikes must be present")

        if self.side is OptionRight.CALL:
            expected = self.atm.strike + self.strike_step
            if abs(self.atm1.strike - expected) > EPSILON:
                raise InstrumentValidationError(
                    f"CE ATM+1 mismatch: expected={expected} actual={self.atm1.strike}"
                )
        elif self.side is OptionRight.PUT:
            expected = self.atm.strike - self.strike_step
            if abs(self.atm1.strike - expected) > EPSILON:
                raise InstrumentValidationError(
                    f"PE ATM+1 mismatch: expected={expected} actual={self.atm1.strike}"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "side": self.side.value,
            "expiry": self.expiry.isoformat(),
            "strike_step": str(self.strike_step),
            "underlying_reference": str(self.underlying_reference),
            "atm": self.atm.to_dict(),
            "atm1": self.atm1.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class RuntimeInstrumentSet:
    """
    Exact active contract-set for downstream runtime services.

    This is the only valid runtime contract-selection output of this module.
    Any Redis publication of this state must happen outside this file.
    """

    selection_version: str
    generated_at: datetime
    source_meta: SourceMeta

    underlying_symbol: str
    underlying_reference: Decimal

    current_future: ContractMetadata

    ce_atm: ContractMetadata
    ce_atm1: ContractMetadata

    pe_atm: ContractMetadata
    pe_atm1: ContractMetadata

    option_expiry: date
    strike_step: Decimal

    def __post_init__(self) -> None:
        if self.current_future.kind is not InstrumentKind.FUTURE:
            raise InstrumentValidationError("current_future must be a future contract")
        if self.underlying_reference <= EPSILON:
            raise InstrumentValidationError("underlying_reference must be positive")
        if self.strike_step <= EPSILON:
            raise InstrumentValidationError("strike_step must be positive")

        option_contracts = (self.ce_atm, self.ce_atm1, self.pe_atm, self.pe_atm1)
        for contract in option_contracts:
            if contract.kind is not InstrumentKind.OPTION:
                raise InstrumentValidationError(
                    f"runtime option contract is not an option: {contract.tradingsymbol}"
                )
            if contract.expiry != self.option_expiry:
                raise InstrumentValidationError(
                    f"runtime option expiry mismatch for {contract.tradingsymbol}"
                )
            if contract.underlying != self.underlying_symbol.upper():
                raise InstrumentValidationError(
                    f"runtime underlying mismatch for {contract.tradingsymbol}: "
                    f"{contract.underlying} != {self.underlying_symbol.upper()}"
                )

        if self.ce_atm.option_right is not OptionRight.CALL:
            raise InstrumentValidationError("ce_atm must be CE")
        if self.ce_atm1.option_right is not OptionRight.CALL:
            raise InstrumentValidationError("ce_atm1 must be CE")
        if self.pe_atm.option_right is not OptionRight.PUT:
            raise InstrumentValidationError("pe_atm must be PE")
        if self.pe_atm1.option_right is not OptionRight.PUT:
            raise InstrumentValidationError("pe_atm1 must be PE")

        if self.ce_atm.strike is None or self.ce_atm1.strike is None:
            raise InstrumentValidationError("CE strikes must be present")
        if self.pe_atm.strike is None or self.pe_atm1.strike is None:
            raise InstrumentValidationError("PE strikes must be present")

        if abs((self.ce_atm1.strike - self.ce_atm.strike) - self.strike_step) > EPSILON:
            raise InstrumentValidationError("CE strike-step mismatch")
        if abs((self.pe_atm.strike - self.pe_atm1.strike) - self.strike_step) > EPSILON:
            raise InstrumentValidationError("PE strike-step mismatch")

        self._assert_runtime_consistency()

    def _assert_runtime_consistency(self) -> None:
        ce_lot_sizes = {self.ce_atm.lot_size, self.ce_atm1.lot_size}
        pe_lot_sizes = {self.pe_atm.lot_size, self.pe_atm1.lot_size}
        if len(ce_lot_sizes) != 1:
            raise InstrumentValidationError("CE lot_size mismatch inside runtime set")
        if len(pe_lot_sizes) != 1:
            raise InstrumentValidationError("PE lot_size mismatch inside runtime set")

        ce_ticks = {self.ce_atm.tick_size, self.ce_atm1.tick_size}
        pe_ticks = {self.pe_atm.tick_size, self.pe_atm1.tick_size}
        if len(ce_ticks) != 1:
            raise InstrumentValidationError("CE tick_size mismatch inside runtime set")
        if len(pe_ticks) != 1:
            raise InstrumentValidationError("PE tick_size mismatch inside runtime set")

    @property
    def ce_pair(self) -> SelectedOptionPair:
        return SelectedOptionPair(
            side=OptionRight.CALL,
            expiry=self.option_expiry,
            strike_step=self.strike_step,
            underlying_reference=self.underlying_reference,
            atm=self.ce_atm,
            atm1=self.ce_atm1,
        )

    @property
    def pe_pair(self) -> SelectedOptionPair:
        return SelectedOptionPair(
            side=OptionRight.PUT,
            expiry=self.option_expiry,
            strike_step=self.strike_step,
            underlying_reference=self.underlying_reference,
            atm=self.pe_atm,
            atm1=self.pe_atm1,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selection_version": self.selection_version,
            "generated_at": self.generated_at.astimezone(timezone.utc).isoformat(),
            "source_meta": {
                "source_path": str(self.source_meta.source_path),
                "source_format": self.source_meta.source_format.value,
                "loaded_at": self.source_meta.loaded_at.isoformat(),
                "source_updated_at": (
                    self.source_meta.source_updated_at.isoformat()
                    if self.source_meta.source_updated_at
                    else None
                ),
                "record_count": self.source_meta.record_count,
            },
            "underlying_symbol": self.underlying_symbol,
            "underlying_reference": str(self.underlying_reference),
            "current_future": self.current_future.to_dict(),
            "ce_atm": self.ce_atm.to_dict(),
            "ce_atm1": self.ce_atm1.to_dict(),
            "pe_atm": self.pe_atm.to_dict(),
            "pe_atm1": self.pe_atm1.to_dict(),
            "option_expiry": self.option_expiry.isoformat(),
            "strike_step": str(self.strike_step),
        }


# =============================================================================
# Normalization helpers
# =============================================================================


def _canonical_key_map(config: InstrumentConfig) -> dict[str, tuple[str, ...]]:
    explicit = {k: v for k, v in config.field_map.items()}

    aliases: dict[str, tuple[str, ...]] = {
        "instrument_token": (
            explicit.get("instrument_token", ""),
            "instrument_token",
            "token",
            "exchange_token",
            "instrument_key",
            "instrument_key_id",
        ),
        "tradingsymbol": (
            explicit.get("tradingsymbol", ""),
            "tradingsymbol",
            "symbol",
            "trading_symbol",
            "name",
            "scrip_name",
        ),
        "exchange": (
            explicit.get("exchange", ""),
            "exchange",
            "exch",
            "exchange_segment",
        ),
        "segment": (
            explicit.get("segment", ""),
            "segment",
            "instrument_type",
            "segment_name",
            "exchange_segment",
        ),
        "underlying": (
            explicit.get("underlying", ""),
            "underlying",
            "underlying_symbol",
            "name",
            "symbol_name",
        ),
        "expiry": (
            explicit.get("expiry", ""),
            "expiry",
            "expiry_date",
            "exp_date",
        ),
        "strike": (
            explicit.get("strike", ""),
            "strike",
            "strike_price",
            "strikeprice",
        ),
        "option_right": (
            explicit.get("option_right", ""),
            "option_type",
            "right",
            "cp_type",
        ),
        "tick_size": (
            explicit.get("tick_size", ""),
            "tick_size",
            "ticksize",
            "minimum_tick",
        ),
        "lot_size": (
            explicit.get("lot_size", ""),
            "lot_size",
            "lotsize",
            "qty",
            "market_lot",
        ),
        "broker": (
            explicit.get("broker", ""),
            "broker",
            "source",
            "vendor",
        ),
        "isin": (
            explicit.get("isin", ""),
            "isin",
        ),
        "display_name": (
            explicit.get("display_name", ""),
            "display_name",
            "company_name",
            "description",
            "display",
        ),
        "series": (
            explicit.get("series", ""),
            "series",
        ),
    }

    cleaned: dict[str, tuple[str, ...]] = {}
    for key, vals in aliases.items():
        cleaned[key] = tuple(v for v in vals if v)
    return cleaned


def _pick_field(row: Mapping[str, Any], names: Sequence[str]) -> Any:
    if not row:
        return None

    for name in names:
        if name in row:
            return row[name]

    upper_map = {_normalize_upper(k): k for k in row.keys()}
    for name in names:
        real = upper_map.get(_normalize_upper(name))
        if real is not None:
            return row[real]

    return None


def _normalize_exchange(raw: Any) -> Exchange:
    text = _normalize_upper(raw)
    if text.startswith("NFO"):
        return Exchange.NFO
    if text.startswith("NSE"):
        return Exchange.NSE
    if text.startswith("BFO"):
        return Exchange.BFO
    return Exchange.UNKNOWN


def _normalize_option_right(raw: Any) -> OptionRight | None:
    text = _normalize_upper(raw)
    if text in {"CE", "CALL", "C"}:
        return OptionRight.CALL
    if text in {"PE", "PUT", "P"}:
        return OptionRight.PUT
    return None


def _infer_kind(
    *,
    segment_text: str,
    option_right: OptionRight | None,
    strike: Decimal | None,
    expiry: date | None,
) -> InstrumentKind:
    seg = _normalize_upper(segment_text)
    if option_right is not None or strike is not None:
        return InstrumentKind.OPTION
    if "FUT" in seg or "FUTURE" in seg:
        return InstrumentKind.FUTURE
    if expiry is not None and ("OPT" not in seg) and ("EQ" not in seg):
        return InstrumentKind.FUTURE
    if "EQ" in seg or "SPOT" in seg or "INDEX" in seg:
        return InstrumentKind.SPOT
    return InstrumentKind.UNKNOWN


def _row_to_contract(
    row: Mapping[str, Any],
    *,
    row_index: int,
    config: InstrumentConfig,
    key_map: Mapping[str, Sequence[str]],
) -> ContractMetadata:
    token_raw = _pick_field(row, key_map["instrument_token"])
    symbol_raw = _pick_field(row, key_map["tradingsymbol"])
    exchange_raw = _pick_field(row, key_map["exchange"])
    segment_raw = _pick_field(row, key_map["segment"])
    underlying_raw = _pick_field(row, key_map["underlying"])
    expiry_raw = _pick_field(row, key_map["expiry"])
    strike_raw = _pick_field(row, key_map["strike"])
    option_right_raw = _pick_field(row, key_map["option_right"])
    tick_size_raw = _pick_field(row, key_map["tick_size"])
    lot_size_raw = _pick_field(row, key_map["lot_size"])
    broker_raw = _pick_field(row, key_map["broker"])
    isin_raw = _pick_field(row, key_map["isin"])
    display_name_raw = _pick_field(row, key_map["display_name"])
    series_raw = _pick_field(row, key_map["series"])

    instrument_token = _normalize_str(token_raw)
    tradingsymbol = _normalize_upper(symbol_raw)
    exchange = _normalize_exchange(exchange_raw)
    segment = _normalize_upper(segment_raw)
    underlying = _normalize_upper(underlying_raw) or _normalize_upper(config.underlying_symbol)

    expiry = _to_date(expiry_raw, field_name="expiry", allow_empty=True)
    strike = _to_decimal(strike_raw, field_name="strike", allow_empty=True)
    option_right = _normalize_option_right(option_right_raw)

    tick_size = _to_decimal(tick_size_raw, field_name="tick_size", allow_empty=False)
    assert tick_size is not None
    lot_size = _safe_int(lot_size_raw, field_name="lot_size", default=1)

    broker = _normalize_lower(broker_raw) or "unknown"
    isin = _normalize_str(isin_raw) or None
    display_name = _normalize_str(display_name_raw) or None
    series = _normalize_str(series_raw) or None

    kind = _infer_kind(
        segment_text=segment,
        option_right=option_right,
        strike=strike,
        expiry=expiry,
    )
    if kind is InstrumentKind.UNKNOWN:
        raise InstrumentValidationError(
            f"could not infer kind for {tradingsymbol!r} row={row_index}"
        )

    if config.enforce_tick_alignment and strike is not None and kind is InstrumentKind.OPTION:
        if not _is_tick_aligned(strike, tick_size):
            raise InstrumentValidationError(
                f"strike not aligned to tick_size for {tradingsymbol!r}: "
                f"strike={strike} tick_size={tick_size}"
            )

    return ContractMetadata(
        instrument_token=instrument_token,
        tradingsymbol=tradingsymbol,
        exchange=exchange,
        segment=segment,
        underlying=underlying,
        kind=kind,
        expiry=expiry,
        strike=strike,
        option_right=option_right,
        tick_size=tick_size,
        lot_size=lot_size,
        broker=broker,
        isin=isin,
        display_name=display_name,
        series=series,
        raw_symbol=_normalize_str(symbol_raw) or None,
        source_row_index=row_index,
    )


# =============================================================================
# Source loaders
# =============================================================================


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]
    except FileNotFoundError as exc:
        raise InstrumentLoadError(f"instrument CSV not found: {path}") from exc
    except OSError as exc:
        raise InstrumentLoadError(f"failed reading instrument CSV: {path}") from exc


def _load_json_rows(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise InstrumentLoadError(f"instrument JSON not found: {path}") from exc
    except OSError as exc:
        raise InstrumentLoadError(f"failed reading instrument JSON: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InstrumentLoadError(f"invalid instrument JSON: {path}") from exc

    return [dict(row) for row in _iter_json_records(payload)]


def _load_source_rows(path: Path, source_format: SourceFormat) -> list[dict[str, Any]]:
    if source_format is SourceFormat.CSV:
        return _load_csv_rows(path)
    if source_format is SourceFormat.JSON:
        return _load_json_rows(path)
    raise InstrumentLoadError(f"unsupported source_format: {source_format!r}")


# =============================================================================
# Repository
# =============================================================================


@dataclass(slots=True)
class InstrumentRepository:
    """
    Deterministic in-memory owner of normalized contract metadata and selection.

    This is not a runtime service and must not be supervised as one.
    """

    config: InstrumentConfig
    source_meta: SourceMeta
    _contracts: tuple[ContractMetadata, ...]
    _futures: tuple[ContractMetadata, ...]
    _calls: tuple[ContractMetadata, ...]
    _puts: tuple[ContractMetadata, ...]
    _loaded_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not self._contracts:
            raise InstrumentLoadError("repository initialized with no contracts")
        if not self._futures:
            raise InstrumentLoadError("repository initialized with no futures")
        if not self._calls:
            raise InstrumentLoadError("repository initialized with no call options")
        if not self._puts:
            raise InstrumentLoadError("repository initialized with no put options")

    def assert_fresh(self, *, now: datetime | None = None) -> None:
        current = now or _utc_now()
        updated_at = self.source_meta.source_updated_at or self.source_meta.loaded_at
        age = current - updated_at
        if age > self.config.freshness_max_age:
            raise MetadataStaleError(
                f"instrument metadata stale: age={age} "
                f"max_age={self.config.freshness_max_age} "
                f"path={self.source_meta.source_path}"
            )

    @property
    def contracts(self) -> tuple[ContractMetadata, ...]:
        return self._contracts

    @property
    def futures(self) -> tuple[ContractMetadata, ...]:
        return self._futures

    @property
    def calls(self) -> tuple[ContractMetadata, ...]:
        return self._calls

    @property
    def puts(self) -> tuple[ContractMetadata, ...]:
        return self._puts

    def get_current_future(self, *, now: datetime | None = None) -> ContractMetadata:
        self.assert_fresh(now=now)
        today = (now or _utc_now()).date()
        candidates = [x for x in self._futures if x.expiry is not None and x.expiry >= today]
        if not candidates:
            raise InstrumentNotFoundError(
                f"no current future found for today or later: {today.isoformat()}"
            )
        return min(candidates, key=lambda x: (x.expiry or date.max, x.tradingsymbol))

    def _eligible_option_expiries(self, *, now: datetime | None = None) -> list[date]:
        current = now or _utc_now()
        today = current.date()

        expiries = sorted(
            {
                x.expiry
                for x in (*self._calls, *self._puts)
                if x.expiry is not None and x.expiry >= today
            }
        )
        if not expiries:
            raise InstrumentNotFoundError("no live option expiries found")

        current_ist = current.astimezone(IST)
        if current_ist.time() >= self.config.market_close_ist:
            expiries = [exp for exp in expiries if exp > today]
            if not expiries:
                raise InstrumentNotFoundError(
                    "no option expiries available after market-close selection rule"
                )

        guard = self.config.option_expiry_days_guard
        guarded = [exp for exp in expiries if (exp - today).days <= guard]
        selected_pool = guarded if guarded else expiries

        if self.config.require_weekly_options:
            weeklies = [exp for exp in selected_pool if _is_probable_weekly_expiry(exp)]
            if weeklies:
                return weeklies
            if not self.config.allow_monthly_fallback:
                raise InstrumentNotFoundError(
                    "no weekly option expiries found within eligible range"
                )

        return selected_pool

    def get_option_expiry(self, *, now: datetime | None = None) -> date:
        self.assert_fresh(now=now)
        expiries = self._eligible_option_expiries(now=now)
        return min(expiries)

    def _chain_for_expiry(self, *, expiry: date, side: OptionRight) -> list[ContractMetadata]:
        pool = self._calls if side is OptionRight.CALL else self._puts
        chain = [x for x in pool if x.expiry == expiry and x.strike is not None]
        if not chain:
            raise InstrumentNotFoundError(
                f"no option chain found for expiry={expiry.isoformat()} side={side.value}"
            )
        return sorted(chain, key=lambda x: (x.strike or Decimal("0"), x.tradingsymbol))

    def _strike_step_for_expiry(self, *, expiry: date) -> Decimal:
        if self.config.strike_step_override is not None:
            return self.config.strike_step_override
        strikes = [
            x.strike
            for x in (*self._calls, *self._puts)
            if x.expiry == expiry and x.strike is not None
        ]
        return _infer_strike_step([x for x in strikes if x is not None])

    @staticmethod
    def _require_unique_contract(
        chain: Sequence[ContractMetadata],
        *,
        strike: Decimal,
        side: OptionRight,
        label: str,
    ) -> ContractMetadata:
        matches = [
            x
            for x in chain
            if x.strike is not None
            and abs(x.strike - strike) <= EPSILON
            and x.option_right is side
        ]
        if not matches:
            raise InstrumentNotFoundError(
                f"{label}: no contract found for strike={strike} side={side.value}"
            )
        if len(matches) > 1:
            raise AmbiguousInstrumentError(
                f"{label}: multiple contracts for strike={strike} side={side.value}: "
                f"{[x.tradingsymbol for x in matches]}"
            )
        return matches[0]

    def _resolve_call_pair(
        self,
        *,
        underlying_ltp: Decimal,
        expiry: date,
        strike_step: Decimal,
    ) -> SelectedOptionPair:
        chain = self._chain_for_expiry(expiry=expiry, side=OptionRight.CALL)

        atm = _round_to_step(underlying_ltp, strike_step)
        atm1 = atm + strike_step

        ce_atm = self._require_unique_contract(
            chain,
            strike=atm,
            side=OptionRight.CALL,
            label="CE ATM",
        )
        ce_atm1 = self._require_unique_contract(
            chain,
            strike=atm1,
            side=OptionRight.CALL,
            label="CE ATM+1",
        )

        return SelectedOptionPair(
            side=OptionRight.CALL,
            expiry=expiry,
            strike_step=strike_step,
            underlying_reference=underlying_ltp,
            atm=ce_atm,
            atm1=ce_atm1,
        )

    def _resolve_put_pair(
        self,
        *,
        underlying_ltp: Decimal,
        expiry: date,
        strike_step: Decimal,
    ) -> SelectedOptionPair:
        chain = self._chain_for_expiry(expiry=expiry, side=OptionRight.PUT)

        atm = _round_to_step(underlying_ltp, strike_step)
        atm1 = atm - strike_step

        pe_atm = self._require_unique_contract(
            chain,
            strike=atm,
            side=OptionRight.PUT,
            label="PE ATM",
        )
        pe_atm1 = self._require_unique_contract(
            chain,
            strike=atm1,
            side=OptionRight.PUT,
            label="PE ATM+1",
        )

        return SelectedOptionPair(
            side=OptionRight.PUT,
            expiry=expiry,
            strike_step=strike_step,
            underlying_reference=underlying_ltp,
            atm=pe_atm,
            atm1=pe_atm1,
        )

    def resolve_option_pair(
        self,
        *,
        side: OptionRight,
        underlying_ltp: Decimal,
        now: datetime | None = None,
    ) -> SelectedOptionPair:
        self.assert_fresh(now=now)
        if underlying_ltp <= EPSILON:
            raise InstrumentValidationError(f"invalid underlying_ltp: {underlying_ltp!r}")

        expiry = self.get_option_expiry(now=now)
        strike_step = self._strike_step_for_expiry(expiry=expiry)

        if side is OptionRight.CALL:
            return self._resolve_call_pair(
                underlying_ltp=underlying_ltp,
                expiry=expiry,
                strike_step=strike_step,
            )
        if side is OptionRight.PUT:
            return self._resolve_put_pair(
                underlying_ltp=underlying_ltp,
                expiry=expiry,
                strike_step=strike_step,
            )

        raise InstrumentValidationError(f"unsupported side: {side!r}")

    def build_runtime_set(
        self,
        *,
        underlying_ltp: Decimal,
        now: datetime | None = None,
    ) -> RuntimeInstrumentSet:
        current = now or _utc_now()
        self.assert_fresh(now=current)

        future = self.get_current_future(now=current)
        call_pair = self.resolve_option_pair(
            side=OptionRight.CALL,
            underlying_ltp=underlying_ltp,
            now=current,
        )
        put_pair = self.resolve_option_pair(
            side=OptionRight.PUT,
            underlying_ltp=underlying_ltp,
            now=current,
        )

        if call_pair.expiry != put_pair.expiry:
            raise AmbiguousInstrumentError(
                f"call/put expiries differ: CE={call_pair.expiry} PE={put_pair.expiry}"
            )
        if call_pair.strike_step != put_pair.strike_step:
            raise AmbiguousInstrumentError(
                f"call/put strike_step differs: CE={call_pair.strike_step} "
                f"PE={put_pair.strike_step}"
            )

        return RuntimeInstrumentSet(
            selection_version=self.config.selection_version,
            generated_at=current,
            source_meta=self.source_meta,
            underlying_symbol=self.config.underlying_symbol.upper(),
            underlying_reference=underlying_ltp,
            current_future=future,
            ce_atm=call_pair.atm,
            ce_atm1=call_pair.atm1,
            pe_atm=put_pair.atm,
            pe_atm1=put_pair.atm1,
            option_expiry=call_pair.expiry,
            strike_step=call_pair.strike_step,
        )


# =============================================================================
# Loader
# =============================================================================


def load_instrument_repository(
    *,
    config: InstrumentConfig,
    logger: logging.Logger | None = None,
    now: datetime | None = None,
) -> InstrumentRepository:
    """
    Load and normalize a broker instrument master into a deterministic repository.

    This function constructs domain state only. It does not register services,
    publish heartbeats, or start runtime loops.
    """

    log = logger or LOGGER
    current = now or _utc_now()
    source_path = config.source_path_resolved
    source_format = config.normalized_source_format()

    rows = _load_source_rows(source_path, source_format)
    if not rows:
        raise InstrumentLoadError(f"instrument source is empty: {source_path}")

    try:
        source_updated_at = datetime.fromtimestamp(
            source_path.stat().st_mtime,
            tz=timezone.utc,
        )
    except OSError:
        source_updated_at = None

    key_map = _canonical_key_map(config)

    contracts: list[ContractMetadata] = []
    errors: list[str] = []

    for idx, row in enumerate(rows, start=1):
        try:
            contract = _row_to_contract(
                row,
                row_index=idx,
                config=config,
                key_map=key_map,
            )
        except InstrumentValidationError as exc:
            errors.append(f"row={idx}: {exc}")
            continue

        if contract.underlying != config.underlying_symbol.upper():
            root_hit = (
                contract.tradingsymbol.startswith(config.future_root.upper())
                or contract.tradingsymbol.startswith(config.option_root.upper())
            )
            if not root_hit:
                continue

        if (
            contract.kind in {InstrumentKind.FUTURE, InstrumentKind.OPTION}
            and contract.exchange not in config.allowed_derivative_exchanges
        ):
            continue

        if contract.kind is InstrumentKind.FUTURE:
            if not contract.tradingsymbol.startswith(config.future_root.upper()):
                continue
        elif contract.kind is InstrumentKind.OPTION:
            if not contract.tradingsymbol.startswith(config.option_root.upper()):
                continue
        else:
            continue

        contracts.append(contract)

    if not contracts:
        sample = "; ".join(errors[:5])
        raise InstrumentLoadError(
            f"no usable contracts after normalization from {source_path}. "
            f"sample_errors={sample}"
        )

    futures = sorted(
        [x for x in contracts if x.kind is InstrumentKind.FUTURE],
        key=lambda x: (x.expiry or date.max, x.tradingsymbol),
    )
    calls = sorted(
        [
            x
            for x in contracts
            if x.kind is InstrumentKind.OPTION and x.option_right is OptionRight.CALL
        ],
        key=lambda x: (x.expiry or date.max, x.strike or Decimal("0"), x.tradingsymbol),
    )
    puts = sorted(
        [
            x
            for x in contracts
            if x.kind is InstrumentKind.OPTION and x.option_right is OptionRight.PUT
        ],
        key=lambda x: (x.expiry or date.max, x.strike or Decimal("0"), x.tradingsymbol),
    )

    if not futures:
        raise InstrumentLoadError(
            f"no futures found for underlying={config.underlying_symbol.upper()} "
            f"root={config.future_root.upper()}"
        )
    if not calls:
        raise InstrumentLoadError(
            f"no call options found for underlying={config.underlying_symbol.upper()} "
            f"root={config.option_root.upper()}"
        )
    if not puts:
        raise InstrumentLoadError(
            f"no put options found for underlying={config.underlying_symbol.upper()} "
            f"root={config.option_root.upper()}"
        )

    meta = SourceMeta(
        source_path=source_path,
        source_format=source_format,
        loaded_at=current,
        source_updated_at=source_updated_at,
        record_count=len(rows),
    )

    repo = InstrumentRepository(
        config=config,
        source_meta=meta,
        _contracts=tuple(contracts),
        _futures=tuple(futures),
        _calls=tuple(calls),
        _puts=tuple(puts),
        _loaded_at=current,
    )

    log.info(
        "instrument_repository_loaded path=%s format=%s records=%s futures=%s calls=%s puts=%s",
        source_path,
        source_format.value,
        len(rows),
        len(futures),
        len(calls),
        len(puts),
    )
    return repo


# =============================================================================
# Thin caller-facing façade
# =============================================================================


@dataclass(slots=True)
class InstrumentSelector:
    """
    Thin caller-facing façade for readability.

    This wrapper does not change ownership and does not make this module a
    runtime service.
    """

    repository: InstrumentRepository

    def current_future(self, *, now: datetime | None = None) -> ContractMetadata:
        return self.repository.get_current_future(now=now)

    def call_pair(
        self,
        *,
        underlying_ltp: Decimal,
        now: datetime | None = None,
    ) -> SelectedOptionPair:
        return self.repository.resolve_option_pair(
            side=OptionRight.CALL,
            underlying_ltp=underlying_ltp,
            now=now,
        )

    def put_pair(
        self,
        *,
        underlying_ltp: Decimal,
        now: datetime | None = None,
    ) -> SelectedOptionPair:
        return self.repository.resolve_option_pair(
            side=OptionRight.PUT,
            underlying_ltp=underlying_ltp,
            now=now,
        )

    def active_contracts(
        self,
        *,
        underlying_ltp: Decimal,
        now: datetime | None = None,
    ) -> RuntimeInstrumentSet:
        return self.repository.build_runtime_set(
            underlying_ltp=underlying_ltp,
            now=now,
        )


# =============================================================================
# Convenience façade
# =============================================================================


def resolve_runtime_instruments(
    *,
    config: InstrumentConfig,
    underlying_ltp: Decimal,
    now: datetime | None = None,
    logger: logging.Logger | None = None,
) -> RuntimeInstrumentSet:
    """
    Pure domain convenience function.

    This function does not publish state, create heartbeats, or register a service.
    """
    repo = load_instrument_repository(config=config, logger=logger, now=now)
    return repo.build_runtime_set(underlying_ltp=underlying_ltp, now=now)


# =============================================================================
# Optional local self-check CLI
# =============================================================================


def _build_arg_parser() -> Any:
    import argparse

    parser = argparse.ArgumentParser(
        description="ScalpX MME instrument identity and deterministic runtime contract selection"
    )
    parser.add_argument("--source-path", required=True, type=str, help="Instrument master path")
    parser.add_argument("--source-format", default="csv", choices=("csv", "json"))
    parser.add_argument("--underlying", default="NIFTY")
    parser.add_argument("--future-root", default="NIFTY")
    parser.add_argument("--option-root", default="NIFTY")
    parser.add_argument("--underlying-ltp", required=True, type=str)
    parser.add_argument("--freshness-days", type=int, default=7)
    parser.add_argument("--option-expiry-days-guard", type=int, default=9)
    parser.add_argument("--market-close-ist", type=str, default="15:30")
    parser.add_argument("--strike-step-override", type=str, default="")
    parser.add_argument("--allow-monthly-fallback", action="store_true")
    parser.add_argument("--disable-weekly-requirement", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    return parser


def _parse_hhmm(text: str) -> time:
    raw = _normalize_str(text)
    try:
        hh, mm = raw.split(":")
        return time(hour=int(hh), minute=int(mm))
    except Exception as exc:
        raise InstrumentValidationError(f"invalid HH:MM time: {text!r}") from exc


def main() -> int:
    """
    Optional local self-check CLI only.

    This is not a runtime-service entrypoint and must not be used as one.
    """
    parser = _build_arg_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    strike_override = (
        Decimal(args.strike_step_override) if _normalize_str(args.strike_step_override) else None
    )

    config = InstrumentConfig(
        source_path=args.source_path,
        source_format=args.source_format,
        underlying_symbol=args.underlying,
        future_root=args.future_root,
        option_root=args.option_root,
        freshness_max_age=timedelta(days=int(args.freshness_days)),
        option_expiry_days_guard=int(args.option_expiry_days_guard),
        require_weekly_options=not bool(args.disable_weekly_requirement),
        allow_monthly_fallback=bool(args.allow_monthly_fallback),
        strike_step_override=strike_override,
        market_close_ist=_parse_hhmm(args.market_close_ist),
    )

    runtime = resolve_runtime_instruments(
        config=config,
        underlying_ltp=Decimal(args.underlying_ltp),
        logger=LOGGER,
    )

    print(json.dumps(runtime.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())