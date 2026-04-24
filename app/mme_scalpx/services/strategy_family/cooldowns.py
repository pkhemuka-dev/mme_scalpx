from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/cooldowns.py

Freeze-grade cooldown routing helpers for ScalpX MME strategy-family.

Purpose
-------
This module OWNS:
- deterministic cooldown routing from family / exit-reason / regime / outcome
- normalized cooldown-decision packaging for downstream strategy-family logic
- parameter-key resolution against doctrine param mappings
- stable default cooldown behavior when doctrine params are absent
- explicit session-reset routing where doctrine requires it

This module DOES NOT own:
- Redis reads or writes
- cooldown state mutation / persistence
- strategy state-machine ownership
- feature computation
- entry/exit decision publication
- broker truth
- risk truth

Frozen design law
-----------------
- This module computes cooldown recommendations only.
- It must remain deterministic, side-effect free, and replay-safe.
- It must not invent new family identities or regime vocabularies.
- It must tolerate missing doctrine params by falling back to frozen defaults.
- Family/doctrine policy may differ, but routing behavior must be explicit.
- Unknown exit reasons must not silently fall through unless the caller
  explicitly opts into default handling.
"""

from dataclasses import dataclass, field
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

from .common import normalize_reason, normalize_regime

# ============================================================================ #
# Exceptions
# ============================================================================ #


class CooldownError(ValueError):
    """Raised when cooldown routing inputs are invalid."""


# ============================================================================ #
# Typed outputs
# ============================================================================ #

SCOPE_SECONDS: Final[str] = "SECONDS"
SCOPE_SESSION_RESET: Final[str] = "SESSION_RESET"


@dataclass(frozen=True, slots=True)
class CooldownDecision:
    """Deterministic cooldown routing result."""

    reason_code: str
    seconds: float
    param_key: str | None = None
    family_id: str | None = None
    regime: str | None = None
    scope: str = SCOPE_SECONDS
    session_reset_required: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason_code": self.reason_code,
            "seconds": self.seconds,
            "param_key": self.param_key,
            "family_id": self.family_id,
            "regime": self.regime,
            "scope": self.scope,
            "session_reset_required": self.session_reset_required,
            "metadata": dict(self.metadata),
        }


# ============================================================================ #
# Frozen reason groups
# ============================================================================ #

TARGET_REASONS: Final[frozenset[str]] = frozenset(
    {
        "hard_target",
        "hard_target_exit",
    }
)

STOP_REASONS: Final[frozenset[str]] = frozenset(
    {
        "hard_stop",
        "hard_stop_exit",
    }
)

FEED_FAIL_REASONS: Final[frozenset[str]] = frozenset(
    {
        "feed_failure",
        "feed_failure_exit",
    }
)

PROFIT_STALL_REASONS: Final[frozenset[str]] = frozenset(
    {
        "profit_stall",
        "profit_stall_exit",
    }
)

TIME_STALL_REASONS: Final[frozenset[str]] = frozenset(
    {
        "time_stall",
        "time_stall_exit",
        "max_hold_exit",
        "early_stall_exit",
    }
)

LIQUIDITY_REASONS: Final[frozenset[str]] = frozenset(
    {
        "liquidity_exit",
    }
)

MICRO_FAIL_REASONS: Final[frozenset[str]] = frozenset(
    {
        "microstructure_failure_exit",
        "breakout_failure_exit",
        "breakout_retest_failure_exit",
        "proof_failure_exit",
        "momentum_fade_exit",
        "futures_option_divergence_exit",
        "absorption_under_response_exit",
        "large_counter_trade_exit",
    }
)

PROOF_FAILURE_REASONS: Final[frozenset[str]] = frozenset(
    {
        "proof_failure_exit",
        "stage1_proof_failure_exit",
        "stage2_proof_failure_exit",
    }
)

OTHER_EXIT_REASONS: Final[frozenset[str]] = frozenset(
    {
        "premium_under_response_exit",
        "futures_option_divergence_exit",
        "momentum_fade_exit",
        "profit_stall_exit",
        "profit_stall",
        "absorption_under_response_exit",
    }
)

SESSION_END_REASONS: Final[frozenset[str]] = frozenset(
    {
        "session_end_flatten_exit",
        "forced_flatten_exit",
        "session_flatten_exit",
        "session_end_exit",
    }
)

DISASTER_REASONS: Final[frozenset[str]] = frozenset(
    {
        "disaster_stop_exit",
    }
)

RECONCILIATION_REASONS: Final[frozenset[str]] = frozenset(
    {
        "reconciliation_exit",
    }
)


# ============================================================================ #
# Frozen family defaults
# ============================================================================ #

_DEFAULT_BY_FAMILY_AND_BUCKET: Final[dict[str, dict[str, float]]] = {
    N.STRATEGY_FAMILY_MIST: {
        "TARGET_LOWVOL": 12.0,
        "TARGET_NORMAL": 8.0,
        "TARGET_FAST": 5.0,
        "STOP": 12.0,
        "FEED_FAIL": 30.0,
        "LIQUIDITY": 10.0,
        "PROFIT_STALL": 8.0,
        "TIME_STALL": 8.0,
        "MICRO_FAIL": 12.0,
        "PROOF_FAIL": 12.0,
        "OTHER_EXIT": 8.0,
        "DISASTER": 300.0,
        "RECONCILIATION": 30.0,
        "DEFAULT": 5.0,
        "SESSION_RESET": 0.0,
    },
    N.STRATEGY_FAMILY_MISB: {
        "TARGET_LOWVOL": 10.0,
        "TARGET_NORMAL": 10.0,
        "TARGET_FAST": 10.0,
        "STOP": 12.0,
        "FEED_FAIL": 30.0,
        "LIQUIDITY": 10.0,
        "PROFIT_STALL": 8.0,
        "TIME_STALL": 8.0,
        "MICRO_FAIL": 12.0,
        "PROOF_FAIL": 12.0,
        "OTHER_EXIT": 8.0,
        "DISASTER": 300.0,
        "RECONCILIATION": 30.0,
        "DEFAULT": 5.0,
        "SESSION_RESET": 0.0,
    },
    N.STRATEGY_FAMILY_MISC: {
        "TARGET_LOWVOL": 10.0,
        "TARGET_NORMAL": 10.0,
        "TARGET_FAST": 10.0,
        "STOP": 12.0,
        "FEED_FAIL": 30.0,
        "LIQUIDITY": 10.0,
        "PROFIT_STALL": 8.0,
        "TIME_STALL": 8.0,
        "MICRO_FAIL": 12.0,
        "PROOF_FAIL": 12.0,
        "OTHER_EXIT": 8.0,
        "DISASTER": 300.0,
        "RECONCILIATION": 30.0,
        "DEFAULT": 5.0,
        "SESSION_RESET": 0.0,
    },
    N.STRATEGY_FAMILY_MISR: {
        "TARGET_LOWVOL": 10.0,
        "TARGET_NORMAL": 10.0,
        "TARGET_FAST": 10.0,
        "STOP": 12.0,
        "FEED_FAIL": 30.0,
        "LIQUIDITY": 10.0,
        "PROFIT_STALL": 8.0,
        "TIME_STALL": 8.0,
        "MICRO_FAIL": 12.0,
        "PROOF_FAIL": 12.0,
        "OTHER_EXIT": 8.0,
        "DISASTER": 300.0,
        "RECONCILIATION": 30.0,
        "DEFAULT": 5.0,
        "SESSION_RESET": 0.0,
    },
    N.STRATEGY_FAMILY_MISO: {
        "TARGET_LOWVOL": 45.0,
        "TARGET_NORMAL": 45.0,
        "TARGET_FAST": 45.0,
        "STOP": 180.0,
        "FEED_FAIL": 600.0,
        "LIQUIDITY": 120.0,
        "PROFIT_STALL": 8.0,
        "TIME_STALL": 90.0,
        "MICRO_FAIL": 150.0,
        "PROOF_FAIL": 150.0,
        "OTHER_EXIT": 90.0,
        "DISASTER": 300.0,
        "RECONCILIATION": 30.0,
        "DEFAULT": 5.0,
        "SESSION_RESET": 0.0,
    },
}

_SUPPORTED_FAMILIES: Final[tuple[str, ...]] = tuple(_DEFAULT_BY_FAMILY_AND_BUCKET.keys())


# ============================================================================ #
# Internal helpers
# ============================================================================ #


def _fail(message: str) -> None:
    raise CooldownError(message)


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _strict_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or value is None:
        _fail(f"{field_name} must be a finite float-compatible value")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise CooldownError(f"{field_name} must be float-compatible") from exc
    if out != out or out in (float("inf"), float("-inf")):
        _fail(f"{field_name} must be finite")
    return out


def _non_negative_float(value: Any, field_name: str) -> float:
    out = _strict_float(value, field_name)
    _require(out >= 0.0, f"{field_name} must be >= 0")
    return out


def _lookup(
    params: Mapping[str, Any],
    *keys: str,
) -> tuple[float | None, str | None]:
    for key in keys:
        if key in params and params[key] is not None:
            return _non_negative_float(params[key], f"params[{key!r}]"), key
    return None, None


def _target_bucket_key(regime: str) -> str:
    if regime == "LOWVOL":
        return "TARGET_LOWVOL"
    if regime == "FAST":
        return "TARGET_FAST"
    return "TARGET_NORMAL"


def _defaults_for_family(family_id: str) -> Mapping[str, float]:
    _require(
        family_id in _SUPPORTED_FAMILIES,
        f"unsupported family_id: {family_id!r}",
    )
    return _DEFAULT_BY_FAMILY_AND_BUCKET[family_id]


def _decision(
    *,
    family_id: str,
    regime: str,
    reason_code: str,
    seconds: float,
    param_key: str | None,
    bucket: str,
    scope: str = SCOPE_SECONDS,
    session_reset_required: bool = False,
    extra_metadata: Mapping[str, Any] | None = None,
) -> CooldownDecision:
    _require(scope in (SCOPE_SECONDS, SCOPE_SESSION_RESET), f"invalid scope: {scope!r}")
    _require(seconds >= 0.0, "cooldown seconds must be >= 0")
    metadata = {
        "bucket": bucket,
        "used_param_key": param_key,
        "used_default": param_key is None,
    }
    if extra_metadata:
        metadata.update(dict(extra_metadata))
    return CooldownDecision(
        reason_code=reason_code,
        seconds=seconds,
        param_key=param_key,
        family_id=family_id,
        regime=regime,
        scope=scope,
        session_reset_required=session_reset_required,
        metadata=metadata,
    )


def _is_profitable_exit(
    *,
    exit_pnl_points: float | None,
    exit_was_profitable: bool | None,
) -> bool | None:
    if exit_was_profitable is not None:
        return bool(exit_was_profitable)
    if exit_pnl_points is None:
        return None
    return _strict_float(exit_pnl_points, "exit_pnl_points") > 0.0


def _bucket_and_keys_for_reason(
    *,
    family_id: str,
    normalized_reason: str,
    normalized_regime: str,
    profitable_exit: bool | None,
) -> tuple[str, tuple[str, ...], str, str, bool]:
    """
    Returns:
    - bucket
    - param lookup keys
    - scope
    - metadata policy tag
    - session_reset_required
    """
    if normalized_reason in SESSION_END_REASONS:
        return (
            "SESSION_RESET",
            (),
            SCOPE_SESSION_RESET,
            "session_reset",
            True,
        )

    if normalized_reason in TARGET_REASONS:
        bucket = _target_bucket_key(normalized_regime)
        return (
            bucket,
            (
                f"COOLDOWN_AFTER_TARGET_{normalized_regime}_SEC",
                f"COOLDOWN_AFTER_TARGET_{normalized_regime}",
                "COOLDOWN_AFTER_TARGET_SEC",
                "COOLDOWN_AFTER_TARGET",
            ),
            SCOPE_SECONDS,
            "target",
            False,
        )

    if normalized_reason in STOP_REASONS:
        return (
            "STOP",
            (
                "COOLDOWN_AFTER_STOP_SEC",
                "COOLDOWN_AFTER_STOP",
            ),
            SCOPE_SECONDS,
            "stop",
            False,
        )

    if normalized_reason in DISASTER_REASONS:
        return (
            "DISASTER",
            (
                "COOLDOWN_AFTER_DISASTER_SEC",
                "COOLDOWN_AFTER_DISASTER",
            ),
            SCOPE_SECONDS,
            "disaster",
            False,
        )

    if normalized_reason in FEED_FAIL_REASONS:
        return (
            "FEED_FAIL",
            (
                "COOLDOWN_AFTER_FEED_FAIL_SEC",
                "COOLDOWN_AFTER_FEED_FAIL",
            ),
            SCOPE_SECONDS,
            "feed_fail",
            False,
        )

    if normalized_reason in LIQUIDITY_REASONS:
        return (
            "LIQUIDITY",
            (
                "COOLDOWN_AFTER_LIQUIDITY_SEC",
                "COOLDOWN_AFTER_LIQUIDITY",
            ),
            SCOPE_SECONDS,
            "liquidity",
            False,
        )

    if family_id == N.STRATEGY_FAMILY_MISR and normalized_reason in PROOF_FAILURE_REASONS:
        return (
            "PROOF_FAIL",
            (
                "COOLDOWN_AFTER_PROOF_FAILURE_SEC",
                "COOLDOWN_AFTER_PROOF_FAILURE",
            ),
            SCOPE_SECONDS,
            "misr_proof_failure",
            False,
        )

    if family_id == N.STRATEGY_FAMILY_MISR and normalized_reason in OTHER_EXIT_REASONS:
        return (
            "OTHER_EXIT",
            (
                "COOLDOWN_AFTER_OTHER_EXIT_SEC",
                "COOLDOWN_AFTER_OTHER_EXIT",
            ),
            SCOPE_SECONDS,
            "misr_other_exit",
            False,
        )

    if family_id == N.STRATEGY_FAMILY_MISB and normalized_reason in TIME_STALL_REASONS:
        if profitable_exit is True:
            bucket = _target_bucket_key(normalized_regime)
            return (
                bucket,
                (
                    f"COOLDOWN_AFTER_TARGET_{normalized_regime}_SEC",
                    f"COOLDOWN_AFTER_TARGET_{normalized_regime}",
                    "COOLDOWN_AFTER_TARGET_SEC",
                    "COOLDOWN_AFTER_TARGET",
                ),
                SCOPE_SECONDS,
                "misb_time_stall_profitable_target",
                False,
            )
        if profitable_exit is False:
            return (
                "STOP",
                (
                    "COOLDOWN_AFTER_STOP_SEC",
                    "COOLDOWN_AFTER_STOP",
                ),
                SCOPE_SECONDS,
                "misb_time_stall_non_profitable_stop",
                False,
            )

    if normalized_reason in PROFIT_STALL_REASONS:
        return (
            "PROFIT_STALL",
            (
                "COOLDOWN_AFTER_PROFIT_STALL_SEC",
                "COOLDOWN_AFTER_PROFIT_STALL",
            ),
            SCOPE_SECONDS,
            "profit_stall",
            False,
        )

    if normalized_reason in TIME_STALL_REASONS:
        return (
            "TIME_STALL",
            (
                "COOLDOWN_AFTER_STALL_SEC",
                "COOLDOWN_AFTER_STALL",
            ),
            SCOPE_SECONDS,
            "time_stall",
            False,
        )

    if normalized_reason in MICRO_FAIL_REASONS:
        return (
            "MICRO_FAIL",
            (
                "COOLDOWN_AFTER_MICRO_FAIL_SEC",
                "COOLDOWN_AFTER_MICRO_FAIL",
            ),
            SCOPE_SECONDS,
            "micro_fail",
            False,
        )

    if normalized_reason in RECONCILIATION_REASONS:
        return (
            "RECONCILIATION",
            (
                "COOLDOWN_AFTER_RECONCILIATION_SEC",
                "COOLDOWN_AFTER_RECONCILIATION",
            ),
            SCOPE_SECONDS,
            "reconciliation",
            False,
        )

    raise CooldownError(f"unsupported exit reason for cooldown routing: {normalized_reason!r}")


# ============================================================================ #
# Public cooldown routing
# ============================================================================ #


def route_cooldown(
    *,
    family_id: str,
    exit_reason: str,
    regime: str | None,
    params: Mapping[str, Any],
    exit_pnl_points: float | None = None,
    exit_was_profitable: bool | None = None,
    allow_default_unknown: bool = False,
) -> CooldownDecision:
    """
    Route a cooldown decision from family / normalized exit reason / regime.

    Lookup precedence:
    1. family/regime-specific doctrine params where applicable
    2. family-neutral doctrine params
    3. frozen family defaults

    By default, unknown reasons are rejected.
    Set allow_default_unknown=True only when the caller explicitly wants a
    fallback default policy.
    """
    _require(isinstance(params, Mapping), "params must be a mapping")

    normalized_reason = normalize_reason(exit_reason)
    normalized_regime = normalize_regime(regime)
    defaults = _defaults_for_family(family_id)
    profitable_exit = _is_profitable_exit(
        exit_pnl_points=exit_pnl_points,
        exit_was_profitable=exit_was_profitable,
    )

    try:
        bucket, key_candidates, scope, policy, session_reset_required = _bucket_and_keys_for_reason(
            family_id=family_id,
            normalized_reason=normalized_reason,
            normalized_regime=normalized_regime,
            profitable_exit=profitable_exit,
        )
    except CooldownError:
        if not allow_default_unknown:
            raise
        bucket = "DEFAULT"
        key_candidates = (
            "COOLDOWN_DEFAULT_SEC",
            "COOLDOWN_DEFAULT",
        )
        scope = SCOPE_SECONDS
        policy = "default_unknown"
        session_reset_required = False

    value, key = _lookup(params, *key_candidates) if key_candidates else (None, None)
    seconds = defaults[bucket] if value is None else value

    return _decision(
        family_id=family_id,
        regime=normalized_regime,
        reason_code=normalized_reason,
        seconds=seconds,
        param_key=key,
        bucket=bucket,
        scope=scope,
        session_reset_required=session_reset_required,
        extra_metadata={
            "route_policy": policy,
            "profitable_exit": profitable_exit,
        },
    )


__all__ = [
    "CooldownDecision",
    "CooldownError",
    "DISASTER_REASONS",
    "FEED_FAIL_REASONS",
    "LIQUIDITY_REASONS",
    "MICRO_FAIL_REASONS",
    "PROFIT_STALL_REASONS",
    "PROOF_FAILURE_REASONS",
    "OTHER_EXIT_REASONS",
    "RECONCILIATION_REASONS",
    "SESSION_END_REASONS",
    "STOP_REASONS",
    "TARGET_REASONS",
    "TIME_STALL_REASONS",
    "SCOPE_SECONDS",
    "SCOPE_SESSION_RESET",
    "route_cooldown",
]
