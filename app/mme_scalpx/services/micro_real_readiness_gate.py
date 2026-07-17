"""Pure micro-real readiness and transaction-cost analysis.

This module cannot place, modify, replace, cancel, or route an order.
It performs no Redis writes and contains no broker transport.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping


class MicroRealDecision(str, Enum):
    BLOCK = "BLOCK"
    READY_FOR_MANUAL_AUTHORIZATION = "READY_FOR_MANUAL_AUTHORIZATION"


@dataclass(frozen=True)
class CostBreakdown:
    brokerage: float
    stt_ctt: float
    exchange_transaction: float
    gst: float
    sebi: float
    stamp_duty: float
    estimated_slippage: float
    other: float = 0.0

    @property
    def total_cost_rupees(self) -> float:
        return round(
            self.brokerage
            + self.stt_ctt
            + self.exchange_transaction
            + self.gst
            + self.sebi
            + self.stamp_duty
            + self.estimated_slippage
            + self.other,
            6,
        )

    def breakeven_points(self, quantity_units: int) -> float:
        if quantity_units <= 0:
            raise ValueError("quantity_units must be positive")
        return round(self.total_cost_rupees / quantity_units, 6)


@dataclass(frozen=True)
class MicroRealReadinessInputs:
    fresh_monday_preflight: bool
    market_session_open: bool
    daily_stop_not_fired: bool

    broker_session_healthy: bool
    broker_flat: bool
    active_broker_orders_zero: bool
    sufficient_margin: bool

    provider_ready_classic: bool
    safe_to_consume: bool
    quote_fresh: bool

    tqag_decision: str
    tqag_hard_veto_count: int
    bid_qty_valid: bool
    ask_qty_valid: bool
    spread_acceptable: bool
    instrument_lock_valid: bool
    option_symbol_stable: bool
    underlying_option_aligned: bool
    no_chase: bool
    edge_after_cost_positive: bool
    timeframe_complete: bool
    data_gap_present: bool
    pending_order_present: bool
    entry_cutoff_passed: bool

    charges_configured: bool
    conservative_breakeven_points: float
    expected_move_points: float

    order_type: str
    max_order_attempts: int
    retry_count: int
    replacement_count: int
    averaging_allowed: bool
    max_lots: int
    max_positions: int
    max_events: int

    explicit_user_authorization: bool


@dataclass(frozen=True)
class MicroRealReadinessResult:
    decision: MicroRealDecision
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    raw_inputs: Mapping[str, Any]

    def to_record(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "raw_inputs": dict(self.raw_inputs),
            # Absolute side-effect proof for this analysis module.
            "can_create_order": False,
            "can_route_order": False,
            "can_modify_order": False,
            "can_cancel_order": False,
            "can_send_broker_order": False,
        }


def evaluate_micro_real_readiness(
    inputs: MicroRealReadinessInputs,
) -> MicroRealReadinessResult:
    blockers: list[str] = []
    warnings: list[str] = []

    required_true = {
        "FRESH_MONDAY_PREFLIGHT": inputs.fresh_monday_preflight,
        "MARKET_SESSION_OPEN": inputs.market_session_open,
        "DAILY_STOP_NOT_FIRED": inputs.daily_stop_not_fired,
        "BROKER_SESSION_HEALTHY": inputs.broker_session_healthy,
        "BROKER_FLAT": inputs.broker_flat,
        "ACTIVE_BROKER_ORDERS_ZERO": inputs.active_broker_orders_zero,
        "SUFFICIENT_MARGIN": inputs.sufficient_margin,
        "PROVIDER_READY_CLASSIC": inputs.provider_ready_classic,
        "SAFE_TO_CONSUME": inputs.safe_to_consume,
        "QUOTE_FRESH": inputs.quote_fresh,
        "BID_QTY_VALID": inputs.bid_qty_valid,
        "ASK_QTY_VALID": inputs.ask_qty_valid,
        "SPREAD_ACCEPTABLE": inputs.spread_acceptable,
        "INSTRUMENT_LOCK_VALID": inputs.instrument_lock_valid,
        "OPTION_SYMBOL_STABLE": inputs.option_symbol_stable,
        "UNDERLYING_OPTION_ALIGNED": inputs.underlying_option_aligned,
        "NO_CHASE": inputs.no_chase,
        "EDGE_AFTER_COST_POSITIVE": inputs.edge_after_cost_positive,
        "TIMEFRAME_COMPLETE": inputs.timeframe_complete,
        "CHARGES_CONFIGURED": inputs.charges_configured,
        "EXPLICIT_USER_AUTHORIZATION": inputs.explicit_user_authorization,
    }

    for name, passed in required_true.items():
        if not passed:
            blockers.append(name)

    if str(inputs.tqag_decision).strip().upper() != "AUTHORIZE":
        blockers.append("TQAG_NOT_AUTHORIZE")

    if inputs.tqag_hard_veto_count != 0:
        blockers.append("TQAG_HARD_VETO_PRESENT")

    if inputs.data_gap_present:
        blockers.append("DATA_GAP_PRESENT")

    if inputs.pending_order_present:
        blockers.append("PENDING_ORDER_PRESENT")

    if inputs.entry_cutoff_passed:
        blockers.append("ENTRY_CUTOFF_PASSED")

    if inputs.order_type.strip().upper() != "MARKETABLE_LIMIT":
        blockers.append("ORDER_TYPE_NOT_MARKETABLE_LIMIT")

    if inputs.max_order_attempts != 1:
        blockers.append("MAX_ORDER_ATTEMPTS_NOT_ONE")

    if inputs.retry_count != 0:
        blockers.append("RETRY_NOT_ZERO")

    if inputs.replacement_count != 0:
        blockers.append("REPLACEMENT_NOT_ZERO")

    if inputs.averaging_allowed:
        blockers.append("AVERAGING_ALLOWED")

    if inputs.max_lots != 1:
        blockers.append("MAX_LOTS_NOT_ONE")

    if inputs.max_positions != 1:
        blockers.append("MAX_POSITIONS_NOT_ONE")

    if inputs.max_events != 1:
        blockers.append("MAX_EVENTS_NOT_ONE")

    if inputs.conservative_breakeven_points < 0:
        blockers.append("INVALID_BREAKEVEN_POINTS")

    if inputs.expected_move_points <= inputs.conservative_breakeven_points:
        blockers.append("EXPECTED_MOVE_NOT_ABOVE_CONSERVATIVE_BREAKEVEN")

    if inputs.expected_move_points < inputs.conservative_breakeven_points * 1.5:
        warnings.append("EDGE_BUFFER_BELOW_1_5X_BREAKEVEN")

    decision = (
        MicroRealDecision.READY_FOR_MANUAL_AUTHORIZATION
        if not blockers
        else MicroRealDecision.BLOCK
    )

    return MicroRealReadinessResult(
        decision=decision,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        raw_inputs=asdict(inputs),
    )
