from __future__ import annotations

"""Shadow-only Trade Quality Authorization Gate v28.

This module evaluates an existing strategy candidate. It never creates a candidate,
places an order, starts risk/execution, or writes to Redis. Its only outcomes are:
AUTHORIZE, VETO, HOLD, and RESET_OBSERVATION.
"""

import argparse
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, time as dt_time
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
SCHEMA = "trade_quality_authorization_gate_v28.v1"


class Verdict(str, Enum):
    AUTHORIZE = "AUTHORIZE"
    VETO = "VETO"
    HOLD = "HOLD"
    RESET_OBSERVATION = "RESET_OBSERVATION"


class LockState(str, Enum):
    CANDIDATE_CREATED = "CANDIDATE_CREATED"
    OPTION_SELECTED = "OPTION_SELECTED"
    OPTION_SYMBOL_LOCKED = "OPTION_SYMBOL_LOCKED"
    MICRO_OBSERVATION_ACTIVE = "MICRO_OBSERVATION_ACTIVE"
    MICRO_OBSERVATION_COMPLETE = "MICRO_OBSERVATION_COMPLETE"
    AUTHORIZED = "AUTHORIZED"


class SessionPhase(str, Enum):
    OPENING = "OPENING"
    MID_SESSION = "MID_SESSION"
    CLOSING = "CLOSING"
    NO_NEW_ENTRY = "NO_NEW_ENTRY"


HARD_VETO_FIELDS: tuple[str, ...] = (
    "QUOTE_FRESH",
    "BID_QTY_VALID",
    "ASK_QTY_VALID",
    "SPREAD_ACCEPTABLE",
    "OPTION_SYMBOL_STABLE",
    "INSTRUMENT_LOCK_VALID",
    "UNDERLYING_OPTION_ALIGNED",
    "NO_CHASE",
    "EDGE_AFTER_COST_POSITIVE",
    "BROKER_FLAT",
    "ACTIVE_BROKER_ORDERS_ZERO",
    "RISK_GATE_OPEN",
    "TIMEFRAME_COMPLETE",
)

NEGATIVE_HARD_VETO_FIELDS: tuple[str, ...] = (
    "DATA_GAP_PRESENT",
    "PENDING_ORDER_PRESENT",
    "ENTRY_CUTOFF_PASSED",
)

COMPONENT_NAMES: tuple[str, ...] = (
    "regime_15m",
    "setup_5m",
    "trigger_3m",
    "option_microstructure",
    "liquidity_execution",
)

DIRECTION_OWNERS: tuple[str, ...] = (
    "NIFTY_FUTURES_SPOT_VWAP_STRUCTURE",
    "NIFTY_FUTURES_SPOT_STRUCTURE",
)


@dataclass(frozen=True)
class SessionPolicy:
    start: str
    end: str
    minimum_score: float
    component_minimum: float
    observation_seconds: int
    max_hold_seconds: int
    spread_deterioration_fraction: float
    no_chase_atr_fraction: float
    no_chase_premium_fraction: float


@dataclass(frozen=True)
class GateConfig:
    total_score_minimum: float = 75.0
    component_minimum: float = 10.0
    maximum_component_score: float = 20.0
    calibration_required: bool = True
    calibration_id: str = "UNSET"
    minimum_net_edge_points: float = 0.25
    max_order_attempts: int = 1
    max_lots: int = 1
    max_positions: int = 1
    max_events: int = 1
    order_type: str = "MARKETABLE_LIMIT"
    retry_allowed: bool = False
    replacement_allowed: bool = False
    averaging_allowed: bool = False
    policies: Mapping[str, SessionPolicy] = field(default_factory=lambda: {
        SessionPhase.OPENING.value: SessionPolicy(
            start="09:15", end="09:45", minimum_score=80.0,
            component_minimum=11.0, observation_seconds=60,
            max_hold_seconds=300, spread_deterioration_fraction=0.20,
            no_chase_atr_fraction=0.30, no_chase_premium_fraction=0.035,
        ),
        SessionPhase.MID_SESSION.value: SessionPolicy(
            start="09:45", end="14:30", minimum_score=75.0,
            component_minimum=10.0, observation_seconds=45,
            max_hold_seconds=300, spread_deterioration_fraction=0.25,
            no_chase_atr_fraction=0.35, no_chase_premium_fraction=0.040,
        ),
        SessionPhase.CLOSING.value: SessionPolicy(
            start="14:30", end="14:50", minimum_score=82.0,
            component_minimum=12.0, observation_seconds=30,
            max_hold_seconds=180, spread_deterioration_fraction=0.15,
            no_chase_atr_fraction=0.25, no_chase_premium_fraction=0.025,
        ),
    })


@dataclass
class ObservationState:
    state: str = LockState.CANDIDATE_CREATED.value
    candidate_identity: str = ""
    family: str = ""
    side: str = ""
    selected_symbol: str = ""
    selected_token: str = ""
    strike_classification: str = ""
    observation_window_id: str = ""
    observation_started_ms: int = 0
    observation_samples: int = 0
    last_quote_ms: int = 0
    last_spread: float | None = None
    authorization_id: str = ""
    reset_count: int = 0


@dataclass(frozen=True)
class EdgeEstimate:
    expected_gross_move_points: float
    entry_cost_points: float
    exit_cost_points: float
    slippage_points: float
    brokerage_points: float
    taxes_exchange_points: float

    @property
    def net_edge_points(self) -> float:
        return (
            self.expected_gross_move_points
            - self.entry_cost_points
            - self.exit_cost_points
            - self.slippage_points
            - self.brokerage_points
            - self.taxes_exchange_points
        )


class GateInputError(ValueError):
    pass


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _float(value: Any, default: float | None = None) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _text(value: Any) -> str:
    return str(value or "").strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _parse_hhmm(value: str) -> dt_time:
    hour, minute = value.split(":", 1)
    return dt_time(hour=int(hour), minute=int(minute))


def session_phase(now: datetime, config: GateConfig) -> tuple[SessionPhase, SessionPolicy | None]:
    local = now.astimezone(IST)
    current = local.time().replace(second=0, microsecond=0)
    if local.weekday() >= 5:
        return SessionPhase.NO_NEW_ENTRY, None
    for phase in (SessionPhase.OPENING, SessionPhase.MID_SESSION, SessionPhase.CLOSING):
        policy = config.policies[phase.value]
        if _parse_hhmm(policy.start) <= current < _parse_hhmm(policy.end):
            return phase, policy
    return SessionPhase.NO_NEW_ENTRY, None


def candidate_identity(packet: Mapping[str, Any]) -> str:
    identity = {
        "family": _text(packet.get("family")).upper(),
        "side": _text(packet.get("side")).upper(),
        "setup_origin": _text(packet.get("setup_origin")),
        "regime_id": _text(packet.get("regime_id")),
        "trigger_level_bucket": _text(packet.get("trigger_level_bucket")),
        "selected_symbol": _text(packet.get("selected_symbol")).upper(),
        "observation_window_id": _text(packet.get("observation_window_id")),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:24]


def cooldown_key(packet: Mapping[str, Any], outcome: str = "") -> str:
    return f"{candidate_identity(packet)}:{_text(outcome).upper() or 'PENDING'}"


def score_component(raw: Mapping[str, Any], maximum: float = 20.0) -> tuple[float, dict[str, float]]:
    normalized: dict[str, float] = {}
    for key, value in raw.items():
        numeric = _float(value)
        if numeric is None:
            continue
        normalized[str(key)] = min(1.0, max(0.0, numeric))
    if not normalized:
        return 0.0, normalized
    return round(sum(normalized.values()) / len(normalized) * maximum, 4), normalized


def component_scores(packet: Mapping[str, Any], config: GateConfig) -> tuple[dict[str, float], dict[str, Any]]:
    raw_components = _mapping(packet.get("components"))
    scores: dict[str, float] = {}
    normalized: dict[str, Any] = {}
    for name in COMPONENT_NAMES:
        score, norm = score_component(_mapping(raw_components.get(name)), config.maximum_component_score)
        scores[name] = score
        normalized[name] = norm
    return scores, normalized


def hard_vetoes(packet: Mapping[str, Any]) -> list[str]:
    checks = _mapping(packet.get("hard_veto_checks"))
    vetoes: list[str] = []
    for field_name in HARD_VETO_FIELDS:
        if not _bool(checks.get(field_name), False):
            vetoes.append(field_name)
    for field_name in NEGATIVE_HARD_VETO_FIELDS:
        if _bool(checks.get(field_name), False):
            vetoes.append(field_name)
    return vetoes


def edge_estimates(packet: Mapping[str, Any]) -> tuple[EdgeEstimate, EdgeEstimate]:
    edge = _mapping(packet.get("edge_after_cost"))
    gross = _float(edge.get("expected_gross_move_points"), 0.0) or 0.0

    optimistic = EdgeEstimate(
        expected_gross_move_points=gross,
        entry_cost_points=_float(edge.get("optimistic_entry_cost_points"), 0.0) or 0.0,
        exit_cost_points=_float(edge.get("optimistic_exit_cost_points"), 0.0) or 0.0,
        slippage_points=_float(edge.get("optimistic_slippage_points"), 0.0) or 0.0,
        brokerage_points=_float(edge.get("brokerage_points"), 0.0) or 0.0,
        taxes_exchange_points=_float(edge.get("taxes_exchange_points"), 0.0) or 0.0,
    )
    conservative = EdgeEstimate(
        expected_gross_move_points=gross,
        entry_cost_points=_float(edge.get("conservative_entry_cost_points"), 0.0) or 0.0,
        exit_cost_points=_float(edge.get("conservative_exit_cost_points"), 0.0) or 0.0,
        slippage_points=_float(edge.get("conservative_slippage_points"), 0.0) or 0.0,
        brokerage_points=_float(edge.get("brokerage_points"), 0.0) or 0.0,
        taxes_exchange_points=_float(edge.get("taxes_exchange_points"), 0.0) or 0.0,
    )
    return optimistic, conservative


def no_chase_result(packet: Mapping[str, Any], policy: SessionPolicy) -> dict[str, Any]:
    creation = _mapping(packet.get("candidate_creation"))
    current = _mapping(packet.get("current_market"))

    trigger_underlying = _float(creation.get("trigger_underlying_price"))
    trigger_mid = _float(creation.get("trigger_option_mid"))
    trigger_spread = _float(creation.get("trigger_spread"))
    atr = _float(creation.get("short_term_atr"))
    current_underlying = _float(current.get("underlying_price"))
    current_mid = _float(current.get("option_mid"))
    current_spread = _float(current.get("spread"))

    missing = [
        name for name, value in {
            "trigger_underlying_price": trigger_underlying,
            "trigger_option_mid": trigger_mid,
            "trigger_spread": trigger_spread,
            "short_term_atr": atr,
            "current_underlying_price": current_underlying,
            "current_option_mid": current_mid,
            "current_spread": current_spread,
        }.items() if value is None
    ]
    if missing or not atr or atr <= 0 or not trigger_mid or trigger_mid <= 0:
        return {"passed": False, "status": "UNCALCULABLE", "missing": missing}

    underlying_displacement = abs(current_underlying - trigger_underlying)
    premium_displacement = max(0.0, current_mid - trigger_mid)
    spread_deterioration = max(0.0, current_spread - trigger_spread)
    allowed_underlying = atr * policy.no_chase_atr_fraction
    allowed_premium = trigger_mid * policy.no_chase_premium_fraction
    allowed_spread = max(trigger_spread * policy.spread_deterioration_fraction, 0.05)

    passed = (
        underlying_displacement <= allowed_underlying
        and premium_displacement <= allowed_premium
        and spread_deterioration <= allowed_spread
    )
    return {
        "passed": passed,
        "status": "PASS" if passed else "CHASED",
        "underlying_displacement": round(underlying_displacement, 6),
        "allowed_underlying_displacement": round(allowed_underlying, 6),
        "premium_displacement": round(premium_displacement, 6),
        "allowed_premium_displacement": round(allowed_premium, 6),
        "spread_deterioration": round(spread_deterioration, 6),
        "allowed_spread_deterioration": round(allowed_spread, 6),
    }


def marketable_limit_plan(packet: Mapping[str, Any], config: GateConfig) -> dict[str, Any]:
    current = _mapping(packet.get("current_market"))
    ask = _float(current.get("ask"))
    spread = _float(current.get("spread"))
    ask_volatility = _float(current.get("recent_ask_volatility"), 0.0) or 0.0
    tick_size = _float(current.get("tick_size"), 0.05) or 0.05
    if ask is None or spread is None or ask <= 0 or spread < 0 or tick_size <= 0:
        return {
            "order_type": config.order_type,
            "plan_ready": False,
            "reason": "PRICE_CAP_INPUT_MISSING",
            "broker_order": 0,
        }
    cap_buffer = max(tick_size, min(max(spread * 0.75, ask_volatility * 1.25), spread * 2.0 + tick_size))
    raw_cap = ask + cap_buffer
    price_cap = math.ceil(raw_cap / tick_size) * tick_size
    return {
        "order_type": config.order_type,
        "plan_ready": True,
        "current_ask": ask,
        "spread": spread,
        "recent_ask_volatility": ask_volatility,
        "tick_size": tick_size,
        "price_cap": round(price_cap, 6),
        "max_order_attempts": config.max_order_attempts,
        "retry_allowed": config.retry_allowed,
        "replacement_allowed": config.replacement_allowed,
        "averaging_allowed": config.averaging_allowed,
        "unfilled_is_safe_outcome": True,
        "broker_order": 0,
    }


def _reset_reason(packet: Mapping[str, Any], state: ObservationState) -> str:
    symbol = _text(packet.get("selected_symbol")).upper()
    token = _text(packet.get("selected_token"))
    strike = _text(packet.get("strike_classification"))
    checks = _mapping(packet.get("hard_veto_checks"))
    if state.selected_symbol and symbol != state.selected_symbol:
        return "OPTION_SYMBOL_CHANGED"
    if state.selected_token and token != state.selected_token:
        return "OPTION_TOKEN_CHANGED"
    if state.strike_classification and strike != state.strike_classification:
        return "STRIKE_CLASSIFICATION_CHANGED"
    if not _bool(checks.get("QUOTE_FRESH"), False):
        return "QUOTE_STALE"
    if not _bool(checks.get("SPREAD_ACCEPTABLE"), False):
        return "SPREAD_EXCEEDED"
    if not (_bool(checks.get("BID_QTY_VALID"), False) and _bool(checks.get("ASK_QTY_VALID"), False)):
        return "DEPTH_DISAPPEARED"
    if not _bool(checks.get("UNDERLYING_OPTION_ALIGNED"), False):
        return "DIRECTION_INCONSISTENT"
    if _bool(checks.get("DATA_GAP_PRESENT"), False):
        return "MATERIAL_DATA_GAP"
    return ""


def advance_observation(
    packet: Mapping[str, Any],
    state: ObservationState,
    now_ms: int,
    required_seconds: int,
) -> tuple[ObservationState, str]:
    identity = candidate_identity(packet)
    symbol = _text(packet.get("selected_symbol")).upper()
    token = _text(packet.get("selected_token"))
    strike = _text(packet.get("strike_classification"))
    window_id = _text(packet.get("observation_window_id"))

    reset_reason = _reset_reason(packet, state) if state.candidate_identity else ""
    if state.candidate_identity and (identity != state.candidate_identity or reset_reason):
        return ObservationState(
            state=LockState.OPTION_SELECTED.value if symbol else LockState.CANDIDATE_CREATED.value,
            candidate_identity=identity,
            family=_text(packet.get("family")).upper(),
            side=_text(packet.get("side")).upper(),
            selected_symbol=symbol,
            selected_token=token,
            strike_classification=strike,
            observation_window_id=window_id,
            reset_count=state.reset_count + 1,
        ), reset_reason or "CANDIDATE_IDENTITY_CHANGED"

    if not state.candidate_identity:
        state = ObservationState(
            state=LockState.CANDIDATE_CREATED.value,
            candidate_identity=identity,
            family=_text(packet.get("family")).upper(),
            side=_text(packet.get("side")).upper(),
            selected_symbol=symbol,
            selected_token=token,
            strike_classification=strike,
            observation_window_id=window_id,
        )

    if not symbol or not token:
        state.state = LockState.CANDIDATE_CREATED.value
        return state, "INSTRUMENT_NOT_SELECTED"
    if state.state == LockState.CANDIDATE_CREATED.value:
        state.state = LockState.OPTION_SELECTED.value
    if state.state == LockState.OPTION_SELECTED.value:
        state.state = LockState.OPTION_SYMBOL_LOCKED.value
    if state.state == LockState.OPTION_SYMBOL_LOCKED.value:
        state.state = LockState.MICRO_OBSERVATION_ACTIVE.value
        state.observation_started_ms = now_ms
        state.observation_samples = 1
    elif state.state == LockState.MICRO_OBSERVATION_ACTIVE.value:
        state.observation_samples += 1
        elapsed = max(0, now_ms - state.observation_started_ms)
        if elapsed >= required_seconds * 1000:
            state.state = LockState.MICRO_OBSERVATION_COMPLETE.value
    state.last_quote_ms = now_ms
    state.last_spread = _float(_mapping(packet.get("current_market")).get("spread"))
    return state, ""


def evaluate(
    packet: Mapping[str, Any],
    state: ObservationState | None = None,
    config: GateConfig | None = None,
    now: datetime | None = None,
) -> tuple[dict[str, Any], ObservationState]:
    config = config or GateConfig()
    state = state or ObservationState()
    now = now or datetime.now(tz=IST)
    now_millis = int(now.timestamp() * 1000)
    phase, policy = session_phase(now, config)

    base: dict[str, Any] = {
        "schema": SCHEMA,
        "evaluated_at": now.isoformat(),
        "verdict": Verdict.HOLD.value,
        "reason": "UNSET",
        "session_phase": phase.value,
        "candidate_identity": candidate_identity(packet),
        "cooldown_identity": cooldown_key(packet),
        "raw_input": dict(packet),
        "broker_order": 0,
        "paper_order": 0,
        "risk_started": 0,
        "execution_started": 0,
        "redis_write": 0,
        "strategy_candidate_created": 0,
        "direction_owner": _text(packet.get("direction_owner")),
        "option_direction_role": "CONFIRMATION_LIQUIDITY_ONLY",
    }

    if phase == SessionPhase.NO_NEW_ENTRY or policy is None:
        base.update({
            "verdict": Verdict.VETO.value,
            "reason": "ENTRY_CUTOFF_PASSED_OR_MARKET_CLOSED",
            "hard_vetoes": ["ENTRY_CUTOFF_PASSED"],
        })
        return base, state

    direction_owner = _text(packet.get("direction_owner")).upper()
    if direction_owner not in DIRECTION_OWNERS:
        base.update({
            "verdict": Verdict.VETO.value,
            "reason": "DIRECTION_OWNER_INVALID_OR_OPTION_LED",
            "hard_vetoes": ["DIRECTION_OWNERSHIP_INVALID"],
        })
        return base, state

    new_state, reset_reason = advance_observation(packet, state, now_millis, policy.observation_seconds)
    base["observation_state"] = asdict(new_state)
    if reset_reason and state.candidate_identity:
        base.update({
            "verdict": Verdict.RESET_OBSERVATION.value,
            "reason": reset_reason,
        })
        return base, new_state

    scores, normalized = component_scores(packet, config)
    total = round(sum(scores.values()), 4)
    no_chase = no_chase_result(packet, policy)
    optimistic, conservative = edge_estimates(packet)
    checks = dict(_mapping(packet.get("hard_veto_checks")))
    checks["NO_CHASE"] = bool(no_chase.get("passed"))
    checks["EDGE_AFTER_COST_POSITIVE"] = conservative.net_edge_points >= config.minimum_net_edge_points
    packet_for_veto = dict(packet)
    packet_for_veto["hard_veto_checks"] = checks
    vetoes = hard_vetoes(packet_for_veto)

    minimum_total = max(config.total_score_minimum, policy.minimum_score)
    minimum_component = max(config.component_minimum, policy.component_minimum)
    low_components = [name for name, score in scores.items() if score < minimum_component]
    calibration_ready = (not config.calibration_required) or config.calibration_id not in {"", "UNSET"}

    base.update({
        "session_policy": asdict(policy),
        "component_scores": scores,
        "component_raw_normalized": normalized,
        "total_score": total,
        "minimum_total_score": minimum_total,
        "minimum_component_score": minimum_component,
        "low_components": low_components,
        "hard_veto_checks": checks,
        "hard_vetoes": vetoes,
        "hard_veto_count": len(vetoes),
        "no_chase": no_chase,
        "edge_after_cost": {
            "optimistic": {**asdict(optimistic), "net_edge_points": round(optimistic.net_edge_points, 6)},
            "conservative": {**asdict(conservative), "net_edge_points": round(conservative.net_edge_points, 6)},
            "minimum_required_net_edge_points": config.minimum_net_edge_points,
        },
        "calibration_required": config.calibration_required,
        "calibration_id": config.calibration_id,
        "calibration_ready": calibration_ready,
        "marketable_limit_plan": marketable_limit_plan(packet, config),
        "first_live_constraints": {
            "order_type": config.order_type,
            "max_order_attempts": config.max_order_attempts,
            "retry_allowed": config.retry_allowed,
            "replacement_allowed": config.replacement_allowed,
            "averaging_allowed": config.averaging_allowed,
            "max_lots": config.max_lots,
            "max_positions": config.max_positions,
            "max_events": config.max_events,
        },
    })

    if vetoes:
        base.update({"verdict": Verdict.VETO.value, "reason": "HARD_VETO_PRESENT"})
        return base, new_state

    if new_state.state != LockState.MICRO_OBSERVATION_COMPLETE.value:
        base.update({"verdict": Verdict.HOLD.value, "reason": "MICRO_OBSERVATION_INCOMPLETE"})
        return base, new_state

    if not calibration_ready:
        base.update({"verdict": Verdict.HOLD.value, "reason": "REPLAY_CALIBRATION_REQUIRED"})
        return base, new_state

    if low_components or total < minimum_total:
        base.update({"verdict": Verdict.VETO.value, "reason": "QUALITY_SCORE_INSUFFICIENT"})
        return base, new_state

    authorization_payload = {
        "candidate_identity": base["candidate_identity"],
        "evaluated_at": base["evaluated_at"],
        "score": total,
        "symbol": _text(packet.get("selected_symbol")).upper(),
        "token": _text(packet.get("selected_token")),
    }
    auth_id = "TQAG28-" + hashlib.sha256(
        json.dumps(authorization_payload, sort_keys=True).encode()
    ).hexdigest()[:20]
    new_state.state = LockState.AUTHORIZED.value
    new_state.authorization_id = auth_id
    base["observation_state"] = asdict(new_state)
    base.update({
        "verdict": Verdict.AUTHORIZE.value,
        "reason": "ALL_HARD_VETOES_CLEAR_SCORE_EDGE_AND_OBSERVATION_PASS",
        "authorization_id": auth_id,
        "authorization_record_only": True,
    })
    return base, new_state


def load_state(path: Path | None) -> ObservationState:
    if path is None or not path.exists():
        return ObservationState()
    raw = json.loads(path.read_text(encoding="utf-8"))
    return ObservationState(**{k: raw.get(k, v.default) for k, v in ObservationState.__dataclass_fields__.items()})


def config_from_json(raw: Mapping[str, Any]) -> GateConfig:
    policies_raw = _mapping(raw.get("policies"))
    policies: dict[str, SessionPolicy] = {}
    defaults = GateConfig().policies
    for phase, default in defaults.items():
        source = _mapping(policies_raw.get(phase))
        policies[phase] = SessionPolicy(**{
            name: source.get(name, getattr(default, name))
            for name in SessionPolicy.__dataclass_fields__
        })
    scalar = {
        name: raw.get(name, getattr(GateConfig(), name))
        for name in GateConfig.__dataclass_fields__
        if name != "policies"
    }
    return GateConfig(**scalar, policies=policies)


def append_record(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--record-ndjson", type=Path)
    parser.add_argument("--now", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    packet = json.loads(args.input.read_text(encoding="utf-8"))
    config = GateConfig()
    if args.config:
        config = config_from_json(json.loads(args.config.read_text(encoding="utf-8")))
    state = load_state(args.state)
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(tz=IST)
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    record, new_state = evaluate(packet, state=state, config=config, now=now)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.state:
        args.state.parent.mkdir(parents=True, exist_ok=True)
        args.state.write_text(json.dumps(asdict(new_state), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.record_ndjson:
        append_record(args.record_ndjson, record)
    print(json.dumps({
        "verdict": record["verdict"],
        "reason": record["reason"],
        "candidate_identity": record["candidate_identity"],
        "authorization_id": record.get("authorization_id", ""),
        "broker_order": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
