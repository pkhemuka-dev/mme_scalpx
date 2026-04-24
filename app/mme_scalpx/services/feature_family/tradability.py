from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/tradability.py

Canonical shared tradability-feature core for ScalpX MME.

Purpose
-------
This module OWNS:
- deterministic doctrine-neutral tradability evaluation helpers
- regime/mode/branch-aware threshold resolution for option tradability
- shared futures-vs-option market-quality guard surfaces
- option entry-shell pass/fail evaluation for classic MIS doctrines
- option live-book tradability shell for MISO
- serializable guard/audit payloads for features.py publication

This module DOES NOT own:
- provider-routing policy
- strike-selection doctrine
- regime classification
- family-specific entry logic
- futures directional truth
- slow-context OI wall logic
- Redis I/O

Frozen design law
-----------------
- selected live option book is tradability truth
- tradability evaluation must stay deterministic and side-effect free
- no doctrine-specific trigger logic may leak into this shared module
- thresholds may vary by branch/mode/regime, but the shell remains explicit:
  stale / crossed-book / spread / depth / response / impact / queue / liquidity
- returned surfaces must be JSON-friendly plain mappings
"""

from math import isfinite
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

EPSILON: Final[float] = 1e-8

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

DEFAULT_MODE_NORMAL: Final[str] = "NORMAL"
DEFAULT_MODE_DHAN_DEGRADED: Final[str] = "DHAN_DEGRADED"

DEFAULT_STALE_THRESHOLD_MS: Final[float] = 1_000.0
DEFAULT_OPT_SPREAD_RATIO_MAX: Final[float] = 1.60
DEFAULT_OPT_DEPTH_MIN: Final[int] = 80
DEFAULT_OPT_RESPONSE_EFF_MIN: Final[float] = 0.17
DEFAULT_DEGRADED_OPT_RESPONSE_EFF_MIN: Final[float] = 0.19
DEFAULT_IMPACT_DEPTH_FRACTION_MAX: Final[float] = 0.27
DEFAULT_DEGRADED_IMPACT_DEPTH_FRACTION_MAX: Final[float] = 0.22
DEFAULT_LIQUIDITY_EXIT_SPREAD_RATIO: Final[float] = 1.90
DEFAULT_LIQUIDITY_EXIT_DEPTH_FRACTION: Final[float] = 0.60
DEFAULT_FUT_SPREAD_RATIO_MAX: Final[float] = 1.60
DEFAULT_FUT_DEPTH_MIN: Final[int] = 250

__all__ = [
    "build_classic_option_tradability_surface",
    "build_futures_liquidity_surface",
    "build_miso_option_tradability_surface",
    "build_tradability_summary",
    "resolve_option_thresholds",
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


def _default_branch_side(branch_id: str) -> str:
    return N.SIDE_CALL if branch_id == N.BRANCH_CALL else N.SIDE_PUT


def _normalize_regime(regime: str) -> str:
    value = _safe_str(regime, REGIME_NORMAL).upper()
    if value in {REGIME_LOWVOL, REGIME_NORMAL, REGIME_FAST}:
        return value
    return REGIME_NORMAL


def _normalize_mode(mode: str) -> str:
    value = _safe_str(mode, DEFAULT_MODE_NORMAL).upper()
    if value in {
        DEFAULT_MODE_NORMAL,
        DEFAULT_MODE_DHAN_DEGRADED,
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_NORMAL", DEFAULT_MODE_NORMAL)).upper(),
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DHAN_DEGRADED", DEFAULT_MODE_DHAN_DEGRADED)).upper(),
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE_5DEPTH")).upper(),
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED", "DEPTH20_ENHANCED")).upper(),
        _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")).upper(),
    }:
        return value
    return DEFAULT_MODE_NORMAL


def _branch_suffix(branch_id: str) -> str:
    return "CE" if branch_id == N.BRANCH_CALL else "PE"


def _strike_depth_key(branch_id: str, selection_label: str, degraded: bool) -> str:
    suffix = _branch_suffix(branch_id)
    base = "ATM1" if selection_label == "active_atm1" else "ATM"
    if degraded:
        return f"DEGRADED_{base}_{suffix}_DEPTH_MIN"
    return f"{base}_{suffix}_DEPTH_MIN"


def _spread_cap_key(branch_id: str, regime: str, degraded: bool) -> str:
    suffix = _branch_suffix(branch_id)
    prefix = "DEGRADED_" if degraded else ""
    return f"{prefix}{regime}_{suffix}_SPREAD_RATIO_MAX"


def _response_eff_key(branch_id: str, degraded: bool) -> str:
    suffix = _branch_suffix(branch_id)
    return f"{'DEGRADED_' if degraded else ''}{suffix}_RESPONSE_EFF_MIN"


def _impact_depth_key(degraded: bool) -> str:
    return "DEGRADED_IMPACT_DEPTH_FRACTION_MAX" if degraded else "IMPACT_DEPTH_FRACTION_MAX"


def _liquidity_exit_depth_fraction(
    thresholds: Mapping[str, Any] | None,
) -> float:
    value = _safe_float_or_none(_pick(thresholds, "LIQUIDITY_EXIT_DEPTH_FRACTION"))
    if value is not None:
        return value
    return DEFAULT_LIQUIDITY_EXIT_DEPTH_FRACTION


def _threshold_value(
    thresholds: Mapping[str, Any] | None,
    key: str,
    default: float | int,
) -> float:
    return _safe_float(_pick(thresholds, key), float(default))


def resolve_option_thresholds(
    *,
    branch_id: str,
    regime: str,
    runtime_mode: str,
    selection_label: str,
    thresholds: Mapping[str, Any] | None = None,
    expiry_tightened: bool = False,
    expiry_response_eff_multiplier: float | None = None,
) -> dict[str, Any]:
    regime_norm = _normalize_regime(regime)
    mode_norm = _normalize_mode(runtime_mode)
    degraded = mode_norm == DEFAULT_MODE_DHAN_DEGRADED
    selection = _safe_str(selection_label, "active_atm")

    spread_cap = _threshold_value(
        thresholds,
        _spread_cap_key(branch_id, regime_norm, degraded),
        DEFAULT_OPT_SPREAD_RATIO_MAX,
    )
    depth_min = _threshold_value(
        thresholds,
        _strike_depth_key(branch_id, selection, degraded),
        DEFAULT_OPT_DEPTH_MIN,
    )
    response_eff_min = _threshold_value(
        thresholds,
        _response_eff_key(branch_id, degraded),
        DEFAULT_DEGRADED_OPT_RESPONSE_EFF_MIN if degraded else DEFAULT_OPT_RESPONSE_EFF_MIN,
    )
    if expiry_tightened:
        multiplier = (
            expiry_response_eff_multiplier
            if expiry_response_eff_multiplier is not None
            else _threshold_value(thresholds, "EXPIRY_RESPONSE_EFF_MULTIPLIER", 1.40)
        )
        response_eff_min = max(response_eff_min, response_eff_min * max(multiplier, 1.0))

    impact_depth_fraction_max = _threshold_value(
        thresholds,
        _impact_depth_key(degraded),
        DEFAULT_DEGRADED_IMPACT_DEPTH_FRACTION_MAX if degraded else DEFAULT_IMPACT_DEPTH_FRACTION_MAX,
    )
    liquidity_exit_spread_ratio = _threshold_value(
        thresholds,
        "LIQUIDITY_EXIT_SPREAD_RATIO",
        DEFAULT_LIQUIDITY_EXIT_SPREAD_RATIO,
    )
    liquidity_exit_depth_fraction = _liquidity_exit_depth_fraction(thresholds)

    return {
        "branch_id": branch_id,
        "regime": regime_norm,
        "runtime_mode": mode_norm,
        "selection_label": selection,
        "degraded": degraded,
        "spread_ratio_max": spread_cap,
        "depth_min": int(max(depth_min, 0)),
        "response_eff_min": response_eff_min,
        "impact_depth_fraction_max": impact_depth_fraction_max,
        "liquidity_exit_spread_ratio": liquidity_exit_spread_ratio,
        "liquidity_exit_depth_fraction": liquidity_exit_depth_fraction,
    }


def _best_bid(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "best_bid", "bid"), 0.0)


def _best_ask(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "best_ask", "ask"), 0.0)


def _spread_ratio(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "spread_ratio"), 0.0)


def _bid_qty(surface: Mapping[str, Any]) -> int:
    return _safe_int(_pick(surface, "bid_qty_5", "best_bid_qty", "bid_qty"), 0)


def _ask_qty(surface: Mapping[str, Any]) -> int:
    return _safe_int(_pick(surface, "ask_qty_5", "best_ask_qty", "ask_qty"), 0)


def _touch_depth(surface: Mapping[str, Any]) -> int:
    direct = _safe_int(_pick(surface, "touch_depth", "depth_total"), 0)
    if direct > 0:
        return direct
    return max(_bid_qty(surface) + _ask_qty(surface), 0)


def _response_eff(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "response_efficiency"), 0.0)


def _age_ms(surface: Mapping[str, Any]) -> float:
    return _safe_float(_pick(surface, "age_ms", "packet_gap_ms"), 0.0)


def _stale(surface: Mapping[str, Any]) -> bool:
    return _safe_bool(_pick(surface, "stale"), False) or (_age_ms(surface) > DEFAULT_STALE_THRESHOLD_MS)


def _crossed_book(surface: Mapping[str, Any]) -> bool:
    ask = _best_ask(surface)
    bid = _best_bid(surface)
    if ask <= 0.0 or bid <= 0.0:
        return True
    return ask <= bid


def _impact_depth_fraction(surface: Mapping[str, Any], entry_qty: float | int | None) -> float | None:
    if entry_qty is None:
        return None
    ask_depth = float(max(_ask_qty(surface), 0))
    if ask_depth <= EPSILON:
        ask_depth = float(max(_touch_depth(surface), 0))
    if ask_depth <= EPSILON:
        return None
    return _safe_float(entry_qty, 0.0) / max(ask_depth, EPSILON)


def _queue_reload_veto(surface: Mapping[str, Any], branch_id: str) -> bool:
    generic = _pick(surface, "queue_reload_veto")
    if generic is not None:
        return _safe_bool(generic, False)

    ask_side = _pick(surface, "ask_reload_veto", "ask_reloaded")
    if ask_side is not None:
        return _safe_bool(ask_side, False)

    if branch_id == N.BRANCH_PUT:
        bid_side = _pick(surface, "bid_reload_veto", "bid_reloaded")
        if bid_side is not None:
            return _safe_bool(bid_side, False)

    return False


def _liquidity_exit_depth_trip(surface: Mapping[str, Any], depth_min: int, fraction: float) -> bool:
    if depth_min <= 0:
        return False
    return _touch_depth(surface) < int(max(depth_min * max(fraction, 0.0), 0.0))


def build_classic_option_tradability_surface(
    *,
    branch_id: str,
    option_surface: Mapping[str, Any] | None,
    regime: str,
    runtime_mode: str,
    selection_label: str,
    thresholds: Mapping[str, Any] | None = None,
    entry_qty: float | int | None = None,
    expiry_tightened: bool = False,
) -> dict[str, Any]:
    surface = _as_mapping(option_surface)
    selected = _as_mapping(_pick(surface, "selected_features") or surface)

    resolved = resolve_option_thresholds(
        branch_id=branch_id,
        regime=regime,
        runtime_mode=runtime_mode,
        selection_label=selection_label,
        thresholds=thresholds,
        expiry_tightened=expiry_tightened,
    )

    present = bool(selected) and _safe_bool(_pick(selected, "present"), True)
    stale = _stale(selected)
    crossed_book = _crossed_book(selected)
    spread_ratio = _spread_ratio(selected)
    depth_total = _touch_depth(selected)
    response_eff = _response_eff(selected)
    impact_depth_fraction = _impact_depth_fraction(selected, entry_qty)
    queue_reload_veto = _queue_reload_veto(selected, branch_id)

    spread_pass = spread_ratio <= _safe_float(resolved["spread_ratio_max"])
    depth_pass = depth_total >= _safe_int(resolved["depth_min"])
    response_pass = response_eff >= _safe_float(resolved["response_eff_min"])
    impact_pass = (
        True
        if impact_depth_fraction is None
        else impact_depth_fraction <= _safe_float(resolved["impact_depth_fraction_max"])
    )
    stale_pass = not stale
    crossed_book_pass = not crossed_book
    queue_pass = not queue_reload_veto

    entry_pass = all(
        (
            present,
            stale_pass,
            crossed_book_pass,
            spread_pass,
            depth_pass,
            response_pass,
            impact_pass,
            queue_pass,
        )
    )

    liquidity_exit_trip = (
        spread_ratio > _safe_float(resolved["liquidity_exit_spread_ratio"])
        or _liquidity_exit_depth_trip(
            selected,
            _safe_int(resolved["depth_min"]),
            _safe_float(resolved["liquidity_exit_depth_fraction"]),
        )
    )

    return {
        "present": present,
        "branch_id": branch_id,
        "side": _default_branch_side(branch_id),
        "regime": resolved["regime"],
        "runtime_mode": resolved["runtime_mode"],
        "selection_label": resolved["selection_label"],
        "thresholds": resolved,
        "spread_ratio": spread_ratio,
        "depth_total": depth_total,
        "response_efficiency": response_eff,
        "impact_depth_fraction": impact_depth_fraction,
        "age_ms": _age_ms(selected),
        "stale": stale,
        "crossed_book": crossed_book,
        "queue_reload_veto": queue_reload_veto,
        "spread_pass": spread_pass,
        "depth_pass": depth_pass,
        "response_pass": response_pass,
        "impact_pass": impact_pass,
        "stale_pass": stale_pass,
        "crossed_book_pass": crossed_book_pass,
        "queue_pass": queue_pass,
        "entry_pass": entry_pass,
        "liquidity_exit_trip": liquidity_exit_trip,
        "blocked_reason": (
            ""
            if entry_pass
            else "not_present"
            if not present
            else "stale"
            if not stale_pass
            else "crossed_book"
            if not crossed_book_pass
            else "spread"
            if not spread_pass
            else "depth"
            if not depth_pass
            else "response"
            if not response_pass
            else "impact"
            if not impact_pass
            else "queue_reload"
            if not queue_pass
            else "unknown"
        ),
    }


def build_miso_option_tradability_surface(
    *,
    option_surface: Mapping[str, Any] | None,
    futures_surface: Mapping[str, Any] | None = None,
    runtime_mode: str,
    thresholds: Mapping[str, Any] | None = None,
    entry_qty: float | int | None = None,
) -> dict[str, Any]:
    option_map = _as_mapping(option_surface)
    selected = _as_mapping(_pick(option_map, "selected_features") or option_map)
    futures_map = _as_mapping(_pick(_as_mapping(futures_surface), "selected_features") or futures_surface)

    present = bool(selected) and _safe_bool(_pick(selected, "present"), True)
    futures_present = bool(futures_map) and _safe_bool(_pick(futures_map, "present"), True)

    spread_ratio_max = _threshold_value(thresholds, "OPT_ENTRY_SPREAD_RATIO_MAX", DEFAULT_OPT_SPREAD_RATIO_MAX)
    depth_min = int(_threshold_value(thresholds, "OPT_TOUCH_DEPTH_MIN", DEFAULT_OPT_DEPTH_MIN))
    fut_spread_ratio_max = _threshold_value(thresholds, "FUT_SPREAD_MAX", DEFAULT_FUT_SPREAD_RATIO_MAX)
    fut_depth_min = int(_threshold_value(thresholds, "FUT_TOUCH_DEPTH_MIN", DEFAULT_FUT_DEPTH_MIN))

    spread_ratio = _spread_ratio(selected)
    depth_total = _touch_depth(selected)
    stale = _stale(selected)
    crossed_book = _crossed_book(selected)
    queue_reload_veto = _safe_bool(
        _pick(selected, "queue_reload_veto", "ask_reload_veto", "ask_reloaded"),
        False,
    )
    impact_depth_fraction = _impact_depth_fraction(selected, entry_qty)
    impact_max = _threshold_value(thresholds, "IMPACT_DEPTH_FRACTION_MAX", DEFAULT_IMPACT_DEPTH_FRACTION_MAX)

    fut_spread_ratio = _safe_float(_pick(futures_map, "spread_ratio"), 0.0)
    fut_depth_total = _safe_int(_pick(futures_map, "touch_depth", "depth_total"), 0)
    futures_liquidity_pass = (
        futures_present
        and fut_spread_ratio <= fut_spread_ratio_max
        and fut_depth_total >= fut_depth_min
        and not _safe_bool(_pick(futures_map, "stale"), False)
    )

    spread_pass = spread_ratio <= spread_ratio_max
    depth_pass = depth_total >= depth_min
    stale_pass = not stale
    crossed_book_pass = not crossed_book
    queue_pass = not queue_reload_veto
    impact_pass = (
        True
        if impact_depth_fraction is None
        else impact_depth_fraction <= impact_max
    )

    entry_pass = all(
        (
            present,
            futures_present,
            spread_pass,
            depth_pass,
            stale_pass,
            crossed_book_pass,
            queue_pass,
            impact_pass,
            futures_liquidity_pass,
            _normalize_mode(runtime_mode) not in {
                _safe_str(getattr(N, "STRATEGY_RUNTIME_MODE_DISABLED", "DISABLED")).upper(),
                "DISABLED",
            },
        )
    )

    return {
        "present": present,
        "runtime_mode": _normalize_mode(runtime_mode),
        "spread_ratio": spread_ratio,
        "depth_total": depth_total,
        "age_ms": _age_ms(selected),
        "stale": stale,
        "crossed_book": crossed_book,
        "queue_reload_veto": queue_reload_veto,
        "impact_depth_fraction": impact_depth_fraction,
        "spread_ratio_max": spread_ratio_max,
        "depth_min": depth_min,
        "impact_depth_fraction_max": impact_max,
        "futures_present": futures_present,
        "futures_liquidity_pass": futures_liquidity_pass,
        "futures_spread_ratio": fut_spread_ratio,
        "futures_depth_total": fut_depth_total,
        "spread_pass": spread_pass,
        "depth_pass": depth_pass,
        "stale_pass": stale_pass,
        "crossed_book_pass": crossed_book_pass,
        "queue_pass": queue_pass,
        "impact_pass": impact_pass,
        "entry_pass": entry_pass,
        "blocked_reason": (
            ""
            if entry_pass
            else "not_present"
            if not present
            else "futures_unavailable"
            if not futures_present
            else "stale"
            if not stale_pass
            else "crossed_book"
            if not crossed_book_pass
            else "spread"
            if not spread_pass
            else "depth"
            if not depth_pass
            else "queue_reload"
            if not queue_pass
            else "impact"
            if not impact_pass
            else "futures_liquidity"
            if not futures_liquidity_pass
            else "disabled_mode"
        ),
    }


def build_futures_liquidity_surface(
    *,
    futures_surface: Mapping[str, Any] | None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    surface = _as_mapping(_pick(_as_mapping(futures_surface), "selected_features") or futures_surface)

    present = bool(surface) and _safe_bool(_pick(surface, "present"), True)
    spread_ratio = _safe_float(_pick(surface, "spread_ratio"), 0.0)
    depth_total = _safe_int(_pick(surface, "touch_depth", "depth_total"), 0)
    stale = _safe_bool(_pick(surface, "stale"), False) or (_age_ms(surface) > DEFAULT_STALE_THRESHOLD_MS)

    spread_cap = _threshold_value(thresholds, "FUT_SPREAD_MAX", DEFAULT_FUT_SPREAD_RATIO_MAX)
    depth_min = int(_threshold_value(thresholds, "FUT_TOUCH_DEPTH_MIN", DEFAULT_FUT_DEPTH_MIN))

    liquidity_pass = present and (not stale) and spread_ratio <= spread_cap and depth_total >= depth_min

    return {
        "present": present,
        "spread_ratio": spread_ratio,
        "depth_total": depth_total,
        "age_ms": _age_ms(surface),
        "stale": stale,
        "spread_ratio_max": spread_cap,
        "depth_min": depth_min,
        "liquidity_pass": liquidity_pass,
    }


def build_tradability_summary(
    *,
    classic_call: Mapping[str, Any] | None = None,
    classic_put: Mapping[str, Any] | None = None,
    miso_call: Mapping[str, Any] | None = None,
    miso_put: Mapping[str, Any] | None = None,
    futures_liquidity: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    classic_call_m = _as_mapping(classic_call)
    classic_put_m = _as_mapping(classic_put)
    miso_call_m = _as_mapping(miso_call)
    miso_put_m = _as_mapping(miso_put)
    fut_m = _as_mapping(futures_liquidity)

    return {
        "present": bool(classic_call_m or classic_put_m or miso_call_m or miso_put_m),
        "classic_call_entry_pass": _safe_bool(_pick(classic_call_m, "entry_pass"), False),
        "classic_put_entry_pass": _safe_bool(_pick(classic_put_m, "entry_pass"), False),
        "miso_call_entry_pass": _safe_bool(_pick(miso_call_m, "entry_pass"), False),
        "miso_put_entry_pass": _safe_bool(_pick(miso_put_m, "entry_pass"), False),
        "futures_liquidity_pass": _safe_bool(_pick(fut_m, "liquidity_pass"), False),
        "classic_call_blocked_reason": _safe_str(_pick(classic_call_m, "blocked_reason")),
        "classic_put_blocked_reason": _safe_str(_pick(classic_put_m, "blocked_reason")),
        "miso_call_blocked_reason": _safe_str(_pick(miso_call_m, "blocked_reason")),
        "miso_put_blocked_reason": _safe_str(_pick(miso_put_m, "blocked_reason")),
    }
