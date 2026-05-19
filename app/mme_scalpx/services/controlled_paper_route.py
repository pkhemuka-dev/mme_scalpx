"""Fail-closed controlled-paper route guard surface.

This module is intentionally side-effect free. It does not start services, touch
Redis, call brokers, place paper orders, or mutate position/order state.

A6-PAPER-R4 adds this as an additive guard surface only. Runtime wiring and any
paper execution path require separate approvals and later proofs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

ENV_OBSERVE_ONLY = "SCALPX_OBSERVE_ONLY"
ENV_ALLOW_CONTROLLED_PAPER_RUNTIME = "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"
ENV_CONTROLLED_PAPER_SCOPE_ACK = "SCALPX_CONTROLLED_PAPER_SCOPE_ACK"
ENV_REAL_LIVE_ALLOWED = "SCALPX_REAL_LIVE_ALLOWED"
ENV_ALLOW_REAL_LIVE = "SCALPX_ALLOW_REAL_LIVE"
ENV_ALLOW_BROKER_ORDERS = "SCALPX_ALLOW_BROKER_ORDERS"
ENV_PAPER_ARMED = "SCALPX_PAPER_ARMED"
ENV_ENABLE_PAPER = "SCALPX_ENABLE_PAPER"
ENV_ENABLE_LIVE = "SCALPX_ENABLE_LIVE"

CONTROLLED_PAPER_SCOPE_ACK_EXPECTED = (
    "I ACKNOWLEDGE CONTROLLED PAPER ONLY: "
    "NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, "
    "ONE APPROVED SCOPE ONLY, POSITION MUST START FLAT"
)

TRUTHY_VALUES = frozenset({"1", "true", "yes", "y", "on"})
LIVE_AND_BROKER_BLOCK_FLAGS = (
    ENV_REAL_LIVE_ALLOWED,
    ENV_ALLOW_REAL_LIVE,
    ENV_ALLOW_BROKER_ORDERS,
    ENV_ENABLE_LIVE,
)


@dataclass(frozen=True)
class ControlledPaperRouteVerdict:
    """Pure-data result for controlled-paper route gating."""

    allowed: bool
    reason: str
    observe_only: bool
    paper_enabled: bool
    paper_armed: bool
    controlled_runtime_allowed: bool
    scope_ack_ok: bool
    broker_live_blocked: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "observe_only": self.observe_only,
            "paper_enabled": self.paper_enabled,
            "paper_armed": self.paper_armed,
            "controlled_runtime_allowed": self.controlled_runtime_allowed,
            "scope_ack_ok": self.scope_ack_ok,
            "broker_live_blocked": self.broker_live_blocked,
        }


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in TRUTHY_VALUES


def _env_truthy(env: Mapping[str, object], name: str) -> bool:
    return _truthy(env.get(name))


def evaluate_controlled_paper_route_env(
    env: Mapping[str, object],
    *,
    position_flat: bool,
    risk_execution_absent: bool,
    orders_zero: bool,
) -> ControlledPaperRouteVerdict:
    """Evaluate controlled-paper route eligibility without side effects.

    The default is fail-closed. This function only returns ``allowed=True`` when
    every explicit paper gate is present, live/broker flags are blocked, and the
    external safety facts prove flat/no-risk/no-orders.
    """

    observe_only = _env_truthy(env, ENV_OBSERVE_ONLY)
    controlled_runtime_allowed = _env_truthy(env, ENV_ALLOW_CONTROLLED_PAPER_RUNTIME)
    paper_enabled = _env_truthy(env, ENV_ENABLE_PAPER)
    paper_armed = _env_truthy(env, ENV_PAPER_ARMED)
    scope_ack_ok = str(env.get(ENV_CONTROLLED_PAPER_SCOPE_ACK, "")).strip() == CONTROLLED_PAPER_SCOPE_ACK_EXPECTED
    broker_live_blocked = not any(_env_truthy(env, name) for name in LIVE_AND_BROKER_BLOCK_FLAGS)

    if observe_only:
        return ControlledPaperRouteVerdict(False, "OBSERVE_ONLY_ACTIVE", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not controlled_runtime_allowed:
        return ControlledPaperRouteVerdict(False, "CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not scope_ack_ok:
        return ControlledPaperRouteVerdict(False, "CONTROLLED_PAPER_SCOPE_ACK_MISSING_OR_INVALID", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not paper_enabled:
        return ControlledPaperRouteVerdict(False, "PAPER_NOT_ENABLED", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not paper_armed:
        return ControlledPaperRouteVerdict(False, "PAPER_NOT_ARMED", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not broker_live_blocked:
        return ControlledPaperRouteVerdict(False, "BROKER_OR_LIVE_FLAG_ACTIVE", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not orders_zero:
        return ControlledPaperRouteVerdict(False, "ORDERS_STREAM_NOT_ZERO", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not position_flat:
        return ControlledPaperRouteVerdict(False, "POSITION_NOT_FLAT", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)
    if not risk_execution_absent:
        return ControlledPaperRouteVerdict(False, "RISK_OR_EXECUTION_ALREADY_RUNNING", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)

    return ControlledPaperRouteVerdict(True, "CONTROLLED_PAPER_ROUTE_ALLOWED_BY_GATES", observe_only, paper_enabled, paper_armed, controlled_runtime_allowed, scope_ack_ok, broker_live_blocked)


def build_fail_closed_controlled_paper_verdict() -> ControlledPaperRouteVerdict:
    """Return the canonical no-env fail-closed verdict."""

    return evaluate_controlled_paper_route_env(
        {},
        position_flat=False,
        risk_execution_absent=False,
        orders_zero=False,
    )
