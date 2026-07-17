"""Shadow-only trade-quality authorization gate.

This module is intentionally incapable of creating, routing, or sending orders.
It evaluates an existing strategy-owned candidate and returns only one of:
AUTHORIZE, VETO, HOLD, RESET_OBSERVATION.

Lane X rule: the strategy remains the candidate owner. This gate only decides
whether the candidate is sufficiently stable and executable for a later layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Mapping


class TQAGDecision(str, Enum):
    AUTHORIZE = "AUTHORIZE"
    VETO = "VETO"
    HOLD = "HOLD"
    RESET_OBSERVATION = "RESET_OBSERVATION"


class InstrumentLockState(str, Enum):
    CANDIDATE_CREATED = "CANDIDATE_CREATED"
    OPTION_SELECTED = "OPTION_SELECTED"
    OPTION_SYMBOL_LOCKED = "OPTION_SYMBOL_LOCKED"
    MICRO_OBSERVATION_ACTIVE = "MICRO_OBSERVATION_ACTIVE"
    MICRO_OBSERVATION_COMPLETE = "MICRO_OBSERVATION_COMPLETE"
    AUTHORIZED = "AUTHORIZED"


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


@dataclass(frozen=True)
class TQAGCosts:
    expected_gross_move: float = 0.0
    entry_half_spread_or_full_crossing_cost: float = 0.0
    expected_exit_spread: float = 0.0
    estimated_slippage: float = 0.0
    brokerage: float = 0.0
    taxes_and_exchange_charges: float = 0.0
    minimum_required_net_edge: float = 0.0

    @property
    def expected_net_edge(self) -> float:
        return (
            self.expected_gross_move
            - self.entry_half_spread_or_full_crossing_cost
            - self.expected_exit_spread
            - self.estimated_slippage
            - self.brokerage
            - self.taxes_and_exchange_charges
        )


@dataclass(frozen=True)
class TQAGResult:
    decision: TQAGDecision
    total_score: float
    component_scores: dict[str, float]
    hard_vetoes: list[str]
    reset_reasons: list[str]
    instrument_lock_state: InstrumentLockState
    expected_net_edge_conservative: float
    expected_net_edge_optimistic: float
    raw_inputs: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        data = asdict(self)
        data["decision"] = self.decision.value
        data["instrument_lock_state"] = self.instrument_lock_state.value
        data["can_create_order"] = False
        data["can_route_order"] = False
        data["can_send_broker_order"] = False
        return data


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "pass", "ok"}
    return bool(value)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _component_scores(raw: Mapping[str, Any]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for name in COMPONENT_NAMES:
        value = _num(raw.get(name), 0.0)
        scores[name] = max(0.0, min(20.0, value))
    return scores


def evaluate_trade_quality_authorization(
    raw_inputs: Mapping[str, Any],
    *,
    conservative_costs: TQAGCosts | None = None,
    optimistic_costs: TQAGCosts | None = None,
    total_score_min: float = 75.0,
    component_score_min: float = 10.0,
) -> TQAGResult:
    """Evaluate a strategy-owned candidate without generating any order."""

    raw = dict(raw_inputs)
    conservative_costs = conservative_costs or TQAGCosts()
    optimistic_costs = optimistic_costs or TQAGCosts()

    hard_vetoes: list[str] = []

    for field_name in HARD_VETO_FIELDS:
        if not _truthy(raw.get(field_name, False)):
            hard_vetoes.append(field_name)

    for field_name in NEGATIVE_HARD_VETO_FIELDS:
        if _truthy(raw.get(field_name, False)):
            hard_vetoes.append(field_name)

    conservative_edge = conservative_costs.expected_net_edge
    optimistic_edge = optimistic_costs.expected_net_edge

    if conservative_edge < conservative_costs.minimum_required_net_edge:
        if "EDGE_AFTER_COST_POSITIVE" not in hard_vetoes:
            hard_vetoes.append("EDGE_AFTER_COST_POSITIVE")

    reset_reasons: list[str] = []
    for key in (
        "symbol_changed",
        "strike_classification_changed",
        "token_changed",
        "quote_stale",
        "spread_exceeded",
        "depth_disappeared",
        "underlying_direction_inconsistent",
        "material_data_gap",
    ):
        if _truthy(raw.get(key, False)):
            reset_reasons.append(key.upper())

    scores = _component_scores(raw)
    total_score = sum(scores.values())

    lock_state_raw = str(raw.get("instrument_lock_state", InstrumentLockState.CANDIDATE_CREATED.value))
    try:
        lock_state = InstrumentLockState(lock_state_raw)
    except ValueError:
        lock_state = InstrumentLockState.CANDIDATE_CREATED
        reset_reasons.append("INVALID_INSTRUMENT_LOCK_STATE")

    if reset_reasons:
        decision = TQAGDecision.RESET_OBSERVATION
        next_state = InstrumentLockState.OPTION_SELECTED
    elif hard_vetoes:
        decision = TQAGDecision.VETO
        next_state = lock_state
    elif total_score < total_score_min or any(v < component_score_min for v in scores.values()):
        decision = TQAGDecision.HOLD
        next_state = lock_state
    else:
        decision = TQAGDecision.AUTHORIZE
        next_state = InstrumentLockState.AUTHORIZED

    return TQAGResult(
        decision=decision,
        total_score=total_score,
        component_scores=scores,
        hard_vetoes=hard_vetoes,
        reset_reasons=reset_reasons,
        instrument_lock_state=next_state,
        expected_net_edge_conservative=conservative_edge,
        expected_net_edge_optimistic=optimistic_edge,
        raw_inputs=raw,
    )


__all__ = [
    "COMPONENT_NAMES",
    "HARD_VETO_FIELDS",
    "NEGATIVE_HARD_VETO_FIELDS",
    "InstrumentLockState",
    "TQAGCosts",
    "TQAGDecision",
    "TQAGResult",
    "evaluate_trade_quality_authorization",
]
