from __future__ import annotations

"""
app/mme_scalpx/strategy_family/eligibility.py

Shared pre-entry and re-entry eligibility helpers for doctrine evaluators.

Purpose
-------
This module OWNS:
- shared pre-entry gating helpers
- rollout / provider-profile / lock / position gate aggregation
- re-entry reason and cap checks shared by doctrines

This module DOES NOT own:
- doctrine-specific entry math
- live publishing
- Redis access
"""

from dataclasses import dataclass, field
from typing import Any, Mapping

from app.mme_scalpx.core import names as N

from .common import (
    ALLOWED_REENTRY_EXIT_REASONS,
    DEFAULT_REENTRY_CAPS,
    FORBIDDEN_REENTRY_EXIT_REASONS,
    LIVE_FAMILY_MODES,
    family_is_classic,
    normalize_reason,
    normalize_regime,
)
from .doctrine_contracts import get_doctrine_contract, get_required_provider_profile
from .doctrine_runtime import DoctrineBlocker, DoctrineRuntimeInput


@dataclass(frozen=True, slots=True)
class EligibilityResult:
    passed: bool
    blocker: DoctrineBlocker | None = None
    checks: Mapping[str, bool] = field(default_factory=dict)


def _pass(checks: Mapping[str, bool] | None = None) -> EligibilityResult:
    return EligibilityResult(passed=True, blocker=None, checks=dict(checks or {}))


def _block(
    *,
    code: str,
    message: str,
    checks: Mapping[str, bool] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> EligibilityResult:
    return EligibilityResult(
        passed=False,
        blocker=DoctrineBlocker(
            code=code,
            message=message,
            metadata=dict(metadata or {}),
        ),
        checks=dict(checks or {}),
    )


def evaluate_rollout_gate(runtime: DoctrineRuntimeInput) -> EligibilityResult:
    mode = runtime.family_runtime_mode or N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY
    if mode not in LIVE_FAMILY_MODES:
        return _block(
            code="family_mode_not_live",
            message=f"family_runtime_mode={mode!r} is not live-eligible",
            checks={"family_runtime_mode_live": False},
        )
    return _pass({"family_runtime_mode_live": True})


def evaluate_position_gate(runtime: DoctrineRuntimeInput) -> EligibilityResult:
    if runtime.position.has_position:
        return _block(
            code="position_already_open",
            message="fresh entry blocked because execution truth already shows a live position",
            checks={"flat_position_required": False},
        )
    return _pass({"flat_position_required": True})


def evaluate_risk_gate(runtime: DoctrineRuntimeInput) -> EligibilityResult:
    risk = runtime.risk
    if risk.veto_entries:
        return _block(
            code="risk_veto_entries",
            message="fresh entry blocked by risk veto_entries",
            checks={"risk_veto_entries_clear": False},
        )
    if risk.daily_loss_lock:
        return _block(
            code="daily_loss_lock",
            message="fresh entry blocked by daily_loss_lock",
            checks={"daily_loss_lock_clear": False},
        )
    if risk.consecutive_loss_pause:
        return _block(
            code="consecutive_loss_pause",
            message="fresh entry blocked by consecutive_loss_pause",
            checks={"consecutive_loss_pause_clear": False},
        )
    if risk.session_close_lock:
        return _block(
            code="session_close_lock",
            message="fresh entry blocked by session_close_lock",
            checks={"session_close_lock_clear": False},
        )
    if risk.reconciliation_lock:
        return _block(
            code="reconciliation_lock",
            message="fresh entry blocked by reconciliation_lock",
            checks={"reconciliation_lock_clear": False},
        )
    if risk.unresolved_disaster_lock:
        return _block(
            code="unresolved_disaster_lock",
            message="fresh entry blocked by unresolved_disaster_lock",
            checks={"unresolved_disaster_lock_clear": False},
        )
    if risk.daily_trade_cap_reached:
        return _block(
            code="daily_trade_cap_reached",
            message="fresh entry blocked by daily_trade_cap_reached",
            checks={"daily_trade_cap_clear": False},
        )
    if risk.preview_quantity_lots <= 0:
        return _block(
            code="preview_quantity_unavailable",
            message="fresh entry blocked because preview_quantity_lots <= 0",
            checks={"preview_quantity_positive": False},
        )
    return _pass(
        {
            "risk_veto_entries_clear": True,
            "daily_loss_lock_clear": True,
            "consecutive_loss_pause_clear": True,
            "session_close_lock_clear": True,
            "reconciliation_lock_clear": True,
            "unresolved_disaster_lock_clear": True,
            "daily_trade_cap_clear": True,
            "preview_quantity_positive": True,
        }
    )


def evaluate_provider_profile_gate(
    runtime: DoctrineRuntimeInput,
    *,
    require_execution_bridge: bool = True,
) -> EligibilityResult:
    contract = get_doctrine_contract(runtime.family_id)
    profile = get_required_provider_profile(contract.required_provider_profile_id)
    provider = runtime.provider
    checks: dict[str, bool] = {}

    if runtime.strategy_runtime_mode is None:
        return _block(
            code="strategy_runtime_mode_missing",
            message="strategy_runtime_mode is missing",
            checks={"strategy_runtime_mode_present": False},
        )

    if runtime.strategy_runtime_mode == N.STRATEGY_RUNTIME_MODE_DISABLED:
        return _block(
            code="strategy_runtime_disabled",
            message="strategy_runtime_mode is DISABLED",
            checks={"strategy_runtime_mode_active": False},
        )

    checks["strategy_runtime_mode_active"] = True

    if family_is_classic(runtime.family_id):
        if provider.active_futures_provider_id is None:
            return _block(
                code="futures_provider_missing",
                message="classic doctrine requires an active futures provider",
                checks={**checks, "active_futures_provider_present": False},
            )
        checks["active_futures_provider_present"] = True

        if provider.active_selected_option_provider_id is None:
            return _block(
                code="selected_option_provider_missing",
                message="classic doctrine requires an active selected-option provider",
                checks={**checks, "active_selected_option_provider_present": False},
            )
        checks["active_selected_option_provider_present"] = True

        if runtime.strategy_runtime_mode == N.STRATEGY_RUNTIME_MODE_NORMAL:
            if provider.active_option_context_provider_id is None:
                return _block(
                    code="option_context_provider_missing",
                    message="NORMAL classic mode requires active option-context provider truth",
                    checks={**checks, "active_option_context_provider_present": False},
                )
            checks["active_option_context_provider_present"] = True
        elif runtime.strategy_runtime_mode == N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED:
            checks["active_option_context_provider_present"] = (
                provider.active_option_context_provider_id is not None
            )
        else:
            return _block(
                code="invalid_classic_runtime_mode",
                message=(
                    "classic doctrine runtime mode must be NORMAL or DHAN_DEGRADED "
                    f"for live entry, got {runtime.strategy_runtime_mode!r}"
                ),
                checks={**checks, "classic_runtime_mode_valid": False},
            )
        checks["classic_runtime_mode_valid"] = True
        return _pass(checks)

    expected_fut = profile.futures_provider_id
    expected_opt = profile.selected_option_provider_id
    expected_ctx = profile.option_context_provider_id

    if provider.active_futures_provider_id != expected_fut:
        return _block(
            code="miso_futures_provider_mismatch",
            message=(
                "MISO requires Dhan futures signal path, got "
                f"{provider.active_futures_provider_id!r}"
            ),
            checks={**checks, "miso_futures_provider_ok": False},
        )
    checks["miso_futures_provider_ok"] = True

    if provider.active_selected_option_provider_id != expected_opt:
        return _block(
            code="miso_selected_option_provider_mismatch",
            message=(
                "MISO requires Dhan selected-option signal path, got "
                f"{provider.active_selected_option_provider_id!r}"
            ),
            checks={**checks, "miso_selected_option_provider_ok": False},
        )
    checks["miso_selected_option_provider_ok"] = True

    if provider.active_option_context_provider_id != expected_ctx:
        return _block(
            code="miso_option_context_provider_mismatch",
            message=(
                "MISO requires Dhan option-context path, got "
                f"{provider.active_option_context_provider_id!r}"
            ),
            checks={**checks, "miso_option_context_provider_ok": False},
        )
    checks["miso_option_context_provider_ok"] = True

    if runtime.strategy_runtime_mode not in (
        N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
        N.STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED,
    ):
        return _block(
            code="miso_runtime_mode_invalid",
            message=(
                "MISO live entry requires BASE_5DEPTH or DEPTH20_ENHANCED mode, got "
                f"{runtime.strategy_runtime_mode!r}"
            ),
            checks={**checks, "miso_runtime_mode_valid": False},
        )
    checks["miso_runtime_mode_valid"] = True

    if require_execution_bridge and profile.execution_bridge_required and not provider.execution_bridge_ok:
        return _block(
            code="miso_execution_bridge_missing",
            message="MISO live entry requires explicit execution_bridge_ok",
            checks={**checks, "execution_bridge_ok": False},
        )
    checks["execution_bridge_ok"] = True

    return _pass(checks)


def pre_entry_gate(
    runtime: DoctrineRuntimeInput,
    *,
    require_execution_bridge: bool = True,
) -> EligibilityResult:
    for gate in (
        evaluate_rollout_gate(runtime),
        evaluate_position_gate(runtime),
        evaluate_risk_gate(runtime),
        evaluate_provider_profile_gate(
            runtime,
            require_execution_bridge=require_execution_bridge,
        ),
    ):
        if not gate.passed:
            return gate
    return _pass(
        {
            "family_runtime_mode_live": True,
            "flat_position_required": True,
            "risk_gate_pass": True,
            "provider_profile_pass": True,
        }
    )


def is_reentry_exit_reason_allowed(
    family_id: str,
    exit_reason: str | None,
    pnl_points: float | None = None,
) -> bool:
    reason = normalize_reason(exit_reason)
    if reason in FORBIDDEN_REENTRY_EXIT_REASONS.get(family_id, ()):
        return False

    allowed = ALLOWED_REENTRY_EXIT_REASONS.get(family_id, ())
    if reason not in allowed:
        return False

    if reason == "time_stall" and (pnl_points is None or pnl_points <= 0):
        return False
    return True


def reentry_cap_allows(
    family_id: str,
    regime: str | None,
    current_reentry_count: int,
) -> bool:
    normalized_regime = normalize_regime(regime)
    caps = DEFAULT_REENTRY_CAPS.get(family_id, {"LOWVOL": 0, "NORMAL": 0, "FAST": 0})
    allowed = caps.get(normalized_regime, 0)
    return current_reentry_count < allowed


__all__ = [
    "EligibilityResult",
    "evaluate_position_gate",
    "evaluate_provider_profile_gate",
    "evaluate_risk_gate",
    "evaluate_rollout_gate",
    "is_reentry_exit_reason_allowed",
    "pre_entry_gate",
    "reentry_cap_allows",
]
