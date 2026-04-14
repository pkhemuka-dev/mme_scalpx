from __future__ import annotations

"""
app/mme_scalpx/services/strategy.py

ScalpX MME - deterministic CALL/PUT strategy service.

Ownership
---------
This module owns:
- deterministic state machine for the locked CALL / PUT doctrine
- futures-led signal evaluation from canonical feature frames
- regime filter gating
- confirmation logic
- canonical decision generation
- strategy-side cooldown / wait / degraded handling
- strategy heartbeat publication
- strategy singleton lock ownership
- runtime entrypoint `run(context)`

This module does NOT own:
- Redis naming or transport implementation
- broker placement / broker reconciliation
- risk truth
- execution truth
- position truth
- feature computation internals
- startup / composition logic

Frozen rules
------------
- execution is sole position truth
- risk may veto entries, never exits
- pending execution maps to WAIT, never degrade
- publish only canonical actions from core.names
- preserve entry_mode end-to-end
- no strategy mutation of execution-owned state
- replay-safe and restart-safe

Important runtime expectation
-----------------------------
features.py publishes a full serialized feature payload into
HASH_STATE_FEATURES_MME_FUT field `payload_json`.
This service reconstructs a lightweight read model from that payload.

Important schema rule
---------------------
StrategyDecision MUST follow the uploaded core.models schema:
- ts_event_ns, not ts_ns
- side must be CALL/PUT
- position_effect must be OPEN / CLOSE / REDUCE / FLATTEN / NONE
- HOLD requires position_effect NONE
- stop_plan / target_plan are model objects
- execution-specific option details are carried in metadata
"""

import contextlib
import json
import logging
from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace
from typing import Any, Final, Mapping
from uuid import uuid4

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
PREMIUM_FLOOR: Final[float] = 40.0
MIN_TARGET: Final[float] = 5.0
MAX_TARGET: Final[float] = 10.0
MIN_STOP: Final[float] = 3.0
MAX_STOP: Final[float] = 7.0

BID_DOM_THRESHOLD: Final[float] = 1.2
VELOCITY_THRESHOLD: Final[float] = 1.5
FALLBACK_VELOCITY_THRESHOLD: Final[float] = 1.7
ENTRY_CONFIRM_VEL: Final[float] = 0.7
EXIT_VEL_THRESHOLD: Final[float] = 0.5

FUT_SPREAD_MAX: Final[float] = 1.3
OPT_SPREAD_MAX: Final[float] = 1.5
SPREAD_EXIT: Final[float] = 1.8
FUT_DEPTH_MIN: Final[int] = 500
OPT_DEPTH_MIN: Final[int] = 100
DEPTH_EXIT_RATIO: Final[float] = 0.6

ENTRY_TIMEOUT_MS: Final[int] = 1_000
CONFIRM_TIMEOUT_MS: Final[int] = 2_000
TIME_STALL_SEC: Final[float] = 12.0
TIME_STALL_PROFIT: Final[float] = 2.0
PROFIT_TRIGGER: Final[float] = 0.7
PROFIT_RETRACE: Final[float] = 0.3
PROFIT_STALL_TIME_SEC: Final[float] = 3.0
COOLDOWN_SEC: Final[float] = 4.0
FEED_STALE_MS: Final[int] = 1_000
FEED_DEAD_MS: Final[int] = 2_000
SYNC_WINDOW_MS: Final[int] = 200
DELTA_MIN: Final[float] = 0.35

VELOCITY_REGIME_MIN: Final[float] = 1.5
SPREAD_REGIME_MAX: Final[float] = 1.5
NOF_FLIP_MAX_10: Final[int] = 3
REGIME_MIN_HISTORY: Final[int] = 10

DEFAULT_HEALTH_STREAM_MAXLEN: Final[int] = 10_000
DEFAULT_ERROR_STREAM_MAXLEN: Final[int] = 10_000


# =============================================================================
# Helpers
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



def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))



def _namespaceify(value: Any) -> Any:
    if isinstance(value, dict):
        return SimpleNamespace(**{k: _namespaceify(v) for k, v in value.items()})
    if isinstance(value, list):
        return [_namespaceify(v) for v in value]
    return value



def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"



def _normalize_entry_mode(value: str | None) -> str:
    valid = {
        N.ENTRY_MODE_UNKNOWN,
        N.ENTRY_MODE_ATM,
        N.ENTRY_MODE_ATM1,
        N.ENTRY_MODE_DIRECT,
        N.ENTRY_MODE_FALLBACK,
    }
    return str(value) if value in valid else N.ENTRY_MODE_UNKNOWN



def _is_long_call(side: str) -> bool:
    return str(side) == N.POSITION_SIDE_LONG_CALL



def _is_long_put(side: str) -> bool:
    return str(side) == N.POSITION_SIDE_LONG_PUT



def _decision_to_wire(decision: StrategyDecision) -> dict[str, str]:
    payload_json = _json_dumps(decision.to_dict())
    blocker_code = _safe_str(getattr(decision, "blocker_code", None))
    metadata = getattr(decision, "metadata", {}) or {}
    reason_code = blocker_code or _safe_str(metadata.get("reason_code"))
    return {
        "decision_id": decision.decision_id,
        "ts_ns": str(decision.ts_event_ns),
        "action": decision.action,
        "reason_code": reason_code,
        "entry_mode": decision.entry_mode,
        "payload_json": payload_json,
    }


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


# =============================================================================
# Strategy machine
# =============================================================================


class StrategyState(str, Enum):
    SCANNING = "SCANNING"
    SIGNAL_READY = "SIGNAL_READY"
    CONFIRMING = "CONFIRMING"
    WAIT = "WAIT"
    ENTRY_PENDING = "ENTRY_PENDING"
    POSITION_OPEN = "POSITION_OPEN"
    EXIT_PENDING = "EXIT_PENDING"
    COOLDOWN = "COOLDOWN"
    DEGRADED = "DEGRADED"


@dataclass(slots=True, frozen=True)
class Candidate:
    side: str
    position_side: str
    option_symbol: str
    option_token: str
    strike: float | None
    entry_mode: str
    fallback_mode: bool
    option_ltp: float
    option_best_ask: float
    option_best_bid: float
    option_tick_size: float
    option_depth_total: int
    target: float
    stop: float
    estimated_cost: float
    confidence: float
    fut_velocity_ratio: float
    fut_ltp: float
    signal_reason: str


@dataclass(slots=True, frozen=True)
class ArmedSignal:
    signal_id: str
    side: str
    position_side: str
    option_symbol: str
    option_token: str
    strike: float | None
    entry_mode: str
    fallback_mode: bool
    signal_reference_option_price: float
    signal_reference_fut_price: float
    signal_fut_velocity_ratio: float
    signal_reference_ts_ns: int
    confirmation_start_ts_ns: int
    confirmation_snapshots_seen: int
    option_tick_size: float
    target: float
    stop: float
    estimated_cost: float
    entry_depth_total: int
    confidence: float
    signal_reason: str


@dataclass(slots=True, frozen=True)
class RuntimeMachine:
    state: StrategyState = StrategyState.SCANNING
    updated_ts_ns: int = 0
    reason_code: str = "boot"
    cooldown_until_ns: int | None = None
    wait_until_ns: int | None = None
    armed_signal: ArmedSignal | None = None


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
    ) -> None:
        self.log = logger or LOGGER.getChild("StrategyEngine")
        self.target_pct = float(target_pct)
        self.stop_pct = float(stop_pct)
        self.pending_wait_ms = int(max(0, pending_wait_ms))
        self.machine = RuntimeMachine(updated_ts_ns=0)
        self._last_bid_dom_below_one_call = 0
        self._last_bid_dom_above_one_put = 0

    def evaluate(
        self,
        *,
        frame: Any,
        risk: RiskView,
        execution: ExecutionView,
        position: PositionView,
        now_ns: int,
        trading_allowed: bool = True,
    ) -> StrategyDecision | None:
        if position.has_position and position.position_side != N.POSITION_SIDE_FLAT:
            self._transition(StrategyState.POSITION_OPEN, now_ns, "position_open")
            return self._handle_open_position(
                frame=frame,
                risk=risk,
                execution=execution,
                position=position,
                now_ns=now_ns,
            )
        return self._handle_flat_position(
            frame=frame,
            risk=risk,
            execution=execution,
            now_ns=now_ns,
            trading_allowed=trading_allowed,
        )

    def _handle_flat_position(
        self,
        *,
        frame: Any,
        risk: RiskView,
        execution: ExecutionView,
        now_ns: int,
        trading_allowed: bool,
    ) -> StrategyDecision | None:
        if execution.broker_degraded:
            self._transition(StrategyState.DEGRADED, now_ns, "execution_broker_degraded")
            return None

        if execution.entry_pending or execution.exit_pending:
            self._transition(
                StrategyState.WAIT,
                now_ns,
                "pending_execution",
                wait_until_ns=now_ns + (self.pending_wait_ms * 1_000_000),
            )
            return None

        if self.machine.state is StrategyState.WAIT:
            if self.machine.wait_until_ns is not None and now_ns < self.machine.wait_until_ns:
                return None
            self._transition(StrategyState.SCANNING, now_ns, "wait_complete")

        if self.machine.state is StrategyState.COOLDOWN:
            if self.machine.cooldown_until_ns is not None and now_ns < self.machine.cooldown_until_ns:
                return None
            self._transition(StrategyState.SCANNING, now_ns, "cooldown_complete")

        gate_reason = self._pre_entry_gate(
            frame=frame,
            risk=risk,
            execution=execution,
            trading_allowed=trading_allowed,
            now_ns=now_ns,
        )
        if gate_reason is not None:
            if self.machine.state in {StrategyState.SIGNAL_READY, StrategyState.CONFIRMING}:
                self._transition(StrategyState.SCANNING, now_ns, gate_reason)
            return self._build_hold_decision(
                now_ns=now_ns,
                reason=gate_reason,
                side=self._hold_side_default(),
            )

        if self.machine.state in {StrategyState.SIGNAL_READY, StrategyState.CONFIRMING} and self.machine.armed_signal is not None:
            return self._confirm_signal(frame=frame, risk=risk, now_ns=now_ns)

        candidate = self._select_candidate(frame=frame)
        if candidate is None:
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="no_candidate",
                side=self._hold_side_default(),
            )

        armed = ArmedSignal(
            signal_id=_new_id("sig"),
            side=candidate.side,
            position_side=candidate.position_side,
            option_symbol=candidate.option_symbol,
            option_token=candidate.option_token,
            strike=candidate.strike,
            entry_mode=_normalize_entry_mode(candidate.entry_mode),
            fallback_mode=candidate.fallback_mode,
            signal_reference_option_price=candidate.option_ltp,
            signal_reference_fut_price=candidate.fut_ltp,
            signal_fut_velocity_ratio=candidate.fut_velocity_ratio,
            signal_reference_ts_ns=now_ns,
            confirmation_start_ts_ns=now_ns,
            confirmation_snapshots_seen=0,
            option_tick_size=candidate.option_tick_size,
            target=candidate.target,
            stop=candidate.stop,
            estimated_cost=candidate.estimated_cost,
            entry_depth_total=candidate.option_depth_total,
            confidence=candidate.confidence,
            signal_reason=candidate.signal_reason,
        )
        self._transition(StrategyState.SIGNAL_READY, now_ns, "signal_ready", armed_signal=armed)
        self._transition(StrategyState.CONFIRMING, now_ns, "confirmation_started", armed_signal=armed)
        return None

    def _pre_entry_gate(
        self,
        *,
        frame: Any,
        risk: RiskView,
        execution: ExecutionView,
        trading_allowed: bool,
        now_ns: int,
    ) -> str | None:
        if not trading_allowed:
            return "outside_trading_window"
        if execution.execution_mode in {N.EXECUTION_MODE_FATAL, N.EXECUTION_MODE_DEGRADED}:
            return "execution_mode_blocks_entry"
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
        if not self._fresh_and_synced(frame=frame):
            return "data_not_fresh_or_synced"
        if not self._regime_ok(frame=frame):
            return "regime_fail"
        return None

    def _regime_ok(self, *, frame: Any) -> bool:
        readiness = getattr(frame, "readiness", None)
        if readiness is not None and hasattr(readiness, "warmup_complete"):
            if not _safe_bool(getattr(readiness, "warmup_complete", False)):
                return False
        fut = getattr(frame, "futures", None)
        if fut is None:
            return False
        history_count = _safe_int(getattr(fut, "history_count", REGIME_MIN_HISTORY), REGIME_MIN_HISTORY)
        if history_count < REGIME_MIN_HISTORY:
            return False
        velocity_ratio = _safe_float(getattr(fut, "velocity_ratio", None), 0.0)
        spread_ratio = _safe_float(getattr(fut, "spread_ratio", None), 999.0)
        nof_flip_count_10 = _safe_int(getattr(fut, "nof_flip_count_10", None), NOF_FLIP_MAX_10 + 1)
        return (
            velocity_ratio >= VELOCITY_REGIME_MIN
            and spread_ratio <= SPREAD_REGIME_MAX
            and nof_flip_count_10 <= NOF_FLIP_MAX_10
        )

    def _fresh_and_synced(self, *, frame: Any) -> bool:
        fut = getattr(frame, "futures", None)
        if fut is None:
            return False
        if _safe_bool(getattr(fut, "valid_tick", True), True) is False:
            return False
        if _safe_bool(getattr(fut, "fresh", True), True) is False:
            return False

        readiness = getattr(frame, "readiness", None)
        if readiness is not None and hasattr(readiness, "sync_valid"):
            return _safe_bool(getattr(readiness, "sync_valid", False))

        fut_ts = _safe_int(getattr(fut, "local_ts_ns", getattr(fut, "ts_event_ns", 0)), 0)
        if fut_ts <= 0:
            return False
        for option in (
            getattr(frame, "ce_atm", None),
            getattr(frame, "ce_atm1", None),
            getattr(frame, "pe_atm", None),
            getattr(frame, "pe_atm1", None),
        ):
            if option is None:
                continue
            if _safe_bool(getattr(option, "valid_tick", True), True) is False:
                continue
            opt_ts = _safe_int(getattr(option, "local_ts_ns", getattr(option, "ts_event_ns", 0)), 0)
            if opt_ts <= 0:
                continue
            if abs(fut_ts - opt_ts) <= (SYNC_WINDOW_MS * 1_000_000):
                return True
        return False

    def _select_candidate(self, *, frame: Any) -> Candidate | None:
        candidates: list[Candidate] = []
        call = self._evaluate_side(frame=frame, side=N.SIDE_CALL)
        if call is not None:
            candidates.append(call)
        put = self._evaluate_side(frame=frame, side=N.SIDE_PUT)
        if put is not None:
            candidates.append(put)
        if not candidates:
            return None
        candidates.sort(
            key=lambda item: (
                item.confidence,
                1.0 if item.entry_mode == N.ENTRY_MODE_ATM else 0.0,
            ),
            reverse=True,
        )
        return candidates[0]

    def _evaluate_side(self, *, frame: Any, side: str) -> Candidate | None:
        fut = getattr(frame, "futures", None)
        if fut is None:
            return None

        if side == N.SIDE_CALL:
            primary_option = getattr(frame, "ce_atm", None)
            fallback_option = getattr(frame, "ce_atm1", None)
            position_side = N.POSITION_SIDE_LONG_CALL
            default_mode = N.ENTRY_MODE_ATM
            fallback_mode_name = N.ENTRY_MODE_ATM1
        else:
            primary_option = getattr(frame, "pe_atm", None)
            fallback_option = getattr(frame, "pe_atm1", None)
            position_side = N.POSITION_SIDE_LONG_PUT
            default_mode = N.ENTRY_MODE_ATM
            fallback_mode_name = N.ENTRY_MODE_ATM1

        if not self._pillar_direction(fut=fut, side=side):
            return None
        if not self._pillar_momentum(fut=fut, side=side, require_fallback_strength=False):
            return None
        if not self._pillar_liquidity(fut=fut):
            return None

        primary = self._candidate_from_option(
            fut=fut,
            option=primary_option,
            side=side,
            position_side=position_side,
            entry_mode=default_mode,
            fallback_mode=False,
        )
        if primary is not None:
            return primary

        return self._candidate_from_option(
            fut=fut,
            option=fallback_option,
            side=side,
            position_side=position_side,
            entry_mode=fallback_mode_name,
            fallback_mode=True,
        )

    def _pillar_direction(self, *, fut: Any, side: str) -> bool:
        bid_qty = _safe_float(getattr(fut, "bid_qty_5", None), 0.0)
        ask_qty = _safe_float(getattr(fut, "ask_qty_5", None), 0.0)
        nof_slope = _safe_float(getattr(fut, "nof_slope_5", None), 0.0)
        bid_dom = _safe_float(getattr(fut, "bid_dominance", None), bid_qty / max(ask_qty, EPSILON))
        ask_dom = _safe_float(getattr(fut, "ask_dominance", None), ask_qty / max(bid_qty, EPSILON))
        if side == N.SIDE_CALL:
            return bid_dom > BID_DOM_THRESHOLD and nof_slope > 0.0
        return ask_dom > BID_DOM_THRESHOLD and nof_slope < 0.0

    def _pillar_momentum(self, *, fut: Any, side: str, require_fallback_strength: bool) -> bool:
        velocity_ratio = _safe_float(getattr(fut, "velocity_ratio", None), 0.0)
        velocity = _safe_float(getattr(fut, "velocity", None), 0.0)
        threshold = FALLBACK_VELOCITY_THRESHOLD if require_fallback_strength else VELOCITY_THRESHOLD
        if velocity_ratio <= threshold:
            return False
        if side == N.SIDE_CALL:
            return velocity > 0.0 and _safe_bool(getattr(fut, "ladder_accel_call", None))
        return velocity < 0.0 and _safe_bool(getattr(fut, "ladder_accel_put", None))

    def _pillar_liquidity(self, *, fut: Any) -> bool:
        spread_ratio = _safe_float(getattr(fut, "spread_ratio", None), 999.0)
        depth_total = _safe_int(getattr(fut, "depth_total", None), 0)
        return spread_ratio <= FUT_SPREAD_MAX and depth_total >= FUT_DEPTH_MIN

    def _candidate_from_option(
        self,
        *,
        fut: Any,
        option: Any,
        side: str,
        position_side: str,
        entry_mode: str,
        fallback_mode: bool,
    ) -> Candidate | None:
        if option is None:
            return None
        if not self._option_confirmation_ok(option=option):
            return None

        premium = _safe_float(getattr(option, "ltp", None), 0.0)
        estimated_cost = max(0.05 * premium, 2.0) + 1.0
        target = _clamp(premium * self.target_pct, MIN_TARGET, MAX_TARGET)
        stop = _clamp(premium * self.stop_pct, MIN_STOP, MAX_STOP)
        if premium < PREMIUM_FLOOR or target < MIN_TARGET or target < (2.5 * estimated_cost):
            return None

        fut_ltp = _safe_float(getattr(fut, "ltp", None), 0.0)
        strike = getattr(option, "strike", None)
        strike_value = None if strike is None else _safe_float(strike, 0.0)

        if fallback_mode:
            strike_distance = abs((strike_value or 0.0) - fut_ltp)
            delta_proxy = max(0.25, 0.55 - 0.0005 * strike_distance)
            if delta_proxy < DELTA_MIN:
                return None
            if not self._pillar_momentum(fut=fut, side=side, require_fallback_strength=True):
                return None

        tick_size = _safe_float(getattr(option, "tick_size", None), 0.0)
        if tick_size <= 0.0:
            return None

        confidence = min(
            1.0,
            _safe_float(getattr(fut, "velocity_ratio", None), 0.0) / FALLBACK_VELOCITY_THRESHOLD,
        )
        if not fallback_mode:
            confidence = min(1.0, confidence + 0.05)

        return Candidate(
            side=side,
            position_side=position_side,
            option_symbol=_safe_str(getattr(option, "trading_symbol", getattr(option, "symbol", ""))),
            option_token=_safe_str(getattr(option, "instrument_token", getattr(option, "token", ""))),
            strike=strike_value,
            entry_mode=_normalize_entry_mode(entry_mode),
            fallback_mode=fallback_mode,
            option_ltp=premium,
            option_best_ask=_safe_float(getattr(option, "best_ask", None), 0.0),
            option_best_bid=_safe_float(getattr(option, "best_bid", None), 0.0),
            option_tick_size=tick_size,
            option_depth_total=_safe_int(getattr(option, "depth_total", 0), 0),
            target=target,
            stop=stop,
            estimated_cost=estimated_cost,
            confidence=confidence,
            fut_velocity_ratio=_safe_float(getattr(fut, "velocity_ratio", None), 0.0),
            fut_ltp=fut_ltp,
            signal_reason=f"{side.lower()}_{'atm1' if fallback_mode else 'atm'}_qualified",
        )

    def _option_confirmation_ok(self, *, option: Any) -> bool:
        if _safe_bool(getattr(option, "valid_tick", True), True) is False:
            return False
        if _safe_bool(getattr(option, "fresh", True), True) is False:
            return False
        if _safe_bool(getattr(option, "sync_valid", True), True) is False:
            return False
        tick_size = _safe_float(getattr(option, "tick_size", None), 0.0)
        if tick_size <= 0.0:
            return False
        depth_total = _safe_int(getattr(option, "depth_total", 0), 0)
        spread_ratio = _safe_float(getattr(option, "spread_ratio", None), 999.0)
        delta_3 = _safe_float(getattr(option, "delta_3", None), -999.0)
        return delta_3 >= 0.0 and spread_ratio <= OPT_SPREAD_MAX and depth_total >= OPT_DEPTH_MIN

    def _confirm_signal(self, *, frame: Any, risk: RiskView, now_ns: int) -> StrategyDecision | None:
        signal = self.machine.armed_signal
        if signal is None:
            self._transition(StrategyState.SCANNING, now_ns, "missing_signal")
            return None

        if risk.force_flatten:
            self._transition(
                StrategyState.COOLDOWN,
                now_ns,
                "force_flatten_during_confirmation",
                cooldown_until_ns=now_ns + int(COOLDOWN_SEC * 1e9),
            )
            return self._build_hold_decision(now_ns=now_ns, reason="force_flatten_active", side=signal.side)

        if risk.veto_entries or risk.degraded_only or risk.stale:
            self._transition(
                StrategyState.COOLDOWN,
                now_ns,
                "risk_veto_during_confirmation",
                cooldown_until_ns=now_ns + int(COOLDOWN_SEC * 1e9),
            )
            return self._build_hold_decision(
                now_ns=now_ns,
                reason=risk.reason_code or "risk_veto",
                side=signal.side,
            )

        if (now_ns - signal.confirmation_start_ts_ns) > (CONFIRM_TIMEOUT_MS * 1_000_000):
            self._transition(
                StrategyState.COOLDOWN,
                now_ns,
                "confirmation_timeout",
                cooldown_until_ns=now_ns + int(COOLDOWN_SEC * 1e9),
            )
            return self._build_hold_decision(now_ns=now_ns, reason="confirmation_timeout", side=signal.side)

        option = self._pick_live_option_by_token(frame=frame, option_token=signal.option_token)
        fut = getattr(frame, "futures", None)
        if option is None or fut is None:
            self._transition(StrategyState.SCANNING, now_ns, "signal_leg_missing")
            return self._build_hold_decision(now_ns=now_ns, reason="signal_leg_missing", side=signal.side)

        if not self._option_confirmation_ok(option=option):
            self._transition(StrategyState.SCANNING, now_ns, "option_invalid_during_confirmation")
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="option_invalid_during_confirmation",
                side=signal.side,
            )

        live_price = _safe_float(getattr(option, "ltp", None), 0.0)
        price_drop = signal.signal_reference_option_price - live_price
        if price_drop >= (signal.option_tick_size - EPSILON):
            self._transition(StrategyState.SCANNING, now_ns, "price_drop_confirmation_fail")
            return self._build_hold_decision(now_ns=now_ns, reason="confirmation_price_drop", side=signal.side)

        if _safe_float(getattr(fut, "velocity_ratio", None), 0.0) < ENTRY_CONFIRM_VEL:
            self._transition(StrategyState.SCANNING, now_ns, "velocity_confirmation_fail")
            return self._build_hold_decision(now_ns=now_ns, reason="confirmation_velocity_fail", side=signal.side)

        seen = signal.confirmation_snapshots_seen + 1
        if seen < 2:
            updated = ArmedSignal(
                signal_id=signal.signal_id,
                side=signal.side,
                position_side=signal.position_side,
                option_symbol=signal.option_symbol,
                option_token=signal.option_token,
                strike=signal.strike,
                entry_mode=signal.entry_mode,
                fallback_mode=signal.fallback_mode,
                signal_reference_option_price=signal.signal_reference_option_price,
                signal_reference_fut_price=signal.signal_reference_fut_price,
                signal_fut_velocity_ratio=signal.signal_fut_velocity_ratio,
                signal_reference_ts_ns=signal.signal_reference_ts_ns,
                confirmation_start_ts_ns=signal.confirmation_start_ts_ns,
                confirmation_snapshots_seen=seen,
                option_tick_size=signal.option_tick_size,
                target=signal.target,
                stop=signal.stop,
                estimated_cost=signal.estimated_cost,
                entry_depth_total=signal.entry_depth_total,
                confidence=signal.confidence,
                signal_reason=signal.signal_reason,
            )
            self._transition(
                StrategyState.CONFIRMING,
                now_ns,
                "confirmation_in_progress",
                armed_signal=updated,
            )
            return None

        return self._build_entry_decision(frame=frame, signal=signal, now_ns=now_ns)

    def _build_entry_decision(self, *, frame: Any, signal: ArmedSignal, now_ns: int) -> StrategyDecision | None:
        option = self._pick_live_option_by_token(frame=frame, option_token=signal.option_token)
        if option is None:
            self._transition(StrategyState.SCANNING, now_ns, "entry_leg_missing")
            return self._build_hold_decision(now_ns=now_ns, reason="entry_leg_missing", side=signal.side)

        tick_size = _safe_float(getattr(option, "tick_size", None), 0.0)
        best_ask = _safe_float(getattr(option, "best_ask", None), 0.0)
        best_bid = _safe_float(getattr(option, "best_bid", None), 0.0)
        depth_total = _safe_int(getattr(option, "depth_total", 0), 0)
        spread_ratio = _safe_float(getattr(option, "spread_ratio", None), 999.0)
        age_ms = _safe_int(getattr(option, "age_ms", 0), 0)

        self._last_bid_dom_below_one_call = 0
        self._last_bid_dom_above_one_put = 0

        if (
            tick_size <= 0.0
            or best_ask <= 0.0
            or best_bid <= 0.0
            or depth_total < OPT_DEPTH_MIN
            or spread_ratio > OPT_SPREAD_MAX
        ):
            self._transition(
                StrategyState.COOLDOWN,
                now_ns,
                "entry_precheck_fail",
                cooldown_until_ns=now_ns + int(COOLDOWN_SEC * 1e9),
            )
            return self._build_hold_decision(now_ns=now_ns, reason="entry_precheck_fail", side=signal.side)

        if age_ms > FEED_STALE_MS:
            self._transition(
                StrategyState.COOLDOWN,
                now_ns,
                "option_stale_before_entry",
                cooldown_until_ns=now_ns + int(COOLDOWN_SEC * 1e9),
            )
            return self._build_hold_decision(now_ns=now_ns, reason="option_stale_before_entry", side=signal.side)

        if (now_ns - signal.signal_reference_ts_ns) > (CONFIRM_TIMEOUT_MS * 1_000_000):
            self._transition(
                StrategyState.COOLDOWN,
                now_ns,
                "signal_stale_before_entry",
                cooldown_until_ns=now_ns + int(COOLDOWN_SEC * 1e9),
            )
            return self._build_hold_decision(now_ns=now_ns, reason="signal_stale_before_entry", side=signal.side)

        limit_price = best_ask + tick_size
        action = N.ACTION_ENTER_CALL if signal.side == N.SIDE_CALL else N.ACTION_ENTER_PUT

        stop_plan = StopPlan(
            stop_price=max(signal.signal_reference_option_price - signal.stop, 0.0),
            adverse_exit_seconds=20,
            time_stop_seconds=int(TIME_STALL_SEC),
        )
        target_plan = TargetPlan(
            target_price=signal.signal_reference_option_price + signal.target,
            trail_after_points=signal.target * PROFIT_TRIGGER,
            trail_step_points=max(signal.option_tick_size, signal.target * 0.1),
        )

        self._transition(StrategyState.ENTRY_PENDING, now_ns, "entry_decision_emitted", armed_signal=None)
        return StrategyDecision(
            decision_id=_new_id("dec"),
            ts_event_ns=now_ns,
            ts_expiry_ns=now_ns + (ENTRY_TIMEOUT_MS * 1_000_000),
            action=action,
            side=signal.side,
            position_effect=N.POSITION_EFFECT_OPEN,
            quantity_lots=1,
            instrument_key=signal.option_token,
            entry_mode=_normalize_entry_mode(signal.entry_mode),
            strategy_mode=N.STRATEGY_AUTO,
            system_state=N.STATE_ENTRY_PENDING,
            explain=signal.signal_reason,
            blocker_code=None,
            blocker_message=None,
            stop_plan=stop_plan,
            target_plan=target_plan,
            metadata={
                "reason_code": signal.signal_reason,
                "state_before": StrategyState.CONFIRMING.value,
                "state_after": StrategyState.ENTRY_PENDING.value,
                "confidence": signal.confidence,
                "option_symbol": signal.option_symbol,
                "option_token": signal.option_token,
                "qty_lots": 1,
                "limit_price": limit_price,
                "strike": signal.strike,
                "fallback_mode": signal.fallback_mode,
                "signal_id": signal.signal_id,
                "signal_reference_option_price": signal.signal_reference_option_price,
                "signal_reference_fut_price": signal.signal_reference_fut_price,
                "signal_fut_velocity_ratio": signal.signal_fut_velocity_ratio,
                "signal_reference_ts_ns": signal.signal_reference_ts_ns,
                "entry_depth_total": signal.entry_depth_total,
                "estimated_cost": signal.estimated_cost,
            },
        )

    def _handle_open_position(
        self,
        *,
        frame: Any,
        risk: RiskView,
        execution: ExecutionView,
        position: PositionView,
        now_ns: int,
    ) -> StrategyDecision | None:
        self._transition(StrategyState.POSITION_OPEN, now_ns, "position_open")

        if execution.entry_pending or execution.exit_pending:
            self._transition(
                StrategyState.WAIT,
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
                live_price=None,
            )

        option = self._pick_live_option_for_position(frame=frame, position=position)
        if option is None:
            return self._build_exit_decision(
                position=position,
                now_ns=now_ns,
                reason="feed_death",
                live_price=None,
            )

        position_side = position.position_side
        current_price = _safe_float(getattr(option, "ltp", None), 0.0)
        entry_price = position.avg_price
        target = _clamp(entry_price * self.target_pct, MIN_TARGET, MAX_TARGET)
        stop = _clamp(entry_price * self.stop_pct, MIN_STOP, MAX_STOP)

        open_profit = current_price - entry_price
        meta = self._position_meta(position)
        highest_profit = max(_safe_float(meta.get("highest_profit"), 0.0), open_profit)
        highest_profit_ts_ns = _safe_int(meta.get("highest_profit_ts_ns"), position.entry_ts_ns or now_ns)
        if open_profit > _safe_float(meta.get("highest_profit"), 0.0) + EPSILON:
            highest_profit_ts_ns = now_ns
        profit_protection_active = _safe_bool(meta.get("profit_protection_active")) or (
            open_profit >= (PROFIT_TRIGGER * target)
        )

        exit_reason = self._evaluate_exit_reason(
            frame=frame,
            option=option,
            position=position,
            now_ns=now_ns,
            entry_price=entry_price,
            current_price=current_price,
            target=target,
            stop=stop,
            open_profit=open_profit,
            highest_profit=highest_profit,
            highest_profit_ts_ns=highest_profit_ts_ns,
            profit_protection_active=profit_protection_active,
        )
        if exit_reason is None:
            return self._build_hold_decision(
                now_ns=now_ns,
                reason="hold_open_position",
                side=N.SIDE_CALL if _is_long_call(position_side) else N.SIDE_PUT,
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
            live_price=current_price,
            extra_meta={
                "highest_profit": highest_profit,
                "highest_profit_ts_ns": highest_profit_ts_ns,
                "profit_protection_active": profit_protection_active,
            },
        )

    def _evaluate_exit_reason(
        self,
        *,
        frame: Any,
        option: Any,
        position: PositionView,
        now_ns: int,
        entry_price: float,
        current_price: float,
        target: float,
        stop: float,
        open_profit: float,
        highest_profit: float,
        highest_profit_ts_ns: int,
        profit_protection_active: bool,
    ) -> str | None:
        fut = getattr(frame, "futures", None)
        if fut is None:
            return "feed_death"

        option_ts_ns = _safe_int(getattr(option, "local_ts_ns", getattr(option, "ts_event_ns", None)), 0)
        if option_ts_ns > 0 and (now_ns - option_ts_ns) > (FEED_DEAD_MS * 1_000_000):
            return "feed_death"

        if current_price <= (entry_price - stop):
            return "hard_stop"
        if current_price >= (entry_price + target):
            return "target_hit"

        if profit_protection_active:
            floor = highest_profit * (1.0 - PROFIT_RETRACE)
            if open_profit < floor:
                return "profit_protection"

        velocity_ratio = _safe_float(getattr(fut, "velocity_ratio", None), 0.0)
        if velocity_ratio < EXIT_VEL_THRESHOLD:
            return "momentum_exit"

        bid_qty = _safe_float(getattr(fut, "bid_qty_5", None), 0.0)
        ask_qty = _safe_float(getattr(fut, "ask_qty_5", None), 0.0)
        bid_dom = _safe_float(getattr(fut, "bid_dominance", None), bid_qty / max(ask_qty, EPSILON))

        if _is_long_call(position.position_side):
            self._last_bid_dom_below_one_call = (
                self._last_bid_dom_below_one_call + 1 if bid_dom < 1.0 else 0
            )
            if self._last_bid_dom_below_one_call >= 2:
                return "momentum_exit"
        elif _is_long_put(position.position_side):
            self._last_bid_dom_above_one_put = (
                self._last_bid_dom_above_one_put + 1 if bid_dom > 1.0 else 0
            )
            if self._last_bid_dom_above_one_put >= 2:
                return "momentum_exit"

        spread_ratio = _safe_float(getattr(option, "spread_ratio", None), 0.0)
        depth_total = _safe_int(getattr(option, "depth_total", 0), 0)
        entry_depth_total = max(_safe_int(self._position_meta(position).get("entry_depth_total"), 0), 1)
        if spread_ratio > SPREAD_EXIT or depth_total < int(DEPTH_EXIT_RATIO * entry_depth_total):
            return "liquidity_exit"

        if (
            profit_protection_active
            and (now_ns - highest_profit_ts_ns) >= int(PROFIT_STALL_TIME_SEC * 1e9)
            and open_profit >= (PROFIT_TRIGGER * target)
        ):
            return "profit_stall"

        entry_ts_ns = position.entry_ts_ns or now_ns
        if (now_ns - entry_ts_ns) >= int(TIME_STALL_SEC * 1e9) and open_profit < TIME_STALL_PROFIT:
            return "time_stall"

        return None

    def _build_exit_decision(
        self,
        *,
        position: PositionView,
        now_ns: int,
        reason: str,
        live_price: float | None,
        extra_meta: Mapping[str, Any] | None = None,
    ) -> StrategyDecision:
        side = N.SIDE_CALL if _is_long_call(position.position_side) else N.SIDE_PUT
        stop_plan = StopPlan(stop_price=None, adverse_exit_seconds=None, time_stop_seconds=None)
        target_plan = TargetPlan(
            target_price=live_price,
            target_points=None,
            trail_after_points=None,
            trail_step_points=None,
        )
        self._transition(StrategyState.EXIT_PENDING, now_ns, reason)
        metadata = {
            "reason_code": reason,
            "state_before": StrategyState.POSITION_OPEN.value,
            "state_after": StrategyState.EXIT_PENDING.value,
            "position_side": position.position_side,
            "qty_lots": position.qty_lots,
            "avg_price": position.avg_price,
            "entry_mode": _normalize_entry_mode(position.entry_mode),
            "option_symbol": position.entry_option_symbol,
            "option_token": position.entry_option_token,
            "limit_price": None,
            "strike": None,
        }
        if extra_meta:
            metadata.update(dict(extra_meta))
        return StrategyDecision(
            decision_id=_new_id("dec"),
            ts_event_ns=now_ns,
            ts_expiry_ns=now_ns + (CONFIRM_TIMEOUT_MS * 1_000_000),
            action=N.ACTION_EXIT,
            side=side,
            position_effect=N.POSITION_EFFECT_FLATTEN,
            quantity_lots=max(0, position.qty_lots),
            instrument_key=position.entry_option_token or None,
            entry_mode=_normalize_entry_mode(position.entry_mode),
            strategy_mode=N.STRATEGY_AUTO,
            system_state=N.STATE_EXIT_PENDING,
            explain=reason,
            blocker_code=None,
            blocker_message=None,
            stop_plan=stop_plan,
            target_plan=target_plan,
            metadata=metadata,
        )

    def _build_hold_decision(
        self,
        *,
        now_ns: int,
        reason: str,
        side: str,
        extra_meta: Mapping[str, Any] | None = None,
    ) -> StrategyDecision:
        metadata = {"reason_code": reason}
        if extra_meta:
            metadata.update(dict(extra_meta))
        state_name = {
            StrategyState.SCANNING: N.STATE_SCANNING,
            StrategyState.SIGNAL_READY: N.STATE_SIGNAL_READY,
            StrategyState.CONFIRMING: N.STATE_CONFIRMING,
            StrategyState.ENTRY_PENDING: N.STATE_ENTRY_PENDING,
            StrategyState.POSITION_OPEN: N.STATE_POSITION_OPEN,
            StrategyState.EXIT_PENDING: N.STATE_EXIT_PENDING,
            StrategyState.COOLDOWN: N.STATE_COOLDOWN,
            StrategyState.WAIT: N.STATE_WAIT,
            StrategyState.DEGRADED: N.STATE_DISABLED,
        }.get(self.machine.state, N.STATE_IDLE)
        return StrategyDecision(
            decision_id=_new_id("dec"),
            ts_event_ns=now_ns,
            ts_expiry_ns=None,
            action=N.ACTION_HOLD,
            side=side,
            position_effect=N.POSITION_EFFECT_NONE,
            quantity_lots=0,
            instrument_key=None,
            entry_mode=N.ENTRY_MODE_UNKNOWN,
            strategy_mode=N.STRATEGY_AUTO,
            system_state=state_name,
            explain=reason,
            blocker_code=reason,
            blocker_message=reason,
            stop_plan=None,
            target_plan=None,
            metadata=metadata,
        )

    def _pick_live_option_for_position(self, *, frame: Any, position: PositionView) -> Any | None:
        token = position.entry_option_token or ""
        if token:
            picked = self._pick_live_option_by_token(frame=frame, option_token=token)
            if picked is not None:
                return picked
        if _is_long_call(position.position_side):
            return getattr(frame, "ce_atm", None) or getattr(frame, "ce_atm1", None)
        if _is_long_put(position.position_side):
            return getattr(frame, "pe_atm", None) or getattr(frame, "pe_atm1", None)
        return None

    def _pick_live_option_by_token(self, *, frame: Any, option_token: str) -> Any | None:
        for option in (
            getattr(frame, "ce_atm", None),
            getattr(frame, "ce_atm1", None),
            getattr(frame, "pe_atm", None),
            getattr(frame, "pe_atm1", None),
        ):
            if option is not None and _safe_str(
                getattr(option, "instrument_token", getattr(option, "token", ""))
            ) == _safe_str(option_token):
                return option
        return None

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

    def _hold_side_default(self) -> str:
        signal = self.machine.armed_signal
        if signal is not None and signal.side in {N.SIDE_CALL, N.SIDE_PUT}:
            return signal.side
        return N.SIDE_CALL

    def _transition(
        self,
        state: StrategyState,
        now_ns: int,
        reason: str,
        *,
        cooldown_until_ns: int | None = None,
        wait_until_ns: int | None = None,
        armed_signal: ArmedSignal | None | object = ...,  # sentinel: preserve current
    ) -> None:
        current_signal = self.machine.armed_signal if armed_signal is ... else armed_signal
        current_cooldown = self.machine.cooldown_until_ns if cooldown_until_ns is None else cooldown_until_ns
        current_wait = self.machine.wait_until_ns if wait_until_ns is None else wait_until_ns
        self.machine = RuntimeMachine(
            state=state,
            updated_ts_ns=now_ns,
            reason_code=reason,
            cooldown_until_ns=current_cooldown,
            wait_until_ns=current_wait,
            armed_signal=current_signal,
        )
        self.log.info("strategy_transition state=%s reason=%s", state.value, reason)


# =============================================================================
# Lightweight service wrapper
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

        self.poll_interval_s = max(self.settings.redis.xread_block_ms, 10) / 1000.0
        self.target_pct = float(self.settings.strategy.target_pct)
        self.stop_pct = float(self.settings.strategy.stop_pct)
        self.pending_wait_ms = int(self.settings.strategy.pending_wait_ms)
        self.heartbeat_ttl_ms = int(self.settings.runtime.heartbeat_ttl_ms)
        self.lock_ttl_ms = int(self.settings.runtime.lock_ttl_ms)
        self.lock_refresh_ms = int(self.settings.runtime.lock_refresh_interval_ms)
        self.heartbeat_refresh_ms = max(1, int(self.settings.runtime.heartbeat_ttl_ms // 3))

        self.engine = StrategyEngine(
            logger=self.log,
            target_pct=self.target_pct,
            stop_pct=self.stop_pct,
            pending_wait_ms=self.pending_wait_ms,
        )

        self._owns_lock = False
        self._last_lock_refresh_ns = 0
        self._last_heartbeat_ns = 0

        self._validate_runtime_contract()

    def _validate_runtime_contract(self) -> None:
        if self.redis is None:
            raise RuntimeError("strategy requires redis client")
        if self.clock is None or not hasattr(self.clock, "wall_time_ns"):
            raise RuntimeError("strategy requires context.clock.wall_time_ns()")
        if self.shutdown is None or not hasattr(self.shutdown, "is_set") or not hasattr(self.shutdown, "wait"):
            raise RuntimeError("strategy requires context.shutdown with is_set()/wait()")
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

    def _fetch_feature_frame(self) -> Any | None:
        raw = RX.hgetall(N.HASH_STATE_FEATURES_MME_FUT, client=self.redis)
        if not raw:
            return None
        payload_json = raw.get("payload_json")
        if not payload_json:
            return None
        try:
            return _namespaceify(json.loads(payload_json))
        except Exception:
            self.log.exception("failed_to_decode_feature_payload")
            return None

    def _fetch_risk_state(self) -> RiskView:
        raw = RX.hgetall(N.HASH_STATE_RISK, client=self.redis)
        if not raw:
            return RiskView(
                veto_entries=False,
                degraded_only=False,
                force_flatten=False,
                stale=False,
                cooldown_active=False,
                cooldown_until_ns=0,
                reason_code="",
                reason_message="",
                max_new_lots=1,
            )
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
            return ExecutionView(
                execution_mode=N.EXECUTION_MODE_NORMAL,
                broker_degraded=False,
                entry_pending=False,
                exit_pending=False,
            )
        return ExecutionView(
            execution_mode=_safe_str(raw.get("execution_mode", N.EXECUTION_MODE_NORMAL)),
            broker_degraded=_safe_bool(raw.get("broker_degraded", "0")),
            entry_pending=_safe_bool(raw.get("entry_pending", "0")),
            exit_pending=_safe_bool(raw.get("exit_pending", "0")),
        )

    def _fetch_position_state(self) -> PositionView:
        raw = RX.hgetall(N.HASH_STATE_POSITION_MME, client=self.redis)
        if not raw:
            return PositionView(
                has_position=False,
                position_side=N.POSITION_SIDE_FLAT,
                entry_option_symbol="",
                entry_option_token="",
                avg_price=0.0,
                qty_lots=0,
                entry_ts_ns=0,
                entry_mode=N.ENTRY_MODE_UNKNOWN,
                meta_json=None,
            )
        return PositionView(
            has_position=_safe_bool(raw.get("has_position", "0")),
            position_side=_safe_str(raw.get("position_side", N.POSITION_SIDE_FLAT)),
            entry_option_symbol=_safe_str(raw.get("entry_option_symbol", "")),
            entry_option_token=_safe_str(raw.get("entry_option_token", "")),
            avg_price=_safe_float(raw.get("avg_price", 0.0), 0.0),
            qty_lots=_safe_int(raw.get("qty_lots", 0), 0),
            entry_ts_ns=_safe_int(raw.get("entry_ts_ns", 0), 0),
            entry_mode=_safe_str(raw.get("entry_mode", N.ENTRY_MODE_UNKNOWN), N.ENTRY_MODE_UNKNOWN),
            meta_json=raw.get("meta_json"),
        )

    def _publish_decision(self, decision: StrategyDecision) -> None:
        RX.xadd_fields(N.STREAM_DECISIONS_MME, _decision_to_wire(decision), client=self.redis)

    def run_once(self, *, trading_allowed: bool = True) -> StrategyDecision | None:
        frame = self._fetch_feature_frame()
        if frame is None:
            return None
        risk = self._fetch_risk_state()
        execution = self._fetch_execution_state()
        position = self._fetch_position_state()
        decision = self.engine.evaluate(
            frame=frame,
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

        try:
            while not self.shutdown.is_set():
                self._refresh_lock_if_due()
                try:
                    self.run_once(trading_allowed=True)
                    status = (
                        N.HEALTH_STATUS_WARN
                        if self.engine.machine.state in {StrategyState.DEGRADED, StrategyState.WAIT}
                        else N.HEALTH_STATUS_OK
                    )
                    message = self.engine.machine.reason_code
                    now_ns = self._now_ns()
                    if (now_ns - self._last_heartbeat_ns) >= (self.heartbeat_refresh_ms * 1_000_000):
                        self._publish_heartbeat(status=status, message=message)
                        self._last_heartbeat_ns = now_ns
                except Exception as exc:
                    self._publish_system_error(
                        event="strategy_service_loop_error",
                        detail=str(exc),
                    )
                    self._publish_heartbeat(status=N.HEALTH_STATUS_ERROR, message=str(exc))
                    if self.settings.startup.fail_fast:
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
        raise RuntimeError(
            "strategy requires context.settings or get_settings() returning AppSettings"
        )

    redis_runtime = getattr(context, "redis", None)
    redis_client = (
        redis_runtime.sync if redis_runtime is not None and hasattr(redis_runtime, "sync") else RX.get_redis()
    )
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
