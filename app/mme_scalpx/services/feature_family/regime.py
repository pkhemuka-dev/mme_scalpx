from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/regime.py

Canonical shared regime and runtime-mode feature core for ScalpX MME.

Purpose
-------
This module OWNS:
- deterministic market regime classification from shared futures/option surfaces
- doctrine-neutral classic MIS runtime-mode resolution
- doctrine-neutral MISO runtime-mode resolution
- serialized regime/mode summary payloads for services/features.py publication

This module DOES NOT own:
- strike selection
- OI wall / ladder logic
- option tradability truth
- doctrine-specific entry / exit logic
- provider failover policy
- Redis I/O

Frozen design law
-----------------
- regime classification is a shared feature-core responsibility
- classic MIS runtime mode is driven by provider/runtime/context health truth
- MISO runtime mode is driven by option/futures live feed readiness plus depth-path readiness
- this module must remain deterministic, side-effect free, and doctrine-neutral
- outputs must be JSON-friendly plain mappings
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

EPSILON: Final[float] = 1e-8

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"
REGIME_UNKNOWN: Final[str] = "UNKNOWN"

DEFAULT_LOWVOL_RATIO_MAX: Final[float] = 0.80
DEFAULT_FAST_RATIO_MIN: Final[float] = 1.50
DEFAULT_EVENT_RATE_SPIKE_FAST_MIN: Final[float] = 1.50
DEFAULT_EVENT_RATE_SPIKE_LOWVOL_MAX: Final[float] = 1.05
DEFAULT_VOLUME_NORM_FAST_MIN: Final[float] = 1.20
DEFAULT_VOLUME_NORM_LOWVOL_MAX: Final[float] = 0.85

DEFAULT_CLASSIC_MODE_NORMAL: Final[str] = "NORMAL"
DEFAULT_CLASSIC_MODE_DHAN_DEGRADED: Final[str] = "DHAN_DEGRADED"

DEFAULT_MISO_MODE_BASE_5DEPTH: Final[str] = "BASE_5DEPTH"
DEFAULT_MISO_MODE_DEPTH20_ENHANCED: Final[str] = "DEPTH20_ENHANCED"
DEFAULT_MISO_MODE_DISABLED: Final[str] = "DISABLED"

DEFAULT_CONTEXT_STALE_MS: Final[float] = 5_000.0
DEFAULT_DEPTH20_STALE_MS: Final[float] = 1_500.0
DEFAULT_SURFACE_STALE_MS: Final[float] = 1_000.0

_PROVIDER_STATUS_HEALTHY: Final[str] = _safe_str(getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY")).upper() if "N" in globals() else "HEALTHY"
_PROVIDER_STATUS_DEGRADED: Final[str] = _safe_str(getattr(N, "PROVIDER_STATUS_DEGRADED", "DEGRADED")).upper() if "N" in globals() else "DEGRADED"
_PROVIDER_STATUS_STALE: Final[str] = _safe_str(getattr(N, "PROVIDER_STATUS_STALE", "STALE")).upper() if "N" in globals() else "STALE"
_PROVIDER_STATUS_UNAVAILABLE: Final[str] = _safe_str(getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")).upper() if "N" in globals() else "UNAVAILABLE"

_CLASSIC_MODE_NORMAL_ALLOWED_PROVIDER_STATUSES: Final[set[str]] = {
    _PROVIDER_STATUS_HEALTHY,
    _PROVIDER_STATUS_DEGRADED,
}
_MISO_MODE_ALLOWED_PROVIDER_STATUSES: Final[set[str]] = {
    _PROVIDER_STATUS_HEALTHY,
    _PROVIDER_STATUS_DEGRADED,
}

__all__ = [
    "build_classic_runtime_mode_surface",
    "build_miso_runtime_mode_surface",
    "build_regime_bundle",
    "build_regime_surface",
    "classify_market_regime",
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return float(default)
    if not isfinite(number):
        return float(default)
    return float(number)


def _safe_float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except Exception:
        return None
    if not isfinite(number):
        return None
    return float(number)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


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
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _pick(mapping: Mapping[str, Any] | None, *keys: str) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _surface_present(surface: Mapping[str, Any]) -> bool:
    return bool(surface) and _safe_bool(_pick(surface, "present"), True)


def _surface_age_ms(surface: Mapping[str, Any]) -> float:
    return _safe_float(_coalesce(_pick(surface, "age_ms"), _pick(surface, "packet_gap_ms")), 0.0)


def _surface_stale(surface: Mapping[str, Any], *, stale_ms: float = DEFAULT_SURFACE_STALE_MS) -> bool:
    return _safe_bool(_pick(surface, "stale"), False) or (_surface_age_ms(surface) > stale_ms)


def _normalize_provider_status(value: Any) -> str:
    text = _safe_str(value).upper()
    if text in {
        _PROVIDER_STATUS_HEALTHY,
        _PROVIDER_STATUS_DEGRADED,
        _PROVIDER_STATUS_STALE,
        _PROVIDER_STATUS_UNAVAILABLE,
    }:
        return text
    return _PROVIDER_STATUS_STALE


def _provider_status_allows_classic_normal(status: str) -> bool:
    return _normalize_provider_status(status) in _CLASSIC_MODE_NORMAL_ALLOWED_PROVIDER_STATUSES


def _provider_status_allows_miso(status: str) -> bool:
    return _normalize_provider_status(status) in _MISO_MODE_ALLOWED_PROVIDER_STATUSES


def _threshold_float(
    thresholds: Mapping[str, Any] | None,
    key: str,
    default: float,
) -> float:
    return _safe_float(_pick(thresholds, key), default)


def classify_market_regime(
    *,
    futures_surface: Mapping[str, Any] | None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Shared regime classifier.

    Uses futures-led shared-core signals only:
    - velocity_ratio
    - event_rate_spike_ratio
    - volume_norm
    - optional direction/microstructure confirmation
    """
    fut = _as_mapping(_pick(_as_mapping(futures_surface), "selected_features") or futures_surface)

    present = _surface_present(fut)
    stale = _surface_stale(fut)
    velocity_ratio = _safe_float(_pick(fut, "velocity_ratio"), 0.0)
    event_rate_spike_ratio = _safe_float(_pick(fut, "event_rate_spike_ratio"), 0.0)
    volume_norm = _safe_float(_pick(fut, "volume_norm"), 0.0)
    direction_score = _safe_float(_pick(fut, "direction_score", "trend_score"), 0.0)
    weighted_ofi = _safe_float(_pick(fut, "weighted_ofi"), 0.0)
    spread_ratio = _safe_float(_pick(fut, "spread_ratio"), 0.0)

    lowvol_ratio_max = _threshold_float(thresholds, "LOWVOL_RATIO_MAX", DEFAULT_LOWVOL_RATIO_MAX)
    fast_ratio_min = _threshold_float(thresholds, "FAST_RATIO_MIN", DEFAULT_FAST_RATIO_MIN)
    fast_event_rate_min = _threshold_float(
        thresholds,
        "EVENT_RATE_SPIKE_FAST_MIN",
        DEFAULT_EVENT_RATE_SPIKE_FAST_MIN,
    )
    lowvol_event_rate_max = _threshold_float(
        thresholds,
        "EVENT_RATE_SPIKE_LOWVOL_MAX",
        DEFAULT_EVENT_RATE_SPIKE_LOWVOL_MAX,
    )
    fast_volume_norm_min = _threshold_float(
        thresholds,
        "FAST_VOLUME_NORM_MIN",
        DEFAULT_VOLUME_NORM_FAST_MIN,
    )
    lowvol_volume_norm_max = _threshold_float(
        thresholds,
        "LOWVOL_VOLUME_NORM_MAX",
        DEFAULT_VOLUME_NORM_LOWVOL_MAX,
    )

    if not present or stale:
        regime = REGIME_UNKNOWN
        reason = "surface_unavailable" if not present else "surface_stale"
    elif (
        velocity_ratio >= fast_ratio_min
        or (event_rate_spike_ratio >= fast_event_rate_min and volume_norm >= fast_volume_norm_min)
    ):
        regime = REGIME_FAST
        reason = "fast_ratio_or_event_rate"
    elif (
        velocity_ratio <= lowvol_ratio_max
        and event_rate_spike_ratio <= lowvol_event_rate_max
        and volume_norm <= lowvol_volume_norm_max
    ):
        regime = REGIME_LOWVOL
        reason = "lowvol_ratio_event_rate_volume"
    else:
        regime = REGIME_NORMAL
        reason = "mid_band"

    regime_score = 0.0
    if regime == REGIME_FAST:
        regime_score = max(
            velocity_ratio / max(fast_ratio_min, EPSILON),
            event_rate_spike_ratio / max(fast_event_rate_min, EPSILON),
            volume_norm / max(fast_volume_norm_min, EPSILON),
        )
    elif regime == REGIME_LOWVOL:
        regime_score = min(
            max(lowvol_ratio_max, EPSILON) / max(velocity_ratio, EPSILON),
            max(lowvol_event_rate_max, EPSILON) / max(event_rate_spike_ratio, EPSILON),
            max(lowvol_volume_norm_max, EPSILON) / max(volume_norm, EPSILON),
        )
    elif regime == REGIME_NORMAL:
        regime_score = 1.0

    return {
        "present": present,
        "stale": stale,
        "regime": regime,
        "regime_reason": reason,
        "regime_score": regime_score,
        "velocity_ratio": velocity_ratio,
        "event_rate_spike_ratio": event_rate_spike_ratio,
        "volume_norm": volume_norm,
        "direction_score": direction_score,
        "weighted_ofi": weighted_ofi,
        "spread_ratio": spread_ratio,
        "futures_surface_present": present,
    }


def build_regime_surface(
    *,
    futures_surface: Mapping[str, Any] | None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    classified = classify_market_regime(
        futures_surface=futures_surface,
        thresholds=thresholds,
    )
    regime = _safe_str(classified.get("regime"), REGIME_UNKNOWN)

    return {
        **classified,
        "is_lowvol": regime == REGIME_LOWVOL,
        "is_normal": regime == REGIME_NORMAL,
        "is_fast": regime == REGIME_FAST,
        "is_known": regime != REGIME_UNKNOWN,
    }


def build_classic_runtime_mode_surface(
    *,
    provider_runtime: Mapping[str, Any] | None,
    dhan_context: Mapping[str, Any] | None = None,
    active_futures_surface: Mapping[str, Any] | None = None,
    active_call_surface: Mapping[str, Any] | None = None,
    active_put_surface: Mapping[str, Any] | None = None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Resolve classic MIS runtime mode.

    NORMAL:
    - active futures surface present and fresh
    - at least one active option side present and fresh
    - Dhan context lane healthy/fresh enough for enhancement

    DHAN_DEGRADED:
    - active futures and selected option live truth are still usable
    - Dhan context is unavailable / stale / degraded beyond usable enhancement
    """
    pr = _as_mapping(provider_runtime)
    ctx = _as_mapping(dhan_context)
    fut = _as_mapping(_pick(_as_mapping(active_futures_surface), "selected_features") or active_futures_surface)
    call = _as_mapping(_pick(_as_mapping(active_call_surface), "selected_features") or active_call_surface)
    put = _as_mapping(_pick(_as_mapping(active_put_surface), "selected_features") or active_put_surface)

    active_feed_ok = _surface_present(fut) and not _surface_stale(fut)
    active_option_ok = (
        (_surface_present(call) and not _surface_stale(call))
        or (_surface_present(put) and not _surface_stale(put))
    )

    context_age_ms = _surface_age_ms(ctx)
    context_present = _surface_present(ctx)
    context_stale_ms = _threshold_float(
        thresholds,
        "DHAN_CONTEXT_MAX_AGE_MS",
        DEFAULT_CONTEXT_STALE_MS,
    )
    context_status = _normalize_provider_status(
        _coalesce(
            _pick(ctx, "context_status"),
            _pick(pr, "option_context_provider_status"),
            _pick(pr, "dhan_context_status"),
            _pick(pr, "context_provider_status"),
        )
    )
    context_fresh = (
        context_present
        and context_age_ms <= context_stale_ms
        and not _safe_bool(_pick(ctx, "stale"), False)
    )

    provider_allows_normal = _provider_status_allows_classic_normal(context_status)

    mode = (
        DEFAULT_CLASSIC_MODE_NORMAL
        if active_feed_ok and active_option_ok and context_fresh and provider_allows_normal
        else DEFAULT_CLASSIC_MODE_DHAN_DEGRADED
    )

    return {
        "present": active_feed_ok and active_option_ok,
        "runtime_mode": mode,
        "active_futures_ok": active_feed_ok,
        "active_option_ok": active_option_ok,
        "dhan_context_present": context_present,
        "dhan_context_fresh": context_fresh,
        "option_context_provider_status": context_status,
        "provider_allows_normal": provider_allows_normal,
        "normal_mode_available": mode == DEFAULT_CLASSIC_MODE_NORMAL,
        "degraded_mode_active": mode == DEFAULT_CLASSIC_MODE_DHAN_DEGRADED,
        "blocked_reason": (
            ""
            if mode == DEFAULT_CLASSIC_MODE_NORMAL
            else "active_live_surface_unavailable"
            if not (active_feed_ok and active_option_ok)
            else "dhan_context_unavailable"
            if not context_present
            else "dhan_context_stale"
            if not context_fresh
            else "provider_status_not_normal"
        ),
    }


def build_miso_runtime_mode_surface(
    *,
    provider_runtime: Mapping[str, Any] | None,
    dhan_futures_surface: Mapping[str, Any] | None,
    dhan_call_surface: Mapping[str, Any] | None = None,
    dhan_put_surface: Mapping[str, Any] | None = None,
    dhan_context: Mapping[str, Any] | None = None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Resolve MISO runtime mode.

    DEPTH20_ENHANCED:
    - Dhan futures present/fresh
    - at least one Dhan option side present/fresh
    - chain/context fresh
    - depth20 readiness explicitly present and fresh enough

    BASE_5DEPTH:
    - same core live surfaces present/fresh
    - depth20 readiness absent or stale

    DISABLED:
    - missing core option/futures/context readiness
    """
    pr = _as_mapping(provider_runtime)
    fut = _as_mapping(_pick(_as_mapping(dhan_futures_surface), "selected_features") or dhan_futures_surface)
    call = _as_mapping(_pick(_as_mapping(dhan_call_surface), "selected_features") or dhan_call_surface)
    put = _as_mapping(_pick(_as_mapping(dhan_put_surface), "selected_features") or dhan_put_surface)
    ctx = _as_mapping(dhan_context)

    futures_status = _normalize_provider_status(
        _coalesce(_pick(pr, "futures_marketdata_status"), _pick(pr, "futures_provider_status"))
    )
    selected_option_status = _normalize_provider_status(
        _coalesce(_pick(pr, "selected_option_marketdata_status"), _pick(pr, "selected_option_provider_status"))
    )
    context_status = _normalize_provider_status(
        _coalesce(
            _pick(ctx, "context_status"),
            _pick(pr, "option_context_status"),
            _pick(pr, "dhan_context_status"),
            _pick(pr, "context_provider_status"),
        )
    )

    futures_ok = (
        _surface_present(fut)
        and not _surface_stale(fut)
        and _provider_status_allows_miso(futures_status)
    )
    option_ok = (
        (
            _surface_present(call)
            and not _surface_stale(call)
        )
        or (
            _surface_present(put)
            and not _surface_stale(put)
        )
    ) and _provider_status_allows_miso(selected_option_status)

    context_age_ms = _surface_age_ms(ctx)
    context_present = _surface_present(ctx)
    context_fresh = (
        context_present
        and context_age_ms <= _threshold_float(
            thresholds,
            "DHAN_CONTEXT_MAX_AGE_MS",
            DEFAULT_CONTEXT_STALE_MS,
        )
        and not _safe_bool(_pick(ctx, "stale"), False)
        and _provider_status_allows_miso(context_status)
    )

    depth20_present = _safe_bool(
        _coalesce(
            _pick(pr, "depth20_present"),
            _pick(pr, "dhan_depth20_present"),
            _pick(ctx, "depth20_present"),
        ),
        False,
    )
    depth20_age_ms = _safe_float(
        _coalesce(
            _pick(pr, "depth20_age_ms"),
            _pick(ctx, "depth20_age_ms"),
        ),
        9_999_999.0,
    )
    depth20_fresh = depth20_present and depth20_age_ms <= _threshold_float(
        thresholds,
        "DEPTH20_MAX_AGE_MS",
        DEFAULT_DEPTH20_STALE_MS,
    )

    mode = DEFAULT_MISO_MODE_DISABLED
    if futures_ok and option_ok and context_fresh:
        mode = DEFAULT_MISO_MODE_DEPTH20_ENHANCED if depth20_fresh else DEFAULT_MISO_MODE_BASE_5DEPTH

    return {
        "present": futures_ok and option_ok,
        "runtime_mode": mode,
        "futures_ok": futures_ok,
        "option_ok": option_ok,
        "context_present": context_present,
        "context_fresh": context_fresh,
        "futures_provider_status": futures_status,
        "selected_option_provider_status": selected_option_status,
        "option_context_provider_status": context_status,
        "depth20_present": depth20_present,
        "depth20_fresh": depth20_fresh,
        "base_5depth_available": mode in {DEFAULT_MISO_MODE_BASE_5DEPTH, DEFAULT_MISO_MODE_DEPTH20_ENHANCED},
        "depth20_enhanced_available": mode == DEFAULT_MISO_MODE_DEPTH20_ENHANCED,
        "disabled": mode == DEFAULT_MISO_MODE_DISABLED,
        "blocked_reason": (
            ""
            if mode != DEFAULT_MISO_MODE_DISABLED
            else "futures_unavailable"
            if not futures_ok
            else "option_unavailable"
            if not option_ok
            else "context_unavailable"
        ),
    }


def build_regime_bundle(
    *,
    provider_runtime: Mapping[str, Any] | None,
    active_futures_surface: Mapping[str, Any] | None,
    dhan_futures_surface: Mapping[str, Any] | None = None,
    active_call_surface: Mapping[str, Any] | None = None,
    active_put_surface: Mapping[str, Any] | None = None,
    dhan_call_surface: Mapping[str, Any] | None = None,
    dhan_put_surface: Mapping[str, Any] | None = None,
    dhan_context: Mapping[str, Any] | None = None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    classic_regime = build_regime_surface(
        futures_surface=active_futures_surface,
        thresholds=thresholds,
    )
    miso_regime = build_regime_surface(
        futures_surface=dhan_futures_surface,
        thresholds=thresholds,
    )
    classic_mode = build_classic_runtime_mode_surface(
        provider_runtime=provider_runtime,
        dhan_context=dhan_context,
        active_futures_surface=active_futures_surface,
        active_call_surface=active_call_surface,
        active_put_surface=active_put_surface,
        thresholds=thresholds,
    )
    miso_mode = build_miso_runtime_mode_surface(
        provider_runtime=provider_runtime,
        dhan_futures_surface=dhan_futures_surface,
        dhan_call_surface=dhan_call_surface,
        dhan_put_surface=dhan_put_surface,
        dhan_context=dhan_context,
        thresholds=thresholds,
    )

    return {
        "present": bool(
            classic_regime.get("present")
            or miso_regime.get("present")
            or classic_mode.get("present")
            or miso_mode.get("present")
        ),
        "classic_regime": classic_regime,
        "miso_regime": miso_regime,
        "classic_runtime_mode": classic_mode,
        "miso_runtime_mode": miso_mode,
        # compatibility alias for older single-regime consumers
        "regime": classic_regime,
    }
