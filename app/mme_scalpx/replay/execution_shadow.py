from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.mme_scalpx.replay.live_adapter import write_replay_live_state
from app.mme_scalpx.replay.transport import LocalReplayTransport


REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_execution_shadow_v1"

REPLAY_SHADOW_FILL_POLICIES = (
    "FULL_FILL",
    "PARTIAL_FILL",
    "NO_FILL",
    "REJECTED",
)

REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS = (
    "schema_version",
    "run_id",
    "assumption_profile",
    "fill_policy",
    "fill_status",
    "requested_qty",
    "filled_qty",
    "entry_price",
    "exit_price",
    "slippage_points",
    "shadow_position_state",
    "shadow_trade_log",
    "shadow_pnl_summary",
    "real_order_sent",
    "broker_calls_executed",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)


@dataclass(frozen=True)
class ReplayShadowAssumptionProfile:
    fill_policy: str = "FULL_FILL"
    requested_qty: int = 75
    partial_fill_ratio: float = 0.5
    entry_reference_price: float = 100.0
    exit_reference_price: float = 104.0
    slippage_points: float = 0.5
    transaction_cost_points: float = 0.25
    reject_reason: str = "replay_assumption_reject"


def _clamp_qty(value: int | float) -> int:
    return max(0, int(value))


def replay_shadow_assumption_profile(**kwargs: Any) -> dict[str, Any]:
    profile = ReplayShadowAssumptionProfile(**kwargs)
    if profile.fill_policy not in REPLAY_SHADOW_FILL_POLICIES:
        raise ValueError(f"unsupported replay shadow fill_policy: {profile.fill_policy}")
    return {
        "fill_policy": profile.fill_policy,
        "requested_qty": int(profile.requested_qty),
        "partial_fill_ratio": float(profile.partial_fill_ratio),
        "entry_reference_price": float(profile.entry_reference_price),
        "exit_reference_price": float(profile.exit_reference_price),
        "slippage_points": float(profile.slippage_points),
        "transaction_cost_points": float(profile.transaction_cost_points),
        "reject_reason": str(profile.reject_reason),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
    }


def simulate_replay_execution_shadow(
    *,
    run_id: str,
    strategy_decision: Mapping[str, Any],
    risk_decision: Mapping[str, Any],
    assumption_profile: Mapping[str, Any],
) -> dict[str, Any]:
    fill_policy = str(assumption_profile.get("fill_policy", "FULL_FILL"))
    if fill_policy not in REPLAY_SHADOW_FILL_POLICIES:
        raise ValueError(f"unsupported replay shadow fill_policy: {fill_policy}")

    requested_qty = _clamp_qty(assumption_profile.get("requested_qty", 0))
    partial_ratio = max(0.0, min(1.0, float(assumption_profile.get("partial_fill_ratio", 0.5))))
    entry_ref = float(assumption_profile.get("entry_reference_price", 100.0))
    exit_ref = float(assumption_profile.get("exit_reference_price", entry_ref))
    slippage = float(assumption_profile.get("slippage_points", 0.0))
    costs = float(assumption_profile.get("transaction_cost_points", 0.0))

    research_allowed = risk_decision.get("research_trade_allowed") is True
    risk_vetoed = risk_decision.get("entry_vetoed") is True

    if risk_vetoed or not research_allowed:
        fill_status = "RISK_VETOED"
        filled_qty = 0
    elif fill_policy == "FULL_FILL":
        fill_status = "FILLED"
        filled_qty = requested_qty
    elif fill_policy == "PARTIAL_FILL":
        fill_status = "PARTIAL_FILLED"
        filled_qty = _clamp_qty(requested_qty * partial_ratio)
    elif fill_policy == "NO_FILL":
        fill_status = "NO_FILL"
        filled_qty = 0
    else:
        fill_status = "REJECTED"
        filled_qty = 0

    entry_price = entry_ref + slippage if filled_qty else None
    exit_price = exit_ref - slippage if filled_qty else None
    gross_points = (exit_price - entry_price) if filled_qty and entry_price is not None and exit_price is not None else 0.0
    net_points = gross_points - costs if filled_qty else 0.0
    net_pnl = net_points * filled_qty

    winning_family = None
    winning_side = None
    arbitration = strategy_decision.get("arbitration")
    if isinstance(arbitration, Mapping):
        winning_family = arbitration.get("winning_family")
        winning_side = arbitration.get("winning_side")

    shadow_trade = {
        "schema_version": "replay_shadow_trade_v1",
        "run_id": str(run_id),
        "winning_family": winning_family,
        "winning_side": winning_side,
        "fill_policy": fill_policy,
        "fill_status": fill_status,
        "requested_qty": requested_qty,
        "filled_qty": filled_qty,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "gross_points": gross_points,
        "transaction_cost_points": costs,
        "net_points": net_points,
        "net_pnl": net_pnl,
        "real_order_sent": False,
        "broker_calls_executed": False,
    }

    position_state = {
        "schema_version": "replay_shadow_position_v1",
        "run_id": str(run_id),
        "position_opened": filled_qty > 0,
        "position_closed": filled_qty > 0,
        "net_qty": 0,
        "filled_qty": filled_qty,
        "side": winning_side,
        "family": winning_family,
        "real_position_mutated": False,
    }

    pnl_summary = {
        "schema_version": "replay_shadow_pnl_summary_v1",
        "run_id": str(run_id),
        "trade_count": 1 if filled_qty else 0,
        "filled_qty": filled_qty,
        "gross_points": gross_points,
        "net_points": net_points,
        "net_pnl": net_pnl,
        "is_profit": net_pnl > 0,
        "is_loss": net_pnl < 0,
    }

    payload = {
        "schema_version": REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION,
        "run_id": str(run_id),
        "assumption_profile": dict(assumption_profile),
        "fill_policy": fill_policy,
        "fill_status": fill_status,
        "requested_qty": requested_qty,
        "filled_qty": filled_qty,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "slippage_points": slippage,
        "shadow_position_state": position_state,
        "shadow_trade_log": (shadow_trade,),
        "shadow_pnl_summary": pnl_summary,
        "risk_vetoed": risk_vetoed,
        "research_trade_allowed": research_allowed,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
        "execution_shadow_shape": "PROVEN_BY_27I",
        "real_execution_parity": "NOT_PROVEN_IN_27I",
    }
    return payload


def validate_replay_execution_shadow(payload: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(field for field in REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS if field not in payload)
    fill_policy_ok = payload.get("fill_policy") in REPLAY_SHADOW_FILL_POLICIES
    no_real_order_ok = (
        payload.get("real_order_sent") is False
        and payload.get("broker_calls_executed") is False
        and payload.get("live_redis_writes_executed") is False
        and payload.get("paper_armed_approved") is False
        and payload.get("live_trading_approved") is False
        and payload.get("execution_arming_created") is False
        and payload.get("production_doctrine_changed") is False
    )
    pnl_ok = isinstance(payload.get("shadow_pnl_summary"), Mapping)
    trade_log_ok = isinstance(payload.get("shadow_trade_log"), tuple)
    position_ok = isinstance(payload.get("shadow_position_state"), Mapping)
    ok = bool(not missing and fill_policy_ok and no_real_order_ok and pnl_ok and trade_log_ok and position_ok)
    return {
        "ok": ok,
        "missing": missing,
        "fill_policy_ok": fill_policy_ok,
        "no_real_order_ok": no_real_order_ok,
        "pnl_ok": pnl_ok,
        "trade_log_ok": trade_log_ok,
        "position_ok": position_ok,
    }


def publish_replay_execution_shadow(
    transport: LocalReplayTransport,
    *,
    run_id: str,
    execution_shadow: Mapping[str, Any],
    updated_ts_ns: int | None = None,
) -> dict[str, Any]:
    validation = validate_replay_execution_shadow(execution_shadow)
    if not validation["ok"]:
        raise ValueError(f"invalid replay execution shadow: {validation}")
    return write_replay_live_state(
        transport,
        surface="execution_shadow",
        row=dict(execution_shadow),
        updated_ts_ns=updated_ts_ns,
    )


def replay_execution_shadow_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION,
        "fill_policies": REPLAY_SHADOW_FILL_POLICIES,
        "required_fields": REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS,
        "execution_shadow_shape": "PROVEN_BY_27I",
        "pnl_shadow_math": "PROVEN_BY_27I",
        "real_execution_parity": "NOT_PROVEN_IN_27I",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION",
    "REPLAY_SHADOW_FILL_POLICIES",
    "REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS",
    "ReplayShadowAssumptionProfile",
    "replay_shadow_assumption_profile",
    "simulate_replay_execution_shadow",
    "validate_replay_execution_shadow",
    "publish_replay_execution_shadow",
    "replay_execution_shadow_contract_summary",
)))
