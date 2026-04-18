from __future__ import annotations

"""
app/mme_scalpx/research_capture/contracts.py

Frozen contract surface for the MME research data capture chapter.

Purpose
-------
This module freezes the symbolic contract for research/archive capture so that
all downstream implementation remains deterministic, auditable, and separated
from production doctrine.

Owns
----
- schema and constitution identifiers
- canonical field metadata enums
- canonical field layers and groups
- field specifications for research capture
- archive filenames, partition policy, and manifest keys
- validation helpers for field-spec integrity

Does not own
------------
- runtime capture logic
- broker IO
- Redis IO
- Parquet IO
- derived metric computation
- replay evaluation logic
- production strategy doctrine

Design laws
-----------
- recorded != strategy-approved
- derived != production-used
- researched != contract-changed
- capture broadly, derive selectively live, derive heavily offline
- anything hard to reconstruct later should be preserved as raw capture
- Redis is hot/latest/live only; archive Parquet is long-term research truth
"""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Iterator, Mapping, Sequence

SCHEMA_NAME = "MME Research Data Capture Schema"
SCHEMA_VERSION = "v1"
CONSTITUTION_NAME = "MME Research Data Capture Constitution v1"
SCHEMA_STATUS = "frozen_for_initial_implementation"
CHAPTER_NAME = "research_capture"

SCHEMA_NOTES: tuple[str, ...] = (
    "research/archive contract only",
    "not the frozen production strategy contract",
    "recorded != strategy-approved",
    "derived != production-used",
    "researched != contract-changed",
)

ARCHIVE_ROOT_RELATIVE = "run/research_capture"
DOC_CONSTITUTION_RELATIVE = "docs/research_data_capture_constitution.md"
FIELD_DICTIONARY_RELATIVE = "etc/research_capture/field_dictionary.csv"
SCHEMA_VERSION_RELATIVE = "etc/research_capture/schema_version.json"
ARCHIVE_CONFIG_RELATIVE = "etc/research_capture/archive_config.json"
PARTITIONS_CONFIG_RELATIVE = "etc/research_capture/partitions.json"

MANIFEST_FILENAME = "manifest.json"
SOURCE_AVAILABILITY_FILENAME = "source_availability.json"
INTEGRITY_SUMMARY_FILENAME = "integrity_summary.json"
TICKS_FUT_FILENAME = "ticks_fut.parquet"
TICKS_OPT_FILENAME = "ticks_opt.parquet"
SIGNALS_AUDIT_FILENAME = "signals_audit.parquet"
RUNTIME_AUDIT_FILENAME = "runtime_audit.parquet"

ARCHIVE_WRITE_MODE = "append"
ARCHIVE_FORMAT = "parquet"
ARCHIVE_COMPRESSION = "snappy"

PRIMARY_PARTITIONS: tuple[str, ...] = (
    "session_date",
    "instrument_type",
    "underlying_symbol",
    "expiry",
    "option_type",
)
SECONDARY_PARTITIONS: tuple[str, ...] = ("strike",)

MANIFEST_REQUIRED_KEYS: tuple[str, ...] = (
    "schema_name",
    "schema_version",
    "constitution_name",
    "chapter",
    "session_date",
    "created_at",
    "source_availability",
    "integrity_summary",
    "archive_outputs",
)

FIELD_DICTIONARY_HEADER: tuple[str, ...] = (
    "field_name",
    "type",
    "source",
    "requiredness",
    "compute_stage",
    "usage_class",
    "storage_target",
    "layer",
    "group",
    "description",
    "allowed_values",
)


class FieldSource(str, Enum):
    BROKER_RAW = "broker_raw"
    STATIC_REFERENCE = "static_reference"
    RUNTIME_CONTEXT = "runtime_context"
    LIVE_DERIVED = "live_derived"
    OFFLINE_DERIVED = "offline_derived"
    STRATEGY_AUDIT = "strategy_audit"


class Requiredness(str, Enum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class ComputeStage(str, Enum):
    RAW_CAPTURE = "raw_capture"
    LIVE_COMPUTE = "live_compute"
    OFFLINE_COMPUTE = "offline_compute"


class UsageClass(str, Enum):
    PRODUCTION_CANDIDATE = "production_candidate"
    RESEARCH_ONLY = "research_only"
    AUDIT_ONLY = "audit_only"


class StorageTarget(str, Enum):
    REDIS_STREAM = "redis_stream"
    REDIS_LATEST = "redis_latest"
    ARCHIVE_PARQUET = "archive_parquet"
    MANIFEST_JSON = "manifest_json"
    REPORT_ARTIFACT = "report_artifact"


class FieldLayer(str, Enum):
    RAW_MANDATORY = "raw_mandatory"
    RAW_RECOMMENDED = "raw_recommended"
    LIVE_DERIVED_LIGHTWEIGHT = "live_derived_lightweight"
    OFFLINE_DERIVED_HEAVYWEIGHT = "offline_derived_heavyweight"
    AUDIT_RUNTIME_FORENSICS = "audit_runtime_strategy_forensics"


class FieldGroup(str, Enum):
    TIMING_IDENTITY = "timing_identity"
    INSTRUMENT_IDENTITY = "instrument_identity"
    CORE_MARKET_BOOK = "core_market_book"
    CONTEXT_ANCHORS = "context_anchors"
    SESSION_EXPIRY_CONTEXT = "session_expiry_context"
    LIVE_DERIVED_METRICS = "live_derived_metrics"
    AUDIT_RUNTIME_FORENSICS = "audit_runtime_strategy_forensics"
    OFFLINE_DERIVED_PACKS = "offline_derived_packs"


BR = FieldSource.BROKER_RAW
SR = FieldSource.STATIC_REFERENCE
RC = FieldSource.RUNTIME_CONTEXT
LD = FieldSource.LIVE_DERIVED
OD = FieldSource.OFFLINE_DERIVED
SA = FieldSource.STRATEGY_AUDIT

REQ = Requiredness.REQUIRED
REC = Requiredness.RECOMMENDED
OPT = Requiredness.OPTIONAL

RAW = ComputeStage.RAW_CAPTURE
LIVE = ComputeStage.LIVE_COMPUTE
OFFLINE = ComputeStage.OFFLINE_COMPUTE

PROD = UsageClass.PRODUCTION_CANDIDATE
RES = UsageClass.RESEARCH_ONLY
AUD = UsageClass.AUDIT_ONLY

RS = StorageTarget.REDIS_STREAM
RL = StorageTarget.REDIS_LATEST
AP = StorageTarget.ARCHIVE_PARQUET
MJ = StorageTarget.MANIFEST_JSON
RA = StorageTarget.REPORT_ARTIFACT


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """Frozen metadata contract for a single research-capture field."""

    name: str
    dtype: str
    source: FieldSource
    requiredness: Requiredness
    compute_stage: ComputeStage
    usage_class: UsageClass
    storage_targets: tuple[StorageTarget, ...]
    layer: FieldLayer
    group: FieldGroup
    description: str
    allowed_values: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "storage_targets", tuple(self.storage_targets))
        object.__setattr__(self, "allowed_values", tuple(self.allowed_values))
        self.validate()

    def validate(self) -> None:
        if not self.name:
            raise ValueError("FieldSpec.name must be non-empty")
        if self.name != self.name.strip():
            raise ValueError(f"FieldSpec.name must not contain leading/trailing spaces: {self.name!r}")
        if not self.dtype:
            raise ValueError(f"{self.name}: dtype must be non-empty")
        if not self.description:
            raise ValueError(f"{self.name}: description must be non-empty")
        if not self.storage_targets:
            raise ValueError(f"{self.name}: storage_targets must be non-empty")
        if len(set(self.storage_targets)) != len(self.storage_targets):
            raise ValueError(f"{self.name}: storage_targets contain duplicates")

        if self.source in {BR, SR, RC} and self.compute_stage is not RAW:
            raise ValueError(f"{self.name}: raw/static/runtime sources must use raw_capture")
        if self.source is LD and self.compute_stage is not LIVE:
            raise ValueError(f"{self.name}: live_derived fields must use live_compute")
        if self.source is OD and self.compute_stage is not OFFLINE:
            raise ValueError(f"{self.name}: offline_derived fields must use offline_compute")
        if self.source is SA and self.compute_stage is not LIVE:
            raise ValueError(f"{self.name}: strategy_audit fields must use live_compute")

        if self.layer is FieldLayer.RAW_MANDATORY and self.compute_stage is not RAW:
            raise ValueError(f"{self.name}: raw_mandatory layer must use raw_capture")
        if self.layer is FieldLayer.RAW_RECOMMENDED and self.compute_stage is not RAW:
            raise ValueError(f"{self.name}: raw_recommended layer must use raw_capture")
        if self.layer is FieldLayer.LIVE_DERIVED_LIGHTWEIGHT and self.compute_stage is not LIVE:
            raise ValueError(f"{self.name}: live_derived layer must use live_compute")
        if self.layer is FieldLayer.OFFLINE_DERIVED_HEAVYWEIGHT and self.compute_stage is not OFFLINE:
            raise ValueError(f"{self.name}: offline_derived layer must use offline_compute")
        if self.layer is FieldLayer.AUDIT_RUNTIME_FORENSICS and self.usage_class is not AUD:
            raise ValueError(f"{self.name}: audit layer must use audit_only")

        if self.usage_class is PROD and self.source in {OD, SA}:
            raise ValueError(f"{self.name}: production_candidate cannot originate from {self.source.value}")
        if self.compute_stage is OFFLINE and any(t in {RS, RL} for t in self.storage_targets):
            raise ValueError(f"{self.name}: offline fields must not target Redis storage")
        if self.usage_class is AUD and self.group is FieldGroup.OFFLINE_DERIVED_PACKS:
            raise ValueError(f"{self.name}: offline derived packs cannot be audit_only")
        if self.allowed_values and any(not value for value in self.allowed_values):
            raise ValueError(f"{self.name}: allowed_values must not contain empty strings")

    @property
    def storage_target_value(self) -> str:
        return "|".join(target.value for target in self.storage_targets)

    @property
    def allowed_values_value(self) -> str:
        return "|".join(self.allowed_values)

    def to_field_dictionary_row(self) -> tuple[str, ...]:
        return (
            self.name,
            self.dtype,
            self.source.value,
            self.requiredness.value,
            self.compute_stage.value,
            self.usage_class.value,
            self.storage_target_value,
            self.layer.value,
            self.group.value,
            self.description,
            self.allowed_values_value,
        )


def _field(
    *,
    name: str,
    dtype: str,
    source: FieldSource,
    requiredness: Requiredness,
    compute_stage: ComputeStage,
    usage_class: UsageClass,
    storage_targets: Sequence[StorageTarget],
    layer: FieldLayer,
    group: FieldGroup,
    description: str,
    allowed_values: Sequence[str] = (),
) -> FieldSpec:
    return FieldSpec(
        name=name,
        dtype=dtype,
        source=source,
        requiredness=requiredness,
        compute_stage=compute_stage,
        usage_class=usage_class,
        storage_targets=tuple(storage_targets),
        layer=layer,
        group=group,
        description=description,
        allowed_values=tuple(allowed_values),
    )


def _build_specs(
    *,
    layer: FieldLayer,
    group: FieldGroup,
    rows: Iterable[
        tuple[
            str,
            str,
            FieldSource,
            Requiredness,
            ComputeStage,
            UsageClass,
            Sequence[StorageTarget],
            str,
            Sequence[str],
        ]
    ],
) -> tuple[FieldSpec, ...]:
    return tuple(
        _field(
            name=name,
            dtype=dtype,
            source=source,
            requiredness=requiredness,
            compute_stage=compute_stage,
            usage_class=usage_class,
            storage_targets=storage_targets,
            layer=layer,
            group=group,
            description=description,
            allowed_values=allowed_values,
        )
        for (
            name,
            dtype,
            source,
            requiredness,
            compute_stage,
            usage_class,
            storage_targets,
            description,
            allowed_values,
        ) in rows
    )


_TIMING_IDENTITY_FIELDS = _build_specs(
    layer=FieldLayer.RAW_MANDATORY,
    group=FieldGroup.TIMING_IDENTITY,
    rows=(
        ("session_date", "str", RC, REQ, RAW, RES, (AP,), "Trading session date", ()),
        ("exchange_ts", "float", BR, REQ, RAW, PROD, (RS, AP), "Broker/exchange event timestamp", ()),
        ("source_ts_ns", "int", BR, REC, RAW, RES, (AP,), "Normalized source timestamp in nanoseconds", ()),
        ("recv_ts_ns", "int", RC, REQ, RAW, AUD, (AP,), "Local receive timestamp in nanoseconds", ()),
        ("process_ts_ns", "int", RC, REQ, RAW, AUD, (AP,), "Local normalization completion timestamp in nanoseconds", ()),
        ("event_seq", "int", RC, REQ, RAW, AUD, (AP,), "Per-symbol monotonic local sequence number", ()),
        ("snapshot_id", "str", RC, REQ, RAW, AUD, (RS, AP), "Shared synchronized FUT/OPT snapshot identifier", ()),
        ("processed_ts", "float", RC, REC, RAW, AUD, (AP,), "Processed timestamp in seconds", ()),
        ("network_time", "float", RC, REC, RAW, AUD, (AP,), "NTP or local network time reference", ()),
    ),
)

_TIMING_DERIVED_AUDIT_FIELDS = _build_specs(
    layer=FieldLayer.AUDIT_RUNTIME_FORENSICS,
    group=FieldGroup.TIMING_IDENTITY,
    rows=(
        ("latency_ns", "int", LD, REQ, LIVE, AUD, (RS, AP), "Approximate end-to-end latency in nanoseconds", ()),
        ("gap_from_prev_tick_ms", "int", LD, REQ, LIVE, AUD, (AP,), "Inter-arrival gap from the previous tick in milliseconds", ()),
    ),
)

_INSTRUMENT_IDENTITY_FIELDS = _build_specs(
    layer=FieldLayer.RAW_MANDATORY,
    group=FieldGroup.INSTRUMENT_IDENTITY,
    rows=(
        ("broker_name", "str", RC, REQ, RAW, RES, (AP,), "Broker identifier", ()),
        ("exchange", "str", BR, REQ, RAW, RES, (AP,), "Exchange name", ()),
        ("exchange_segment", "str", BR, REQ, RAW, RES, (AP,), "Exchange segment such as NFO", ()),
        ("instrument_token", "str_or_int", BR, REQ, RAW, PROD, (RS, RL, AP), "Broker instrument token", ()),
        ("symbol_token", "str", BR, REC, RAW, RES, (AP,), "Alternate broker symbol token if supplied", ()),
        ("tradingsymbol", "str", BR, REQ, RAW, PROD, (RS, RL, AP), "Broker trading symbol", ()),
        ("symbol", "str", BR, REC, RAW, RES, (AP,), "Full instrument key or symbol", ()),
        ("contract_name", "str", SR, REC, RAW, RES, (AP,), "Human-readable contract name", ()),
        ("instrument_type", "str", SR, REQ, RAW, RES, (AP,), "Instrument type", ("SPOT", "FUT", "CE", "PE", "VIX", "INDEX")),
        ("symbol_root", "str", BR, REQ, RAW, RES, (AP,), "Underlying root such as NIFTY", ()),
        ("underlying_symbol", "str", SR, REQ, RAW, RES, (AP,), "Underlying symbol", ()),
        ("underlying_token", "str_or_int", SR, REC, RAW, RES, (AP,), "Underlying token if maintained", ()),
        ("option_type", "str", SR, REQ, RAW, PROD, (RS, AP), "Option type or None for non-options", ("CE", "PE", "None")),
        ("strike", "int", SR, REQ, RAW, PROD, (RS, AP), "Option strike for options contracts", ()),
        ("expiry", "str", SR, REQ, RAW, PROD, (RS, AP), "Expiry date for derivatives", ()),
        ("expiry_type", "str", SR, REC, RAW, RES, (AP,), "Expiry bucket", ("weekly", "monthly", "None")),
        ("tick_size", "float", SR, REQ, RAW, PROD, (RL, AP), "Instrument tick size", ()),
        ("lot_size", "int", SR, REQ, RAW, PROD, (RL, AP), "Contract lot size", ()),
        ("freeze_qty", "int", SR, REC, RAW, RES, (AP,), "Freeze quantity limit", ()),
        ("strike_step", "int", SR, REC, RAW, RES, (AP,), "Strike interval", ()),
    ),
)

_INSTRUMENT_RECOMMENDED_FIELDS = _build_specs(
    layer=FieldLayer.LIVE_DERIVED_LIGHTWEIGHT,
    group=FieldGroup.INSTRUMENT_IDENTITY,
    rows=(
        ("moneyness_bucket", "str", LD, REC, LIVE, RES, (AP,), "ITM/ATM/OTM bucket", ("ITM", "ATM", "OTM", "None")),
    ),
)

_CORE_MARKET_BOOK_FIELDS = _build_specs(
    layer=FieldLayer.RAW_MANDATORY,
    group=FieldGroup.CORE_MARKET_BOOK,
    rows=(
        ("ltp", "float", BR, REQ, RAW, PROD, (RS, RL, AP), "Last traded price", ()),
        ("price", "float", BR, REC, RAW, RES, (AP,), "Canonical price alias", ()),
        ("volume", "int", BR, REQ, RAW, PROD, (RS, RL, AP), "Volume", ()),
        ("oi", "int", BR, REC, RAW, PROD, (RS, RL, AP), "Open interest", ()),
        ("best_bid", "float", BR, REQ, RAW, PROD, (RS, RL, AP), "Best bid price", ()),
        ("best_ask", "float", BR, REQ, RAW, PROD, (RS, RL, AP), "Best ask price", ()),
        ("best_bid_qty", "int", BR, REC, RAW, RES, (AP,), "Best bid quantity", ()),
        ("best_ask_qty", "int", BR, REC, RAW, RES, (AP,), "Best ask quantity", ()),
        ("bid_prices", "json_list_float", BR, REQ, RAW, RES, (AP,), "Bid ladder prices", ()),
        ("bid_qty", "json_list_int", BR, REQ, RAW, RES, (AP,), "Bid ladder quantities", ()),
        ("ask_prices", "json_list_float", BR, REQ, RAW, RES, (AP,), "Ask ladder prices", ()),
        ("ask_qty", "json_list_int", BR, REQ, RAW, RES, (AP,), "Ask ladder quantities", ()),
        ("depth_levels_present_bid", "int", BR, REC, RAW, RES, (AP,), "Number of valid bid depth levels", ()),
        ("depth_levels_present_ask", "int", BR, REC, RAW, RES, (AP,), "Number of valid ask depth levels", ()),
    ),
)

_CORE_MARKET_BOOK_DERIVED_FIELDS = _build_specs(
    layer=FieldLayer.LIVE_DERIVED_LIGHTWEIGHT,
    group=FieldGroup.CORE_MARKET_BOOK,
    rows=(
        ("mid_price", "float", LD, REC, LIVE, RES, (AP,), "Mid price from best bid and best ask", ()),
        ("microprice", "float", LD, REC, LIVE, RES, (AP,), "Queue-weighted microprice", ()),
    ),
)

_CONTEXT_ANCHOR_FIELDS = _build_specs(
    layer=FieldLayer.RAW_RECOMMENDED,
    group=FieldGroup.CONTEXT_ANCHORS,
    rows=(
        ("spot_symbol", "str", SR, REC, RAW, RES, (AP,), "Spot symbol reference", ()),
        ("spot", "float", BR, REC, RAW, RES, (AP,), "Spot price", ()),
        ("spot_ts", "float", BR, REC, RAW, AUD, (AP,), "Spot timestamp", ()),
        ("fut_symbol", "str", SR, REC, RAW, RES, (AP,), "Front future symbol", ()),
        ("fut_ltp", "float", BR, REC, RAW, RES, (AP,), "Front future price", ()),
        ("fut_vol", "int", BR, OPT, RAW, RES, (AP,), "Front future volume", ()),
        ("fut_ts", "float", BR, OPT, RAW, AUD, (AP,), "Front future timestamp", ()),
        ("vix", "float", BR, REC, RAW, RES, (RL, AP), "VIX value", ()),
        ("vix_ts", "float", BR, REC, RAW, AUD, (AP,), "VIX timestamp", ()),
        ("pcr", "float", BR, OPT, RAW, RES, (AP,), "Put-call ratio when cheaply available", ()),
        ("iv", "float", BR, REC, RAW, RES, (AP,), "Implied volatility when available", ()),
        ("atm_iv", "float", BR, OPT, RAW, RES, (AP,), "ATM implied volatility snapshot", ()),
    ),
)

_CONTEXT_ANCHOR_DERIVED_FIELDS = _build_specs(
    layer=FieldLayer.LIVE_DERIVED_LIGHTWEIGHT,
    group=FieldGroup.CONTEXT_ANCHORS,
    rows=(
        ("orb_high", "float", LD, REC, LIVE, RES, (RL, AP), "Opening range breakout high anchor", ()),
        ("orb_low", "float", LD, REC, LIVE, RES, (RL, AP), "Opening range breakout low anchor", ()),
        ("orb_ts", "float", LD, OPT, LIVE, RES, (AP,), "Opening range breakout anchor timestamp", ()),
    ),
)

_SESSION_EXPIRY_FIELDS = _build_specs(
    layer=FieldLayer.RAW_RECOMMENDED,
    group=FieldGroup.SESSION_EXPIRY_CONTEXT,
    rows=(
        ("market_open", "str", RC, REC, RAW, RES, (AP,), "Market open reference", ()),
        ("market_close", "str", RC, REC, RAW, RES, (AP,), "Market close reference", ()),
        ("is_expiry", "bool", RC, REQ, RAW, RES, (AP,), "Expiry-day flag", ()),
        ("dte", "int", RC, REQ, RAW, RES, (AP,), "Days to expiry", ()),
        ("days_to_expiry_exact", "float", RC, REC, RAW, RES, (AP,), "Fractional days to expiry", ()),
        ("is_current_week", "bool", RC, REC, RAW, RES, (AP,), "Current weekly expiry flag", ()),
        ("is_next_week", "bool", RC, REC, RAW, RES, (AP,), "Next weekly expiry flag", ()),
        ("is_monthly_expiry", "bool", RC, REC, RAW, RES, (AP,), "Monthly expiry flag", ()),
        ("trading_minute_index", "int", RC, REC, RAW, RES, (AP,), "Minute index from market open", ()),
        ("is_preopen", "bool", RC, REQ, RAW, AUD, (AP,), "Pre-open session flag", ()),
        ("is_postclose", "bool", RC, REQ, RAW, AUD, (AP,), "Post-close session flag", ()),
        ("weekday", "int", RC, OPT, RAW, RES, (AP,), "Weekday number", ()),
        ("month", "int", RC, OPT, RAW, RES, (AP,), "Month number", ()),
        ("expiry_week_flag", "bool", RC, OPT, RAW, RES, (AP,), "Expiry-week flag", ()),
    ),
)

_LIVE_DERIVED_METRIC_FIELDS = _build_specs(
    layer=FieldLayer.LIVE_DERIVED_LIGHTWEIGHT,
    group=FieldGroup.LIVE_DERIVED_METRICS,
    rows=(
        ("spread", "float", LD, REQ, LIVE, PROD, (RS, AP), "Best ask minus best bid", ()),
        ("spread_pct", "float", LD, REQ, LIVE, PROD, (RS, AP), "Spread normalized by price", ()),
        ("half_spread", "float", LD, REC, LIVE, RES, (AP,), "Half spread", ()),
        ("sum_bid", "int", LD, REQ, LIVE, RES, (AP,), "Aggregated bid quantity across chosen levels", ()),
        ("sum_ask", "int", LD, REQ, LIVE, RES, (AP,), "Aggregated ask quantity across chosen levels", ()),
        ("nof", "float", LD, REQ, LIVE, PROD, (RS, AP), "Net order flow ratio", ()),
        ("nof_ema20", "float", LD, REC, LIVE, RES, (AP,), "EMA of net order flow", ()),
        ("nof_slope3", "float", LD, REC, LIVE, RES, (AP,), "Short net order flow slope", ()),
        ("queue_imbalance_l1", "float", LD, REC, LIVE, RES, (AP,), "Level-1 queue imbalance", ()),
        ("queue_imbalance_l5", "float", LD, REC, LIVE, RES, (AP,), "Top-5 queue imbalance", ()),
        ("book_pressure_ratio_5", "float", LD, REC, LIVE, RES, (AP,), "Top-5 bid/ask pressure ratio", ()),
        ("book_pressure_ratio_10", "float", LD, REC, LIVE, RES, (AP,), "Top-10 bid/ask pressure ratio", ()),
        ("book_notional_bid_5", "float", LD, OPT, LIVE, RES, (AP,), "Top-5 bid notional", ()),
        ("book_notional_ask_5", "float", LD, OPT, LIVE, RES, (AP,), "Top-5 ask notional", ()),
        ("book_notional_bid_10", "float", LD, OPT, LIVE, RES, (AP,), "Top-10 bid notional", ()),
        ("book_notional_ask_10", "float", LD, OPT, LIVE, RES, (AP,), "Top-10 ask notional", ()),
        ("top_bid_notional", "float", LD, OPT, LIVE, RES, (AP,), "Level-1 bid notional", ()),
        ("top_ask_notional", "float", LD, OPT, LIVE, RES, (AP,), "Level-1 ask notional", ()),
        ("cvd", "int", LD, REC, LIVE, RES, (AP,), "Cumulative delta proxy", ()),
        ("cvd_slope_3", "float", LD, REC, LIVE, PROD, (AP,), "Short cumulative delta slope", ()),
        ("cvd_slope_5", "float", LD, OPT, LIVE, RES, (AP,), "Medium cumulative delta slope", ()),
        ("cvd_slope_10", "float", LD, OPT, LIVE, RES, (AP,), "Longer cumulative delta slope", ()),
        ("trade_through_up", "bool", LD, OPT, LIVE, RES, (AP,), "Upward trade-through proxy", ()),
        ("trade_through_down", "bool", LD, OPT, LIVE, RES, (AP,), "Downward trade-through proxy", ()),
        ("bbid_stepdowns_10", "int", LD, OPT, LIVE, RES, (AP,), "Best-bid stepdowns over recent ticks", ()),
        ("bask_stepups_10", "int", LD, OPT, LIVE, RES, (AP,), "Best-ask stepups over recent ticks", ()),
        ("spread_widening_10", "bool", LD, OPT, LIVE, RES, (AP,), "Recent spread widening flag", ()),
        ("nof_neutral_ticks", "int", LD, OPT, LIVE, RES, (AP,), "Count of neutral net-order-flow ticks", ()),
        ("prev_price", "float", LD, OPT, LIVE, RES, (AP,), "Previous price", ()),
        ("price_delta_1tick", "float", LD, OPT, LIVE, RES, (AP,), "One-tick price delta", ()),
        ("price_delta_1s", "float", LD, OPT, LIVE, RES, (AP,), "One-second price delta", ()),
        ("price_delta_5s", "float", LD, OPT, LIVE, RES, (AP,), "Five-second price delta", ()),
        ("session_high_so_far", "float", LD, OPT, LIVE, RES, (AP,), "Running session high", ()),
        ("session_low_so_far", "float", LD, OPT, LIVE, RES, (AP,), "Running session low", ()),
        ("distance_from_session_high", "float", LD, OPT, LIVE, RES, (AP,), "Distance from running session high", ()),
        ("distance_from_session_low", "float", LD, OPT, LIVE, RES, (AP,), "Distance from running session low", ()),
        ("distance_from_orb_high", "float", LD, OPT, LIVE, RES, (AP,), "Distance from ORB high", ()),
        ("distance_from_orb_low", "float", LD, OPT, LIVE, RES, (AP,), "Distance from ORB low", ()),
        ("distance_from_day_open", "float", LD, OPT, LIVE, RES, (AP,), "Distance from session open", ()),
        ("vwap", "float", LD, REC, LIVE, PROD, (AP,), "Session VWAP", ()),
        ("vwap_dist", "float", LD, REC, LIVE, PROD, (AP,), "Distance from VWAP", ()),
        ("vwap_slope", "float", LD, REC, LIVE, RES, (AP,), "VWAP slope", ()),
        ("bb_upper", "float", LD, OPT, LIVE, RES, (AP,), "Upper Bollinger band", ()),
        ("bb_lower", "float", LD, OPT, LIVE, RES, (AP,), "Lower Bollinger band", ()),
        ("bb_mid", "float", LD, OPT, LIVE, RES, (AP,), "Middle Bollinger band", ()),
        ("bb_width", "float", LD, OPT, LIVE, RES, (AP,), "Bollinger band width", ()),
        ("bb_width_ratio", "float", LD, OPT, LIVE, RES, (AP,), "Normalized Bollinger band width", ()),
        ("recent_swing_high", "float", LD, OPT, LIVE, RES, (AP,), "Recent swing high", ()),
        ("recent_swing_low", "float", LD, OPT, LIVE, RES, (AP,), "Recent swing low", ()),
        ("recent_high_5min", "float", LD, OPT, LIVE, RES, (AP,), "Rolling 5-minute high", ()),
        ("recent_low_5min", "float", LD, OPT, LIVE, RES, (AP,), "Rolling 5-minute low", ()),
        ("price_range_5m", "float", LD, OPT, LIVE, RES, (AP,), "Five-minute price range", ()),
        ("pullback_depth", "float", LD, OPT, LIVE, RES, (AP,), "Pullback depth", ()),
        ("pullback_secs", "int", LD, OPT, LIVE, RES, (AP,), "Pullback duration in seconds", ()),
        ("high_since_entry_candidate", "float", LD, OPT, LIVE, RES, (AP,), "High since candidate start", ()),
        ("low_since_entry_candidate", "float", LD, OPT, LIVE, RES, (AP,), "Low since candidate start", ()),
        ("vol_ma10", "float", LD, REC, LIVE, RES, (AP,), "Short volume moving average", ()),
        ("vol_ma20", "float", LD, REC, LIVE, RES, (AP,), "Longer volume moving average", ()),
        ("vol_delta_1m", "float", LD, OPT, LIVE, RES, (AP,), "One-minute volume delta", ()),
        ("vol_delta_5m", "float", LD, OPT, LIVE, RES, (AP,), "Five-minute volume delta", ()),
        ("cum_volume_session", "int", LD, REC, LIVE, RES, (AP,), "Cumulative session volume", ()),
        ("cum_notional_session", "float", LD, OPT, LIVE, RES, (AP,), "Cumulative session notional", ()),
        ("trade_count_proxy", "int", LD, OPT, LIVE, RES, (AP,), "Trade count proxy", ()),
        ("relative_volume_1m", "float", LD, OPT, LIVE, RES, (AP,), "Relative volume over one minute", ()),
        ("relative_volume_5m", "float", LD, OPT, LIVE, RES, (AP,), "Relative volume over five minutes", ()),
        ("volume_zscore", "float", LD, OPT, LIVE, RES, (AP,), "Volume z-score", ()),
        ("spikes_5", "int", LD, OPT, LIVE, RES, (AP,), "Short spike count", ()),
        ("spikes_10", "int", LD, OPT, LIVE, RES, (AP,), "Medium spike count", ()),
        ("spikes_20", "int", LD, OPT, LIVE, RES, (AP,), "Longer spike count", ()),
        ("vpi", "float", LD, OPT, LIVE, RES, (AP,), "Volume pressure index", ()),
        ("signal_confidence", "float", LD, OPT, LIVE, RES, (AP,), "Cheap signal confidence proxy", ()),
        ("oi_delta_option", "int", LD, REC, LIVE, RES, (AP,), "Option open-interest delta", ()),
        ("oi_change_1m", "int", LD, OPT, LIVE, RES, (AP,), "One-minute open-interest change", ()),
        ("oi_change_5m", "int", LD, OPT, LIVE, RES, (AP,), "Five-minute open-interest change", ()),
        ("oi_velocity", "float", LD, OPT, LIVE, RES, (AP,), "Open-interest velocity", ()),
        ("premium", "float", LD, REC, LIVE, RES, (AP,), "Premium alias for option LTP", ()),
        ("strike_dist_pts", "float", LD, OPT, LIVE, RES, (AP,), "Strike distance from spot in points", ()),
        ("delta_proxy", "float", LD, REC, LIVE, RES, (AP,), "Approximate option delta", ()),
        ("gamma_proxy", "float", LD, OPT, LIVE, RES, (AP,), "Approximate gamma proxy", ()),
        ("iv_rank", "float", LD, OPT, LIVE, RES, (AP,), "Implied-volatility percentile rank", ()),
        ("mu_vol_pct", "float", LD, REC, LIVE, RES, (AP,), "Micro-volatility percent", ()),
        ("regime", "str", LD, REC, LIVE, RES, (AP,), "Detected market regime", ("trend", "expansion", "mean_reversion", "neutral")),
        ("is_choppy", "bool", LD, OPT, LIVE, RES, (AP,), "Choppiness flag", ()),
        ("volatility_bucket", "str", LD, OPT, LIVE, RES, (AP,), "Volatility classification bucket", ()),
        ("spot_fut_basis", "float", LD, OPT, LIVE, RES, (AP,), "Spot-future basis", ()),
        ("basis_change_1m", "float", LD, OPT, LIVE, RES, (AP,), "One-minute basis change", ()),
        ("fut_opt_sync_gap_ms", "int", LD, REC, LIVE, RES, (AP,), "FUT-OPT synchronization gap in milliseconds", ()),
        ("fut_move_1s", "float", LD, OPT, LIVE, RES, (AP,), "One-second future move", ()),
        ("fut_move_3s", "float", LD, OPT, LIVE, RES, (AP,), "Three-second future move", ()),
        ("fut_move_5s", "float", LD, OPT, LIVE, RES, (AP,), "Five-second future move", ()),
        ("opt_response_1s", "float", LD, OPT, LIVE, RES, (AP,), "Option response to future move over one second", ()),
        ("opt_response_3s", "float", LD, OPT, LIVE, RES, (AP,), "Option response to future move over three seconds", ()),
        ("lead_lag_score", "float", LD, REC, LIVE, RES, (AP,), "Futures-led confirmation score", ()),
        ("fut_direction", "str", LD, OPT, LIVE, RES, (AP,), "Direction of future move", ("up", "down", "flat", "unknown")),
        ("opt_confirmation_state", "str", LD, OPT, LIVE, RES, (AP,), "Option confirmation state", ()),
        ("fake_break", "bool", LD, OPT, LIVE, RES, (AP,), "ORB fake-break flag", ()),
        ("fake_dir", "str", LD, OPT, LIVE, RES, (AP,), "Fake-break direction", ("up", "down", "none")),
        ("reentry_secs", "int", LD, OPT, LIVE, RES, (AP,), "Seconds to re-enter ORB range", ()),
        ("inrange_hold_secs", "int", LD, OPT, LIVE, RES, (AP,), "Seconds holding inside ORB after re-entry", ()),
        ("breakout_strength", "float", LD, OPT, LIVE, RES, (AP,), "Breakout overshoot magnitude", ()),
        ("retrace_speed", "float", LD, OPT, LIVE, RES, (AP,), "Retrace speed after fakeout", ()),
        ("volume_breakout", "float", LD, OPT, LIVE, RES, (AP,), "Breakout volume versus baseline", ()),
        ("cvd_vs_price", "float", LD, OPT, LIVE, RES, (AP,), "CVD divergence versus price", ()),
        ("near_vwap_band", "bool", LD, OPT, LIVE, RES, (AP,), "Within configured VWAP band", ()),
        ("iceberg_score", "float", LD, OPT, LIVE, RES, (AP,), "Iceberg or refresh proxy score", ()),
        ("iceberg_50p", "float", LD, OPT, LIVE, RES, (AP,), "Rolling 50th percentile iceberg score", ()),
        ("iceberg_75p", "float", LD, OPT, LIVE, RES, (AP,), "Rolling 75th percentile iceberg score", ()),
        ("iceberg_90p", "float", LD, OPT, LIVE, RES, (AP,), "Rolling 90th percentile iceberg score", ()),
        ("dark_pool", "float", LD, OPT, LIVE, RES, (AP,), "Hidden-liquidity proxy", ()),
        ("dark_pool_score", "float", LD, OPT, LIVE, RES, (AP,), "Hidden-liquidity score", ()),
    ),
)

_AUDIT_RUNTIME_FORENSICS_FIELDS = _build_specs(
    layer=FieldLayer.AUDIT_RUNTIME_FORENSICS,
    group=FieldGroup.AUDIT_RUNTIME_FORENSICS,
    rows=(
        ("is_stale_tick", "bool", LD, REQ, LIVE, AUD, (AP,), "Stale-tick flag", ()),
        ("stale_reason", "str", LD, REC, LIVE, AUD, (AP,), "Reason tick was marked stale", ()),
        ("missing_depth_flag", "bool", LD, REQ, LIVE, AUD, (AP,), "Depth unavailable flag", ()),
        ("missing_oi_flag", "bool", LD, REQ, LIVE, AUD, (AP,), "Open-interest unavailable flag", ()),
        ("thin_book", "bool", LD, REQ, LIVE, AUD, (AP,), "Thin-book flag", ()),
        ("book_is_thin", "bool", LD, OPT, LIVE, AUD, (AP,), "Alternate thin-book classifier", ()),
        ("crossed_book_flag", "bool", LD, OPT, LIVE, AUD, (AP,), "Crossed-book flag", ()),
        ("locked_book_flag", "bool", LD, OPT, LIVE, AUD, (AP,), "Locked-book flag", ()),
        ("integrity_flags", "json_list_str", LD, REQ, LIVE, AUD, (AP, RA), "Integrity flags list", ()),
        ("fallback_used_flag", "bool", RC, REC, RAW, AUD, (AP,), "Whether fallback source was used", ()),
        ("fallback_source", "str", RC, OPT, RAW, AUD, (AP,), "Fallback source label", ()),
        ("schema_version", "str", RC, REQ, RAW, AUD, (RL, MJ, AP), "Capture schema version", ()),
        ("normalization_version", "str", RC, REC, RAW, AUD, (MJ,), "Normalization logic version", ()),
        ("derived_version", "str", RC, REC, RAW, AUD, (MJ,), "Derived-metrics logic version", ()),
        ("calendar_version", "str", RC, OPT, RAW, AUD, (MJ,), "Calendar or market-session version", ()),
        ("heartbeat_status", "str", RC, OPT, RAW, AUD, (AP,), "Feed heartbeat summary", ()),
        ("reconnect_count", "int", RC, OPT, RAW, AUD, (AP,), "Reconnect count", ()),
        ("last_reconnect_reason", "str", RC, OPT, RAW, AUD, (AP,), "Last reconnect reason", ()),
        ("gpu_fallback", "bool", RC, OPT, RAW, AUD, (AP,), "GPU fallback flag", ()),
        ("cpu_mode_flag", "bool", RC, OPT, RAW, AUD, (AP,), "CPU mode flag", ()),
        ("candidate_id", "str", SA, REC, LIVE, AUD, (AP,), "Candidate lineage identifier", ()),
        ("candidate_stage", "str", SA, REC, LIVE, AUD, (AP,), "Candidate state or stage", ()),
        ("candidate_side", "str", SA, REC, LIVE, AUD, (AP,), "Candidate side marker", ()),
        ("candidate_score", "float", SA, REC, LIVE, AUD, (AP,), "Candidate score", ()),
        ("blocker_mask", "str", SA, REC, LIVE, AUD, (AP,), "Compact blocker mask", ()),
        ("blocker_primary", "str", SA, REC, LIVE, AUD, (AP,), "Primary blocker", ()),
        ("blocker_chain", "str", SA, OPT, LIVE, AUD, (AP,), "Full blocker lineage", ()),
        ("entry_window_open_flag", "bool", SA, OPT, LIVE, AUD, (AP,), "Entry window open flag", ()),
        ("regime_gate_flag", "bool", SA, OPT, LIVE, AUD, (AP,), "Regime gate status", ()),
        ("context_gate_flag", "bool", SA, OPT, LIVE, AUD, (AP,), "Context gate status", ()),
        ("confirmation_gate_flag", "bool", SA, OPT, LIVE, AUD, (AP,), "Confirmation gate status", ()),
        ("risk_gate_flag", "bool", SA, OPT, LIVE, AUD, (AP,), "Risk gate status", ()),
        ("hold_against", "int", SA, OPT, LIVE, AUD, (AP,), "Seconds holding against thesis", ()),
        ("invalid_secs", "int", SA, OPT, LIVE, AUD, (AP,), "Seconds in invalid state", ()),
        ("strategy_id", "str", SA, OPT, LIVE, AUD, (AP,), "Strategy identifier", ()),
        ("decision_id", "str", SA, OPT, LIVE, AUD, (AP,), "Decision lineage identifier", ()),
        ("decision_action", "str", SA, OPT, LIVE, AUD, (AP,), "Decision action", ()),
        ("execution_mode", "str", SA, OPT, LIVE, AUD, (AP,), "Execution mode at decision time", ()),
        ("ack_type", "str", SA, OPT, LIVE, AUD, (AP,), "ACK state", ()),
        ("order_id", "str", SA, OPT, LIVE, AUD, (AP,), "Order identifier", ()),
        ("trade_id", "str", SA, OPT, LIVE, AUD, (AP,), "Trade identifier", ()),
        ("position_side", "str", SA, OPT, LIVE, AUD, (AP,), "Position side", ()),
        ("entry_mode", "str", SA, OPT, LIVE, AUD, (AP,), "Entry mode", ()),
        ("exit_reason", "str", SA, OPT, LIVE, AUD, (AP,), "Exit reason", ()),
    ),
)

_OFFLINE_DERIVED_PACK_FIELDS = _build_specs(
    layer=FieldLayer.OFFLINE_DERIVED_HEAVYWEIGHT,
    group=FieldGroup.OFFLINE_DERIVED_PACKS,
    rows=(
        ("vp_poc", "float", OD, OPT, OFFLINE, RES, (RA, AP), "Volume-profile point of control", ()),
        ("vp_vah", "float", OD, OPT, OFFLINE, RES, (RA, AP), "Volume-profile value area high", ()),
        ("vp_val", "float", OD, OPT, OFFLINE, RES, (RA, AP), "Volume-profile value area low", ()),
        ("vp_hvn_count", "int", OD, OPT, OFFLINE, RES, (RA,), "High-volume-node count", ()),
        ("vp_lvn_count", "int", OD, OPT, OFFLINE, RES, (RA,), "Low-volume-node count", ()),
        ("vp_shape", "str", OD, OPT, OFFLINE, RES, (RA,), "Volume-profile shape classification", ()),
        ("session_profile_balance_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Auction balance score", ()),
        ("book_refresh_rate_bid", "float", OD, OPT, OFFLINE, RES, (RA,), "Bid refresh rate", ()),
        ("book_refresh_rate_ask", "float", OD, OPT, OFFLINE, RES, (RA,), "Ask refresh rate", ()),
        ("quote_persistence_bid", "float", OD, OPT, OFFLINE, RES, (RA,), "Bid quote persistence", ()),
        ("quote_persistence_ask", "float", OD, OPT, OFFLINE, RES, (RA,), "Ask quote persistence", ()),
        ("micro_reversion_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Microstructure reversion score", ()),
        ("book_absorption_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Absorption score", ()),
        ("cross_strike_flow_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Cross-strike flow score", ()),
        ("cross_strike_oi_rotation_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Cross-strike open-interest rotation score", ()),
        ("iv_regime", "str", OD, OPT, OFFLINE, RES, (RA,), "Implied-volatility regime class", ()),
        ("term_structure_proxy", "float", OD, OPT, OFFLINE, RES, (RA,), "Term-structure proxy", ()),
        ("effective_spread_proxy", "float", OD, OPT, OFFLINE, RES, (RA, AP), "Effective spread estimate", ()),
        ("slippage_entry_est", "float", OD, OPT, OFFLINE, RES, (RA, AP), "Entry slippage estimate", ()),
        ("slippage_exit_est", "float", OD, OPT, OFFLINE, RES, (RA, AP), "Exit slippage estimate", ()),
        ("round_trip_cost_est", "float", OD, REC, OFFLINE, RES, (RA, AP), "Round-trip cost estimate", ()),
        ("tick_value", "float", OD, OPT, OFFLINE, RES, (RA,), "Tick value", ()),
        ("premium_in_ticks", "float", OD, OPT, OFFLINE, RES, (RA,), "Premium expressed in ticks", ()),
        ("stop_distance_ticks", "float", OD, OPT, OFFLINE, RES, (RA,), "Stop distance in ticks", ()),
        ("target_distance_ticks", "float", OD, OPT, OFFLINE, RES, (RA,), "Target distance in ticks", ()),
        ("rr_net_of_cost", "float", OD, OPT, OFFLINE, RES, (RA,), "Net risk-reward after costs", ()),
        ("economics_valid_flag", "bool", OD, REC, OFFLINE, RES, (RA, AP), "Economics validity flag", ()),
        ("economics_reject_reason", "str", OD, REC, OFFLINE, RES, (RA,), "Primary economics rejection reason", ()),
        ("gap_up_down_flag", "str", OD, OPT, OFFLINE, RES, (RA,), "Gap direction classification", ()),
        ("opening_drive_flag", "bool", OD, OPT, OFFLINE, RES, (RA,), "Opening-drive day flag", ()),
        ("trend_day_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Trend-day score", ()),
        ("range_day_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Range-day score", ()),
        ("chop_day_score", "float", OD, OPT, OFFLINE, RES, (RA,), "Chop-day score", ()),
        ("event_day_flag", "bool", OD, OPT, OFFLINE, RES, (RA,), "Event-day flag", ()),
    ),
)

FIELD_SPECS: tuple[FieldSpec, ...] = (
    *_TIMING_IDENTITY_FIELDS,
    *_TIMING_DERIVED_AUDIT_FIELDS,
    *_INSTRUMENT_IDENTITY_FIELDS,
    *_INSTRUMENT_RECOMMENDED_FIELDS,
    *_CORE_MARKET_BOOK_FIELDS,
    *_CORE_MARKET_BOOK_DERIVED_FIELDS,
    *_CONTEXT_ANCHOR_FIELDS,
    *_CONTEXT_ANCHOR_DERIVED_FIELDS,
    *_SESSION_EXPIRY_FIELDS,
    *_LIVE_DERIVED_METRIC_FIELDS,
    *_AUDIT_RUNTIME_FORENSICS_FIELDS,
    *_OFFLINE_DERIVED_PACK_FIELDS,
)

_FIELD_SPECS_BY_NAME_DICT: dict[str, FieldSpec] = {}
for _spec in FIELD_SPECS:
    if _spec.name in _FIELD_SPECS_BY_NAME_DICT:
        raise ValueError(f"Duplicate field contract detected: {_spec.name}")
    _FIELD_SPECS_BY_NAME_DICT[_spec.name] = _spec

FIELD_SPECS_BY_NAME: Mapping[str, FieldSpec] = MappingProxyType(_FIELD_SPECS_BY_NAME_DICT)

FIELDS_BY_LAYER: Mapping[FieldLayer, tuple[FieldSpec, ...]] = MappingProxyType(
    {
        layer: tuple(spec for spec in FIELD_SPECS if spec.layer is layer)
        for layer in FieldLayer
    }
)

FIELDS_BY_GROUP: Mapping[FieldGroup, tuple[FieldSpec, ...]] = MappingProxyType(
    {
        group: tuple(spec for spec in FIELD_SPECS if spec.group is group)
        for group in FieldGroup
    }
)

FIELD_NAMES: tuple[str, ...] = tuple(spec.name for spec in FIELD_SPECS)
RAW_CAPTURE_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name for spec in FIELD_SPECS if spec.compute_stage is RAW
)
LIVE_COMPUTE_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name for spec in FIELD_SPECS if spec.compute_stage is LIVE
)
OFFLINE_COMPUTE_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name for spec in FIELD_SPECS if spec.compute_stage is OFFLINE
)

HOT_STORAGE_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name
    for spec in FIELD_SPECS
    if any(target in {RS, RL} for target in spec.storage_targets)
)
ARCHIVE_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name for spec in FIELD_SPECS if AP in spec.storage_targets
)
MANIFEST_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name for spec in FIELD_SPECS if MJ in spec.storage_targets
)
REPORT_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name for spec in FIELD_SPECS if RA in spec.storage_targets
)

REQUIRED_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name for spec in FIELD_SPECS if spec.requiredness is REQ
)
REQUIRED_RAW_FIELD_NAMES: tuple[str, ...] = tuple(
    spec.name
    for spec in FIELD_SPECS
    if spec.requiredness is REQ and spec.compute_stage is RAW
)

ARCHIVE_OUTPUT_FILENAMES: Mapping[str, str] = MappingProxyType(
    {
        "ticks_fut": TICKS_FUT_FILENAME,
        "ticks_opt": TICKS_OPT_FILENAME,
        "signals_audit": SIGNALS_AUDIT_FILENAME,
        "runtime_audit": RUNTIME_AUDIT_FILENAME,
    }
)

SESSION_FILE_FILENAMES: Mapping[str, str] = MappingProxyType(
    {
        "manifest": MANIFEST_FILENAME,
        "source_availability": SOURCE_AVAILABILITY_FILENAME,
        "integrity_summary": INTEGRITY_SUMMARY_FILENAME,
    }
)


def get_field_spec(name: str) -> FieldSpec:
    """Return the frozen field specification for the requested field name."""
    try:
        return FIELD_SPECS_BY_NAME[name]
    except KeyError as exc:
        raise KeyError(f"Unknown research-capture field: {name}") from exc


def has_field(name: str) -> bool:
    """Return True when a field exists in the frozen capture contract."""
    return name in FIELD_SPECS_BY_NAME


def iter_field_specs() -> Iterator[FieldSpec]:
    """Iterate over all field specifications in canonical order."""
    return iter(FIELD_SPECS)


def iter_field_specs_for_layer(layer: FieldLayer) -> Iterator[FieldSpec]:
    """Iterate over field specifications for one capture layer."""
    return iter(FIELDS_BY_LAYER[layer])


def iter_field_specs_for_group(group: FieldGroup) -> Iterator[FieldSpec]:
    """Iterate over field specifications for one field group."""
    return iter(FIELDS_BY_GROUP[group])


def iter_field_specs_for_storage_target(target: StorageTarget) -> Iterator[FieldSpec]:
    """Iterate over field specifications targeting a specific storage destination."""
    return (spec for spec in FIELD_SPECS if target in spec.storage_targets)


def required_field_names_for_stage(stage: ComputeStage) -> tuple[str, ...]:
    """Return required field names for the selected compute stage."""
    return tuple(
        spec.name
        for spec in FIELD_SPECS
        if spec.requiredness is REQ and spec.compute_stage is stage
    )


def validate_field_names(names: Iterable[str]) -> tuple[str, ...]:
    """
    Validate a collection of field names against the frozen contract.

    Returns the canonicalized tuple in input order. Raises KeyError if any field
    is unknown and ValueError if duplicates are present.
    """
    canonical = tuple(names)
    unknown = tuple(name for name in canonical if name not in FIELD_SPECS_BY_NAME)
    if unknown:
        raise KeyError(f"Unknown research-capture fields: {', '.join(unknown)}")
    duplicates = tuple(
        name for index, name in enumerate(canonical) if name in canonical[:index]
    )
    if duplicates:
        raise ValueError(f"Duplicate research-capture fields: {', '.join(duplicates)}")
    return canonical


def field_dictionary_rows() -> tuple[tuple[str, ...], ...]:
    """Return the canonical field-dictionary rows for CSV or tabular export."""
    return tuple(spec.to_field_dictionary_row() for spec in FIELD_SPECS)


def schema_identity() -> Mapping[str, object]:
    """Return immutable schema identity metadata for manifests and diagnostics."""
    return MappingProxyType(
        {
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "constitution_name": CONSTITUTION_NAME,
            "status": SCHEMA_STATUS,
            "chapter": CHAPTER_NAME,
            "notes": SCHEMA_NOTES,
        }
    )


def archive_contract() -> Mapping[str, object]:
    """Return immutable archive contract metadata for manifests and writers."""
    return MappingProxyType(
        {
            "archive_root_relative": ARCHIVE_ROOT_RELATIVE,
            "format": ARCHIVE_FORMAT,
            "compression": ARCHIVE_COMPRESSION,
            "write_mode": ARCHIVE_WRITE_MODE,
            "primary_partitions": PRIMARY_PARTITIONS,
            "secondary_partitions": SECONDARY_PARTITIONS,
            "archive_outputs": ARCHIVE_OUTPUT_FILENAMES,
            "session_files": SESSION_FILE_FILENAMES,
        }
    )


def _validate_contract_surface() -> None:
    if not FIELD_SPECS:
        raise ValueError("research_capture contract must contain at least one field")
    if len(FIELD_NAMES) != len(set(FIELD_NAMES)):
        raise ValueError("research_capture field names must be globally unique")
    if tuple(sorted(FIELD_NAMES)) != tuple(sorted(FIELD_SPECS_BY_NAME)):
        raise ValueError("research_capture field index mismatch")
    for layer in FieldLayer:
        if not FIELDS_BY_LAYER[layer]:
            raise ValueError(f"research_capture layer has no fields: {layer.value}")
    for required_name in ("exchange_ts", "instrument_token", "tradingsymbol", "ltp", "volume", "schema_version"):
        if required_name not in FIELD_SPECS_BY_NAME:
            raise ValueError(f"critical field missing from contract: {required_name}")
    if MANIFEST_REQUIRED_KEYS[0] != "schema_name":
        raise ValueError("manifest required key ordering drift detected")


_validate_contract_surface()

__all__ = [
    "ARCHIVE_COMPRESSION",
    "ARCHIVE_CONFIG_RELATIVE",
    "ARCHIVE_FORMAT",
    "ARCHIVE_OUTPUT_FILENAMES",
    "ARCHIVE_ROOT_RELATIVE",
    "ARCHIVE_WRITE_MODE",
    "CHAPTER_NAME",
    "CONSTITUTION_NAME",
    "ComputeStage",
    "DOC_CONSTITUTION_RELATIVE",
    "FIELD_DICTIONARY_HEADER",
    "FIELD_DICTIONARY_RELATIVE",
    "FIELD_NAMES",
    "FIELD_SPECS",
    "FIELD_SPECS_BY_NAME",
    "FIELDS_BY_GROUP",
    "FIELDS_BY_LAYER",
    "FieldGroup",
    "FieldLayer",
    "FieldSource",
    "FieldSpec",
    "HOT_STORAGE_FIELD_NAMES",
    "INTEGRITY_SUMMARY_FILENAME",
    "MANIFEST_FILENAME",
    "MANIFEST_REQUIRED_KEYS",
    "PARTITIONS_CONFIG_RELATIVE",
    "PRIMARY_PARTITIONS",
    "REQUIRED_FIELD_NAMES",
    "REQUIRED_RAW_FIELD_NAMES",
    "Requiredness",
    "SCHEMA_NAME",
    "SCHEMA_NOTES",
    "SCHEMA_STATUS",
    "SCHEMA_VERSION",
    "SCHEMA_VERSION_RELATIVE",
    "SECONDARY_PARTITIONS",
    "SESSION_FILE_FILENAMES",
    "SIGNALS_AUDIT_FILENAME",
    "SOURCE_AVAILABILITY_FILENAME",
    "StorageTarget",
    "TICKS_FUT_FILENAME",
    "TICKS_OPT_FILENAME",
    "UsageClass",
    "archive_contract",
    "field_dictionary_rows",
    "get_field_spec",
    "has_field",
    "iter_field_specs",
    "iter_field_specs_for_group",
    "iter_field_specs_for_layer",
    "iter_field_specs_for_storage_target",
    "required_field_names_for_stage",
    "schema_identity",
    "validate_field_names",
]# PASTE THE REAL FULL contracts.py CODE HERE
