from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/common.py

Pure deterministic helper builders for ScalpX MME feature-family publication.

Purpose
-------
This module OWNS:
- pure helper builders for frozen family_features subtrees
- exact-key merge/update helpers for contract-safe subtree construction
- deterministic payload assembly helpers that validate against
  feature_family.contracts
- small normalization/coercion helpers used by services/features.py while
  constructing family-facing payloads

This module DOES NOT own:
- Redis reads or writes
- service loops
- runtime polling / heartbeats / health publication
- provider selection or failover policy
- strategy doctrine logic
- cooldown / proof-window / entry / exit decisions
- deep formula ownership
- publication side effects

Design law
----------
- services/features.py remains the sole live publisher of family_features
- this module helps features.py build contract-safe payloads
- classic MIS families remain branch-shaped
- MISO remains option-led and side-support-shaped
- builders here must remain deterministic and side-effect free
- any object built here must be validated against contracts.py before return
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.feature_family import contracts as C

EPSILON: Final[float] = 1e-8

OPTION_SIDE_CALL: Final[str] = N.SIDE_CALL
OPTION_SIDE_PUT: Final[str] = N.SIDE_PUT
OPTION_SIDE_IDS: Final[tuple[str, ...]] = (
    OPTION_SIDE_CALL,
    OPTION_SIDE_PUT,
)


# ============================================================================
# Exceptions
# ============================================================================


class FeatureFamilyCommonError(ValueError):
    """Raised when helper construction inputs are invalid."""


# ============================================================================
# Small internal helpers
# ============================================================================


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FeatureFamilyCommonError(message)


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{field_name} must be mapping")
    return value


def _non_empty_str(value: Any, *, field_name: str) -> str:
    _require(isinstance(value, str), f"{field_name} must be str")
    text = value.strip()
    _require(bool(text), f"{field_name} must be non-empty")
    return text


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = _safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    try:
        text = _safe_str(value)
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    try:
        text = _safe_str(value)
        if not text:
            return default
        out = float(text)
    except Exception:
        return default
    if not isfinite(out):
        return default
    return out


def _clean_optional_str(value: Any) -> str | None:
    text = _safe_str(value)
    return text or None


def _normalize_side(side: Any, *, field_name: str = "side") -> str:
    normalized = _safe_str(side).upper()
    _require(
        normalized in OPTION_SIDE_IDS,
        f"{field_name} must be one of {OPTION_SIDE_IDS!r}",
    )
    return normalized


def _normalize_branch(branch_id: Any, *, field_name: str = "branch_id") -> str:
    normalized = _safe_str(branch_id).upper()
    _require(
        normalized in C.BRANCH_IDS,
        f"{field_name} must be one of {C.BRANCH_IDS!r}",
    )
    return normalized


def _normalize_family_id(family_id: Any) -> str:
    normalized = _safe_str(family_id).upper()
    _require(
        normalized in C.FAMILY_IDS,
        f"family_id must be one of {C.FAMILY_IDS!r}",
    )
    return normalized


def _normalize_provider_id(
    provider_id: Any,
    *,
    field_name: str,
    allow_none: bool = True,
) -> str | None:
    if provider_id is None and allow_none:
        return None
    text = _safe_str(provider_id)
    if not text and allow_none:
        return None
    _require(
        text in C.ALLOWED_PROVIDER_IDS,
        f"{field_name} must be one of {C.ALLOWED_PROVIDER_IDS!r}",
    )
    return text


def _normalize_provider_status(
    status: Any,
    *,
    field_name: str,
    default: str = N.PROVIDER_STATUS_UNAVAILABLE,
) -> str:
    text = _safe_str(status, default=default)
    _require(
        text in C.ALLOWED_PROVIDER_STATUSES,
        f"{field_name} must be one of {C.ALLOWED_PROVIDER_STATUSES!r}",
    )
    return text


def _normalize_family_runtime_mode(
    value: Any,
    *,
    field_name: str = "family_runtime_mode",
    default: str = N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
) -> str:
    text = _safe_str(value, default=default)
    _require(
        text in C.ALLOWED_FAMILY_RUNTIME_MODES,
        f"{field_name} must be one of {C.ALLOWED_FAMILY_RUNTIME_MODES!r}",
    )
    return text


def _normalize_strategy_runtime_mode(
    value: Any,
    *,
    family_id: str | None,
    field_name: str = "strategy_runtime_mode",
    default: str = N.STRATEGY_RUNTIME_MODE_DISABLED,
) -> str:
    text = _safe_str(value, default=default)
    _require(
        text in C.ALLOWED_STRATEGY_RUNTIME_MODES,
        f"{field_name} must be one of {C.ALLOWED_STRATEGY_RUNTIME_MODES!r}",
    )
    if family_id is None:
        return text
    if family_id == C.FAMILY_ID_MISO:
        _require(
            text in C.MISO_ALLOWED_STRATEGY_RUNTIME_MODES,
            f"{field_name}={text!r} invalid for MISO",
        )
        return text
    _require(
        text in C.CLASSIC_ALLOWED_STRATEGY_RUNTIME_MODES,
        f"{field_name}={text!r} invalid for classic family",
    )
    return text


def _safe_ratio(numer: float, denom: float, default: float = 0.0) -> float:
    if abs(denom) <= EPSILON:
        return default
    return numer / denom


def _rounded(value: float, ndigits: int = 6) -> float:
    return round(float(value), ndigits)


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return _safe_float(value)


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return _safe_int(value)


def _copy_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    return dict(_require_mapping(value, field_name="mapping"))


def _deep_merge_exact(base: Mapping[str, Any], update: Mapping[str, Any]) -> dict[str, Any]:
    base_map = dict(_require_mapping(base, field_name="base"))
    update_map = dict(_require_mapping(update, field_name="update"))

    out: dict[str, Any] = dict(base_map)
    for key, value in update_map.items():
        if isinstance(value, Mapping) and isinstance(out.get(key), Mapping):
            out[key] = _deep_merge_exact(
                _require_mapping(out[key], field_name=f"base[{key!r}]"),
                _require_mapping(value, field_name=f"update[{key!r}]"),
            )
        else:
            out[key] = value
    return out


def _ensure_keys(value: Mapping[str, Any], *, required_keys: tuple[str, ...], field_name: str) -> dict[str, Any]:
    mapping = dict(_require_mapping(value, field_name=field_name))
    missing = [key for key in required_keys if key not in mapping]
    _require(not missing, f"{field_name} missing keys: {', '.join(missing)}")
    return mapping


def _dict_without_nones(mapping: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in mapping.items():
        if value is None:
            continue
        if isinstance(value, Mapping):
            out[key] = _dict_without_nones(value)
        else:
            out[key] = value
    return out


def _regime_or_default(value: Any, default: str = C.REGIME_NORMAL) -> str:
    text = _safe_str(value, default=default).upper()
    _require(text in C.ALLOWED_REGIMES, f"regime must be one of {C.ALLOWED_REGIMES!r}")
    return text


# ============================================================================
# Shared derivation helpers
# ============================================================================


def derive_provider_ready_classic(
    *,
    active_futures_provider_id: Any,
    active_selected_option_provider_id: Any,
    strategy_runtime_mode: Any,
) -> bool:
    fut_provider = _normalize_provider_id(
        active_futures_provider_id,
        field_name="active_futures_provider_id",
        allow_none=True,
    )
    opt_provider = _normalize_provider_id(
        active_selected_option_provider_id,
        field_name="active_selected_option_provider_id",
        allow_none=True,
    )
    runtime_mode = _safe_str(strategy_runtime_mode)
    return bool(
        fut_provider is not None
        and opt_provider is not None
        and runtime_mode
        and runtime_mode != N.STRATEGY_RUNTIME_MODE_DISABLED
    )


def derive_provider_ready_miso(
    *,
    active_futures_provider_id: Any,
    active_selected_option_provider_id: Any,
    active_option_context_provider_id: Any,
    strategy_runtime_mode: Any,
) -> bool:
    fut_provider = _normalize_provider_id(
        active_futures_provider_id,
        field_name="active_futures_provider_id",
        allow_none=True,
    )
    opt_provider = _normalize_provider_id(
        active_selected_option_provider_id,
        field_name="active_selected_option_provider_id",
        allow_none=True,
    )
    ctx_provider = _normalize_provider_id(
        active_option_context_provider_id,
        field_name="active_option_context_provider_id",
        allow_none=True,
    )
    runtime_mode = _safe_str(strategy_runtime_mode)
    return bool(
        fut_provider == N.PROVIDER_DHAN
        and opt_provider == N.PROVIDER_DHAN
        and ctx_provider == N.PROVIDER_DHAN
        and runtime_mode
        and runtime_mode != N.STRATEGY_RUNTIME_MODE_DISABLED
    )


def derive_selected_option_present(
    *,
    call_present: bool,
    put_present: bool,
) -> bool:
    return bool(call_present or put_present)


def derive_common_premium_floor_ok(
    premium: Any,
    *,
    premium_floor: float,
) -> bool:
    return _safe_float(premium, 0.0) >= max(_safe_float(premium_floor, 0.0), 0.0)


def derive_depth_ok(
    depth_total: Any,
    *,
    depth_min: int,
) -> bool:
    return _safe_int(depth_total, 0) >= max(_safe_int(depth_min, 0), 0)


def derive_spread_ratio_ok(
    spread_ratio: Any,
    *,
    spread_ratio_max: float,
) -> bool:
    ratio = _safe_float(spread_ratio, float("inf"))
    maximum = max(_safe_float(spread_ratio_max, 0.0), 0.0)
    return isfinite(ratio) and ratio <= maximum


def derive_response_efficiency_ok(
    response_efficiency: Any,
    *,
    response_efficiency_min: float,
) -> bool:
    return _safe_float(response_efficiency, 0.0) >= _safe_float(
        response_efficiency_min,
        0.0,
    )


def derive_tradability_ok(
    *,
    premium_floor_ok: bool,
    depth_ok: bool,
    spread_ratio_ok: bool,
    response_efficiency_ok: bool,
) -> bool:
    return bool(
        premium_floor_ok
        and depth_ok
        and spread_ratio_ok
        and response_efficiency_ok
    )


def derive_selected_option_tradability_ok(
    *,
    premium: Any,
    premium_floor: float,
    depth_total: Any,
    depth_min: int,
    spread_ratio: Any,
    spread_ratio_max: float,
    response_efficiency: Any,
    response_efficiency_min: float,
) -> bool:
    return derive_tradability_ok(
        premium_floor_ok=derive_common_premium_floor_ok(
            premium,
            premium_floor=premium_floor,
        ),
        depth_ok=derive_depth_ok(depth_total, depth_min=depth_min),
        spread_ratio_ok=derive_spread_ratio_ok(
            spread_ratio,
            spread_ratio_max=spread_ratio_max,
        ),
        response_efficiency_ok=derive_response_efficiency_ok(
            response_efficiency,
            response_efficiency_min=response_efficiency_min,
        ),
    )


def derive_stage_flags(
    *,
    snapshot_valid: bool,
    session_eligible: bool,
    warmup_complete: bool,
    risk_veto_active: bool,
    reconciliation_lock_active: bool,
    active_position_present: bool,
    provider_ready_classic: bool,
    provider_ready_miso: bool,
    dhan_context_fresh: bool,
    futures_present: bool,
    call_present: bool,
    put_present: bool,
    selected_option_present: bool,
    data_quality_ok: bool | None = None,
) -> dict[str, Any]:
    return build_stage_flags_block(
        data_valid=snapshot_valid,
        data_quality_ok=snapshot_valid if data_quality_ok is None else data_quality_ok,
        session_eligible=session_eligible,
        warmup_complete=warmup_complete,
        risk_veto_active=risk_veto_active,
        reconciliation_lock_active=reconciliation_lock_active,
        active_position_present=active_position_present,
        provider_ready_classic=provider_ready_classic,
        provider_ready_miso=provider_ready_miso,
        dhan_context_fresh=dhan_context_fresh,
        selected_option_present=selected_option_present,
        futures_present=futures_present,
        call_present=call_present,
        put_present=put_present,
    )


# ============================================================================
# Shared top-level block builders
# ============================================================================


def build_snapshot_block(
    *,
    snapshot_valid: bool,
    snapshot_sync_ok: bool,
    snapshot_validity: str,
    snapshot_reason: str | None = None,
    ts_frame_ns: int | None = None,
    ts_span_ms: int | None = None,
    frame_id: str | None = None,
    selection_version: str | None = None,
    stale_mask: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    return {
        "snapshot_valid": bool(snapshot_valid),
        "snapshot_sync_ok": bool(snapshot_sync_ok),
        "snapshot_validity": _safe_str(snapshot_validity),
        "snapshot_reason": _clean_optional_str(snapshot_reason),
        "ts_frame_ns": _optional_int(ts_frame_ns),
        "ts_span_ms": _optional_int(ts_span_ms),
        "frame_id": _clean_optional_str(frame_id),
        "selection_version": _clean_optional_str(selection_version),
        "stale_mask": tuple(str(item) for item in (stale_mask or ())),
    }


def build_provider_runtime_block(
    *,
    active_futures_provider_id: Any,
    active_selected_option_provider_id: Any,
    active_option_context_provider_id: Any,
    execution_primary_provider_id: Any | None = None,
    execution_fallback_provider_id: Any | None = None,
    family_runtime_mode: Any = N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
    classic_runtime_mode: Any = N.STRATEGY_RUNTIME_MODE_DISABLED,
    miso_runtime_mode: Any = N.STRATEGY_RUNTIME_MODE_DISABLED,
    futures_provider_status: Any = N.PROVIDER_STATUS_UNAVAILABLE,
    selected_option_provider_status: Any = N.PROVIDER_STATUS_UNAVAILABLE,
    option_context_provider_status: Any = N.PROVIDER_STATUS_UNAVAILABLE,
    provider_ready_classic: bool | None = None,
    provider_ready_miso: bool | None = None,
) -> dict[str, Any]:
    active_fut = _normalize_provider_id(
        active_futures_provider_id,
        field_name="active_futures_provider_id",
        allow_none=True,
    )
    active_opt = _normalize_provider_id(
        active_selected_option_provider_id,
        field_name="active_selected_option_provider_id",
        allow_none=True,
    )
    active_ctx = _normalize_provider_id(
        active_option_context_provider_id,
        field_name="active_option_context_provider_id",
        allow_none=True,
    )
    family_mode = _normalize_family_runtime_mode(family_runtime_mode)
    classic_mode = _normalize_strategy_runtime_mode(
        classic_runtime_mode,
        family_id=C.FAMILY_ID_MIST,
    )
    miso_mode = _normalize_strategy_runtime_mode(
        miso_runtime_mode,
        family_id=C.FAMILY_ID_MISO,
    )
    resolved_ready_classic = (
        derive_provider_ready_classic(
            active_futures_provider_id=active_fut,
            active_selected_option_provider_id=active_opt,
            strategy_runtime_mode=classic_mode,
        )
        if provider_ready_classic is None
        else bool(provider_ready_classic)
    )
    resolved_ready_miso = (
        derive_provider_ready_miso(
            active_futures_provider_id=active_fut,
            active_selected_option_provider_id=active_opt,
            active_option_context_provider_id=active_ctx,
            strategy_runtime_mode=miso_mode,
        )
        if provider_ready_miso is None
        else bool(provider_ready_miso)
    )
    return {
        "active_futures_provider_id": active_fut,
        "active_selected_option_provider_id": active_opt,
        "active_option_context_provider_id": active_ctx,
        "execution_primary_provider_id": _normalize_provider_id(
            execution_primary_provider_id,
            field_name="execution_primary_provider_id",
            allow_none=True,
        ),
        "execution_fallback_provider_id": _normalize_provider_id(
            execution_fallback_provider_id,
            field_name="execution_fallback_provider_id",
            allow_none=True,
        ),
        "futures_provider_status": _normalize_provider_status(
            futures_provider_status,
            field_name="futures_provider_status",
        ),
        "selected_option_provider_status": _normalize_provider_status(
            selected_option_provider_status,
            field_name="selected_option_provider_status",
        ),
        "option_context_provider_status": _normalize_provider_status(
            option_context_provider_status,
            field_name="option_context_provider_status",
        ),
        "family_runtime_mode": family_mode,
        "classic_runtime_mode": classic_mode,
        "miso_runtime_mode": miso_mode,
        "provider_ready_classic": resolved_ready_classic,
        "provider_ready_miso": resolved_ready_miso,
    }


def build_market_block(
    *,
    instrument_key: str | None = None,
    instrument_token: str | None = None,
    option_symbol: str | None = None,
    ltp: Any = None,
    best_bid: Any = None,
    best_ask: Any = None,
    bid_qty_5: Any = None,
    ask_qty_5: Any = None,
    spread: Any = None,
    spread_ratio: Any = None,
    spread_ticks: Any = None,
    depth_total: Any = None,
    response_efficiency: Any = None,
    impact_fraction: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    delta_3: Any = None,
    nof_slope: Any = None,
    age_ms: Any = None,
    tick_size: Any = None,
    lot_size: Any = None,
    premium_floor_ok: bool | None = None,
    depth_ok: bool | None = None,
    spread_ratio_ok: bool | None = None,
    response_efficiency_ok: bool | None = None,
    tradability_ok: bool | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    market = {
        "instrument_key": _clean_optional_str(instrument_key),
        "instrument_token": _clean_optional_str(instrument_token),
        "option_symbol": _clean_optional_str(option_symbol),
        "ltp": _optional_float(ltp),
        "best_bid": _optional_float(best_bid),
        "best_ask": _optional_float(best_ask),
        "bid_qty_5": _optional_int(bid_qty_5),
        "ask_qty_5": _optional_int(ask_qty_5),
        "spread": _optional_float(spread),
        "spread_ratio": _optional_float(spread_ratio),
        "spread_ticks": _optional_float(spread_ticks),
        "depth_total": _optional_int(depth_total),
        "response_efficiency": _optional_float(response_efficiency),
        "impact_fraction": _optional_float(impact_fraction),
        "velocity_ratio": _optional_float(velocity_ratio),
        "weighted_ofi_persist": _optional_float(weighted_ofi_persist),
        "delta_3": _optional_float(delta_3),
        "nof_slope": _optional_float(nof_slope),
        "age_ms": _optional_int(age_ms),
        "tick_size": _optional_float(tick_size),
        "lot_size": _optional_int(lot_size),
        "premium_floor_ok": None if premium_floor_ok is None else bool(premium_floor_ok),
        "depth_ok": None if depth_ok is None else bool(depth_ok),
        "spread_ratio_ok": None if spread_ratio_ok is None else bool(spread_ratio_ok),
        "response_efficiency_ok": None if response_efficiency_ok is None else bool(response_efficiency_ok),
        "tradability_ok": None if tradability_ok is None else bool(tradability_ok),
        "metadata": _copy_mapping(metadata),
    }
    return market


def build_common_futures_block(
    *,
    instrument_key: str | None = None,
    instrument_token: str | None = None,
    ltp: Any = None,
    best_bid: Any = None,
    best_ask: Any = None,
    bid_qty_5: Any = None,
    ask_qty_5: Any = None,
    spread: Any = None,
    spread_ratio: Any = None,
    depth_total: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    delta_3: Any = None,
    nof_slope: Any = None,
    vwap_distance: Any = None,
    vwap_distance_ratio: Any = None,
    trend_score: Any = None,
    age_ms: Any = None,
    provider_id: str | None = None,
) -> dict[str, Any]:
    return {
        **build_market_block(
            instrument_key=instrument_key,
            instrument_token=instrument_token,
            ltp=ltp,
            best_bid=best_bid,
            best_ask=best_ask,
            bid_qty_5=bid_qty_5,
            ask_qty_5=ask_qty_5,
            spread=spread,
            spread_ratio=spread_ratio,
            depth_total=depth_total,
            velocity_ratio=velocity_ratio,
            weighted_ofi_persist=weighted_ofi_persist,
            delta_3=delta_3,
            nof_slope=nof_slope,
            age_ms=age_ms,
        ),
        "provider_id": _normalize_provider_id(
            provider_id,
            field_name="provider_id",
            allow_none=True,
        ),
        "vwap_distance": _optional_float(vwap_distance),
        "vwap_distance_ratio": _optional_float(vwap_distance_ratio),
        "trend_score": _optional_float(trend_score),
    }


def build_common_option_block(
    *,
    side: str,
    instrument_key: str | None = None,
    instrument_token: str | None = None,
    option_symbol: str | None = None,
    strike: Any = None,
    entry_mode: str | None = None,
    ltp: Any = None,
    best_bid: Any = None,
    best_ask: Any = None,
    bid_qty_5: Any = None,
    ask_qty_5: Any = None,
    spread: Any = None,
    spread_ratio: Any = None,
    spread_ticks: Any = None,
    depth_total: Any = None,
    response_efficiency: Any = None,
    impact_fraction: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    delta_3: Any = None,
    nof_slope: Any = None,
    premium_floor_ok: bool | None = None,
    depth_ok: bool | None = None,
    spread_ratio_ok: bool | None = None,
    response_efficiency_ok: bool | None = None,
    tradability_ok: bool | None = None,
    context_score: Any = None,
    context_iv: Any = None,
    context_iv_change_1m_pct: Any = None,
    context_oi: Any = None,
    context_oi_change: Any = None,
    volume: Any = None,
    delta_proxy: Any = None,
    authoritative_delta: Any = None,
    gamma: Any = None,
    theta: Any = None,
    vega: Any = None,
    provider_id: str | None = None,
    age_ms: Any = None,
    ask_reloaded: bool | None = None,
    bid_reloaded: bool | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_side = _normalize_side(side, field_name="side")
    block = {
        **build_market_block(
            instrument_key=instrument_key,
            instrument_token=instrument_token,
            option_symbol=option_symbol,
            ltp=ltp,
            best_bid=best_bid,
            best_ask=best_ask,
            bid_qty_5=bid_qty_5,
            ask_qty_5=ask_qty_5,
            spread=spread,
            spread_ratio=spread_ratio,
            spread_ticks=spread_ticks,
            depth_total=depth_total,
            response_efficiency=response_efficiency,
            impact_fraction=impact_fraction,
            velocity_ratio=velocity_ratio,
            weighted_ofi_persist=weighted_ofi_persist,
            delta_3=delta_3,
            nof_slope=nof_slope,
            age_ms=age_ms,
            premium_floor_ok=premium_floor_ok,
            depth_ok=depth_ok,
            spread_ratio_ok=spread_ratio_ok,
            response_efficiency_ok=response_efficiency_ok,
            tradability_ok=tradability_ok,
            metadata=metadata,
        ),
        "side": normalized_side,
        "strike": _optional_float(strike),
        "entry_mode": (
            None if entry_mode in (None, "") else _safe_str(entry_mode)
        ),
        "provider_id": _normalize_provider_id(
            provider_id,
            field_name="provider_id",
            allow_none=True,
        ),
        "context_score": _optional_float(context_score),
        "context_iv": _optional_float(context_iv),
        "context_iv_change_1m_pct": _optional_float(context_iv_change_1m_pct),
        "context_oi": _optional_int(context_oi),
        "context_oi_change": _optional_int(context_oi_change),
        "volume": _optional_int(volume),
        "delta_proxy": _optional_float(delta_proxy),
        "authoritative_delta": _optional_float(authoritative_delta),
        "gamma": _optional_float(gamma),
        "theta": _optional_float(theta),
        "vega": _optional_float(vega),
        "ask_reloaded": None if ask_reloaded is None else bool(ask_reloaded),
        "bid_reloaded": None if bid_reloaded is None else bool(bid_reloaded),
    }
    return block


def build_selected_option_block(
    *,
    side: str,
    instrument_key: str | None = None,
    instrument_token: str | None = None,
    option_symbol: str | None = None,
    strike: Any = None,
    entry_mode: str | None = None,
    ltp: Any = None,
    best_bid: Any = None,
    best_ask: Any = None,
    bid_qty_5: Any = None,
    ask_qty_5: Any = None,
    spread: Any = None,
    spread_ratio: Any = None,
    spread_ticks: Any = None,
    depth_total: Any = None,
    response_efficiency: Any = None,
    impact_fraction: Any = None,
    velocity_ratio: Any = None,
    weighted_ofi_persist: Any = None,
    delta_3: Any = None,
    nof_slope: Any = None,
    premium_floor_ok: bool | None = None,
    depth_ok: bool | None = None,
    spread_ratio_ok: bool | None = None,
    response_efficiency_ok: bool | None = None,
    tradability_ok: bool | None = None,
    context_score: Any = None,
    context_iv: Any = None,
    context_iv_change_1m_pct: Any = None,
    context_oi: Any = None,
    context_oi_change: Any = None,
    volume: Any = None,
    delta_proxy: Any = None,
    authoritative_delta: Any = None,
    gamma: Any = None,
    theta: Any = None,
    vega: Any = None,
    provider_id: str | None = None,
    age_ms: Any = None,
    ask_reloaded: bool | None = None,
    bid_reloaded: bool | None = None,
    selected_option_present: bool = True,
    selected_option_tradability_ok: bool | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        **build_common_option_block(
            side=side,
            instrument_key=instrument_key,
            instrument_token=instrument_token,
            option_symbol=option_symbol,
            strike=strike,
            entry_mode=entry_mode,
            ltp=ltp,
            best_bid=best_bid,
            best_ask=best_ask,
            bid_qty_5=bid_qty_5,
            ask_qty_5=ask_qty_5,
            spread=spread,
            spread_ratio=spread_ratio,
            spread_ticks=spread_ticks,
            depth_total=depth_total,
            response_efficiency=response_efficiency,
            impact_fraction=impact_fraction,
            velocity_ratio=velocity_ratio,
            weighted_ofi_persist=weighted_ofi_persist,
            delta_3=delta_3,
            nof_slope=nof_slope,
            premium_floor_ok=premium_floor_ok,
            depth_ok=depth_ok,
            spread_ratio_ok=spread_ratio_ok,
            response_efficiency_ok=response_efficiency_ok,
            tradability_ok=tradability_ok,
            context_score=context_score,
            context_iv=context_iv,
            context_iv_change_1m_pct=context_iv_change_1m_pct,
            context_oi=context_oi,
            context_oi_change=context_oi_change,
            volume=volume,
            delta_proxy=delta_proxy,
            authoritative_delta=authoritative_delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            provider_id=provider_id,
            age_ms=age_ms,
            ask_reloaded=ask_reloaded,
            bid_reloaded=bid_reloaded,
            metadata=metadata,
        ),
        "selected_option_present": bool(selected_option_present),
        "selected_option_tradability_ok": (
            None
            if selected_option_tradability_ok is None
            else bool(selected_option_tradability_ok)
        ),
    }


def build_cross_option_block(
    *,
    call_features: Mapping[str, Any],
    put_features: Mapping[str, Any],
    selected_option_present: bool,
    nearest_call_oi_resistance_strike: Any = None,
    nearest_put_oi_support_strike: Any = None,
    call_wall_distance_pts: Any = None,
    put_wall_distance_pts: Any = None,
    call_wall_strength_score: Any = None,
    put_wall_strength_score: Any = None,
    oi_bias: Any = None,
) -> dict[str, Any]:
    call_map = dict(_require_mapping(call_features, field_name="call_features"))
    put_map = dict(_require_mapping(put_features, field_name="put_features"))
    return {
        "call": call_map,
        "put": put_map,
        "selected_option_present": bool(selected_option_present),
        "call_present": bool(call_map.get("selected_option_present", False) or call_map.get("instrument_key")),
        "put_present": bool(put_map.get("selected_option_present", False) or put_map.get("instrument_key")),
        "nearest_call_oi_resistance_strike": _optional_float(nearest_call_oi_resistance_strike),
        "nearest_put_oi_support_strike": _optional_float(nearest_put_oi_support_strike),
        "call_wall_distance_pts": _optional_float(call_wall_distance_pts),
        "put_wall_distance_pts": _optional_float(put_wall_distance_pts),
        "call_wall_strength_score": _optional_float(call_wall_strength_score),
        "put_wall_strength_score": _optional_float(put_wall_strength_score),
        "oi_bias": _optional_float(oi_bias),
    }


def build_economics_block(
    *,
    economics_valid: bool,
    expected_total_cost_rupees: Any = None,
    expected_slippage_rupees: Any = None,
    spread_rupees: Any = None,
    spread_bps: Any = None,
    blocker_code: str | None = None,
    blocker_message: str | None = None,
) -> dict[str, Any]:
    return {
        "economics_valid": bool(economics_valid),
        "expected_total_cost_rupees": _optional_float(expected_total_cost_rupees),
        "expected_slippage_rupees": _optional_float(expected_slippage_rupees),
        "spread_rupees": _optional_float(spread_rupees),
        "spread_bps": _optional_float(spread_bps),
        "blocker_code": _clean_optional_str(blocker_code),
        "blocker_message": _clean_optional_str(blocker_message),
    }


def build_signals_block(
    *,
    futures_bias: Any = None,
    futures_impulse: Any = None,
    options_confirmation: bool = False,
    options_side: str | None = None,
    liquidity_ok: bool = True,
    alignment_ok: bool = True,
) -> dict[str, Any]:
    return {
        "futures_bias": _optional_float(futures_bias),
        "futures_impulse": _optional_float(futures_impulse),
        "options_confirmation": bool(options_confirmation),
        "options_side": None if options_side in (None, "") else _normalize_side(options_side, field_name="options_side"),
        "liquidity_ok": bool(liquidity_ok),
        "alignment_ok": bool(alignment_ok),
    }


def build_common_block(
    *,
    snapshot: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
    futures_features: Mapping[str, Any],
    selected_call: Mapping[str, Any],
    selected_put: Mapping[str, Any],
    cross_option: Mapping[str, Any],
    economics: Mapping[str, Any],
    signals: Mapping[str, Any],
    regime: str,
    regime_reason: str | None = None,
    family_runtime_mode: Any = N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
    classic_runtime_mode: Any = N.STRATEGY_RUNTIME_MODE_DISABLED,
    miso_runtime_mode: Any = N.STRATEGY_RUNTIME_MODE_DISABLED,
) -> dict[str, Any]:
    return {
        "snapshot": dict(_require_mapping(snapshot, field_name="snapshot")),
        "provider_runtime": dict(
            _require_mapping(provider_runtime, field_name="provider_runtime")
        ),
        "futures_features": dict(
            _require_mapping(futures_features, field_name="futures_features")
        ),
        "selected_call": dict(
            _require_mapping(selected_call, field_name="selected_call")
        ),
        "selected_put": dict(
            _require_mapping(selected_put, field_name="selected_put")
        ),
        "cross_option": dict(
            _require_mapping(cross_option, field_name="cross_option")
        ),
        "economics": dict(_require_mapping(economics, field_name="economics")),
        "signals": dict(_require_mapping(signals, field_name="signals")),
        "regime": _regime_or_default(regime),
        "regime_reason": _clean_optional_str(regime_reason),
        "family_runtime_mode": _normalize_family_runtime_mode(family_runtime_mode),
        "classic_runtime_mode": _normalize_strategy_runtime_mode(
            classic_runtime_mode,
            family_id=C.FAMILY_ID_MIST,
        ),
        "miso_runtime_mode": _normalize_strategy_runtime_mode(
            miso_runtime_mode,
            family_id=C.FAMILY_ID_MISO,
        ),
    }


def build_stage_flags_block(
    *,
    data_valid: bool,
    data_quality_ok: bool,
    session_eligible: bool,
    warmup_complete: bool,
    risk_veto_active: bool,
    reconciliation_lock_active: bool,
    active_position_present: bool,
    provider_ready_classic: bool,
    provider_ready_miso: bool,
    dhan_context_fresh: bool,
    selected_option_present: bool,
    futures_present: bool,
    call_present: bool,
    put_present: bool,
) -> dict[str, Any]:
    return {
        "data_valid": bool(data_valid),
        "data_quality_ok": bool(data_quality_ok),
        "session_eligible": bool(session_eligible),
        "warmup_complete": bool(warmup_complete),
        "risk_veto_active": bool(risk_veto_active),
        "reconciliation_lock_active": bool(reconciliation_lock_active),
        "active_position_present": bool(active_position_present),
        "provider_ready_classic": bool(provider_ready_classic),
        "provider_ready_miso": bool(provider_ready_miso),
        "dhan_context_fresh": bool(dhan_context_fresh),
        "selected_option_present": bool(selected_option_present),
        "futures_present": bool(futures_present),
        "call_present": bool(call_present),
        "put_present": bool(put_present),
    }


# ============================================================================
# Family-specific support builders
# ============================================================================


def build_mist_branch_support(
    *,
    branch_id: str,
    runtime_mode: Any,
    futures_features: Mapping[str, Any],
    selected_features: Mapping[str, Any],
    regime: str,
    regime_reason: str | None = None,
    trend_score: Any = None,
    trend_direction_ok: bool = False,
    pullback_depth: Any = None,
    resume_support: bool = False,
    micro_trap_present: bool = False,
    resume_override_pass: bool = False,
) -> dict[str, Any]:
    branch = _normalize_branch(branch_id)
    return {
        "surface_kind": "mist",
        "branch_id": branch,
        "runtime_mode": _normalize_strategy_runtime_mode(
            runtime_mode,
            family_id=C.FAMILY_ID_MIST,
        ),
        "futures_features": dict(
            _require_mapping(futures_features, field_name="futures_features")
        ),
        "selected_features": dict(
            _require_mapping(selected_features, field_name="selected_features")
        ),
        "trend_score": _optional_float(trend_score),
        "trend_direction_ok": bool(trend_direction_ok),
        "pullback_depth": _optional_float(pullback_depth),
        "resume_support": bool(resume_support),
        "micro_trap_present": bool(micro_trap_present),
        "resume_override_pass": bool(resume_override_pass),
        "regime": _regime_or_default(regime),
        "regime_reason": _clean_optional_str(regime_reason),
    }


def build_misb_branch_support(
    *,
    branch_id: str,
    runtime_mode: Any,
    futures_features: Mapping[str, Any],
    selected_features: Mapping[str, Any],
    regime: str,
    regime_reason: str | None = None,
    breakout_trigger_ok: bool = False,
    breakout_acceptance_ok: bool = False,
    shelf_score: Any = None,
    breakout_score: Any = None,
) -> dict[str, Any]:
    branch = _normalize_branch(branch_id)
    return {
        "surface_kind": "misb",
        "branch_id": branch,
        "runtime_mode": _normalize_strategy_runtime_mode(
            runtime_mode,
            family_id=C.FAMILY_ID_MISB,
        ),
        "futures_features": dict(
            _require_mapping(futures_features, field_name="futures_features")
        ),
        "selected_features": dict(
            _require_mapping(selected_features, field_name="selected_features")
        ),
        "breakout_trigger_ok": bool(breakout_trigger_ok),
        "breakout_acceptance_ok": bool(breakout_acceptance_ok),
        "shelf_score": _optional_float(shelf_score),
        "breakout_score": _optional_float(breakout_score),
        "regime": _regime_or_default(regime),
        "regime_reason": _clean_optional_str(regime_reason),
    }


def build_misc_branch_support(
    *,
    branch_id: str,
    runtime_mode: Any,
    futures_features: Mapping[str, Any],
    selected_features: Mapping[str, Any],
    regime: str,
    regime_reason: str | None = None,
    compression_score: Any = None,
    breakout_trigger_ok: bool = False,
    expansion_acceptance_ok: bool = False,
    retest_valid: bool = False,
    hesitation_valid: bool = False,
    resume_confirmation_ok: bool = False,
) -> dict[str, Any]:
    branch = _normalize_branch(branch_id)
    return {
        "surface_kind": "misc",
        "branch_id": branch,
        "runtime_mode": _normalize_strategy_runtime_mode(
            runtime_mode,
            family_id=C.FAMILY_ID_MISC,
        ),
        "futures_features": dict(
            _require_mapping(futures_features, field_name="futures_features")
        ),
        "selected_features": dict(
            _require_mapping(selected_features, field_name="selected_features")
        ),
        "compression_score": _optional_float(compression_score),
        "breakout_trigger_ok": bool(breakout_trigger_ok),
        "expansion_acceptance_ok": bool(expansion_acceptance_ok),
        "retest_valid": bool(retest_valid),
        "hesitation_valid": bool(hesitation_valid),
        "resume_confirmation_ok": bool(resume_confirmation_ok),
        "regime": _regime_or_default(regime),
        "regime_reason": _clean_optional_str(regime_reason),
    }


def build_misr_active_zone(
    *,
    zone_id: str | None = None,
    zone_type: str | None = None,
    zone_low: Any = None,
    zone_high: Any = None,
    zone_mid: Any = None,
    zone_distance_pts: Any = None,
    zone_valid: bool = False,
) -> dict[str, Any]:
    return {
        "zone_id": _clean_optional_str(zone_id),
        "zone_type": _clean_optional_str(zone_type),
        "zone_low": _optional_float(zone_low),
        "zone_high": _optional_float(zone_high),
        "zone_mid": _optional_float(zone_mid),
        "zone_distance_pts": _optional_float(zone_distance_pts),
        "zone_valid": bool(zone_valid),
    }


def build_misr_branch_support(
    *,
    branch_id: str,
    runtime_mode: Any,
    futures_features: Mapping[str, Any],
    selected_features: Mapping[str, Any],
    active_zone: Mapping[str, Any],
    regime: str,
    regime_reason: str | None = None,
    trap_detected: bool = False,
    fake_break_detected: bool = False,
    absorption_ok: bool = False,
    reclaim_ok: bool = False,
    hold_proof_ok: bool = False,
    reversal_impulse_ok: bool = False,
    trap_event_id: str | None = None,
) -> dict[str, Any]:
    branch = _normalize_branch(branch_id)
    return {
        "surface_kind": "misr",
        "branch_id": branch,
        "runtime_mode": _normalize_strategy_runtime_mode(
            runtime_mode,
            family_id=C.FAMILY_ID_MISR,
        ),
        "futures_features": dict(
            _require_mapping(futures_features, field_name="futures_features")
        ),
        "selected_features": dict(
            _require_mapping(selected_features, field_name="selected_features")
        ),
        "active_zone": dict(_require_mapping(active_zone, field_name="active_zone")),
        "trap_detected": bool(trap_detected),
        "fake_break_detected": bool(fake_break_detected),
        "absorption_ok": bool(absorption_ok),
        "reclaim_ok": bool(reclaim_ok),
        "hold_proof_ok": bool(hold_proof_ok),
        "reversal_impulse_ok": bool(reversal_impulse_ok),
        "trap_event_id": _clean_optional_str(trap_event_id),
        "regime": _regime_or_default(regime),
        "regime_reason": _clean_optional_str(regime_reason),
    }


def build_miso_side_support(
    *,
    branch_id: str,
    runtime_mode: Any,
    futures_features: Mapping[str, Any],
    selected_features: Mapping[str, Any],
    shadow_features: Mapping[str, Any],
    regime_surface: Mapping[str, Any],
    aggressive_flow: bool,
    tape_speed: Any,
    imbalance_persistence: Any,
    queue_reload_veto: bool,
    shadow_support: bool,
    futures_vwap_alignment_ok: bool,
    futures_contradiction_veto: bool,
    selected_context_score: Any = None,
    selected_context_iv: Any = None,
    selected_context_oi: Any = None,
    burst_event_id: str | None = None,
) -> dict[str, Any]:
    branch = _normalize_branch(branch_id)
    return {
        "surface_kind": "miso",
        "branch_id": branch,
        "runtime_mode": _normalize_strategy_runtime_mode(
            runtime_mode,
            family_id=C.FAMILY_ID_MISO,
        ),
        "futures_features": dict(
            _require_mapping(futures_features, field_name="futures_features")
        ),
        "selected_features": dict(
            _require_mapping(selected_features, field_name="selected_features")
        ),
        "shadow_features": dict(
            _require_mapping(shadow_features, field_name="shadow_features")
        ),
        "aggressive_flow": bool(aggressive_flow),
        "tape_speed": _optional_float(tape_speed),
        "imbalance_persistence": _optional_float(imbalance_persistence),
        "queue_reload_veto": bool(queue_reload_veto),
        "shadow_support": bool(shadow_support),
        "futures_vwap_alignment_ok": bool(futures_vwap_alignment_ok),
        "futures_contradiction_veto": bool(futures_contradiction_veto),
        "selected_context_score": _optional_float(selected_context_score),
        "selected_context_iv": _optional_float(selected_context_iv),
        "selected_context_oi": _optional_int(selected_context_oi),
        "regime": _regime_or_default(regime_surface.get("regime")),
        "regime_reason": _clean_optional_str(regime_surface.get("regime_reason")),
        "regime_surface": dict(
            _require_mapping(regime_surface, field_name="regime_surface")
        ),
        "burst_event_id": _clean_optional_str(burst_event_id),
    }


# ============================================================================
# Family wrappers
# ============================================================================


def build_mist_family_support(
    *,
    call_support: Mapping[str, Any],
    put_support: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "family_id": C.FAMILY_ID_MIST,
        "surface_kind": "classic_family",
        "branches": {
            C.BRANCH_CALL: dict(
                _require_mapping(call_support, field_name="call_support")
            ),
            C.BRANCH_PUT: dict(
                _require_mapping(put_support, field_name="put_support")
            ),
        },
    }


def build_misb_family_support(
    *,
    call_support: Mapping[str, Any],
    put_support: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "family_id": C.FAMILY_ID_MISB,
        "surface_kind": "classic_family",
        "branches": {
            C.BRANCH_CALL: dict(
                _require_mapping(call_support, field_name="call_support")
            ),
            C.BRANCH_PUT: dict(
                _require_mapping(put_support, field_name="put_support")
            ),
        },
    }


def build_misc_family_support(
    *,
    call_support: Mapping[str, Any],
    put_support: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "family_id": C.FAMILY_ID_MISC,
        "surface_kind": "classic_family",
        "branches": {
            C.BRANCH_CALL: dict(
                _require_mapping(call_support, field_name="call_support")
            ),
            C.BRANCH_PUT: dict(
                _require_mapping(put_support, field_name="put_support")
            ),
        },
    }


def build_misr_family_support(
    *,
    call_support: Mapping[str, Any],
    put_support: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "family_id": C.FAMILY_ID_MISR,
        "surface_kind": "classic_family",
        "branches": {
            C.BRANCH_CALL: dict(
                _require_mapping(call_support, field_name="call_support")
            ),
            C.BRANCH_PUT: dict(
                _require_mapping(put_support, field_name="put_support")
            ),
        },
    }


def build_miso_family_support(
    *,
    call_support: Mapping[str, Any],
    put_support: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "family_id": C.FAMILY_ID_MISO,
        "surface_kind": "miso_family",
        "sides": {
            C.BRANCH_CALL: dict(
                _require_mapping(call_support, field_name="call_support")
            ),
            C.BRANCH_PUT: dict(
                _require_mapping(put_support, field_name="put_support")
            ),
        },
    }


def build_families_block(
    *,
    mist_support: Mapping[str, Any],
    misb_support: Mapping[str, Any],
    misc_support: Mapping[str, Any],
    misr_support: Mapping[str, Any],
    miso_support: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        C.FAMILY_ID_MIST: dict(
            _require_mapping(mist_support, field_name="mist_support")
        ),
        C.FAMILY_ID_MISB: dict(
            _require_mapping(misb_support, field_name="misb_support")
        ),
        C.FAMILY_ID_MISC: dict(
            _require_mapping(misc_support, field_name="misc_support")
        ),
        C.FAMILY_ID_MISR: dict(
            _require_mapping(misr_support, field_name="misr_support")
        ),
        C.FAMILY_ID_MISO: dict(
            _require_mapping(miso_support, field_name="miso_support")
        ),
    }


# ============================================================================
# Final payload assembly
# ============================================================================


def build_family_features_payload(
    *,
    snapshot: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
    common: Mapping[str, Any],
    stage_flags: Mapping[str, Any],
    families: Mapping[str, Any],
    payload_source: str = "features",
    payload_version: str = C.FAMILY_FEATURES_VERSION,
    legacy: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "payload_source": _non_empty_str(payload_source, field_name="payload_source"),
        "payload_version": _safe_str(payload_version, default=C.FAMILY_FEATURES_VERSION),
        "snapshot": dict(_require_mapping(snapshot, field_name="snapshot")),
        "provider_runtime": dict(
            _require_mapping(provider_runtime, field_name="provider_runtime")
        ),
        "common": dict(_require_mapping(common, field_name="common")),
        "stage_flags": dict(
            _require_mapping(stage_flags, field_name="stage_flags")
        ),
        "families": dict(_require_mapping(families, field_name="families")),
        "legacy": _copy_mapping(legacy),
        "metadata": _copy_mapping(metadata),
    }
    C.validate_family_features_payload(payload)
    return payload


def build_publishable_family_features_payload(
    *,
    snapshot: Mapping[str, Any],
    provider_runtime: Mapping[str, Any],
    common: Mapping[str, Any],
    stage_flags: Mapping[str, Any],
    families: Mapping[str, Any],
    payload_source: str = "features",
    payload_version: str = C.FAMILY_FEATURES_VERSION,
    legacy: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = build_family_features_payload(
        snapshot=snapshot,
        provider_runtime=provider_runtime,
        common=common,
        stage_flags=stage_flags,
        families=families,
        payload_source=payload_source,
        payload_version=payload_version,
        legacy=legacy,
        metadata=metadata,
    )
    C.validate_publishable_family_features_payload(payload)
    return payload


__all__ = [
    "FeatureFamilyCommonError",
    "EPSILON",
    "OPTION_SIDE_CALL",
    "OPTION_SIDE_PUT",
    "OPTION_SIDE_IDS",
    "build_snapshot_block",
    "build_provider_runtime_block",
    "build_market_block",
    "build_common_futures_block",
    "build_common_option_block",
    "build_selected_option_block",
    "build_cross_option_block",
    "build_economics_block",
    "build_signals_block",
    "build_common_block",
    "build_stage_flags_block",
    "build_mist_branch_support",
    "build_misb_branch_support",
    "build_misc_branch_support",
    "build_misr_active_zone",
    "build_misr_branch_support",
    "build_miso_side_support",
    "build_mist_family_support",
    "build_misb_family_support",
    "build_misc_family_support",
    "build_misr_family_support",
    "build_miso_family_support",
    "build_families_block",
    "build_family_features_payload",
    "build_publishable_family_features_payload",
    "derive_provider_ready_classic",
    "derive_provider_ready_miso",
    "derive_selected_option_present",
    "derive_common_premium_floor_ok",
    "derive_depth_ok",
    "derive_spread_ratio_ok",
    "derive_response_efficiency_ok",
    "derive_tradability_ok",
    "derive_selected_option_tradability_ok",
    "derive_stage_flags",
]
