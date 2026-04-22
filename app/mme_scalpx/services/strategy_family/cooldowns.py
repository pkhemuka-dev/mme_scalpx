from __future__ import annotations

"""
app/mme_scalpx/strategy_family/cooldowns.py

Shared cooldown routing helpers for doctrine evaluators and the future thin
strategy-family coordinator.

Purpose
-------
This module OWNS:
- normalized exit-reason grouping
- parameter-driven cooldown lookup
- deterministic cooldown fallback routing

This module DOES NOT own:
- doctrine-specific entry logic
- Redis access
- live state mutation
"""

from dataclasses import dataclass, field
from typing import Any, Mapping

from app.mme_scalpx.core import names as N

from .common import normalize_reason, normalize_regime, safe_float

TARGET_REASONS = {"hard_target", "hard_target_exit"}
STOP_REASONS = {"hard_stop", "hard_stop_exit"}
FEED_FAIL_REASONS = {"feed_failure", "feed_failure_exit"}
PROFIT_STALL_REASONS = {"profit_stall", "profit_stall_exit"}
TIME_STALL_REASONS = {"time_stall", "time_stall_exit", "max_hold_exit", "early_stall_exit"}
LIQUIDITY_REASONS = {"liquidity_exit"}
MICRO_FAIL_REASONS = {
    "microstructure_failure_exit",
    "breakout_failure_exit",
    "breakout_retest_failure_exit",
    "proof_failure_exit",
    "momentum_fade_exit",
    "futures_option_divergence_exit",
    "absorption_under_response_exit",
    "large_counter_trade_exit",
}
DISASTER_REASONS = {"disaster_stop_exit"}
RECONCILIATION_REASONS = {"reconciliation_exit"}


@dataclass(frozen=True, slots=True)
class CooldownDecision:
    reason_code: str
    seconds: float
    param_key: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


def _lookup(params: Mapping[str, Any], *keys: str) -> tuple[float | None, str | None]:
    for key in keys:
        if key in params:
            return safe_float(params[key], 0.0), key
    return None, None


def route_cooldown(
    *,
    family_id: str,
    exit_reason: str,
    regime: str | None,
    params: Mapping[str, Any],
) -> CooldownDecision:
    normalized_reason = normalize_reason(exit_reason)
    normalized_regime = normalize_regime(regime)

    if normalized_reason in TARGET_REASONS:
        if family_id == N.STRATEGY_FAMILY_MIST:
            value, key = _lookup(
                params,
                f"COOLDOWN_AFTER_TARGET_{normalized_regime}_SEC",
                f"COOLDOWN_AFTER_TARGET_{normalized_regime}",
                "COOLDOWN_AFTER_TARGET_SEC",
                "COOLDOWN_AFTER_TARGET",
            )
            if value is None:
                value = {"LOWVOL": 12.0, "NORMAL": 8.0, "FAST": 5.0}[normalized_regime]
            return CooldownDecision(
                reason_code=normalized_reason,
                seconds=value,
                param_key=key,
                metadata={"family_id": family_id, "regime": normalized_regime},
            )

        if family_id == N.STRATEGY_FAMILY_MISO:
            value, key = _lookup(params, "COOLDOWN_AFTER_TARGET_SEC", "COOLDOWN_AFTER_TARGET")
            return CooldownDecision(
                reason_code=normalized_reason,
                seconds=(45.0 if value is None else value),
                param_key=key,
                metadata={"family_id": family_id, "regime": normalized_regime},
            )

        value, key = _lookup(
            params,
            f"COOLDOWN_AFTER_TARGET_{normalized_regime}_SEC",
            f"COOLDOWN_AFTER_TARGET_{normalized_regime}",
            "COOLDOWN_AFTER_TARGET_SEC",
            "COOLDOWN_AFTER_TARGET",
        )
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=(10.0 if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in STOP_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_STOP_SEC", "COOLDOWN_AFTER_STOP")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=((180.0 if family_id == N.STRATEGY_FAMILY_MISO else 12.0) if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in DISASTER_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_DISASTER_SEC", "COOLDOWN_AFTER_DISASTER")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=(300.0 if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in FEED_FAIL_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_FEED_FAIL_SEC", "COOLDOWN_AFTER_FEED_FAIL")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=((600.0 if family_id == N.STRATEGY_FAMILY_MISO else 30.0) if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in LIQUIDITY_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_LIQUIDITY_SEC", "COOLDOWN_AFTER_LIQUIDITY")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=((120.0 if family_id == N.STRATEGY_FAMILY_MISO else 10.0) if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in PROFIT_STALL_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_PROFIT_STALL_SEC", "COOLDOWN_AFTER_PROFIT_STALL")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=(8.0 if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in TIME_STALL_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_STALL_SEC", "COOLDOWN_AFTER_STALL")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=((90.0 if family_id == N.STRATEGY_FAMILY_MISO else 8.0) if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in MICRO_FAIL_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_MICRO_FAIL_SEC", "COOLDOWN_AFTER_MICRO_FAIL")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=((150.0 if family_id == N.STRATEGY_FAMILY_MISO else 12.0) if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    if normalized_reason in RECONCILIATION_REASONS:
        value, key = _lookup(params, "COOLDOWN_AFTER_RECONCILIATION_SEC", "COOLDOWN_AFTER_RECONCILIATION")
        return CooldownDecision(
            reason_code=normalized_reason,
            seconds=(30.0 if value is None else value),
            param_key=key,
            metadata={"family_id": family_id, "regime": normalized_regime},
        )

    value, key = _lookup(params, "COOLDOWN_DEFAULT_SEC", "COOLDOWN_DEFAULT")
    return CooldownDecision(
        reason_code=normalized_reason,
        seconds=(5.0 if value is None else value),
        param_key=key,
        metadata={"family_id": family_id, "regime": normalized_regime},
    )


__all__ = ["CooldownDecision", "route_cooldown"]
