from __future__ import annotations

"""
app/mme_scalpx/services/strategy.py

ScalpX MME - provider-aware 5-family decision engine.

Purpose
-------
This module OWNS:
- deterministic family arbitration across MIST / MISB / MISC / MISR / MISO
- strategy-side state machine for arming / confirmation / entry / open-position / exit / cooldown
- provider-aware decision construction from frozen feature payloads
- risk/execution/position truth consumption for entry gating and open-position management
- canonical decision publication to STREAM_DECISIONS_MME
- strategy heartbeat publication
- strategy singleton lock ownership
- runtime entrypoint ``run(context)``

This module DOES NOT own:
- Redis names / transport helpers
- feature math or provider-routing policy
- broker placement / broker reconciliation
- risk truth mutation
- execution truth mutation
- raw feed parsing / normalization
- composition-root wiring

Frozen runtime rules
--------------------
- strategy.py is the only live family decision publisher and emits at most one live decision at a time
- execution remains sole position truth
- risk may veto entries but never exits
- provider-runtime truth is consumed from the feature payload; strategy does not invent provider routing
- classic MIS families are futures-led / option-confirmed and degrade-safe when Dhan enhancement is unavailable
- MISO is option-led and must not silently trade unless its Dhan-mandatory signal path is present
- no mid-position provider migration logic is implemented here
- replay-safe and restart-safe behavior takes priority over aggressive optimization

Important implementation note
-----------------------------
The frozen feature service publishes a fully serialized provider-aware payload into
HASH_STATE_FEATURES_MME_FUT field ``payload_json``. This strategy service rebuilds
lightweight read models from that payload and consumes:
- payload["provider_surface"]
- payload["family_surfaces"]
- payload["family_frames"]
- payload["shared_features"]

MISO execution bridge note
--------------------------
The migration plan requires an explicit MISO execution-feasibility bridge before
order send. The current frozen live payload does not yet expose a hard bridge-ok
surface proving Dhan-selected strike -> execution-provider mapping. Therefore
this module keeps MISO fully evaluated, but blocks live MISO entries unless the
signal and execution providers are already aligned or the payload explicitly
provides ``execution_bridge_ok`` in the MISO surface metadata. This preserves the
provider law without inventing unsafe execution compatibility. 
"""

import contextlib
import json
import logging
import time
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Final, Iterable, Mapping, Sequence
from uuid import uuid4
from zoneinfo import ZoneInfo

import yaml

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX
from app.mme_scalpx.core.models import StopPlan, StrategyDecision, TargetPlan
from app.mme_scalpx.core.settings import AppSettings, get_settings

LOGGER = logging.getLogger("app.mme_scalpx.services.strategy")


# =============================================================================
# Required surface validation
# =============================================================================

_REQUIRED_NAME_EXPORTS: Final[tuple[str, ...]] = (
    "SERVICE_STRATEGY",
    "STREAM_DECISIONS_MME",
    "STREAM_SYSTEM_HEALTH",
    "STREAM_SYSTEM_ERRORS",
    "HASH_STATE_FEATURES_MME_FUT",
    "HASH_STATE_RISK",
    "HASH_STATE_EXECUTION",
    "HASH_STATE_POSITION_MME",
    "KEY_HEALTH_STRATEGY",
    "KEY_LOCK_STRATEGY",
    "ACTION_ENTER_CALL",
    "ACTION_ENTER_PUT",
    "ACTION_EXIT",
    "ACTION_HOLD",
    "SIDE_CALL",
    "SIDE_PUT",
    "POSITION_EFFECT_OPEN",
    "POSITION_EFFECT_CLOSE",
    "POSITION_EFFECT_REDUCE",
    "POSITION_EFFECT_FLATTEN",
    "POSITION_EFFECT_NONE",
    "ENTRY_MODE_UNKNOWN",
    "ENTRY_MODE_ATM",
    "ENTRY_MODE_ATM1",
    "ENTRY_MODE_DIRECT",
    "ENTRY_MODE_FALLBACK",
    "POSITION_SIDE_FLAT",
    "POSITION_SIDE_LONG_CALL",
    "POSITION_SIDE_LONG_PUT",
    "STRATEGY_CALL",
    "STRATEGY_PUT",
    "STRATEGY_AUTO",
    "STATE_IDLE",
    "STATE_SCANNING",
    "STATE_SIGNAL_READY",
    "STATE_CONFIRMING",
    "STATE_ENTRY_PENDING",
    "STATE_POSITION_OPEN",
    "STATE_EXIT_PENDING",
    "STATE_COOLDOWN",
    "STATE_WAIT",
    "STATE_DISABLED",
    "HEALTH_STATUS_OK",
    "HEALTH_STATUS_WARN",
    "HEALTH_STATUS_ERROR",
    "STRATEGY_FAMILY_MIST",
    "STRATEGY_FAMILY_MISB",
    "STRATEGY_FAMILY_MISC",
    "STRATEGY_FAMILY_MISR",
    "STRATEGY_FAMILY_MISO",
    "DOCTRINE_MIST",
    "DOCTRINE_MISB",
    "DOCTRINE_MISC",
    "DOCTRINE_MISR",
    "DOCTRINE_MISO",
    "BRANCH_CALL",
    "BRANCH_PUT",
    "FAMILY_RUNTIME_MODE_OBSERVE_ONLY",
    "FAMILY_RUNTIME_MODE_LEGACY_LIVE_FAMILY_SHADOW",
    "FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW",
    "FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY",
    "STRATEGY_RUNTIME_MODE_NORMAL",
    "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED",
    "STRATEGY_RUNTIME_MODE_BASE_5DEPTH",
    "STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED",
    "STRATEGY_RUNTIME_MODE_DISABLED",
    "PROVIDER_ZERODHA",
    "PROVIDER_DHAN",
    "PROVIDER_STATUS_HEALTHY",
    "PROVIDER_STATUS_DEGRADED",
    "EXECUTION_MODE_NORMAL",
    "EXECUTION_MODE_EXIT_ONLY",
    "EXECUTION_MODE_DEGRADED",
    "EXECUTION_MODE_FATAL",
)


def _validate_name_surface_or_die() -> None:
    missing = [name for name in _REQUIRED_NAME_EXPORTS if not hasattr(N, name)]
    if missing:
        raise RuntimeError(
            "strategy.py missing required names.py exports: "
            + ", ".join(sorted(missing))
        )


# =============================================================================
# Locked constants
# =============================================================================

EPSILON: Final[float] = 1e-8
DEFAULT_TARGET_PCT: Final[float] = 0.12
DEFAULT_STOP_PCT: Final[float] = 0.07
DEFAULT_MIN_TARGET_POINTS: Final[float] = 5.0
DEFAULT_MAX_TARGET_POINTS: Final[float] = 10.0
DEFAULT_MIN_STOP_POINTS: Final[float] = 3.0
DEFAULT_MAX_STOP_POINTS: Final[float] = 7.0
MISO_TARGET_POINTS: Final[float] = 5.0
MISO_STOP_POINTS: Final[float] = 4.0

DEFAULT_CONFIRMATION_SNAPSHOTS: Final[int] = 2
DEFAULT_CONFIRMATION_TIMEOUT_MS: Final[int] = 2_000
DEFAULT_PENDING_WAIT_MS: Final[int] = 1_000
DEFAULT_TARGET_COOLDOWN_SEC: Final[float] = 8.0
DEFAULT_STOP_COOLDOWN_SEC: Final[float] = 12.0
DEFAULT_WAIT_COOLDOWN_SEC: Final[float] = 2.0
DEFAULT_TIME_STALL_SEC: Final[float] = 12.0
DEFAULT_PROFIT_STALL_SEC: Final[float] = 3.0
DEFAULT_PROFIT_PROTECT_TRIGGER: Final[float] = 0.70
DEFAULT_PROFIT_RETRACE: Final[float] = 0.30
DEFAULT_MOMENTUM_FADE_RATIO: Final[float] = 0.85
DEFAULT_HARD_TARGET_BUFFER_TICKS: Final[float] = 0.0
DEFAULT_HARD_STOP_BUFFER_TICKS: Final[float] = 0.0
DEFAULT_NO_FEATURE_WARN_AFTER_LOOPS: Final[int] = 20
DEFAULT_HOLD_PUBLISH_INTERVAL_MS: Final[int] = 2_000
DEFAULT_PROOF_WINDOW_SEC: Final[float] = 3.0
DEFAULT_STAGE2_PROOF_WINDOW_SEC: Final[float] = 5.0
DEFAULT_MAX_HOLD_LOWVOL_SEC: Final[float] = 12.0
DEFAULT_MAX_HOLD_NORMAL_SEC: Final[float] = 10.0
DEFAULT_MAX_HOLD_FAST_SEC: Final[float] = 10.0
DEFAULT_TIME_STALL_LOWVOL_SEC: Final[float] = 12.0
DEFAULT_TIME_STALL_NORMAL_SEC: Final[float] = 10.0
DEFAULT_TIME_STALL_FAST_SEC: Final[float] = 7.0
DEFAULT_PROOF_MIN_RESPONSE: Final[float] = 0.14
DEFAULT_DIVERGENCE_RESPONSE_FLOOR: Final[float] = 0.10
DEFAULT_ABSORPTION_RESPONSE_FLOOR: Final[float] = 0.10
DEFAULT_ABSORPTION_OFI_BULL: Final[float] = 0.62
DEFAULT_ABSORPTION_OFI_BEAR: Final[float] = 0.38
DEFAULT_MISO_DISASTER_STOP_POINTS: Final[float] = 6.0
DEFAULT_MISO_TAPE_SPEED_FAIL: Final[float] = 0.90
DEFAULT_MISO_IMBALANCE_FAIL_BULL: Final[float] = 0.52
DEFAULT_MISO_IMBALANCE_FAIL_BEAR: Final[float] = 0.48

DEFAULT_CLASSIC_RESPONSE_MIN_NORMAL: Final[float] = 0.17
DEFAULT_CLASSIC_RESPONSE_MIN_DEGRADED: Final[float] = 0.19
DEFAULT_CLASSIC_SPREAD_RATIO_MAX: Final[float] = 1.70
DEFAULT_CLASSIC_SPREAD_RATIO_MAX_DEGRADED: Final[float] = 1.55
DEFAULT_CLASSIC_DEPTH_MIN: Final[int] = 78
DEFAULT_CLASSIC_DEPTH_MIN_DEGRADED: Final[int] = 88
DEFAULT_CLASSIC_IMPACT_MAX: Final[float] = 0.27
DEFAULT_CLASSIC_IMPACT_MAX_DEGRADED: Final[float] = 0.22
DEFAULT_CLASSIC_VELOCITY_RATIO_MIN: Final[float] = 1.10
DEFAULT_CLASSIC_OFI_BULL_MIN: Final[float] = 0.55
DEFAULT_CLASSIC_OFI_BEAR_MAX: Final[float] = 0.45
DEFAULT_CLASSIC_SCORE_MIN: Final[float] = 1.0

DEFAULT_MISO_TAPE_SPEED_MIN: Final[float] = 1.25
DEFAULT_MISO_IMBALANCE_MIN_BULL: Final[float] = 0.55
DEFAULT_MISO_IMBALANCE_MAX_BEAR: Final[float] = 0.45
DEFAULT_MISO_SCORE_MIN: Final[float] = 1.20
DEFAULT_MISO_PREMIUM_FLOOR: Final[float] = 25.0
DEFAULT_MISC_RETEST_MONITOR_SEC: Final[float] = 11.0
DEFAULT_MISR_ARMED_MONITOR_SEC: Final[float] = 6.0
DEFAULT_SESSION_END_FLATTEN_HHMM: Final[str] = "1518"
DEFAULT_MISO_LARGE_COUNTER_QTY: Final[float] = 0.0
DEFAULT_EARLY_STALL_SEC: Final[float] = 6.0


DEFAULT_HEALTH_STREAM_MAXLEN: Final[int] = 10_000
DEFAULT_ERROR_STREAM_MAXLEN: Final[int] = 10_000

LIVE_FAMILY_MODES: Final[tuple[str, ...]] = (
    N.FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW,
    N.FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY,
)

CLASSIC_FAMILIES: Final[tuple[str, ...]] = (
    N.STRATEGY_FAMILY_MIST,
    N.STRATEGY_FAMILY_MISB,
    N.STRATEGY_FAMILY_MISC,
    N.STRATEGY_FAMILY_MISR,
)

FAMILY_ORDER: Final[tuple[str, ...]] = (
    N.STRATEGY_FAMILY_MIST,
    N.STRATEGY_FAMILY_MISB,
    N.STRATEGY_FAMILY_MISC,
    N.STRATEGY_FAMILY_MISR,
    N.STRATEGY_FAMILY_MISO,
)

DOCTRINE_BY_FAMILY: Final[dict[str, str]] = {
    N.STRATEGY_FAMILY_MIST: N.DOCTRINE_MIST,
    N.STRATEGY_FAMILY_MISB: N.DOCTRINE_MISB,
    N.STRATEGY_FAMILY_MISC: N.DOCTRINE_MISC,
    N.STRATEGY_FAMILY_MISR: N.DOCTRINE_MISR,
    N.STRATEGY_FAMILY_MISO: N.DOCTRINE_MISO,
}

BRANCH_TO_SIDE: Final[dict[str, str]] = {
    N.BRANCH_CALL: N.SIDE_CALL,
    N.BRANCH_PUT: N.SIDE_PUT,
}

BRANCH_TO_POSITION_SIDE: Final[dict[str, str]] = {
    N.BRANCH_CALL: N.POSITION_SIDE_LONG_CALL,
    N.BRANCH_PUT: N.POSITION_SIDE_LONG_PUT,
}

BRANCH_TO_STRATEGY_MODE: Final[dict[str, str]] = {
    N.BRANCH_CALL: N.STRATEGY_CALL,
    N.BRANCH_PUT: N.STRATEGY_PUT,
}

DOCTRINE_PARAM_PATHS: Final[dict[tuple[str, str], str]] = {
    (N.STRATEGY_FAMILY_MIST, N.BRANCH_CALL): "etc/strategy_family/frozen/mist_call.yaml",
    (N.STRATEGY_FAMILY_MIST, N.BRANCH_PUT): "etc/strategy_family/frozen/mist_put.yaml",
    (N.STRATEGY_FAMILY_MISB, N.BRANCH_CALL): "etc/strategy_family/frozen/misb_call.yaml",
    (N.STRATEGY_FAMILY_MISB, N.BRANCH_PUT): "etc/strategy_family/frozen/misb_put.yaml",
    (N.STRATEGY_FAMILY_MISC, N.BRANCH_CALL): "etc/strategy_family/frozen/misc_call.yaml",
    (N.STRATEGY_FAMILY_MISC, N.BRANCH_PUT): "etc/strategy_family/frozen/misc_put.yaml",
    (N.STRATEGY_FAMILY_MISR, N.BRANCH_CALL): "etc/strategy_family/frozen/misr_call.yaml",
    (N.STRATEGY_FAMILY_MISR, N.BRANCH_PUT): "etc/strategy_family/frozen/misr_put.yaml",
    (N.STRATEGY_FAMILY_MISO, N.BRANCH_CALL): "etc/strategy_family/frozen/miso_call.yaml",
    (N.STRATEGY_FAMILY_MISO, N.BRANCH_PUT): "etc/strategy_family/frozen/miso_put.yaml",
}

ALLOWED_REENTRY_EXIT_REASONS: Final[dict[str, tuple[str, ...]]] = {
    N.STRATEGY_FAMILY_MIST: ("hard_target", "profit_stall", "time_stall"),
    N.STRATEGY_FAMILY_MISB: ("hard_target", "profit_stall", "time_stall", "max_hold_exit"),
    N.STRATEGY_FAMILY_MISC: ("hard_target", "profit_stall", "time_stall"),
    N.STRATEGY_FAMILY_MISR: (),
    N.STRATEGY_FAMILY_MISO: (),
}

FORBIDDEN_REENTRY_EXIT_REASONS: Final[dict[str, tuple[str, ...]]] = {
    N.STRATEGY_FAMILY_MIST: ("hard_stop", "proof_failure_exit", "feed_failure_exit", "futures_option_divergence_exit", "absorption_under_response_exit", "liquidity_exit", "momentum_fade_exit"),
    N.STRATEGY_FAMILY_MISB: ("hard_stop", "proof_failure_exit", "breakout_failure_exit", "feed_failure_exit", "futures_option_divergence_exit", "absorption_under_response_exit", "liquidity_exit", "momentum_fade_exit"),
    N.STRATEGY_FAMILY_MISC: ("hard_stop", "proof_failure_exit", "breakout_failure_exit", "feed_failure_exit", "futures_option_divergence_exit", "absorption_under_response_exit", "liquidity_exit", "momentum_fade_exit"),
    N.STRATEGY_FAMILY_MISR: ("hard_stop", "proof_failure_exit", "breakout_failure_exit", "feed_failure_exit", "futures_option_divergence_exit", "absorption_under_response_exit", "liquidity_exit", "momentum_fade_exit"),
    N.STRATEGY_FAMILY_MISO: ("hard_stop", "disaster_stop_exit", "microstructure_failure_exit", "feed_failure_exit", "reconciliation_exit"),
}

DEFAULT_REENTRY_CAPS: Final[dict[str, dict[str, int]]] = {
    N.STRATEGY_FAMILY_MIST: {"LOWVOL": 0, "NORMAL": 1, "FAST": 1},
    N.STRATEGY_FAMILY_MISB: {"LOWVOL": 0, "NORMAL": 1, "FAST": 1},
    N.STRATEGY_FAMILY_MISC: {"LOWVOL": 0, "NORMAL": 1, "FAST": 1},
    N.STRATEGY_FAMILY_MISR: {"LOWVOL": 0, "NORMAL": 0, "FAST": 0},
    N.STRATEGY_FAMILY_MISO: {"LOWVOL": 0, "NORMAL": 0, "FAST": 0},
}


# =============================================================================
# Small helpers
# =============================================================================


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except Exception:
        return default
    if out != out or out in (float("inf"), float("-inf")):
        return default
    return out


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        raw = value.strip().lower()
        if raw in {"1", "true", "yes", "y", "ok", "on"}:
            return True
        if raw in {"0", "false", "no", "n", "off"}:
            return False
        return default
    return bool(value)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    out = str(value).strip()
    return out if out else default


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False, default=str)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    if abs(denominator) <= EPSILON:
        return default
    return numerator / denominator


def _nested_get(mapping: Any, *keys: str, default: Any = None) -> Any:
    cur = mapping
    for key in keys:
        if isinstance(cur, Mapping):
            if key not in cur:
                return default
            cur = cur[key]
        else:
            return default
    return cur


def _normalize_entry_mode(value: str | None) -> str:
    valid = {
        N.ENTRY_MODE_UNKNOWN,
        N.ENTRY_MODE_ATM,
        N.ENTRY_MODE_ATM1,
        N.ENTRY_MODE_DIRECT,
        N.ENTRY_MODE_FALLBACK,
    }
    text = _safe_str(value, N.ENTRY_MODE_UNKNOWN)
    return text if text in valid else N.ENTRY_MODE_UNKNOWN


def _cooldown_ns(seconds: float) -> int:
    return int(max(seconds, 0.0) * 1_000_000_000)


def _state_to_wire(state: "InternalState") -> str:
    mapping = {
        InternalState.SCANNING: N.STATE_SCANNING,
        InternalState.ARMED: N.STATE_SIGNAL_READY,
        InternalState.RETEST_MONITOR: N.STATE_SIGNAL_READY,
        InternalState.CONFIRMING: N.STATE_CONFIRMING,
        InternalState.ENTRY_PENDING: N.STATE_ENTRY_PENDING,
        InternalState.POSITION_OPEN: N.STATE_POSITION_OPEN,
        InternalState.EXIT_PENDING: N.STATE_EXIT_PENDING,
        InternalState.COOLDOWN: N.STATE_COOLDOWN,
        InternalState.WAIT: N.STATE_WAIT,
        InternalState.DISABLED: N.STATE_DISABLED,
    }
    return mapping.get(state, N.STATE_IDLE)


def _decision_to_wire(decision: StrategyDecision) -> dict[str, str]:
    metadata = getattr(decision, "metadata", {}) or {}
    blocker_code = _safe_str(getattr(decision, "blocker_code", None))
    reason_code = blocker_code or _safe_str(metadata.get("reason_code")) or _safe_str(getattr(decision, "explain", None))
    return {
        "decision_id": decision.decision_id,
        "ts_ns": str(decision.ts_event_ns),
        "action": decision.action,
        "reason_code": reason_code,
        "entry_mode": decision.entry_mode,
        "payload_json": _json_dumps(decision.to_dict()),
    }


def _recursive_lookup(mapping: Any, key: str) -> Any:
    if isinstance(mapping, Mapping):
        if key in mapping:
            return mapping[key]
        for value in mapping.values():
            found = _recursive_lookup(value, key)
            if found is not None:
                return found
    elif isinstance(mapping, Sequence) and not isinstance(mapping, (str, bytes, bytearray)):
        for value in mapping:
            found = _recursive_lookup(value, key)
            if found is not None:
                return found
    return None


def _load_yaml_file(path: str) -> Mapping[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {}
    try:
        raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, Mapping) else {}


class DoctrineParamStore:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], Mapping[str, Any]] = {}
        for key, path in DOCTRINE_PARAM_PATHS.items():
            self._cache[key] = _load_yaml_file(path)

    def get(self, family_id: str | None, branch_id: str | None, key: str, default: Any) -> Any:
        if not family_id or not branch_id:
            return default
        raw = self._cache.get((family_id, branch_id)) or {}
        found = _recursive_lookup(raw, key)
        return default if found is None else found


# =============================================================================
# Internal read models
# =============================================================================


@dataclass(slots=True, frozen=True)
class RiskView:
    veto_entries: bool
    degraded_only: bool
    force_flatten: bool
    stale: bool
    cooldown_active: bool
    cooldown_until_ns: int
    reason_code: str
    reason_message: str
    max_new_lots: int


@dataclass(slots=True, frozen=True)
class ExecutionView:
    execution_mode: str
    broker_degraded: bool
    entry_pending: bool
    exit_pending: bool
    reconciliation_lock: bool = False
    unresolved_disaster_lock: bool = False
    execution_primary_provider_id: str = ""
    execution_primary_status: str = ""
    fallback_execution_provider_id: str = ""
    fallback_execution_status: str = ""
    execution_bridge_ok: bool = False


@dataclass(slots=True, frozen=True)
class PositionView:
    has_position: bool
    position_side: str
    entry_option_symbol: str
    entry_option_token: str
    avg_price: float
    qty_lots: int
    entry_ts_ns: int
    entry_mode: str
    meta_json: str | None


@dataclass(slots=True, frozen=True)
class FeaturePayloadView:
    frame_id: str
    frame_ts_ns: int
    selection_version: str
    readiness: Mapping[str, Any]
    provider_surface: Mapping[str, Any]
    family_surfaces: Mapping[str, Any]
    family_frames: Mapping[str, Any]
    shared_features: Mapping[str, Any]


@dataclass(slots=True, frozen=True)
class Candidate:
    family_id: str
    doctrine_id: str
    branch_id: str
    side: str
    position_side: str
    strategy_runtime_mode: str
    family_runtime_mode: str
    active_futures_provider_id: str | None
    active_selected_option_provider_id: str | None
    active_option_context_provider_id: str | None
    instrument_key: str
    instrument_token: str
    option_symbol: str
    strike: float | None
    entry_mode: str
    option_price: float
    tick_size: float
    depth_total: int
    spread_ratio: float
    response_efficiency: float
    target_points: float
    stop_points: float
    score: float
    reason_chain: tuple[str, ...]
    source_event_id: str
    trap_event_id: str | None = None
    burst_event_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ArmedSetup:
    setup_id: str
    candidate: Candidate
    armed_ts_ns: int
    confirmation_deadline_ns: int
    confirmations_seen: int = 0


@dataclass(slots=True, frozen=True)
class OpenPositionContext:
    family_id: str | None
    doctrine_id: str | None
    branch_id: str | None
    strategy_runtime_mode: str | None
    family_runtime_mode: str | None
    source_event_id: str | None
    trap_event_id: str | None
    burst_event_id: str | None
    target_points: float | None
    stop_points: float | None
    setup_id: str | None
    regime: str | None
    current_leg_id: str | None
    primary_entry_done_in_current_leg: bool
    reentry_count_in_current_leg: int
    last_exit_reason: str | None
    last_exit_pnl_points: float
    last_exit_fut_price: float | None
    last_exit_ts_ns: int
    post_exit_high_fut: float | None
    post_exit_low_fut: float | None
    entry_fut_price: float | None
    proof_deadline_ns: int
    stage1_deadline_ns: int
    stage2_deadline_ns: int
    highest_profit: float
    highest_profit_ts_ns: int
    profit_protection_active: bool


# =============================================================================
# Strategy machine
# =============================================================================


class InternalState(str, Enum):
    SCANNING = "SCANNING"
    ARMED = "ARMED"
    RETEST_MONITOR = "RETEST_MONITOR"
    CONFIRMING = "CONFIRMING"
    ENTRY_PENDING = "ENTRY_PENDING"
    POSITION_OPEN = "POSITION_OPEN"
    EXIT_PENDING = "EXIT_PENDING"
    COOLDOWN = "COOLDOWN"
    WAIT = "WAIT"
    DISABLED = "DISABLED"


@dataclass(slots=True, frozen=True)
class RuntimeMachine:
    state: InternalState = InternalState.SCANNING
    updated_ts_ns: int = 0
    reason_code: str = "boot"
    cooldown_until_ns: int | None = None
    wait_until_ns: int | None = None
    armed_setup: ArmedSetup | None = None
    last_consumed_burst_id: str | None = None
    last_consumed_trap_id: str | None = None
    current_leg_id: str | None = None
    current_leg_family_id: str | None = None
    current_leg_branch_id: str | None = None
    primary_entry_done_in_current_leg: bool = False
    reentry_count_in_current_leg: int = 0
    last_exit_reason: str | None = None
    last_exit_pnl_points: float = 0.0
    last_exit_fut_price: float | None = None
    last_exit_ts_ns: int = 0
    post_exit_high_fut: float | None = None
    post_exit_low_fut: float | None = None


# =============================================================================
# Engine
# =============================================================================


class StrategyEngine:
    def __init__(
        self,
        *,
        logger: logging.Logger | None = None,
        target_pct: float,
        stop_pct: float,
        pending_wait_ms: int,
        confirmation_timeout_ms: int,
    ) -> None:
        self.log = logger or LOGGER.getChild("StrategyEngine")
        self.target_pct = float(target_pct)
        self.stop_pct = float(stop_pct)
        self.pending_wait_ms = int(max(0, pending_wait_ms))
        self.confirmation_timeout_ms = int(max(250, confirmation_timeout_ms))
        self.params = DoctrineParamStore()
        self.machine = RuntimeMachine(updated_ts_ns=0)

    def _param(self, family_id: str | None, branch_id: str | None, key: str, default: Any) -> Any:
        return self.params.get(family_id, branch_id, key, default)

    def _response_min(self, family_id: str | None, branch_id: str | None, runtime_mode: str | None) -> float:
        degraded = runtime_mode == N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED
        default = DEFAULT_CLASSIC_RESPONSE_MIN_DEGRADED if degraded else DEFAULT_CLASSIC_RESPONSE_MIN_NORMAL
        return _safe_float(self._param(family_id, branch_id, "response_eff_min", default), default)

    def _spread_max(self, family_id: str | None, branch_id: str | None, runtime_mode: str | None) -> float:
        degraded = runtime_mode == N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED
        default = DEFAULT_CLASSIC_SPREAD_RATIO_MAX_DEGRADED if degraded else DEFAULT_CLASSIC_SPREAD_RATIO_MAX
        return _safe_float(self._param(family_id, branch_id, "spread_ratio_max", default), default)

    def _depth_min(self, family_id: str | None, branch_id: str | None, runtime_mode: str | None) -> int:
        degraded = runtime_mode == N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED
        default = DEFAULT_CLASSIC_DEPTH_MIN_DEGRADED if degraded else DEFAULT_CLASSIC_DEPTH_MIN
        return _safe_int(self._param(family_id, branch_id, "depth_min", default), default)

    def _impact_max(self, family_id: str | None, branch_id: str | None, runtime_mode: str | None) -> float:
        degraded = runtime_mode == N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED
        default = DEFAULT_CLASSIC_IMPACT_MAX_DEGRADED if degraded else DEFAULT_CLASSIC_IMPACT_MAX
        return _safe_float(self._param(family_id, branch_id, "impact_depth_fraction_max", default), default)

    def _proof_window_sec(self, family_id: str | None, branch_id: str | None) -> float:
        default = 1.75 if family_id == N.STRATEGY_FAMILY_MISC else DEFAULT_PROOF_WINDOW_SEC
        return _safe_float(self._param(family_id, branch_id, "proof_window_sec", default), default)

    def _stage2_window_sec(self, family_id: str | None, branch_id: str | None) -> float:
        default = 5.0 if family_id == N.STRATEGY_FAMILY_MISC else DEFAULT_STAGE2_PROOF_WINDOW_SEC
        return _safe_float(self._param(family_id, branch_id, "stage2_proof_window_sec", default), default)

    def _retest_monitor_sec(self, family_id: str | None, branch_id: str | None, regime: str | None) -> float:
        regime_key = _safe_str(regime, "NORMAL").upper()
        default = {"LOWVOL": 10.0, "NORMAL": DEFAULT_MISC_RETEST_MONITOR_SEC, "FAST": 6.0}.get(regime_key, DEFAULT_MISC_RETEST_MONITOR_SEC)
        return _safe_float(self._param(family_id, branch_id, f"{regime_key.lower()}_retest_max_time_sec", default), default)

    def _armed_monitor_sec(self, family_id: str | None, branch_id: str | None) -> float:
        default = DEFAULT_MISR_ARMED_MONITOR_SEC
        return _safe_float(self._param(family_id, branch_id, "armed_monitor_sec", default), default)

    def _session_end_flatten_hhmm(self, family_id: str | None, branch_id: str | None) -> str:
        value = _safe_str(self._param(family_id, branch_id, "session_end_flatten_hhmm", DEFAULT_SESSION_END_FLATTEN_HHMM), DEFAULT_SESSION_END_FLATTEN_HHMM)
        digits = "".join(ch for ch in value if ch.isdigit())
        return digits if len(digits) == 4 else DEFAULT_SESSION_END_FLATTEN_HHMM

    def _max_hold_sec(self, family_id: str | None, branch_id: str | None, regime: str | None) -> float:
        regime_key = _safe_str(regime, "NORMAL").upper()
        default = {"LOWVOL": DEFAULT_MAX_HOLD_LOWVOL_SEC, "NORMAL": DEFAULT_MAX_HOLD_NORMAL_SEC, "FAST": DEFAULT_MAX_HOLD_FAST_SEC}.get(regime_key, DEFAULT_MAX_HOLD_NORMAL_SEC)
        return _safe_float(self._param(family_id, branch_id, f"{regime_key.lower()}_max_hold_sec", default), default)

    def _time_stall_sec(self, family_id: str | None, branch_id: str | None, regime: str | None) -> float:
        regime_key = _safe_str(regime, "NORMAL").upper()
        default = {"LOWVOL": DEFAULT_TIME_STALL_LOWVOL_SEC, "NORMAL": DEFAULT_TIME_STALL_NORMAL_SEC, "FAST": DEFAULT_TIME_STALL_FAST_SEC}.get(regime_key, DEFAULT_TIME_STALL_NORMAL_SEC)
        return _safe_float(self._param(family_id, branch_id, f"{regime_key.lower()}_time_stall_sec", default), default)

    def _route_cooldown_sec(self, family_id: str | None, branch_id: str | None, regime: str | None, exit_reason: str, pnl_points: float) -> float:
        positive = pnl_points > 0.0
        target_like = exit_reason in {"hard_target", "profit_stall"} or (exit_reason in {"time_stall", "max_hold_exit"} and positive)
        regime_key = _safe_str(regime, "NORMAL").upper()
        if family_id == N.STRATEGY_FAMILY_MIST and target_like:
            default = {"LOWVOL": 12.0, "NORMAL": 8.0, "FAST": 5.0}.get(regime_key, 8.0)
            return _safe_float(self._param(family_id, branch_id, f"cooldown_after_target_{regime_key.lower()}", default), default)
        if target_like:
            default = DEFAULT_TARGET_COOLDOWN_SEC
            return _safe_float(self._param(family_id, branch_id, "cooldown_after_target_sec", default), default)
        default = DEFAULT_STOP_COOLDOWN_SEC
        return _safe_float(self._param(family_id, branch_id, "cooldown_after_stop_sec", default), default)

    def _reentry_cap(self, family_id: str | None, regime: str | None) -> int:
        regime_key = _safe_str(regime, "NORMAL").upper()
        default = DEFAULT_REENTRY_CAPS.get(family_id or "", {}).get(regime_key, 0)
        return default

    def _allowed_reentry(self, family_id: str | None, last_exit_reason: str | None) -> bool:
        if not family_id or not last_exit_reason:
            return False
        return _safe_str(last_exit_reason) in ALLOWED_REENTRY_EXIT_REASONS.get(family_id, ())

    def _forbidden_reentry(self, family_id: str | None, last_exit_reason: str | None) -> bool:
        if not family_id or not last_exit_reason:
            return False
        return _safe_str(last_exit_reason) in FORBIDDEN_REENTRY_EXIT_REASONS.get(family_id, ())

    def evaluate(
        self,
        *,
        payload: FeaturePayloadView,
        risk: RiskView,
        execution: ExecutionView,
        position: PositionView,
        now_ns: int,
        trading_allowed: bool = True,
    ) -> StrategyDecision | None:
        if position.has_position and position.position_side != N.POSITION_SIDE_FLAT:
            reason = "position_open"
            if self.machine.state == InternalState.ENTRY_PENDING:
                reason = "entry_fill_detected"
            self._transition(InternalState.POSITION_OPEN, now_ns, reason)
            return self._handle_open_position(
                payload=payload,
                risk=risk,
                execution=execution,
                position=position,
                now_ns=now_ns,
            )
        return self._handle_flat_position(
            payload=payload,
            risk=risk,
            execution=execution,
            now_ns=now_ns,
            trading_allowed=trading_allowed,
        )

    def _handle_flat_position(
        self,
        *,
        payload: FeaturePayloadView,
        risk: RiskView,
        execution: ExecutionView,
        now_ns: int,
        trading_allowed: bool,
    ) -> StrategyDecision | None:
        family_runtime_mode = _safe_str(payload.provider_surface.get("family_runtime_mode"), N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY)
        self._maybe_reset_leg_on_bias_failure(payload=payload, now_ns=now_ns)
        self._update_post_exit_extremes(payload=payload)

        if execution.broker_degraded:
            self._transition(InternalState.DISABLED, now_ns, "execution_broker_degraded")
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="execution_broker_degraded",
                side=N.SIDE_CALL,
                family_runtime_mode=family_runtime_mode,
            )

        if execution.entry_pending or execution.exit_pending:
            self._transition(
                InternalState.WAIT,
                now_ns,
                "pending_execution",
                wait_until_ns=now_ns + (self.pending_wait_ms * 1_000_000),
            )
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="pending_execution",
                side=N.SIDE_CALL,
                family_runtime_mode=family_runtime_mode,
            )

        if self.machine.state is InternalState.WAIT:
            if self.machine.wait_until_ns is not None and now_ns < self.machine.wait_until_ns:
                return self._build_hold_decision(
                    now_ns=now_ns,
                    reason="pending_execution",
                    side=N.SIDE_CALL,
                    family_runtime_mode=family_runtime_mode,
                )
            self._transition(InternalState.SCANNING, now_ns, "wait_complete")

        if self.machine.state is InternalState.COOLDOWN:
            if self.machine.cooldown_until_ns is not None and now_ns < self.machine.cooldown_until_ns:
                return self._build_hold_decision(
                    now_ns=now_ns,
                    reason="cooldown_active",
                    side=N.SIDE_CALL,
                    family_runtime_mode=family_runtime_mode,
                )
            self._transition(InternalState.SCANNING, now_ns, "cooldown_complete")

        gate_reason = self._pre_entry_gate(
            payload=payload,
            risk=risk,
            execution=execution,
            trading_allowed=trading_allowed,
            now_ns=now_ns,
        )
        if gate_reason is not None:
            if self.machine.state in {InternalState.ARMED, InternalState.CONFIRMING}:
                self._transition(InternalState.SCANNING, now_ns, gate_reason, armed_setup=None)
            return self._build_hold_decision(
                now_ns=now_ns,
                reason=gate_reason,
                side=N.SIDE_CALL,
                family_runtime_mode=family_runtime_mode,
            )

        if self.machine.state in {InternalState.ARMED, InternalState.RETEST_MONITOR, InternalState.CONFIRMING} and self.machine.armed_setup is not None:
            return self._confirm_armed_setup(
                payload=payload,
                risk=risk,
                now_ns=now_ns,
            )

        best = self._select_best_candidate(payload=payload, now_ns=now_ns)
        if best is None:
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="no_candidate",
                side=N.SIDE_CALL,
                family_runtime_mode=family_runtime_mode,
            )

        reentry_block = self._reentry_block_reason(candidate=best, payload=payload, now_ns=now_ns)
        if reentry_block is not None:
            return self._build_hold_decision(
                now_ns=now_ns,
                reason=reentry_block,
                side=best.side,
                family_id=best.family_id,
                doctrine_id=best.doctrine_id,
                branch_id=best.branch_id,
                family_runtime_mode=best.family_runtime_mode,
                strategy_runtime_mode=best.strategy_runtime_mode,
            )

        armed = ArmedSetup(
            setup_id=_new_id("setup"),
            candidate=best,
            armed_ts_ns=now_ns,
            confirmation_deadline_ns=now_ns + (self.confirmation_timeout_ms * 1_000_000),
            confirmations_seen=0,
        )
        if best.family_id == N.STRATEGY_FAMILY_MISC and not _safe_bool(best.metadata.get("resume_ready"), False):
            armed = ArmedSetup(
                setup_id=armed.setup_id,
                candidate=best,
                armed_ts_ns=armed.armed_ts_ns,
                confirmation_deadline_ns=now_ns + _cooldown_ns(self._retest_monitor_sec(best.family_id, best.branch_id, _safe_str(best.metadata.get("regime"), "NORMAL"))),
                confirmations_seen=0,
            )
            self._transition(InternalState.RETEST_MONITOR, now_ns, "misc_retest_monitor_started", armed_setup=armed)
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="misc_retest_monitor",
                side=best.side,
                family_id=best.family_id,
                doctrine_id=best.doctrine_id,
                branch_id=best.branch_id,
                family_runtime_mode=best.family_runtime_mode,
                strategy_runtime_mode=best.strategy_runtime_mode,
            )
        if best.family_id == N.STRATEGY_FAMILY_MISR and not _safe_bool(best.metadata.get("reversal_ready"), False):
            armed = ArmedSetup(
                setup_id=armed.setup_id,
                candidate=best,
                armed_ts_ns=armed.armed_ts_ns,
                confirmation_deadline_ns=now_ns + _cooldown_ns(self._armed_monitor_sec(best.family_id, best.branch_id)),
                confirmations_seen=0,
            )
            self._transition(InternalState.ARMED, now_ns, "misr_armed_waiting_reversal", armed_setup=armed)
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="misr_armed_waiting_reversal",
                side=best.side,
                family_id=best.family_id,
                doctrine_id=best.doctrine_id,
                branch_id=best.branch_id,
                family_runtime_mode=best.family_runtime_mode,
                strategy_runtime_mode=best.strategy_runtime_mode,
            )
        self._transition(InternalState.ARMED, now_ns, "candidate_armed", armed_setup=armed)
        self._transition(InternalState.CONFIRMING, now_ns, "confirmation_started", armed_setup=armed)
        return None

    def _pre_entry_gate(
        self,
        *,
        payload: FeaturePayloadView,
        risk: RiskView,
        execution: ExecutionView,
        trading_allowed: bool,
        now_ns: int,
    ) -> str | None:
        family_runtime_mode = _safe_str(payload.provider_surface.get("family_runtime_mode"), N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY)
        if not trading_allowed:
            return "outside_trading_window"
        if family_runtime_mode not in LIVE_FAMILY_MODES:
            return f"family_runtime_mode:{family_runtime_mode.lower()}"
        if execution.execution_mode in {N.EXECUTION_MODE_FATAL, N.EXECUTION_MODE_EXIT_ONLY}:
            return "execution_mode_blocks_entry"
        if execution.reconciliation_lock:
            return "reconciliation_lock_active"
        if execution.unresolved_disaster_lock:
            return "unresolved_disaster_lock_active"
        if risk.force_flatten:
            return "force_flatten_active"
        if risk.degraded_only:
            return "risk_degraded_only"
        if risk.stale:
            return "risk_stale"
        if risk.veto_entries:
            return risk.reason_code or "risk_veto"
        if risk.cooldown_active and risk.cooldown_until_ns > now_ns:
            return "risk_cooldown"
        if risk.max_new_lots <= 0:
            return "risk_zero_quantity"
        if not _safe_bool(payload.readiness.get("provider_runtime_present"), False):
            return "provider_runtime_missing"
        if not _safe_bool(payload.readiness.get("features_present"), True):
            return "feature_payload_missing"
        return None

    def _select_best_candidate(self, *, payload: FeaturePayloadView, now_ns: int) -> Candidate | None:
        candidates: list[Candidate] = []
        for family in FAMILY_ORDER:
            for branch in (N.BRANCH_CALL, N.BRANCH_PUT):
                candidate = self._evaluate_family_branch(
                    payload=payload,
                    family_id=family,
                    branch_id=branch,
                    now_ns=now_ns,
                )
                if candidate is not None:
                    candidates.append(candidate)
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item.score, -FAMILY_ORDER.index(item.family_id), item.branch_id == N.BRANCH_CALL), reverse=True)
        return candidates[0]

    def _evaluate_family_branch(
        self,
        *,
        payload: FeaturePayloadView,
        family_id: str,
        branch_id: str,
        now_ns: int,
    ) -> Candidate | None:
        key = f"{family_id.lower()}_{branch_id.lower()}"
        surface = payload.family_surfaces.get(key)
        frame = payload.family_frames.get(key)
        if not isinstance(surface, Mapping) or not isinstance(frame, Mapping):
            return None

        base = self._base_candidate_context(
            payload=payload,
            surface=surface,
            frame=frame,
            family_id=family_id,
            branch_id=branch_id,
            now_ns=now_ns,
        )
        if base is None:
            return None

        if family_id == N.STRATEGY_FAMILY_MIST:
            return self._evaluate_mist(base)
        if family_id == N.STRATEGY_FAMILY_MISB:
            return self._evaluate_misb(base)
        if family_id == N.STRATEGY_FAMILY_MISC:
            return self._evaluate_misc(base)
        if family_id == N.STRATEGY_FAMILY_MISR:
            return self._evaluate_misr(base)
        if family_id == N.STRATEGY_FAMILY_MISO:
            return self._evaluate_miso(base, payload=payload)
        return None

    def _base_candidate_context(
        self,
        *,
        payload: FeaturePayloadView,
        surface: Mapping[str, Any],
        frame: Mapping[str, Any],
        family_id: str,
        branch_id: str,
        now_ns: int,
    ) -> dict[str, Any] | None:
        frame_valid = _safe_bool(frame.get("frame_valid"), False)
        warmup_complete = _safe_bool(frame.get("warmup_complete"), False)
        strategy_runtime_mode = _safe_str(frame.get("strategy_runtime_mode"), N.STRATEGY_RUNTIME_MODE_DISABLED)
        family_runtime_mode = _safe_str(frame.get("family_runtime_mode"), N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY)
        if not frame_valid or not warmup_complete or strategy_runtime_mode == N.STRATEGY_RUNTIME_MODE_DISABLED:
            return None
        if family_runtime_mode not in LIVE_FAMILY_MODES:
            return None

        economic = frame.get("economic_viability") or {}
        four_pillar = frame.get("four_pillar") or {}
        if not _safe_bool(economic.get("is_viable"), False):
            return None
        if not _safe_bool(four_pillar.get("liquidity_ok"), False):
            return None
        if not _safe_bool(four_pillar.get("alignment_ok"), False):
            return None

        is_miso = family_id == N.STRATEGY_FAMILY_MISO
        option_features = surface.get("selected_features") if is_miso else surface.get("primary_features")
        fallback_features = None if is_miso else surface.get("fallback_features")
        if not isinstance(option_features, Mapping):
            return None

        entry_mode_hint = _normalize_entry_mode(frame.get("entry_mode_hint"))
        chosen_features = option_features
        chosen_entry_mode = entry_mode_hint
        if not is_miso and entry_mode_hint == N.ENTRY_MODE_ATM1 and isinstance(fallback_features, Mapping) and _safe_bool(surface.get("fallback_ready"), False):
            chosen_features = fallback_features
            chosen_entry_mode = N.ENTRY_MODE_ATM1
        elif chosen_entry_mode == N.ENTRY_MODE_UNKNOWN:
            chosen_entry_mode = N.ENTRY_MODE_DIRECT if is_miso else N.ENTRY_MODE_ATM

        instrument_key = _safe_str(chosen_features.get("instrument_key"))
        instrument_token = _safe_str(chosen_features.get("instrument_token"))
        option_symbol = _safe_str(chosen_features.get("trading_symbol"))
        option_price = _safe_float(chosen_features.get("ltp"), 0.0)
        tick_size = _safe_float(chosen_features.get("tick_size"), 0.0)
        depth_total = _safe_int(chosen_features.get("depth_total"), 0)
        spread_ratio = _safe_float(chosen_features.get("spread_ratio"), 999.0)
        response_efficiency = _safe_float(surface.get("response_efficiency"), 0.0)
        impact_fraction = _safe_float(chosen_features.get("impact_depth_fraction_one_lot"), 1.0)
        regime = _safe_str(surface.get("regime"), "NORMAL")

        if not instrument_key or not instrument_token or not option_symbol:
            return None
        if option_price <= 0.0 or tick_size <= 0.0 or depth_total <= 0:
            return None

        if spread_ratio > self._spread_max(family_id, branch_id, strategy_runtime_mode):
            return None
        if depth_total < self._depth_min(family_id, branch_id, strategy_runtime_mode):
            return None
        if impact_fraction > self._impact_max(family_id, branch_id, strategy_runtime_mode):
            return None
        if family_id != N.STRATEGY_FAMILY_MISO and response_efficiency < self._response_min(family_id, branch_id, strategy_runtime_mode):
            return None

        target_points = self._default_target_points(family_id, branch_id, option_price)
        stop_points = self._default_stop_points(family_id, branch_id, option_price)

        provider_runtime = payload.provider_surface.get("runtime") or {}
        source_event_id = _safe_str(payload.frame_id, f"frame-{now_ns}")
        trap_event_id = None
        burst_event_id = None
        if family_id == N.STRATEGY_FAMILY_MISR:
            trap_event_id = f"misr:{branch_id.lower()}:{instrument_key}:{source_event_id}"
        if family_id == N.STRATEGY_FAMILY_MISO:
            burst_event_id = f"miso:{branch_id.lower()}:{instrument_key}:{source_event_id}"

        return {
            "payload": payload,
            "surface": surface,
            "frame": frame,
            "family_id": family_id,
            "doctrine_id": DOCTRINE_BY_FAMILY[family_id],
            "branch_id": branch_id,
            "side": BRANCH_TO_SIDE[branch_id],
            "position_side": BRANCH_TO_POSITION_SIDE[branch_id],
            "strategy_runtime_mode": strategy_runtime_mode,
            "family_runtime_mode": family_runtime_mode,
            "active_futures_provider_id": _safe_str(frame.get("active_futures_provider_id")) or None,
            "active_selected_option_provider_id": _safe_str(frame.get("active_selected_option_provider_id")) or None,
            "active_option_context_provider_id": _safe_str(frame.get("active_option_context_provider_id")) or None,
            "provider_runtime": provider_runtime,
            "economic": economic,
            "four_pillar": four_pillar,
            "option_features": chosen_features,
            "primary_features": option_features,
            "fallback_features": fallback_features,
            "instrument_key": instrument_key,
            "instrument_token": instrument_token,
            "option_symbol": option_symbol,
            "strike": chosen_features.get("strike"),
            "entry_mode": chosen_entry_mode,
            "option_price": option_price,
            "tick_size": tick_size,
            "depth_total": depth_total,
            "spread_ratio": spread_ratio,
            "response_efficiency": response_efficiency,
            "impact_fraction": impact_fraction,
            "target_points": target_points,
            "stop_points": stop_points,
            "source_event_id": source_event_id,
            "trap_event_id": trap_event_id,
            "burst_event_id": burst_event_id,
            "surface_kind": _safe_str(surface.get("surface_kind")),
            "regime": regime,
            "fut_ltp": _safe_float(_nested_get(surface, "futures_features", "ltp", default=0.0), 0.0),
        }

    def _evaluate_mist(self, base: Mapping[str, Any]) -> Candidate | None:
        surface = base["surface"]
        bullish = base["branch_id"] == N.BRANCH_CALL
        trend_score = _safe_float(surface.get("trend_score"), 0.0)
        resume_support = _safe_bool(surface.get("resume_support"), False)
        direction_ok = _safe_bool(surface.get("trend_direction_ok"), False)
        pullback_depth = _safe_float(surface.get("pullback_depth"), 0.0)
        response_eff = _safe_float(base["response_efficiency"], 0.0)
        fut_vel = _safe_float(_nested_get(surface, "futures_features", "velocity_ratio", default=0.0), 0.0)
        fut_ofi = _safe_float(_nested_get(surface, "futures_features", "weighted_ofi_persist", default=0.5), 0.5)
        ofi_ok = fut_ofi >= DEFAULT_CLASSIC_OFI_BULL_MIN if bullish else fut_ofi <= DEFAULT_CLASSIC_OFI_BEAR_MAX
        if not (direction_ok and resume_support and ofi_ok and fut_vel >= DEFAULT_CLASSIC_VELOCITY_RATIO_MIN):
            return None
        score = (abs(trend_score) * 0.55) + (response_eff * 1.4) + (fut_vel * 0.35) - min(pullback_depth * 0.02, 0.5)
        if score < DEFAULT_CLASSIC_SCORE_MIN:
            return None
        return self._build_candidate(
            base,
            score=score,
            reason_chain=("mist", "trend_direction_ok", "resume_support", "response_eff_ok"),
        )

    def _evaluate_misb(self, base: Mapping[str, Any]) -> Candidate | None:
        surface = base["surface"]
        breakout_trigger = _safe_bool(surface.get("breakout_trigger"), False)
        breakout_acceptance = _safe_bool(surface.get("breakout_acceptance"), False)
        alignment_ok = _safe_bool(surface.get("alignment_ok"), False)
        response_eff = _safe_float(base["response_efficiency"], 0.0)
        fut_vel = _safe_float(_nested_get(surface, "futures_features", "velocity_ratio", default=0.0), 0.0)
        shelf_width = _safe_float(surface.get("shelf_width"), 0.0)
        if not (breakout_trigger and breakout_acceptance and alignment_ok and fut_vel >= DEFAULT_CLASSIC_VELOCITY_RATIO_MIN):
            return None
        score = (1.2 if breakout_trigger else 0.0) + (1.0 if breakout_acceptance else 0.0) + (response_eff * 1.4) + (fut_vel * 0.4) - min(shelf_width * 0.02, 0.4)
        if score < DEFAULT_CLASSIC_SCORE_MIN:
            return None
        return self._build_candidate(
            base,
            score=score,
            reason_chain=("misb", "breakout_trigger", "breakout_acceptance", "response_eff_ok"),
        )

    def _evaluate_misc(self, base: Mapping[str, Any]) -> Candidate | None:
        surface = base["surface"]
        breakout_trigger = _safe_bool(surface.get("breakout_trigger"), False)
        resume_support = _safe_bool(surface.get("resume_support"), False)
        alignment_ok = _safe_bool(surface.get("alignment_ok"), False)
        compression_ratio = _safe_float(surface.get("compression_ratio"), 1.0)
        retest_distance = _safe_float(surface.get("retest_distance"), 0.0)
        hesitation = _safe_bool(surface.get("hesitation"), False)
        response_eff = _safe_float(base["response_efficiency"], 0.0)
        if not (breakout_trigger and alignment_ok):
            return None
        if compression_ratio > 1.25:
            return None
        score = 1.1 + (1.0 if breakout_trigger else 0.0) + (0.8 if resume_support else 0.0) + (response_eff * 1.3) - min(retest_distance * 0.015, 0.5)
        if hesitation:
            score -= 0.1
        if score < (DEFAULT_CLASSIC_SCORE_MIN - 0.25):
            return None
        return self._build_candidate(
            base,
            score=score,
            reason_chain=("misc", "compression_breakout", "resume_support" if resume_support else "retest_monitor", "response_eff_ok"),
            extra_meta={
                "resume_ready": resume_support,
                "retest_monitor_required": True,
                "retest_distance": retest_distance,
                "hesitation": hesitation,
            },
        )

    def _evaluate_misr(self, base: Mapping[str, Any]) -> Candidate | None:
        surface = base["surface"]
        fake_break = _safe_bool(surface.get("fake_break"), False)
        absorption = _safe_bool(surface.get("absorption"), False)
        range_reentry = _safe_bool(surface.get("range_reentry"), False)
        hold_proof = _safe_bool(surface.get("hold_proof"), False)
        reversal_impulse = _safe_bool(surface.get("reversal_impulse"), False)
        response_eff = _safe_float(base["response_efficiency"], 0.0)
        if not (fake_break and absorption):
            return None
        reversal_ready = range_reentry and hold_proof and reversal_impulse
        score = 1.4 + (0.6 if fake_break else 0.0) + (0.6 if absorption else 0.0) + (0.6 if range_reentry else 0.0) + (0.6 if hold_proof else 0.0) + (0.7 if reversal_impulse else 0.0) + (response_eff * 1.2)
        return self._build_candidate(
            base,
            score=score,
            reason_chain=("misr", "fake_break", "absorption", "reversal_impulse" if reversal_ready else "armed_waiting_reversal"),
            extra_meta={
                "reversal_ready": reversal_ready,
                "trap_monitor_required": True,
                "fake_break": fake_break,
                "absorption": absorption,
                "range_reentry": range_reentry,
                "hold_proof": hold_proof,
                "reversal_impulse": reversal_impulse,
            },
        )

    def _evaluate_miso(self, base: Mapping[str, Any], *, payload: FeaturePayloadView) -> Candidate | None:
        surface = base["surface"]
        if base["strategy_runtime_mode"] not in {N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH, N.STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED}:
            return None
        aggressive_flow = _safe_bool(surface.get("aggressive_flow"), False)
        tape_speed = _safe_float(surface.get("tape_speed"), 0.0)
        imbalance = _safe_float(surface.get("imbalance_persistence"), 0.5)
        queue_reload_veto = _safe_bool(surface.get("queue_reload_veto"), False)
        shadow_support = _safe_bool(surface.get("shadow_support"), False)
        fut_align = _safe_bool(surface.get("futures_vwap_alignment_ok"), False)
        fut_contradiction = _safe_bool(surface.get("futures_contradiction_veto"), False)
        score = _safe_float(base["option_features"].get("context_score"), 0.0)
        bullish = base["branch_id"] == N.BRANCH_CALL
        imbalance_ok = imbalance >= DEFAULT_MISO_IMBALANCE_MIN_BULL if bullish else imbalance <= DEFAULT_MISO_IMBALANCE_MAX_BEAR
        if not aggressive_flow or tape_speed < DEFAULT_MISO_TAPE_SPEED_MIN or not imbalance_ok:
            return None
        if queue_reload_veto or fut_contradiction or not fut_align:
            return None
        if not shadow_support:
            score -= 0.15
        if base["option_price"] < DEFAULT_MISO_PREMIUM_FLOOR:
            return None

        bridge_reason = self._miso_execution_bridge_reason(base=base, payload=payload)
        if bridge_reason is not None:
            return None

        score = score + 1.0 + (0.9 if aggressive_flow else 0.0) + (tape_speed * 0.35) + (abs(imbalance - 0.5) * 2.0)
        if score < DEFAULT_MISO_SCORE_MIN:
            return None
        return self._build_candidate(
            base,
            score=score,
            reason_chain=("miso", "aggressive_flow", "tape_speed", "imbalance_persist", "execution_bridge_ok"),
            extra_meta={
                "large_counter_trade": _safe_bool(surface.get("large_counter_trade"), False),
                "selected_execution_instrument_key": _safe_str(_nested_get(surface, "selected_features", "execution_instrument_key", default="")),
                "selected_execution_tradable": _safe_bool(_nested_get(surface, "selected_features", "execution_provider_tradable", default=False), False),
            },
        )

    @staticmethod
    def _miso_execution_bridge_reason(*, base: Mapping[str, Any], payload: FeaturePayloadView) -> str | None:
        provider_runtime = base.get("provider_runtime") or {}
        surface = base.get("surface") or {}
        selected = surface.get("selected_features") or {}
        explicit_bridge_ok = _safe_bool(_nested_get(surface, "execution_bridge_ok", default=False), False)
        if explicit_bridge_ok:
            return None
        execution_primary_provider_id = _safe_str(provider_runtime.get("execution_primary_provider_id"))
        execution_primary_status = _safe_str(provider_runtime.get("execution_primary_status"))
        execution_fallback_provider_id = _safe_str(provider_runtime.get("fallback_execution_provider_id"))
        execution_fallback_status = _safe_str(provider_runtime.get("fallback_execution_status"))
        selected_provider_id = _safe_str(base.get("active_selected_option_provider_id"))
        instrument_key = _safe_str(selected.get("instrument_key"))
        instrument_token = _safe_str(selected.get("instrument_token"))
        execution_instrument_key = _safe_str(selected.get("execution_instrument_key"))
        execution_provider_tradable = _safe_bool(selected.get("execution_provider_tradable"), False)
        tradability_ok = (_safe_int(selected.get("depth_total"), 0) > 0) and (_safe_float(selected.get("spread_ratio"), 999.0) < 3.0)
        if not instrument_key or not instrument_token:
            return "miso_execution_bridge_missing_instrument_mapping"
        if not execution_instrument_key and not execution_provider_tradable:
            return "miso_execution_bridge_missing_execution_mapping"
        if execution_primary_provider_id == selected_provider_id and execution_primary_status in {N.PROVIDER_STATUS_HEALTHY, N.PROVIDER_STATUS_DEGRADED} and tradability_ok:
            return None
        if execution_provider_tradable and execution_primary_provider_id in {N.PROVIDER_ZERODHA, N.PROVIDER_DHAN} and execution_primary_status in {N.PROVIDER_STATUS_HEALTHY, N.PROVIDER_STATUS_DEGRADED}:
            return None
        if execution_fallback_provider_id == selected_provider_id and execution_fallback_status in {N.PROVIDER_STATUS_HEALTHY, N.PROVIDER_STATUS_DEGRADED} and tradability_ok:
            return None
        if execution_provider_tradable and execution_fallback_provider_id in {N.PROVIDER_ZERODHA, N.PROVIDER_DHAN} and execution_fallback_status in {N.PROVIDER_STATUS_HEALTHY, N.PROVIDER_STATUS_DEGRADED}:
            return None
        return "miso_execution_bridge_unavailable"

    @staticmethod
    def _build_candidate(
        base: Mapping[str, Any],
        *,
        score: float,
        reason_chain: Sequence[str],
        extra_meta: Mapping[str, Any] | None = None,
    ) -> Candidate:
        metadata = {
                "surface_kind": base.get("surface_kind"),
                "regime": _safe_str(base.get("regime")),
                "regime_reason": _safe_str(_nested_get(base, "surface", "regime_reason", default="")),
                "impact_fraction": base.get("impact_fraction"),
                "economic_blocker": _nested_get(base, "economic", "blocker_code"),
                "fut_ltp": base.get("fut_ltp"),
                "score": score,
            }
        if extra_meta:
            metadata.update(dict(extra_meta))
        return Candidate(
            family_id=base["family_id"],
            doctrine_id=base["doctrine_id"],
            branch_id=base["branch_id"],
            side=base["side"],
            position_side=base["position_side"],
            strategy_runtime_mode=base["strategy_runtime_mode"],
            family_runtime_mode=base["family_runtime_mode"],
            active_futures_provider_id=base["active_futures_provider_id"],
            active_selected_option_provider_id=base["active_selected_option_provider_id"],
            active_option_context_provider_id=base["active_option_context_provider_id"],
            instrument_key=base["instrument_key"],
            instrument_token=base["instrument_token"],
            option_symbol=base["option_symbol"],
            strike=(None if base["strike"] in (None, "") else _safe_float(base["strike"], 0.0)),
            entry_mode=_normalize_entry_mode(base["entry_mode"]),
            option_price=base["option_price"],
            tick_size=base["tick_size"],
            depth_total=base["depth_total"],
            spread_ratio=base["spread_ratio"],
            response_efficiency=base["response_efficiency"],
            target_points=base["target_points"],
            stop_points=base["stop_points"],
            score=score,
            reason_chain=tuple(reason_chain),
            source_event_id=base["source_event_id"],
            trap_event_id=base.get("trap_event_id"),
            burst_event_id=base.get("burst_event_id"),
            metadata=metadata,
        )

    def _confirm_armed_setup(
        self,
        *,
        payload: FeaturePayloadView,
        risk: RiskView,
        now_ns: int,
    ) -> StrategyDecision | None:
        armed = self.machine.armed_setup
        if armed is None:
            self._transition(InternalState.SCANNING, now_ns, "armed_setup_missing", armed_setup=None)
            return None

        if risk.force_flatten or risk.veto_entries or risk.degraded_only or risk.stale:
            self._transition(
                InternalState.COOLDOWN,
                now_ns,
                "risk_blocks_confirmation",
                cooldown_until_ns=now_ns + _cooldown_ns(DEFAULT_STOP_COOLDOWN_SEC),
                armed_setup=None,
            )
            return self._build_hold_decision(
                now_ns=now_ns,
                reason=risk.reason_code or "risk_blocks_confirmation",
                side=armed.candidate.side,
                family_id=armed.candidate.family_id,
                doctrine_id=armed.candidate.doctrine_id,
                branch_id=armed.candidate.branch_id,
                family_runtime_mode=armed.candidate.family_runtime_mode,
                strategy_runtime_mode=armed.candidate.strategy_runtime_mode,
            )

        if now_ns > armed.confirmation_deadline_ns:
            self._transition(
                InternalState.COOLDOWN,
                now_ns,
                "confirmation_timeout",
                cooldown_until_ns=now_ns + _cooldown_ns(DEFAULT_WAIT_COOLDOWN_SEC),
                armed_setup=None,
            )
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="confirmation_timeout",
                side=armed.candidate.side,
                family_id=armed.candidate.family_id,
                doctrine_id=armed.candidate.doctrine_id,
                branch_id=armed.candidate.branch_id,
                family_runtime_mode=armed.candidate.family_runtime_mode,
                strategy_runtime_mode=armed.candidate.strategy_runtime_mode,
            )

        refreshed = self._evaluate_family_branch(
            payload=payload,
            family_id=armed.candidate.family_id,
            branch_id=armed.candidate.branch_id,
            now_ns=now_ns,
        )
        if refreshed is None:
            self._transition(InternalState.SCANNING, now_ns, "candidate_no_longer_valid", armed_setup=None)
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="candidate_no_longer_valid",
                side=armed.candidate.side,
                family_id=armed.candidate.family_id,
                doctrine_id=armed.candidate.doctrine_id,
                branch_id=armed.candidate.branch_id,
                family_runtime_mode=armed.candidate.family_runtime_mode,
                strategy_runtime_mode=armed.candidate.strategy_runtime_mode,
            )

        if refreshed.instrument_key != armed.candidate.instrument_key:
            self._transition(InternalState.SCANNING, now_ns, "instrument_changed_during_confirmation", armed_setup=None)
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="instrument_changed_during_confirmation",
                side=armed.candidate.side,
                family_id=armed.candidate.family_id,
                doctrine_id=armed.candidate.doctrine_id,
                branch_id=armed.candidate.branch_id,
                family_runtime_mode=armed.candidate.family_runtime_mode,
                strategy_runtime_mode=armed.candidate.strategy_runtime_mode,
            )

        if self.machine.state == InternalState.RETEST_MONITOR and refreshed.family_id == N.STRATEGY_FAMILY_MISC:
            if not _safe_bool(refreshed.metadata.get("resume_ready"), False):
                updated = ArmedSetup(
                    setup_id=armed.setup_id,
                    candidate=refreshed,
                    armed_ts_ns=armed.armed_ts_ns,
                    confirmation_deadline_ns=armed.confirmation_deadline_ns,
                    confirmations_seen=0,
                )
                self._transition(InternalState.RETEST_MONITOR, now_ns, "misc_retest_monitor_active", armed_setup=updated)
                return self._build_hold_decision(
                    now_ns=now_ns,
                    reason="misc_retest_monitor",
                    side=refreshed.side,
                    family_id=refreshed.family_id,
                    doctrine_id=refreshed.doctrine_id,
                    branch_id=refreshed.branch_id,
                    family_runtime_mode=refreshed.family_runtime_mode,
                    strategy_runtime_mode=refreshed.strategy_runtime_mode,
                )
            updated = ArmedSetup(
                setup_id=armed.setup_id,
                candidate=refreshed,
                armed_ts_ns=armed.armed_ts_ns,
                confirmation_deadline_ns=now_ns + (self.confirmation_timeout_ms * 1_000_000),
                confirmations_seen=0,
            )
            self._transition(InternalState.CONFIRMING, now_ns, "misc_resume_confirming", armed_setup=updated)
            return None

        if self.machine.state == InternalState.ARMED and refreshed.family_id == N.STRATEGY_FAMILY_MISR:
            if not _safe_bool(refreshed.metadata.get("reversal_ready"), False):
                updated = ArmedSetup(
                    setup_id=armed.setup_id,
                    candidate=refreshed,
                    armed_ts_ns=armed.armed_ts_ns,
                    confirmation_deadline_ns=armed.confirmation_deadline_ns,
                    confirmations_seen=0,
                )
                self._transition(InternalState.ARMED, now_ns, "misr_armed_waiting_reversal", armed_setup=updated)
                return self._build_hold_decision(
                    now_ns=now_ns,
                    reason="misr_armed_waiting_reversal",
                    side=refreshed.side,
                    family_id=refreshed.family_id,
                    doctrine_id=refreshed.doctrine_id,
                    branch_id=refreshed.branch_id,
                    family_runtime_mode=refreshed.family_runtime_mode,
                    strategy_runtime_mode=refreshed.strategy_runtime_mode,
                )
            updated = ArmedSetup(
                setup_id=armed.setup_id,
                candidate=refreshed,
                armed_ts_ns=armed.armed_ts_ns,
                confirmation_deadline_ns=now_ns + (self.confirmation_timeout_ms * 1_000_000),
                confirmations_seen=0,
            )
            self._transition(InternalState.CONFIRMING, now_ns, "misr_reversal_confirming", armed_setup=updated)
            return None

        confirmations_seen = armed.confirmations_seen + 1
        if confirmations_seen < DEFAULT_CONFIRMATION_SNAPSHOTS:
            updated = ArmedSetup(
                setup_id=armed.setup_id,
                candidate=refreshed,
                armed_ts_ns=armed.armed_ts_ns,
                confirmation_deadline_ns=armed.confirmation_deadline_ns,
                confirmations_seen=confirmations_seen,
            )
            self._transition(InternalState.CONFIRMING, now_ns, "confirmation_in_progress", armed_setup=updated)
            return None

        qty_lots = max(1, risk.max_new_lots)
        return self._build_entry_decision(candidate=refreshed, setup_id=armed.setup_id, now_ns=now_ns, quantity_lots=qty_lots)

    def _handle_open_position(
        self,
        *,
        payload: FeaturePayloadView,
        risk: RiskView,
        execution: ExecutionView,
        position: PositionView,
        now_ns: int,
    ) -> StrategyDecision | None:
        self._transition(InternalState.POSITION_OPEN, now_ns, "position_open")

        position_ctx = self._position_context(position)
        if position_ctx.current_leg_id:
            self.machine = RuntimeMachine(
                state=self.machine.state,
                updated_ts_ns=self.machine.updated_ts_ns,
                reason_code=self.machine.reason_code,
                cooldown_until_ns=self.machine.cooldown_until_ns,
                wait_until_ns=self.machine.wait_until_ns,
                armed_setup=self.machine.armed_setup,
                last_consumed_burst_id=self.machine.last_consumed_burst_id,
                last_consumed_trap_id=self.machine.last_consumed_trap_id,
                current_leg_id=position_ctx.current_leg_id,
                current_leg_family_id=position_ctx.family_id or self.machine.current_leg_family_id,
                current_leg_branch_id=position_ctx.branch_id or self.machine.current_leg_branch_id,
                primary_entry_done_in_current_leg=True,
                reentry_count_in_current_leg=max(
                    self.machine.reentry_count_in_current_leg,
                    position_ctx.reentry_count_in_current_leg,
                ),
                last_exit_reason=self.machine.last_exit_reason,
                last_exit_pnl_points=self.machine.last_exit_pnl_points,
                last_exit_fut_price=self.machine.last_exit_fut_price,
                last_exit_ts_ns=self.machine.last_exit_ts_ns,
                post_exit_high_fut=position_ctx.post_exit_high_fut if position_ctx.post_exit_high_fut is not None else self.machine.post_exit_high_fut,
                post_exit_low_fut=position_ctx.post_exit_low_fut if position_ctx.post_exit_low_fut is not None else self.machine.post_exit_low_fut,
            )

        if execution.entry_pending or execution.exit_pending:
            self._transition(
                InternalState.WAIT,
                now_ns,
                "pending_execution",
                wait_until_ns=now_ns + (self.pending_wait_ms * 1_000_000),
            )
            return None

        if risk.force_flatten:
            return self._build_exit_decision(
                position=position,
                now_ns=now_ns,
                reason="risk_force_flatten",
                surface=None,
            )

        position_ctx = self._position_context(position)
        active_surface = self._find_open_position_surface(payload=payload, position=position, position_ctx=position_ctx)
        if active_surface is None:
            return self._build_exit_decision(
                position=position,
                now_ns=now_ns,
                reason="feed_failure_exit",
                surface=None,
            )

        current_price = _safe_float(_nested_get(active_surface, "option_features", "ltp", default=0.0), 0.0)
        if current_price <= 0.0:
            return self._build_exit_decision(
                position=position,
                now_ns=now_ns,
                reason="feed_failure_exit",
                surface=active_surface,
            )

        target_points = position_ctx.target_points or self._default_target_points(position_ctx.family_id, position_ctx.branch_id, current_price)
        stop_points = position_ctx.stop_points or self._default_stop_points(position_ctx.family_id, position_ctx.branch_id, current_price)
        open_profit = current_price - position.avg_price
        highest_profit = max(position_ctx.highest_profit, open_profit)
        highest_profit_ts_ns = position_ctx.highest_profit_ts_ns or (position.entry_ts_ns or now_ns)
        if open_profit > position_ctx.highest_profit + EPSILON:
            highest_profit_ts_ns = now_ns
        profit_protection_active = position_ctx.profit_protection_active or (open_profit >= (DEFAULT_PROFIT_PROTECT_TRIGGER * target_points))

        exit_reason = self._evaluate_exit_reason(
            position=position,
            position_ctx=position_ctx,
            surface=active_surface,
            now_ns=now_ns,
            current_price=current_price,
            target_points=target_points,
            stop_points=stop_points,
            open_profit=open_profit,
            highest_profit=highest_profit,
            highest_profit_ts_ns=highest_profit_ts_ns,
            profit_protection_active=profit_protection_active,
        )
        if exit_reason is None:
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="hold_open_position",
                side=(N.SIDE_CALL if position.position_side == N.POSITION_SIDE_LONG_CALL else N.SIDE_PUT),
                family_id=position_ctx.family_id,
                doctrine_id=position_ctx.doctrine_id,
                branch_id=position_ctx.branch_id,
                family_runtime_mode=position_ctx.family_runtime_mode,
                strategy_runtime_mode=position_ctx.strategy_runtime_mode,
                extra_meta={
                    "highest_profit": highest_profit,
                    "highest_profit_ts_ns": highest_profit_ts_ns,
                    "profit_protection_active": profit_protection_active,
                },
            )

        return self._build_exit_decision(
            position=position,
            now_ns=now_ns,
            reason=exit_reason,
            surface=active_surface,
            extra_meta={
                "highest_profit": highest_profit,
                "highest_profit_ts_ns": highest_profit_ts_ns,
                "profit_protection_active": profit_protection_active,
                "target_points": target_points,
                "stop_points": stop_points,
                "open_profit": open_profit,
            },
        )

    def _find_open_position_surface(
        self,
        *,
        payload: FeaturePayloadView,
        position: PositionView,
        position_ctx: OpenPositionContext,
    ) -> Mapping[str, Any] | None:
        option_features = None
        family_surface = None
        key = None
        if position_ctx.family_id and position_ctx.branch_id:
            key = f"{position_ctx.family_id.lower()}_{position_ctx.branch_id.lower()}"
            family_surface = payload.family_surfaces.get(key)
        if not isinstance(family_surface, Mapping):
            candidate_family = position_ctx.family_id or N.STRATEGY_FAMILY_MIST
            candidate_branch = N.BRANCH_CALL if position.position_side == N.POSITION_SIDE_LONG_CALL else N.BRANCH_PUT
            key = f"{candidate_family.lower()}_{candidate_branch.lower()}"
            family_surface = payload.family_surfaces.get(key)
        if not isinstance(family_surface, Mapping):
            return None

        resolved_family_id = position_ctx.family_id or candidate_family
        resolved_branch_id = position_ctx.branch_id or candidate_branch
        resolved_doctrine_id = position_ctx.doctrine_id or DOCTRINE_BY_FAMILY.get(resolved_family_id)

        option_features = family_surface.get("selected_features") if family_surface.get("surface_kind") == "miso" else family_surface.get("primary_features")
        if not isinstance(option_features, Mapping):
            return None
        if position.entry_option_token:
            token = _safe_str(option_features.get("instrument_token"))
            if token and token != _safe_str(position.entry_option_token):
                # if token drifted, surface is not trustworthy for this open position
                return None
        return {
            "family_id": resolved_family_id,
            "doctrine_id": resolved_doctrine_id,
            "branch_id": resolved_branch_id,
            "family_surface": family_surface,
            "option_features": option_features,
        }

    def _bias_active_for_surface(self, family_id: str | None, branch_id: str | None, family_surface: Mapping[str, Any]) -> bool:
        if not family_id:
            return True
        if family_id == N.STRATEGY_FAMILY_MIST:
            return _safe_bool(family_surface.get("trend_direction_ok"), True)
        if family_id in {N.STRATEGY_FAMILY_MISB, N.STRATEGY_FAMILY_MISC}:
            return _safe_bool(family_surface.get("alignment_ok"), _safe_bool(family_surface.get("breakout_trigger"), True))
        if family_id == N.STRATEGY_FAMILY_MISR:
            return _safe_bool(family_surface.get("absorption"), True) or _safe_bool(family_surface.get("fake_break"), True)
        if family_id == N.STRATEGY_FAMILY_MISO:
            return not _safe_bool(family_surface.get("futures_contradiction_veto"), False)
        return True

    def _maybe_reset_leg_on_bias_failure(self, *, payload: FeaturePayloadView, now_ns: int) -> None:
        if self.machine.current_leg_id is None or not self.machine.current_leg_family_id or not self.machine.current_leg_branch_id:
            return
        key = f"{self.machine.current_leg_family_id.lower()}_{self.machine.current_leg_branch_id.lower()}"
        family_surface = payload.family_surfaces.get(key)
        if not isinstance(family_surface, Mapping):
            return
        if self._bias_active_for_surface(self.machine.current_leg_family_id, self.machine.current_leg_branch_id, family_surface):
            return
        self.machine = RuntimeMachine(
            state=self.machine.state,
            updated_ts_ns=now_ns,
            reason_code="leg_reset_bias_failed",
            cooldown_until_ns=self.machine.cooldown_until_ns,
            wait_until_ns=self.machine.wait_until_ns,
            armed_setup=self.machine.armed_setup,
            last_consumed_burst_id=self.machine.last_consumed_burst_id,
            last_consumed_trap_id=self.machine.last_consumed_trap_id,
            current_leg_id=None,
            current_leg_family_id=None,
            current_leg_branch_id=None,
            primary_entry_done_in_current_leg=False,
            reentry_count_in_current_leg=0,
            last_exit_reason=self.machine.last_exit_reason,
            last_exit_pnl_points=self.machine.last_exit_pnl_points,
            last_exit_fut_price=self.machine.last_exit_fut_price,
            last_exit_ts_ns=self.machine.last_exit_ts_ns,
            post_exit_high_fut=None,
            post_exit_low_fut=None,
        )

    def _update_post_exit_extremes(self, *, payload: FeaturePayloadView) -> None:
        shared = payload.shared_features or {}
        future = shared.get("active_futures") or shared.get("dhan_futures") or {}
        fut_ltp = _safe_float(future.get("ltp"), 0.0)
        if fut_ltp <= 0.0:
            return
        post_high = self.machine.post_exit_high_fut
        post_low = self.machine.post_exit_low_fut
        if post_high is None or fut_ltp > post_high:
            post_high = fut_ltp
        if post_low is None or fut_ltp < post_low:
            post_low = fut_ltp
        self.machine = RuntimeMachine(
            state=self.machine.state,
            updated_ts_ns=self.machine.updated_ts_ns,
            reason_code=self.machine.reason_code,
            cooldown_until_ns=self.machine.cooldown_until_ns,
            wait_until_ns=self.machine.wait_until_ns,
            armed_setup=self.machine.armed_setup,
            last_consumed_burst_id=self.machine.last_consumed_burst_id,
            last_consumed_trap_id=self.machine.last_consumed_trap_id,
            current_leg_id=self.machine.current_leg_id,
            current_leg_family_id=self.machine.current_leg_family_id,
            current_leg_branch_id=self.machine.current_leg_branch_id,
            primary_entry_done_in_current_leg=self.machine.primary_entry_done_in_current_leg,
            reentry_count_in_current_leg=self.machine.reentry_count_in_current_leg,
            last_exit_reason=self.machine.last_exit_reason,
            last_exit_pnl_points=self.machine.last_exit_pnl_points,
            last_exit_fut_price=self.machine.last_exit_fut_price,
            last_exit_ts_ns=self.machine.last_exit_ts_ns,
            post_exit_high_fut=post_high,
            post_exit_low_fut=post_low,
        )

    def _fresh_structure_ok(self, *, candidate: Candidate) -> bool:
        if self.machine.current_leg_id is None:
            return True
        if self.machine.current_leg_family_id != candidate.family_id or self.machine.current_leg_branch_id != candidate.branch_id:
            return True
        fut_ltp = _safe_float(candidate.metadata.get("fut_ltp"), 0.0)
        if candidate.branch_id == N.BRANCH_CALL and self.machine.post_exit_high_fut is not None:
            return fut_ltp > self.machine.post_exit_high_fut + candidate.tick_size
        if candidate.branch_id == N.BRANCH_PUT and self.machine.post_exit_low_fut is not None:
            return fut_ltp < self.machine.post_exit_low_fut - candidate.tick_size
        return False

    def _reentry_block_reason(self, *, candidate: Candidate, payload: FeaturePayloadView, now_ns: int) -> str | None:
        if candidate.family_id in {N.STRATEGY_FAMILY_MISO, N.STRATEGY_FAMILY_MISR}:
            if candidate.burst_event_id and candidate.burst_event_id == self.machine.last_consumed_burst_id:
                return "same_burst_retry_blocked"
            if candidate.trap_event_id and candidate.trap_event_id == self.machine.last_consumed_trap_id:
                return "same_trap_retry_blocked"
        if self.machine.current_leg_id is None:
            return None
        if self.machine.current_leg_family_id != candidate.family_id or self.machine.current_leg_branch_id != candidate.branch_id:
            return None
        if self._forbidden_reentry(candidate.family_id, self.machine.last_exit_reason):
            return "reentry_forbidden_by_exit_reason"
        if not self._allowed_reentry(candidate.family_id, self.machine.last_exit_reason):
            return "reentry_not_allowed"
        regime = _safe_str(candidate.metadata.get("regime"), "NORMAL")
        if self.machine.reentry_count_in_current_leg >= self._reentry_cap(candidate.family_id, regime):
            return "reentry_cap_reached"
        if not self._fresh_structure_ok(candidate=candidate):
            return "fresh_structure_not_rebuilt"
        return None

    def _proof_failure_reason(self, *, position_ctx: OpenPositionContext, family_surface: Mapping[str, Any], option_features: Mapping[str, Any], now_ns: int) -> str | None:
        response_eff = _safe_float(option_features.get("response_efficiency"), _safe_float(family_surface.get("response_efficiency"), 0.0))
        if position_ctx.proof_deadline_ns and now_ns <= position_ctx.proof_deadline_ns:
            family_id = position_ctx.family_id
            if family_id == N.STRATEGY_FAMILY_MIST:
                if not _safe_bool(family_surface.get("resume_support"), False):
                    return "proof_failure_exit"
            elif family_id == N.STRATEGY_FAMILY_MISB:
                if not _safe_bool(family_surface.get("breakout_acceptance"), False):
                    return "proof_failure_exit"
            elif family_id == N.STRATEGY_FAMILY_MISC:
                if position_ctx.stage1_deadline_ns and now_ns <= position_ctx.stage1_deadline_ns and not _safe_bool(family_surface.get("breakout_trigger"), False):
                    return "proof_failure_exit"
                if position_ctx.stage2_deadline_ns and now_ns <= position_ctx.stage2_deadline_ns and not _safe_bool(family_surface.get("resume_support"), False):
                    return "proof_failure_exit"
            elif family_id == N.STRATEGY_FAMILY_MISR:
                if not (_safe_bool(family_surface.get("hold_proof"), False) and _safe_bool(family_surface.get("reversal_impulse"), False)):
                    return "proof_failure_exit"
            elif family_id == N.STRATEGY_FAMILY_MISO:
                if not _safe_bool(family_surface.get("aggressive_flow"), False):
                    return "proof_failure_exit"
                if _safe_bool(family_surface.get("futures_contradiction_veto"), False):
                    return "proof_failure_exit"
            if response_eff > 0.0 and response_eff < DEFAULT_PROOF_MIN_RESPONSE:
                return "proof_failure_exit"
        return None

    def _divergence_exit_reason(self, *, position_ctx: OpenPositionContext, family_surface: Mapping[str, Any], option_features: Mapping[str, Any]) -> str | None:
        response_eff = _safe_float(option_features.get("response_efficiency"), _safe_float(family_surface.get("response_efficiency"), 0.0))
        fut_delta = _safe_float(_nested_get(family_surface, "futures_features", "delta_3", default=0.0), 0.0)
        opt_delta = _safe_float(option_features.get("delta_3"), 0.0)
        if position_ctx.branch_id == N.BRANCH_CALL and fut_delta > 0.0 and opt_delta <= 0.0 and response_eff < DEFAULT_DIVERGENCE_RESPONSE_FLOOR:
            return "futures_option_divergence_exit"
        if position_ctx.branch_id == N.BRANCH_PUT and fut_delta < 0.0 and opt_delta <= 0.0 and response_eff < DEFAULT_DIVERGENCE_RESPONSE_FLOOR:
            return "futures_option_divergence_exit"
        return None

    def _absorption_exit_reason(self, *, position_ctx: OpenPositionContext, family_surface: Mapping[str, Any], option_features: Mapping[str, Any]) -> str | None:
        response_eff = _safe_float(option_features.get("response_efficiency"), _safe_float(family_surface.get("response_efficiency"), 0.0))
        fut_ofi = _safe_float(_nested_get(family_surface, "futures_features", "weighted_ofi_persist", default=0.5), 0.5)
        if position_ctx.branch_id == N.BRANCH_CALL and fut_ofi >= DEFAULT_ABSORPTION_OFI_BULL and response_eff < DEFAULT_ABSORPTION_RESPONSE_FLOOR:
            return "absorption_under_response_exit"
        if position_ctx.branch_id == N.BRANCH_PUT and fut_ofi <= DEFAULT_ABSORPTION_OFI_BEAR and response_eff < DEFAULT_ABSORPTION_RESPONSE_FLOOR:
            return "absorption_under_response_exit"
        return None

    def _liquidity_exit_reason(
        self,
        *,
        position_ctx: OpenPositionContext,
        option_features: Mapping[str, Any],
    ) -> str | None:
        family_id = position_ctx.family_id
        branch_id = position_ctx.branch_id
        runtime_mode = position_ctx.strategy_runtime_mode or position_ctx.family_runtime_mode

        spread_ratio = _safe_float(option_features.get("spread_ratio"), 0.0)
        depth_total = _safe_int(option_features.get("depth_total"), 0)

        spread_exit = max(self._spread_max(family_id, branch_id, runtime_mode) + 0.20, 1.80)
        if family_id == N.STRATEGY_FAMILY_MISO:
            spread_exit = max(spread_exit, 1.90)

        depth_floor = max(1, int(self._depth_min(family_id, branch_id, runtime_mode) * 0.60))

        if spread_ratio > spread_exit:
            return "liquidity_exit"
        if depth_total < depth_floor:
            return "liquidity_exit"
        return None

    def _momentum_fade_reason(
        self,
        *,
        position_ctx: OpenPositionContext,
        family_surface: Mapping[str, Any],
        option_features: Mapping[str, Any],
    ) -> str | None:
        fut_velocity_ratio = _safe_float(
            _nested_get(family_surface, "futures_features", "velocity_ratio", default=0.0),
            0.0,
        )
        fut_velocity = _safe_float(
            _nested_get(family_surface, "futures_features", "velocity", default=0.0),
            0.0,
        )
        opt_delta = _safe_float(option_features.get("delta_3"), 0.0)
        imbalance = _safe_float(
            option_features.get("weighted_ofi_persist"),
            _safe_float(option_features.get("imbalance_persistence"), 0.5),
        )

        if fut_velocity_ratio >= DEFAULT_MOMENTUM_FADE_RATIO:
            return None

        if position_ctx.branch_id == N.BRANCH_CALL:
            if fut_velocity <= 0.0 or opt_delta <= 0.0 or imbalance < 0.50:
                return "momentum_fade_exit"
        elif position_ctx.branch_id == N.BRANCH_PUT:
            if fut_velocity >= 0.0 or opt_delta >= 0.0 or imbalance > 0.50:
                return "momentum_fade_exit"

        return None

    def _session_end_exit_reason(self, *, family_id: str | None, branch_id: str | None, now_ns: int) -> str | None:
        try:
            tz = ZoneInfo("Asia/Kolkata")
        except Exception:
            return None
        dt = datetime.fromtimestamp(now_ns / 1_000_000_000, tz=tz)
        hhmm = int(dt.strftime("%H%M"))
        cutoff = int(self._session_end_flatten_hhmm(family_id, branch_id))
        if hhmm >= cutoff:
            return "session_end_flatten_exit"
        return None

    def _large_counter_trade_exit_reason(self, *, family_surface: Mapping[str, Any]) -> str | None:
        if _safe_bool(family_surface.get("large_counter_trade"), False):
            return "large_counter_trade_exit"
        qty = _safe_float(family_surface.get("inferred_counter_trade_qty"), 0.0)
        threshold = DEFAULT_MISO_LARGE_COUNTER_QTY
        if threshold > 0.0 and qty >= threshold:
            return "large_counter_trade_exit"
        return None

    def _evaluate_exit_reason(
        self,
        *,
        position: PositionView,
        position_ctx: OpenPositionContext,
        surface: Mapping[str, Any],
        now_ns: int,
        current_price: float,
        target_points: float,
        stop_points: float,
        open_profit: float,
        highest_profit: float,
        highest_profit_ts_ns: int,
        profit_protection_active: bool,
    ) -> str | None:
        option_features = surface["option_features"]
        family_surface = surface["family_surface"]
        family_id = position_ctx.family_id or _safe_str(surface.get("family_id"))
        branch_id = position_ctx.branch_id or _safe_str(surface.get("branch_id"))
        regime = position_ctx.regime or _safe_str(family_surface.get("regime"), "NORMAL")

        def hard_stop() -> str | None:
            tick_size = max(_safe_float(option_features.get("tick_size"), 0.0), 0.05)
            if current_price <= (position.avg_price - stop_points - (tick_size * DEFAULT_HARD_STOP_BUFFER_TICKS)):
                return "hard_stop"
            return None

        def hard_target() -> str | None:
            tick_size = max(_safe_float(option_features.get("tick_size"), 0.0), 0.05)
            if current_price >= (position.avg_price + target_points + (tick_size * DEFAULT_HARD_TARGET_BUFFER_TICKS)):
                return "hard_target"
            return None

        def feed_failure() -> str | None:
            age_ms = _safe_int(option_features.get("age_ms"), 0)
            if age_ms > 2_000:
                return "feed_failure_exit"
            return None

        def disaster_stop() -> str | None:
            if family_id == N.STRATEGY_FAMILY_MISO and current_price <= (position.avg_price - DEFAULT_MISO_DISASTER_STOP_POINTS):
                return "disaster_stop_exit"
            return None

        def breakout_failure() -> str | None:
            if family_id == N.STRATEGY_FAMILY_MISB:
                if not _safe_bool(family_surface.get("breakout_trigger"), False):
                    return "breakout_failure_exit"
                if not _safe_bool(family_surface.get("breakout_acceptance"), False):
                    return "breakout_failure_exit"
            elif family_id == N.STRATEGY_FAMILY_MISC:
                if not _safe_bool(family_surface.get("breakout_trigger"), False):
                    return "breakout_retest_failure_exit"
                if not _safe_bool(family_surface.get("resume_support"), False):
                    return "breakout_retest_failure_exit"
            elif family_id == N.STRATEGY_FAMILY_MISR:
                if not _safe_bool(family_surface.get("range_reentry"), False):
                    return "breakout_failure_exit"
                if not _safe_bool(family_surface.get("fake_break"), False):
                    return "breakout_failure_exit"
            return None

        def proof_failure() -> str | None:
            return self._proof_failure_reason(position_ctx=position_ctx, family_surface=family_surface, option_features=option_features, now_ns=now_ns)

        def divergence() -> str | None:
            return self._divergence_exit_reason(position_ctx=position_ctx, family_surface=family_surface, option_features=option_features)

        def absorption() -> str | None:
            return self._absorption_exit_reason(position_ctx=position_ctx, family_surface=family_surface, option_features=option_features)

        def liquidity() -> str | None:
            return self._liquidity_exit_reason(position_ctx=position_ctx, option_features=option_features)

        def momentum_fade() -> str | None:
            return self._momentum_fade_reason(position_ctx=position_ctx, family_surface=family_surface, option_features=option_features)

        def profit_stall() -> str | None:
            if profit_protection_active and (now_ns - highest_profit_ts_ns) >= _cooldown_ns(DEFAULT_PROFIT_STALL_SEC) and open_profit >= (DEFAULT_PROFIT_PROTECT_TRIGGER * target_points):
                return "profit_stall"
            return None

        def time_stall() -> str | None:
            entry_ts_ns = position.entry_ts_ns or now_ns
            if (now_ns - entry_ts_ns) >= _cooldown_ns(self._time_stall_sec(family_id, branch_id, regime)) and open_profit < max(1.0, target_points * 0.4):
                return "time_stall"
            return None

        def early_stall() -> str | None:
            entry_ts_ns = position.entry_ts_ns or now_ns
            if family_id == N.STRATEGY_FAMILY_MISO and (now_ns - entry_ts_ns) >= _cooldown_ns(DEFAULT_EARLY_STALL_SEC) and open_profit <= 0.0:
                return "early_stall_exit"
            return None

        def max_hold() -> str | None:
            entry_ts_ns = position.entry_ts_ns or now_ns
            if (now_ns - entry_ts_ns) >= _cooldown_ns(self._max_hold_sec(family_id, branch_id, regime)):
                return "max_hold_exit"
            return None

        def microstructure_failure() -> str | None:
            if family_id != N.STRATEGY_FAMILY_MISO:
                return None
            if _safe_bool(family_surface.get("queue_reload_veto"), False):
                return "microstructure_failure_exit"
            if _safe_bool(family_surface.get("futures_contradiction_veto"), False):
                return "microstructure_failure_exit"
            if not _safe_bool(family_surface.get("aggressive_flow"), False):
                return "microstructure_failure_exit"
            tape_speed = _safe_float(family_surface.get("tape_speed"), 0.0)
            if tape_speed < DEFAULT_MISO_TAPE_SPEED_FAIL:
                return "microstructure_failure_exit"
            imbalance = _safe_float(family_surface.get("imbalance_persistence"), 0.5)
            if branch_id == N.BRANCH_CALL and imbalance < DEFAULT_MISO_IMBALANCE_FAIL_BULL:
                return "microstructure_failure_exit"
            if branch_id == N.BRANCH_PUT and imbalance > DEFAULT_MISO_IMBALANCE_FAIL_BEAR:
                return "microstructure_failure_exit"
            return None

        if family_id == N.STRATEGY_FAMILY_MISO:
            ordered_checks = (
                lambda: self._session_end_exit_reason(family_id=family_id, branch_id=branch_id, now_ns=now_ns),
                feed_failure,
                disaster_stop,
                hard_stop,
                hard_target,
                lambda: self._large_counter_trade_exit_reason(family_surface=family_surface),
                microstructure_failure,
                liquidity,
                early_stall,
                max_hold,
            )
        elif family_id == N.STRATEGY_FAMILY_MISB:
            ordered_checks = (
                lambda: self._session_end_exit_reason(family_id=family_id, branch_id=branch_id, now_ns=now_ns),
                feed_failure,
                hard_stop,
                hard_target,
                breakout_failure,
                proof_failure,
                divergence,
                absorption,
                momentum_fade,
                liquidity,
                profit_stall,
                time_stall,
                max_hold,
            )
        elif family_id == N.STRATEGY_FAMILY_MISC:
            ordered_checks = (
                lambda: self._session_end_exit_reason(family_id=family_id, branch_id=branch_id, now_ns=now_ns),
                feed_failure,
                hard_stop,
                hard_target,
                breakout_failure,
                proof_failure,
                divergence,
                absorption,
                momentum_fade,
                liquidity,
                profit_stall,
                time_stall,
                max_hold,
            )
        elif family_id == N.STRATEGY_FAMILY_MISR:
            ordered_checks = (
                lambda: self._session_end_exit_reason(family_id=family_id, branch_id=branch_id, now_ns=now_ns),
                feed_failure,
                hard_stop,
                hard_target,
                breakout_failure,
                proof_failure,
                divergence,
                absorption,
                momentum_fade,
                liquidity,
                profit_stall,
                time_stall,
                max_hold,
            )
        else:
            ordered_checks = (
                lambda: self._session_end_exit_reason(family_id=family_id, branch_id=branch_id, now_ns=now_ns),
                feed_failure,
                hard_stop,
                hard_target,
                proof_failure,
                divergence,
                absorption,
                momentum_fade,
                liquidity,
                profit_stall,
                time_stall,
                max_hold,
            )

        for check in ordered_checks:
            reason = check()
            if reason is not None:
                return reason

        if profit_protection_active:
            floor = highest_profit * (1.0 - DEFAULT_PROFIT_RETRACE)
            if open_profit < floor:
                return "profit_protection"

        return None


    def _build_entry_decision(self, *, candidate: Candidate, setup_id: str, now_ns: int, quantity_lots: int) -> StrategyDecision:
        proof_deadline_ns = now_ns + _cooldown_ns(self._proof_window_sec(candidate.family_id, candidate.branch_id))
        stage1_deadline_ns = proof_deadline_ns
        stage2_deadline_ns = now_ns + _cooldown_ns(self._stage2_window_sec(candidate.family_id, candidate.branch_id))
        current_leg_id = self.machine.current_leg_id
        primary_entry_done = self.machine.primary_entry_done_in_current_leg
        reentry_count = self.machine.reentry_count_in_current_leg
        if current_leg_id is None or self.machine.current_leg_family_id != candidate.family_id or self.machine.current_leg_branch_id != candidate.branch_id or not primary_entry_done:
            current_leg_id = _new_id(f"leg-{candidate.family_id.lower()}-{candidate.branch_id.lower()}")
            primary_entry_done = False
            reentry_count = 0
        else:
            reentry_count += 1

        stop_plan = StopPlan(
            stop_points=candidate.stop_points,
            adverse_exit_seconds=20,
            time_stop_seconds=int(self._time_stall_sec(candidate.family_id, candidate.branch_id, _safe_str(candidate.metadata.get("regime"), "NORMAL"))),
        )
        target_plan = TargetPlan(
            target_points=candidate.target_points,
            trail_after_points=(candidate.target_points * DEFAULT_PROFIT_PROTECT_TRIGGER),
            trail_step_points=max(candidate.tick_size, candidate.target_points * 0.10),
        )
        self._transition(
            InternalState.ENTRY_PENDING,
            now_ns,
            "entry_decision_emitted",
            armed_setup=None,
        )
        self.machine = RuntimeMachine(
            state=self.machine.state,
            updated_ts_ns=self.machine.updated_ts_ns,
            reason_code=self.machine.reason_code,
            cooldown_until_ns=self.machine.cooldown_until_ns,
            wait_until_ns=self.machine.wait_until_ns,
            armed_setup=self.machine.armed_setup,
            last_consumed_burst_id=candidate.burst_event_id or self.machine.last_consumed_burst_id,
            last_consumed_trap_id=candidate.trap_event_id or self.machine.last_consumed_trap_id,
            current_leg_id=current_leg_id,
            current_leg_family_id=candidate.family_id,
            current_leg_branch_id=candidate.branch_id,
            primary_entry_done_in_current_leg=self.machine.primary_entry_done_in_current_leg,
            reentry_count_in_current_leg=self.machine.reentry_count_in_current_leg,
            last_exit_reason=self.machine.last_exit_reason,
            last_exit_pnl_points=self.machine.last_exit_pnl_points,
            last_exit_fut_price=self.machine.last_exit_fut_price,
            last_exit_ts_ns=self.machine.last_exit_ts_ns,
            post_exit_high_fut=self.machine.post_exit_high_fut,
            post_exit_low_fut=self.machine.post_exit_low_fut,
        )
        action = N.ACTION_ENTER_CALL if candidate.branch_id == N.BRANCH_CALL else N.ACTION_ENTER_PUT
        lots = max(1, quantity_lots)
        return StrategyDecision(
            decision_id=_new_id("dec"),
            ts_event_ns=now_ns,
            ts_expiry_ns=now_ns + (self.pending_wait_ms * 1_000_000),
            action=action,
            side=candidate.side,
            position_effect=N.POSITION_EFFECT_OPEN,
            quantity_lots=lots,
            instrument_key=candidate.instrument_key,
            strategy_family_id=candidate.family_id,
            doctrine_id=candidate.doctrine_id,
            branch_id=candidate.branch_id,
            family_runtime_mode=candidate.family_runtime_mode,
            strategy_runtime_mode=candidate.strategy_runtime_mode,
            source_event_id=candidate.source_event_id,
            trap_event_id=candidate.trap_event_id,
            burst_event_id=candidate.burst_event_id,
            active_futures_provider_id=candidate.active_futures_provider_id,
            active_selected_option_provider_id=candidate.active_selected_option_provider_id,
            active_option_context_provider_id=candidate.active_option_context_provider_id,
            entry_mode=_normalize_entry_mode(candidate.entry_mode),
            strategy_mode=BRANCH_TO_STRATEGY_MODE.get(candidate.branch_id, N.STRATEGY_AUTO),
            system_state=N.STATE_ENTRY_PENDING,
            explain=" -> ".join(candidate.reason_chain),
            blocker_code=None,
            blocker_message=None,
            stop_plan=stop_plan,
            target_plan=target_plan,
            metadata={
                "reason_code": _safe_str(candidate.reason_chain[-1]) if candidate.reason_chain else "entry_candidate",
                "state_before": InternalState.CONFIRMING.value,
                "state_after": InternalState.ENTRY_PENDING.value,
                "confidence": candidate.score,
                "option_symbol": candidate.option_symbol,
                "option_token": candidate.instrument_token,
                "qty_lots": lots,
                "strike": candidate.strike,
                "target_points": candidate.target_points,
                "stop_points": candidate.stop_points,
                "setup_id": setup_id,
                "current_leg_id": current_leg_id,
                "primary_entry_done_in_current_leg": True,
                "reentry_count_in_current_leg": reentry_count,
                "proof_deadline_ns": proof_deadline_ns,
                "stage1_deadline_ns": stage1_deadline_ns,
                "stage2_deadline_ns": stage2_deadline_ns,
                "regime": _safe_str(candidate.metadata.get("regime")),
                "fut_ltp": candidate.metadata.get("fut_ltp"),
                "surface_kind": candidate.metadata.get("surface_kind"),
                "impact_fraction": candidate.metadata.get("impact_fraction"),
            },
        )

    def _build_exit_decision(
        self,
        *,
        position: PositionView,
        now_ns: int,
        reason: str,
        surface: Mapping[str, Any] | None,
        extra_meta: Mapping[str, Any] | None = None,
    ) -> StrategyDecision:
        position_ctx = self._position_context(position)
        side = N.SIDE_CALL if position.position_side == N.POSITION_SIDE_LONG_CALL else N.SIDE_PUT
        pnl_points = _safe_float(_nested_get(extra_meta or {}, "open_profit", default=0.0), 0.0)
        cooldown_sec = self._route_cooldown_sec(position_ctx.family_id, position_ctx.branch_id, position_ctx.regime, reason, pnl_points)
        self._transition(InternalState.EXIT_PENDING, now_ns, reason)
        self.machine = RuntimeMachine(
            state=self.machine.state,
            updated_ts_ns=self.machine.updated_ts_ns,
            reason_code=self.machine.reason_code,
            cooldown_until_ns=now_ns + _cooldown_ns(cooldown_sec),
            wait_until_ns=self.machine.wait_until_ns,
            armed_setup=self.machine.armed_setup,
            last_consumed_burst_id=self.machine.last_consumed_burst_id,
            last_consumed_trap_id=self.machine.last_consumed_trap_id,
            current_leg_id=self.machine.current_leg_id or position_ctx.current_leg_id,
            current_leg_family_id=position_ctx.family_id or self.machine.current_leg_family_id,
            current_leg_branch_id=position_ctx.branch_id or self.machine.current_leg_branch_id,
            primary_entry_done_in_current_leg=position_ctx.primary_entry_done_in_current_leg or self.machine.primary_entry_done_in_current_leg,
            reentry_count_in_current_leg=position_ctx.reentry_count_in_current_leg or self.machine.reentry_count_in_current_leg,
            last_exit_reason=reason,
            last_exit_pnl_points=pnl_points,
            last_exit_fut_price=position_ctx.entry_fut_price,
            last_exit_ts_ns=now_ns,
            post_exit_high_fut=position_ctx.post_exit_high_fut,
            post_exit_low_fut=position_ctx.post_exit_low_fut,
        )
        metadata = {
            "reason_code": reason,
            "state_before": InternalState.POSITION_OPEN.value,
            "state_after": InternalState.EXIT_PENDING.value,
            "position_side": position.position_side,
            "qty_lots": position.qty_lots,
            "avg_price": position.avg_price,
            "entry_mode": _normalize_entry_mode(position.entry_mode),
            "option_symbol": position.entry_option_symbol,
            "option_token": position.entry_option_token,
            "family_id": position_ctx.family_id,
            "doctrine_id": position_ctx.doctrine_id,
            "branch_id": position_ctx.branch_id,
            "setup_id": position_ctx.setup_id,
            "current_leg_id": position_ctx.current_leg_id or self.machine.current_leg_id,
            "reentry_count_in_current_leg": position_ctx.reentry_count_in_current_leg,
            "last_exit_pnl_points": pnl_points,
            "cooldown_sec": cooldown_sec,
            "regime": position_ctx.regime,
        }
        if extra_meta:
            metadata.update(dict(extra_meta))
        return StrategyDecision(
            decision_id=_new_id("dec"),
            ts_event_ns=now_ns,
            ts_expiry_ns=now_ns + (self.pending_wait_ms * 1_000_000),
            action=N.ACTION_EXIT,
            side=side,
            position_effect=N.POSITION_EFFECT_FLATTEN,
            quantity_lots=max(0, position.qty_lots),
            instrument_key=(position.entry_option_token or None),
            strategy_family_id=position_ctx.family_id,
            doctrine_id=position_ctx.doctrine_id,
            branch_id=position_ctx.branch_id,
            family_runtime_mode=position_ctx.family_runtime_mode,
            strategy_runtime_mode=position_ctx.strategy_runtime_mode,
            source_event_id=position_ctx.source_event_id,
            trap_event_id=position_ctx.trap_event_id,
            burst_event_id=position_ctx.burst_event_id,
            entry_mode=_normalize_entry_mode(position.entry_mode),
            strategy_mode=BRANCH_TO_STRATEGY_MODE.get(position_ctx.branch_id or (N.BRANCH_CALL if side == N.SIDE_CALL else N.BRANCH_PUT), N.STRATEGY_AUTO),
            system_state=N.STATE_EXIT_PENDING,
            explain=reason,
            blocker_code=None,
            blocker_message=None,
            stop_plan=StopPlan(stop_price=None, stop_points=None, time_stop_seconds=None, adverse_exit_seconds=None),
            target_plan=TargetPlan(target_price=None, target_points=None, trail_after_points=None, trail_step_points=None),
            metadata=metadata,
        )

    def _build_hold_decision(
        self,
        *,
        now_ns: int,
        reason: str,
        side: str,
        family_id: str | None = None,
        doctrine_id: str | None = None,
        branch_id: str | None = None,
        family_runtime_mode: str | None = None,
        strategy_runtime_mode: str | None = None,
        extra_meta: Mapping[str, Any] | None = None,
    ) -> StrategyDecision:
        metadata = {"reason_code": reason}
        if extra_meta:
            metadata.update(dict(extra_meta))
        return StrategyDecision(
            decision_id=_new_id("dec"),
            ts_event_ns=now_ns,
            ts_expiry_ns=None,
            action=N.ACTION_HOLD,
            side=side,
            position_effect=N.POSITION_EFFECT_NONE,
            quantity_lots=0,
            instrument_key=None,
            strategy_family_id=family_id,
            doctrine_id=doctrine_id,
            branch_id=branch_id,
            family_runtime_mode=family_runtime_mode,
            strategy_runtime_mode=strategy_runtime_mode,
            entry_mode=N.ENTRY_MODE_UNKNOWN,
            strategy_mode=(BRANCH_TO_STRATEGY_MODE.get(branch_id, N.STRATEGY_AUTO) if branch_id is not None else N.STRATEGY_AUTO),
            system_state=_state_to_wire(self.machine.state),
            explain=reason,
            blocker_code=reason,
            blocker_message=reason,
            stop_plan=None,
            target_plan=None,
            metadata=metadata,
        )

    def _position_context(self, position: PositionView) -> OpenPositionContext:
        meta = self._position_meta(position)
        return OpenPositionContext(
            family_id=_safe_str(meta.get("family_id")) or None,
            doctrine_id=_safe_str(meta.get("doctrine_id")) or None,
            branch_id=_safe_str(meta.get("branch_id")) or None,
            strategy_runtime_mode=_safe_str(meta.get("strategy_runtime_mode")) or None,
            family_runtime_mode=_safe_str(meta.get("family_runtime_mode")) or None,
            source_event_id=_safe_str(meta.get("source_event_id")) or None,
            trap_event_id=_safe_str(meta.get("trap_event_id")) or None,
            burst_event_id=_safe_str(meta.get("burst_event_id")) or None,
            target_points=(None if meta.get("target_points") in (None, "") else _safe_float(meta.get("target_points"), 0.0)),
            stop_points=(None if meta.get("stop_points") in (None, "") else _safe_float(meta.get("stop_points"), 0.0)),
            setup_id=_safe_str(meta.get("setup_id")) or None,
            regime=_safe_str(meta.get("regime")) or None,
            current_leg_id=_safe_str(meta.get("current_leg_id")) or None,
            primary_entry_done_in_current_leg=_safe_bool(meta.get("primary_entry_done_in_current_leg"), False),
            reentry_count_in_current_leg=_safe_int(meta.get("reentry_count_in_current_leg"), 0),
            last_exit_reason=_safe_str(meta.get("last_exit_reason")) or None,
            last_exit_pnl_points=_safe_float(meta.get("last_exit_pnl_points"), 0.0),
            last_exit_fut_price=(None if meta.get("last_exit_fut_price") in (None, "") else _safe_float(meta.get("last_exit_fut_price"), 0.0)),
            last_exit_ts_ns=_safe_int(meta.get("last_exit_ts_ns"), 0),
            post_exit_high_fut=(None if meta.get("post_exit_high_fut") in (None, "") else _safe_float(meta.get("post_exit_high_fut"), 0.0)),
            post_exit_low_fut=(None if meta.get("post_exit_low_fut") in (None, "") else _safe_float(meta.get("post_exit_low_fut"), 0.0)),
            entry_fut_price=(None if meta.get("fut_ltp") in (None, "") else _safe_float(meta.get("fut_ltp"), 0.0)),
            proof_deadline_ns=_safe_int(meta.get("proof_deadline_ns"), 0),
            stage1_deadline_ns=_safe_int(meta.get("stage1_deadline_ns"), 0),
            stage2_deadline_ns=_safe_int(meta.get("stage2_deadline_ns"), 0),
            highest_profit=_safe_float(meta.get("highest_profit"), 0.0),
            highest_profit_ts_ns=_safe_int(meta.get("highest_profit_ts_ns"), 0),
            profit_protection_active=_safe_bool(meta.get("profit_protection_active"), False),
        )

    @staticmethod
    def _position_meta(position: PositionView) -> dict[str, Any]:
        raw = position.meta_json
        if not raw:
            return {}
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                return obj
        except Exception:
            return {}
        return {}

    def _default_target_points(self, family_id: str | None, branch_id: str | None, option_price: float) -> float:
        lookup_branch = branch_id or N.BRANCH_CALL
        if family_id == N.STRATEGY_FAMILY_MISO:
            default = MISO_TARGET_POINTS
            return _safe_float(self._param(family_id, lookup_branch, "target_points", default), default)
        default = _clamp(option_price * self.target_pct, DEFAULT_MIN_TARGET_POINTS, DEFAULT_MAX_TARGET_POINTS)
        return _safe_float(self._param(family_id, lookup_branch, "target_points", default), default)

    def _default_stop_points(self, family_id: str | None, branch_id: str | None, option_price: float) -> float:
        lookup_branch = branch_id or N.BRANCH_CALL
        if family_id == N.STRATEGY_FAMILY_MISO:
            default = MISO_STOP_POINTS
            return _safe_float(self._param(family_id, lookup_branch, "stop_points", default), default)
        default = _clamp(option_price * self.stop_pct, DEFAULT_MIN_STOP_POINTS, DEFAULT_MAX_STOP_POINTS)
        return _safe_float(self._param(family_id, lookup_branch, "stop_points", default), default)

    def _transition(
        self,
        state: InternalState,
        now_ns: int,
        reason: str,
        *,
        cooldown_until_ns: int | None = None,
        wait_until_ns: int | None = None,
        armed_setup: ArmedSetup | None | object = ...,  # sentinel = preserve
    ) -> None:
        current_armed = self.machine.armed_setup if armed_setup is ... else armed_setup
        current_cooldown = self.machine.cooldown_until_ns if cooldown_until_ns is None else cooldown_until_ns
        current_wait = self.machine.wait_until_ns if wait_until_ns is None else wait_until_ns
        self.machine = RuntimeMachine(
            state=state,
            updated_ts_ns=now_ns,
            reason_code=reason,
            cooldown_until_ns=current_cooldown,
            wait_until_ns=current_wait,
            armed_setup=current_armed,
            last_consumed_burst_id=self.machine.last_consumed_burst_id,
            last_consumed_trap_id=self.machine.last_consumed_trap_id,
            current_leg_id=self.machine.current_leg_id,
            current_leg_family_id=self.machine.current_leg_family_id,
            current_leg_branch_id=self.machine.current_leg_branch_id,
            primary_entry_done_in_current_leg=self.machine.primary_entry_done_in_current_leg,
            reentry_count_in_current_leg=self.machine.reentry_count_in_current_leg,
            last_exit_reason=self.machine.last_exit_reason,
            last_exit_pnl_points=self.machine.last_exit_pnl_points,
            last_exit_fut_price=self.machine.last_exit_fut_price,
            last_exit_ts_ns=self.machine.last_exit_ts_ns,
            post_exit_high_fut=self.machine.post_exit_high_fut,
            post_exit_low_fut=self.machine.post_exit_low_fut,
        )
        self.log.info("strategy_transition state=%s reason=%s", state.value, reason)



# =============================================================================
# Service wrapper
# =============================================================================


class StrategyService:
    def __init__(
        self,
        *,
        redis_client: Any,
        clock: Any,
        shutdown: Any,
        instance_id: str,
        settings: AppSettings,
        logger: logging.Logger | None = None,
    ) -> None:
        self.redis = redis_client
        self.clock = clock
        self.shutdown = shutdown
        self.instance_id = instance_id
        self.settings = settings
        self.log = logger or LOGGER.getChild("StrategyService")

        self.poll_interval_s = max(_safe_int(_nested_get(settings, "redis", "xread_block_ms", default=100), 100), 10) / 1000.0
        self.target_pct = _safe_float(_nested_get(settings, "strategy", "target_pct", default=DEFAULT_TARGET_PCT), DEFAULT_TARGET_PCT)
        self.stop_pct = _safe_float(_nested_get(settings, "strategy", "stop_pct", default=DEFAULT_STOP_PCT), DEFAULT_STOP_PCT)
        self.pending_wait_ms = _safe_int(_nested_get(settings, "strategy", "pending_wait_ms", default=DEFAULT_PENDING_WAIT_MS), DEFAULT_PENDING_WAIT_MS)
        self.confirmation_timeout_ms = _safe_int(_nested_get(settings, "strategy", "confirmation_timeout_ms", default=DEFAULT_CONFIRMATION_TIMEOUT_MS), DEFAULT_CONFIRMATION_TIMEOUT_MS)
        self.heartbeat_ttl_ms = _safe_int(_nested_get(settings, "runtime", "heartbeat_ttl_ms", default=10_000), 10_000)
        self.lock_ttl_ms = _safe_int(_nested_get(settings, "runtime", "lock_ttl_ms", default=30_000), 30_000)
        self.lock_refresh_ms = _safe_int(_nested_get(settings, "runtime", "lock_refresh_interval_ms", default=10_000), 10_000)
        self.heartbeat_refresh_ms = max(1, int(self.heartbeat_ttl_ms // 3))
        self.hold_publish_interval_ms = DEFAULT_HOLD_PUBLISH_INTERVAL_MS

        self.engine = StrategyEngine(
            logger=self.log,
            target_pct=self.target_pct,
            stop_pct=self.stop_pct,
            pending_wait_ms=self.pending_wait_ms,
            confirmation_timeout_ms=self.confirmation_timeout_ms,
        )

        self._owns_lock = False
        self._last_lock_refresh_ns = 0
        self._last_heartbeat_ns = 0
        self._last_hold_publish_ns = 0
        self._last_hold_signature: tuple[Any, ...] | None = None

        self._validate_runtime_contract()

    def _validate_runtime_contract(self) -> None:
        if self.redis is None:
            raise RuntimeError("strategy requires redis client")
        if self.clock is None or not hasattr(self.clock, "wall_time_ns"):
            raise RuntimeError("strategy requires context.clock.wall_time_ns()")
        if self.shutdown is None or not hasattr(self.shutdown, "is_set") or not hasattr(self.shutdown, "wait"):
            raise RuntimeError("strategy requires context.shutdown")
        if not self.instance_id:
            raise RuntimeError("strategy requires non-empty instance_id")
        if not RX.ping_redis(client=self.redis):
            raise RuntimeError("strategy redis ping failed during startup")

    def _now_ns(self) -> int:
        return int(self.clock.wall_time_ns())

    def _publish_heartbeat(self, *, status: str, message: str | None = None) -> None:
        RX.write_heartbeat(
            N.KEY_HEALTH_STRATEGY,
            service=N.SERVICE_STRATEGY,
            instance_id=self.instance_id,
            status=status,
            ts_event_ns=self._now_ns(),
            message=message,
            ttl_ms=self.heartbeat_ttl_ms,
            client=self.redis,
        )

    def _publish_system_health(self, *, event: str, status: str, detail: str) -> None:
        RX.xadd_fields(
            N.STREAM_SYSTEM_HEALTH,
            {
                "event_type": event,
                "service_name": N.SERVICE_STRATEGY,
                "instance_id": self.instance_id,
                "status": status,
                "detail": detail,
                "ts_ns": str(self._now_ns()),
            },
            maxlen_approx=DEFAULT_HEALTH_STREAM_MAXLEN,
            client=self.redis,
        )

    def _publish_system_error(self, *, event: str, detail: str) -> None:
        RX.xadd_fields(
            N.STREAM_SYSTEM_ERRORS,
            {
                "event_type": event,
                "service_name": N.SERVICE_STRATEGY,
                "instance_id": self.instance_id,
                "detail": detail,
                "ts_ns": str(self._now_ns()),
            },
            maxlen_approx=DEFAULT_ERROR_STREAM_MAXLEN,
            client=self.redis,
        )

    def _acquire_lock_or_die(self) -> None:
        ok = RX.acquire_lock(
            N.KEY_LOCK_STRATEGY,
            self.instance_id,
            ttl_ms=self.lock_ttl_ms,
            client=self.redis,
        )
        if not ok:
            raise RuntimeError("strategy singleton lock not acquired")
        self._owns_lock = True
        self._last_lock_refresh_ns = self._now_ns()

    def _refresh_lock_if_due(self) -> None:
        if not self._owns_lock:
            raise RuntimeError("strategy lock not owned")
        now_ns = self._now_ns()
        if (now_ns - self._last_lock_refresh_ns) < (self.lock_refresh_ms * 1_000_000):
            return
        ok = RX.refresh_lock(
            N.KEY_LOCK_STRATEGY,
            self.instance_id,
            ttl_ms=self.lock_ttl_ms,
            client=self.redis,
        )
        if not ok:
            raise RuntimeError("strategy singleton lock refresh failed")
        self._last_lock_refresh_ns = now_ns

    def _release_lock(self) -> None:
        if not self._owns_lock:
            return
        with contextlib.suppress(Exception):
            RX.release_lock(N.KEY_LOCK_STRATEGY, self.instance_id, client=self.redis)
        self._owns_lock = False

    def _fetch_feature_payload(self) -> FeaturePayloadView | None:
        raw = RX.hgetall(N.HASH_STATE_FEATURES_MME_FUT, client=self.redis)
        if not raw:
            return None
        payload_json = raw.get("payload_json")
        if not payload_json:
            return None
        try:
            obj = json.loads(payload_json)
        except Exception:
            self.log.exception("failed_to_decode_feature_payload")
            return None
        if not isinstance(obj, Mapping):
            return None
        return FeaturePayloadView(
            frame_id=_safe_str(obj.get("frame_id"), _safe_str(raw.get("frame_id"))),
            frame_ts_ns=_safe_int(obj.get("frame_ts_ns"), _safe_int(raw.get("frame_ts_ns"), 0)),
            selection_version=_safe_str(obj.get("selection_version"), _safe_str(raw.get("selection_version"))),
            readiness=(obj.get("readiness") if isinstance(obj.get("readiness"), Mapping) else {}),
            provider_surface=(obj.get("provider_surface") if isinstance(obj.get("provider_surface"), Mapping) else {}),
            family_surfaces=(obj.get("family_surfaces") if isinstance(obj.get("family_surfaces"), Mapping) else {}),
            family_frames=(obj.get("family_frames") if isinstance(obj.get("family_frames"), Mapping) else {}),
            shared_features=(obj.get("shared_features") if isinstance(obj.get("shared_features"), Mapping) else {}),
        )

    def _fetch_risk_state(self) -> RiskView:
        raw = RX.hgetall(N.HASH_STATE_RISK, client=self.redis)
        if not raw:
            return RiskView(False, False, False, False, False, 0, "", "", 1)
        return RiskView(
            veto_entries=_safe_bool(raw.get("veto_entries", "0")),
            degraded_only=_safe_bool(raw.get("degraded_only", "0")),
            force_flatten=_safe_bool(raw.get("force_flatten", "0")),
            stale=_safe_bool(raw.get("stale", "0")),
            cooldown_active=_safe_bool(raw.get("cooldown_active", "0")),
            cooldown_until_ns=_safe_int(raw.get("cooldown_until_ns", 0), 0),
            reason_code=_safe_str(raw.get("reason_code", "")),
            reason_message=_safe_str(raw.get("reason_message", "")),
            max_new_lots=max(0, _safe_int(raw.get("max_new_lots", 1), 1)),
        )

    def _fetch_execution_state(self) -> ExecutionView:
        raw = RX.hgetall(N.HASH_STATE_EXECUTION, client=self.redis)
        if not raw:
            return ExecutionView(N.EXECUTION_MODE_NORMAL, False, False, False)
        return ExecutionView(
            execution_mode=_safe_str(raw.get("execution_mode", N.EXECUTION_MODE_NORMAL), N.EXECUTION_MODE_NORMAL),
            broker_degraded=_safe_bool(raw.get("broker_degraded", "0")),
            entry_pending=_safe_bool(raw.get("entry_pending", "0")),
            exit_pending=_safe_bool(raw.get("exit_pending", "0")),
            reconciliation_lock=_safe_bool(raw.get("reconciliation_lock", raw.get("reconciliation_active", "0"))),
            unresolved_disaster_lock=_safe_bool(raw.get("unresolved_disaster_lock", raw.get("disaster_lock", "0"))),
            execution_primary_provider_id=_safe_str(raw.get("execution_primary_provider_id", raw.get("active_execution_provider_id", ""))),
            execution_primary_status=_safe_str(raw.get("execution_primary_status", raw.get("active_execution_provider_status", ""))),
            fallback_execution_provider_id=_safe_str(raw.get("fallback_execution_provider_id", "")),
            fallback_execution_status=_safe_str(raw.get("fallback_execution_status", "")),
            execution_bridge_ok=_safe_bool(raw.get("execution_bridge_ok", "0")),
        )

    def _fetch_position_state(self) -> PositionView:
        raw = RX.hgetall(N.HASH_STATE_POSITION_MME, client=self.redis)
        if not raw:
            return PositionView(False, N.POSITION_SIDE_FLAT, "", "", 0.0, 0, 0, N.ENTRY_MODE_UNKNOWN, None)
        return PositionView(
            has_position=_safe_bool(raw.get("has_position", "0")),
            position_side=_safe_str(raw.get("position_side", N.POSITION_SIDE_FLAT), N.POSITION_SIDE_FLAT),
            entry_option_symbol=_safe_str(raw.get("entry_option_symbol", "")),
            entry_option_token=_safe_str(raw.get("entry_option_token", "")),
            avg_price=_safe_float(raw.get("avg_price", 0.0), 0.0),
            qty_lots=_safe_int(raw.get("qty_lots", 0), 0),
            entry_ts_ns=_safe_int(raw.get("entry_ts_ns", 0), 0),
            entry_mode=_safe_str(raw.get("entry_mode", N.ENTRY_MODE_UNKNOWN), N.ENTRY_MODE_UNKNOWN),
            meta_json=raw.get("meta_json"),
        )

    def _should_publish_hold(self, decision: StrategyDecision, *, now_ns: int) -> bool:
        if decision.action != N.ACTION_HOLD:
            return True
        signature = (
            decision.system_state,
            decision.blocker_code,
            decision.strategy_family_id,
            decision.doctrine_id,
            decision.branch_id,
            _safe_str(_nested_get(decision.metadata, "reason_code", default="")),
        )
        if self._last_hold_signature != signature:
            self._last_hold_signature = signature
            self._last_hold_publish_ns = now_ns
            return True
        if (now_ns - self._last_hold_publish_ns) >= (self.hold_publish_interval_ms * 1_000_000):
            self._last_hold_publish_ns = now_ns
            return True
        return False

    def _publish_decision(self, decision: StrategyDecision) -> None:
        now_ns = self._now_ns()
        if not self._should_publish_hold(decision, now_ns=now_ns):
            return
        RX.xadd_fields(N.STREAM_DECISIONS_MME, _decision_to_wire(decision), client=self.redis)

    def run_once(self, *, trading_allowed: bool = True) -> StrategyDecision | None:
        payload = self._fetch_feature_payload()
        if payload is None:
            return None
        risk = self._fetch_risk_state()
        execution = self._fetch_execution_state()
        position = self._fetch_position_state()
        decision = self.engine.evaluate(
            payload=payload,
            risk=risk,
            execution=execution,
            position=position,
            now_ns=self._now_ns(),
            trading_allowed=trading_allowed,
        )
        if decision is not None:
            self._publish_decision(decision)
        return decision

    def start(self) -> int:
        self._acquire_lock_or_die()
        self._publish_heartbeat(status=N.HEALTH_STATUS_OK, message="strategy_started")
        self._publish_system_health(
            event="strategy_bootstrap_complete",
            status=N.HEALTH_STATUS_OK,
            detail="strategy_initialized",
        )

        no_feature_loops = 0
        try:
            while not self.shutdown.is_set():
                self._refresh_lock_if_due()
                try:
                    decision = self.run_once(trading_allowed=True)
                    if decision is None:
                        no_feature_loops += 1
                        status = N.HEALTH_STATUS_WARN if no_feature_loops >= DEFAULT_NO_FEATURE_WARN_AFTER_LOOPS else N.HEALTH_STATUS_OK
                        message = "strategy_waiting_for_features"
                    else:
                        no_feature_loops = 0
                        if self.engine.machine.state in {InternalState.DISABLED, InternalState.WAIT}:
                            status = N.HEALTH_STATUS_WARN
                        else:
                            status = N.HEALTH_STATUS_OK
                        message = self.engine.machine.reason_code
                    now_ns = self._now_ns()
                    if (now_ns - self._last_heartbeat_ns) >= (self.heartbeat_refresh_ms * 1_000_000):
                        self._publish_heartbeat(status=status, message=message)
                        self._last_heartbeat_ns = now_ns
                except Exception as exc:
                    self._publish_system_error(event="strategy_service_loop_error", detail=str(exc))
                    self._publish_heartbeat(status=N.HEALTH_STATUS_ERROR, message=str(exc))
                    if _safe_bool(_nested_get(self.settings, "startup", "fail_fast", default=False), False):
                        raise
                    self.log.exception("strategy_service_loop_error")
                self.shutdown.wait(self.poll_interval_s)
        finally:
            with contextlib.suppress(Exception):
                self._publish_heartbeat(status=N.HEALTH_STATUS_WARN, message="strategy_stopping")
            self._release_lock()
        return 0


# =============================================================================
# Canonical entrypoint
# =============================================================================


def run(context: Any) -> int:
    _validate_name_surface_or_die()

    settings = getattr(context, "settings", None) or get_settings()
    if not isinstance(settings, AppSettings):
        raise RuntimeError("strategy requires context.settings or get_settings() returning AppSettings")

    redis_runtime = getattr(context, "redis", None)
    redis_client = redis_runtime.sync if redis_runtime is not None and hasattr(redis_runtime, "sync") else RX.get_redis()
    shutdown = getattr(context, "shutdown", None)
    clock = getattr(context, "clock", None)
    instance_id = _safe_str(getattr(context, "instance_id", ""))

    if shutdown is None:
        raise RuntimeError("strategy requires context.shutdown")
    if clock is None:
        raise RuntimeError("strategy requires context.clock")
    if not instance_id:
        raise RuntimeError("strategy requires context.instance_id")

    service = StrategyService(
        redis_client=redis_client,
        clock=clock,
        shutdown=shutdown,
        instance_id=instance_id,
        settings=settings,
        logger=LOGGER,
    )
    return service.start()
