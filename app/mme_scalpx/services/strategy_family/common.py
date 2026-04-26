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

import hashlib
import json
import math
from dataclasses import is_dataclass, replace
from types import MappingProxyType
from typing import Any, Final, Mapping

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


# ============================================================================
# Shared fail-closed stage-gate contract
# ============================================================================

GLOBAL_REQUIRED_STAGE_FLAGS: Final[tuple[str, ...]] = (
    "data_valid",
    "data_quality_ok",
    "session_eligible",
    "warmup_complete",
)

GLOBAL_EXPECTED_FALSE_STAGE_FLAGS: Final[tuple[str, ...]] = (
    "risk_veto_active",
    "reconciliation_lock_active",
    "active_position_present",
)

MISO_REQUIRED_STAGE_FLAGS: Final[tuple[str, ...]] = (
    "provider_ready_miso",
    "dhan_context_fresh",
)


def validate_global_stage_gates(
    stage: Mapping[str, Any],
    *,
    required_true: tuple[str, ...] = GLOBAL_REQUIRED_STAGE_FLAGS,
    expected_false: tuple[str, ...] = GLOBAL_EXPECTED_FALSE_STAGE_FLAGS,
) -> tuple[bool, str | None]:
    """Validate shared pre-entry stage gates using fail-closed semantics.

    Freeze-grade law:
    - required true flags must be present and true
    - expected false blocker flags must be present and false
    - missing flags are explicit blockers, never silent defaults
    """
    if not isinstance(stage, Mapping):
        return False, "stage_flags_missing"

    for key in required_true:
        if key not in stage:
            return False, f"stage_{key}_missing"
        if safe_bool(stage.get(key), False) is not True:
            return False, f"stage_{key}_failed"

    for key in expected_false:
        if key not in stage:
            return False, f"stage_{key}_missing"
        if safe_bool(stage.get(key), False) is not False:
            return False, f"stage_{key}_failed"

    return True, None


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


def _plain_value_for_id(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise StrategyFamilyCommonError("stable_id payload contains non-finite float")
        return value
    if isinstance(value, Mapping):
        return {
            str(k): _plain_value_for_id(v)
            for k, v in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_plain_value_for_id(v) for v in value]
    if isinstance(value, set):
        return sorted(_plain_value_for_id(v) for v in value)
    return str(value)


def stable_id(prefix: str, *parts: Any, payload: Mapping[str, Any] | None = None) -> str:
    stem = safe_str(prefix, "id").replace(" ", "_")
    if payload is not None and parts:
        raise StrategyFamilyCommonError("stable_id accepts either parts or payload, not both")
    if payload is None:
        _require(len(parts) > 0, "stable_id requires deterministic parts or payload")
        material_obj: Any = [_plain_value_for_id(part) for part in parts]
    else:
        material_obj = _plain_value_for_id(dict(payload))
    material = json.dumps(
        material_obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]
    return f"{stem}-{digest}"


def new_id(prefix: str, *parts: Any, payload: Mapping[str, Any] | None = None) -> str:
    """
    Backward-compatible deterministic alias.

    Freeze-grade rule:
    - caller must provide deterministic parts or payload
    - zero-argument UUID-style generation is forbidden
    """
    return stable_id(prefix, *parts, payload=payload)


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
# Batch 25P candidate metadata contract
# ============================================================================

CANDIDATE_METADATA_REQUIRED_KEYS: Final[tuple[str, ...]] = (
    "candidate_id",
    "strategy_family",
    "strategy_branch",
    "doctrine_id",
    "action_hint",
    "side",
    "instrument_key",
    "option_symbol",
    "option_token",
    "strike",
    "limit_price_hint",
    "quantity_lots_hint",
    "entry_mode",
    "provider_id",
    "execution_provider_id",
    "risk_gate_required",
    "score",
    "blockers",
    "source_feature_frame_id",
    "source_feature_ts_ns",
)


def _as_plain_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            mapped = value.to_dict()
            if isinstance(mapped, Mapping):
                return dict(mapped)
        except Exception:
            return {}
    return {}


def _view_mapping_for_metadata(view_like: Any) -> dict[str, Any]:
    if isinstance(view_like, Mapping):
        return dict(view_like)
    out: dict[str, Any] = {}
    for key in (
        "frame_id",
        "frame_ts_ns",
        "features_generated_at_ns",
        "provider_runtime",
        "risk",
        "stage_flags",
    ):
        if hasattr(view_like, key):
            out[key] = getattr(view_like, key)
    return out


def _metadata_provider_runtime(view_like: Any) -> dict[str, Any]:
    view = _view_mapping_for_metadata(view_like)
    provider_runtime = view.get("provider_runtime")
    if isinstance(provider_runtime, Mapping):
        return dict(provider_runtime)
    nested_runtime = mapping_get(view, "family_features", "provider_runtime", default={})
    return dict(nested_runtime) if isinstance(nested_runtime, Mapping) else {}


def _metadata_risk(view_like: Any) -> dict[str, Any]:
    view = _view_mapping_for_metadata(view_like)
    risk = view.get("risk")
    return dict(risk) if isinstance(risk, Mapping) else {}


def _metadata_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _metadata_float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    number = safe_float(value, 0.0)
    return number if number > 0.0 else None


def _metadata_int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    number = safe_int(value, 0)
    return number if number > 0 else None


def standardize_candidate_metadata(
    *,
    candidate: Any,
    view_like: Any,
    family_id: str,
    doctrine_id: str,
    result_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Return the frozen Batch 25P candidate metadata shape.

    This function standardizes metadata only. It does not promote candidates,
    publish strategy decisions, call risk, or call execution.
    """

    candidate_data = _as_plain_mapping(candidate)
    existing = _as_plain_mapping(candidate_data.get("metadata"))
    result_meta = dict(result_metadata or {})
    provider_runtime = _metadata_provider_runtime(view_like)
    risk = _metadata_risk(view_like)
    view = _view_mapping_for_metadata(view_like)

    branch_id = safe_str(
        _metadata_value(
            candidate_data.get("branch_id"),
            existing.get("strategy_branch"),
            result_meta.get("branch_id"),
        )
    )
    strategy_family = safe_str(
        _metadata_value(
            candidate_data.get("family_id"),
            existing.get("strategy_family"),
            family_id,
        )
    )
    resolved_doctrine = safe_str(
        _metadata_value(
            candidate_data.get("doctrine_id"),
            existing.get("doctrine_id"),
            doctrine_id,
        )
    )
    action_hint = safe_str(
        _metadata_value(candidate_data.get("action"), existing.get("action_hint"))
    )
    side = safe_str(_metadata_value(candidate_data.get("side"), existing.get("side")))
    instrument_key = safe_str(
        _metadata_value(candidate_data.get("instrument_key"), existing.get("instrument_key"))
    )
    option_symbol = safe_str(
        _metadata_value(candidate_data.get("option_symbol"), existing.get("option_symbol"))
    )
    option_token = safe_str(
        _metadata_value(
            candidate_data.get("instrument_token"),
            candidate_data.get("option_token"),
            existing.get("option_token"),
        )
    )
    strike = _metadata_float_or_none(
        _metadata_value(candidate_data.get("strike"), existing.get("strike"))
    )
    limit_price_hint = _metadata_float_or_none(
        _metadata_value(
            candidate_data.get("option_price"),
            candidate_data.get("limit_price_hint"),
            existing.get("limit_price_hint"),
        )
    )

    quantity_lots_hint = _metadata_int_or_none(
        _metadata_value(
            candidate_data.get("quantity_lots_hint"),
            existing.get("quantity_lots_hint"),
            risk.get("preview_quantity_lots"),
        )
    )
    entry_mode = safe_str(
        _metadata_value(
            candidate_data.get("entry_mode"),
            existing.get("entry_mode"),
            result_meta.get("entry_mode"),
        )
    )
    provider_id = safe_str(
        _metadata_value(
            candidate_data.get("provider_id"),
            existing.get("provider_id"),
            provider_runtime.get("selected_option_marketdata_provider_id"),
            provider_runtime.get("active_selected_option_provider_id"),
        )
    )
    execution_provider_id = safe_str(
        _metadata_value(
            existing.get("execution_provider_id"),
            provider_runtime.get("execution_primary_provider_id"),
            provider_runtime.get("active_execution_provider_id"),
        )
    )

    source_feature_frame_id = safe_str(
        _metadata_value(
            existing.get("source_feature_frame_id"),
            view.get("frame_id"),
            result_meta.get("source_feature_frame_id"),
        )
    )
    source_feature_ts_ns = _metadata_int_or_none(
        _metadata_value(
            existing.get("source_feature_ts_ns"),
            view.get("features_generated_at_ns"),
            view.get("frame_ts_ns"),
            result_meta.get("source_feature_ts_ns"),
        )
    )

    blockers_raw = existing.get("blockers")
    blockers = blockers_raw if isinstance(blockers_raw, list) else []

    score = _metadata_float_or_none(
        _metadata_value(candidate_data.get("score"), existing.get("score"))
    )
    if score is None:
        score = 0.0

    payload_for_id = {
        "strategy_family": strategy_family,
        "strategy_branch": branch_id,
        "doctrine_id": resolved_doctrine,
        "action_hint": action_hint,
        "instrument_key": instrument_key,
        "option_token": option_token,
        "option_symbol": option_symbol,
        "strike": strike,
        "limit_price_hint": limit_price_hint,
        "source_feature_frame_id": source_feature_frame_id,
        "source_feature_ts_ns": source_feature_ts_ns,
    }

    candidate_id = safe_str(existing.get("candidate_id")) or stable_id(
        "candidate",
        payload=payload_for_id,
    )

    metadata = {
        **existing,
        "candidate_id": candidate_id,
        "strategy_family": strategy_family,
        "strategy_branch": branch_id,
        "doctrine_id": resolved_doctrine,
        "action_hint": action_hint,
        "side": side,
        "instrument_key": instrument_key,
        "option_symbol": option_symbol,
        "option_token": option_token,
        "strike": strike,
        "limit_price_hint": limit_price_hint,
        "quantity_lots_hint": quantity_lots_hint,
        "entry_mode": entry_mode,
        "provider_id": provider_id,
        "execution_provider_id": execution_provider_id,
        "risk_gate_required": True,
        "score": score,
        "blockers": blockers,
        "source_feature_frame_id": source_feature_frame_id,
        "source_feature_ts_ns": source_feature_ts_ns,
        "batch25p_candidate_metadata_standardized": True,
        "candidate_metadata_contract_version": "25P.1",
    }

    complete, missing = candidate_metadata_contract_status(metadata)
    metadata["candidate_metadata_contract_complete"] = complete
    metadata["candidate_metadata_missing"] = missing
    return metadata


def standardize_candidate_mapping(
    candidate: Any,
    *,
    view_like: Any,
    family_id: str,
    doctrine_id: str,
    result_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = _as_plain_mapping(candidate)
    metadata = standardize_candidate_metadata(
        candidate=data,
        view_like=view_like,
        family_id=family_id,
        doctrine_id=doctrine_id,
        result_metadata=result_metadata,
    )
    data["metadata"] = metadata
    return data


def standardize_candidate_result(
    result: Any,
    *,
    view_like: Any,
    family_id: str,
    doctrine_id: str,
) -> Any:
    """
    Return a result with standardized candidate metadata when result is a candidate.

    The returned result remains a doctrine evaluation result. This function does
    not convert candidates into orders and does not alter activation mode.
    """

    if not getattr(result, "is_candidate", False):
        return result

    candidate_obj = getattr(result, "candidate", None)
    if candidate_obj is None:
        return result

    result_metadata = _as_plain_mapping(getattr(result, "metadata", None))
    standardized = standardize_candidate_mapping(
        candidate_obj,
        view_like=view_like,
        family_id=family_id,
        doctrine_id=doctrine_id,
        result_metadata=result_metadata,
    )
    metadata = dict(standardized.get("metadata", {}))

    new_candidate: Any = standardized
    if is_dataclass(candidate_obj):
        try:
            new_candidate = replace(candidate_obj, metadata=metadata)
        except Exception:
            new_candidate = standardized

    if is_dataclass(result):
        try:
            new_result_metadata = {
                **result_metadata,
                "batch25p_candidate_metadata_standardized": True,
                "candidate_metadata_contract_complete": metadata.get(
                    "candidate_metadata_contract_complete",
                    False,
                ),
                "candidate_metadata_missing": list(
                    metadata.get("candidate_metadata_missing", [])
                ),
            }
            return replace(result, candidate=new_candidate, metadata=new_result_metadata)
        except Exception:
            return result

    return result


def candidate_metadata_contract_status(
    metadata: Mapping[str, Any],
) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for key in CANDIDATE_METADATA_REQUIRED_KEYS:
        value = metadata.get(key)
        if key == "blockers":
            if not isinstance(value, list):
                missing.append(key)
            continue
        if key == "risk_gate_required":
            if value is not True:
                missing.append(key)
            continue
        if value in (None, ""):
            missing.append(key)
    return (not missing, missing)


def candidate_metadata_contract_ok(metadata: Mapping[str, Any]) -> bool:
    complete, _missing = candidate_metadata_contract_status(metadata)
    return complete


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


# ============================================================================
# Batch 26C runtime-mode canonicalization helpers
# ============================================================================

def _canonical_runtime_constant(name: str, default: str) -> str:
    """Return canonical hyphenated runtime mode text.

    Some historical constants use underscores or may be absent/None. The
    strategy-family runtime contract is hyphenated and fail-closed.
    """
    raw = getattr(N, name, default)
    text = safe_str(raw) or default
    normalized = text.upper().replace("_", "-").replace(" ", "-")
    return normalized or default


CLASSIC_RUNTIME_MODE_NORMAL: Final[str] = _canonical_runtime_constant(
    "STRATEGY_RUNTIME_MODE_NORMAL",
    "NORMAL",
)
CLASSIC_RUNTIME_MODE_DHAN_DEGRADED: Final[str] = _canonical_runtime_constant(
    "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED",
    "DHAN-DEGRADED",
)
CLASSIC_RUNTIME_MODE_DISABLED: Final[str] = _canonical_runtime_constant(
    "STRATEGY_RUNTIME_MODE_DISABLED",
    "DISABLED",
)

MISO_RUNTIME_MODE_BASE_5DEPTH: Final[str] = _canonical_runtime_constant(
    "STRATEGY_RUNTIME_MODE_BASE_5DEPTH",
    "BASE-5DEPTH",
)
MISO_RUNTIME_MODE_DEPTH20_ENHANCED: Final[str] = _canonical_runtime_constant(
    "STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED",
    "DEPTH20-ENHANCED",
)
MISO_RUNTIME_MODE_DISABLED: Final[str] = _canonical_runtime_constant(
    "STRATEGY_RUNTIME_MODE_DISABLED",
    "DISABLED",
)


def _runtime_token(value: Any) -> str:
    return safe_str(value).upper().replace("_", "-").replace(" ", "-")


def normalize_classic_runtime_mode(value: Any) -> str:
    """Normalize classic-family runtime mode with fail-closed missing handling."""
    token = _runtime_token(value)
    if not token:
        return CLASSIC_RUNTIME_MODE_DISABLED

    aliases = {
        "NORMAL": CLASSIC_RUNTIME_MODE_NORMAL,
        "LIVE": CLASSIC_RUNTIME_MODE_NORMAL,
        "DHAN-DEGRADED": CLASSIC_RUNTIME_MODE_DHAN_DEGRADED,
        "DHAN-DEGRADED-SAFE": CLASSIC_RUNTIME_MODE_DHAN_DEGRADED,
        "DEGRADED": CLASSIC_RUNTIME_MODE_DHAN_DEGRADED,
        "DISABLED": CLASSIC_RUNTIME_MODE_DISABLED,
        "OFF": CLASSIC_RUNTIME_MODE_DISABLED,
    }
    return aliases.get(token, CLASSIC_RUNTIME_MODE_DISABLED)


def normalize_miso_runtime_mode(value: Any) -> str:
    """Normalize MISO runtime mode with fail-closed missing handling."""
    token = _runtime_token(value)
    if not token:
        return MISO_RUNTIME_MODE_DISABLED

    aliases = {
        "BASE-5DEPTH": MISO_RUNTIME_MODE_BASE_5DEPTH,
        "BASE5DEPTH": MISO_RUNTIME_MODE_BASE_5DEPTH,
        "BASE": MISO_RUNTIME_MODE_BASE_5DEPTH,
        "DEPTH20-ENHANCED": MISO_RUNTIME_MODE_DEPTH20_ENHANCED,
        "DEPTH20": MISO_RUNTIME_MODE_DEPTH20_ENHANCED,
        "ENHANCED": MISO_RUNTIME_MODE_DEPTH20_ENHANCED,
        "DISABLED": MISO_RUNTIME_MODE_DISABLED,
        "OFF": MISO_RUNTIME_MODE_DISABLED,
    }
    return aliases.get(token, MISO_RUNTIME_MODE_DISABLED)


def resolve_classic_runtime_mode(
    common_surface: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
) -> str:
    """Resolve classic runtime mode from canonical surfaces, fail-closed."""
    raw = (
        mapping_get(common_surface, "strategy_runtime_mode_classic")
        or mapping_get(common_surface, "classic_runtime_mode")
        or mapping_get(provider_runtime, "classic_runtime_mode")
        or mapping_get(provider_runtime, "strategy_runtime_mode_classic")
    )
    return normalize_classic_runtime_mode(raw)


def resolve_miso_runtime_mode(
    common_surface: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
    family_status: Mapping[str, Any] | None = None,
) -> str:
    """Resolve MISO runtime mode from canonical surfaces, fail-closed."""
    status = family_status if isinstance(family_status, Mapping) else {}
    raw = (
        mapping_get(status, "mode")
        or mapping_get(common_surface, "strategy_runtime_mode_miso")
        or mapping_get(common_surface, "miso_runtime_mode")
        or mapping_get(provider_runtime, "miso_runtime_mode")
        or mapping_get(provider_runtime, "strategy_runtime_mode_miso")
    )
    return normalize_miso_runtime_mode(raw)


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
    "CANDIDATE_METADATA_REQUIRED_KEYS",
    "standardize_candidate_metadata",
    "standardize_candidate_mapping",
    "standardize_candidate_result",
    "candidate_metadata_contract_status",
    "candidate_metadata_contract_ok",
    "StrategyFamilyCommonError",
    "doctrine_for_family",
    "family_is_classic",
    "family_requires_dhan_signal_path",
    "mapping_get",
    "new_id",
    "stable_id",
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
    "CLASSIC_RUNTIME_MODE_NORMAL",
    "CLASSIC_RUNTIME_MODE_DHAN_DEGRADED",
    "CLASSIC_RUNTIME_MODE_DISABLED",
    "MISO_RUNTIME_MODE_BASE_5DEPTH",
    "MISO_RUNTIME_MODE_DEPTH20_ENHANCED",
    "MISO_RUNTIME_MODE_DISABLED",
    "normalize_classic_runtime_mode",
    "normalize_miso_runtime_mode",
    "resolve_classic_runtime_mode",
    "resolve_miso_runtime_mode",
]
