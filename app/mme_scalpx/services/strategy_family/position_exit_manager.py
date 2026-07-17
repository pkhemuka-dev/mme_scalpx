"""Pure strategy-owned position exit policy.

This module evaluates an already-open option position and may construct a
canonical EXIT StrategyDecision.

It does not:
- read or write Redis;
- call any broker;
- place or simulate an order;
- mutate position, risk or execution state;
- enable paper or live trading.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core.models import StrategyDecision

from .decisions import build_exit_decision


POLICY_VERSION = "R38TK3_FAMILY_CONTRACT_EXIT_V3_TARGET_STOP_STRUCTURAL_TIME"

ELIGIBLE_FAMILIES = frozenset(
    {
        "MIST",
        "MISB",
        "MISC",
        "MISR",
    }
)


class PositionExitPolicyError(ValueError):
    """Raised for invalid exit-policy inputs."""


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    try:
        result = Decimal(text)
    except (InvalidOperation, ValueError):
        return None

    if not result.is_finite():
        return None

    return result


def _positive_decimal(value: Any) -> Decimal | None:
    result = _decimal(value)

    if result is None or result <= 0:
        return None

    return result


def _integer(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, bool):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _text(value: Any) -> str:
    return str(value or "").strip()


def _upper(value: Any) -> str:
    return _text(value).upper()


def _truthy(value: Any) -> bool:
    return _text(value).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True, slots=True)
class ExitPolicy:
    target_points: Decimal = Decimal("5")
    stop_points: Decimal = Decimal("4")
    max_hold_sec: Decimal = Decimal("300")
    max_quote_age_ms: int = 5_000
    signal_change_grace_sec: Decimal = Decimal("20")
    signal_change_confirm_samples: int = 2
    signal_change_enabled: bool = False

    def validate(self) -> None:
        if self.target_points <= 0:
            raise PositionExitPolicyError(
                "target_points must be positive"
            )

        if self.stop_points <= 0:
            raise PositionExitPolicyError(
                "stop_points must be positive"
            )

        if self.max_hold_sec <= 0:
            raise PositionExitPolicyError(
                "max_hold_sec must be positive"
            )

        if self.max_quote_age_ms <= 0:
            raise PositionExitPolicyError(
                "max_quote_age_ms must be positive"
            )

        if self.signal_change_confirm_samples <= 0:
            raise PositionExitPolicyError(
                "signal_change_confirm_samples must be positive"
            )


@dataclass(slots=True)
class ExitTracker:
    position_key: str = ""
    mfe_points: Decimal = Decimal("0")
    mae_points: Decimal = Decimal("0")
    signal_change_samples: int = 0

    def reset(self, position_key: str) -> None:
        self.position_key = position_key
        self.mfe_points = Decimal("0")
        self.mae_points = Decimal("0")
        self.signal_change_samples = 0


@dataclass(frozen=True, slots=True)
class ExitEvaluation:
    should_exit: bool
    blocked: bool
    reason_code: str
    exit_priority: str
    family_id: str
    branch_id: str
    option_symbol: str
    option_token: str
    bid_price: Decimal | None
    ask_price: Decimal | None
    entry_price: Decimal | None
    pnl_points: Decimal | None
    holding_seconds: Decimal | None
    mfe_points: Decimal
    mae_points: Decimal
    quantity_lots: int
    quantity_units: int
    decision: StrategyDecision | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "should_exit": self.should_exit,
            "blocked": self.blocked,
            "reason_code": self.reason_code,
            "exit_priority": self.exit_priority,
            "family_id": self.family_id,
            "branch_id": self.branch_id,
            "option_symbol": self.option_symbol,
            "option_token": self.option_token,
            "bid_price": (
                str(self.bid_price)
                if self.bid_price is not None
                else None
            ),
            "ask_price": (
                str(self.ask_price)
                if self.ask_price is not None
                else None
            ),
            "entry_price": (
                str(self.entry_price)
                if self.entry_price is not None
                else None
            ),
            "pnl_points": (
                str(self.pnl_points)
                if self.pnl_points is not None
                else None
            ),
            "holding_seconds": (
                str(self.holding_seconds)
                if self.holding_seconds is not None
                else None
            ),
            "mfe_points": str(self.mfe_points),
            "mae_points": str(self.mae_points),
            "quantity_lots": self.quantity_lots,
            "quantity_units": self.quantity_units,
            "decision": (
                self.decision.to_dict()
                if self.decision is not None
                else None
            ),
        }


class PositionExitManager:
    """Evaluate target, stop, structural and maximum-hold exits."""

    def __init__(
        self,
        *,
        policy: ExitPolicy | None = None,
    ) -> None:
        self.policy = policy or ExitPolicy()
        self.policy.validate()
        self.tracker = ExitTracker()

    def _blocked(
        self,
        *,
        reason: str,
        family_id: str = "",
        branch_id: str = "",
        option_symbol: str = "",
        option_token: str = "",
        entry_price: Decimal | None = None,
        bid_price: Decimal | None = None,
        ask_price: Decimal | None = None,
        quantity_lots: int = 0,
        quantity_units: int = 0,
    ) -> ExitEvaluation:
        return ExitEvaluation(
            should_exit=False,
            blocked=True,
            reason_code=reason,
            exit_priority="BLOCK",
            family_id=family_id,
            branch_id=branch_id,
            option_symbol=option_symbol,
            option_token=option_token,
            bid_price=bid_price,
            ask_price=ask_price,
            entry_price=entry_price,
            pnl_points=None,
            holding_seconds=None,
            mfe_points=self.tracker.mfe_points,
            mae_points=self.tracker.mae_points,
            quantity_lots=quantity_lots,
            quantity_units=quantity_units,
            decision=None,
        )

    def evaluate(
        self,
        *,
        now_ns: int,
        family_id: str,
        position: Mapping[str, Any],
        quote: Mapping[str, Any],
        signal_changed: bool = False,
    ) -> ExitEvaluation:
        family = _upper(family_id)

        if family not in ELIGIBLE_FAMILIES:
            return self._blocked(
                reason="family_not_exit_manager_eligible",
                family_id=family,
            )

        if not _truthy(position.get("has_position")):
            return self._blocked(
                reason="no_open_position",
                family_id=family,
            )

        position_side = _upper(
            position.get("position_side")
        )

        if position_side == getattr(
            N,
            "POSITION_SIDE_LONG_CALL",
            "LONG_CALL",
        ):
            branch_id = getattr(
                N,
                "BRANCH_CALL",
                "CALL",
            )
        elif position_side == getattr(
            N,
            "POSITION_SIDE_LONG_PUT",
            "LONG_PUT",
        ):
            branch_id = getattr(
                N,
                "BRANCH_PUT",
                "PUT",
            )
        else:
            return self._blocked(
                reason="unsupported_position_side",
                family_id=family,
            )

        quantity_lots = _integer(
            position.get("qty_lots"),
            0,
        )
        quantity_units = _integer(
            position.get("qty_units"),
            0,
        )

        if quantity_lots <= 0 or quantity_units <= 0:
            return self._blocked(
                reason="open_position_quantity_invalid",
                family_id=family,
                branch_id=branch_id,
                quantity_lots=quantity_lots,
                quantity_units=quantity_units,
            )

        option_symbol = _upper(
            position.get("entry_option_symbol")
        )
        option_token = _text(
            position.get("entry_option_token")
        )
        entry_price = _positive_decimal(
            position.get("avg_price")
        )
        entry_ts_ns = _integer(
            position.get("entry_ts_ns"),
            0,
        )

        if (
            not option_symbol
            or not option_token
            or entry_price is None
            or entry_ts_ns <= 0
        ):
            return self._blocked(
                reason="open_position_contract_incomplete",
                family_id=family,
                branch_id=branch_id,
                option_symbol=option_symbol,
                option_token=option_token,
                entry_price=entry_price,
                quantity_lots=quantity_lots,
                quantity_units=quantity_units,
            )

        quote_symbol = _upper(
            quote.get("option_symbol")
            or quote.get("tradingsymbol")
            or quote.get("symbol")
        )
        quote_token = _text(
            quote.get("option_token")
            or quote.get("instrument_token")
            or quote.get("token")
        )

        if quote_symbol != option_symbol:
            return self._blocked(
                reason="exit_quote_symbol_mismatch",
                family_id=family,
                branch_id=branch_id,
                option_symbol=option_symbol,
                option_token=option_token,
                entry_price=entry_price,
                quantity_lots=quantity_lots,
                quantity_units=quantity_units,
            )

        if quote_token != option_token:
            return self._blocked(
                reason="exit_quote_token_mismatch",
                family_id=family,
                branch_id=branch_id,
                option_symbol=option_symbol,
                option_token=option_token,
                entry_price=entry_price,
                quantity_lots=quantity_lots,
                quantity_units=quantity_units,
            )

        bid_price = _positive_decimal(
            quote.get("bid")
            or quote.get("best_bid")
            or quote.get("bid_price")
        )
        ask_price = _positive_decimal(
            quote.get("ask")
            or quote.get("best_ask")
            or quote.get("ask_price")
        )
        quote_ts_ns = _integer(
            quote.get("ts_event_ns")
            or quote.get("ts_ns"),
            0,
        )

        if bid_price is None or ask_price is None:
            return self._blocked(
                reason="exit_quote_bid_ask_missing",
                family_id=family,
                branch_id=branch_id,
                option_symbol=option_symbol,
                option_token=option_token,
                entry_price=entry_price,
                bid_price=bid_price,
                ask_price=ask_price,
                quantity_lots=quantity_lots,
                quantity_units=quantity_units,
            )

        quote_age_ms = (
            now_ns - quote_ts_ns
        ) // 1_000_000

        if (
            quote_ts_ns <= 0
            or quote_age_ms < 0
            or quote_age_ms
            > self.policy.max_quote_age_ms
        ):
            return self._blocked(
                reason="exit_quote_stale",
                family_id=family,
                branch_id=branch_id,
                option_symbol=option_symbol,
                option_token=option_token,
                entry_price=entry_price,
                bid_price=bid_price,
                ask_price=ask_price,
                quantity_lots=quantity_lots,
                quantity_units=quantity_units,
            )

        holding_seconds = Decimal(
            max(0, now_ns - entry_ts_ns)
        ) / Decimal("1000000000")

        pnl_points = bid_price - entry_price

        position_key = "|".join(
            (
                family,
                branch_id,
                option_symbol,
                option_token,
                _text(position.get("decision_id")),
                _text(position.get("broker_order_id")),
            )
        )

        if position_key != self.tracker.position_key:
            self.tracker.reset(position_key)

        self.tracker.mfe_points = max(
            self.tracker.mfe_points,
            pnl_points,
        )
        self.tracker.mae_points = min(
            self.tracker.mae_points,
            pnl_points,
        )

        if signal_changed:
            self.tracker.signal_change_samples += 1
        else:
            self.tracker.signal_change_samples = 0

        should_exit = False
        reason_code = "position_hold"
        exit_priority = "HOLD"

        # Contract priority: target, hard stop, structural exit, time exit.
        if pnl_points >= self.policy.target_points:
            should_exit = True
            reason_code = "target_points"
            exit_priority = "P0_TARGET"
        elif pnl_points <= -self.policy.stop_points:
            should_exit = True
            reason_code = "hard_stop_points"
            exit_priority = "P1_HARD_STOP"
        elif (
            self.policy.signal_change_enabled
            and signal_changed
            and holding_seconds
            >= self.policy.signal_change_grace_sec
            and self.tracker.signal_change_samples
            >= self.policy.signal_change_confirm_samples
        ):
            should_exit = True
            reason_code = "confirmed_signal_change"
            exit_priority = "P2_STRUCTURAL_EXIT"
        elif holding_seconds >= self.policy.max_hold_sec:
            should_exit = True
            reason_code = "max_hold_seconds"
            exit_priority = "P3_TIME_STOP"

        decision: StrategyDecision | None = None

        if should_exit:
            decision = build_exit_decision(
                now_ns=now_ns,
                quantity_lots=quantity_lots,
                family_id=family,
                doctrine_id=family,
                branch_id=branch_id,
                reason_code=reason_code,
                position_effect=getattr(
                    N,
                    "POSITION_EFFECT_CLOSE",
                    "CLOSE",
                ),
                instrument_key=option_token,
                # R38VM_NORMALIZE_PROJECTED_EXIT_ENTRY_MODE: projected paper is a route label,
                # not a valid StrategyDecision entry-mode literal.
                entry_mode=(
                    getattr(N, "ENTRY_MODE_UNKNOWN", "UNKNOWN")
                    if _text(position.get("entry_mode")).upper()
                    == "CONTROLLED_PAPER_PROJECTED"
                    else (
                        _text(position.get("entry_mode"))
                        or getattr(
                            N,
                            "ENTRY_MODE_UNKNOWN",
                            "UNKNOWN",
                        )
                    )
                ),
                explain=reason_code,
                system_state=getattr(
                    N,
                    "STATE_EXIT_PENDING",
                    "EXIT_PENDING",
                ),
                stop_plan={
                    "stop_points":
                        float(self.policy.stop_points),
                    "time_stop_seconds":
                        int(self.policy.max_hold_sec),
                },
                target_plan={
                    "target_points":
                        float(self.policy.target_points),
                },
                extra_metadata={
                    "reason_code": reason_code,
                    "confidence": 1.0,
                    "option_symbol": option_symbol,
                    "option_token": option_token,
                    "instrument_token": option_token,
                    "strike": _text(
                        position.get("entry_strike")
                    ),
                    "limit_price": str(bid_price),
                    "exit_quote_bid": str(bid_price),
                    "exit_quote_ask": str(ask_price),
                    "exit_quote_age_ms":
                        int(quote_age_ms),
                    "entry_price": str(entry_price),
                    "pnl_points": str(pnl_points),
                    "holding_seconds":
                        str(holding_seconds),
                    "mfe_points":
                        str(self.tracker.mfe_points),
                    "mae_points":
                        str(self.tracker.mae_points),
                    "exit_priority": exit_priority,
                    "exit_policy_version":
                        POLICY_VERSION,
                    "signal_change_enabled":
                        self.policy.signal_change_enabled,
                    "signal_change_samples":
                        self.tracker.signal_change_samples,
                    "paper_exit_manager": True,
                    "no_real_live": True,
                    "no_broker_order": True,
                },
            )

        return ExitEvaluation(
            should_exit=should_exit,
            blocked=False,
            reason_code=reason_code,
            exit_priority=exit_priority,
            family_id=family,
            branch_id=branch_id,
            option_symbol=option_symbol,
            option_token=option_token,
            bid_price=bid_price,
            ask_price=ask_price,
            entry_price=entry_price,
            pnl_points=pnl_points,
            holding_seconds=holding_seconds,
            mfe_points=self.tracker.mfe_points,
            mae_points=self.tracker.mae_points,
            quantity_lots=quantity_lots,
            quantity_units=quantity_units,
            decision=decision,
        )


# R38TK2_CANONICAL_EXIT_POSITION_EFFECT_CLOSE_V1

# LANE-X-R38VXFFW: controlled-paper projected exit normalization helper.
def normalize_controlled_paper_projected_exit_side(value: object) -> str:
    """Normalize transient controlled-paper projected exit state to UNKNOWN.

    This helper is intentionally side-effect-free and does not alter Redis,
    risk, execution, order routing, or broker behavior.
    """
    text = "" if value is None else str(value).strip().upper()
    if text in {"CONTROLLED_PAPER_PROJECTED", "PROJECTED", "PAPER_PROJECTED"}:
        return "UNKNOWN"
    return text or "UNKNOWN"
