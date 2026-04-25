from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/decisions.py

Freeze-grade canonical StrategyDecision builders for strategy-family doctrine
evaluation.

Purpose
-------
This module OWNS:
- deterministic StrategyDecision construction helpers for strategy-family leaves
- canonical conversion from doctrine candidates / doctrine action requests into
  core.models.StrategyDecision payloads
- strict stop/target-plan normalization from doctrine metadata
- hold / block / entry / exit decision builders used by thin strategy-family
  orchestration

This module DOES NOT own:
- Redis reads or writes
- live publication
- broker truth
- risk truth mutation
- feature math
- doctrine scoring
- arbitration
- state-machine transition ownership

Design rules
------------
- This module must only construct typed StrategyDecision payloads.
- It must align exactly with canonical names.py and models.py surfaces.
- It must not invent new action, side, mode, or state vocabularies.
- It must be deterministic, side-effect free, and replay-safe.
- Bad stop/target metadata must fail fast rather than silently degrade to zero.
"""

import hashlib
import json
import math
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core.models import StopPlan, StrategyDecision, TargetPlan

from .common import (
    normalize_reason,
    safe_str,
    side_for_branch,
    strategy_mode_for_branch,
)
from .doctrine_runtime import (
    DoctrineActionRequest,
    DoctrineBlocker,
    DoctrineSignalCandidate,
)

_ALLOWED_ENTRY_ACTIONS: Final[tuple[str, ...]] = (
    N.ACTION_ENTER_CALL,
    N.ACTION_ENTER_PUT,
)

_ALLOWED_HOLDISH_ACTIONS: Final[tuple[str, ...]] = (
    N.ACTION_HOLD,
    N.ACTION_BLOCK,
)

_ALLOWED_EXIT_POSITION_EFFECTS: Final[tuple[str, ...]] = (
    N.POSITION_EFFECT_CLOSE,
    N.POSITION_EFFECT_REDUCE,
    N.POSITION_EFFECT_FLATTEN,
)

_ALLOWED_OPTION_SIDES: Final[tuple[str, ...]] = (
    N.SIDE_CALL,
    N.SIDE_PUT,
)

_ALLOWED_BRANCH_IDS: Final[tuple[str, ...]] = (
    N.BRANCH_CALL,
    N.BRANCH_PUT,
)

_ALLOWED_DECISION_ACTIONS: Final[tuple[str, ...]] = (
    N.ACTION_ENTER_CALL,
    N.ACTION_ENTER_PUT,
    N.ACTION_EXIT,
    N.ACTION_HOLD,
    N.ACTION_BLOCK,
)


# ============================================================================
# Exceptions / small helpers
# ============================================================================


class StrategyFamilyDecisionError(ValueError):
    """Raised when a strategy-family decision helper receives invalid input."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StrategyFamilyDecisionError(message)


def _require_non_empty_str(value: Any, field_name: str) -> str:
    text = safe_str(value, "")
    if not text:
        raise StrategyFamilyDecisionError(f"{field_name} must be non-empty str")
    return text


def _clean_optional_str(value: Any) -> str | None:
    text = safe_str(value, "")
    return text or None


def _require_literal(value: Any, field_name: str, allowed: tuple[str, ...]) -> str:
    text = _require_non_empty_str(value, field_name)
    if text not in allowed:
        raise StrategyFamilyDecisionError(
            f"{field_name} must be one of {allowed!r}, got {text!r}"
        )
    return text


def _require_non_negative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise StrategyFamilyDecisionError(f"{field_name} must be int")
    if value < 0:
        raise StrategyFamilyDecisionError(f"{field_name} must be >= 0")
    return value


def _require_positive_int(value: Any, field_name: str) -> int:
    result = _require_non_negative_int(value, field_name)
    if result <= 0:
        raise StrategyFamilyDecisionError(f"{field_name} must be > 0")
    return result


def _require_non_negative_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise StrategyFamilyDecisionError(f"{field_name} must be float|int")
    out = float(value)
    if not math.isfinite(out):
        raise StrategyFamilyDecisionError(f"{field_name} must be finite")
    if out < 0.0:
        raise StrategyFamilyDecisionError(f"{field_name} must be >= 0")
    return out


def _optional_non_negative_float(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    return _require_non_negative_float(value, field_name)


def _optional_non_negative_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    return _require_non_negative_int(value, field_name)


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise StrategyFamilyDecisionError(f"{field_name} must be a mapping")
    return value


def _validate_branch_side(branch_id: str, side: str) -> None:
    normalized_branch = _require_literal(
        branch_id,
        "branch_id",
        allowed=_ALLOWED_BRANCH_IDS,
    )
    normalized_side = _require_literal(
        side,
        "side",
        allowed=_ALLOWED_OPTION_SIDES,
    )
    expected_side = side_for_branch(normalized_branch)
    _require(
        normalized_side == expected_side,
        f"side {normalized_side!r} must match branch_id {normalized_branch!r}",
    )


def _entry_action_for_branch(branch_id: str) -> str:
    normalized_branch = _require_literal(
        branch_id,
        "branch_id",
        allowed=_ALLOWED_BRANCH_IDS,
    )
    if normalized_branch == N.BRANCH_CALL:
        return N.ACTION_ENTER_CALL
    return N.ACTION_ENTER_PUT


def _branch_for_entry_action(action: str) -> str:
    normalized_action = _require_literal(
        action,
        "action",
        allowed=_ALLOWED_ENTRY_ACTIONS,
    )
    if normalized_action == N.ACTION_ENTER_CALL:
        return N.BRANCH_CALL
    return N.BRANCH_PUT


def _plain_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise StrategyFamilyDecisionError("metadata contains non-finite float")
        return value
    if isinstance(value, StopPlan):
        return {
            "stop_price": value.stop_price,
            "stop_points": value.stop_points,
            "time_stop_seconds": value.time_stop_seconds,
            "adverse_exit_seconds": value.adverse_exit_seconds,
        }
    if isinstance(value, TargetPlan):
        return {
            "target_price": value.target_price,
            "target_points": value.target_points,
            "trail_after_points": value.trail_after_points,
            "trail_step_points": value.trail_step_points,
        }
    if isinstance(value, Mapping):
        return {
            str(k): _plain_value(v)
            for k, v in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_plain_value(v) for v in value]
    if isinstance(value, set):
        return sorted(_plain_value(v) for v in value)
    return str(value)


def _stable_decision_id(prefix: str, payload: Mapping[str, Any]) -> str:
    stem = safe_str(prefix, "dec").replace(" ", "_")
    material = json.dumps(
        _plain_value(dict(payload)),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]
    return f"{stem}-{digest}"


def _as_metadata(extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not extra:
        return {}
    source = _require_mapping(extra, "extra_metadata")
    return {str(k): _plain_value(v) for k, v in source.items()}


def _merge_metadata(
    *parts: Mapping[str, Any] | None,
    reason_code: str | None = None,
) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    if reason_code:
        merged["reason_code"] = normalize_reason(reason_code)
    for part in parts:
        if part:
            merged.update(_as_metadata(part))
    return merged


def _decision(
    *,
    prefix: str = "dec",
    **decision_data: Any,
) -> StrategyDecision:
    decision_id = _stable_decision_id(prefix, decision_data)
    return StrategyDecision(decision_id=decision_id, **decision_data)


def _normalize_target_plan_mapping(raw: Mapping[str, Any] | None) -> TargetPlan | None:
    if raw is None:
        return None
    data = dict(_require_mapping(raw, "target_plan"))
    target_price = _optional_non_negative_float(data.get("target_price"), "target_price")
    target_points = _optional_non_negative_float(data.get("target_points"), "target_points")
    trail_after_points = _optional_non_negative_float(
        data.get("trail_after_points"),
        "trail_after_points",
    )
    trail_step_points = _optional_non_negative_float(
        data.get("trail_step_points"),
        "trail_step_points",
    )
    if (
        target_price is None
        and target_points is None
        and trail_after_points is None
        and trail_step_points is None
    ):
        return None
    return TargetPlan(
        target_price=target_price,
        target_points=target_points,
        trail_after_points=trail_after_points,
        trail_step_points=trail_step_points,
    )


def _normalize_stop_plan_mapping(raw: Mapping[str, Any] | None) -> StopPlan | None:
    if raw is None:
        return None
    data = dict(_require_mapping(raw, "stop_plan"))
    stop_price = _optional_non_negative_float(data.get("stop_price"), "stop_price")
    stop_points = _optional_non_negative_float(data.get("stop_points"), "stop_points")
    time_stop_seconds = _optional_non_negative_int(
        data.get("time_stop_seconds"),
        "time_stop_seconds",
    )
    adverse_exit_seconds = _optional_non_negative_int(
        data.get("adverse_exit_seconds"),
        "adverse_exit_seconds",
    )
    if (
        stop_price is None
        and stop_points is None
        and time_stop_seconds is None
        and adverse_exit_seconds is None
    ):
        return None
    return StopPlan(
        stop_price=stop_price,
        stop_points=stop_points,
        time_stop_seconds=time_stop_seconds,
        adverse_exit_seconds=adverse_exit_seconds,
    )


def _target_plan_from_candidate(candidate: DoctrineSignalCandidate) -> TargetPlan | None:
    metadata = dict(candidate.metadata)
    explicit = metadata.get("target_plan")
    if explicit is not None:
        return _normalize_target_plan_mapping(_require_mapping(explicit, "candidate.metadata.target_plan"))

    target_price = _optional_non_negative_float(metadata.get("target_price"), "target_price")
    trail_after_points = _optional_non_negative_float(
        metadata.get("trail_after_points"),
        "trail_after_points",
    )
    trail_step_points = _optional_non_negative_float(
        metadata.get("trail_step_points"),
        "trail_step_points",
    )
    target_points = _optional_non_negative_float(candidate.target_points, "candidate.target_points")

    if (
        target_price is None
        and target_points is None
        and trail_after_points is None
        and trail_step_points is None
    ):
        return None

    return TargetPlan(
        target_price=target_price,
        target_points=target_points,
        trail_after_points=trail_after_points,
        trail_step_points=trail_step_points,
    )


def _stop_plan_from_candidate(candidate: DoctrineSignalCandidate) -> StopPlan | None:
    metadata = dict(candidate.metadata)
    explicit = metadata.get("stop_plan")
    if explicit is not None:
        return _normalize_stop_plan_mapping(_require_mapping(explicit, "candidate.metadata.stop_plan"))

    stop_price = _optional_non_negative_float(metadata.get("stop_price"), "stop_price")
    time_stop_seconds = _optional_non_negative_int(
        metadata.get("time_stop_seconds"),
        "time_stop_seconds",
    )
    adverse_exit_seconds = _optional_non_negative_int(
        metadata.get("adverse_exit_seconds"),
        "adverse_exit_seconds",
    )
    stop_points = _optional_non_negative_float(candidate.stop_points, "candidate.stop_points")

    if (
        stop_price is None
        and stop_points is None
        and time_stop_seconds is None
        and adverse_exit_seconds is None
    ):
        return None

    return StopPlan(
        stop_price=stop_price,
        stop_points=stop_points,
        time_stop_seconds=time_stop_seconds,
        adverse_exit_seconds=adverse_exit_seconds,
    )


def _provider_ids_from_candidate(
    candidate: DoctrineSignalCandidate,
) -> tuple[str | None, str | None, str | None]:
    metadata = dict(candidate.metadata)
    return (
        _clean_optional_str(metadata.get("active_futures_provider_id")),
        _clean_optional_str(metadata.get("active_selected_option_provider_id")),
        _clean_optional_str(metadata.get("active_option_context_provider_id")),
    )


# ============================================================================
# Canonical decision builders
# ============================================================================


def build_entry_decision(
    *,
    now_ns: int,
    quantity_lots: int,
    candidate: DoctrineSignalCandidate,
    system_state: str = N.STATE_ENTRY_PENDING,
    ts_expiry_ns: int | None = None,
    explain: str | None = None,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    _require_non_negative_int(now_ns, "now_ns")
    qty = _require_positive_int(quantity_lots, "quantity_lots")
    _require(bool(candidate.instrument_key), "entry candidate requires instrument_key")

    branch_id = _require_literal(candidate.branch_id, "candidate.branch_id", _ALLOWED_BRANCH_IDS)
    side = _require_literal(candidate.side, "candidate.side", _ALLOWED_OPTION_SIDES)
    _validate_branch_side(branch_id, side)

    action = _entry_action_for_branch(branch_id)
    explain_text = (
        _clean_optional_str(explain)
        or _clean_optional_str(dict(candidate.metadata).get("explain"))
        or "entry_candidate"
    )

    cand_fut_pid, cand_opt_pid, cand_ctx_pid = _provider_ids_from_candidate(candidate)

    metadata = _merge_metadata(
        candidate.metadata,
        extra_metadata,
        reason_code=dict(candidate.metadata).get("reason_code") or "entry_candidate",
    )
    metadata.setdefault("candidate_score", float(candidate.score))
    metadata.setdefault("candidate_priority", float(candidate.priority))
    metadata.setdefault("setup_kind", _clean_optional_str(candidate.setup_kind))
    metadata.setdefault("tick_size", _optional_non_negative_float(candidate.tick_size, "candidate.tick_size"))
    metadata.setdefault("quantity_lots", qty)

    return _decision(
        prefix="dec",
        ts_event_ns=now_ns,
        ts_expiry_ns=ts_expiry_ns,
        action=action,
        side=side,
        position_effect=N.POSITION_EFFECT_OPEN,
        quantity_lots=qty,
        instrument_key=_require_non_empty_str(candidate.instrument_key, "candidate.instrument_key"),
        strategy_family_id=_clean_optional_str(candidate.family_id),
        doctrine_id=_clean_optional_str(candidate.doctrine_id),
        branch_id=branch_id,
        family_runtime_mode=_clean_optional_str(candidate.family_runtime_mode),
        strategy_runtime_mode=_clean_optional_str(candidate.strategy_runtime_mode),
        source_event_id=_clean_optional_str(candidate.source_event_id),
        trap_event_id=_clean_optional_str(candidate.trap_event_id),
        burst_event_id=_clean_optional_str(candidate.burst_event_id),
        active_futures_provider_id=(
            _clean_optional_str(active_futures_provider_id) or cand_fut_pid
        ),
        active_selected_option_provider_id=(
            _clean_optional_str(active_selected_option_provider_id) or cand_opt_pid
        ),
        active_option_context_provider_id=(
            _clean_optional_str(active_option_context_provider_id) or cand_ctx_pid
        ),
        entry_mode=candidate.entry_mode,
        strategy_mode=strategy_mode_for_branch(branch_id),
        system_state=system_state,
        explain=explain_text,
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
    family_id: str,
    doctrine_id: str,
    branch_id: str,
    reason_code: str,
    position_effect: str = N.POSITION_EFFECT_FLATTEN,
    instrument_key: str | None = None,
    family_runtime_mode: str | None = None,
    strategy_runtime_mode: str | None = None,
    source_event_id: str | None = None,
    trap_event_id: str | None = None,
    burst_event_id: str | None = None,
    entry_mode: str = N.ENTRY_MODE_UNKNOWN,
    explain: str | None = None,
    stop_plan: StopPlan | Mapping[str, Any] | None = None,
    target_plan: TargetPlan | Mapping[str, Any] | None = None,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    ts_expiry_ns: int | None = None,
    system_state: str = N.STATE_EXIT_PENDING,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    _require_non_negative_int(now_ns, "now_ns")
    qty = _require_non_negative_int(quantity_lots, "quantity_lots")
    normalized_family_id = _require_non_empty_str(family_id, "family_id")
    normalized_doctrine_id = _require_non_empty_str(doctrine_id, "doctrine_id")
    normalized_branch_id = _require_literal(branch_id, "branch_id", _ALLOWED_BRANCH_IDS)
    normalized_reason = normalize_reason(reason_code)
    normalized_position_effect = _require_literal(
        position_effect,
        "position_effect",
        _ALLOWED_EXIT_POSITION_EFFECTS,
    )

    if isinstance(stop_plan, StopPlan):
        normalized_stop_plan = stop_plan
    else:
        normalized_stop_plan = _normalize_stop_plan_mapping(stop_plan)

    if isinstance(target_plan, TargetPlan):
        normalized_target_plan = target_plan
    else:
        normalized_target_plan = _normalize_target_plan_mapping(target_plan)

    explain_text = _clean_optional_str(explain) or normalized_reason

    return _decision(
        prefix="dec",
        ts_event_ns=now_ns,
        ts_expiry_ns=ts_expiry_ns,
        action=N.ACTION_EXIT,
        side=side_for_branch(normalized_branch_id),
        position_effect=normalized_position_effect,
        quantity_lots=qty,
        instrument_key=_clean_optional_str(instrument_key),
        strategy_family_id=normalized_family_id,
        doctrine_id=normalized_doctrine_id,
        branch_id=normalized_branch_id,
        family_runtime_mode=_clean_optional_str(family_runtime_mode),
        strategy_runtime_mode=_clean_optional_str(strategy_runtime_mode),
        source_event_id=_clean_optional_str(source_event_id),
        trap_event_id=_clean_optional_str(trap_event_id),
        burst_event_id=_clean_optional_str(burst_event_id),
        active_futures_provider_id=_clean_optional_str(active_futures_provider_id),
        active_selected_option_provider_id=_clean_optional_str(active_selected_option_provider_id),
        active_option_context_provider_id=_clean_optional_str(active_option_context_provider_id),
        entry_mode=entry_mode,
        strategy_mode=strategy_mode_for_branch(normalized_branch_id),
        system_state=system_state,
        explain=explain_text,
        blocker_code=None,
        blocker_message=None,
        stop_plan=normalized_stop_plan,
        target_plan=normalized_target_plan,
        metadata=_merge_metadata(extra_metadata, reason_code=normalized_reason),
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
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    ts_expiry_ns: int | None = None,
    system_state: str = N.STATE_WAIT,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    _require_non_negative_int(now_ns, "now_ns")
    normalized_side = _require_literal(side, "side", _ALLOWED_OPTION_SIDES)
    normalized_branch_id = _clean_optional_str(branch_id)
    if normalized_branch_id is not None:
        _validate_branch_side(normalized_branch_id, normalized_side)

    explain_text = _clean_optional_str(explain) or _clean_optional_str(reason_code) or "hold"
    block_code = (
        _clean_optional_str(blocker.code) if blocker is not None else _clean_optional_str(reason_code)
    )
    block_message = (
        _clean_optional_str(blocker.message) if blocker is not None else explain_text
    )

    return _decision(
        prefix="dec",
        ts_event_ns=now_ns,
        ts_expiry_ns=ts_expiry_ns,
        action=N.ACTION_HOLD,
        side=normalized_side,
        position_effect=N.POSITION_EFFECT_NONE,
        quantity_lots=0,
        instrument_key=None,
        strategy_family_id=_clean_optional_str(family_id),
        doctrine_id=_clean_optional_str(doctrine_id),
        branch_id=normalized_branch_id,
        family_runtime_mode=_clean_optional_str(family_runtime_mode),
        strategy_runtime_mode=_clean_optional_str(strategy_runtime_mode),
        source_event_id=None,
        trap_event_id=None,
        burst_event_id=None,
        active_futures_provider_id=_clean_optional_str(active_futures_provider_id),
        active_selected_option_provider_id=_clean_optional_str(active_selected_option_provider_id),
        active_option_context_provider_id=_clean_optional_str(active_option_context_provider_id),
        entry_mode=N.ENTRY_MODE_UNKNOWN,
        strategy_mode=(
            strategy_mode_for_branch(normalized_branch_id)
            if normalized_branch_id is not None
            else N.STRATEGY_AUTO
        ),
        system_state=system_state,
        explain=explain_text,
        blocker_code=block_code,
        blocker_message=block_message,
        stop_plan=None,
        target_plan=None,
        metadata=_merge_metadata(
            blocker.metadata if blocker is not None else None,
            extra_metadata,
            reason_code=reason_code,
        ),
    )


def build_block_decision(
    *,
    now_ns: int,
    side: str,
    family_id: str | None = None,
    doctrine_id: str | None = None,
    branch_id: str | None = None,
    family_runtime_mode: str | None = None,
    strategy_runtime_mode: str | None = None,
    blocker: DoctrineBlocker | None = None,
    reason_code: str | None = None,
    explain: str | None = None,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    ts_expiry_ns: int | None = None,
    system_state: str = N.STATE_WAIT,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    _require_non_negative_int(now_ns, "now_ns")
    normalized_side = _require_literal(side, "side", _ALLOWED_OPTION_SIDES)
    normalized_branch_id = _clean_optional_str(branch_id)
    if normalized_branch_id is not None:
        _validate_branch_side(normalized_branch_id, normalized_side)

    explain_text = (
        _clean_optional_str(explain)
        or _clean_optional_str(reason_code)
        or (_clean_optional_str(blocker.message) if blocker is not None else None)
        or "blocked"
    )
    block_code = (
        _clean_optional_str(blocker.code) if blocker is not None else _clean_optional_str(reason_code)
    )
    block_message = (
        _clean_optional_str(blocker.message) if blocker is not None else explain_text
    )

    return _decision(
        prefix="dec",
        ts_event_ns=now_ns,
        ts_expiry_ns=ts_expiry_ns,
        action=N.ACTION_BLOCK,
        side=normalized_side,
        position_effect=N.POSITION_EFFECT_NONE,
        quantity_lots=0,
        instrument_key=None,
        strategy_family_id=_clean_optional_str(family_id),
        doctrine_id=_clean_optional_str(doctrine_id),
        branch_id=normalized_branch_id,
        family_runtime_mode=_clean_optional_str(family_runtime_mode),
        strategy_runtime_mode=_clean_optional_str(strategy_runtime_mode),
        source_event_id=None,
        trap_event_id=None,
        burst_event_id=None,
        active_futures_provider_id=_clean_optional_str(active_futures_provider_id),
        active_selected_option_provider_id=_clean_optional_str(active_selected_option_provider_id),
        active_option_context_provider_id=_clean_optional_str(active_option_context_provider_id),
        entry_mode=N.ENTRY_MODE_UNKNOWN,
        strategy_mode=(
            strategy_mode_for_branch(normalized_branch_id)
            if normalized_branch_id is not None
            else N.STRATEGY_AUTO
        ),
        system_state=system_state,
        explain=explain_text,
        blocker_code=block_code,
        blocker_message=block_message,
        stop_plan=None,
        target_plan=None,
        metadata=_merge_metadata(
            blocker.metadata if blocker is not None else None,
            extra_metadata,
            reason_code=reason_code,
        ),
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
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    ts_expiry_ns: int | None = None,
    system_state: str = N.STATE_WAIT,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    """
    Compatibility alias preserved during migration freeze.

    Semantically, a blocked condition should emit ACTION_BLOCK, not ACTION_HOLD.
    This function therefore preserves the historical name while routing to the
    canonical block decision builder.
    """
    normalized_branch_id = _require_literal(branch_id, "branch_id", _ALLOWED_BRANCH_IDS)
    return build_block_decision(
        now_ns=now_ns,
        side=side_for_branch(normalized_branch_id),
        family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=normalized_branch_id,
        family_runtime_mode=family_runtime_mode,
        strategy_runtime_mode=strategy_runtime_mode,
        blocker=blocker,
        reason_code=blocker.code,
        explain=blocker.message,
        active_futures_provider_id=active_futures_provider_id,
        active_selected_option_provider_id=active_selected_option_provider_id,
        active_option_context_provider_id=active_option_context_provider_id,
        ts_expiry_ns=ts_expiry_ns,
        system_state=system_state,
        extra_metadata=extra_metadata,
    )


def build_decision_from_action_request(
    *,
    now_ns: int,
    family_id: str,
    doctrine_id: str,
    branch_id: str,
    family_runtime_mode: str | None,
    strategy_runtime_mode: str | None,
    action_request: DoctrineActionRequest,
    source_event_id: str | None = None,
    trap_event_id: str | None = None,
    burst_event_id: str | None = None,
    entry_mode: str = N.ENTRY_MODE_UNKNOWN,
    strategy_mode: str | None = None,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    ts_expiry_ns: int | None = None,
    system_state: str = N.STATE_WAIT,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    _require_non_negative_int(now_ns, "now_ns")
    normalized_family_id = _require_non_empty_str(family_id, "family_id")
    normalized_doctrine_id = _require_non_empty_str(doctrine_id, "doctrine_id")
    normalized_branch_id = _require_literal(branch_id, "branch_id", _ALLOWED_BRANCH_IDS)
    _require(bool(action_request.explain), "action_request.explain must be non-empty")

    action = _require_literal(action_request.action, "action_request.action", _ALLOWED_DECISION_ACTIONS)
    side = _require_literal(action_request.side, "action_request.side", _ALLOWED_OPTION_SIDES)
    _validate_branch_side(normalized_branch_id, side)

    normalized_stop_plan = _normalize_stop_plan_mapping(action_request.stop_plan)
    normalized_target_plan = _normalize_target_plan_mapping(action_request.target_plan)

    metadata = _merge_metadata(
        action_request.metadata,
        action_request.blocker.metadata if action_request.blocker is not None else None,
        extra_metadata,
        reason_code=action_request.reason_code,
    )

    blocker_code: str | None = None
    blocker_message: str | None = None

    if action in _ALLOWED_ENTRY_ACTIONS:
        expected_branch = _branch_for_entry_action(action)
        _require(
            normalized_branch_id == expected_branch,
            "branch_id must match entry action branch",
        )
        _require(
            action_request.position_effect == N.POSITION_EFFECT_OPEN,
            "entry action request must use position_effect OPEN",
        )
        _require_positive_int(action_request.quantity_lots, "action_request.quantity_lots")
        _require(
            bool(action_request.instrument_key),
            "entry action request requires instrument_key",
        )

    elif action == N.ACTION_EXIT:
        _require(
            action_request.position_effect in _ALLOWED_EXIT_POSITION_EFFECTS,
            "exit action request requires CLOSE / REDUCE / FLATTEN position_effect",
        )
        _require_non_negative_int(action_request.quantity_lots, "action_request.quantity_lots")

    elif action in _ALLOWED_HOLDISH_ACTIONS:
        _require(
            action_request.position_effect == N.POSITION_EFFECT_NONE,
            "hold/block action request requires position_effect NONE",
        )
        _require_non_negative_int(action_request.quantity_lots, "action_request.quantity_lots")
        blocker_code = (
            _clean_optional_str(action_request.blocker.code)
            if action_request.blocker is not None
            else normalize_reason(action_request.reason_code)
        )
        blocker_message = (
            _clean_optional_str(action_request.blocker.message)
            if action_request.blocker is not None
            else _clean_optional_str(action_request.explain)
        )

    return _decision(
        prefix="dec",
        ts_event_ns=now_ns,
        ts_expiry_ns=ts_expiry_ns,
        action=action,
        side=side,
        position_effect=action_request.position_effect,
        quantity_lots=int(action_request.quantity_lots),
        instrument_key=_clean_optional_str(action_request.instrument_key),
        strategy_family_id=normalized_family_id,
        doctrine_id=normalized_doctrine_id,
        branch_id=normalized_branch_id,
        family_runtime_mode=_clean_optional_str(family_runtime_mode),
        strategy_runtime_mode=_clean_optional_str(strategy_runtime_mode),
        source_event_id=_clean_optional_str(source_event_id),
        trap_event_id=_clean_optional_str(trap_event_id),
        burst_event_id=_clean_optional_str(burst_event_id),
        active_futures_provider_id=_clean_optional_str(active_futures_provider_id),
        active_selected_option_provider_id=_clean_optional_str(active_selected_option_provider_id),
        active_option_context_provider_id=_clean_optional_str(active_option_context_provider_id),
        entry_mode=entry_mode,
        strategy_mode=strategy_mode or strategy_mode_for_branch(normalized_branch_id),
        system_state=system_state,
        explain=action_request.explain,
        blocker_code=blocker_code,
        blocker_message=blocker_message,
        stop_plan=normalized_stop_plan,
        target_plan=normalized_target_plan,
        metadata=metadata,
    )


__all__ = [
    "StrategyFamilyDecisionError",
    "build_block_decision",
    "build_blocked_hold_decision",
    "build_decision_from_action_request",
    "build_entry_decision",
    "build_exit_decision",
    "build_hold_decision",
]

# =============================================================================
# Batch 11 freeze hardening: entry decisions require order-intent metadata
# =============================================================================

_BATCH11_DECISION_ENTRY_CONTRACT_VERSION = "1"
_BATCH11_ENTRY_REQUIRED_METADATA = (
    "option_symbol",
    "option_token",
    "strike",
    "limit_price",
    "active_futures_provider_id",
    "active_selected_option_provider_id",
    "active_option_context_provider_id",
)


def _batch11_candidate_metadata(candidate: DoctrineSignalCandidate) -> dict[str, Any]:
    raw = getattr(candidate, "metadata", {})
    return dict(raw) if isinstance(raw, Mapping) else {}


def _batch11_require_entry_contract(candidate: DoctrineSignalCandidate) -> None:
    metadata = _batch11_candidate_metadata(candidate)
    missing = []
    for key in _BATCH11_ENTRY_REQUIRED_METADATA:
        value = metadata.get(key)
        if value in (None, ""):
            missing.append(key)

    if missing:
        raise StrategyFamilyDecisionError(
            "entry candidate missing execution-required metadata: "
            + ", ".join(missing)
        )


_BATCH11_ORIGINAL_BUILD_ENTRY_DECISION = build_entry_decision


def build_entry_decision(
    *,
    now_ns: int,
    quantity_lots: int,
    candidate: DoctrineSignalCandidate,
    system_state: str = N.STATE_ENTRY_PENDING,
    ts_expiry_ns: int | None = None,
    explain: str | None = None,
    active_futures_provider_id: str | None = None,
    active_selected_option_provider_id: str | None = None,
    active_option_context_provider_id: str | None = None,
    extra_metadata: Mapping[str, Any] | None = None,
) -> StrategyDecision:
    _batch11_require_entry_contract(candidate)
    metadata = _batch11_candidate_metadata(candidate)

    return _BATCH11_ORIGINAL_BUILD_ENTRY_DECISION(
        now_ns=now_ns,
        quantity_lots=quantity_lots,
        candidate=candidate,
        system_state=system_state,
        ts_expiry_ns=ts_expiry_ns,
        explain=explain,
        active_futures_provider_id=active_futures_provider_id or metadata.get("active_futures_provider_id"),
        active_selected_option_provider_id=(
            active_selected_option_provider_id or metadata.get("active_selected_option_provider_id")
        ),
        active_option_context_provider_id=(
            active_option_context_provider_id or metadata.get("active_option_context_provider_id")
        ),
        extra_metadata={
            **metadata,
            **dict(extra_metadata or {}),
            "batch11_entry_contract_checked": True,
        },
    )
