"""Report-only controlled-paper route observability surface.

This module is intentionally side-effect free. It does not start services, touch
Redis, call brokers, publish decisions, write order streams, place paper orders,
or mutate position/order state.

A6-PAPER-R7 wires the R4 fail-closed guard into an import-safe observability
surface only. Runtime integration, risk/execution start, and any paper order path
require later explicit approvals and proofs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from app.mme_scalpx.services.controlled_paper_route import (
    ControlledPaperRouteVerdict,
    evaluate_controlled_paper_route_env,
)


CONTROLLED_PAPER_OBSERVABILITY_VERSION = "a6_paper_r7_report_only_v1"


@dataclass(frozen=True)
class ControlledPaperSafetyFacts:
    """External safety facts supplied by a caller.

    The class is pure data. It never reads Redis, process lists, files, broker
    state, or environment variables on its own.
    """

    orders_zero: bool
    position_flat: bool
    risk_execution_absent: bool
    lock_execution_absent: bool | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "orders_zero": self.orders_zero,
            "position_flat": self.position_flat,
            "risk_execution_absent": self.risk_execution_absent,
            "lock_execution_absent": self.lock_execution_absent,
        }


@dataclass(frozen=True)
class ControlledPaperRouteObservation:
    """Report-only observation for diagnostics/readiness surfaces."""

    version: str
    route_allowed: bool
    route_reason: str
    verdict: ControlledPaperRouteVerdict
    safety: ControlledPaperSafetyFacts
    report_only: bool = True
    order_intent_allowed: bool = False
    broker_call_allowed: bool = False
    risk_execution_start_allowed: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "report_only": self.report_only,
            "route_allowed": self.route_allowed,
            "route_reason": self.route_reason,
            "verdict": self.verdict.as_dict(),
            "safety": self.safety.as_dict(),
            "order_intent_allowed": self.order_intent_allowed,
            "broker_call_allowed": self.broker_call_allowed,
            "risk_execution_start_allowed": self.risk_execution_start_allowed,
        }


def build_controlled_paper_route_observation(
    env: Mapping[str, object],
    *,
    safety: ControlledPaperSafetyFacts,
) -> ControlledPaperRouteObservation:
    """Build a pure report-only controlled-paper route observation.

    This function may return ``route_allowed=True`` only to report that the pure
    gate would pass. It still keeps order/broker/risk-execution action booleans
    false because R7 is observability-only and not an execution route.
    """

    verdict = evaluate_controlled_paper_route_env(
        env,
        position_flat=safety.position_flat,
        risk_execution_absent=safety.risk_execution_absent,
        orders_zero=safety.orders_zero,
    )
    return ControlledPaperRouteObservation(
        version=CONTROLLED_PAPER_OBSERVABILITY_VERSION,
        route_allowed=verdict.allowed,
        route_reason=verdict.reason,
        verdict=verdict,
        safety=safety,
        report_only=True,
        order_intent_allowed=False,
        broker_call_allowed=False,
        risk_execution_start_allowed=False,
    )


def build_fail_closed_controlled_paper_observation() -> ControlledPaperRouteObservation:
    """Return canonical fail-closed report-only observation."""

    return build_controlled_paper_route_observation(
        {},
        safety=ControlledPaperSafetyFacts(
            orders_zero=False,
            position_flat=False,
            risk_execution_absent=False,
            lock_execution_absent=None,
        ),
    )
