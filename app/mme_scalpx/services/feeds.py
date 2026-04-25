from __future__ import annotations

"""
app/mme_scalpx/services/feeds.py

ScalpX MME - provider-aware production feed normalization and publication service.

Purpose
-------
This module OWNS:
- active-universe-only market-data acceptance from approved runtime instruments
- provider-aware normalization of futures ticks, option ticks, and Dhan context
- per-provider latest quote cache for the approved 5-leg live universe
- canonical publication to provider-specific and compatibility streams
- latest-state hash publication for provider-specific and active snapshots
- provider-health derivation for market-data/auth/runtime surfaces
- provider-runtime resolution using canonical config + provider_runtime policy
- feeds singleton lock ownership
- runtime entrypoint ``run(context)``

This module DOES NOT own:
- instrument discovery / ATM resolution
- strike selection / family state machines / strategy decisions
- feature computation such as EMA/OFI/VWAP/regime classification
- broker order placement / reconciliation / execution truth
- Redis helper implementation
- composition root wiring

Frozen runtime rules
--------------------
- no local instrument discovery
- active universe comes only from RuntimeInstrumentSet
- no raw Redis names outside core.names
- shared-wire truth must be canonical and deterministic
- provider selection comes only from integrations.provider_runtime
- compatibility streams / hashes carry only active-provider truth
- provider-specific streams / hashes carry every accepted provider payload
- latest state belongs in hashes; event/history belongs in streams
- Dhan context must publish stale/unavailable truth explicitly; never silently fill defaults
- use context.clock, never a process-global clock singleton
- supervised loop must use context.shutdown.wait(...)
"""

import contextlib
import json
import logging
import math
import os
from collections import deque
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Final, Iterable, Mapping, MutableMapping, Protocol, Sequence

import yaml

from app.mme_scalpx.core import models as M
from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX
from app.mme_scalpx.domain.instruments import ContractMetadata, RuntimeInstrumentSet
from app.mme_scalpx.integrations import provider_runtime as PR

LOGGER = logging.getLogger("app.mme_scalpx.services.feeds")


# =============================================================================
# Required surface validation
# =============================================================================

_REQUIRED_NAME_EXPORTS: Final[tuple[str, ...]] = (
    "SERVICE_FEEDS",
    "STREAM_TICKS_MME_FUT",
    "STREAM_TICKS_MME_OPT",
    "STREAM_TICKS_MME_FUT_ZERODHA",
    "STREAM_TICKS_MME_FUT_DHAN",
    "STREAM_TICKS_MME_OPT_SELECTED_ZERODHA",
    "STREAM_TICKS_MME_OPT_SELECTED_DHAN",
    "STREAM_TICKS_MME_OPT_CONTEXT_DHAN",
    "STREAM_PROVIDER_RUNTIME",
    "STREAM_SYSTEM_HEALTH",
    "STREAM_SYSTEM_ERRORS",
    "HASH_STATE_SNAPSHOT_MME_FUT",
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED",
    "HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA",
    "HASH_STATE_SNAPSHOT_MME_FUT_DHAN",
    "HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE",
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA",
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN",
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE",
    "HASH_STATE_DHAN_CONTEXT",
    "HASH_STATE_PROVIDER_RUNTIME",
    "HASH_STATE_RUNTIME",
    "KEY_HEALTH_FEEDS",
    "KEY_HEALTH_DHAN_AUTH",
    "KEY_HEALTH_DHAN_MARKETDATA",
    "KEY_HEALTH_DHAN_EXECUTION",
    "KEY_HEALTH_ZERODHA_MARKETDATA",
    "KEY_HEALTH_ZERODHA_EXECUTION",
    "KEY_HEALTH_PROVIDER_RUNTIME",
    "KEY_LOCK_FEEDS",
    "HEALTH_STATUS_OK",
    "HEALTH_STATUS_WARN",
    "HEALTH_STATUS_ERROR",
)

_REQUIRED_MODEL_EXPORTS: Final[tuple[str, ...]] = (
    "BookLevel",
    "DhanContextEvent",
    "DhanContextState",
    "FeedTick",
    "FuturesSnapshot",
    "FuturesSnapshotState",
    "OptionSnapshot",
    "OptionSnapshotState",
    "ProviderHealthState",
    "ProviderRuntimeState",
    "ProviderTransitionEvent",
    "RuntimeModeState",
    "SnapshotFrame",
    "SnapshotMember",
    "SnapshotValidity",
    "TickValidity",
)

_REQUIRED_PROVIDER_RUNTIME_EXPORTS: Final[tuple[str, ...]] = (
    "ProviderRuntimeConfig",
    "ProviderRuntimeResolution",
    "resolve_provider_runtime",
)


def _validate_surface_or_die() -> None:
    missing_names = [name for name in _REQUIRED_NAME_EXPORTS if not hasattr(N, name)]
    missing_models = [name for name in _REQUIRED_MODEL_EXPORTS if not hasattr(M, name)]
    missing_pr = [name for name in _REQUIRED_PROVIDER_RUNTIME_EXPORTS if not hasattr(PR, name)]
    if missing_names or missing_models or missing_pr:
        problems: list[str] = []
        if missing_names:
            problems.append("names=" + ", ".join(sorted(missing_names)))
        if missing_models:
            problems.append("models=" + ", ".join(sorted(missing_models)))
        if missing_pr:
            problems.append("provider_runtime=" + ", ".join(sorted(missing_pr)))
        raise RuntimeError("feeds.py missing required frozen surfaces: " + " | ".join(problems))


# =============================================================================
# Locked defaults
# =============================================================================

DEFAULT_HEARTBEAT_INTERVAL_MS = 2_000
DEFAULT_STATE_PUBLISH_INTERVAL_MS = 1_000
DEFAULT_PROVIDER_RUNTIME_PUBLISH_INTERVAL_MS = 1_000
DEFAULT_POLL_INTERVAL_MS = 50
DEFAULT_LOCK_TTL_MS = 30_000
DEFAULT_LOCK_REFRESH_MS = 10_000
DEFAULT_NO_DATA_WARN_AFTER_MS = 3_000
DEFAULT_NO_DATA_ERROR_AFTER_MS = 8_000
DEFAULT_ANOMALY_WINDOW = 32
DEFAULT_ANOMALY_MIN_SAMPLES = 10
DEFAULT_ANOMALY_MEDIAN_TICKS = 8.0
DEFAULT_CONTEXT_STALE_MS = 5_000
DEFAULT_CONTEXT_DEAD_MS = 15_000
DEFAULT_SNAPSHOT_SYNC_MAX_MS = 250
HEALTH_STREAM_MAXLEN = 10_000
ERROR_STREAM_MAXLEN = 10_000
PROVIDER_RUNTIME_STREAM_MAXLEN = 10_000

COMPATIBILITY_ROLE_ORDER: Final[tuple[str, ...]] = (
    M.InstrumentRole.FUTURES,
    M.InstrumentRole.CE_ATM,
    M.InstrumentRole.CE_ATM1,
    M.InstrumentRole.PE_ATM,
    M.InstrumentRole.PE_ATM1,
)

PROVIDER_IDS: Final[tuple[str, ...]] = (
    N.PROVIDER_ZERODHA,
    N.PROVIDER_DHAN,
)


# =============================================================================
# Exceptions
# =============================================================================


class FeedsError(RuntimeError):
    """Base feed service error."""


class FeedConfigError(FeedsError):
    """Raised on invalid feed configuration."""


class FeedValidationError(FeedsError):
    """Raised on invalid runtime or payload state."""


class FeedStartupError(FeedsError):
    """Raised on invalid startup surface."""


# =============================================================================
# Helper protocols
# =============================================================================


class ClockProtocol(Protocol):
    def wall_time_ns(self) -> int: ...


class FeedAdapterProtocol(Protocol):
    def poll(self) -> Iterable[Mapping[str, Any]]: ...


# =============================================================================
# Small helpers
# =============================================================================


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False, default=str)


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = _safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _safe_float(value: Any, default: float = math.nan) -> float:
    if value is None:
        return default
    try:
        text = str(value).strip()
        if text == "":
            return default
        out = float(text)
    except Exception:
        return default
    if math.isnan(out) or math.isinf(out):
        return default
    return out


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        text = str(value).strip()
        if text == "":
            return default
        return int(float(text))
    except Exception:
        return default


def _stream_enum_value(value: Any) -> str:
    return getattr(value, "value", str(value))


def _first_value(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _path_get(mapping: Mapping[str, Any], *path: str) -> Any:
    cur: Any = mapping
    for key in path:
        if not isinstance(cur, Mapping) or key not in cur:
            return None
        cur = cur[key]
    return cur


def _iter_depth_levels(payload: Mapping[str, Any], side: str) -> list[Mapping[str, Any]]:
    # Zerodha style depth: {"depth": {"buy": [...], "sell": [...]}}
    depth = payload.get("depth")
    if isinstance(depth, Mapping):
        if side == "buy":
            levels = depth.get("buy")
        else:
            levels = depth.get("sell")
        if isinstance(levels, Sequence) and not isinstance(levels, (str, bytes, bytearray)):
            return [level for level in levels if isinstance(level, Mapping)]

    # Generic style: {"bids": [...], "asks": [...]} / {"buy": [...], "sell": [...]}
    key = "bids" if side == "buy" else "asks"
    alt_key = "buy" if side == "buy" else "sell"
    for raw_key in (key, alt_key):
        levels = payload.get(raw_key)
        if isinstance(levels, Sequence) and not isinstance(levels, (str, bytes, bytearray)):
            out: list[Mapping[str, Any]] = []
            for level in levels:
                if isinstance(level, Mapping):
                    out.append(level)
                elif isinstance(level, Sequence) and len(level) >= 2:
                    out.append({"price": level[0], "quantity": level[1]})
            return out
    return []


# =============================================================================
# Config surfaces
# =============================================================================


@dataclass(slots=True, frozen=True)
class FeedConfig:
    service_name: str = N.SERVICE_FEEDS
    heartbeat_interval_ms: int = DEFAULT_HEARTBEAT_INTERVAL_MS
    state_publish_interval_ms: int = DEFAULT_STATE_PUBLISH_INTERVAL_MS
    provider_runtime_publish_interval_ms: int = DEFAULT_PROVIDER_RUNTIME_PUBLISH_INTERVAL_MS
    poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS
    lock_ttl_ms: int = DEFAULT_LOCK_TTL_MS
    lock_refresh_ms: int = DEFAULT_LOCK_REFRESH_MS
    no_data_warn_after_ms: int = DEFAULT_NO_DATA_WARN_AFTER_MS
    no_data_error_after_ms: int = DEFAULT_NO_DATA_ERROR_AFTER_MS
    anomaly_window: int = DEFAULT_ANOMALY_WINDOW
    anomaly_min_samples: int = DEFAULT_ANOMALY_MIN_SAMPLES
    anomaly_median_ticks: float = DEFAULT_ANOMALY_MEDIAN_TICKS
    context_stale_ms: int = DEFAULT_CONTEXT_STALE_MS
    context_dead_ms: int = DEFAULT_CONTEXT_DEAD_MS
    snapshot_sync_max_ms: int = DEFAULT_SNAPSHOT_SYNC_MAX_MS
    publish_every_tick: bool = True
    publish_provider_specific_streams: bool = True
    publish_compatibility_streams: bool = True
    publish_runtime_transitions: bool = True

    def __post_init__(self) -> None:
        if self.heartbeat_interval_ms <= 0:
            raise FeedConfigError("heartbeat_interval_ms must be positive")
        if self.state_publish_interval_ms <= 0:
            raise FeedConfigError("state_publish_interval_ms must be positive")
        if self.provider_runtime_publish_interval_ms <= 0:
            raise FeedConfigError("provider_runtime_publish_interval_ms must be positive")
        if self.poll_interval_ms <= 0:
            raise FeedConfigError("poll_interval_ms must be positive")
        if self.lock_ttl_ms <= 0 or self.lock_refresh_ms <= 0:
            raise FeedConfigError("lock TTL/refresh must be positive")
        if self.lock_refresh_ms >= self.lock_ttl_ms:
            raise FeedConfigError("lock_refresh_ms must be smaller than lock_ttl_ms")
        if self.no_data_warn_after_ms <= 0:
            raise FeedConfigError("no_data_warn_after_ms must be positive")
        if self.no_data_error_after_ms <= self.no_data_warn_after_ms:
            raise FeedConfigError(
                "no_data_error_after_ms must be greater than no_data_warn_after_ms"
            )
        if self.anomaly_window < 8:
            raise FeedConfigError("anomaly_window must be >= 8")
        if self.anomaly_min_samples < 4:
            raise FeedConfigError("anomaly_min_samples must be >= 4")
        if self.anomaly_median_ticks <= 0.0:
            raise FeedConfigError("anomaly_median_ticks must be positive")
        if self.context_stale_ms <= 0 or self.context_dead_ms <= self.context_stale_ms:
            raise FeedConfigError("invalid context stale/dead thresholds")
        if self.snapshot_sync_max_ms <= 0:
            raise FeedConfigError("snapshot_sync_max_ms must be positive")


@dataclass(slots=True, frozen=True)
class BrokerProviderSurfaces:
    runtime_yaml: Mapping[str, Any]
    provider_roles_yaml: Mapping[str, Any]
    dhan_yaml: Mapping[str, Any]
    zerodha_yaml: Mapping[str, Any]

    def provider_runtime_config(self) -> PR.ProviderRuntimeConfig:
        runtime = self.runtime_yaml.get("provider_runtime") or {}
        return PR.ProviderRuntimeConfig(
            family_runtime_mode=str(
                runtime.get("family_runtime_mode", N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY)
            ),
            failover_mode=str(
                runtime.get("failover_mode", N.PROVIDER_FAILOVER_MODE_MANUAL)
            ),
            override_mode=str(
                runtime.get("override_mode", N.PROVIDER_OVERRIDE_MODE_AUTO)
            ),
            allow_failback_when_recovered=bool(
                runtime.get("allow_failback_when_recovered", True)
            ),
            require_flat_for_role_switch=bool(
                runtime.get("require_flat_for_role_switch", True)
            ),
            invalidate_preposition_setup_on_switch=bool(
                runtime.get("invalidate_preposition_setup_on_switch", True)
            ),
        )

    def provider_enabled(self, provider_id: str) -> bool:
        cfg = self._provider_yaml(provider_id)
        return bool(cfg.get("enabled", False))

    def provider_capability_enabled(self, provider_id: str, role: str) -> bool:
        cfg = self._provider_yaml(provider_id)
        caps = cfg.get("capabilities") or {}
        if role == N.PROVIDER_ROLE_FUTURES_MARKETDATA:
            return bool(_path_get(caps, "futures_marketdata", "enabled"))
        if role == N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA:
            return bool(_path_get(caps, "selected_option_marketdata", "enabled"))
        if role == N.PROVIDER_ROLE_OPTION_CONTEXT:
            return bool(_path_get(caps, "option_context", "enabled"))
        if role in (N.PROVIDER_ROLE_EXECUTION_PRIMARY, N.PROVIDER_ROLE_EXECUTION_FALLBACK):
            return bool(_path_get(caps, "execution", "enabled"))
        return False

    def stale_after_ms(self, provider_id: str, role: str) -> int:
        cfg = self._provider_yaml(provider_id)
        health = cfg.get("health_contract") or {}
        stale = health.get("stale_after_ms") or {}
        return int(stale.get(role, DEFAULT_CONTEXT_STALE_MS))

    def dead_after_ms(self, provider_id: str, role: str) -> int:
        cfg = self._provider_yaml(provider_id)
        health = cfg.get("health_contract") or {}
        dead = health.get("dead_after_ms") or {}
        return int(dead.get(role, DEFAULT_CONTEXT_DEAD_MS))

    def miso_requires_dhan_option_context(self) -> bool:
        return bool(
            _path_get(self.provider_roles_yaml, "provider_role_laws", "miso_requires_dhan_option_context")
        )

    def miso_requires_dhan_selected_option_marketdata(self) -> bool:
        return bool(
            _path_get(
                self.provider_roles_yaml,
                "provider_role_laws",
                "miso_requires_dhan_selected_option_marketdata",
            )
        )

    def _provider_yaml(self, provider_id: str) -> Mapping[str, Any]:
        if provider_id == N.PROVIDER_DHAN:
            return self.dhan_yaml
        if provider_id == N.PROVIDER_ZERODHA:
            return self.zerodha_yaml
        raise FeedConfigError(f"unknown provider id in broker config: {provider_id!r}")


@dataclass(slots=True, frozen=True)
class ApprovedInstrument:
    role: str
    instrument_key: str
    instrument_token: str
    trading_symbol: str
    tick_size: Decimal
    lot_size: int
    strike: Decimal | None
    expiry_iso: str | None
    option_side: str | None

    @staticmethod
    def from_contract(role: str, contract: ContractMetadata) -> "ApprovedInstrument":
        try:
            tick_size = Decimal(str(getattr(contract, "tick_size")))
            if tick_size <= 0:
                raise ValueError("tick_size must be positive")
            lot_size = int(getattr(contract, "lot_size"))
            if lot_size <= 0:
                raise ValueError("lot_size must be positive")
            trading_symbol = str(getattr(contract, "tradingsymbol"))
            instrument_key = _safe_str(getattr(contract, "instrument_key", None))
            if not instrument_key:
                instrument_key = _safe_str(getattr(contract, "key", None))
            if not instrument_key:
                instrument_key = f"NFO:{trading_symbol}"
            strike_obj = getattr(contract, "strike", None)
            strike = None if strike_obj is None else Decimal(str(strike_obj))
            expiry = getattr(contract, "expiry", None)
            option_side = None
            if role.startswith("CE_") or role.startswith("CE"):
                option_side = N.SIDE_CALL
            elif role.startswith("PE_") or role.startswith("PE"):
                option_side = N.SIDE_PUT
            return ApprovedInstrument(
                role=role,
                instrument_key=instrument_key,
                instrument_token=str(getattr(contract, "instrument_token")),
                trading_symbol=trading_symbol,
                tick_size=tick_size,
                lot_size=lot_size,
                strike=strike,
                expiry_iso=None if expiry is None else str(expiry.isoformat()),
                option_side=option_side,
            )
        except Exception as exc:
            raise FeedValidationError(
                f"invalid contract metadata for role={role}: {exc}"
            ) from exc


@dataclass(slots=True, frozen=True)
class ActiveUniverse:
    selection_version: str
    generated_at_ns: int
    underlying_symbol: str
    underlying_reference: Decimal
    option_expiry_iso: str
    strike_step: Decimal
    instruments: tuple[ApprovedInstrument, ...]

    @staticmethod
    def from_runtime_set(
        runtime_set: RuntimeInstrumentSet,
        *,
        generated_at_ns: int,
    ) -> "ActiveUniverse":
        try:
            instruments = (
                ApprovedInstrument.from_contract(M.InstrumentRole.FUTURES, runtime_set.current_future),
                ApprovedInstrument.from_contract(M.InstrumentRole.CE_ATM, runtime_set.ce_atm),
                ApprovedInstrument.from_contract(M.InstrumentRole.CE_ATM1, runtime_set.ce_atm1),
                ApprovedInstrument.from_contract(M.InstrumentRole.PE_ATM, runtime_set.pe_atm),
                ApprovedInstrument.from_contract(M.InstrumentRole.PE_ATM1, runtime_set.pe_atm1),
            )
            return ActiveUniverse(
                selection_version=str(runtime_set.selection_version),
                generated_at_ns=int(generated_at_ns),
                underlying_symbol=str(runtime_set.underlying_symbol),
                underlying_reference=Decimal(str(runtime_set.underlying_reference)),
                option_expiry_iso=str(runtime_set.option_expiry.isoformat()),
                strike_step=Decimal(str(runtime_set.strike_step)),
                instruments=instruments,
            )
        except Exception as exc:
            raise FeedValidationError(f"failed to construct active universe: {exc}") from exc

    def instrument_by_token(self) -> dict[str, ApprovedInstrument]:
        return {ins.instrument_token: ins for ins in self.instruments}

    def instrument_by_role(self) -> dict[str, ApprovedInstrument]:
        return {ins.role: ins for ins in self.instruments}


@dataclass(slots=True, frozen=True)
class ProviderAdapterSurface:
    provider_id: str
    adapter: FeedAdapterProtocol
    context_only: bool = False


@dataclass(slots=True, frozen=True)
class BrokerRawTick:
    instrument_token: str
    provider_id: str
    payload: Mapping[str, Any]
    recv_ts_ns: int


@dataclass(slots=True, frozen=True)
class RawDhanContext:
    provider_id: str
    payload: Mapping[str, Any]
    recv_ts_ns: int


@dataclass(slots=True)
class QuoteCacheEntry:
    approved: ApprovedInstrument
    provider_id: str
    last_event_ns: int = 0
    last_provider_ns: int = 0
    ltp: float = math.nan
    best_bid: float = math.nan
    best_ask: float = math.nan
    bid_qty: int = 0
    ask_qty: int = 0
    bid_qty_5: int = 0
    ask_qty_5: int = 0
    volume: int = 0
    oi: int = 0
    last_qty: int = 0
    seq_no: int = 0
    bids: tuple[M.BookLevel, ...] = ()
    asks: tuple[M.BookLevel, ...] = ()
    last_validity: str = M.TickValidity.MALFORMED
    last_validity_reason: str = "not_seen"
    anomaly_window: deque[float] = field(default_factory=deque)

    def age_ms(self, *, now_ns: int) -> int:
        if self.last_event_ns <= 0:
            return 10**9
        return max(int((now_ns - self.last_event_ns) / 1_000_000), 0)


@dataclass(slots=True)
class ProviderRoleWatermark:
    provider_id: str
    role: str
    last_seen_ns: int = 0
    last_status: str = N.HEALTH_STATUS_WARN


@dataclass(slots=True)
class FeedCounters:
    ticks_received_total: int = 0
    ticks_accepted_total: int = 0
    ticks_rejected_total: int = 0
    futures_ticks_total: int = 0
    option_ticks_total: int = 0
    context_events_total: int = 0
    provider_transitions_total: int = 0
    state_publishes_total: int = 0
    heartbeats_total: int = 0


@dataclass(slots=True, frozen=True)
class FeedState:
    selection_version: str
    ts_ns: int
    approved_tokens: int
    seen_tokens_zerodha: int
    seen_tokens_dhan: int
    active_futures_provider_id: str
    active_selected_option_provider_id: str
    active_option_context_provider_id: str
    active_execution_primary_provider_id: str
    active_execution_fallback_provider_id: str
    provider_transition_seq: int
    failover_active: bool
    pending_failover: bool
    last_runtime_reason: str
    latest_context_status: str
    ticks_received_total: int
    ticks_accepted_total: int
    ticks_rejected_total: int
    futures_ticks_total: int
    option_ticks_total: int
    context_events_total: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# =============================================================================
# YAML config loading
# =============================================================================


def _load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FeedStartupError(f"broker config file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise FeedStartupError(f"failed to parse YAML {path}: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise FeedStartupError(f"YAML config must be mapping: {path}")
    return dict(raw)


def load_broker_provider_surfaces(base_dir: str | Path) -> BrokerProviderSurfaces:
    base = Path(base_dir)
    runtime_yaml = _load_yaml_file(base / "runtime.yaml")
    provider_roles_yaml = _load_yaml_file(base / "provider_roles.yaml")
    dhan_yaml = _load_yaml_file(base / "dhan.yaml")
    zerodha_yaml = _load_yaml_file(base / "zerodha.yaml")
    return BrokerProviderSurfaces(
        runtime_yaml=runtime_yaml,
        provider_roles_yaml=provider_roles_yaml,
        dhan_yaml=dhan_yaml,
        zerodha_yaml=zerodha_yaml,
    )


# =============================================================================
# Normalization helpers
# =============================================================================


class TickNormalizer:
    def __init__(self, *, config: FeedConfig, logger: logging.Logger | None = None) -> None:
        self._cfg = config
        self._log = logger or LOGGER.getChild("TickNormalizer")

    def normalize_tick(
        self,
        *,
        raw: BrokerRawTick,
        approved: ApprovedInstrument,
        cache_entry: QuoteCacheEntry,
        now_ns: int,
    ) -> tuple[M.FeedTick, M.FuturesSnapshot | M.OptionSnapshot]:
        payload = dict(raw.payload)
        provider_ns = self._extract_provider_ts_ns(payload) or raw.recv_ts_ns
        seq_no = _safe_int(_first_value(payload, "seq_no", "sequence", "seq", "token_seq"), 0) or None
        ltp = _safe_float(_first_value(payload, "ltp", "last_price", "LTP", "price"), math.nan)
        last_qty = _safe_int(_first_value(payload, "last_qty", "ltq", "last_traded_qty"), 0) or None
        volume = _safe_int(_first_value(payload, "volume", "vol", "total_volume"), 0) or None
        oi = _safe_int(_first_value(payload, "oi", "open_interest"), 0) or None
        bid = _safe_float(_first_value(payload, "best_bid", "bid", "bbid"), math.nan)
        ask = _safe_float(_first_value(payload, "best_ask", "ask", "bask"), math.nan)
        bid_qty = _safe_int(_first_value(payload, "best_bid_qty", "bid_qty", "bbid_qty"), 0) or None
        ask_qty = _safe_int(_first_value(payload, "best_ask_qty", "ask_qty", "bask_qty"), 0) or None

        bids = self._extract_book_levels(payload, side="buy")
        asks = self._extract_book_levels(payload, side="sell")

        if bids and (math.isnan(bid) or bid <= 0.0):
            bid = bids[0].price
        if asks and (math.isnan(ask) or ask <= 0.0):
            ask = asks[0].price
        if bids and (bid_qty is None or bid_qty <= 0):
            bid_qty = bids[0].quantity
        if asks and (ask_qty is None or ask_qty <= 0):
            ask_qty = asks[0].quantity

        bid, ask, bid_qty, ask_qty, incomplete_quote = self._merge_quote(
            bid=bid,
            ask=ask,
            bid_qty=bid_qty,
            ask_qty=ask_qty,
            cache_entry=cache_entry,
        )

        bid_qty_5 = sum(level.quantity for level in bids[:5]) if bids else max(int(bid_qty or 0), 0)
        ask_qty_5 = sum(level.quantity for level in asks[:5]) if asks else max(int(ask_qty or 0), 0)

        validity = M.TickValidity.OK
        reason = "ok"
        if math.isnan(ltp):
            validity = M.TickValidity.MISSING_LTP
            reason = "ltp_missing"
        elif ltp <= 0.0:
            validity = M.TickValidity.NON_POSITIVE_LTP
            reason = "ltp_non_positive"
        elif bid_qty_5 < 0 or ask_qty_5 < 0:
            validity = M.TickValidity.NEGATIVE_QUANTITY
            reason = "negative_qty"
        elif incomplete_quote:
            validity = M.TickValidity.INCOMPLETE_QUOTE
            reason = "quote_incomplete"

        tick_size = float(approved.tick_size)
        if tick_size <= 0.0:
            validity = M.TickValidity.BAD_TICK_SIZE
            reason = "tick_size_non_positive"

        if validity == M.TickValidity.OK and bid > 0.0 and ask > 0.0 and ask < bid:
            validity = M.TickValidity.NON_POSITIVE_SPREAD
            reason = "ask_below_bid"

        if validity == M.TickValidity.OK and not self._passes_anomaly_clamp(
            cache_entry=cache_entry,
            role=approved.role,
            ltp=ltp,
            tick_size=tick_size,
            best_bid=bid,
            best_ask=ask,
        ):
            validity = M.TickValidity.ANOMALY_CLAMPED
            reason = "ltp_anomaly_clamped"

        age_ms = max(int((now_ns - provider_ns) / 1_000_000), 0)

        feed_tick = M.FeedTick(
            instrument_key=approved.instrument_key,
            instrument_role=approved.role,
            ts_event_ns=provider_ns,
            provider_id=raw.provider_id,
            provider_role=(
                N.PROVIDER_ROLE_FUTURES_MARKETDATA
                if approved.role == M.InstrumentRole.FUTURES
                else N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA
            ),
            exchange="NFO",
            instrument_token=approved.instrument_token,
            trading_symbol=approved.trading_symbol,
            ts_provider_ns=provider_ns,
            ts_recv_ns=raw.recv_ts_ns,
            seq_no=seq_no,
            ltp=None if math.isnan(ltp) else ltp,
            last_qty=last_qty,
            volume=volume,
            oi=oi,
            bid=None if math.isnan(bid) else bid,
            ask=None if math.isnan(ask) else ask,
            bid_qty=bid_qty,
            ask_qty=ask_qty,
            bids=bids,
            asks=asks,
            option_side=approved.option_side,
            strike=None if approved.strike is None else float(approved.strike),
            expiry=approved.expiry_iso,
            tick_validity=validity,
            reject_reason=None if validity == M.TickValidity.OK else reason,
            is_selected_option=False,
            is_shadow_option=False,
        )

        if approved.role == M.InstrumentRole.FUTURES:
            snapshot: M.FuturesSnapshot | M.OptionSnapshot = M.FuturesSnapshot(
                instrument_key=approved.instrument_key,
                ts_event_ns=provider_ns,
                ltp=max(ltp, 0.0) if not math.isnan(ltp) else 0.0,
                provider_id=raw.provider_id,
                provider_role=N.PROVIDER_ROLE_FUTURES_MARKETDATA,
                instrument_token=approved.instrument_token,
                trading_symbol=approved.trading_symbol,
                ts_provider_ns=provider_ns,
                ts_recv_ns=raw.recv_ts_ns,
                last_qty=last_qty,
                volume=volume,
                oi=oi,
                bid=None if math.isnan(bid) else bid,
                ask=None if math.isnan(ask) else ask,
                bid_qty=bid_qty,
                ask_qty=ask_qty,
                bids=bids,
                asks=asks,
                seq_no=seq_no,
            )
        else:
            delta_proxy = _safe_float(_first_value(payload, "delta_proxy", "delta"), math.nan)
            snapshot = M.OptionSnapshot(
                instrument_key=approved.instrument_key,
                ts_event_ns=provider_ns,
                option_side=approved.option_side or N.SIDE_CALL,
                strike=float(approved.strike) if approved.strike is not None else 0.0,
                expiry=approved.expiry_iso,
                ltp=max(ltp, 0.0) if not math.isnan(ltp) else 0.0,
                provider_id=raw.provider_id,
                provider_role=N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
                instrument_token=approved.instrument_token,
                trading_symbol=approved.trading_symbol,
                ts_provider_ns=provider_ns,
                ts_recv_ns=raw.recv_ts_ns,
                last_qty=last_qty,
                volume=volume,
                oi=oi,
                bid=None if math.isnan(bid) else bid,
                ask=None if math.isnan(ask) else ask,
                bid_qty=bid_qty,
                ask_qty=ask_qty,
                bids=bids,
                asks=asks,
                delta_proxy=None if math.isnan(delta_proxy) else delta_proxy,
                seq_no=seq_no,
                is_selected_option=False,
                is_shadow_option=False,
            )

        return feed_tick, snapshot

    def normalize_dhan_context(
        self,
        *,
        raw: RawDhanContext,
        now_ns: int,
    ) -> tuple[M.DhanContextEvent, M.DhanContextState]:
        payload = dict(raw.payload)
        provider_ns = self._extract_provider_ts_ns(payload) or raw.recv_ts_ns

        call_components = self._build_score_components(payload, side="call")
        put_components = self._build_score_components(payload, side="put")

        event = M.DhanContextEvent(
            ts_event_ns=provider_ns,
            provider_id=N.PROVIDER_DHAN,
            context_status=self._derive_context_status(payload, now_ns=now_ns, provider_ns=provider_ns),
            atm_strike=_safe_float(_first_value(payload, "atm_strike", "atm"), math.nan),
            selected_call_instrument_key=_safe_str(_first_value(payload, "selected_call_instrument_key", "call_instrument_key")) or None,
            selected_put_instrument_key=_safe_str(_first_value(payload, "selected_put_instrument_key", "put_instrument_key")) or None,
            selected_call_score=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_score", "call_score"), math.nan)),
            selected_put_score=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_score", "put_score"), math.nan)),
            selected_call_delta=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_delta", "call_delta"), math.nan)),
            selected_put_delta=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_delta", "put_delta"), math.nan)),
            selected_call_authoritative_delta=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_authoritative_delta", "call_authoritative_delta"), math.nan)),
            selected_put_authoritative_delta=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_authoritative_delta", "put_authoritative_delta"), math.nan)),
            selected_call_gamma=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_gamma", "call_gamma"), math.nan)),
            selected_put_gamma=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_gamma", "put_gamma"), math.nan)),
            selected_call_theta=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_theta", "call_theta"), math.nan)),
            selected_put_theta=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_theta", "put_theta"), math.nan)),
            selected_call_vega=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_vega", "call_vega"), math.nan)),
            selected_put_vega=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_vega", "put_vega"), math.nan)),
            selected_call_iv=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_iv", "call_iv"), math.nan)),
            selected_put_iv=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_iv", "put_iv"), math.nan)),
            selected_call_iv_change_1m_pct=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_iv_change_1m_pct", "call_iv_change_1m_pct", "call_iv_change"), math.nan)),
            selected_put_iv_change_1m_pct=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_iv_change_1m_pct", "put_iv_change_1m_pct", "put_iv_change"), math.nan)),
            selected_call_oi=_safe_int(_first_value(payload, "selected_call_oi", "call_oi"), 0) or None,
            selected_put_oi=_safe_int(_first_value(payload, "selected_put_oi", "put_oi"), 0) or None,
            selected_call_oi_change=_safe_int(_first_value(payload, "selected_call_oi_change", "call_oi_change"), 0) or None,
            selected_put_oi_change=_safe_int(_first_value(payload, "selected_put_oi_change", "put_oi_change"), 0) or None,
            selected_call_volume=_safe_int(_first_value(payload, "selected_call_volume", "call_volume"), 0) or None,
            selected_put_volume=_safe_int(_first_value(payload, "selected_put_volume", "put_volume"), 0) or None,
            selected_call_cross_strike_spread_rank=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_cross_strike_spread_rank", "call_cross_strike_spread_rank"), math.nan)),
            selected_put_cross_strike_spread_rank=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_cross_strike_spread_rank", "put_cross_strike_spread_rank"), math.nan)),
            selected_call_cross_strike_volume_rank=self._none_if_nan(_safe_float(_first_value(payload, "selected_call_cross_strike_volume_rank", "call_cross_strike_volume_rank"), math.nan)),
            selected_put_cross_strike_volume_rank=self._none_if_nan(_safe_float(_first_value(payload, "selected_put_cross_strike_volume_rank", "put_cross_strike_volume_rank"), math.nan)),
            selected_call_score_components=call_components,
            selected_put_score_components=put_components,
            message=_safe_str(payload.get("message")) or None,
        )

        state = M.DhanContextState(
            ts_event_ns=event.ts_event_ns,
            provider_id=event.provider_id,
            context_status=event.context_status,
            atm_strike=event.atm_strike,
            selected_call_instrument_key=event.selected_call_instrument_key,
            selected_put_instrument_key=event.selected_put_instrument_key,
            selected_call_score=event.selected_call_score,
            selected_put_score=event.selected_put_score,
            selected_call_delta=event.selected_call_delta,
            selected_put_delta=event.selected_put_delta,
            selected_call_authoritative_delta=event.selected_call_authoritative_delta,
            selected_put_authoritative_delta=event.selected_put_authoritative_delta,
            selected_call_gamma=event.selected_call_gamma,
            selected_put_gamma=event.selected_put_gamma,
            selected_call_theta=event.selected_call_theta,
            selected_put_theta=event.selected_put_theta,
            selected_call_vega=event.selected_call_vega,
            selected_put_vega=event.selected_put_vega,
            selected_call_iv=event.selected_call_iv,
            selected_put_iv=event.selected_put_iv,
            selected_call_iv_change_1m_pct=event.selected_call_iv_change_1m_pct,
            selected_put_iv_change_1m_pct=event.selected_put_iv_change_1m_pct,
            selected_call_oi=event.selected_call_oi,
            selected_put_oi=event.selected_put_oi,
            selected_call_oi_change=event.selected_call_oi_change,
            selected_put_oi_change=event.selected_put_oi_change,
            selected_call_volume=event.selected_call_volume,
            selected_put_volume=event.selected_put_volume,
            selected_call_cross_strike_spread_rank=event.selected_call_cross_strike_spread_rank,
            selected_put_cross_strike_spread_rank=event.selected_put_cross_strike_spread_rank,
            selected_call_cross_strike_volume_rank=event.selected_call_cross_strike_volume_rank,
            selected_put_cross_strike_volume_rank=event.selected_put_cross_strike_volume_rank,
            selected_call_spread_score=call_components.spread_score if call_components else None,
            selected_put_spread_score=put_components.spread_score if put_components else None,
            selected_call_depth_score=call_components.depth_score if call_components else None,
            selected_put_depth_score=put_components.depth_score if put_components else None,
            selected_call_volume_score=call_components.volume_score if call_components else None,
            selected_put_volume_score=put_components.volume_score if put_components else None,
            selected_call_oi_score=call_components.oi_score if call_components else None,
            selected_put_oi_score=put_components.oi_score if put_components else None,
            selected_call_iv_score=call_components.iv_score if call_components else None,
            selected_put_iv_score=put_components.iv_score if put_components else None,
            selected_call_delta_score=call_components.delta_score if call_components else None,
            selected_put_delta_score=put_components.delta_score if put_components else None,
            selected_call_gamma_score=call_components.gamma_score if call_components else None,
            selected_put_gamma_score=put_components.gamma_score if put_components else None,
            selected_call_iv_sanity_score=call_components.iv_sanity_score if call_components else None,
            selected_put_iv_sanity_score=put_components.iv_sanity_score if put_components else None,
            last_update_ns=now_ns,
            message=event.message,
        )
        return event, state

    @staticmethod
    def _none_if_nan(value: float) -> float | None:
        return None if math.isnan(value) else value

    def _derive_context_status(self, payload: Mapping[str, Any], *, now_ns: int, provider_ns: int) -> str:
        explicit = _safe_str(_first_value(payload, "context_status", "status")).upper()
        if explicit in N.ALLOWED_PROVIDER_STATUSES:
            return explicit
        age_ms = max(int((now_ns - provider_ns) / 1_000_000), 0)
        if age_ms > self._cfg.context_dead_ms:
            return N.PROVIDER_STATUS_UNAVAILABLE
        if age_ms > self._cfg.context_stale_ms:
            return N.PROVIDER_STATUS_STALE
        return N.PROVIDER_STATUS_HEALTHY

    def _build_score_components(
        self,
        payload: Mapping[str, Any],
        *,
        side: str,
    ) -> M.DhanStrikeScoreComponents | None:
        prefix = "call" if side == "call" else "put"
        fields = {
            "spread_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_spread_score", payload.get(f"{prefix}_spread_score")), math.nan)),
            "depth_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_depth_score", payload.get(f"{prefix}_depth_score")), math.nan)),
            "volume_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_volume_score", payload.get(f"{prefix}_volume_score")), math.nan)),
            "oi_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_oi_score", payload.get(f"{prefix}_oi_score")), math.nan)),
            "iv_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_iv_score", payload.get(f"{prefix}_iv_score")), math.nan)),
            "delta_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_delta_score", payload.get(f"{prefix}_delta_score")), math.nan)),
            "gamma_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_gamma_score", payload.get(f"{prefix}_gamma_score")), math.nan)),
            "iv_sanity_score": self._none_if_nan(_safe_float(payload.get(f"selected_{prefix}_iv_sanity_score", payload.get(f"{prefix}_iv_sanity_score")), math.nan)),
        }
        if all(value is None for value in fields.values()):
            return None
        return M.DhanStrikeScoreComponents(**fields)

    @staticmethod
    def _extract_provider_ts_ns(payload: Mapping[str, Any]) -> int | None:
        raw = _first_value(payload, "provider_ts_ns", "exchange_ts_ns", "exch_ts_ns", "ts_ns", "provider_ts", "exchange_ts", "ts")
        if raw is None:
            return None
        val = _safe_int(raw, 0)
        if val <= 0:
            return None
        if val < 10_000_000_000:
            return val * 1_000_000_000
        if val < 10_000_000_000_000:
            return val * 1_000_000
        if val < 10_000_000_000_000_000:
            return val * 1_000
        return val

    def _extract_book_levels(self, payload: Mapping[str, Any], *, side: str) -> tuple[M.BookLevel, ...]:
        out: list[M.BookLevel] = []
        for level in _iter_depth_levels(payload, side):
            price = _safe_float(_first_value(level, "price", "p"), math.nan)
            quantity = _safe_int(_first_value(level, "quantity", "qty", "q"), -1)
            orders = _safe_int(_first_value(level, "orders", "count", "o"), -1)
            if math.isnan(price) or price <= 0.0 or quantity < 0:
                continue
            out.append(
                M.BookLevel(
                    price=price,
                    quantity=quantity,
                    orders=None if orders < 0 else orders,
                )
            )
        return tuple(out)

    @staticmethod
    def _merge_quote(
        *,
        bid: float,
        ask: float,
        bid_qty: int | None,
        ask_qty: int | None,
        cache_entry: QuoteCacheEntry,
    ) -> tuple[float, float, int | None, int | None, bool]:
        out_bid = bid if bid > 0.0 and not math.isnan(bid) else cache_entry.best_bid
        out_ask = ask if ask > 0.0 and not math.isnan(ask) else cache_entry.best_ask
        out_bq = bid_qty if bid_qty is not None and bid_qty > 0 else cache_entry.bid_qty
        out_aq = ask_qty if ask_qty is not None and ask_qty > 0 else cache_entry.ask_qty
        incomplete = math.isnan(out_bid) or math.isnan(out_ask) or out_bid <= 0.0 or out_ask <= 0.0
        return out_bid, out_ask, out_bq, out_aq, incomplete

    def _passes_anomaly_clamp(
        self,
        *,
        cache_entry: QuoteCacheEntry,
        role: str,
        ltp: float,
        tick_size: float,
        best_bid: float,
        best_ask: float,
    ) -> bool:
        if math.isnan(ltp) or ltp <= 0.0:
            return True
        is_futures = str(role).upper().endswith("FUTURES")
        tick_unit = max(tick_size, 1e-9)
        envelope_ticks = 8.0 if is_futures else 12.0
        median_ticks = float(self._cfg.anomaly_median_ticks) * (2.0 if is_futures else 3.0)

        if (
            not math.isnan(best_bid)
            and not math.isnan(best_ask)
            and best_bid > 0.0
            and best_ask > 0.0
            and best_ask >= best_bid
        ):
            envelope_pad = envelope_ticks * tick_unit
            if (best_bid - envelope_pad) <= ltp <= (best_ask + envelope_pad):
                dq = cache_entry.anomaly_window
                if dq.maxlen is None or dq.maxlen != self._cfg.anomaly_window:
                    dq = deque(dq, maxlen=self._cfg.anomaly_window)
                    cache_entry.anomaly_window = dq
                dq.append(ltp)
                return True

        dq = cache_entry.anomaly_window
        if dq.maxlen is None or dq.maxlen != self._cfg.anomaly_window:
            dq = deque(dq, maxlen=self._cfg.anomaly_window)
            cache_entry.anomaly_window = dq
        dq.append(ltp)
        if len(dq) < self._cfg.anomaly_min_samples:
            return True
        median = sorted(dq)[len(dq) // 2]
        return abs(ltp - median) <= (median_ticks * tick_unit)


# =============================================================================
# Snapshot assembly
# =============================================================================


class SnapshotAssembler:
    def __init__(self, *, logger: logging.Logger | None = None) -> None:
        self._log = logger or LOGGER.getChild("SnapshotAssembler")

    def build_frame(
        self,
        *,
        universe: ActiveUniverse,
        cache_by_token: Mapping[str, QuoteCacheEntry],
        now_ns: int,
        stale_after_ms: int,
        sync_tolerance_ms: int,
    ) -> M.SnapshotFrame:
        ins_by_role = universe.instrument_by_role()
        future = self._member_from_cache(ins_by_role.get(M.InstrumentRole.FUTURES), cache_by_token, now_ns, stale_after_ms)
        ce_atm = self._member_from_cache(ins_by_role.get(M.InstrumentRole.CE_ATM), cache_by_token, now_ns, stale_after_ms)
        ce_atm1 = self._member_from_cache(ins_by_role.get(M.InstrumentRole.CE_ATM1), cache_by_token, now_ns, stale_after_ms)
        pe_atm = self._member_from_cache(ins_by_role.get(M.InstrumentRole.PE_ATM), cache_by_token, now_ns, stale_after_ms)
        pe_atm1 = self._member_from_cache(ins_by_role.get(M.InstrumentRole.PE_ATM1), cache_by_token, now_ns, stale_after_ms)

        missing = [
            role_name
            for role_name, member in (
                ("future", future),
                ("ce_atm", ce_atm),
                ("ce_atm1", ce_atm1),
                ("pe_atm", pe_atm),
                ("pe_atm1", pe_atm1),
            )
            if member is None
        ]
        if missing:
            return M.SnapshotFrame(
                frame_id=f"frame-{now_ns}",
                selection_version=universe.selection_version,
                ts_frame_ns=now_ns,
                ts_min_member_ns=0,
                ts_max_member_ns=0,
                ts_span_ms=0,
                validity=M.SnapshotValidity.INCOMPLETE,
                validity_reason=f"missing_members:{','.join(missing)}",
                sync_ok=False,
                stale_mask=tuple(),
                future=future,
                ce_atm=ce_atm,
                ce_atm1=ce_atm1,
                pe_atm=pe_atm,
                pe_atm1=pe_atm1,
            )

        assert future is not None and ce_atm is not None and ce_atm1 is not None and pe_atm is not None and pe_atm1 is not None
        members = [future, ce_atm, ce_atm1, pe_atm, pe_atm1]
        invalid_members = [str(m.role) for m in members if m.validity != M.TickValidity.OK]
        stale_members = [str(m.role) for m in members if m.age_ms > stale_after_ms]
        member_ts = [m.ts_event_ns for m in members]
        ts_min = min(member_ts)
        ts_max = max(member_ts)
        span_ms = int((ts_max - ts_min) / 1_000_000)
        sync_ok = span_ms <= sync_tolerance_ms
        validity = M.SnapshotValidity.OK
        reason = "ok"
        if invalid_members:
            validity = M.SnapshotValidity.INVALID_MEMBER
            reason = f"invalid_members:{','.join(invalid_members)}"
        elif stale_members:
            validity = M.SnapshotValidity.STALE
            reason = f"stale_members:{','.join(stale_members)}"
        elif not sync_ok:
            validity = M.SnapshotValidity.UNSYNCED
            reason = f"unsynced:span_ms={span_ms}"

        return M.SnapshotFrame(
            frame_id=f"frame-{now_ns}",
            selection_version=universe.selection_version,
            ts_frame_ns=now_ns,
            ts_min_member_ns=ts_min,
            ts_max_member_ns=ts_max,
            ts_span_ms=span_ms,
            validity=validity,
            validity_reason=reason,
            sync_ok=sync_ok,
            stale_mask=tuple(stale_members),
            future=future,
            ce_atm=ce_atm,
            ce_atm1=ce_atm1,
            pe_atm=pe_atm,
            pe_atm1=pe_atm1,
        )

    @staticmethod
    def _member_from_cache(
        approved: ApprovedInstrument | None,
        cache_by_token: Mapping[str, QuoteCacheEntry],
        now_ns: int,
        stale_after_ms: int,
    ) -> M.SnapshotMember | None:
        if approved is None:
            return None
        cache = cache_by_token.get(approved.instrument_token)
        if cache is None or cache.last_event_ns <= 0 or math.isnan(cache.ltp) or cache.ltp <= 0.0:
            return None
        age_ms = cache.age_ms(now_ns=now_ns)
        validity = cache.last_validity if age_ms <= stale_after_ms else M.TickValidity.STALE
        spread = 0.0
        spread_ticks = 0.0
        if cache.best_ask > 0.0 and cache.best_bid > 0.0:
            spread = max(cache.best_ask - cache.best_bid, 0.0)
            spread_ticks = spread / float(approved.tick_size)
        return M.SnapshotMember(
            role=approved.role,
            instrument_token=approved.instrument_token,
            trading_symbol=approved.trading_symbol,
            ts_event_ns=cache.last_event_ns,
            ltp=cache.ltp,
            best_bid=0.0 if math.isnan(cache.best_bid) else cache.best_bid,
            best_ask=0.0 if math.isnan(cache.best_ask) else cache.best_ask,
            bid_qty_5=max(cache.bid_qty_5, 0),
            ask_qty_5=max(cache.ask_qty_5, 0),
            spread=spread,
            spread_ticks=spread_ticks,
            age_ms=age_ms,
            tick_size=float(approved.tick_size),
            lot_size=approved.lot_size,
            strike=None if approved.strike is None else float(approved.strike),
            validity=validity,
        )


# =============================================================================
# Feed service
# =============================================================================


class FeedService:
    REQUIRED_ROLE_COUNT = 5

    def __init__(
        self,
        *,
        universe: ActiveUniverse,
        config: FeedConfig,
        broker_surfaces: BrokerProviderSurfaces,
        redis_client: Any,
        clock: ClockProtocol,
        instance_id: str,
        logger: logging.Logger | None = None,
    ) -> None:
        self._cfg = config
        self._broker_surfaces = broker_surfaces
        self._provider_runtime_config = broker_surfaces.provider_runtime_config()
        self._clock = clock
        self._redis = redis_client
        self._instance_id = instance_id
        self._log = logger or LOGGER.getChild(config.service_name)
        self._universe = universe
        self._token_to_approved = universe.instrument_by_token()
        if len(self._token_to_approved) != self.REQUIRED_ROLE_COUNT:
            raise FeedConfigError(
                f"active universe must contain exactly {self.REQUIRED_ROLE_COUNT} contracts; got {len(self._token_to_approved)}"
            )
        self._normalizer = TickNormalizer(config=config, logger=self._log)
        self._assembler = SnapshotAssembler(logger=self._log)
        self._counters = FeedCounters()
        self._provider_caches: dict[str, dict[str, QuoteCacheEntry]] = {
            provider_id: {
                token: QuoteCacheEntry(
                    approved=approved,
                    provider_id=provider_id,
                    anomaly_window=deque(maxlen=self._cfg.anomaly_window),
                )
                for token, approved in self._token_to_approved.items()
            }
            for provider_id in PROVIDER_IDS
        }
        self._role_watermarks: dict[tuple[str, str], ProviderRoleWatermark] = {
            (provider_id, role): ProviderRoleWatermark(provider_id=provider_id, role=role)
            for provider_id in PROVIDER_IDS
            for role in (
                N.PROVIDER_ROLE_FUTURES_MARKETDATA,
                N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
                N.PROVIDER_ROLE_OPTION_CONTEXT,
            )
        }
        self._adapter_health_hints: dict[str, Mapping[str, Any]] = {}
        self._last_runtime_publish_ns = 0
        self._last_heartbeat_ns = 0
        self._last_state_publish_ns = 0
        self._last_lock_refresh_ns = 0
        self._last_tick_recv_ns = 0
        self._current_health_status = N.HEALTH_STATUS_OK
        self._current_health_detail = "booting"
        self._dhan_context_state: M.DhanContextState | None = None
        self._last_provider_runtime: M.ProviderRuntimeState | None = None
        self._last_runtime_resolution: PR.ProviderRuntimeResolution | None = None

    def start(self) -> None:
        now_ns = self._clock.wall_time_ns()
        self._last_lock_refresh_ns = now_ns
        self._set_health(status=N.HEALTH_STATUS_OK, detail="service_started")
        self._publish_health_event(event="service_started")

    def stop(self) -> None:
        self._set_health(status=N.HEALTH_STATUS_WARN, detail="service_stopping")
        self._publish_health_event(event="service_stopping")

    def refresh_lock_if_due(self) -> None:
        now_ns = self._clock.wall_time_ns()
        if (now_ns - self._last_lock_refresh_ns) < (self._cfg.lock_refresh_ms * 1_000_000):
            return
        ok = RX.refresh_lock(
            N.KEY_LOCK_FEEDS,
            self._instance_id,
            ttl_ms=self._cfg.lock_ttl_ms,
            client=self._redis,
        )
        if not ok:
            raise FeedStartupError("feeds singleton lock refresh failed")
        self._last_lock_refresh_ns = now_ns

    def ingest_adapter_poll(
        self,
        *,
        provider_id: str,
        adapter_items: Iterable[Mapping[str, Any]],
        adapter_health: Mapping[str, Any] | None = None,
    ) -> None:
        if provider_id not in PROVIDER_IDS:
            raise FeedValidationError(f"unsupported provider id in feeds ingest: {provider_id!r}")
        if adapter_health is not None:
            self._adapter_health_hints[provider_id] = dict(adapter_health)
        for item in adapter_items:
            if not isinstance(item, Mapping):
                continue
            self._ingest_polled_item(provider_id=provider_id, item=item)

    def _ingest_polled_item(self, *, provider_id: str, item: Mapping[str, Any]) -> None:
        record_type = _safe_str(_first_value(item, "record_type", "type", "kind")).lower()
        payload = item.get("payload")
        if not isinstance(payload, Mapping):
            payload = item
        recv_ts_ns = _safe_int(item.get("recv_ts_ns"), self._clock.wall_time_ns())

        if provider_id == N.PROVIDER_DHAN and record_type in {"context", "dhan_context", "option_context", "chain_context"}:
            self.handle_dhan_context(
                RawDhanContext(provider_id=provider_id, payload=dict(payload), recv_ts_ns=recv_ts_ns)
            )
            return

        if provider_id == N.PROVIDER_DHAN and (
            "selected_call_score" in payload
            or "selected_put_score" in payload
            or record_type == "chain"
        ) and "instrument_token" not in item and "instrument_token" not in payload:
            self.handle_dhan_context(
                RawDhanContext(provider_id=provider_id, payload=dict(payload), recv_ts_ns=recv_ts_ns)
            )
            return

        instrument_token = _safe_str(_first_value(item, "instrument_token", "token"))
        if not instrument_token:
            instrument_token = _safe_str(_first_value(payload, "instrument_token", "token"))
        if not instrument_token:
            return
        self.handle_raw_tick(
            BrokerRawTick(
                instrument_token=instrument_token,
                provider_id=provider_id,
                payload=dict(payload),
                recv_ts_ns=recv_ts_ns,
            )
        )

    def handle_raw_tick(self, raw: BrokerRawTick) -> tuple[M.FeedTick | None, M.FuturesSnapshot | M.OptionSnapshot | None]:
        self._counters.ticks_received_total += 1
        self._last_tick_recv_ns = max(self._last_tick_recv_ns, raw.recv_ts_ns)
        approved = self._token_to_approved.get(raw.instrument_token)
        if approved is None:
            self._counters.ticks_rejected_total += 1
            return None, None
        now_ns = self._clock.wall_time_ns()
        cache_entry = self._provider_caches[raw.provider_id][raw.instrument_token]
        tick, snapshot = self._normalizer.normalize_tick(
            raw=raw,
            approved=approved,
            cache_entry=cache_entry,
            now_ns=now_ns,
        )

        role = (
            N.PROVIDER_ROLE_FUTURES_MARKETDATA
            if approved.role == M.InstrumentRole.FUTURES
            else N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA
        )
        self._mark_role_seen(provider_id=raw.provider_id, role=role, ts_event_ns=tick.ts_event_ns)

        if tick.tick_validity == M.TickValidity.OK:
            self._accept_tick_into_cache(tick=tick, snapshot=snapshot, cache_entry=cache_entry)
            self._counters.ticks_accepted_total += 1
            if approved.role == M.InstrumentRole.FUTURES:
                self._counters.futures_ticks_total += 1
            else:
                self._counters.option_ticks_total += 1
            self._set_health(status=N.HEALTH_STATUS_OK, detail="ticks_flowing")
        else:
            cache_entry.last_validity = tick.tick_validity
            cache_entry.last_validity_reason = tick.reject_reason or "invalid_tick"
            self._counters.ticks_rejected_total += 1

        self._publish_tick_event(tick=tick)
        self._publish_provider_specific_snapshot_hash(provider_id=raw.provider_id, approved=approved)
        self._resolve_and_publish_provider_runtime(now_ns=now_ns)
        self._publish_active_compatibility_hashes(now_ns=now_ns)
        return tick, snapshot

    def handle_dhan_context(self, raw: RawDhanContext) -> tuple[M.DhanContextEvent, M.DhanContextState]:
        now_ns = self._clock.wall_time_ns()
        event, state = self._normalizer.normalize_dhan_context(raw=raw, now_ns=now_ns)
        self._mark_role_seen(
            provider_id=N.PROVIDER_DHAN,
            role=N.PROVIDER_ROLE_OPTION_CONTEXT,
            ts_event_ns=event.ts_event_ns,
        )
        self._dhan_context_state = state
        self._counters.context_events_total += 1
        self._publish_dhan_context_event(event)
        self._publish_dhan_context_state(state)
        self._resolve_and_publish_provider_runtime(now_ns=now_ns)
        self._publish_active_compatibility_hashes(now_ns=now_ns)
        return event, state

    def run_housekeeping_once(
        self,
        *,
        position_state: M.PositionState | None = None,
        strategy_state: M.StrategyState | None = None,
    ) -> None:
        now_ns = self._clock.wall_time_ns()
        self._update_no_data_health(now_ns=now_ns)
        self._resolve_and_publish_provider_runtime(
            now_ns=now_ns,
            position_state=position_state,
            strategy_state=strategy_state,
        )

        if (now_ns - self._last_heartbeat_ns) >= (self._cfg.heartbeat_interval_ms * 1_000_000):
            self._publish_service_heartbeat(now_ns=now_ns)
            self._publish_provider_health_heartbeats(now_ns=now_ns)
            self._publish_provider_runtime_heartbeat(now_ns=now_ns)
            self._last_heartbeat_ns = now_ns

        if (now_ns - self._last_state_publish_ns) >= (self._cfg.state_publish_interval_ms * 1_000_000):
            self._publish_state(now_ns=now_ns)
            self._last_state_publish_ns = now_ns

    def _accept_tick_into_cache(
        self,
        *,
        tick: M.FeedTick,
        snapshot: M.FuturesSnapshot | M.OptionSnapshot,
        cache_entry: QuoteCacheEntry,
    ) -> None:
        cache_entry.last_event_ns = tick.ts_event_ns
        cache_entry.last_provider_ns = tick.ts_provider_ns or tick.ts_event_ns
        cache_entry.ltp = float(tick.ltp or 0.0)
        cache_entry.best_bid = float(tick.bid) if tick.bid is not None else math.nan
        cache_entry.best_ask = float(tick.ask) if tick.ask is not None else math.nan
        cache_entry.bid_qty = int(tick.bid_qty or 0)
        cache_entry.ask_qty = int(tick.ask_qty or 0)
        cache_entry.bid_qty_5 = int(sum(level.quantity for level in tick.bids[:5])) if tick.bids else int(tick.bid_qty or 0)
        cache_entry.ask_qty_5 = int(sum(level.quantity for level in tick.asks[:5])) if tick.asks else int(tick.ask_qty or 0)
        cache_entry.volume = int(tick.volume or 0)
        cache_entry.oi = int(tick.oi or 0)
        cache_entry.last_qty = int(tick.last_qty or 0)
        cache_entry.seq_no = int(tick.seq_no or 0)
        cache_entry.bids = tick.bids
        cache_entry.asks = tick.asks
        cache_entry.last_validity = tick.tick_validity
        cache_entry.last_validity_reason = tick.reject_reason or "ok"
        cache_entry.anomaly_window.append(cache_entry.ltp)

    def _publish_tick_event(self, *, tick: M.FeedTick) -> None:
        if self._cfg.publish_provider_specific_streams:
            RX.xadd_fields(
                self._provider_specific_stream_name_for_tick(tick),
                tick.to_dict(),
                client=self._redis,
            )
        if self._cfg.publish_compatibility_streams and self._tick_matches_active_provider(tick):
            compat_stream = N.STREAM_TICKS_MME_FUT if tick.instrument_role == M.InstrumentRole.FUTURES else N.STREAM_TICKS_MME_OPT
            RX.xadd_fields(compat_stream, tick.to_dict(), client=self._redis)

    def _provider_specific_stream_name_for_tick(self, tick: M.FeedTick) -> str:
        if tick.instrument_role == M.InstrumentRole.FUTURES:
            return (
                N.STREAM_TICKS_MME_FUT_ZERODHA
                if tick.provider_id == N.PROVIDER_ZERODHA
                else N.STREAM_TICKS_MME_FUT_DHAN
            )
        return (
            N.STREAM_TICKS_MME_OPT_SELECTED_ZERODHA
            if tick.provider_id == N.PROVIDER_ZERODHA
            else N.STREAM_TICKS_MME_OPT_SELECTED_DHAN
        )

    def _tick_matches_active_provider(self, tick: M.FeedTick) -> bool:
        runtime = self._last_provider_runtime
        if runtime is None or tick.provider_id is None:
            return False
        if tick.instrument_role == M.InstrumentRole.FUTURES:
            return tick.provider_id == runtime.futures_marketdata_provider_id
        return tick.provider_id == runtime.selected_option_marketdata_provider_id

    def _publish_dhan_context_event(self, event: M.DhanContextEvent) -> None:
        RX.xadd_fields(
            N.STREAM_TICKS_MME_OPT_CONTEXT_DHAN,
            event.to_dict(),
            client=self._redis,
        )

    def _publish_dhan_context_state(self, state: M.DhanContextState) -> None:
        RX.write_hash_fields(N.HASH_STATE_DHAN_CONTEXT, state.to_dict(), client=self._redis)

    def _publish_provider_specific_snapshot_hash(self, *, provider_id: str, approved: ApprovedInstrument) -> None:
        now_ns = self._clock.wall_time_ns()
        frame = self._assembler.build_frame(
            universe=self._universe,
            cache_by_token=self._provider_caches[provider_id],
            now_ns=now_ns,
            stale_after_ms=self._broker_surfaces.stale_after_ms(provider_id, N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA),
            sync_tolerance_ms=self._cfg.snapshot_sync_max_ms,
        )
        if approved.role == M.InstrumentRole.FUTURES:
            fut_payload = self._build_futures_snapshot_payload(
                provider_id=provider_id,
                frame=frame,
                active_provider=(self._last_provider_runtime.futures_marketdata_provider_id if self._last_provider_runtime else None),
            )
            fut_hash = N.HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA if provider_id == N.PROVIDER_ZERODHA else N.HASH_STATE_SNAPSHOT_MME_FUT_DHAN
            RX.write_hash_fields(fut_hash, fut_payload, client=self._redis)
        else:
            opt_payload = self._build_option_snapshot_payload(
                provider_id=provider_id,
                frame=frame,
                active_provider=(self._last_provider_runtime.selected_option_marketdata_provider_id if self._last_provider_runtime else None),
                dhan_context_state=self._dhan_context_state,
            )
            opt_hash = (
                N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA
                if provider_id == N.PROVIDER_ZERODHA
                else N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN
            )
            RX.write_hash_fields(opt_hash, opt_payload, client=self._redis)

    def _publish_active_compatibility_hashes(self, *, now_ns: int) -> None:
        runtime = self._last_provider_runtime
        if runtime is None:
            return
        active_frame = self._build_active_frame(now_ns=now_ns, runtime_state=runtime)
        fut_payload = self._build_futures_snapshot_payload(
            provider_id=runtime.futures_marketdata_provider_id,
            frame=active_frame,
            active_provider=runtime.futures_marketdata_provider_id,
        )
        RX.write_hash_fields(N.HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE, fut_payload, client=self._redis)
        RX.write_hash_fields(N.HASH_STATE_SNAPSHOT_MME_FUT, fut_payload, client=self._redis)

        opt_payload = self._build_option_snapshot_payload(
            provider_id=runtime.selected_option_marketdata_provider_id,
            frame=active_frame,
            active_provider=runtime.selected_option_marketdata_provider_id,
            dhan_context_state=self._dhan_context_state,
        )
        RX.write_hash_fields(N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE, opt_payload, client=self._redis)
        RX.write_hash_fields(N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED, opt_payload, client=self._redis)

    def _build_active_frame(self, *, now_ns: int, runtime_state: M.ProviderRuntimeState) -> M.SnapshotFrame:
        caches: dict[str, QuoteCacheEntry] = {}
        for role, approved in self._universe.instrument_by_role().items():
            provider_id = (
                runtime_state.futures_marketdata_provider_id
                if role == M.InstrumentRole.FUTURES
                else runtime_state.selected_option_marketdata_provider_id
            )
            caches[approved.instrument_token] = self._provider_caches[provider_id][approved.instrument_token]
        stale_after_ms = max(
            self._broker_surfaces.stale_after_ms(runtime_state.futures_marketdata_provider_id, N.PROVIDER_ROLE_FUTURES_MARKETDATA),
            self._broker_surfaces.stale_after_ms(runtime_state.selected_option_marketdata_provider_id, N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA),
        )
        sync_tolerance_ms = max(
            self._broker_surfaces.dead_after_ms(runtime_state.futures_marketdata_provider_id, N.PROVIDER_ROLE_FUTURES_MARKETDATA),
            self._broker_surfaces.dead_after_ms(runtime_state.selected_option_marketdata_provider_id, N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA),
        )
        return self._assembler.build_frame(
            universe=self._universe,
            cache_by_token=caches,
            now_ns=now_ns,
            stale_after_ms=stale_after_ms,
            sync_tolerance_ms=sync_tolerance_ms,
        )

    def _build_futures_snapshot_payload(
        self,
        *,
        provider_id: str,
        frame: M.SnapshotFrame,
        active_provider: str | None,
    ) -> dict[str, Any]:
        future = frame.future
        if future is None:
            return {
                "frame_id": frame.frame_id,
                "selection_version": frame.selection_version,
                "ts_frame_ns": frame.ts_frame_ns,
                "validity": _stream_enum_value(frame.validity),
                "validity_reason": frame.validity_reason or "missing_future",
                "sync_ok": "1" if frame.sync_ok else "0",
                "provider_id": provider_id,
                "future_json": "null",
            }
        approved = self._universe.instrument_by_role()[M.InstrumentRole.FUTURES]
        state = M.FuturesSnapshotState(
            instrument_key=approved.instrument_key,
            ts_event_ns=future.ts_event_ns,
            provider_id=provider_id,
            provider_role=N.PROVIDER_ROLE_FUTURES_MARKETDATA,
            instrument_token=future.instrument_token,
            trading_symbol=future.trading_symbol,
            ltp=future.ltp,
            bid=future.best_bid,
            ask=future.best_ask,
            bid_qty_5=future.bid_qty_5,
            ask_qty_5=future.ask_qty_5,
            tick_validity=future.validity,
            last_update_ns=frame.ts_frame_ns,
            is_active_provider_snapshot=(provider_id == active_provider),
        )
        payload = state.to_dict()
        payload.update(
            {
                "frame_id": frame.frame_id,
                "selection_version": frame.selection_version,
                "ts_frame_ns": frame.ts_frame_ns,
                "validity": _stream_enum_value(frame.validity),
                "validity_reason": frame.validity_reason or "ok",
                "sync_ok": "1" if frame.sync_ok else "0",
                "ts_span_ms": frame.ts_span_ms,
                "stale_mask_json": _json_dumps(list(frame.stale_mask)),
                "future_json": _json_dumps(future.to_dict() if hasattr(future, "to_dict") else asdict(future)),
            }
        )
        return payload

    def _build_option_snapshot_payload(
        self,
        *,
        provider_id: str,
        frame: M.SnapshotFrame,
        active_provider: str | None,
        dhan_context_state: M.DhanContextState | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "frame_id": frame.frame_id,
            "selection_version": frame.selection_version,
            "ts_frame_ns": frame.ts_frame_ns,
            "provider_id": provider_id,
            "validity": _stream_enum_value(frame.validity),
            "validity_reason": frame.validity_reason or "ok",
            "sync_ok": "1" if frame.sync_ok else "0",
            "ts_span_ms": frame.ts_span_ms,
            "stale_mask_json": _json_dumps(list(frame.stale_mask)),
            "is_active_provider_snapshot": "1" if provider_id == active_provider else "0",
            "ce_atm_json": _json_dumps(self._snapshot_member_to_dict(frame.ce_atm)),
            "ce_atm1_json": _json_dumps(self._snapshot_member_to_dict(frame.ce_atm1)),
            "pe_atm_json": _json_dumps(self._snapshot_member_to_dict(frame.pe_atm)),
            "pe_atm1_json": _json_dumps(self._snapshot_member_to_dict(frame.pe_atm1)),
        }
        if dhan_context_state is not None:
            payload["selected_call_instrument_key"] = dhan_context_state.selected_call_instrument_key or ""
            payload["selected_put_instrument_key"] = dhan_context_state.selected_put_instrument_key or ""
            payload["selected_call_score"] = "" if dhan_context_state.selected_call_score is None else dhan_context_state.selected_call_score
            payload["selected_put_score"] = "" if dhan_context_state.selected_put_score is None else dhan_context_state.selected_put_score
            payload["context_status"] = dhan_context_state.context_status
            payload["selected_call_json"] = _json_dumps(self._selected_option_member(frame, dhan_context_state.selected_call_instrument_key))
            payload["selected_put_json"] = _json_dumps(self._selected_option_member(frame, dhan_context_state.selected_put_instrument_key))
        return payload

    def _selected_option_member(self, frame: M.SnapshotFrame, instrument_key: str | None) -> Any:
        if not instrument_key:
            return None
        for member in (frame.ce_atm, frame.ce_atm1, frame.pe_atm, frame.pe_atm1):
            if member is None:
                continue
            approved = self._token_to_approved.get(member.instrument_token)
            if approved is not None and approved.instrument_key == instrument_key:
                return self._snapshot_member_to_dict(member)
        return None

    @staticmethod
    def _snapshot_member_to_dict(member: M.SnapshotMember | None) -> Any:
        if member is None:
            return None
        return member.to_dict() if hasattr(member, "to_dict") else asdict(member)

    def _resolve_and_publish_provider_runtime(
        self,
        *,
        now_ns: int,
        position_state: M.PositionState | None = None,
        strategy_state: M.StrategyState | None = None,
    ) -> None:
        provider_health = self._derive_provider_health_states(now_ns=now_ns)
        resolution = PR.resolve_provider_runtime(
            ts_event_ns=now_ns,
            provider_health=provider_health,
            config=self._provider_runtime_config,
            dhan_context_state=self._dhan_context_state,
            position_state=position_state,
            strategy_state=strategy_state,
            previous_runtime_state=self._last_provider_runtime,
        )
        self._last_runtime_resolution = resolution
        self._last_provider_runtime = resolution.runtime_state
        RX.write_hash_fields(N.HASH_STATE_PROVIDER_RUNTIME, resolution.runtime_state.to_dict(), client=self._redis)

        if self._cfg.publish_runtime_transitions and resolution.transition_events:
            for event in resolution.transition_events:
                RX.xadd_fields(
                    N.STREAM_PROVIDER_RUNTIME,
                    event.to_dict(),
                    maxlen_approx=PROVIDER_RUNTIME_STREAM_MAXLEN,
                    client=self._redis,
                )
            self._counters.provider_transitions_total += len(resolution.transition_events)

        if resolution.message:
            self._publish_health_event(event="provider_runtime_update")
        if resolution.setup_rebuild_required:
            self._publish_error_event(
                event="provider_setup_rebuild_required",
                detail=resolution.setup_rebuild_reason or "provider role change while pre-position",
            )
        self._last_runtime_publish_ns = now_ns

    def _derive_provider_health_states(self, *, now_ns: int) -> dict[str, M.ProviderHealthState]:
        out: dict[str, M.ProviderHealthState] = {}
        for provider_id in PROVIDER_IDS:
            marketdata_status = self._derive_provider_marketdata_status(provider_id=provider_id, now_ns=now_ns)
            adapter_hint = dict(self._adapter_health_hints.get(provider_id, {}))
            authenticated = _safe_bool(_first_value(adapter_hint, "authenticated", "auth_ok"), True)
            execution_healthy = _safe_bool(_first_value(adapter_hint, "execution_healthy", "execution_ok"), True)
            lag_ms = self._derive_provider_lag_ms(provider_id=provider_id, now_ns=now_ns)
            out[provider_id] = M.ProviderHealthState(
                provider_id=provider_id,
                status=marketdata_status,
                authenticated=authenticated,
                stale=(marketdata_status == N.PROVIDER_STATUS_STALE),
                marketdata_healthy=(marketdata_status in (N.PROVIDER_STATUS_HEALTHY, N.PROVIDER_STATUS_DEGRADED, N.PROVIDER_STATUS_FAILOVER_ACTIVE)),
                execution_healthy=execution_healthy,
                lag_ms=lag_ms,
                last_update_ns=now_ns,
                message=self._provider_health_message(provider_id=provider_id, status=marketdata_status, lag_ms=lag_ms),
            )
        return out

    def _derive_provider_marketdata_status(self, *, provider_id: str, now_ns: int) -> str:
        if not self._broker_surfaces.provider_enabled(provider_id):
            return N.PROVIDER_STATUS_DISABLED
        ages: list[int] = []
        for role in (N.PROVIDER_ROLE_FUTURES_MARKETDATA, N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA):
            if not self._broker_surfaces.provider_capability_enabled(provider_id, role):
                continue
            watermark = self._role_watermarks[(provider_id, role)]
            if watermark.last_seen_ns <= 0:
                return N.PROVIDER_STATUS_UNAVAILABLE
            age_ms = max(int((now_ns - watermark.last_seen_ns) / 1_000_000), 0)
            if age_ms > self._broker_surfaces.dead_after_ms(provider_id, role):
                return N.PROVIDER_STATUS_UNAVAILABLE
            ages.append(age_ms)
        if not ages:
            return N.PROVIDER_STATUS_UNAVAILABLE
        if any(
            age_ms > self._broker_surfaces.stale_after_ms(provider_id, role)
            for role in (N.PROVIDER_ROLE_FUTURES_MARKETDATA, N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA)
            if self._broker_surfaces.provider_capability_enabled(provider_id, role)
            for age_ms in [max(int((now_ns - self._role_watermarks[(provider_id, role)].last_seen_ns) / 1_000_000), 0)]
        ):
            return N.PROVIDER_STATUS_STALE
        return N.PROVIDER_STATUS_HEALTHY

    def _derive_provider_lag_ms(self, *, provider_id: str, now_ns: int) -> int:
        ages: list[int] = []
        for role in (N.PROVIDER_ROLE_FUTURES_MARKETDATA, N.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA, N.PROVIDER_ROLE_OPTION_CONTEXT):
            watermark = self._role_watermarks.get((provider_id, role))
            if watermark is None or watermark.last_seen_ns <= 0:
                continue
            ages.append(max(int((now_ns - watermark.last_seen_ns) / 1_000_000), 0))
        return max(ages) if ages else 0

    @staticmethod
    def _provider_health_message(*, provider_id: str, status: str, lag_ms: int) -> str:
        return f"provider={provider_id} status={status} lag_ms={lag_ms}"

    def _mark_role_seen(self, *, provider_id: str, role: str, ts_event_ns: int) -> None:
        watermark = self._role_watermarks[(provider_id, role)]
        watermark.last_seen_ns = max(watermark.last_seen_ns, int(ts_event_ns))
        watermark.last_status = N.HEALTH_STATUS_OK

    def _publish_state(self, *, now_ns: int) -> None:
        runtime = self._last_provider_runtime
        if runtime is None:
            active_fut = ""
            active_opt = ""
            active_ctx = ""
            active_exec = ""
            active_exec_fb = ""
            transition_seq = 0
            failover_active = False
            pending_failover = False
            runtime_reason = "booting"
        else:
            active_fut = runtime.futures_marketdata_provider_id
            active_opt = runtime.selected_option_marketdata_provider_id
            active_ctx = runtime.option_context_provider_id
            active_exec = runtime.execution_primary_provider_id
            active_exec_fb = runtime.execution_fallback_provider_id
            transition_seq = runtime.provider_transition_seq
            failover_active = runtime.failover_active
            pending_failover = runtime.pending_failover
            runtime_reason = runtime.transition_reason

        state = FeedState(
            selection_version=self._universe.selection_version,
            ts_ns=now_ns,
            approved_tokens=len(self._token_to_approved),
            seen_tokens_zerodha=sum(1 for c in self._provider_caches[N.PROVIDER_ZERODHA].values() if c.last_event_ns > 0),
            seen_tokens_dhan=sum(1 for c in self._provider_caches[N.PROVIDER_DHAN].values() if c.last_event_ns > 0),
            active_futures_provider_id=active_fut,
            active_selected_option_provider_id=active_opt,
            active_option_context_provider_id=active_ctx,
            active_execution_primary_provider_id=active_exec,
            active_execution_fallback_provider_id=active_exec_fb,
            provider_transition_seq=transition_seq,
            failover_active=failover_active,
            pending_failover=pending_failover,
            last_runtime_reason=runtime_reason,
            latest_context_status=(self._dhan_context_state.context_status if self._dhan_context_state else N.PROVIDER_STATUS_UNAVAILABLE),
            ticks_received_total=self._counters.ticks_received_total,
            ticks_accepted_total=self._counters.ticks_accepted_total,
            ticks_rejected_total=self._counters.ticks_rejected_total,
            futures_ticks_total=self._counters.futures_ticks_total,
            option_ticks_total=self._counters.option_ticks_total,
            context_events_total=self._counters.context_events_total,
        )
        payload = {f"feeds_{k}": v for k, v in state.to_dict().items()}
        RX.write_hash_fields(N.HASH_STATE_RUNTIME, payload, client=self._redis)
        self._counters.state_publishes_total += 1

    def _publish_service_heartbeat(self, *, now_ns: int) -> None:
        RX.write_heartbeat(
            N.KEY_HEALTH_FEEDS,
            service=N.SERVICE_FEEDS,
            instance_id=self._instance_id,
            status=self._current_health_status,
            ts_event_ns=now_ns,
            ttl_ms=self._cfg.heartbeat_interval_ms * 3,
            client=self._redis,
        )
        self._counters.heartbeats_total += 1

    def _publish_provider_health_heartbeats(self, *, now_ns: int) -> None:
        provider_health = self._derive_provider_health_states(now_ns=now_ns)
        for provider_id, health_state in provider_health.items():
            status = self._provider_status_to_health_status(health_state.status)
            if provider_id == N.PROVIDER_DHAN:
                RX.write_heartbeat(
                    N.KEY_HEALTH_DHAN_MARKETDATA,
                    service=N.SERVICE_FEEDS,
                    instance_id=self._instance_id,
                    status=status,
                    ts_event_ns=now_ns,
                    ttl_ms=self._cfg.heartbeat_interval_ms * 3,
                    client=self._redis,
                )
                RX.write_heartbeat(
                    N.KEY_HEALTH_DHAN_AUTH,
                    service=N.SERVICE_FEEDS,
                    instance_id=self._instance_id,
                    status=(N.HEALTH_STATUS_OK if health_state.authenticated is not False else N.HEALTH_STATUS_ERROR),
                    ts_event_ns=now_ns,
                    ttl_ms=self._cfg.heartbeat_interval_ms * 3,
                    client=self._redis,
                )
                RX.write_heartbeat(
                    N.KEY_HEALTH_DHAN_EXECUTION,
                    service=N.SERVICE_FEEDS,
                    instance_id=self._instance_id,
                    status=(N.HEALTH_STATUS_OK if health_state.execution_healthy is not False else N.HEALTH_STATUS_WARN),
                    ts_event_ns=now_ns,
                    ttl_ms=self._cfg.heartbeat_interval_ms * 3,
                    client=self._redis,
                )
            elif provider_id == N.PROVIDER_ZERODHA:
                RX.write_heartbeat(
                    N.KEY_HEALTH_ZERODHA_MARKETDATA,
                    service=N.SERVICE_FEEDS,
                    instance_id=self._instance_id,
                    status=status,
                    ts_event_ns=now_ns,
                    ttl_ms=self._cfg.heartbeat_interval_ms * 3,
                    client=self._redis,
                )
                RX.write_heartbeat(
                    N.KEY_HEALTH_ZERODHA_EXECUTION,
                    service=N.SERVICE_FEEDS,
                    instance_id=self._instance_id,
                    status=(N.HEALTH_STATUS_OK if health_state.execution_healthy is not False else N.HEALTH_STATUS_WARN),
                    ts_event_ns=now_ns,
                    ttl_ms=self._cfg.heartbeat_interval_ms * 3,
                    client=self._redis,
                )

    def _publish_provider_runtime_heartbeat(self, *, now_ns: int) -> None:
        runtime = self._last_provider_runtime
        status = N.HEALTH_STATUS_WARN
        if runtime is not None:
            if runtime.pending_failover:
                status = N.HEALTH_STATUS_WARN
            elif runtime.failover_active:
                status = N.HEALTH_STATUS_WARN
            else:
                status = N.HEALTH_STATUS_OK
            if runtime.futures_marketdata_status in (
                N.PROVIDER_STATUS_UNAVAILABLE,
                N.PROVIDER_STATUS_AUTH_FAILED,
                N.PROVIDER_STATUS_DISABLED,
            ) or runtime.selected_option_marketdata_status in (
                N.PROVIDER_STATUS_UNAVAILABLE,
                N.PROVIDER_STATUS_AUTH_FAILED,
                N.PROVIDER_STATUS_DISABLED,
            ):
                status = N.HEALTH_STATUS_ERROR
        RX.write_heartbeat(
            N.KEY_HEALTH_PROVIDER_RUNTIME,
            service=N.SERVICE_FEEDS,
            instance_id=self._instance_id,
            status=status,
            ts_event_ns=now_ns,
            ttl_ms=self._cfg.heartbeat_interval_ms * 3,
            client=self._redis,
        )

    @staticmethod
    def _provider_status_to_health_status(provider_status: str) -> str:
        if provider_status in (N.PROVIDER_STATUS_HEALTHY, N.PROVIDER_STATUS_FAILOVER_ACTIVE):
            return N.HEALTH_STATUS_OK
        if provider_status in (N.PROVIDER_STATUS_DEGRADED, N.PROVIDER_STATUS_STALE):
            return N.HEALTH_STATUS_WARN
        return N.HEALTH_STATUS_ERROR

    def _publish_health_event(self, *, event: str) -> None:
        now_ns = self._clock.wall_time_ns()
        RX.xadd_fields(
            N.STREAM_SYSTEM_HEALTH,
            {
                "service_name": N.SERVICE_FEEDS,
                "instance_id": self._instance_id,
                "status": self._current_health_status,
                "event": event,
                "detail": self._current_health_detail,
                "ts_ns": str(now_ns),
                "ticks_received_total": self._counters.ticks_received_total,
                "ticks_accepted_total": self._counters.ticks_accepted_total,
                "ticks_rejected_total": self._counters.ticks_rejected_total,
                "provider_transition_seq": 0 if self._last_provider_runtime is None else self._last_provider_runtime.provider_transition_seq,
                "selection_version": self._universe.selection_version,
            },
            maxlen_approx=HEALTH_STREAM_MAXLEN,
            client=self._redis,
        )

    def _publish_error_event(self, *, event: str, detail: str) -> None:
        now_ns = self._clock.wall_time_ns()
        RX.xadd_fields(
            N.STREAM_SYSTEM_ERRORS,
            {
                "service_name": N.SERVICE_FEEDS,
                "instance_id": self._instance_id,
                "error_type": event,
                "detail": detail,
                "ts_ns": str(now_ns),
                "selection_version": self._universe.selection_version,
            },
            maxlen_approx=ERROR_STREAM_MAXLEN,
            client=self._redis,
        )

    def _set_health(self, *, status: str, detail: str) -> None:
        self._current_health_status = status
        self._current_health_detail = detail

    def _update_no_data_health(self, *, now_ns: int) -> None:
        if self._last_tick_recv_ns <= 0:
            self._set_health(status=N.HEALTH_STATUS_WARN, detail="waiting_for_first_tick")
            return
        age_ms = max(int((now_ns - self._last_tick_recv_ns) / 1_000_000), 0)
        if age_ms >= self._cfg.no_data_error_after_ms:
            self._set_health(status=N.HEALTH_STATUS_ERROR, detail="tick_flow_dead")
        elif age_ms >= self._cfg.no_data_warn_after_ms:
            self._set_health(status=N.HEALTH_STATUS_WARN, detail="tick_flow_stale")
        elif self._current_health_status != N.HEALTH_STATUS_OK:
            self._set_health(status=N.HEALTH_STATUS_OK, detail="ticks_flowing")


# =============================================================================
# Adapter extraction
# =============================================================================


def _extract_adapter_surfaces(context: Any) -> tuple[dict[str, ProviderAdapterSurface], Mapping[str, Any]]:
    adapters: dict[str, ProviderAdapterSurface] = {}
    settings = getattr(context, "settings", None)

    explicit_map = getattr(context, "feed_adapters", None)
    if isinstance(explicit_map, Mapping):
        for provider_id, adapter in explicit_map.items():
            pid = _safe_str(provider_id).upper()
            if pid in PROVIDER_IDS and adapter is not None:
                adapters[pid] = ProviderAdapterSurface(provider_id=pid, adapter=adapter)

    if not adapters:
        z_adapter = getattr(context, "zerodha_feed_adapter", None)
        if z_adapter is not None:
            adapters[N.PROVIDER_ZERODHA] = ProviderAdapterSurface(
                provider_id=N.PROVIDER_ZERODHA,
                adapter=z_adapter,
            )
        d_adapter = getattr(context, "dhan_feed_adapter", None)
        if d_adapter is not None:
            adapters[N.PROVIDER_DHAN] = ProviderAdapterSurface(
                provider_id=N.PROVIDER_DHAN,
                adapter=d_adapter,
            )

    if not adapters:
        single_adapter = getattr(context, "feed_adapter", None)
        if single_adapter is None:
            single_adapter = getattr(context, "market_data_adapter", None)
        provider_name = _safe_str(getattr(settings, "feed_provider", None)).upper()
        if single_adapter is not None and provider_name in PROVIDER_IDS:
            adapters[provider_name] = ProviderAdapterSurface(
                provider_id=provider_name,
                adapter=single_adapter,
            )

    dhan_context_adapter = getattr(context, "dhan_context_adapter", None)
    if dhan_context_adapter is not None:
        adapters.setdefault(
            N.PROVIDER_DHAN,
            ProviderAdapterSurface(provider_id=N.PROVIDER_DHAN, adapter=dhan_context_adapter, context_only=True),
        )

    if not adapters:
        raise FeedStartupError(
            "context must provide provider-aware feed adapters via feed_adapters or zerodha_feed_adapter/dhan_feed_adapter"
        )

    unknown = [pid for pid in adapters if pid not in PROVIDER_IDS]
    if unknown:
        raise FeedStartupError("unsupported provider ids in feed adapters: " + ", ".join(sorted(unknown)))

    return adapters, settings


def _adapter_health_hint(adapter: Any) -> Mapping[str, Any] | None:
    with contextlib.suppress(Exception):
        if hasattr(adapter, "health") and callable(adapter.health):
            result = adapter.health()
            if isinstance(result, Mapping):
                return dict(result)
    with contextlib.suppress(Exception):
        if hasattr(adapter, "info") and callable(adapter.info):
            result = adapter.info()
            if isinstance(result, Mapping):
                return dict(result)
            if result is not None and hasattr(result, "__dict__"):
                return dict(vars(result))
    return None


# =============================================================================
# Canonical entrypoint
# =============================================================================


def run(context: Any) -> int:
    _validate_surface_or_die()

    settings = context.settings
    redis_runtime = context.redis
    redis_client = redis_runtime.sync if hasattr(redis_runtime, "sync") else redis_runtime
    shutdown = context.shutdown
    clock = context.clock
    instance_id = context.instance_id

    if clock is None or not hasattr(clock, "wall_time_ns"):
        raise FeedStartupError("context.clock with wall_time_ns() is required")
    if shutdown is None or not hasattr(shutdown, "is_set") or not hasattr(shutdown, "wait"):
        raise FeedStartupError("context.shutdown with is_set()/wait() is required")
    if not instance_id:
        raise FeedStartupError("context.instance_id is required")

    runtime_set = getattr(context, "runtime_instruments", None)
    if runtime_set is None:
        runtime_set = getattr(context, "instrument_set", None)
    if runtime_set is None:
        raise FeedStartupError("context must provide runtime_instruments / instrument_set")

    adapters, settings = _extract_adapter_surfaces(context)
    dhan_context_adapter = getattr(context, "dhan_context_adapter", None)

    broker_config_dir = _safe_str(getattr(settings, "brokers_config_dir", None)) or "etc/brokers"
    broker_surfaces = load_broker_provider_surfaces(broker_config_dir)

    if not RX.ping_redis(client=redis_client):
        raise FeedStartupError("feeds redis ping failed during startup")

    cfg = FeedConfig(
        heartbeat_interval_ms=int(getattr(settings, "feeds_heartbeat_interval_ms", DEFAULT_HEARTBEAT_INTERVAL_MS)),
        state_publish_interval_ms=int(getattr(settings, "feeds_state_publish_interval_ms", DEFAULT_STATE_PUBLISH_INTERVAL_MS)),
        provider_runtime_publish_interval_ms=int(getattr(settings, "feeds_provider_runtime_publish_interval_ms", DEFAULT_PROVIDER_RUNTIME_PUBLISH_INTERVAL_MS)),
        poll_interval_ms=int(getattr(settings, "feeds_poll_interval_ms", DEFAULT_POLL_INTERVAL_MS)),
        lock_ttl_ms=int(getattr(settings, "feeds_lock_ttl_ms", DEFAULT_LOCK_TTL_MS)),
        lock_refresh_ms=int(getattr(settings, "feeds_lock_refresh_ms", DEFAULT_LOCK_REFRESH_MS)),
        no_data_warn_after_ms=int(getattr(settings, "feeds_no_data_warn_after_ms", DEFAULT_NO_DATA_WARN_AFTER_MS)),
        no_data_error_after_ms=int(getattr(settings, "feeds_no_data_error_after_ms", DEFAULT_NO_DATA_ERROR_AFTER_MS)),
        anomaly_window=int(getattr(settings, "feeds_anomaly_window", DEFAULT_ANOMALY_WINDOW)),
        anomaly_min_samples=int(getattr(settings, "feeds_anomaly_min_samples", DEFAULT_ANOMALY_MIN_SAMPLES)),
        anomaly_median_ticks=float(getattr(settings, "feeds_anomaly_median_ticks", DEFAULT_ANOMALY_MEDIAN_TICKS)),
        context_stale_ms=int(getattr(settings, "feeds_context_stale_ms", DEFAULT_CONTEXT_STALE_MS)),
        context_dead_ms=int(getattr(settings, "feeds_context_dead_ms", DEFAULT_CONTEXT_DEAD_MS)),
        publish_every_tick=bool(getattr(settings, "feeds_publish_every_tick", True)),
        publish_provider_specific_streams=bool(getattr(settings, "feeds_publish_provider_specific_streams", True)),
        publish_compatibility_streams=bool(getattr(settings, "feeds_publish_compatibility_streams", True)),
        publish_runtime_transitions=bool(getattr(settings, "feeds_publish_runtime_transitions", True)),
    )

    acquired = RX.acquire_lock(
        N.KEY_LOCK_FEEDS,
        instance_id,
        ttl_ms=cfg.lock_ttl_ms,
        client=redis_client,
    )
    if not acquired:
        raise FeedStartupError("feeds singleton lock not acquired")

    service = FeedService(
        universe=ActiveUniverse.from_runtime_set(runtime_set, generated_at_ns=int(clock.wall_time_ns())),
        config=cfg,
        broker_surfaces=broker_surfaces,
        redis_client=redis_client,
        clock=clock,
        instance_id=instance_id,
        logger=LOGGER,
    )
    service.start()

    poll_interval_s = max(cfg.poll_interval_ms, 10) / 1000.0

    try:
        while not shutdown.is_set():
            try:
                for provider_id, surface in adapters.items():
                    adapter = surface.adapter
                    polled = adapter.poll() if hasattr(adapter, "poll") and callable(adapter.poll) else []
                    if polled is None:
                        polled = []
                    service.ingest_adapter_poll(
                        provider_id=provider_id,
                        adapter_items=polled,
                        adapter_health=_adapter_health_hint(adapter),
                    )

                if (
                    dhan_context_adapter is not None
                    and hasattr(dhan_context_adapter, "poll")
                    and callable(dhan_context_adapter.poll)
                    and dhan_context_adapter is not adapters.get(N.PROVIDER_DHAN).adapter
                ):
                    context_polled = dhan_context_adapter.poll()
                    if context_polled is None:
                        context_polled = []
                    service.ingest_adapter_poll(
                        provider_id=N.PROVIDER_DHAN,
                        adapter_items=context_polled,
                        adapter_health=_adapter_health_hint(dhan_context_adapter),
                    )

                position_state = getattr(context, "position_state", None)
                strategy_state = getattr(context, "strategy_state", None)
                service.refresh_lock_if_due()
                service.run_housekeeping_once(
                    position_state=position_state,
                    strategy_state=strategy_state,
                )
            except Exception as exc:
                LOGGER.exception("feeds_service_loop_error")
                with contextlib.suppress(Exception):
                    service._set_health(
                        status=N.HEALTH_STATUS_ERROR,
                        detail=f"loop_error:{type(exc).__name__}",
                    )
                    service._publish_error_event(
                        event="feeds_service_loop_error",
                        detail=f"{type(exc).__name__}:{exc}",
                    )
            shutdown.wait(poll_interval_s)
    finally:
        service.stop()
        with contextlib.suppress(Exception):
            RX.write_heartbeat(
                N.KEY_HEALTH_FEEDS,
                service=N.SERVICE_FEEDS,
                instance_id=instance_id,
                status="STOPPED",
                ts_event_ns=int(clock.wall_time_ns()),
                ttl_ms=cfg.heartbeat_interval_ms * 3,
                client=redis_client,
            )
        with contextlib.suppress(Exception):
            RX.release_lock(N.KEY_LOCK_FEEDS, instance_id, client=redis_client)

    LOGGER.info("feeds_service_stopped")
    return 0

# =============================================================================
# Batch 7 freeze hardening: provider market-data/context separation
# =============================================================================

def _batch7_env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = str(raw).strip().lower()
    if value in {"1", "true", "yes", "y", "on"}:
        return True
    if value in {"0", "false", "no", "n", "off", ""}:
        return False
    raise FeedStartupError(f"{name} must be boolean-like, got {raw!r}")


def _batch7_strict_provider_runtime_enabled() -> bool:
    return _batch7_env_flag("MME_PROVIDER_RUNTIME_STRICT", default=False)


def _batch7_is_context_only_surface(surface: Any) -> bool:
    return bool(getattr(surface, "context_only", False))


def _batch7_marketdata_adapter_map(
    adapters: Mapping[str, ProviderAdapterSurface],
) -> dict[str, ProviderAdapterSurface]:
    return {
        str(provider_id): surface
        for provider_id, surface in dict(adapters or {}).items()
        if not _batch7_is_context_only_surface(surface)
    }


def _batch7_context_adapter_map(
    adapters: Mapping[str, ProviderAdapterSurface],
) -> dict[str, ProviderAdapterSurface]:
    return {
        str(provider_id): surface
        for provider_id, surface in dict(adapters or {}).items()
        if _batch7_is_context_only_surface(surface)
    }


def _batch7_validate_adapter_surfaces(
    adapters: Mapping[str, ProviderAdapterSurface],
) -> None:
    marketdata = _batch7_marketdata_adapter_map(adapters)
    if not marketdata:
        raise FeedStartupError(
            "feeds service requires at least one true market-data adapter; "
            "Dhan context-only adapter cannot satisfy market-data dependency"
        )

    if _batch7_strict_provider_runtime_enabled():
        missing = [
            provider_id
            for provider_id in (N.PROVIDER_ZERODHA, N.PROVIDER_DHAN)
            if provider_id not in marketdata
        ]
        if missing:
            raise FeedStartupError(
                "strict provider runtime requires true market-data adapters for: "
                + ", ".join(missing)
            )


if "_extract_adapter_surfaces" in globals() and "_BATCH7_ORIGINAL_EXTRACT_ADAPTER_SURFACES" not in globals():
    _BATCH7_ORIGINAL_EXTRACT_ADAPTER_SURFACES = _extract_adapter_surfaces

    def _extract_adapter_surfaces(context: Any) -> dict[str, ProviderAdapterSurface]:
        adapters = dict(_BATCH7_ORIGINAL_EXTRACT_ADAPTER_SURFACES(context))
        _batch7_validate_adapter_surfaces(adapters)
        return adapters

# =============================================================================
# Batch 7 corrective closure: preserve adapter extraction return contract
# =============================================================================
#
# Original contract:
#     _extract_adapter_surfaces(context) -> tuple[dict[str, ProviderAdapterSurface], Mapping[str, Any]]
#
# Earlier Batch 7 hardening accidentally treated the tuple as a dict. This
# corrective wrapper preserves the original tuple shape while still enforcing
# market-data vs context-only separation.

def _batch7_extract_adapter_result_parts(result: Any) -> tuple[dict[str, ProviderAdapterSurface], Mapping[str, Any]]:
    if (
        isinstance(result, tuple)
        and len(result) == 2
        and isinstance(result[0], Mapping)
    ):
        adapters = dict(result[0])
        settings = result[1] if isinstance(result[1], Mapping) else {}
        return adapters, settings

    if isinstance(result, Mapping):
        return dict(result), {}

    raise FeedStartupError(
        "_extract_adapter_surfaces returned unsupported shape; expected "
        "tuple[dict[str, ProviderAdapterSurface], Mapping[str, Any]]"
    )


def _batch7_extract_adapter_surfaces_contract_safe(
    context: Any,
) -> tuple[dict[str, ProviderAdapterSurface], Mapping[str, Any]]:
    original = globals().get("_BATCH7_ORIGINAL_EXTRACT_ADAPTER_SURFACES")
    if not callable(original):
        raise FeedStartupError("original _extract_adapter_surfaces is unavailable")

    adapters, settings = _batch7_extract_adapter_result_parts(original(context))
    _batch7_validate_adapter_surfaces(adapters)
    return adapters, settings


_extract_adapter_surfaces = _batch7_extract_adapter_surfaces_contract_safe
