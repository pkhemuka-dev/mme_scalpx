from __future__ import annotations

"""
app/mme_scalpx/core/names.py

Canonical contract names and symbolic constants for ScalpX MME.

Purpose
-------
Single source of truth for:
- Redis stream names
- Redis latest-state hash names
- heartbeat / health keys
- process-safety lock keys
- notify channel names
- consumer-group names
- replay namespace derivation
- service identity registry and bootstrap order
- contract-level symbolic constants
- ownership registries
- additive observability publisher registries
- bootstrap consumer-group specs
- event type constants
- grouped live/replay bundles
- compatibility aliases required during integration freeze

Ownership
---------
This module OWNS:
- canonical Redis names
- replay-name derivation rules
- service identity constants and service registry
- consumer-group names
- contract constants such as commands / actions / sides / modes / ack types
- ownership registries
- additive-publisher registries where a stream has one primary semantic owner
  but multiple allowed additive publishers
- stream bootstrap group specs
- event symbolic names
- common defaults used across transport callers
- compatibility aliases for legacy/generic symbol names

This module DOES NOT own:
- runtime settings / environment parsing
- Redis client lifecycle
- serialization behavior
- payload / state schemas
- trading logic
- broker symbols
- holiday calendars

Core contract rules
-------------------
- Streams are event/history transport.
- Hashes / scalar keys are latest state / control / liveness.
- No raw Redis names should be hardcoded elsewhere.
- Replay names must remain namespace-isolated from live names.
- execution = sole position truth.
- risk may block entries but never block exits.
- monitor = observability/control plane only.
- report = read-only reconstruction only.
- Compatibility aliases may exist only inside this file.

Primary-owner clarification
---------------------------
Some streams have one primary semantic owner while still allowing additive
publishers. In particular:
- STREAM_SYSTEM_HEALTH and STREAM_SYSTEM_ERRORS remain monitor-owned from a
  semantic / aggregation perspective
- other frozen services may append additive observability to those streams
  when their own module contracts explicitly permit it

This file therefore distinguishes:
- primary ownership registries
- additive publisher registries

so the contract remains explicit and non-contradictory.
"""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping, Sequence

from .validators import assert_no_duplicates, require_non_empty_str

# ============================================================================
# Project / contract identity
# ============================================================================

PROJECT_ALIAS: Final[str] = "mme_scalpx"
PROJECT_NAME: Final[str] = "mme_scalpx"
STRATEGY_ALIAS: Final[str] = "MME"

CONTRACTS_VERSION: Final[str] = "1.2"
DEFAULT_SCHEMA_VERSION: Final[int] = 1

REPLAY_PREFIX: Final[str] = "replay:"
NAMESPACE: Final[str] = "mme"

# ============================================================================
# Defaults / general transport constants
# ============================================================================

DEFAULT_STREAM_MAXLEN: Final[int] = 10_000
DEFAULT_XREAD_COUNT: Final[int] = 10
DEFAULT_XREAD_BLOCK_MS: Final[int] = 100

TARGET_PCT_DEFAULT: Final[float] = 0.12
STOP_PCT_DEFAULT: Final[float] = 0.07

# ============================================================================
# Exceptions
# ============================================================================


class NamesContractError(ValueError):
    """Raised when the names contract is invalid or internally inconsistent."""


# ============================================================================
# Local wrappers around shared validators
# ============================================================================


def _wrap_validation(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        if isinstance(exc, NamesContractError):
            raise
        raise NamesContractError(str(exc)) from exc


def _require_non_empty_str(value: str, *, field_name: str) -> str:
    return _wrap_validation(require_non_empty_str, value, field_name=field_name)


def _assert_no_duplicates(values: Sequence[str], *, label: str) -> None:
    _wrap_validation(assert_no_duplicates, values, label=label)


# ============================================================================
# Small helpers
# ============================================================================


def _join_name(*parts: str) -> str:
    cleaned_parts: list[str] = []
    for idx, part in enumerate(parts):
        token = _require_non_empty_str(part, field_name=f"parts[{idx}]")
        cleaned_parts.append(token.strip(":"))
    return ":".join(cleaned_parts)


def ensure_live_name(name: str) -> str:
    value = _require_non_empty_str(name, field_name="name")
    if value.startswith(REPLAY_PREFIX):
        raise NamesContractError(f"Expected live name, got replay name: {value}")
    return value


def ensure_replay_name(name: str) -> str:
    value = _require_non_empty_str(name, field_name="name")
    if not value.startswith(REPLAY_PREFIX):
        raise NamesContractError(f"Expected replay name, got live name: {value}")
    return value


def replay_name(name: str) -> str:
    live_name = ensure_live_name(name)
    return _join_name("replay", live_name)


def is_replay_name(name: str) -> bool:
    value = _require_non_empty_str(name, field_name="name")
    return value.startswith(REPLAY_PREFIX)


# ============================================================================
# Canonical service identities
# ============================================================================

SERVICE_MAIN: Final[str] = "main"
SERVICE_LOGIN: Final[str] = "login"
SERVICE_INSTRUMENTS: Final[str] = "instruments"
SERVICE_FEEDS: Final[str] = "feeds"
SERVICE_FEATURES: Final[str] = "features"
SERVICE_STRATEGY: Final[str] = "strategy"
SERVICE_RISK: Final[str] = "risk"
SERVICE_EXECUTION: Final[str] = "execution"
SERVICE_MONITOR: Final[str] = "monitor"
SERVICE_REPORT: Final[str] = "report"

SERVICE_NAMES: Final[tuple[str, ...]] = (
    SERVICE_MAIN,
    SERVICE_LOGIN,
    SERVICE_INSTRUMENTS,
    SERVICE_FEEDS,
    SERVICE_FEATURES,
    SERVICE_STRATEGY,
    SERVICE_RISK,
    SERVICE_EXECUTION,
    SERVICE_MONITOR,
    SERVICE_REPORT,
)

BOOTSTRAP_SERVICE_ORDER: Final[tuple[str, ...]] = (
    SERVICE_LOGIN,
    SERVICE_INSTRUMENTS,
    SERVICE_FEEDS,
    SERVICE_FEATURES,
    SERVICE_STRATEGY,
    SERVICE_RISK,
    SERVICE_EXECUTION,
    SERVICE_MONITOR,
    SERVICE_REPORT,
)


@dataclass(frozen=True, slots=True)
class ServiceDef:
    """Canonical description of one service contract identity."""

    name: str
    module_path: str
    owns_heartbeat: str | None = None
    owns_lock: str | None = None
    description: str = ""


# ============================================================================
# Canonical instrument routing identities
# ============================================================================

IK_MME_FUT: Final[str] = "NFO:MME_FUT"
IK_MME_CE: Final[str] = "NFO:MME_CE"
IK_MME_PE: Final[str] = "NFO:MME_PE"

INSTRUMENT_KEYS: Final[tuple[str, ...]] = (
    IK_MME_FUT,
    IK_MME_CE,
    IK_MME_PE,
)

# ============================================================================
# Strategy family / doctrine identifiers
# ============================================================================

STRATEGY_FAMILY_MIST: Final[str] = "MIST"
STRATEGY_FAMILY_MISB: Final[str] = "MISB"
STRATEGY_FAMILY_MISC: Final[str] = "MISC"
STRATEGY_FAMILY_MISR: Final[str] = "MISR"
STRATEGY_FAMILY_MISO: Final[str] = "MISO"

STRATEGY_FAMILY_IDS: Final[tuple[str, ...]] = (
    STRATEGY_FAMILY_MIST,
    STRATEGY_FAMILY_MISB,
    STRATEGY_FAMILY_MISC,
    STRATEGY_FAMILY_MISR,
    STRATEGY_FAMILY_MISO,
)

DOCTRINE_MIST: Final[str] = STRATEGY_FAMILY_MIST
DOCTRINE_MISB: Final[str] = STRATEGY_FAMILY_MISB
DOCTRINE_MISC: Final[str] = STRATEGY_FAMILY_MISC
DOCTRINE_MISR: Final[str] = STRATEGY_FAMILY_MISR
DOCTRINE_MISO: Final[str] = STRATEGY_FAMILY_MISO

DOCTRINE_IDS: Final[tuple[str, ...]] = (
    DOCTRINE_MIST,
    DOCTRINE_MISB,
    DOCTRINE_MISC,
    DOCTRINE_MISR,
    DOCTRINE_MISO,
)

BRANCH_CALL: Final[str] = "CALL"
BRANCH_PUT: Final[str] = "PUT"

BRANCH_IDS: Final[tuple[str, ...]] = (
    BRANCH_CALL,
    BRANCH_PUT,
)

# ============================================================================
# Provider identifiers / roles / migration runtime modes
# ============================================================================

PROVIDER_ZERODHA: Final[str] = "ZERODHA"
PROVIDER_DHAN: Final[str] = "DHAN"

PROVIDER_IDS: Final[tuple[str, ...]] = (
    PROVIDER_ZERODHA,
    PROVIDER_DHAN,
)

PROVIDER_ROLE_FUTURES_MARKETDATA: Final[str] = "futures_marketdata"
PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA: Final[str] = "selected_option_marketdata"
PROVIDER_ROLE_OPTION_CONTEXT: Final[str] = "option_context"
PROVIDER_ROLE_EXECUTION_PRIMARY: Final[str] = "execution_primary"
PROVIDER_ROLE_EXECUTION_FALLBACK: Final[str] = "execution_fallback"

PROVIDER_ROLES: Final[tuple[str, ...]] = (
    PROVIDER_ROLE_FUTURES_MARKETDATA,
    PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
    PROVIDER_ROLE_OPTION_CONTEXT,
    PROVIDER_ROLE_EXECUTION_PRIMARY,
    PROVIDER_ROLE_EXECUTION_FALLBACK,
)

PROVIDER_STATUS_HEALTHY: Final[str] = "HEALTHY"
PROVIDER_STATUS_DEGRADED: Final[str] = "DEGRADED"
PROVIDER_STATUS_STALE: Final[str] = "STALE"
PROVIDER_STATUS_AUTH_FAILED: Final[str] = "AUTH_FAILED"
PROVIDER_STATUS_UNAVAILABLE: Final[str] = "UNAVAILABLE"
PROVIDER_STATUS_DISABLED: Final[str] = "DISABLED"
PROVIDER_STATUS_FAILOVER_ACTIVE: Final[str] = "FAILOVER_ACTIVE"

PROVIDER_STATUSES: Final[tuple[str, ...]] = (
    PROVIDER_STATUS_HEALTHY,
    PROVIDER_STATUS_DEGRADED,
    PROVIDER_STATUS_STALE,
    PROVIDER_STATUS_AUTH_FAILED,
    PROVIDER_STATUS_UNAVAILABLE,
    PROVIDER_STATUS_DISABLED,
    PROVIDER_STATUS_FAILOVER_ACTIVE,
)

PROVIDER_FAILOVER_MODE_MANUAL: Final[str] = "MANUAL"
PROVIDER_FAILOVER_MODE_ARMED_MANUAL: Final[str] = "ARMED_MANUAL"
PROVIDER_FAILOVER_MODE_AUTO_AFTER_PROOF: Final[str] = "AUTO_AFTER_PROOF"

PROVIDER_FAILOVER_MODES: Final[tuple[str, ...]] = (
    PROVIDER_FAILOVER_MODE_MANUAL,
    PROVIDER_FAILOVER_MODE_ARMED_MANUAL,
    PROVIDER_FAILOVER_MODE_AUTO_AFTER_PROOF,
)

PROVIDER_OVERRIDE_MODE_AUTO: Final[str] = "AUTO"
PROVIDER_OVERRIDE_MODE_FORCE_ZERODHA: Final[str] = "FORCE_ZERODHA"
PROVIDER_OVERRIDE_MODE_FORCE_DHAN: Final[str] = "FORCE_DHAN"

PROVIDER_OVERRIDE_MODES: Final[tuple[str, ...]] = (
    PROVIDER_OVERRIDE_MODE_AUTO,
    PROVIDER_OVERRIDE_MODE_FORCE_ZERODHA,
    PROVIDER_OVERRIDE_MODE_FORCE_DHAN,
)

PROVIDER_TRANSITION_REASON_BOOTSTRAP: Final[str] = "BOOTSTRAP"
PROVIDER_TRANSITION_REASON_CONFIG_RELOAD: Final[str] = "CONFIG_RELOAD"
PROVIDER_TRANSITION_REASON_MANUAL_OVERRIDE: Final[str] = "MANUAL_OVERRIDE"
PROVIDER_TRANSITION_REASON_HEALTH_FAIL: Final[str] = "HEALTH_FAIL"
PROVIDER_TRANSITION_REASON_STALE_DATA: Final[str] = "STALE_DATA"
PROVIDER_TRANSITION_REASON_AUTH_FAILED: Final[str] = "AUTH_FAILED"
PROVIDER_TRANSITION_REASON_PROOF_PROMOTION: Final[str] = "PROOF_PROMOTION"
PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED: Final[str] = "FAILOVER_ACTIVATED"
PROVIDER_TRANSITION_REASON_FAILBACK_RECOVERY: Final[str] = "FAILBACK_RECOVERY"

PROVIDER_TRANSITION_REASONS: Final[tuple[str, ...]] = (
    PROVIDER_TRANSITION_REASON_BOOTSTRAP,
    PROVIDER_TRANSITION_REASON_CONFIG_RELOAD,
    PROVIDER_TRANSITION_REASON_MANUAL_OVERRIDE,
    PROVIDER_TRANSITION_REASON_HEALTH_FAIL,
    PROVIDER_TRANSITION_REASON_STALE_DATA,
    PROVIDER_TRANSITION_REASON_AUTH_FAILED,
    PROVIDER_TRANSITION_REASON_PROOF_PROMOTION,
    PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED,
    PROVIDER_TRANSITION_REASON_FAILBACK_RECOVERY,
)

STRATEGY_RUNTIME_MODE_NORMAL: Final[str] = "NORMAL"
STRATEGY_RUNTIME_MODE_DHAN_DEGRADED: Final[str] = "DHAN_DEGRADED"
STRATEGY_RUNTIME_MODE_BASE_5DEPTH: Final[str] = "BASE_5DEPTH"
STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED: Final[str] = "DEPTH20_ENHANCED"
STRATEGY_RUNTIME_MODE_DISABLED: Final[str] = "DISABLED"

STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = (
    STRATEGY_RUNTIME_MODE_NORMAL,
    STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
    STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
    STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED,
    STRATEGY_RUNTIME_MODE_DISABLED,
)

FAMILY_RUNTIME_MODE_OBSERVE_ONLY: Final[str] = "OBSERVE_ONLY"
FAMILY_RUNTIME_MODE_LEGACY_LIVE_FAMILY_SHADOW: Final[str] = "LEGACY_LIVE_FAMILY_SHADOW"
FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW: Final[str] = "FAMILY_LIVE_LEGACY_SHADOW"
FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY: Final[str] = "FAMILY_LIVE_ONLY"

FAMILY_RUNTIME_MODES: Final[tuple[str, ...]] = (
    FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
    FAMILY_RUNTIME_MODE_LEGACY_LIVE_FAMILY_SHADOW,
    FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW,
    FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY,
)

# ============================================================================
# Live streams
# ============================================================================

STREAM_TICKS_MME_FUT: Final[str] = "ticks:mme:fut:stream"
STREAM_TICKS_MME_OPT: Final[str] = "ticks:mme:opt:stream"
STREAM_FEATURES_MME: Final[str] = "features:mme:stream"
STREAM_DECISIONS_MME: Final[str] = "decisions:mme:stream"
STREAM_DECISIONS_ACK: Final[str] = "decisions:ack:stream"
STREAM_ORDERS_MME: Final[str] = "orders:mme:stream"
STREAM_TRADES_LEDGER: Final[str] = "trades:ledger:stream"
STREAM_CMD_MME: Final[str] = "cmd:mme:stream"
STREAM_SYSTEM_HEALTH: Final[str] = "system:health:stream"
STREAM_SYSTEM_ERRORS: Final[str] = "system:errors:stream"

LIVE_STREAM_NAMES: Final[tuple[str, ...]] = (
    STREAM_TICKS_MME_FUT,
    STREAM_TICKS_MME_OPT,
    STREAM_FEATURES_MME,
    STREAM_DECISIONS_MME,
    STREAM_DECISIONS_ACK,
    STREAM_ORDERS_MME,
    STREAM_TRADES_LEDGER,
    STREAM_CMD_MME,
    STREAM_SYSTEM_HEALTH,
    STREAM_SYSTEM_ERRORS,
)

STREAM_TICKS_MME_FUT_ZERODHA: Final[str] = "ticks:mme:fut:zerodha:stream"
STREAM_TICKS_MME_FUT_DHAN: Final[str] = "ticks:mme:fut:dhan:stream"
STREAM_TICKS_MME_OPT_SELECTED_ZERODHA: Final[str] = "ticks:mme:opt:selected:zerodha:stream"
STREAM_TICKS_MME_OPT_SELECTED_DHAN: Final[str] = "ticks:mme:opt:selected:dhan:stream"
STREAM_TICKS_MME_OPT_CONTEXT_DHAN: Final[str] = "ticks:mme:opt:context:dhan:stream"
STREAM_PROVIDER_RUNTIME: Final[str] = "provider:runtime:stream"

LIVE_PROVIDER_STREAM_NAMES: Final[tuple[str, ...]] = (
    STREAM_TICKS_MME_FUT_ZERODHA,
    STREAM_TICKS_MME_FUT_DHAN,
    STREAM_TICKS_MME_OPT_SELECTED_ZERODHA,
    STREAM_TICKS_MME_OPT_SELECTED_DHAN,
    STREAM_TICKS_MME_OPT_CONTEXT_DHAN,
    STREAM_PROVIDER_RUNTIME,
)

# ============================================================================
# Replay streams
# ============================================================================

STREAM_REPLAY_TICKS_MME_FUT: Final[str] = replay_name(STREAM_TICKS_MME_FUT)
STREAM_REPLAY_TICKS_MME_OPT: Final[str] = replay_name(STREAM_TICKS_MME_OPT)
STREAM_REPLAY_FEATURES_MME: Final[str] = replay_name(STREAM_FEATURES_MME)
STREAM_REPLAY_DECISIONS_MME: Final[str] = replay_name(STREAM_DECISIONS_MME)
STREAM_REPLAY_DECISIONS_ACK: Final[str] = replay_name(STREAM_DECISIONS_ACK)
STREAM_REPLAY_ORDERS_MME: Final[str] = replay_name(STREAM_ORDERS_MME)
STREAM_REPLAY_TRADES_LEDGER: Final[str] = replay_name(STREAM_TRADES_LEDGER)
STREAM_REPLAY_CMD_MME: Final[str] = replay_name(STREAM_CMD_MME)
STREAM_REPLAY_SYSTEM_HEALTH: Final[str] = replay_name(STREAM_SYSTEM_HEALTH)
STREAM_REPLAY_SYSTEM_ERRORS: Final[str] = replay_name(STREAM_SYSTEM_ERRORS)

STREAM_REPLAY_TICKS_MME_FUT_ZERODHA: Final[str] = replay_name(STREAM_TICKS_MME_FUT_ZERODHA)
STREAM_REPLAY_TICKS_MME_FUT_DHAN: Final[str] = replay_name(STREAM_TICKS_MME_FUT_DHAN)
STREAM_REPLAY_TICKS_MME_OPT_SELECTED_ZERODHA: Final[str] = replay_name(
    STREAM_TICKS_MME_OPT_SELECTED_ZERODHA
)
STREAM_REPLAY_TICKS_MME_OPT_SELECTED_DHAN: Final[str] = replay_name(
    STREAM_TICKS_MME_OPT_SELECTED_DHAN
)
STREAM_REPLAY_TICKS_MME_OPT_CONTEXT_DHAN: Final[str] = replay_name(
    STREAM_TICKS_MME_OPT_CONTEXT_DHAN
)
STREAM_REPLAY_PROVIDER_RUNTIME: Final[str] = replay_name(STREAM_PROVIDER_RUNTIME)

REPLAY_STREAM_NAMES: Final[tuple[str, ...]] = (
    STREAM_REPLAY_TICKS_MME_FUT,
    STREAM_REPLAY_TICKS_MME_OPT,
    STREAM_REPLAY_FEATURES_MME,
    STREAM_REPLAY_DECISIONS_MME,
    STREAM_REPLAY_DECISIONS_ACK,
    STREAM_REPLAY_ORDERS_MME,
    STREAM_REPLAY_TRADES_LEDGER,
    STREAM_REPLAY_CMD_MME,
    STREAM_REPLAY_SYSTEM_HEALTH,
    STREAM_REPLAY_SYSTEM_ERRORS,
)

REPLAY_PROVIDER_STREAM_NAMES: Final[tuple[str, ...]] = (
    STREAM_REPLAY_TICKS_MME_FUT_ZERODHA,
    STREAM_REPLAY_TICKS_MME_FUT_DHAN,
    STREAM_REPLAY_TICKS_MME_OPT_SELECTED_ZERODHA,
    STREAM_REPLAY_TICKS_MME_OPT_SELECTED_DHAN,
    STREAM_REPLAY_TICKS_MME_OPT_CONTEXT_DHAN,
    STREAM_REPLAY_PROVIDER_RUNTIME,
)

# ============================================================================
# Live latest-state hashes / keys
# ============================================================================

HASH_STATE_INSTRUMENTS_MME: Final[str] = "state:instruments:mme"
HASH_STATE_SNAPSHOT_MME_FUT: Final[str] = "state:snapshot:mme:fut"
HASH_STATE_SNAPSHOT_MME_OPT_SELECTED: Final[str] = "state:snapshot:mme:opt:selected"
HASH_STATE_FEATURES_MME_FUT: Final[str] = "state:features:mme:fut"
HASH_STATE_BASELINES_MME_FUT: Final[str] = "state:baselines:mme:fut"
HASH_STATE_OPTION_CONFIRM: Final[str] = "state:option:confirm"
HASH_STATE_RISK: Final[str] = "state:risk"
HASH_STATE_POSITION_MME: Final[str] = "state:position:mme"
HASH_STATE_EXECUTION: Final[str] = "state:execution"
HASH_STATE_RUNTIME: Final[str] = "state:runtime"
HASH_STATE_MODE: Final[str] = "state:mode"
HASH_STATE_LOGIN: Final[str] = "state:login"
HASH_STATE_REPORT: Final[str] = "state:report"
HASH_PARAMS_MME: Final[str] = "params:mme"
HASH_PARAMS_MME_META: Final[str] = "params:mme:meta"

LIVE_STATE_HASH_NAMES: Final[tuple[str, ...]] = (
    HASH_STATE_INSTRUMENTS_MME,
    HASH_STATE_SNAPSHOT_MME_FUT,
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED,
    HASH_STATE_FEATURES_MME_FUT,
    HASH_STATE_BASELINES_MME_FUT,
    HASH_STATE_OPTION_CONFIRM,
    HASH_STATE_RISK,
    HASH_STATE_POSITION_MME,
    HASH_STATE_EXECUTION,
    HASH_STATE_RUNTIME,
    HASH_STATE_MODE,
    HASH_STATE_LOGIN,
    HASH_STATE_REPORT,
    HASH_PARAMS_MME,
    HASH_PARAMS_MME_META,
)

HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA: Final[str] = "state:snapshot:mme:fut:zerodha"
HASH_STATE_SNAPSHOT_MME_FUT_DHAN: Final[str] = "state:snapshot:mme:fut:dhan"
HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE: Final[str] = "state:snapshot:mme:fut:active"
HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: Final[str] = (
    "state:snapshot:mme:opt:selected:zerodha"
)
HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN: Final[str] = (
    "state:snapshot:mme:opt:selected:dhan"
)
HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE: Final[str] = (
    "state:snapshot:mme:opt:selected:active"
)
HASH_STATE_DHAN_CONTEXT: Final[str] = "state:context:mme:dhan"
HASH_STATE_PROVIDER_RUNTIME: Final[str] = "state:provider:runtime"

LIVE_PROVIDER_STATE_HASH_NAMES: Final[tuple[str, ...]] = (
    HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA,
    HASH_STATE_SNAPSHOT_MME_FUT_DHAN,
    HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE,
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE,
    HASH_STATE_DHAN_CONTEXT,
    HASH_STATE_PROVIDER_RUNTIME,
)

# ============================================================================
# Replay latest-state hashes / keys
# ============================================================================

HASH_REPLAY_STATE_INSTRUMENTS_MME: Final[str] = replay_name(HASH_STATE_INSTRUMENTS_MME)
HASH_REPLAY_STATE_SNAPSHOT_MME_FUT: Final[str] = replay_name(HASH_STATE_SNAPSHOT_MME_FUT)
HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED: Final[str] = replay_name(
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED
)
HASH_REPLAY_STATE_FEATURES_MME_FUT: Final[str] = replay_name(HASH_STATE_FEATURES_MME_FUT)
HASH_REPLAY_STATE_BASELINES_MME_FUT: Final[str] = replay_name(HASH_STATE_BASELINES_MME_FUT)
HASH_REPLAY_STATE_OPTION_CONFIRM: Final[str] = replay_name(HASH_STATE_OPTION_CONFIRM)
HASH_REPLAY_STATE_RISK: Final[str] = replay_name(HASH_STATE_RISK)
HASH_REPLAY_STATE_POSITION_MME: Final[str] = replay_name(HASH_STATE_POSITION_MME)
HASH_REPLAY_STATE_EXECUTION: Final[str] = replay_name(HASH_STATE_EXECUTION)
HASH_REPLAY_STATE_RUNTIME: Final[str] = replay_name(HASH_STATE_RUNTIME)
HASH_REPLAY_STATE_MODE: Final[str] = replay_name(HASH_STATE_MODE)
HASH_REPLAY_STATE_LOGIN: Final[str] = replay_name(HASH_STATE_LOGIN)
HASH_REPLAY_STATE_REPORT: Final[str] = replay_name(HASH_STATE_REPORT)
HASH_REPLAY_PARAMS_MME: Final[str] = replay_name(HASH_PARAMS_MME)
HASH_REPLAY_PARAMS_MME_META: Final[str] = replay_name(HASH_PARAMS_MME_META)

HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ZERODHA: Final[str] = replay_name(
    HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA
)
HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_DHAN: Final[str] = replay_name(
    HASH_STATE_SNAPSHOT_MME_FUT_DHAN
)
HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ACTIVE: Final[str] = replay_name(
    HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE
)
HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: Final[str] = replay_name(
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA
)
HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN: Final[str] = replay_name(
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN
)
HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE: Final[str] = replay_name(
    HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE
)
HASH_REPLAY_STATE_DHAN_CONTEXT: Final[str] = replay_name(HASH_STATE_DHAN_CONTEXT)
HASH_REPLAY_STATE_PROVIDER_RUNTIME: Final[str] = replay_name(HASH_STATE_PROVIDER_RUNTIME)

REPLAY_STATE_HASH_NAMES: Final[tuple[str, ...]] = (
    HASH_REPLAY_STATE_INSTRUMENTS_MME,
    HASH_REPLAY_STATE_SNAPSHOT_MME_FUT,
    HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED,
    HASH_REPLAY_STATE_FEATURES_MME_FUT,
    HASH_REPLAY_STATE_BASELINES_MME_FUT,
    HASH_REPLAY_STATE_OPTION_CONFIRM,
    HASH_REPLAY_STATE_RISK,
    HASH_REPLAY_STATE_POSITION_MME,
    HASH_REPLAY_STATE_EXECUTION,
    HASH_REPLAY_STATE_RUNTIME,
    HASH_REPLAY_STATE_MODE,
    HASH_REPLAY_STATE_LOGIN,
    HASH_REPLAY_STATE_REPORT,
    HASH_REPLAY_PARAMS_MME,
    HASH_REPLAY_PARAMS_MME_META,
)

REPLAY_PROVIDER_STATE_HASH_NAMES: Final[tuple[str, ...]] = (
    HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ZERODHA,
    HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_DHAN,
    HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ACTIVE,
    HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
    HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
    HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE,
    HASH_REPLAY_STATE_DHAN_CONTEXT,
    HASH_REPLAY_STATE_PROVIDER_RUNTIME,
)

# ============================================================================
# Health / heartbeat keys
# ============================================================================

KEY_HEALTH_LOGIN: Final[str] = "health:login"
KEY_HEALTH_INSTRUMENTS: Final[str] = "health:instruments"
KEY_HEALTH_FEEDS: Final[str] = "health:feeds"
KEY_HEALTH_FEATURES: Final[str] = "health:features"
KEY_HEALTH_STRATEGY: Final[str] = "health:strategy"
KEY_HEALTH_RISK: Final[str] = "health:risk"
KEY_HEALTH_EXECUTION: Final[str] = "health:execution"
KEY_HEALTH_MONITOR: Final[str] = "health:monitor"
KEY_HEALTH_REPORT: Final[str] = "health:report"

LIVE_HEALTH_KEYS: Final[tuple[str, ...]] = (
    KEY_HEALTH_LOGIN,
    KEY_HEALTH_INSTRUMENTS,
    KEY_HEALTH_FEEDS,
    KEY_HEALTH_FEATURES,
    KEY_HEALTH_STRATEGY,
    KEY_HEALTH_RISK,
    KEY_HEALTH_EXECUTION,
    KEY_HEALTH_MONITOR,
    KEY_HEALTH_REPORT,
)

KEY_HEALTH_ZERODHA_AUTH: Final[str] = "health:zerodha:auth"
KEY_HEALTH_ZERODHA_MARKETDATA: Final[str] = "health:zerodha:marketdata"
KEY_HEALTH_ZERODHA_EXECUTION: Final[str] = "health:zerodha:execution"
KEY_HEALTH_DHAN_AUTH: Final[str] = "health:dhan:auth"
KEY_HEALTH_DHAN_MARKETDATA: Final[str] = "health:dhan:marketdata"
KEY_HEALTH_DHAN_EXECUTION: Final[str] = "health:dhan:execution"
KEY_HEALTH_PROVIDER_RUNTIME: Final[str] = "health:provider:runtime"

LIVE_PROVIDER_HEALTH_KEYS: Final[tuple[str, ...]] = (
    KEY_HEALTH_ZERODHA_AUTH,
    KEY_HEALTH_ZERODHA_MARKETDATA,
    KEY_HEALTH_ZERODHA_EXECUTION,
    KEY_HEALTH_DHAN_AUTH,
    KEY_HEALTH_DHAN_MARKETDATA,
    KEY_HEALTH_DHAN_EXECUTION,
    KEY_HEALTH_PROVIDER_RUNTIME,
)

KEY_REPLAY_HEALTH_LOGIN: Final[str] = replay_name(KEY_HEALTH_LOGIN)
KEY_REPLAY_HEALTH_INSTRUMENTS: Final[str] = replay_name(KEY_HEALTH_INSTRUMENTS)
KEY_REPLAY_HEALTH_FEEDS: Final[str] = replay_name(KEY_HEALTH_FEEDS)
KEY_REPLAY_HEALTH_FEATURES: Final[str] = replay_name(KEY_HEALTH_FEATURES)
KEY_REPLAY_HEALTH_STRATEGY: Final[str] = replay_name(KEY_HEALTH_STRATEGY)
KEY_REPLAY_HEALTH_RISK: Final[str] = replay_name(KEY_HEALTH_RISK)
KEY_REPLAY_HEALTH_EXECUTION: Final[str] = replay_name(KEY_HEALTH_EXECUTION)
KEY_REPLAY_HEALTH_MONITOR: Final[str] = replay_name(KEY_HEALTH_MONITOR)
KEY_REPLAY_HEALTH_REPORT: Final[str] = replay_name(KEY_HEALTH_REPORT)

KEY_REPLAY_HEALTH_ZERODHA_AUTH: Final[str] = replay_name(KEY_HEALTH_ZERODHA_AUTH)
KEY_REPLAY_HEALTH_ZERODHA_MARKETDATA: Final[str] = replay_name(
    KEY_HEALTH_ZERODHA_MARKETDATA
)
KEY_REPLAY_HEALTH_ZERODHA_EXECUTION: Final[str] = replay_name(
    KEY_HEALTH_ZERODHA_EXECUTION
)
KEY_REPLAY_HEALTH_DHAN_AUTH: Final[str] = replay_name(KEY_HEALTH_DHAN_AUTH)
KEY_REPLAY_HEALTH_DHAN_MARKETDATA: Final[str] = replay_name(
    KEY_HEALTH_DHAN_MARKETDATA
)
KEY_REPLAY_HEALTH_DHAN_EXECUTION: Final[str] = replay_name(
    KEY_HEALTH_DHAN_EXECUTION
)
KEY_REPLAY_HEALTH_PROVIDER_RUNTIME: Final[str] = replay_name(
    KEY_HEALTH_PROVIDER_RUNTIME
)

REPLAY_HEALTH_KEYS: Final[tuple[str, ...]] = (
    KEY_REPLAY_HEALTH_LOGIN,
    KEY_REPLAY_HEALTH_INSTRUMENTS,
    KEY_REPLAY_HEALTH_FEEDS,
    KEY_REPLAY_HEALTH_FEATURES,
    KEY_REPLAY_HEALTH_STRATEGY,
    KEY_REPLAY_HEALTH_RISK,
    KEY_REPLAY_HEALTH_EXECUTION,
    KEY_REPLAY_HEALTH_MONITOR,
    KEY_REPLAY_HEALTH_REPORT,
)

REPLAY_PROVIDER_HEALTH_KEYS: Final[tuple[str, ...]] = (
    KEY_REPLAY_HEALTH_ZERODHA_AUTH,
    KEY_REPLAY_HEALTH_ZERODHA_MARKETDATA,
    KEY_REPLAY_HEALTH_ZERODHA_EXECUTION,
    KEY_REPLAY_HEALTH_DHAN_AUTH,
    KEY_REPLAY_HEALTH_DHAN_MARKETDATA,
    KEY_REPLAY_HEALTH_DHAN_EXECUTION,
    KEY_REPLAY_HEALTH_PROVIDER_RUNTIME,
)

# ============================================================================
# Process-safety lock keys
# ============================================================================

KEY_LOCK_FEEDS: Final[str] = "lock:feeds"
KEY_LOCK_STRATEGY: Final[str] = "lock:strategy"
KEY_LOCK_EXECUTION: Final[str] = "lock:execution"
KEY_LOCK_MONITOR: Final[str] = "lock:monitor"

LIVE_LOCK_KEYS: Final[tuple[str, ...]] = (
    KEY_LOCK_FEEDS,
    KEY_LOCK_STRATEGY,
    KEY_LOCK_EXECUTION,
    KEY_LOCK_MONITOR,
)

KEY_REPLAY_LOCK_FEEDS: Final[str] = replay_name(KEY_LOCK_FEEDS)
KEY_REPLAY_LOCK_STRATEGY: Final[str] = replay_name(KEY_LOCK_STRATEGY)
KEY_REPLAY_LOCK_EXECUTION: Final[str] = replay_name(KEY_LOCK_EXECUTION)
KEY_REPLAY_LOCK_MONITOR: Final[str] = replay_name(KEY_LOCK_MONITOR)

REPLAY_LOCK_KEYS: Final[tuple[str, ...]] = (
    KEY_REPLAY_LOCK_FEEDS,
    KEY_REPLAY_LOCK_STRATEGY,
    KEY_REPLAY_LOCK_EXECUTION,
    KEY_REPLAY_LOCK_MONITOR,
)

# ============================================================================
# Optional wake-up notify channels
# ============================================================================

CHANNEL_CMD_MME_NOTIFY: Final[str] = "cmd:mme:notify"
CHANNEL_REPLAY_CMD_MME_NOTIFY: Final[str] = replay_name(CHANNEL_CMD_MME_NOTIFY)

LIVE_NOTIFY_CHANNELS: Final[tuple[str, ...]] = (CHANNEL_CMD_MME_NOTIFY,)
REPLAY_NOTIFY_CHANNELS: Final[tuple[str, ...]] = (CHANNEL_REPLAY_CMD_MME_NOTIFY,)

# ============================================================================
# Consumer groups (live)
# ============================================================================

GROUP_FEATURES_MME_FUT_V1: Final[str] = "cg:features:mme:fut:v1"
GROUP_FEATURES_MME_OPT_V1: Final[str] = "cg:features:mme:opt:v1"
GROUP_STRATEGY_MME_V1: Final[str] = "cg:strategy:mme:v1"
GROUP_EXECUTION_MME_V1: Final[str] = "cg:execution:mme:v1"
GROUP_RISK_MME_V1: Final[str] = "cg:risk:mme:v1"
GROUP_MONITOR_MME_V1: Final[str] = "cg:monitor:mme:v1"

LIVE_GROUP_NAMES: Final[tuple[str, ...]] = (
    GROUP_FEATURES_MME_FUT_V1,
    GROUP_FEATURES_MME_OPT_V1,
    GROUP_STRATEGY_MME_V1,
    GROUP_EXECUTION_MME_V1,
    GROUP_RISK_MME_V1,
    GROUP_MONITOR_MME_V1,
)

# ============================================================================
# Consumer groups (replay)
# ============================================================================

GROUP_REPLAY_FEATURES_MME_FUT_V1: Final[str] = replay_name(GROUP_FEATURES_MME_FUT_V1)
GROUP_REPLAY_FEATURES_MME_OPT_V1: Final[str] = replay_name(GROUP_FEATURES_MME_OPT_V1)
GROUP_REPLAY_STRATEGY_MME_V1: Final[str] = replay_name(GROUP_STRATEGY_MME_V1)
GROUP_REPLAY_EXECUTION_MME_V1: Final[str] = replay_name(GROUP_EXECUTION_MME_V1)
GROUP_REPLAY_RISK_MME_V1: Final[str] = replay_name(GROUP_RISK_MME_V1)
GROUP_REPLAY_MONITOR_MME_V1: Final[str] = replay_name(GROUP_MONITOR_MME_V1)

REPLAY_GROUP_NAMES: Final[tuple[str, ...]] = (
    GROUP_REPLAY_FEATURES_MME_FUT_V1,
    GROUP_REPLAY_FEATURES_MME_OPT_V1,
    GROUP_REPLAY_STRATEGY_MME_V1,
    GROUP_REPLAY_EXECUTION_MME_V1,
    GROUP_REPLAY_RISK_MME_V1,
    GROUP_REPLAY_MONITOR_MME_V1,
)

# ============================================================================
# Event types
# ============================================================================

EVENT_TYPE_DECISION_EMITTED: Final[str] = "event:decision_emitted"
EVENT_TYPE_ORDER_PLACED: Final[str] = "event:order_placed"
EVENT_TYPE_ORDER_FILLED: Final[str] = "event:order_filled"
EVENT_TYPE_ORDER_REJECTED: Final[str] = "event:order_rejected"
EVENT_TYPE_POSITION_UPDATED: Final[str] = "event:position_updated"
EVENT_TYPE_RISK_UPDATED: Final[str] = "event:risk_updated"
EVENT_TYPE_COMMAND_PUBLISHED: Final[str] = "event:command_published"

EVENT_TYPES: Final[tuple[str, ...]] = (
    EVENT_TYPE_DECISION_EMITTED,
    EVENT_TYPE_ORDER_PLACED,
    EVENT_TYPE_ORDER_FILLED,
    EVENT_TYPE_ORDER_REJECTED,
    EVENT_TYPE_POSITION_UPDATED,
    EVENT_TYPE_RISK_UPDATED,
    EVENT_TYPE_COMMAND_PUBLISHED,
)

# ============================================================================
# Canonical ACK types
# ============================================================================

ACK_RECEIVED: Final[str] = "RECEIVED"
ACK_REJECTED: Final[str] = "REJECTED"
ACK_SENT_TO_BROKER: Final[str] = "SENT_TO_BROKER"
ACK_FILLED: Final[str] = "FILLED"
ACK_FAILED: Final[str] = "FAILED"
ACK_EXIT_SENT: Final[str] = "EXIT_SENT"
ACK_EXIT_FILLED: Final[str] = "EXIT_FILLED"

ACK_TYPES: Final[tuple[str, ...]] = (
    ACK_RECEIVED,
    ACK_REJECTED,
    ACK_SENT_TO_BROKER,
    ACK_FILLED,
    ACK_FAILED,
    ACK_EXIT_SENT,
    ACK_EXIT_FILLED,
)

# ============================================================================
# Canonical command types
# ============================================================================

CMD_PARAMS_RELOAD: Final[str] = "PARAMS_RELOAD"
CMD_PAUSE_TRADING: Final[str] = "PAUSE_TRADING"
CMD_RESUME_TRADING: Final[str] = "RESUME_TRADING"
CMD_FORCE_FLATTEN: Final[str] = "FORCE_FLATTEN"
CMD_SET_MODE: Final[str] = "SET_MODE"

COMMAND_TYPES: Final[tuple[str, ...]] = (
    CMD_PARAMS_RELOAD,
    CMD_PAUSE_TRADING,
    CMD_RESUME_TRADING,
    CMD_FORCE_FLATTEN,
    CMD_SET_MODE,
)

# ============================================================================
# Canonical actions
# ============================================================================

ACTION_ENTER: Final[str] = "ENTER"
ACTION_EXIT: Final[str] = "EXIT"
ACTION_HOLD: Final[str] = "HOLD"
ACTION_BLOCK: Final[str] = "BLOCK"
ACTION_ENTER_CALL: Final[str] = "ENTER_CALL"
ACTION_ENTER_PUT: Final[str] = "ENTER_PUT"

ACTION_TYPES: Final[tuple[str, ...]] = (
    ACTION_ENTER,
    ACTION_EXIT,
    ACTION_HOLD,
    ACTION_BLOCK,
    ACTION_ENTER_CALL,
    ACTION_ENTER_PUT,
)

# ============================================================================
# Canonical position sides
# ============================================================================

POSITION_SIDE_FLAT: Final[str] = "FLAT"
POSITION_SIDE_LONG_CALL: Final[str] = "LONG_CALL"
POSITION_SIDE_LONG_PUT: Final[str] = "LONG_PUT"

POSITION_SIDE_TYPES: Final[tuple[str, ...]] = (
    POSITION_SIDE_FLAT,
    POSITION_SIDE_LONG_CALL,
    POSITION_SIDE_LONG_PUT,
)

SIDE_CALL: Final[str] = "CALL"
SIDE_PUT: Final[str] = "PUT"
SIDE_FLAT: Final[str] = "FLAT"

SIDE_TYPES: Final[tuple[str, ...]] = (
    SIDE_CALL,
    SIDE_PUT,
    SIDE_FLAT,
)

# ============================================================================
# Canonical strategy direction modes
# ============================================================================

STRATEGY_CALL: Final[str] = "CALL"
STRATEGY_PUT: Final[str] = "PUT"
STRATEGY_AUTO: Final[str] = "AUTO"

STRATEGY_MODES: Final[tuple[str, ...]] = (
    STRATEGY_CALL,
    STRATEGY_PUT,
    STRATEGY_AUTO,
)

# ============================================================================
# Canonical entry modes
# ============================================================================

ENTRY_MODE_UNKNOWN: Final[str] = "UNKNOWN"
ENTRY_MODE_ATM: Final[str] = "ATM"
ENTRY_MODE_ATM1: Final[str] = "ATM1"
ENTRY_MODE_DIRECT: Final[str] = "DIRECT"
ENTRY_MODE_FALLBACK: Final[str] = "FALLBACK"
ENTRY_MODE_ATM1_FALLBACK: Final[str] = ENTRY_MODE_FALLBACK

ENTRY_MODES: Final[tuple[str, ...]] = (
    ENTRY_MODE_UNKNOWN,
    ENTRY_MODE_ATM,
    ENTRY_MODE_ATM1,
    ENTRY_MODE_DIRECT,
    ENTRY_MODE_FALLBACK,
)

# ============================================================================
# Canonical position effects
# ============================================================================

POSITION_EFFECT_OPEN: Final[str] = "OPEN"
POSITION_EFFECT_CLOSE: Final[str] = "CLOSE"
POSITION_EFFECT_REDUCE: Final[str] = "REDUCE"
POSITION_EFFECT_FLATTEN: Final[str] = "FLATTEN"
POSITION_EFFECT_NONE: Final[str] = "NONE"

POSITION_EFFECTS: Final[tuple[str, ...]] = (
    POSITION_EFFECT_OPEN,
    POSITION_EFFECT_CLOSE,
    POSITION_EFFECT_REDUCE,
    POSITION_EFFECT_FLATTEN,
    POSITION_EFFECT_NONE,
)

# ============================================================================
# Canonical execution modes
# ============================================================================

EXECUTION_MODE_NORMAL: Final[str] = "NORMAL"
EXECUTION_MODE_EXIT_ONLY: Final[str] = "EXIT_ONLY"
EXECUTION_MODE_DEGRADED: Final[str] = "DEGRADED"
EXECUTION_MODE_FATAL: Final[str] = "FATAL"

EXECUTION_MODES: Final[tuple[str, ...]] = (
    EXECUTION_MODE_NORMAL,
    EXECUTION_MODE_EXIT_ONLY,
    EXECUTION_MODE_DEGRADED,
    EXECUTION_MODE_FATAL,
)

EXEC_MODE_NORMAL: Final[str] = EXECUTION_MODE_NORMAL
EXEC_MODE_EXIT_ONLY: Final[str] = EXECUTION_MODE_EXIT_ONLY
EXEC_MODE_DEGRADED: Final[str] = EXECUTION_MODE_DEGRADED
EXEC_MODE_FATAL: Final[str] = EXECUTION_MODE_FATAL

# ============================================================================
# Error severities
# ============================================================================

ERROR_SEVERITY_INFO: Final[str] = "INFO"
ERROR_SEVERITY_WARN: Final[str] = "WARN"
ERROR_SEVERITY_ERROR: Final[str] = "ERROR"
ERROR_SEVERITY_FATAL: Final[str] = "FATAL"

ERROR_SEVERITIES: Final[tuple[str, ...]] = (
    ERROR_SEVERITY_INFO,
    ERROR_SEVERITY_WARN,
    ERROR_SEVERITY_ERROR,
    ERROR_SEVERITY_FATAL,
)

# ============================================================================
# Health statuses
# ============================================================================

HEALTH_STATUS_OK: Final[str] = "OK"
HEALTH_STATUS_WARN: Final[str] = "WARN"
HEALTH_STATUS_ERROR: Final[str] = "ERROR"

HEALTH_OK: Final[str] = HEALTH_STATUS_OK
HEALTH_WARN: Final[str] = HEALTH_STATUS_WARN
HEALTH_ERROR: Final[str] = HEALTH_STATUS_ERROR

HEALTH_STATUSES: Final[tuple[str, ...]] = (
    HEALTH_STATUS_OK,
    HEALTH_STATUS_WARN,
    HEALTH_STATUS_ERROR,
)

# ============================================================================
# Canonical runtime/system states
# ============================================================================

STATE_IDLE: Final[str] = "IDLE"
STATE_SCANNING: Final[str] = "SCANNING"
STATE_ARMED: Final[str] = "ARMED"
STATE_SIGNAL_READY: Final[str] = "SIGNAL_READY"
STATE_CONFIRMING: Final[str] = "CONFIRMING"
STATE_RETEST_MONITOR: Final[str] = "RETEST_MONITOR"
STATE_ENTRY_PENDING: Final[str] = "ENTRY_PENDING"
STATE_POSITION_OPEN: Final[str] = "POSITION_OPEN"
STATE_EXIT_PENDING: Final[str] = "EXIT_PENDING"
STATE_COOLDOWN: Final[str] = "COOLDOWN"
STATE_DISABLED: Final[str] = "DISABLED"
STATE_WAIT: Final[str] = "WAIT"

SYSTEM_STATES: Final[tuple[str, ...]] = (
    STATE_IDLE,
    STATE_SCANNING,
    STATE_ARMED,
    STATE_SIGNAL_READY,
    STATE_CONFIRMING,
    STATE_RETEST_MONITOR,
    STATE_ENTRY_PENDING,
    STATE_POSITION_OPEN,
    STATE_EXIT_PENDING,
    STATE_COOLDOWN,
    STATE_DISABLED,
    STATE_WAIT,
)

# ============================================================================
# Control modes for SET_MODE
# ============================================================================

CONTROL_MODE_NORMAL: Final[str] = "NORMAL"
CONTROL_MODE_SAFE: Final[str] = "SAFE"
CONTROL_MODE_REPLAY: Final[str] = "REPLAY"
CONTROL_MODE_DISABLED: Final[str] = "DISABLED"

CONTROL_MODES: Final[tuple[str, ...]] = (
    CONTROL_MODE_NORMAL,
    CONTROL_MODE_SAFE,
    CONTROL_MODE_REPLAY,
    CONTROL_MODE_DISABLED,
)

# ============================================================================
# Compatibility alias layer
# ============================================================================

STREAM_CMD: Final[str] = STREAM_CMD_MME
STREAM_DECISIONS: Final[str] = STREAM_DECISIONS_MME
STREAM_ORDERS: Final[str] = STREAM_ORDERS_MME
STREAM_FEATURES: Final[str] = STREAM_FEATURES_MME

STATE_INSTRUMENTS: Final[str] = HASH_STATE_INSTRUMENTS_MME
STATE_SNAPSHOT_FUT: Final[str] = HASH_STATE_SNAPSHOT_MME_FUT
STATE_SNAPSHOT_OPT_SELECTED: Final[str] = HASH_STATE_SNAPSHOT_MME_OPT_SELECTED
STATE_FEATURES: Final[str] = HASH_STATE_FEATURES_MME_FUT
STATE_BASELINES: Final[str] = HASH_STATE_BASELINES_MME_FUT
STATE_OPTION_CONFIRM: Final[str] = HASH_STATE_OPTION_CONFIRM
STATE_RISK: Final[str] = HASH_STATE_RISK
STATE_POSITION: Final[str] = HASH_STATE_POSITION_MME
STATE_EXECUTION: Final[str] = HASH_STATE_EXECUTION
STATE_RUNTIME: Final[str] = HASH_STATE_RUNTIME
STATE_MODE: Final[str] = HASH_STATE_MODE
STATE_LOGIN: Final[str] = HASH_STATE_LOGIN
STATE_REPORT: Final[str] = HASH_STATE_REPORT
STATE_PARAMS: Final[str] = HASH_PARAMS_MME
STATE_PARAMS_META: Final[str] = HASH_PARAMS_MME_META

HB_LOGIN: Final[str] = KEY_HEALTH_LOGIN
HB_INSTRUMENTS: Final[str] = KEY_HEALTH_INSTRUMENTS
HB_FEEDS: Final[str] = KEY_HEALTH_FEEDS
HB_FEATURES: Final[str] = KEY_HEALTH_FEATURES
HB_STRATEGY: Final[str] = KEY_HEALTH_STRATEGY
HB_RISK: Final[str] = KEY_HEALTH_RISK
HB_EXECUTION: Final[str] = KEY_HEALTH_EXECUTION
HB_MONITOR: Final[str] = KEY_HEALTH_MONITOR
HB_REPORT: Final[str] = KEY_HEALTH_REPORT

GROUP_EXEC: Final[str] = GROUP_EXECUTION_MME_V1
GROUP_RISK: Final[str] = GROUP_RISK_MME_V1
GROUP_MONITOR: Final[str] = GROUP_MONITOR_MME_V1
GROUP_STRATEGY: Final[str] = GROUP_STRATEGY_MME_V1
GROUP_FEATURES_FUT: Final[str] = GROUP_FEATURES_MME_FUT_V1
GROUP_FEATURES_OPT: Final[str] = GROUP_FEATURES_MME_OPT_V1

LOCK_FEEDS: Final[str] = KEY_LOCK_FEEDS
LOCK_STRATEGY: Final[str] = KEY_LOCK_STRATEGY
LOCK_EXECUTION: Final[str] = KEY_LOCK_EXECUTION
LOCK_MONITOR: Final[str] = KEY_LOCK_MONITOR

STATE_SNAPSHOT_FUT_ZERODHA: Final[str] = HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA
STATE_SNAPSHOT_FUT_DHAN: Final[str] = HASH_STATE_SNAPSHOT_MME_FUT_DHAN
STATE_SNAPSHOT_FUT_ACTIVE: Final[str] = HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE
STATE_SNAPSHOT_OPT_SELECTED_ZERODHA: Final[str] = HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA
STATE_SNAPSHOT_OPT_SELECTED_DHAN: Final[str] = HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN
STATE_SNAPSHOT_OPT_SELECTED_ACTIVE: Final[str] = HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE
STATE_DHAN_CONTEXT: Final[str] = HASH_STATE_DHAN_CONTEXT
STATE_PROVIDER_RUNTIME: Final[str] = HASH_STATE_PROVIDER_RUNTIME

HB_ZERODHA_AUTH: Final[str] = KEY_HEALTH_ZERODHA_AUTH
HB_ZERODHA_MARKETDATA: Final[str] = KEY_HEALTH_ZERODHA_MARKETDATA
HB_ZERODHA_EXECUTION: Final[str] = KEY_HEALTH_ZERODHA_EXECUTION
HB_DHAN_AUTH: Final[str] = KEY_HEALTH_DHAN_AUTH
HB_DHAN_MARKETDATA: Final[str] = KEY_HEALTH_DHAN_MARKETDATA
HB_DHAN_EXECUTION: Final[str] = KEY_HEALTH_DHAN_EXECUTION
HB_PROVIDER_RUNTIME: Final[str] = KEY_HEALTH_PROVIDER_RUNTIME

# ============================================================================
# Public aliases for model validation
# ============================================================================

ALLOWED_ACK_TYPES: Final[tuple[str, ...]] = ACK_TYPES
ALLOWED_ACTION_TYPES: Final[tuple[str, ...]] = ACTION_TYPES
ALLOWED_COMMAND_TYPES: Final[tuple[str, ...]] = COMMAND_TYPES
ALLOWED_CONTROL_MODES: Final[tuple[str, ...]] = CONTROL_MODES
ALLOWED_ENTRY_MODES: Final[tuple[str, ...]] = ENTRY_MODES
ALLOWED_ERROR_SEVERITIES: Final[tuple[str, ...]] = ERROR_SEVERITIES
ALLOWED_EXECUTION_MODES: Final[tuple[str, ...]] = EXECUTION_MODES
ALLOWED_HEALTH_STATUSES: Final[tuple[str, ...]] = HEALTH_STATUSES
ALLOWED_POSITION_EFFECTS: Final[tuple[str, ...]] = POSITION_EFFECTS
ALLOWED_POSITION_SIDES: Final[tuple[str, ...]] = POSITION_SIDE_TYPES
ALLOWED_SIDE_TYPES: Final[tuple[str, ...]] = SIDE_TYPES
ALLOWED_STRATEGY_MODES: Final[tuple[str, ...]] = STRATEGY_MODES
ALLOWED_SYSTEM_STATES: Final[tuple[str, ...]] = SYSTEM_STATES
ALLOWED_STRATEGY_FAMILY_IDS: Final[tuple[str, ...]] = STRATEGY_FAMILY_IDS
ALLOWED_DOCTRINE_IDS: Final[tuple[str, ...]] = DOCTRINE_IDS
ALLOWED_BRANCH_IDS: Final[tuple[str, ...]] = BRANCH_IDS
ALLOWED_STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = STRATEGY_RUNTIME_MODES
ALLOWED_FAMILY_RUNTIME_MODES: Final[tuple[str, ...]] = FAMILY_RUNTIME_MODES
ALLOWED_PROVIDER_IDS: Final[tuple[str, ...]] = PROVIDER_IDS
ALLOWED_PROVIDER_ROLES: Final[tuple[str, ...]] = PROVIDER_ROLES
ALLOWED_PROVIDER_STATUSES: Final[tuple[str, ...]] = PROVIDER_STATUSES
ALLOWED_PROVIDER_FAILOVER_MODES: Final[tuple[str, ...]] = PROVIDER_FAILOVER_MODES
ALLOWED_PROVIDER_OVERRIDE_MODES: Final[tuple[str, ...]] = PROVIDER_OVERRIDE_MODES
ALLOWED_PROVIDER_TRANSITION_REASONS: Final[tuple[str, ...]] = (
    PROVIDER_TRANSITION_REASONS
)

# ============================================================================
# Ownership registries
# ============================================================================

STREAM_OWNERS: Final[Mapping[str, str]] = MappingProxyType(
    {
        STREAM_TICKS_MME_FUT: SERVICE_FEEDS,
        STREAM_TICKS_MME_OPT: SERVICE_FEEDS,
        STREAM_FEATURES_MME: SERVICE_FEATURES,
        STREAM_DECISIONS_MME: SERVICE_STRATEGY,
        STREAM_DECISIONS_ACK: SERVICE_EXECUTION,
        STREAM_ORDERS_MME: SERVICE_EXECUTION,
        STREAM_TRADES_LEDGER: SERVICE_EXECUTION,
        STREAM_CMD_MME: SERVICE_MONITOR,
        STREAM_SYSTEM_HEALTH: SERVICE_MONITOR,
        STREAM_SYSTEM_ERRORS: SERVICE_MONITOR,
        STREAM_TICKS_MME_FUT_ZERODHA: SERVICE_FEEDS,
        STREAM_TICKS_MME_FUT_DHAN: SERVICE_FEEDS,
        STREAM_TICKS_MME_OPT_SELECTED_ZERODHA: SERVICE_FEEDS,
        STREAM_TICKS_MME_OPT_SELECTED_DHAN: SERVICE_FEEDS,
        STREAM_TICKS_MME_OPT_CONTEXT_DHAN: SERVICE_FEEDS,
        STREAM_PROVIDER_RUNTIME: SERVICE_MAIN,
    }
)

STATE_HASH_OWNERS: Final[Mapping[str, str]] = MappingProxyType(
    {
        HASH_STATE_INSTRUMENTS_MME: SERVICE_INSTRUMENTS,
        HASH_STATE_SNAPSHOT_MME_FUT: SERVICE_FEEDS,
        HASH_STATE_SNAPSHOT_MME_OPT_SELECTED: SERVICE_FEEDS,
        HASH_STATE_FEATURES_MME_FUT: SERVICE_FEATURES,
        HASH_STATE_BASELINES_MME_FUT: SERVICE_FEATURES,
        HASH_STATE_OPTION_CONFIRM: SERVICE_FEATURES,
        HASH_STATE_RISK: SERVICE_RISK,
        HASH_STATE_POSITION_MME: SERVICE_EXECUTION,
        HASH_STATE_EXECUTION: SERVICE_EXECUTION,
        HASH_STATE_RUNTIME: SERVICE_MAIN,
        HASH_STATE_MODE: SERVICE_MAIN,
        HASH_STATE_LOGIN: SERVICE_LOGIN,
        HASH_STATE_REPORT: SERVICE_REPORT,
        HASH_PARAMS_MME: SERVICE_MAIN,
        HASH_PARAMS_MME_META: SERVICE_MAIN,
        HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA: SERVICE_FEEDS,
        HASH_STATE_SNAPSHOT_MME_FUT_DHAN: SERVICE_FEEDS,
        HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE: SERVICE_FEEDS,
        HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA: SERVICE_FEEDS,
        HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN: SERVICE_FEEDS,
        HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE: SERVICE_FEEDS,
        HASH_STATE_DHAN_CONTEXT: SERVICE_FEEDS,
        HASH_STATE_PROVIDER_RUNTIME: SERVICE_MAIN,
    }
)

HEALTH_OWNERS: Final[Mapping[str, str]] = MappingProxyType(
    {
        KEY_HEALTH_LOGIN: SERVICE_LOGIN,
        KEY_HEALTH_INSTRUMENTS: SERVICE_INSTRUMENTS,
        KEY_HEALTH_FEEDS: SERVICE_FEEDS,
        KEY_HEALTH_FEATURES: SERVICE_FEATURES,
        KEY_HEALTH_STRATEGY: SERVICE_STRATEGY,
        KEY_HEALTH_RISK: SERVICE_RISK,
        KEY_HEALTH_EXECUTION: SERVICE_EXECUTION,
        KEY_HEALTH_MONITOR: SERVICE_MONITOR,
        KEY_HEALTH_REPORT: SERVICE_REPORT,
        KEY_HEALTH_ZERODHA_AUTH: SERVICE_LOGIN,
        KEY_HEALTH_ZERODHA_MARKETDATA: SERVICE_FEEDS,
        KEY_HEALTH_ZERODHA_EXECUTION: SERVICE_EXECUTION,
        KEY_HEALTH_DHAN_AUTH: SERVICE_LOGIN,
        KEY_HEALTH_DHAN_MARKETDATA: SERVICE_FEEDS,
        KEY_HEALTH_DHAN_EXECUTION: SERVICE_EXECUTION,
        KEY_HEALTH_PROVIDER_RUNTIME: SERVICE_MAIN,
    }
)

LOCK_OWNERS: Final[Mapping[str, str]] = MappingProxyType(
    {
        KEY_LOCK_FEEDS: SERVICE_FEEDS,
        KEY_LOCK_STRATEGY: SERVICE_STRATEGY,
        KEY_LOCK_EXECUTION: SERVICE_EXECUTION,
        KEY_LOCK_MONITOR: SERVICE_MONITOR,
    }
)

CHANNEL_OWNERS: Final[Mapping[str, str]] = MappingProxyType(
    {
        CHANNEL_CMD_MME_NOTIFY: SERVICE_MONITOR,
    }
)

# Explicit additive-publisher registries for streams that have one primary
# semantic owner but permit additive appenders.
STREAM_ADDITIVE_PUBLISHERS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        STREAM_SYSTEM_HEALTH: (
            SERVICE_LOGIN,
            SERVICE_FEEDS,
            SERVICE_FEATURES,
            SERVICE_STRATEGY,
            SERVICE_RISK,
            SERVICE_EXECUTION,
            SERVICE_MONITOR,
            SERVICE_REPORT,
        ),
        STREAM_SYSTEM_ERRORS: (
            SERVICE_LOGIN,
            SERVICE_FEEDS,
            SERVICE_FEATURES,
            SERVICE_STRATEGY,
            SERVICE_RISK,
            SERVICE_EXECUTION,
            SERVICE_MONITOR,
            SERVICE_REPORT,
        ),
    }
)

# ============================================================================
# Service registry
# ============================================================================

SERVICE_REGISTRY: Final[Mapping[str, ServiceDef]] = MappingProxyType(
    {
        SERVICE_MAIN: ServiceDef(
            name=SERVICE_MAIN,
            module_path="app.mme_scalpx.main",
            description="Single composition root / orchestration / supervision.",
        ),
        SERVICE_LOGIN: ServiceDef(
            name=SERVICE_LOGIN,
            module_path="app.mme_scalpx.integrations.login",
            owns_heartbeat=KEY_HEALTH_LOGIN,
            description="Broker auth, token refresh, and broker readiness.",
        ),
        SERVICE_INSTRUMENTS: ServiceDef(
            name=SERVICE_INSTRUMENTS,
            module_path="app.mme_scalpx.domain.instruments",
            owns_heartbeat=KEY_HEALTH_INSTRUMENTS,
            description="Instrument identity and runtime contract selection.",
        ),
        SERVICE_FEEDS: ServiceDef(
            name=SERVICE_FEEDS,
            module_path="app.mme_scalpx.services.feeds",
            owns_heartbeat=KEY_HEALTH_FEEDS,
            owns_lock=KEY_LOCK_FEEDS,
            description="Market-data ingestion and snapshot ownership.",
        ),
        SERVICE_FEATURES: ServiceDef(
            name=SERVICE_FEATURES,
            module_path="app.mme_scalpx.services.features",
            owns_heartbeat=KEY_HEALTH_FEATURES,
            description="Feature extraction and baseline maintenance.",
        ),
        SERVICE_STRATEGY: ServiceDef(
            name=SERVICE_STRATEGY,
            module_path="app.mme_scalpx.services.strategy",
            owns_heartbeat=KEY_HEALTH_STRATEGY,
            owns_lock=KEY_LOCK_STRATEGY,
            description="Decision engine and deterministic state machine.",
        ),
        SERVICE_RISK: ServiceDef(
            name=SERVICE_RISK,
            module_path="app.mme_scalpx.services.risk",
            owns_heartbeat=KEY_HEALTH_RISK,
            description="Entry veto and risk state ownership; never blocks exits.",
        ),
        SERVICE_EXECUTION: ServiceDef(
            name=SERVICE_EXECUTION,
            module_path="app.mme_scalpx.services.execution",
            owns_heartbeat=KEY_HEALTH_EXECUTION,
            owns_lock=KEY_LOCK_EXECUTION,
            description="Order routing, ACK emission, fills, and sole position truth.",
        ),
        SERVICE_MONITOR: ServiceDef(
            name=SERVICE_MONITOR,
            module_path="app.mme_scalpx.services.monitor",
            owns_heartbeat=KEY_HEALTH_MONITOR,
            owns_lock=KEY_LOCK_MONITOR,
            description="Observability and control-plane command publisher only.",
        ),
        SERVICE_REPORT: ServiceDef(
            name=SERVICE_REPORT,
            module_path="app.mme_scalpx.services.report",
            owns_heartbeat=KEY_HEALTH_REPORT,
            description="Read-only reconstruction and reporting.",
        ),
    }
)

# ============================================================================
# Bundle types
# ============================================================================


@dataclass(frozen=True, slots=True)
class StreamSet:
    ticks_mme_fut: str
    ticks_mme_opt: str
    features_mme: str
    decisions_mme: str
    decisions_ack: str
    orders_mme: str
    trades_ledger: str
    cmd_mme: str
    system_health: str
    system_errors: str


@dataclass(frozen=True, slots=True)
class StateHashSet:
    instruments_mme: str
    snapshot_mme_fut: str
    snapshot_mme_opt_selected: str
    features_mme_fut: str
    baselines_mme_fut: str
    option_confirm: str
    risk: str
    position_mme: str
    execution: str
    runtime: str
    mode: str
    login: str
    report: str
    params_mme: str
    params_mme_meta: str


@dataclass(frozen=True, slots=True)
class HealthSet:
    login: str
    instruments: str
    feeds: str
    features: str
    strategy: str
    risk: str
    execution: str
    monitor: str
    report: str


@dataclass(frozen=True, slots=True)
class LockSet:
    feeds: str
    strategy: str
    execution: str
    monitor: str


@dataclass(frozen=True, slots=True)
class GroupSet:
    features_mme_fut: str
    features_mme_opt: str
    strategy_mme: str
    execution_mme: str
    risk_mme: str
    monitor_mme: str


@dataclass(frozen=True, slots=True)
class ProviderStreamSet:
    ticks_mme_fut_zerodha: str
    ticks_mme_fut_dhan: str
    ticks_mme_opt_selected_zerodha: str
    ticks_mme_opt_selected_dhan: str
    ticks_mme_opt_context_dhan: str
    provider_runtime: str


@dataclass(frozen=True, slots=True)
class ProviderStateHashSet:
    snapshot_mme_fut_zerodha: str
    snapshot_mme_fut_dhan: str
    snapshot_mme_fut_active: str
    snapshot_mme_opt_selected_zerodha: str
    snapshot_mme_opt_selected_dhan: str
    snapshot_mme_opt_selected_active: str
    dhan_context: str
    provider_runtime: str


@dataclass(frozen=True, slots=True)
class ProviderHealthSet:
    zerodha_auth: str
    zerodha_marketdata: str
    zerodha_execution: str
    dhan_auth: str
    dhan_marketdata: str
    dhan_execution: str
    provider_runtime: str


# ============================================================================
# Live / replay bundles
# ============================================================================

LIVE_STREAMS: Final[StreamSet] = StreamSet(
    ticks_mme_fut=STREAM_TICKS_MME_FUT,
    ticks_mme_opt=STREAM_TICKS_MME_OPT,
    features_mme=STREAM_FEATURES_MME,
    decisions_mme=STREAM_DECISIONS_MME,
    decisions_ack=STREAM_DECISIONS_ACK,
    orders_mme=STREAM_ORDERS_MME,
    trades_ledger=STREAM_TRADES_LEDGER,
    cmd_mme=STREAM_CMD_MME,
    system_health=STREAM_SYSTEM_HEALTH,
    system_errors=STREAM_SYSTEM_ERRORS,
)

REPLAY_STREAMS: Final[StreamSet] = StreamSet(
    ticks_mme_fut=STREAM_REPLAY_TICKS_MME_FUT,
    ticks_mme_opt=STREAM_REPLAY_TICKS_MME_OPT,
    features_mme=STREAM_REPLAY_FEATURES_MME,
    decisions_mme=STREAM_REPLAY_DECISIONS_MME,
    decisions_ack=STREAM_REPLAY_DECISIONS_ACK,
    orders_mme=STREAM_REPLAY_ORDERS_MME,
    trades_ledger=STREAM_REPLAY_TRADES_LEDGER,
    cmd_mme=STREAM_REPLAY_CMD_MME,
    system_health=STREAM_REPLAY_SYSTEM_HEALTH,
    system_errors=STREAM_REPLAY_SYSTEM_ERRORS,
)

LIVE_STATE_HASHES: Final[StateHashSet] = StateHashSet(
    instruments_mme=HASH_STATE_INSTRUMENTS_MME,
    snapshot_mme_fut=HASH_STATE_SNAPSHOT_MME_FUT,
    snapshot_mme_opt_selected=HASH_STATE_SNAPSHOT_MME_OPT_SELECTED,
    features_mme_fut=HASH_STATE_FEATURES_MME_FUT,
    baselines_mme_fut=HASH_STATE_BASELINES_MME_FUT,
    option_confirm=HASH_STATE_OPTION_CONFIRM,
    risk=HASH_STATE_RISK,
    position_mme=HASH_STATE_POSITION_MME,
    execution=HASH_STATE_EXECUTION,
    runtime=HASH_STATE_RUNTIME,
    mode=HASH_STATE_MODE,
    login=HASH_STATE_LOGIN,
    report=HASH_STATE_REPORT,
    params_mme=HASH_PARAMS_MME,
    params_mme_meta=HASH_PARAMS_MME_META,
)

REPLAY_STATE_HASHES: Final[StateHashSet] = StateHashSet(
    instruments_mme=HASH_REPLAY_STATE_INSTRUMENTS_MME,
    snapshot_mme_fut=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT,
    snapshot_mme_opt_selected=HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED,
    features_mme_fut=HASH_REPLAY_STATE_FEATURES_MME_FUT,
    baselines_mme_fut=HASH_REPLAY_STATE_BASELINES_MME_FUT,
    option_confirm=HASH_REPLAY_STATE_OPTION_CONFIRM,
    risk=HASH_REPLAY_STATE_RISK,
    position_mme=HASH_REPLAY_STATE_POSITION_MME,
    execution=HASH_REPLAY_STATE_EXECUTION,
    runtime=HASH_REPLAY_STATE_RUNTIME,
    mode=HASH_REPLAY_STATE_MODE,
    login=HASH_REPLAY_STATE_LOGIN,
    report=HASH_REPLAY_STATE_REPORT,
    params_mme=HASH_REPLAY_PARAMS_MME,
    params_mme_meta=HASH_REPLAY_PARAMS_MME_META,
)

LIVE_HEALTH: Final[HealthSet] = HealthSet(
    login=KEY_HEALTH_LOGIN,
    instruments=KEY_HEALTH_INSTRUMENTS,
    feeds=KEY_HEALTH_FEEDS,
    features=KEY_HEALTH_FEATURES,
    strategy=KEY_HEALTH_STRATEGY,
    risk=KEY_HEALTH_RISK,
    execution=KEY_HEALTH_EXECUTION,
    monitor=KEY_HEALTH_MONITOR,
    report=KEY_HEALTH_REPORT,
)

REPLAY_HEALTH: Final[HealthSet] = HealthSet(
    login=KEY_REPLAY_HEALTH_LOGIN,
    instruments=KEY_REPLAY_HEALTH_INSTRUMENTS,
    feeds=KEY_REPLAY_HEALTH_FEEDS,
    features=KEY_REPLAY_HEALTH_FEATURES,
    strategy=KEY_REPLAY_HEALTH_STRATEGY,
    risk=KEY_REPLAY_HEALTH_RISK,
    execution=KEY_REPLAY_HEALTH_EXECUTION,
    monitor=KEY_REPLAY_HEALTH_MONITOR,
    report=KEY_REPLAY_HEALTH_REPORT,
)

LIVE_PROVIDER_STREAMS: Final[ProviderStreamSet] = ProviderStreamSet(
    ticks_mme_fut_zerodha=STREAM_TICKS_MME_FUT_ZERODHA,
    ticks_mme_fut_dhan=STREAM_TICKS_MME_FUT_DHAN,
    ticks_mme_opt_selected_zerodha=STREAM_TICKS_MME_OPT_SELECTED_ZERODHA,
    ticks_mme_opt_selected_dhan=STREAM_TICKS_MME_OPT_SELECTED_DHAN,
    ticks_mme_opt_context_dhan=STREAM_TICKS_MME_OPT_CONTEXT_DHAN,
    provider_runtime=STREAM_PROVIDER_RUNTIME,
)

REPLAY_PROVIDER_STREAMS: Final[ProviderStreamSet] = ProviderStreamSet(
    ticks_mme_fut_zerodha=STREAM_REPLAY_TICKS_MME_FUT_ZERODHA,
    ticks_mme_fut_dhan=STREAM_REPLAY_TICKS_MME_FUT_DHAN,
    ticks_mme_opt_selected_zerodha=STREAM_REPLAY_TICKS_MME_OPT_SELECTED_ZERODHA,
    ticks_mme_opt_selected_dhan=STREAM_REPLAY_TICKS_MME_OPT_SELECTED_DHAN,
    ticks_mme_opt_context_dhan=STREAM_REPLAY_TICKS_MME_OPT_CONTEXT_DHAN,
    provider_runtime=STREAM_REPLAY_PROVIDER_RUNTIME,
)

LIVE_PROVIDER_STATE_HASHES: Final[ProviderStateHashSet] = ProviderStateHashSet(
    snapshot_mme_fut_zerodha=HASH_STATE_SNAPSHOT_MME_FUT_ZERODHA,
    snapshot_mme_fut_dhan=HASH_STATE_SNAPSHOT_MME_FUT_DHAN,
    snapshot_mme_fut_active=HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE,
    snapshot_mme_opt_selected_zerodha=HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
    snapshot_mme_opt_selected_dhan=HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
    snapshot_mme_opt_selected_active=HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE,
    dhan_context=HASH_STATE_DHAN_CONTEXT,
    provider_runtime=HASH_STATE_PROVIDER_RUNTIME,
)

REPLAY_PROVIDER_STATE_HASHES: Final[ProviderStateHashSet] = ProviderStateHashSet(
    snapshot_mme_fut_zerodha=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ZERODHA,
    snapshot_mme_fut_dhan=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_DHAN,
    snapshot_mme_fut_active=HASH_REPLAY_STATE_SNAPSHOT_MME_FUT_ACTIVE,
    snapshot_mme_opt_selected_zerodha=HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ZERODHA,
    snapshot_mme_opt_selected_dhan=HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_DHAN,
    snapshot_mme_opt_selected_active=HASH_REPLAY_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE,
    dhan_context=HASH_REPLAY_STATE_DHAN_CONTEXT,
    provider_runtime=HASH_REPLAY_STATE_PROVIDER_RUNTIME,
)

LIVE_PROVIDER_HEALTH: Final[ProviderHealthSet] = ProviderHealthSet(
    zerodha_auth=KEY_HEALTH_ZERODHA_AUTH,
    zerodha_marketdata=KEY_HEALTH_ZERODHA_MARKETDATA,
    zerodha_execution=KEY_HEALTH_ZERODHA_EXECUTION,
    dhan_auth=KEY_HEALTH_DHAN_AUTH,
    dhan_marketdata=KEY_HEALTH_DHAN_MARKETDATA,
    dhan_execution=KEY_HEALTH_DHAN_EXECUTION,
    provider_runtime=KEY_HEALTH_PROVIDER_RUNTIME,
)

REPLAY_PROVIDER_HEALTH: Final[ProviderHealthSet] = ProviderHealthSet(
    zerodha_auth=KEY_REPLAY_HEALTH_ZERODHA_AUTH,
    zerodha_marketdata=KEY_REPLAY_HEALTH_ZERODHA_MARKETDATA,
    zerodha_execution=KEY_REPLAY_HEALTH_ZERODHA_EXECUTION,
    dhan_auth=KEY_REPLAY_HEALTH_DHAN_AUTH,
    dhan_marketdata=KEY_REPLAY_HEALTH_DHAN_MARKETDATA,
    dhan_execution=KEY_REPLAY_HEALTH_DHAN_EXECUTION,
    provider_runtime=KEY_REPLAY_HEALTH_PROVIDER_RUNTIME,
)

LIVE_LOCKS: Final[LockSet] = LockSet(
    feeds=KEY_LOCK_FEEDS,
    strategy=KEY_LOCK_STRATEGY,
    execution=KEY_LOCK_EXECUTION,
    monitor=KEY_LOCK_MONITOR,
)

REPLAY_LOCKS: Final[LockSet] = LockSet(
    feeds=KEY_REPLAY_LOCK_FEEDS,
    strategy=KEY_REPLAY_LOCK_STRATEGY,
    execution=KEY_REPLAY_LOCK_EXECUTION,
    monitor=KEY_REPLAY_LOCK_MONITOR,
)

LIVE_GROUPS: Final[GroupSet] = GroupSet(
    features_mme_fut=GROUP_FEATURES_MME_FUT_V1,
    features_mme_opt=GROUP_FEATURES_MME_OPT_V1,
    strategy_mme=GROUP_STRATEGY_MME_V1,
    execution_mme=GROUP_EXECUTION_MME_V1,
    risk_mme=GROUP_RISK_MME_V1,
    monitor_mme=GROUP_MONITOR_MME_V1,
)

REPLAY_GROUPS: Final[GroupSet] = GroupSet(
    features_mme_fut=GROUP_REPLAY_FEATURES_MME_FUT_V1,
    features_mme_opt=GROUP_REPLAY_FEATURES_MME_OPT_V1,
    strategy_mme=GROUP_REPLAY_STRATEGY_MME_V1,
    execution_mme=GROUP_REPLAY_EXECUTION_MME_V1,
    risk_mme=GROUP_REPLAY_RISK_MME_V1,
    monitor_mme=GROUP_REPLAY_MONITOR_MME_V1,
)

# ============================================================================
# Bootstrap consumer-group specs
# ============================================================================

LIVE_GROUP_SPECS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        STREAM_TICKS_MME_FUT: (GROUP_FEATURES_MME_FUT_V1,),
        STREAM_TICKS_MME_OPT: (GROUP_FEATURES_MME_OPT_V1,),
        STREAM_FEATURES_MME: (GROUP_STRATEGY_MME_V1,),
        STREAM_DECISIONS_MME: (GROUP_EXECUTION_MME_V1,),
        STREAM_TRADES_LEDGER: (GROUP_RISK_MME_V1,),
        STREAM_SYSTEM_HEALTH: (GROUP_MONITOR_MME_V1,),
        STREAM_SYSTEM_ERRORS: (GROUP_MONITOR_MME_V1,),
    }
)

REPLAY_GROUP_SPECS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        STREAM_REPLAY_TICKS_MME_FUT: (GROUP_REPLAY_FEATURES_MME_FUT_V1,),
        STREAM_REPLAY_TICKS_MME_OPT: (GROUP_REPLAY_FEATURES_MME_OPT_V1,),
        STREAM_REPLAY_FEATURES_MME: (GROUP_REPLAY_STRATEGY_MME_V1,),
        STREAM_REPLAY_DECISIONS_MME: (GROUP_REPLAY_EXECUTION_MME_V1,),
        STREAM_REPLAY_TRADES_LEDGER: (GROUP_REPLAY_RISK_MME_V1,),
        STREAM_REPLAY_SYSTEM_HEALTH: (GROUP_REPLAY_MONITOR_MME_V1,),
        STREAM_REPLAY_SYSTEM_ERRORS: (GROUP_REPLAY_MONITOR_MME_V1,),
    }
)

# ============================================================================
# Full registries
# ============================================================================

LIVE_ALL_NAMES: Final[tuple[str, ...]] = (
    *LIVE_STREAM_NAMES,
    *LIVE_PROVIDER_STREAM_NAMES,
    *LIVE_STATE_HASH_NAMES,
    *LIVE_PROVIDER_STATE_HASH_NAMES,
    *LIVE_HEALTH_KEYS,
    *LIVE_PROVIDER_HEALTH_KEYS,
    *LIVE_LOCK_KEYS,
    *LIVE_NOTIFY_CHANNELS,
    *LIVE_GROUP_NAMES,
)

REPLAY_ALL_NAMES: Final[tuple[str, ...]] = (
    *REPLAY_STREAM_NAMES,
    *REPLAY_PROVIDER_STREAM_NAMES,
    *REPLAY_STATE_HASH_NAMES,
    *REPLAY_PROVIDER_STATE_HASH_NAMES,
    *REPLAY_HEALTH_KEYS,
    *REPLAY_PROVIDER_HEALTH_KEYS,
    *REPLAY_LOCK_KEYS,
    *REPLAY_NOTIFY_CHANNELS,
    *REPLAY_GROUP_NAMES,
)

# ============================================================================
# Access helpers
# ============================================================================


def get_streams(*, replay: bool = False) -> StreamSet:
    return REPLAY_STREAMS if replay else LIVE_STREAMS


def get_state_hashes(*, replay: bool = False) -> StateHashSet:
    return REPLAY_STATE_HASHES if replay else LIVE_STATE_HASHES


def get_provider_streams(*, replay: bool = False) -> ProviderStreamSet:
    return REPLAY_PROVIDER_STREAMS if replay else LIVE_PROVIDER_STREAMS


def get_provider_state_hashes(*, replay: bool = False) -> ProviderStateHashSet:
    return REPLAY_PROVIDER_STATE_HASHES if replay else LIVE_PROVIDER_STATE_HASHES


def get_health_keys(*, replay: bool = False) -> HealthSet:
    return REPLAY_HEALTH if replay else LIVE_HEALTH


def get_provider_health_keys(*, replay: bool = False) -> ProviderHealthSet:
    return REPLAY_PROVIDER_HEALTH if replay else LIVE_PROVIDER_HEALTH


def get_heartbeats(*, replay: bool = False) -> HealthSet:
    return get_health_keys(replay=replay)


def get_locks(*, replay: bool = False) -> LockSet:
    return REPLAY_LOCKS if replay else LIVE_LOCKS


def get_groups(*, replay: bool = False) -> GroupSet:
    return REPLAY_GROUPS if replay else LIVE_GROUPS


def get_group_specs(*, replay: bool = False) -> dict[str, tuple[str, ...]]:
    specs = REPLAY_GROUP_SPECS if replay else LIVE_GROUP_SPECS
    return {stream: tuple(groups) for stream, groups in specs.items()}


def get_service_def(service_name: str) -> ServiceDef:
    name = _require_non_empty_str(service_name, field_name="service_name")
    try:
        return SERVICE_REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(SERVICE_NAMES)
        raise NamesContractError(
            f"Unknown service {name!r}; expected one of: {known}"
        ) from exc


def all_live_names() -> tuple[str, ...]:
    return LIVE_ALL_NAMES


def all_replay_names() -> tuple[str, ...]:
    return REPLAY_ALL_NAMES


# ============================================================================
# Validation
# ============================================================================


def _validate_group_spec_entry(stream_name: str, groups: Sequence[str]) -> None:
    if not isinstance(groups, Sequence) or not groups:
        raise NamesContractError(
            f"Group spec for {stream_name!r} must be a non-empty sequence"
        )

    normalized: list[str] = []
    for idx, group in enumerate(groups):
        group_name = _require_non_empty_str(group, field_name=f"group[{idx}]")
        normalized.append(group_name)

    _assert_no_duplicates(normalized, label=f"group spec for {stream_name!r}")


def validate_names_contract() -> None:
    _assert_no_duplicates(LIVE_STREAM_NAMES, label="LIVE_STREAM_NAMES")
    _assert_no_duplicates(LIVE_PROVIDER_STREAM_NAMES, label="LIVE_PROVIDER_STREAM_NAMES")
    _assert_no_duplicates(REPLAY_STREAM_NAMES, label="REPLAY_STREAM_NAMES")
    _assert_no_duplicates(REPLAY_PROVIDER_STREAM_NAMES, label="REPLAY_PROVIDER_STREAM_NAMES")
    _assert_no_duplicates(LIVE_STATE_HASH_NAMES, label="LIVE_STATE_HASH_NAMES")
    _assert_no_duplicates(
        LIVE_PROVIDER_STATE_HASH_NAMES,
        label="LIVE_PROVIDER_STATE_HASH_NAMES",
    )
    _assert_no_duplicates(REPLAY_STATE_HASH_NAMES, label="REPLAY_STATE_HASH_NAMES")
    _assert_no_duplicates(
        REPLAY_PROVIDER_STATE_HASH_NAMES,
        label="REPLAY_PROVIDER_STATE_HASH_NAMES",
    )
    _assert_no_duplicates(LIVE_HEALTH_KEYS, label="LIVE_HEALTH_KEYS")
    _assert_no_duplicates(
        LIVE_PROVIDER_HEALTH_KEYS,
        label="LIVE_PROVIDER_HEALTH_KEYS",
    )
    _assert_no_duplicates(REPLAY_HEALTH_KEYS, label="REPLAY_HEALTH_KEYS")
    _assert_no_duplicates(
        REPLAY_PROVIDER_HEALTH_KEYS,
        label="REPLAY_PROVIDER_HEALTH_KEYS",
    )
    _assert_no_duplicates(LIVE_LOCK_KEYS, label="LIVE_LOCK_KEYS")
    _assert_no_duplicates(REPLAY_LOCK_KEYS, label="REPLAY_LOCK_KEYS")
    _assert_no_duplicates(LIVE_NOTIFY_CHANNELS, label="LIVE_NOTIFY_CHANNELS")
    _assert_no_duplicates(REPLAY_NOTIFY_CHANNELS, label="REPLAY_NOTIFY_CHANNELS")
    _assert_no_duplicates(LIVE_GROUP_NAMES, label="LIVE_GROUP_NAMES")
    _assert_no_duplicates(REPLAY_GROUP_NAMES, label="REPLAY_GROUP_NAMES")
    _assert_no_duplicates(LIVE_ALL_NAMES, label="LIVE_ALL_NAMES")
    _assert_no_duplicates(REPLAY_ALL_NAMES, label="REPLAY_ALL_NAMES")
    _assert_no_duplicates(SERVICE_NAMES, label="SERVICE_NAMES")
    _assert_no_duplicates(EVENT_TYPES, label="EVENT_TYPES")
    _assert_no_duplicates(ACK_TYPES, label="ACK_TYPES")
    _assert_no_duplicates(COMMAND_TYPES, label="COMMAND_TYPES")
    _assert_no_duplicates(ACTION_TYPES, label="ACTION_TYPES")
    _assert_no_duplicates(POSITION_SIDE_TYPES, label="POSITION_SIDE_TYPES")
    _assert_no_duplicates(SIDE_TYPES, label="SIDE_TYPES")
    _assert_no_duplicates(STRATEGY_MODES, label="STRATEGY_MODES")
    _assert_no_duplicates(ENTRY_MODES, label="ENTRY_MODES")
    _assert_no_duplicates(POSITION_EFFECTS, label="POSITION_EFFECTS")
    _assert_no_duplicates(EXECUTION_MODES, label="EXECUTION_MODES")
    _assert_no_duplicates(ERROR_SEVERITIES, label="ERROR_SEVERITIES")
    _assert_no_duplicates(HEALTH_STATUSES, label="HEALTH_STATUSES")
    _assert_no_duplicates(SYSTEM_STATES, label="SYSTEM_STATES")
    _assert_no_duplicates(CONTROL_MODES, label="CONTROL_MODES")
    _assert_no_duplicates(INSTRUMENT_KEYS, label="INSTRUMENT_KEYS")
    _assert_no_duplicates(STRATEGY_FAMILY_IDS, label="STRATEGY_FAMILY_IDS")
    _assert_no_duplicates(DOCTRINE_IDS, label="DOCTRINE_IDS")
    _assert_no_duplicates(BRANCH_IDS, label="BRANCH_IDS")
    _assert_no_duplicates(STRATEGY_RUNTIME_MODES, label="STRATEGY_RUNTIME_MODES")
    _assert_no_duplicates(FAMILY_RUNTIME_MODES, label="FAMILY_RUNTIME_MODES")
    _assert_no_duplicates(PROVIDER_IDS, label="PROVIDER_IDS")
    _assert_no_duplicates(PROVIDER_ROLES, label="PROVIDER_ROLES")
    _assert_no_duplicates(PROVIDER_STATUSES, label="PROVIDER_STATUSES")
    _assert_no_duplicates(PROVIDER_FAILOVER_MODES, label="PROVIDER_FAILOVER_MODES")
    _assert_no_duplicates(PROVIDER_OVERRIDE_MODES, label="PROVIDER_OVERRIDE_MODES")
    _assert_no_duplicates(
        PROVIDER_TRANSITION_REASONS,
        label="PROVIDER_TRANSITION_REASONS",
    )

    for live_name in LIVE_ALL_NAMES:
        ensure_live_name(live_name)

    for replay_key in REPLAY_ALL_NAMES:
        ensure_replay_name(replay_key)

    for stream_name, owner in STREAM_OWNERS.items():
        ensure_live_name(stream_name)
        _require_non_empty_str(owner, field_name=f"STREAM_OWNERS[{stream_name!r}]")
        if owner not in SERVICE_NAMES:
            raise NamesContractError(
                f"Unknown stream owner {owner!r} for stream {stream_name!r}"
            )

    for stream_name in (*LIVE_STREAM_NAMES, *LIVE_PROVIDER_STREAM_NAMES):
        if stream_name not in STREAM_OWNERS:
            raise NamesContractError(
                f"Missing stream owner registry entry for live stream {stream_name!r}"
            )

    for stream_name, publishers in STREAM_ADDITIVE_PUBLISHERS.items():
        ensure_live_name(stream_name)
        if stream_name not in STREAM_OWNERS:
            raise NamesContractError(
                f"Additive-publisher registry references unknown primary-owned stream {stream_name!r}"
            )
        if not publishers:
            raise NamesContractError(
                f"Additive-publisher registry for {stream_name!r} must be non-empty"
            )
        _assert_no_duplicates(publishers, label=f"STREAM_ADDITIVE_PUBLISHERS[{stream_name!r}]")
        for publisher in publishers:
            _require_non_empty_str(
                publisher,
                field_name=f"STREAM_ADDITIVE_PUBLISHERS[{stream_name!r}]",
            )
            if publisher not in SERVICE_NAMES:
                raise NamesContractError(
                    f"Unknown additive publisher {publisher!r} for stream {stream_name!r}"
                )

    for hash_name, owner in STATE_HASH_OWNERS.items():
        ensure_live_name(hash_name)
        _require_non_empty_str(owner, field_name=f"STATE_HASH_OWNERS[{hash_name!r}]")
        if owner not in SERVICE_NAMES:
            raise NamesContractError(
                f"Unknown state-hash owner {owner!r} for hash {hash_name!r}"
            )

    for hash_name in (*LIVE_STATE_HASH_NAMES, *LIVE_PROVIDER_STATE_HASH_NAMES):
        if hash_name not in STATE_HASH_OWNERS:
            raise NamesContractError(
                f"Missing state-hash owner registry entry for live hash {hash_name!r}"
            )

    for health_key, owner in HEALTH_OWNERS.items():
        ensure_live_name(health_key)
        _require_non_empty_str(owner, field_name=f"HEALTH_OWNERS[{health_key!r}]")
        if owner not in SERVICE_NAMES:
            raise NamesContractError(
                f"Unknown health owner {owner!r} for key {health_key!r}"
            )

    for health_key in (*LIVE_HEALTH_KEYS, *LIVE_PROVIDER_HEALTH_KEYS):
        if health_key not in HEALTH_OWNERS:
            raise NamesContractError(
                f"Missing health owner registry entry for live key {health_key!r}"
            )

    for lock_key, owner in LOCK_OWNERS.items():
        ensure_live_name(lock_key)
        _require_non_empty_str(owner, field_name=f"LOCK_OWNERS[{lock_key!r}]")
        if owner not in SERVICE_NAMES:
            raise NamesContractError(
                f"Unknown lock owner {owner!r} for key {lock_key!r}"
            )

    for channel_name, owner in CHANNEL_OWNERS.items():
        ensure_live_name(channel_name)
        _require_non_empty_str(owner, field_name=f"CHANNEL_OWNERS[{channel_name!r}]")
        if owner not in SERVICE_NAMES:
            raise NamesContractError(
                f"Unknown channel owner {owner!r} for channel {channel_name!r}"
            )

    for service_name, service_def in SERVICE_REGISTRY.items():
        if service_name != service_def.name:
            raise NamesContractError(
                f"SERVICE_REGISTRY key {service_name!r} does not match ServiceDef.name "
                f"{service_def.name!r}"
            )
        if service_def.owns_heartbeat is not None:
            ensure_live_name(service_def.owns_heartbeat)
            if service_def.owns_heartbeat not in LIVE_HEALTH_KEYS:
                raise NamesContractError(
                    f"Service {service_name!r} owns unknown heartbeat/health key "
                    f"{service_def.owns_heartbeat!r}"
                )
        if service_def.owns_lock is not None:
            ensure_live_name(service_def.owns_lock)
            if service_def.owns_lock not in LIVE_LOCK_KEYS:
                raise NamesContractError(
                    f"Service {service_name!r} owns unknown lock key "
                    f"{service_def.owns_lock!r}"
                )

    for stream_name, groups in LIVE_GROUP_SPECS.items():
        ensure_live_name(stream_name)
        _validate_group_spec_entry(stream_name, groups)
        if stream_name not in (*LIVE_STREAM_NAMES, *LIVE_PROVIDER_STREAM_NAMES):
            raise NamesContractError(
                f"Live group spec references unknown stream {stream_name!r}"
            )
        for group_name in groups:
            if group_name not in LIVE_GROUP_NAMES:
                raise NamesContractError(
                    f"Live group spec for {stream_name!r} references unknown group {group_name!r}"
                )

    for stream_name, groups in REPLAY_GROUP_SPECS.items():
        ensure_replay_name(stream_name)
        _validate_group_spec_entry(stream_name, groups)
        if stream_name not in (*REPLAY_STREAM_NAMES, *REPLAY_PROVIDER_STREAM_NAMES):
            raise NamesContractError(
                f"Replay group spec references unknown stream {stream_name!r}"
            )
        for group_name in groups:
            if group_name not in REPLAY_GROUP_NAMES:
                raise NamesContractError(
                    f"Replay group spec for {stream_name!r} references unknown group {group_name!r}"
                )

    alias_map: dict[str, str] = {
        "STREAM_CMD": STREAM_CMD,
        "STREAM_DECISIONS": STREAM_DECISIONS,
        "STREAM_ORDERS": STREAM_ORDERS,
        "STREAM_FEATURES": STREAM_FEATURES,
        "STATE_INSTRUMENTS": STATE_INSTRUMENTS,
        "STATE_SNAPSHOT_FUT": STATE_SNAPSHOT_FUT,
        "STATE_SNAPSHOT_OPT_SELECTED": STATE_SNAPSHOT_OPT_SELECTED,
        "STATE_FEATURES": STATE_FEATURES,
        "STATE_BASELINES": STATE_BASELINES,
        "STATE_OPTION_CONFIRM": STATE_OPTION_CONFIRM,
        "STATE_RISK": STATE_RISK,
        "STATE_POSITION": STATE_POSITION,
        "STATE_EXECUTION": STATE_EXECUTION,
        "STATE_RUNTIME": STATE_RUNTIME,
        "STATE_MODE": STATE_MODE,
        "STATE_LOGIN": STATE_LOGIN,
        "STATE_REPORT": STATE_REPORT,
        "STATE_PARAMS": STATE_PARAMS,
        "STATE_PARAMS_META": STATE_PARAMS_META,
        "STATE_SNAPSHOT_FUT_ZERODHA": STATE_SNAPSHOT_FUT_ZERODHA,
        "STATE_SNAPSHOT_FUT_DHAN": STATE_SNAPSHOT_FUT_DHAN,
        "STATE_SNAPSHOT_FUT_ACTIVE": STATE_SNAPSHOT_FUT_ACTIVE,
        "STATE_SNAPSHOT_OPT_SELECTED_ZERODHA": STATE_SNAPSHOT_OPT_SELECTED_ZERODHA,
        "STATE_SNAPSHOT_OPT_SELECTED_DHAN": STATE_SNAPSHOT_OPT_SELECTED_DHAN,
        "STATE_SNAPSHOT_OPT_SELECTED_ACTIVE": STATE_SNAPSHOT_OPT_SELECTED_ACTIVE,
        "STATE_DHAN_CONTEXT": STATE_DHAN_CONTEXT,
        "STATE_PROVIDER_RUNTIME": STATE_PROVIDER_RUNTIME,
        "HB_LOGIN": HB_LOGIN,
        "HB_INSTRUMENTS": HB_INSTRUMENTS,
        "HB_FEEDS": HB_FEEDS,
        "HB_FEATURES": HB_FEATURES,
        "HB_STRATEGY": HB_STRATEGY,
        "HB_RISK": HB_RISK,
        "HB_EXECUTION": HB_EXECUTION,
        "HB_MONITOR": HB_MONITOR,
        "HB_REPORT": HB_REPORT,
        "HB_ZERODHA_AUTH": HB_ZERODHA_AUTH,
        "HB_ZERODHA_MARKETDATA": HB_ZERODHA_MARKETDATA,
        "HB_ZERODHA_EXECUTION": HB_ZERODHA_EXECUTION,
        "HB_DHAN_AUTH": HB_DHAN_AUTH,
        "HB_DHAN_MARKETDATA": HB_DHAN_MARKETDATA,
        "HB_DHAN_EXECUTION": HB_DHAN_EXECUTION,
        "HB_PROVIDER_RUNTIME": HB_PROVIDER_RUNTIME,
        "GROUP_EXEC": GROUP_EXEC,
        "GROUP_RISK": GROUP_RISK,
        "GROUP_MONITOR": GROUP_MONITOR,
        "GROUP_STRATEGY": GROUP_STRATEGY,
        "GROUP_FEATURES_FUT": GROUP_FEATURES_FUT,
        "GROUP_FEATURES_OPT": GROUP_FEATURES_OPT,
        "LOCK_FEEDS": LOCK_FEEDS,
        "LOCK_STRATEGY": LOCK_STRATEGY,
        "LOCK_EXECUTION": LOCK_EXECUTION,
        "LOCK_MONITOR": LOCK_MONITOR,
        "HEALTH_STATUS_OK": HEALTH_STATUS_OK,
        "HEALTH_STATUS_WARN": HEALTH_STATUS_WARN,
        "HEALTH_STATUS_ERROR": HEALTH_STATUS_ERROR,
        "HEALTH_OK": HEALTH_OK,
        "HEALTH_WARN": HEALTH_WARN,
        "HEALTH_ERROR": HEALTH_ERROR,
        "EXECUTION_MODE_NORMAL": EXECUTION_MODE_NORMAL,
        "EXECUTION_MODE_EXIT_ONLY": EXECUTION_MODE_EXIT_ONLY,
        "EXECUTION_MODE_DEGRADED": EXECUTION_MODE_DEGRADED,
        "EXECUTION_MODE_FATAL": EXECUTION_MODE_FATAL,
        "EXEC_MODE_NORMAL": EXEC_MODE_NORMAL,
        "EXEC_MODE_EXIT_ONLY": EXEC_MODE_EXIT_ONLY,
        "EXEC_MODE_DEGRADED": EXEC_MODE_DEGRADED,
        "EXEC_MODE_FATAL": EXEC_MODE_FATAL,
        "ACTION_ENTER_CALL": ACTION_ENTER_CALL,
        "ACTION_ENTER_PUT": ACTION_ENTER_PUT,
        "ACTION_EXIT": ACTION_EXIT,
        "ACTION_HOLD": ACTION_HOLD,
        "POSITION_SIDE_FLAT": POSITION_SIDE_FLAT,
        "POSITION_SIDE_LONG_CALL": POSITION_SIDE_LONG_CALL,
        "POSITION_SIDE_LONG_PUT": POSITION_SIDE_LONG_PUT,
        "ENTRY_MODE_UNKNOWN": ENTRY_MODE_UNKNOWN,
        "ENTRY_MODE_ATM": ENTRY_MODE_ATM,
        "ENTRY_MODE_ATM1": ENTRY_MODE_ATM1,
        "ENTRY_MODE_DIRECT": ENTRY_MODE_DIRECT,
        "ENTRY_MODE_FALLBACK": ENTRY_MODE_FALLBACK,
        "ENTRY_MODE_ATM1_FALLBACK": ENTRY_MODE_ATM1_FALLBACK,
        "ACK_RECEIVED": ACK_RECEIVED,
        "ACK_REJECTED": ACK_REJECTED,
        "ACK_SENT_TO_BROKER": ACK_SENT_TO_BROKER,
        "ACK_FILLED": ACK_FILLED,
        "ACK_FAILED": ACK_FAILED,
        "ACK_EXIT_SENT": ACK_EXIT_SENT,
        "ACK_EXIT_FILLED": ACK_EXIT_FILLED,
    }
    for alias_name, resolved in alias_map.items():
        _require_non_empty_str(alias_name, field_name="alias_name")
        _require_non_empty_str(resolved, field_name=f"{alias_name}.value")


validate_names_contract()

__all__ = tuple(
    name
    for name in globals()
    if name.isupper()
    or name
    in {
        "NamesContractError",
        "ServiceDef",
        "StreamSet",
        "StateHashSet",
        "HealthSet",
        "LockSet",
        "GroupSet",
        "ProviderStreamSet",
        "ProviderStateHashSet",
        "ProviderHealthSet",
        "ensure_live_name",
        "ensure_replay_name",
        "replay_name",
        "is_replay_name",
        "get_streams",
        "get_state_hashes",
        "get_provider_streams",
        "get_provider_state_hashes",
        "get_health_keys",
        "get_provider_health_keys",
        "get_heartbeats",
        "get_locks",
        "get_groups",
        "get_group_specs",
        "get_service_def",
        "all_live_names",
        "all_replay_names",
        "validate_names_contract",
    }
)