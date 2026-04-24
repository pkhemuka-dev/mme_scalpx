from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/common.py

Shared immutable helpers and family-neutral constants for strategy-family
doctrine extraction.

Purpose
-------
This module OWNS:
- family-neutral strategy-family constants
- family / branch / doctrine routing helpers
- frozen param-path registry for doctrine YAMLs
- deterministic scalar coercion helpers for family/doctrine code
- deterministic nested mapping lookup helpers
- normalized reason / regime helpers
- additive re-entry policy registries shared across doctrines

This module DOES NOT own:
- Redis access
- live publishing
- feature math
- broker truth
- risk truth mutation
- doctrine-specific signal logic
- composition wiring

Design rules
------------
- This module is static / deterministic and must remain runtime-agnostic.
- It must not depend on Redis, settings mutation, or service ownership logic.
- Mappings are frozen at import time to avoid accidental mutation.
- Family/doctrine/branch surfaces must align exactly with canonical names.py
  symbols and with the frozen migration plan.
"""

from types import MappingProxyType
from typing import Any, Final, Mapping
from uuid import uuid4

from app.mme_scalpx.core import names as N

# ============================================================================
# Exceptions / helpers
# ============================================================================


class StrategyFamilyCommonError(ValueError):
    """Raised when common strategy-family constants are internally inconsistent."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StrategyFamilyCommonError(message)


def _require_non_empty_str(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise StrategyFamilyCommonError(
            f"{field_name} must be str, got {type(value).__name__}"
        )
    cleaned = value.strip()
    if not cleaned:
        raise StrategyFamilyCommonError(f"{field_name} must be non-empty")
    return cleaned


def _freeze_mapping(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(mapping))


def _freeze_nested_mapping(
    mapping: Mapping[str, Mapping[str, Any] | tuple[str, ...]]
) -> Mapping[str, Mapping[str, Any] | tuple[str, ...]]:
    frozen: dict[str, Mapping[str, Any] | tuple[str, ...]] = {}
    for key, value in mapping.items():
        if isinstance(value, Mapping):
            frozen[key] = MappingProxyType(dict(value))
        else:
            frozen[key] = value
    return MappingProxyType(frozen)


# ============================================================================
# Frozen family/runtime identities
# ============================================================================

LIVE_FAMILY_MODES: Final[tuple[str, ...]] = (
    N.FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW,
    N.FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY,
)

CLASSIC_FAMILIES: Final[tuple[str, ...]] = (
    N.STRATEGY_FAMILY_MIST,
    N.STRATEGY_FAMILY_MISB,
    N.STRATEGY_FAMILY_MISC,
    N.STRATEGY_FAMILY_MISR,
)

FAMILY_ORDER: Final[tuple[str, ...]] = (
    N.STRATEGY_FAMILY_MIST,
    N.STRATEGY_FAMILY_MISB,
    N.STRATEGY_FAMILY_MISC,
    N.STRATEGY_FAMILY_MISR,
    N.STRATEGY_FAMILY_MISO,
)

DOCTRINE_BY_FAMILY: Final[Mapping[str, str]] = _freeze_mapping(
    {
        N.STRATEGY_FAMILY_MIST: N.DOCTRINE_MIST,
        N.STRATEGY_FAMILY_MISB: N.DOCTRINE_MISB,
        N.STRATEGY_FAMILY_MISC: N.DOCTRINE_MISC,
        N.STRATEGY_FAMILY_MISR: N.DOCTRINE_MISR,
        N.STRATEGY_FAMILY_MISO: N.DOCTRINE_MISO,
    }
)

BRANCH_TO_SIDE: Final[Mapping[str, str]] = _freeze_mapping(
    {
        N.BRANCH_CALL: N.SIDE_CALL,
        N.BRANCH_PUT: N.SIDE_PUT,
    }
)

BRANCH_TO_POSITION_SIDE: Final[Mapping[str, str]] = _freeze_mapping(
    {
        N.BRANCH_CALL: N.POSITION_SIDE_LONG_CALL,
        N.BRANCH_PUT: N.POSITION_SIDE_LONG_PUT,
    }
)

BRANCH_TO_STRATEGY_MODE: Final[Mapping[str, str]] = _freeze_mapping(
    {
        N.BRANCH_CALL: N.STRATEGY_CALL,
        N.BRANCH_PUT: N.STRATEGY_PUT,
    }
)

DOCTRINE_PARAM_PATHS: Final[Mapping[tuple[str, str], str]] = MappingProxyType(
    {
        (N.STRATEGY_FAMILY_MIST, N.BRANCH_CALL): "etc/strategy_family/frozen/mist_call.yaml",
        (N.STRATEGY_FAMILY_MIST, N.BRANCH_PUT): "etc/strategy_family/frozen/mist_put.yaml",
        (N.STRATEGY_FAMILY_MISB, N.BRANCH_CALL): "etc/strategy_family/frozen/misb_call.yaml",
        (N.STRATEGY_FAMILY_MISB, N.BRANCH_PUT): "etc/strategy_family/frozen/misb_put.yaml",
        (N.STRATEGY_FAMILY_MISC, N.BRANCH_CALL): "etc/strategy_family/frozen/misc_call.yaml",
        (N.STRATEGY_FAMILY_MISC, N.BRANCH_PUT): "etc/strategy_family/frozen/misc_put.yaml",
        (N.STRATEGY_FAMILY_MISR, N.BRANCH_CALL): "etc/strategy_family/frozen/misr_call.yaml",
        (N.STRATEGY_FAMILY_MISR, N.BRANCH_PUT): "etc/strategy_family/frozen/misr_put.yaml",
        (N.STRATEGY_FAMILY_MISO, N.BRANCH_CALL): "etc/strategy_family/frozen/miso_call.yaml",
        (N.STRATEGY_FAMILY_MISO, N.BRANCH_PUT): "etc/strategy_family/frozen/miso_put.yaml",
    }
)

# ============================================================================
# Frozen shared re-entry policy registries
# ============================================================================

ALLOWED_REENTRY_EXIT_REASONS: Final[Mapping[str, tuple[str, ...]]] = _freeze_nested_mapping(
    {
        N.STRATEGY_FAMILY_MIST: ("hard_target", "profit_stall", "time_stall"),
        N.STRATEGY_FAMILY_MISB: (
            "hard_target",
            "profit_stall",
            "time_stall",
            "max_hold_exit",
        ),
        N.STRATEGY_FAMILY_MISC: ("hard_target", "profit_stall", "time_stall"),
        N.STRATEGY_FAMILY_MISR: (),
        N.STRATEGY_FAMILY_MISO: (),
    }
)

FORBIDDEN_REENTRY_EXIT_REASONS: Final[
    Mapping[str, tuple[str, ...]]
] = _freeze_nested_mapping(
    {
        N.STRATEGY_FAMILY_MIST: (
            "hard_stop",
            "proof_failure_exit",
            "feed_failure_exit",
            "futures_option_divergence_exit",
            "absorption_under_response_exit",
            "liquidity_exit",
            "momentum_fade_exit",
        ),
        N.STRATEGY_FAMILY_MISB: (
            "hard_stop",
            "proof_failure_exit",
            "breakout_failure_exit",
            "feed_failure_exit",
            "futures_option_divergence_exit",
            "absorption_under_response_exit",
            "liquidity_exit",
            "momentum_fade_exit",
        ),
        N.STRATEGY_FAMILY_MISC: (
            "hard_stop",
            "proof_failure_exit",
            "breakout_failure_exit",
            "feed_failure_exit",
            "futures_option_divergence_exit",
            "absorption_under_response_exit",
            "liquidity_exit",
            "momentum_fade_exit",
        ),
        N.STRATEGY_FAMILY_MISR: (
            "hard_stop",
            "proof_failure_exit",
            "breakout_failure_exit",
            "feed_failure_exit",
            "futures_option_divergence_exit",
            "absorption_under_response_exit",
            "liquidity_exit",
            "momentum_fade_exit",
        ),
        N.STRATEGY_FAMILY_MISO: (
            "hard_stop",
            "disaster_stop_exit",
            "microstructure_failure_exit",
            "feed_failure_exit",
            "reconciliation_exit",
        ),
    }
)

DEFAULT_REENTRY_CAPS: Final[Mapping[str, Mapping[str, int]]] = _freeze_nested_mapping(
    {
        N.STRATEGY_FAMILY_MIST: {"LOWVOL": 0, "NORMAL": 1, "FAST": 1},
        N.STRATEGY_FAMILY_MISB: {"LOWVOL": 0, "NORMAL": 1, "FAST": 1},
        N.STRATEGY_FAMILY_MISC: {"LOWVOL": 0, "NORMAL": 1, "FAST": 1},
        N.STRATEGY_FAMILY_MISR: {"LOWVOL": 0, "NORMAL": 0, "FAST": 0},
        N.STRATEGY_FAMILY_MISO: {"LOWVOL": 0, "NORMAL": 0, "FAST": 0},
    }
)

_ALLOWED_REGIMES: Final[tuple[str, ...]] = ("LOWVOL", "NORMAL", "FAST")

# ============================================================================
# Scalar / normalization helpers
# ============================================================================


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else default
    return str(value)


def safe_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    normalized = safe_str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return float(int(value))
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_regime(value: str | None) -> str:
    normalized = safe_str(value, "NORMAL").upper()
    if normalized not in _ALLOWED_REGIMES:
        return "NORMAL"
    return normalized


def normalize_reason(value: str | None) -> str:
    normalized = safe_str(value).lower().replace("-", "_").replace(" ", "_")
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized


def new_id(prefix: str) -> str:
    stem = safe_str(prefix, "id").replace(" ", "_")
    return f"{stem}-{uuid4().hex[:20]}"


# ============================================================================
# Routing helpers
# ============================================================================


def family_is_classic(family_id: str) -> bool:
    return safe_str(family_id) in CLASSIC_FAMILIES


def family_requires_dhan_signal_path(family_id: str) -> bool:
    return safe_str(family_id) == N.STRATEGY_FAMILY_MISO


def doctrine_for_family(family_id: str) -> str:
    normalized = safe_str(family_id)
    doctrine = DOCTRINE_BY_FAMILY.get(normalized)
    if doctrine is None:
        raise ValueError(f"unknown family_id: {family_id!r}")
    return doctrine


def side_for_branch(branch_id: str) -> str:
    normalized = safe_str(branch_id)
    side = BRANCH_TO_SIDE.get(normalized)
    if side is None:
        raise ValueError(f"unknown branch_id: {branch_id!r}")
    return side


def position_side_for_branch(branch_id: str) -> str:
    normalized = safe_str(branch_id)
    position_side = BRANCH_TO_POSITION_SIDE.get(normalized)
    if position_side is None:
        raise ValueError(f"unknown branch_id: {branch_id!r}")
    return position_side


def strategy_mode_for_branch(branch_id: str) -> str:
    normalized = safe_str(branch_id)
    strategy_mode = BRANCH_TO_STRATEGY_MODE.get(normalized)
    if strategy_mode is None:
        raise ValueError(f"unknown branch_id: {branch_id!r}")
    return strategy_mode


def param_path_for(family_id: str, branch_id: str) -> str:
    key = (safe_str(family_id), safe_str(branch_id))
    path = DOCTRINE_PARAM_PATHS.get(key)
    if path is None:
        raise ValueError(f"unknown doctrine param path for key={key!r}")
    return path


# ============================================================================
# Nested mapping helper
# ============================================================================


def mapping_get(mapping: Mapping[str, Any] | None, *path: str, default: Any = None) -> Any:
    if mapping is None:
        return default
    current: Any = mapping
    for part in path:
        if not isinstance(current, Mapping):
            return default
        if part not in current:
            return default
        current = current[part]
    return current


# ============================================================================
# Validation
# ============================================================================


def _validate_common_surface() -> None:
    _require(
        tuple(FAMILY_ORDER) == tuple(N.ALLOWED_STRATEGY_FAMILY_IDS),
        "FAMILY_ORDER must match names.ALLOWED_STRATEGY_FAMILY_IDS exactly",
    )
    _require(
        set(DOCTRINE_BY_FAMILY.keys()) == set(FAMILY_ORDER),
        "DOCTRINE_BY_FAMILY must cover FAMILY_ORDER exactly",
    )
    _require(
        set(BRANCH_TO_SIDE.keys()) == set(N.ALLOWED_BRANCH_IDS),
        "BRANCH_TO_SIDE must cover allowed branch ids exactly",
    )
    _require(
        set(BRANCH_TO_POSITION_SIDE.keys()) == set(N.ALLOWED_BRANCH_IDS),
        "BRANCH_TO_POSITION_SIDE must cover allowed branch ids exactly",
    )
    _require(
        set(BRANCH_TO_STRATEGY_MODE.keys()) == set(N.ALLOWED_BRANCH_IDS),
        "BRANCH_TO_STRATEGY_MODE must cover allowed branch ids exactly",
    )

    for family_id in FAMILY_ORDER:
        doctrine_id = DOCTRINE_BY_FAMILY[family_id]
        _require(
            doctrine_id in N.ALLOWED_DOCTRINE_IDS,
            f"DOCTRINE_BY_FAMILY contains unsupported doctrine_id: {doctrine_id!r}",
        )

    expected_param_keys = {
        (family_id, branch_id)
        for family_id in FAMILY_ORDER
        for branch_id in N.ALLOWED_BRANCH_IDS
    }
    _require(
        set(DOCTRINE_PARAM_PATHS.keys()) == expected_param_keys,
        "DOCTRINE_PARAM_PATHS must cover every family/branch pair exactly",
    )

    for (family_id, branch_id), path in DOCTRINE_PARAM_PATHS.items():
        _require_non_empty_str(family_id, "family_id")
        _require_non_empty_str(branch_id, "branch_id")
        _require_non_empty_str(path, "param_path")
        _require(
            family_id in FAMILY_ORDER,
            f"DOCTRINE_PARAM_PATHS has unsupported family_id: {family_id!r}",
        )
        _require(
            branch_id in N.ALLOWED_BRANCH_IDS,
            f"DOCTRINE_PARAM_PATHS has unsupported branch_id: {branch_id!r}",
        )
        _require(
            path.endswith(".yaml"),
            f"DOCTRINE_PARAM_PATHS must point to .yaml file: {path!r}",
        )

    _require(
        set(ALLOWED_REENTRY_EXIT_REASONS.keys()) == set(FAMILY_ORDER),
        "ALLOWED_REENTRY_EXIT_REASONS must cover FAMILY_ORDER exactly",
    )
    _require(
        set(FORBIDDEN_REENTRY_EXIT_REASONS.keys()) == set(FAMILY_ORDER),
        "FORBIDDEN_REENTRY_EXIT_REASONS must cover FAMILY_ORDER exactly",
    )
    _require(
        set(DEFAULT_REENTRY_CAPS.keys()) == set(FAMILY_ORDER),
        "DEFAULT_REENTRY_CAPS must cover FAMILY_ORDER exactly",
    )

    for family_id, caps in DEFAULT_REENTRY_CAPS.items():
        _require(
            isinstance(caps, Mapping),
            f"DEFAULT_REENTRY_CAPS[{family_id!r}] must be a mapping",
        )
        _require(
            set(caps.keys()) == set(_ALLOWED_REGIMES),
            f"DEFAULT_REENTRY_CAPS[{family_id!r}] must cover LOWVOL/NORMAL/FAST",
        )
        for regime, count in caps.items():
            _require(
                isinstance(count, int) and count >= 0,
                f"DEFAULT_REENTRY_CAPS[{family_id!r}][{regime!r}] must be int >= 0",
            )

    _require(
        tuple(CLASSIC_FAMILIES)
        == (
            N.STRATEGY_FAMILY_MIST,
            N.STRATEGY_FAMILY_MISB,
            N.STRATEGY_FAMILY_MISC,
            N.STRATEGY_FAMILY_MISR,
        ),
        "CLASSIC_FAMILIES must remain the frozen classic-four set",
    )

    _require(
        family_requires_dhan_signal_path(N.STRATEGY_FAMILY_MISO) is True,
        "MISO must require Dhan signal path",
    )
    for family_id in CLASSIC_FAMILIES:
        _require(
            family_requires_dhan_signal_path(family_id) is False,
            f"{family_id} must not require Dhan mandatory signal path",
        )


_validate_common_surface()

# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "ALLOWED_REENTRY_EXIT_REASONS",
    "BRANCH_TO_POSITION_SIDE",
    "BRANCH_TO_SIDE",
    "BRANCH_TO_STRATEGY_MODE",
    "CLASSIC_FAMILIES",
    "DEFAULT_REENTRY_CAPS",
    "DOCTRINE_BY_FAMILY",
    "DOCTRINE_PARAM_PATHS",
    "FAMILY_ORDER",
    "FORBIDDEN_REENTRY_EXIT_REASONS",
    "LIVE_FAMILY_MODES",
    "StrategyFamilyCommonError",
    "doctrine_for_family",
    "family_is_classic",
    "family_requires_dhan_signal_path",
    "mapping_get",
    "new_id",
    "normalize_reason",
    "normalize_regime",
    "param_path_for",
    "position_side_for_branch",
    "safe_bool",
    "safe_float",
    "safe_int",
    "safe_str",
    "side_for_branch",
    "strategy_mode_for_branch",
]
