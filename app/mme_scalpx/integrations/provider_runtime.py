from __future__ import annotations

"""
app/mme_scalpx/integrations/provider_runtime.py

Provider-role resolution and failover policy for ScalpX MME.

Purpose
-------
This module OWNS:
- provider-role resolution for market data, option context, and execution
- interpretation of failover mode and provider override mode
- normalization of provider health/context into active-provider runtime truth
- deterministic provider-transition event construction
- pre-position setup invalidation signaling when active providers change
- enforcement of "no silent provider switch" and "no mid-position provider migration"

This module DOES NOT own:
- broker API clients
- websocket/session lifecycle
- market data normalization
- strategy feature computation
- execution order placement
- Redis IO / stream publishing
- long-lived service supervision

Core design rules
-----------------
- core.names remains the single source of truth for provider ids, roles, modes,
  statuses, transition reasons, and system states.
- core.models owns the typed transport/state/event surfaces.
- provider_runtime.py is pure resolution logic and policy.
- Dhan is the preferred selected-option market-data and option-context lane.
- Zerodha is the preferred futures market-data and execution-primary lane until
  staged proof promotes a different posture.
- Dhan is the canonical execution-fallback lane.
- No active provider role may silently change while a position is open.
- If a provider role changes while flat but the strategy is pre-position
  (ARMED / RETEST_MONITOR / ENTRY_PENDING), the live setup must rebuild.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, Mapping, Sequence

from app.mme_scalpx.core import models, names
from app.mme_scalpx.core.validators import (
    ValidationError,
    require,
    require_bool,
    require_int,
    require_literal,
    require_mapping,
    require_non_empty_str,
)

# ============================================================================
# Exceptions
# ============================================================================


class ProviderRuntimeError(ValueError):
    """Base error for provider-runtime policy failures."""


class ProviderRuntimeValidationError(ProviderRuntimeError):
    """Raised when provider-runtime inputs or policy are invalid."""


# ============================================================================
# Local wrappers around shared validators
# ============================================================================


def _wrap_validation(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        if isinstance(exc, ProviderRuntimeValidationError):
            raise
        if isinstance(exc, ValidationError):
            raise ProviderRuntimeValidationError(str(exc)) from exc
        raise ProviderRuntimeValidationError(str(exc)) from exc


def _require(condition: bool, message: str) -> None:
    _wrap_validation(require, condition, message)


def _require_non_empty_str(value: str, field_name: str) -> str:
    return _wrap_validation(require_non_empty_str, value, field_name=field_name)


def _require_bool(value: bool, field_name: str) -> bool:
    return _wrap_validation(require_bool, value, field_name=field_name)


def _require_int(
    value: int,
    field_name: str,
    *,
    min_value: int | None = None,
) -> int:
    return _wrap_validation(
        require_int,
        value,
        field_name=field_name,
        min_value=min_value,
    )


def _require_literal(
    value: str,
    field_name: str,
    *,
    allowed: Sequence[str],
) -> str:
    return _wrap_validation(
        require_literal,
        value,
        field_name=field_name,
        allowed=allowed,
    )


def _require_mapping(value: Mapping[str, object], field_name: str) -> dict[str, object]:
    return _wrap_validation(require_mapping, value, field_name=field_name)


# ============================================================================
# Canonical role policy
# ============================================================================

_ALLOWED_SWITCHABLE_ACTIVE_ROLES: Final[tuple[str, ...]] = (
    names.PROVIDER_ROLE_FUTURES_MARKETDATA,
    names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
    names.PROVIDER_ROLE_OPTION_CONTEXT,
    names.PROVIDER_ROLE_EXECUTION_PRIMARY,
)

_PREPOSITION_INVALIDATION_STATES: Final[tuple[str, ...]] = (
    names.STATE_ARMED,
    names.STATE_RETEST_MONITOR,
    names.STATE_ENTRY_PENDING,
)

_BASELINE_ROLE_PROVIDER_ORDER: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        names.PROVIDER_ROLE_FUTURES_MARKETDATA: (
            names.PROVIDER_ZERODHA,
            names.PROVIDER_DHAN,
        ),
        names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA: (
            names.PROVIDER_DHAN,
            names.PROVIDER_ZERODHA,
        ),
        names.PROVIDER_ROLE_OPTION_CONTEXT: (
            names.PROVIDER_DHAN,
        ),
        names.PROVIDER_ROLE_EXECUTION_PRIMARY: (
            names.PROVIDER_ZERODHA,
            names.PROVIDER_DHAN,
        ),
        names.PROVIDER_ROLE_EXECUTION_FALLBACK: (
            names.PROVIDER_DHAN,
            names.PROVIDER_ZERODHA,
        ),
    }
)

_STATUSES_ALLOWING_ACTIVE_ASSIGNMENT: Final[frozenset[str]] = frozenset(
    {
        names.PROVIDER_STATUS_HEALTHY,
        names.PROVIDER_STATUS_DEGRADED,
        names.PROVIDER_STATUS_FAILOVER_ACTIVE,
    }
)


# ============================================================================
# Small internal helpers
# ============================================================================


def _status_allows_active_assignment(status: str) -> bool:
    return status in _STATUSES_ALLOWING_ACTIVE_ASSIGNMENT


def _normalize_provider_health_map(
    provider_health: Mapping[str, models.ProviderHealthState]
    | Sequence[models.ProviderHealthState],
) -> dict[str, models.ProviderHealthState]:
    if isinstance(provider_health, Mapping):
        raw = _require_mapping(provider_health, "provider_health")
        out: dict[str, models.ProviderHealthState] = {}
        for provider_id, state in raw.items():
            key = _require_non_empty_str(str(provider_id), "provider_health.key")
            if not isinstance(state, models.ProviderHealthState):
                raise ProviderRuntimeValidationError(
                    f"provider_health[{key!r}] must be ProviderHealthState, "
                    f"got {type(state).__name__}"
                )
            out[key] = state
        return out

    if isinstance(provider_health, Sequence) and not isinstance(
        provider_health,
        (str, bytes, bytearray),
    ):
        out = {}
        for idx, state in enumerate(provider_health):
            if not isinstance(state, models.ProviderHealthState):
                raise ProviderRuntimeValidationError(
                    f"provider_health[{idx}] must be ProviderHealthState, "
                    f"got {type(state).__name__}"
                )
            out[state.provider_id] = state
        return out

    raise ProviderRuntimeValidationError(
        "provider_health must be mapping[str, ProviderHealthState] or sequence[ProviderHealthState]"
    )


def _get_runtime_provider_id(
    runtime_state: models.ProviderRuntimeState,
    role: str,
) -> str:
    if role == names.PROVIDER_ROLE_FUTURES_MARKETDATA:
        return runtime_state.futures_marketdata_provider_id
    if role == names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA:
        return runtime_state.selected_option_marketdata_provider_id
    if role == names.PROVIDER_ROLE_OPTION_CONTEXT:
        return runtime_state.option_context_provider_id
    if role == names.PROVIDER_ROLE_EXECUTION_PRIMARY:
        return runtime_state.execution_primary_provider_id
    if role == names.PROVIDER_ROLE_EXECUTION_FALLBACK:
        return runtime_state.execution_fallback_provider_id
    raise ProviderRuntimeValidationError(f"unknown provider role: {role!r}")


def _get_runtime_status(
    runtime_state: models.ProviderRuntimeState,
    role: str,
) -> str:
    if role == names.PROVIDER_ROLE_FUTURES_MARKETDATA:
        return runtime_state.futures_marketdata_status
    if role == names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA:
        return runtime_state.selected_option_marketdata_status
    if role == names.PROVIDER_ROLE_OPTION_CONTEXT:
        return runtime_state.option_context_status
    if role == names.PROVIDER_ROLE_EXECUTION_PRIMARY:
        return runtime_state.execution_primary_status
    if role == names.PROVIDER_ROLE_EXECUTION_FALLBACK:
        return runtime_state.execution_fallback_status
    raise ProviderRuntimeValidationError(f"unknown provider role: {role!r}")


def _status_reason_from_status(status: str) -> str:
    if status == names.PROVIDER_STATUS_STALE:
        return names.PROVIDER_TRANSITION_REASON_STALE_DATA
    if status == names.PROVIDER_STATUS_AUTH_FAILED:
        return names.PROVIDER_TRANSITION_REASON_AUTH_FAILED
    if status in (
        names.PROVIDER_STATUS_DEGRADED,
        names.PROVIDER_STATUS_UNAVAILABLE,
        names.PROVIDER_STATUS_DISABLED,
    ):
        return names.PROVIDER_TRANSITION_REASON_HEALTH_FAIL
    return names.PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED


def _determine_provider_status(
    *,
    provider_id: str,
    role: str,
    provider_health_map: Mapping[str, models.ProviderHealthState],
    dhan_context_state: models.DhanContextState | None,
) -> str:
    health_state = provider_health_map.get(provider_id)
    if health_state is None:
        if role == names.PROVIDER_ROLE_OPTION_CONTEXT and provider_id == names.PROVIDER_DHAN:
            if dhan_context_state is not None:
                return dhan_context_state.context_status
        return names.PROVIDER_STATUS_UNAVAILABLE

    base_status = health_state.status

    if base_status == names.PROVIDER_STATUS_DISABLED:
        return names.PROVIDER_STATUS_DISABLED

    if health_state.authenticated is False:
        return names.PROVIDER_STATUS_AUTH_FAILED

    if role == names.PROVIDER_ROLE_OPTION_CONTEXT and provider_id == names.PROVIDER_DHAN:
        if dhan_context_state is None:
            if health_state.stale:
                return names.PROVIDER_STATUS_STALE
            return base_status
        if dhan_context_state.context_status == names.PROVIDER_STATUS_AUTH_FAILED:
            return names.PROVIDER_STATUS_AUTH_FAILED
        if dhan_context_state.context_status == names.PROVIDER_STATUS_STALE:
            return names.PROVIDER_STATUS_STALE
        if dhan_context_state.context_status in (
            names.PROVIDER_STATUS_UNAVAILABLE,
            names.PROVIDER_STATUS_DISABLED,
        ):
            return dhan_context_state.context_status
        if health_state.stale:
            return names.PROVIDER_STATUS_STALE
        return dhan_context_state.context_status

    if health_state.stale:
        return names.PROVIDER_STATUS_STALE

    if role in (
        names.PROVIDER_ROLE_FUTURES_MARKETDATA,
        names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
    ) and health_state.marketdata_healthy is False:
        if base_status in (
            names.PROVIDER_STATUS_HEALTHY,
            names.PROVIDER_STATUS_FAILOVER_ACTIVE,
        ):
            return names.PROVIDER_STATUS_DEGRADED
        return base_status

    if role in (
        names.PROVIDER_ROLE_EXECUTION_PRIMARY,
        names.PROVIDER_ROLE_EXECUTION_FALLBACK,
    ) and health_state.execution_healthy is False:
        if base_status in (
            names.PROVIDER_STATUS_HEALTHY,
            names.PROVIDER_STATUS_FAILOVER_ACTIVE,
        ):
            return names.PROVIDER_STATUS_DEGRADED
        return base_status

    return base_status


def _candidate_order_for_role(
    *,
    role: str,
    override_mode: str,
) -> tuple[str, ...]:
    baseline = _BASELINE_ROLE_PROVIDER_ORDER[role]

    if role == names.PROVIDER_ROLE_OPTION_CONTEXT:
        return baseline

    if override_mode == names.PROVIDER_OVERRIDE_MODE_FORCE_ZERODHA:
        if role == names.PROVIDER_ROLE_EXECUTION_FALLBACK:
            return (
                names.PROVIDER_DHAN,
                names.PROVIDER_ZERODHA,
            )
        if names.PROVIDER_ZERODHA in baseline:
            return (
                names.PROVIDER_ZERODHA,
                *tuple(p for p in baseline if p != names.PROVIDER_ZERODHA),
            )

    if override_mode == names.PROVIDER_OVERRIDE_MODE_FORCE_DHAN:
        if role == names.PROVIDER_ROLE_EXECUTION_FALLBACK:
            return (
                names.PROVIDER_ZERODHA,
                names.PROVIDER_DHAN,
            )
        if names.PROVIDER_DHAN in baseline:
            return (
                names.PROVIDER_DHAN,
                *tuple(p for p in baseline if p != names.PROVIDER_DHAN),
            )

    return baseline


def _derive_execution_fallback_provider_id(
    execution_primary_provider_id: str,
) -> str:
    if execution_primary_provider_id == names.PROVIDER_ZERODHA:
        return names.PROVIDER_DHAN
    return names.PROVIDER_ZERODHA


@dataclass(frozen=True, slots=True)
class _RoleChoice:
    role: str
    provider_id: str
    status: str
    switched: bool = False
    pending_failover: bool = False
    blocked_mid_position_switch: bool = False
    reason: str = names.PROVIDER_TRANSITION_REASON_BOOTSTRAP
    message: str | None = None


# ============================================================================
# Public config / input / result models
# ============================================================================


@dataclass(frozen=True, slots=True)
class ProviderRuntimeConfig:
    family_runtime_mode: str = names.FAMILY_RUNTIME_MODE_OBSERVE_ONLY
    failover_mode: str = names.PROVIDER_FAILOVER_MODE_MANUAL
    override_mode: str = names.PROVIDER_OVERRIDE_MODE_AUTO
    allow_failback_when_recovered: bool = True
    require_flat_for_role_switch: bool = True
    invalidate_preposition_setup_on_switch: bool = True

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        _require_literal(
            self.family_runtime_mode,
            "family_runtime_mode",
            allowed=names.ALLOWED_FAMILY_RUNTIME_MODES,
        )
        _require_literal(
            self.failover_mode,
            "failover_mode",
            allowed=names.ALLOWED_PROVIDER_FAILOVER_MODES,
        )
        _require_literal(
            self.override_mode,
            "override_mode",
            allowed=names.ALLOWED_PROVIDER_OVERRIDE_MODES,
        )
        _require_bool(self.allow_failback_when_recovered, "allow_failback_when_recovered")
        _require_bool(self.require_flat_for_role_switch, "require_flat_for_role_switch")
        _require_bool(
            self.invalidate_preposition_setup_on_switch,
            "invalidate_preposition_setup_on_switch",
        )


@dataclass(frozen=True, slots=True)
class ProviderRuntimeInputs:
    ts_event_ns: int
    provider_health: Mapping[str, models.ProviderHealthState] | Sequence[models.ProviderHealthState]
    config: ProviderRuntimeConfig = field(default_factory=ProviderRuntimeConfig)
    dhan_context_state: models.DhanContextState | None = None
    position_state: models.PositionState | None = None
    strategy_state: models.StrategyState | None = None
    previous_runtime_state: models.ProviderRuntimeState | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        _require_int(self.ts_event_ns, "ts_event_ns", min_value=0)
        if not isinstance(self.config, ProviderRuntimeConfig):
            raise ProviderRuntimeValidationError(
                f"config must be ProviderRuntimeConfig, got {type(self.config).__name__}"
            )
        normalized = _normalize_provider_health_map(self.provider_health)
        object.__setattr__(self, "provider_health", normalized)
        if self.dhan_context_state is not None and not isinstance(
            self.dhan_context_state,
            models.DhanContextState,
        ):
            raise ProviderRuntimeValidationError(
                f"dhan_context_state must be DhanContextState, got {type(self.dhan_context_state).__name__}"
            )
        if self.position_state is not None and not isinstance(
            self.position_state,
            models.PositionState,
        ):
            raise ProviderRuntimeValidationError(
                f"position_state must be PositionState, got {type(self.position_state).__name__}"
            )
        if self.strategy_state is not None and not isinstance(
            self.strategy_state,
            models.StrategyState,
        ):
            raise ProviderRuntimeValidationError(
                f"strategy_state must be StrategyState, got {type(self.strategy_state).__name__}"
            )
        if self.previous_runtime_state is not None and not isinstance(
            self.previous_runtime_state,
            models.ProviderRuntimeState,
        ):
            raise ProviderRuntimeValidationError(
                f"previous_runtime_state must be ProviderRuntimeState, got {type(self.previous_runtime_state).__name__}"
            )


@dataclass(frozen=True, slots=True)
class ProviderRuntimeResolution:
    runtime_state: models.ProviderRuntimeState
    transition_events: tuple[models.ProviderTransitionEvent, ...] = ()
    setup_rebuild_required: bool = False
    setup_rebuild_reason: str | None = None
    pending_failover: bool = False
    blocked_mid_position_switch: bool = False
    message: str | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.runtime_state, models.ProviderRuntimeState):
            raise ProviderRuntimeValidationError(
                f"runtime_state must be ProviderRuntimeState, got {type(self.runtime_state).__name__}"
            )
        for idx, event in enumerate(self.transition_events):
            if not isinstance(event, models.ProviderTransitionEvent):
                raise ProviderRuntimeValidationError(
                    f"transition_events[{idx}] must be ProviderTransitionEvent, got {type(event).__name__}"
                )
        _require_bool(self.setup_rebuild_required, "setup_rebuild_required")
        if self.setup_rebuild_reason is not None:
            _require_non_empty_str(self.setup_rebuild_reason, "setup_rebuild_reason")
        _require_bool(self.pending_failover, "pending_failover")
        _require_bool(self.blocked_mid_position_switch, "blocked_mid_position_switch")
        if self.message is not None:
            _require_non_empty_str(self.message, "message")


# ============================================================================
# Resolver
# ============================================================================


@dataclass(frozen=True, slots=True)
class ProviderRuntimeResolver:
    config: ProviderRuntimeConfig = field(default_factory=ProviderRuntimeConfig)

    def __post_init__(self) -> None:
        if not isinstance(self.config, ProviderRuntimeConfig):
            raise ProviderRuntimeValidationError(
                f"config must be ProviderRuntimeConfig, got {type(self.config).__name__}"
            )

    def resolve(
        self,
        *,
        ts_event_ns: int,
        provider_health: Mapping[str, models.ProviderHealthState] | Sequence[models.ProviderHealthState],
        dhan_context_state: models.DhanContextState | None = None,
        position_state: models.PositionState | None = None,
        strategy_state: models.StrategyState | None = None,
        previous_runtime_state: models.ProviderRuntimeState | None = None,
    ) -> ProviderRuntimeResolution:
        inputs = ProviderRuntimeInputs(
            ts_event_ns=ts_event_ns,
            provider_health=provider_health,
            config=self.config,
            dhan_context_state=dhan_context_state,
            position_state=position_state,
            strategy_state=strategy_state,
            previous_runtime_state=previous_runtime_state,
        )
        return _resolve_provider_runtime_inputs(inputs)


def _resolve_role_choice(
    *,
    role: str,
    inputs: ProviderRuntimeInputs,
    has_open_position: bool,
) -> _RoleChoice:
    config = inputs.config
    provider_health_map = inputs.provider_health
    previous_runtime_state = inputs.previous_runtime_state

    candidate_order = _candidate_order_for_role(
        role=role,
        override_mode=config.override_mode,
    )
    status_by_provider = {
        provider_id: _determine_provider_status(
            provider_id=provider_id,
            role=role,
            provider_health_map=provider_health_map,
            dhan_context_state=inputs.dhan_context_state,
        )
        for provider_id in candidate_order
    }

    preferred_provider_id = candidate_order[0]
    previous_provider_id = (
        _get_runtime_provider_id(previous_runtime_state, role)
        if previous_runtime_state is not None
        else None
    )

    if previous_provider_id is not None and previous_provider_id not in status_by_provider:
        status_by_provider[previous_provider_id] = _determine_provider_status(
            provider_id=previous_provider_id,
            role=role,
            provider_health_map=provider_health_map,
            dhan_context_state=inputs.dhan_context_state,
        )

    first_eligible_provider_id: str | None = None
    for provider_id in candidate_order:
        if _status_allows_active_assignment(status_by_provider[provider_id]):
            first_eligible_provider_id = provider_id
            break

    if config.override_mode != names.PROVIDER_OVERRIDE_MODE_AUTO and role != names.PROVIDER_ROLE_EXECUTION_FALLBACK:
        desired_provider_id = preferred_provider_id
    elif config.failover_mode == names.PROVIDER_FAILOVER_MODE_AUTO_AFTER_PROOF:
        desired_provider_id = first_eligible_provider_id or preferred_provider_id
    else:
        desired_provider_id = previous_provider_id or preferred_provider_id

    blocked_mid_position_switch = False
    pending_failover = False

    if (
        has_open_position
        and config.require_flat_for_role_switch
        and previous_provider_id is not None
        and role in _ALLOWED_SWITCHABLE_ACTIVE_ROLES
        and desired_provider_id != previous_provider_id
    ):
        desired_provider_id = previous_provider_id
        blocked_mid_position_switch = True
        pending_failover = first_eligible_provider_id is not None and (
            first_eligible_provider_id != previous_provider_id
        )

    status = status_by_provider[desired_provider_id]

    if config.failover_mode == names.PROVIDER_FAILOVER_MODE_MANUAL:
        if not _status_allows_active_assignment(status) and first_eligible_provider_id is not None:
            pending_failover = True
    elif config.failover_mode == names.PROVIDER_FAILOVER_MODE_ARMED_MANUAL:
        if desired_provider_id != (first_eligible_provider_id or desired_provider_id):
            pending_failover = first_eligible_provider_id is not None and (
                first_eligible_provider_id != desired_provider_id
            )
        elif not _status_allows_active_assignment(status):
            pending_failover = first_eligible_provider_id is not None and (
                first_eligible_provider_id != desired_provider_id
            )

    switched = previous_provider_id is not None and desired_provider_id != previous_provider_id
    reason = names.PROVIDER_TRANSITION_REASON_BOOTSTRAP
    message: str | None = None

    if previous_provider_id is None:
        reason = names.PROVIDER_TRANSITION_REASON_BOOTSTRAP
    elif switched:
        previous_status = status_by_provider[previous_provider_id]
        if config.override_mode != names.PROVIDER_OVERRIDE_MODE_AUTO:
            reason = names.PROVIDER_TRANSITION_REASON_MANUAL_OVERRIDE
        elif desired_provider_id == candidate_order[0] and previous_provider_id != candidate_order[0]:
            if config.allow_failback_when_recovered:
                reason = names.PROVIDER_TRANSITION_REASON_FAILBACK_RECOVERY
            else:
                reason = names.PROVIDER_TRANSITION_REASON_CONFIG_RELOAD
        elif _status_allows_active_assignment(status) and not _status_allows_active_assignment(previous_status):
            if previous_status in (
                names.PROVIDER_STATUS_STALE,
                names.PROVIDER_STATUS_AUTH_FAILED,
            ):
                reason = _status_reason_from_status(previous_status)
            else:
                reason = names.PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED
        else:
            reason = names.PROVIDER_TRANSITION_REASON_CONFIG_RELOAD
    else:
        if not _status_allows_active_assignment(status):
            reason = _status_reason_from_status(status)
        elif status == names.PROVIDER_STATUS_FAILOVER_ACTIVE:
            reason = names.PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED
        else:
            reason = previous_runtime_state.transition_reason if previous_runtime_state else names.PROVIDER_TRANSITION_REASON_BOOTSTRAP

    if blocked_mid_position_switch:
        message = (
            f"{role} candidate switch to {first_eligible_provider_id or preferred_provider_id} "
            f"blocked because position is open"
        )
    elif pending_failover:
        message = (
            f"{role} remains on {desired_provider_id} while eligible fallback "
            f"{first_eligible_provider_id} is pending"
        )

    return _RoleChoice(
        role=role,
        provider_id=desired_provider_id,
        status=status,
        switched=switched,
        pending_failover=pending_failover,
        blocked_mid_position_switch=blocked_mid_position_switch,
        reason=reason,
        message=message,
    )


def _build_transition_events(
    *,
    ts_event_ns: int,
    previous_runtime_state: models.ProviderRuntimeState | None,
    role_choices: Mapping[str, _RoleChoice],
    config: ProviderRuntimeConfig,
) -> tuple[models.ProviderTransitionEvent, ...]:
    events: list[models.ProviderTransitionEvent] = []

    if previous_runtime_state is None:
        for role in (
            names.PROVIDER_ROLE_FUTURES_MARKETDATA,
            names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
            names.PROVIDER_ROLE_OPTION_CONTEXT,
            names.PROVIDER_ROLE_EXECUTION_PRIMARY,
            names.PROVIDER_ROLE_EXECUTION_FALLBACK,
        ):
            choice = role_choices[role]
            events.append(
                models.ProviderTransitionEvent(
                    ts_event_ns=ts_event_ns,
                    role=role,
                    to_provider_id=choice.provider_id,
                    from_provider_id=None,
                    reason=names.PROVIDER_TRANSITION_REASON_BOOTSTRAP,
                    previous_status=None,
                    new_status=choice.status,
                    family_runtime_mode=config.family_runtime_mode,
                    failover_mode=config.failover_mode,
                    override_mode=config.override_mode,
                    message=choice.message,
                )
            )
        return tuple(events)

    for role in (
        names.PROVIDER_ROLE_FUTURES_MARKETDATA,
        names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
        names.PROVIDER_ROLE_OPTION_CONTEXT,
        names.PROVIDER_ROLE_EXECUTION_PRIMARY,
        names.PROVIDER_ROLE_EXECUTION_FALLBACK,
    ):
        choice = role_choices[role]
        previous_provider_id = _get_runtime_provider_id(previous_runtime_state, role)
        previous_status = _get_runtime_status(previous_runtime_state, role)

        if previous_provider_id != choice.provider_id:
            events.append(
                models.ProviderTransitionEvent(
                    ts_event_ns=ts_event_ns,
                    role=role,
                    to_provider_id=choice.provider_id,
                    from_provider_id=previous_provider_id,
                    reason=choice.reason,
                    previous_status=previous_status,
                    new_status=choice.status,
                    family_runtime_mode=config.family_runtime_mode,
                    failover_mode=config.failover_mode,
                    override_mode=config.override_mode,
                    message=choice.message,
                )
            )
            continue

        if previous_status != choice.status:
            events.append(
                models.ProviderTransitionEvent(
                    ts_event_ns=ts_event_ns,
                    role=role,
                    to_provider_id=choice.provider_id,
                    from_provider_id=previous_provider_id,
                    reason=_status_reason_from_status(choice.status)
                    if not _status_allows_active_assignment(choice.status)
                    else choice.reason,
                    previous_status=previous_status,
                    new_status=choice.status,
                    family_runtime_mode=config.family_runtime_mode,
                    failover_mode=config.failover_mode,
                    override_mode=config.override_mode,
                    message=choice.message,
                )
            )

    return tuple(events)


def _build_setup_rebuild_flags(
    *,
    role_choices: Mapping[str, _RoleChoice],
    inputs: ProviderRuntimeInputs,
) -> tuple[bool, str | None]:
    strategy_state = inputs.strategy_state
    previous_runtime_state = inputs.previous_runtime_state

    if previous_runtime_state is None or strategy_state is None:
        return False, None

    if not inputs.config.invalidate_preposition_setup_on_switch:
        return False, None

    if strategy_state.system_state not in _PREPOSITION_INVALIDATION_STATES:
        return False, None

    if inputs.position_state is not None and inputs.position_state.has_position:
        return False, None

    changed_roles: list[str] = []
    for role in (
        names.PROVIDER_ROLE_FUTURES_MARKETDATA,
        names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
        names.PROVIDER_ROLE_OPTION_CONTEXT,
        names.PROVIDER_ROLE_EXECUTION_PRIMARY,
    ):
        previous_provider_id = _get_runtime_provider_id(previous_runtime_state, role)
        if role_choices[role].provider_id != previous_provider_id:
            changed_roles.append(role)

    if not changed_roles:
        return False, None

    reason = (
        "provider role change while strategy is pre-position requires setup rebuild: "
        + ", ".join(changed_roles)
    )
    return True, reason


def _resolve_provider_runtime_inputs(
    inputs: ProviderRuntimeInputs,
) -> ProviderRuntimeResolution:
    has_open_position = bool(inputs.position_state.has_position) if inputs.position_state else False

    futures_choice = _resolve_role_choice(
        role=names.PROVIDER_ROLE_FUTURES_MARKETDATA,
        inputs=inputs,
        has_open_position=has_open_position,
    )
    selected_option_choice = _resolve_role_choice(
        role=names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA,
        inputs=inputs,
        has_open_position=has_open_position,
    )
    option_context_choice = _resolve_role_choice(
        role=names.PROVIDER_ROLE_OPTION_CONTEXT,
        inputs=inputs,
        has_open_position=has_open_position,
    )
    execution_primary_choice = _resolve_role_choice(
        role=names.PROVIDER_ROLE_EXECUTION_PRIMARY,
        inputs=inputs,
        has_open_position=has_open_position,
    )

    execution_fallback_provider_id = _derive_execution_fallback_provider_id(
        execution_primary_choice.provider_id
    )
    execution_fallback_status = _determine_provider_status(
        provider_id=execution_fallback_provider_id,
        role=names.PROVIDER_ROLE_EXECUTION_FALLBACK,
        provider_health_map=inputs.provider_health,
        dhan_context_state=inputs.dhan_context_state,
    )
    execution_fallback_choice = _RoleChoice(
        role=names.PROVIDER_ROLE_EXECUTION_FALLBACK,
        provider_id=execution_fallback_provider_id,
        status=execution_fallback_status,
        switched=(
            inputs.previous_runtime_state is not None
            and execution_fallback_provider_id
            != inputs.previous_runtime_state.execution_fallback_provider_id
        ),
        pending_failover=False,
        blocked_mid_position_switch=False,
        reason=(
            names.PROVIDER_TRANSITION_REASON_MANUAL_OVERRIDE
            if inputs.config.override_mode != names.PROVIDER_OVERRIDE_MODE_AUTO
            else names.PROVIDER_TRANSITION_REASON_BOOTSTRAP
            if inputs.previous_runtime_state is None
            else names.PROVIDER_TRANSITION_REASON_CONFIG_RELOAD
        ),
    )

    role_choices: dict[str, _RoleChoice] = {
        names.PROVIDER_ROLE_FUTURES_MARKETDATA: futures_choice,
        names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA: selected_option_choice,
        names.PROVIDER_ROLE_OPTION_CONTEXT: option_context_choice,
        names.PROVIDER_ROLE_EXECUTION_PRIMARY: execution_primary_choice,
        names.PROVIDER_ROLE_EXECUTION_FALLBACK: execution_fallback_choice,
    }

    transition_events = _build_transition_events(
        ts_event_ns=inputs.ts_event_ns,
        previous_runtime_state=inputs.previous_runtime_state,
        role_choices=role_choices,
        config=inputs.config,
    )

    pending_failover = any(choice.pending_failover for choice in role_choices.values())
    blocked_mid_position_switch = any(
        choice.blocked_mid_position_switch for choice in role_choices.values()
    )

    baseline_futures = _BASELINE_ROLE_PROVIDER_ORDER[names.PROVIDER_ROLE_FUTURES_MARKETDATA][0]
    baseline_selected_option = _BASELINE_ROLE_PROVIDER_ORDER[
        names.PROVIDER_ROLE_SELECTED_OPTION_MARKETDATA
    ][0]
    baseline_execution_primary = _BASELINE_ROLE_PROVIDER_ORDER[
        names.PROVIDER_ROLE_EXECUTION_PRIMARY
    ][0]

    failover_active = (
        inputs.config.override_mode == names.PROVIDER_OVERRIDE_MODE_AUTO
        and (
            futures_choice.provider_id != baseline_futures
            or selected_option_choice.provider_id != baseline_selected_option
            or execution_primary_choice.provider_id != baseline_execution_primary
        )
    )

    transition_reason = (
        transition_events[-1].reason
        if transition_events
        else (
            inputs.previous_runtime_state.transition_reason
            if inputs.previous_runtime_state is not None
            else names.PROVIDER_TRANSITION_REASON_BOOTSTRAP
        )
    )

    setup_rebuild_required, setup_rebuild_reason = _build_setup_rebuild_flags(
        role_choices=role_choices,
        inputs=inputs,
    )

    messages = [
        choice.message
        for choice in role_choices.values()
        if choice.message is not None
    ]
    if setup_rebuild_reason is not None:
        messages.append(setup_rebuild_reason)
    message = "; ".join(messages) if messages else None

    runtime_state = models.ProviderRuntimeState(
        ts_event_ns=inputs.ts_event_ns,
        futures_marketdata_provider_id=futures_choice.provider_id,
        selected_option_marketdata_provider_id=selected_option_choice.provider_id,
        option_context_provider_id=option_context_choice.provider_id,
        execution_primary_provider_id=execution_primary_choice.provider_id,
        execution_fallback_provider_id=execution_fallback_choice.provider_id,
        futures_marketdata_status=(
            names.PROVIDER_STATUS_FAILOVER_ACTIVE
            if failover_active and futures_choice.provider_id != baseline_futures
            else futures_choice.status
        ),
        selected_option_marketdata_status=(
            names.PROVIDER_STATUS_FAILOVER_ACTIVE
            if failover_active and selected_option_choice.provider_id != baseline_selected_option
            else selected_option_choice.status
        ),
        option_context_status=option_context_choice.status,
        execution_primary_status=(
            names.PROVIDER_STATUS_FAILOVER_ACTIVE
            if failover_active and execution_primary_choice.provider_id != baseline_execution_primary
            else execution_primary_choice.status
        ),
        execution_fallback_status=execution_fallback_choice.status,
        family_runtime_mode=inputs.config.family_runtime_mode,
        failover_mode=inputs.config.failover_mode,
        override_mode=inputs.config.override_mode,
        transition_reason=transition_reason,
        provider_transition_seq=(
            (inputs.previous_runtime_state.provider_transition_seq + len(transition_events))
            if inputs.previous_runtime_state is not None
            else len(transition_events)
        ),
        failover_active=failover_active,
        pending_failover=pending_failover,
        last_update_ns=inputs.ts_event_ns,
        message=message,
    )

    return ProviderRuntimeResolution(
        runtime_state=runtime_state,
        transition_events=transition_events,
        setup_rebuild_required=setup_rebuild_required,
        setup_rebuild_reason=setup_rebuild_reason,
        pending_failover=pending_failover,
        blocked_mid_position_switch=blocked_mid_position_switch,
        message=message,
    )


# ============================================================================
# Convenience API
# ============================================================================


def resolve_provider_runtime(
    *,
    ts_event_ns: int,
    provider_health: Mapping[str, models.ProviderHealthState] | Sequence[models.ProviderHealthState],
    config: ProviderRuntimeConfig | None = None,
    dhan_context_state: models.DhanContextState | None = None,
    position_state: models.PositionState | None = None,
    strategy_state: models.StrategyState | None = None,
    previous_runtime_state: models.ProviderRuntimeState | None = None,
) -> ProviderRuntimeResolution:
    resolver = ProviderRuntimeResolver(
        config=config or ProviderRuntimeConfig(),
    )
    return resolver.resolve(
        ts_event_ns=ts_event_ns,
        provider_health=provider_health,
        dhan_context_state=dhan_context_state,
        position_state=position_state,
        strategy_state=strategy_state,
        previous_runtime_state=previous_runtime_state,
    )


__all__ = [
    "ProviderRuntimeConfig",
    "ProviderRuntimeError",
    "ProviderRuntimeInputs",
    "ProviderRuntimeResolution",
    "ProviderRuntimeResolver",
    "ProviderRuntimeValidationError",
    "resolve_provider_runtime",
]
