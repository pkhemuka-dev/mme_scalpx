from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.mme_scalpx.replay.live_adapter import write_replay_live_state
from app.mme_scalpx.replay.transport import LocalReplayTransport


REPLAY_RISK_ADAPTER_CONTRACT_VERSION = "replay_risk_adapter_v1"

REPLAY_RISK_REQUIRED_FIELDS = (
    "schema_version",
    "run_id",
    "risk_evaluated",
    "research_trade_allowed",
    "entry_vetoed",
    "veto_reasons",
    "risk_score",
    "max_loss_points",
    "max_slippage_points",
    "order_allowed",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)


@dataclass(frozen=True)
class ReplayRiskDecision:
    schema_version: str
    run_id: str
    risk_evaluated: bool
    research_trade_allowed: bool
    entry_vetoed: bool
    veto_reasons: tuple[str, ...]
    risk_score: float
    max_loss_points: float
    max_slippage_points: float
    order_allowed: bool = False
    real_order_intent_generated: bool = False
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    production_doctrine_changed: bool = False


def build_replay_risk_decision(
    *,
    run_id: str,
    strategy_decision: Mapping[str, Any],
    max_loss_points: float = 12.0,
    max_slippage_points: float = 2.0,
    force_veto_reasons: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    arbitration = dict(strategy_decision.get("arbitration") or {})
    winner = arbitration.get("winner")
    final_action = strategy_decision.get("final_action") or strategy_decision.get("action")
    veto_reasons: list[str] = []

    if final_action != "HOLD_REPORT_ONLY":
        veto_reasons.append("non_hold_report_action_forbidden_in_replay")
    if strategy_decision.get("order_allowed") is not False:
        veto_reasons.append("strategy_order_allowed_not_false")
    if strategy_decision.get("real_order_intent_generated") is not False:
        veto_reasons.append("real_order_intent_not_false")
    if not winner:
        veto_reasons.append("no_research_winner")
    if force_veto_reasons:
        veto_reasons.extend(str(x) for x in force_veto_reasons)

    risk_score = float(winner.get("score", 0.0)) if isinstance(winner, Mapping) else 0.0
    entry_vetoed = bool(veto_reasons)

    decision = ReplayRiskDecision(
        schema_version=REPLAY_RISK_ADAPTER_CONTRACT_VERSION,
        run_id=str(run_id),
        risk_evaluated=True,
        research_trade_allowed=bool(winner) and not entry_vetoed,
        entry_vetoed=entry_vetoed,
        veto_reasons=tuple(veto_reasons),
        risk_score=risk_score,
        max_loss_points=float(max_loss_points),
        max_slippage_points=float(max_slippage_points),
    )
    return {
        "schema_version": decision.schema_version,
        "run_id": decision.run_id,
        "risk_evaluated": decision.risk_evaluated,
        "research_trade_allowed": decision.research_trade_allowed,
        "entry_vetoed": decision.entry_vetoed,
        "veto_reasons": decision.veto_reasons,
        "risk_score": decision.risk_score,
        "max_loss_points": decision.max_loss_points,
        "max_slippage_points": decision.max_slippage_points,
        "order_allowed": decision.order_allowed,
        "real_order_intent_generated": decision.real_order_intent_generated,
        "paper_armed_approved": decision.paper_armed_approved,
        "live_trading_approved": decision.live_trading_approved,
        "execution_arming_created": decision.execution_arming_created,
        "production_doctrine_changed": decision.production_doctrine_changed,
        "risk_parity": "NOT_PROVEN_IN_27I",
        "risk_shape_parity": "PROVEN_BY_27I",
    }


def validate_replay_risk_decision(decision: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(field for field in REPLAY_RISK_REQUIRED_FIELDS if field not in decision)
    no_order_ok = (
        decision.get("order_allowed") is False
        and decision.get("real_order_intent_generated") is False
        and decision.get("paper_armed_approved") is False
        and decision.get("live_trading_approved") is False
        and decision.get("execution_arming_created") is False
        and decision.get("production_doctrine_changed") is False
    )
    ok = bool(not missing and decision.get("risk_evaluated") is True and no_order_ok)
    return {
        "ok": ok,
        "missing": missing,
        "no_order_ok": no_order_ok,
        "risk_evaluated": decision.get("risk_evaluated") is True,
    }


def publish_replay_risk_shadow(
    transport: LocalReplayTransport,
    *,
    run_id: str,
    risk_decision: Mapping[str, Any],
    updated_ts_ns: int | None = None,
) -> dict[str, Any]:
    validation = validate_replay_risk_decision(risk_decision)
    if not validation["ok"]:
        raise ValueError(f"invalid replay risk decision: {validation}")
    return write_replay_live_state(
        transport,
        surface="risk_shadow",
        row=dict(risk_decision),
        updated_ts_ns=updated_ts_ns,
    )


def replay_risk_adapter_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_RISK_ADAPTER_CONTRACT_VERSION,
        "required_fields": REPLAY_RISK_REQUIRED_FIELDS,
        "risk_shape_parity": "PROVEN_BY_27I",
        "real_risk_parity": "NOT_PROVEN_IN_27I",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "order_allowed": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_RISK_ADAPTER_CONTRACT_VERSION",
    "REPLAY_RISK_REQUIRED_FIELDS",
    "ReplayRiskDecision",
    "build_replay_risk_decision",
    "validate_replay_risk_decision",
    "publish_replay_risk_shadow",
    "replay_risk_adapter_contract_summary",
)))
