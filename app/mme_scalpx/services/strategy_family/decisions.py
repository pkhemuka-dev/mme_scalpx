from __future__ import annotations

"""
app/mme_scalpx/strategy_family/decisions.py

Shared canonical StrategyDecision builders for doctrine extraction.

Purpose
-------
This module OWNS:
- family-neutral StrategyDecision construction helpers
- canonical entry / exit / hold builders for doctrine outputs
- stop/target-plan conversion from doctrine candidates

This module DOES NOT own:
- Redis publication
- broker truth
- risk truth mutation
- doctrine-specific signal logic
"""

from typing import Any, Mapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core.models import StopPlan, StrategyDecision, TargetPlan

from .common import new_id, side_for_branch, strategy_mode_for_branch
from .doctrine_runtime import DoctrineBlocker, DoctrineSignalCandidate


def _metadata(reason_code: str | None, extra_metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if reason_code is not None:
        payload["reason_code"] = reason_code
    if extra_metadata:
        payload.update(dict(extra_metadata))
    return payload


def _target_plan_from_candidate(candidate: DoctrineSignalCandidate) -> TargetPlan:
    meta = dict(candidate.metadata)
    target_points = candidate.target_points
    trail_after_points = meta.get("trail_after_points")
    trail_step_points = meta.get("trail_step_points")
    target_price = meta.get("target_price")
    return TargetPlan(
        target_price=float(target_price) if target_price is not None else None,
        target_points=float(target_points) if target_points is not None else None,
        trail_after_points=float(trail_after_points) if trail_after_points is not None else None,
        trail_step_points=float(trail_step_points) if trail_step_points is not None else None,
    )


def _stop_plan_from_candidate(candidate: DoctrineSignalCandidate) -> StopPlan:
    meta = dict(candidate.metadata)
    stop_points = candidate.stop_points
    stop_price = meta.get("stop_price")
    time_stop_seconds = meta.get("time_stop_seconds")
    adverse_exit_seconds = meta.get("adverse_exit_seconds")
    return StopPlan(
        stop_price=float(stop_price) if stop_price is not None else None,
        stop_points=float(stop_points) if stop_points is not None else None,
        time_stop_seconds=int(time_stop_seconds) if time_stop_seconds is not None else None,
        adverse_exit_seconds=int(adverse_exit_seconds) if adverse_exit_seconds is not None else None,
    )


def build_entry_decision(
    *,
    now_ns: int,
    quantity_lots: int,
    candidate: DoctrineSignalCandidate,
    explain: str | None = None,
    system_state: str = N.STATE_ENTRY_PENDING,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    action = N.ACTION_ENTER_CALL if candidate.branch_id == N.BRANCH_CALL else N.ACTION_ENTER_PUT
    metadata = _metadata(explain, candidate.metadata)
    if extra_metadata:
        metadata.update(dict(extra_metadata))

    return StrategyDecision(
        decision_id=new_id("dec"),
        ts_event_ns=now_ns,
        ts_expiry_ns=None,
        action=action,
        side=candidate.side,
        position_effect=N.POSITION_EFFECT_OPEN,
        quantity_lots=max(1, int(quantity_lots)),
        instrument_key=candidate.instrument_key,
        strategy_family_id=candidate.family_id,
        doctrine_id=candidate.doctrine_id,
        branch_id=candidate.branch_id,
        family_runtime_mode=candidate.family_runtime_mode,
        strategy_runtime_mode=candidate.strategy_runtime_mode,
        source_event_id=candidate.source_event_id,
        trap_event_id=candidate.trap_event_id,
        burst_event_id=candidate.burst_event_id,
        active_futures_provider_id=active_futures_provider_id,
        active_selected_option_provider_id=active_selected_option_provider_id,
        active_option_context_provider_id=active_option_context_provider_id,
        entry_mode=candidate.entry_mode,
        strategy_mode=strategy_mode_for_branch(candidate.branch_id),
        system_state=system_state,
        explain=explain,
        blocker_code=None,
        blocker_message=None,
        stop_plan=_stop_plan_from_candidate(candidate),
        target_plan=_target_plan_from_candidate(candidate),
        metadata=metadata,
    )


def build_exit_decision(
    *,
    now_ns: int,
    quantity_lots: int,
    reason_code: str,
    family_id: str,
    doctrine_id: str,
    branch_id: str,
    instrument_key: str | None,
    family_runtime_mode: str | None,
    strategy_runtime_mode: str | None,
    source_event_id: str | None = None,
    trap_event_id: str | None = None,
    burst_event_id: str | None = None,
    entry_mode: str = N.ENTRY_MODE_UNKNOWN,
    explain: str | None = None,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    side = side_for_branch(branch_id)
    metadata = _metadata(reason_code, extra_metadata)

    return StrategyDecision(
        decision_id=new_id("dec"),
        ts_event_ns=now_ns,
        ts_expiry_ns=None,
        action=N.ACTION_EXIT,
        side=side,
        position_effect=N.POSITION_EFFECT_FLATTEN,
        quantity_lots=max(0, int(quantity_lots)),
        instrument_key=instrument_key,
        strategy_family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=branch_id,
        family_runtime_mode=family_runtime_mode,
        strategy_runtime_mode=strategy_runtime_mode,
        source_event_id=source_event_id,
        trap_event_id=trap_event_id,
        burst_event_id=burst_event_id,
        active_futures_provider_id=active_futures_provider_id,
        active_selected_option_provider_id=active_selected_option_provider_id,
        active_option_context_provider_id=active_option_context_provider_id,
        entry_mode=entry_mode,
        strategy_mode=strategy_mode_for_branch(branch_id),
        system_state=N.STATE_EXIT_PENDING,
        explain=explain or reason_code,
        blocker_code=None,
        blocker_message=None,
        stop_plan=StopPlan(),
        target_plan=TargetPlan(),
        metadata=metadata,
    )


def build_hold_decision(
    *,
    now_ns: int,
    side: str,
    family_id: str | None = None,
    doctrine_id: str | None = None,
    branch_id: str | None = None,
    family_runtime_mode: str | None = None,
    strategy_runtime_mode: str | None = None,
    reason_code: str | None = None,
    explain: str | None = None,
    blocker: DoctrineBlocker | None = None,
    system_state: str = N.STATE_WAIT,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    metadata = _metadata(reason_code, extra_metadata)

    return StrategyDecision(
        decision_id=new_id("dec"),
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
        source_event_id=None,
        trap_event_id=None,
        burst_event_id=None,
        active_futures_provider_id=active_futures_provider_id,
        active_selected_option_provider_id=active_selected_option_provider_id,
        active_option_context_provider_id=active_option_context_provider_id,
        entry_mode=N.ENTRY_MODE_UNKNOWN,
        strategy_mode=(strategy_mode_for_branch(branch_id) if branch_id is not None else N.STRATEGY_AUTO),
        system_state=system_state,
        explain=explain or reason_code,
        blocker_code=(blocker.code if blocker is not None else reason_code),
        blocker_message=(blocker.message if blocker is not None else explain or reason_code),
        stop_plan=None,
        target_plan=None,
        metadata=metadata,
    )


def build_blocked_hold_decision(
    *,
    now_ns: int,
    branch_id: str,
    family_id: str,
    doctrine_id: str,
    family_runtime_mode: str | None,
    strategy_runtime_mode: str | None,
    blocker: DoctrineBlocker,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    return build_hold_decision(
        now_ns=now_ns,
        side=side_for_branch(branch_id),
        family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=branch_id,
        family_runtime_mode=family_runtime_mode,
        strategy_runtime_mode=strategy_runtime_mode,
        reason_code=blocker.code,
        explain=blocker.message,
        blocker=blocker,
        system_state=N.STATE_WAIT,
        extra_metadata=extra_metadata,
    )


__all__ = [
    "build_blocked_hold_decision",
    "build_entry_decision",
    "build_exit_decision",
    "build_hold_decision",
]
