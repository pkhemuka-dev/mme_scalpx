# R38SK_COMMON_MULTI_WINDOW_MEMORY_ENGINE_V1
"""
Common observe-only multi-window market-memory engine for MME-ScalpX.

Purpose:
- Build one common memory context usable by MIST/MISB/MISC/MISR/MISO.
- Use existing feature-family surfaces when present.
- Stay observe-only: no Redis writes and no paper/live promotion decision.
- Produce quality/context fields that later strategy-family gates can consume.

This module intentionally does not start services or route market activity,
or mutate Redis. It is pure advisory computation over feature payload dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Tuple


R38SK_MARKER = "R38SK_COMMON_MULTI_WINDOW_MEMORY_ENGINE_V1"
R38SKA_SOFT_ADVISORY_MARKER = "R38SKA_SOFT_ADVISORY_MEMORY_HYGIENE_V1"

FAMILIES: Tuple[str, ...] = ("MIST", "MISB", "MISC", "MISR", "MISO")
SIDES: Tuple[str, ...] = ("CALL", "PUT")

WINDOWS: Tuple[str, ...] = ("30s", "1m", "3m", "5m", "15m", "30m")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        return float(value)
    except Exception:
        return default


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "on", "ok", "pass", "passed", "ready", "valid"}


def _safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _norm_abs(value: Any, scale: float) -> float:
    if scale <= 0:
        return 0.0
    return _clamp(abs(_safe_float(value)) / scale)


def _get(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = mapping
    for key in keys:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


def _first_present(mapping: Mapping[str, Any], paths: Iterable[Tuple[str, ...]], default: Any = None) -> Any:
    for path in paths:
        value = _get(mapping, *path, default=None)
        if value not in (None, "", [], {}):
            return value
    return default


def _family_surface_keys(family: str, side: str) -> Tuple[str, ...]:
    fam = family.lower()
    side_l = side.lower()
    side_u = side.upper()
    return (
        f"{fam}_{side_l}",
        f"{family}_{side_u}",
        f"{family}_{side_l}",
        f"{fam}_{side_u}",
    )


def _find_family_surface(payload: Mapping[str, Any], family: str, side: str) -> Mapping[str, Any]:
    for key in _family_surface_keys(family, side):
        surface = payload.get(key)
        if isinstance(surface, Mapping):
            return surface
    branches = payload.get("branches")
    if isinstance(branches, Mapping):
        for key in _family_surface_keys(family, side):
            surface = branches.get(key)
            if isinstance(surface, Mapping):
                return surface
    return {}


def _extract_feature_refs(surface: Mapping[str, Any]) -> Mapping[str, Any]:
    refs = surface.get("feature_refs")
    return refs if isinstance(refs, Mapping) else {}


def _extract_futures_features(surface: Mapping[str, Any]) -> Mapping[str, Any]:
    fut = surface.get("futures_features")
    return fut if isinstance(fut, Mapping) else {}


def _extract_primary_features(surface: Mapping[str, Any]) -> Mapping[str, Any]:
    primary = surface.get("primary_features") or surface.get("selected_features") or surface.get("option_features")
    return primary if isinstance(primary, Mapping) else {}


def _extract_tradability(surface: Mapping[str, Any]) -> Mapping[str, Any]:
    trad = surface.get("tradability") or surface.get("tradability_surface")
    return trad if isinstance(trad, Mapping) else {}


def _extract_oi_summary(surface: Mapping[str, Any]) -> Mapping[str, Any]:
    paths = (
        ("oi_wall_context", "summary"),
        ("strike_surface", "oi_wall_summary"),
        ("ladder_surface", "oi_wall_summary"),
    )
    for path in paths:
        value = _get(surface, *path, default=None)
        if isinstance(value, Mapping):
            return value
    return {}


def _extract_regime(surface: Mapping[str, Any]) -> Mapping[str, Any]:
    regime = surface.get("regime_surface")
    return regime if isinstance(regime, Mapping) else {}


def _side_direction(side: str) -> float:
    return 1.0 if side.upper() == "CALL" else -1.0


def _memory_from_surface(family: str, side: str, surface: Mapping[str, Any]) -> Dict[str, Any]:
    refs = _extract_feature_refs(surface)
    fut = _extract_futures_features(surface)
    opt = _extract_primary_features(surface)
    trad = _extract_tradability(surface)
    oi = _extract_oi_summary(surface)
    regime_s = _extract_regime(surface)

    present = _safe_bool(surface.get("present")) or _safe_bool(surface.get("branch_ready"))
    provider_ready = _safe_bool(surface.get("provider_ready")) or _safe_bool(_get(surface, "runtime_mode_surface", "provider_ready"))
    stale = _safe_bool(surface.get("stale")) or _safe_bool(fut.get("stale")) or _safe_bool(opt.get("stale")) or _safe_bool(trad.get("stale"))

    fut_velocity = _first_present(surface, (
        ("feature_refs", "fut_velocity_ratio"),
        ("futures_features", "velocity_ratio"),
        ("regime_surface", "velocity_ratio"),
    ), 0.0)
    fut_volume_norm = _first_present(surface, (
        ("feature_refs", "fut_volume_norm"),
        ("futures_features", "volume_norm"),
        ("regime_surface", "volume_norm"),
    ), 0.0)
    fut_event_spike = _first_present(surface, (
        ("feature_refs", "fut_event_rate_spike_ratio"),
        ("futures_features", "event_rate_spike_ratio"),
        ("regime_surface", "event_rate_spike_ratio"),
    ), 0.0)
    fut_vwap_distance = _first_present(surface, (
        ("feature_refs", "fut_vwap_distance"),
        ("futures_features", "vwap_distance"),
        ("futures_features", "vwap_distance_ratio"),
    ), 0.0)
    fut_direction = _first_present(surface, (
        ("feature_refs", "fut_direction_score"),
        ("futures_features", "direction_score"),
        ("regime_surface", "direction_score"),
    ), 0.0)
    fut_weighted_ofi = _first_present(surface, (
        ("feature_refs", "fut_weighted_ofi"),
        ("futures_features", "weighted_ofi"),
        ("futures_features", "weighted_ofi_persist"),
    ), 0.0)

    opt_velocity = _first_present(surface, (
        ("feature_refs", "opt_velocity_ratio"),
        ("primary_features", "velocity_ratio"),
        ("selected_features", "velocity_ratio"),
        ("option_features", "velocity_ratio"),
    ), 0.0)
    opt_spread_ratio = _first_present(surface, (
        ("feature_refs", "opt_spread_ratio"),
        ("primary_features", "spread_ratio"),
        ("selected_features", "spread_ratio"),
        ("option_features", "spread_ratio"),
        ("tradability", "spread_ratio"),
        ("tradability_surface", "spread_ratio"),
    ), 0.0)
    opt_response = _first_present(surface, (
        ("feature_refs", "opt_response_efficiency"),
        ("primary_features", "response_efficiency"),
        ("selected_features", "response_efficiency"),
        ("option_features", "response_efficiency"),
        ("tradability", "response_efficiency"),
        ("tradability_surface", "response_efficiency"),
    ), 0.0)

    depth_total = _first_present(surface, (
        ("primary_features", "depth_total"),
        ("selected_features", "depth_total"),
        ("option_features", "depth_total"),
        ("tradability", "depth_total"),
        ("tradability_surface", "depth_total"),
    ), 0.0)

    oi_bias_score = _safe_float(oi.get("oi_bias_score"))
    total_call_oi_change = _safe_float(oi.get("total_call_oi_change"))
    total_put_oi_change = _safe_float(oi.get("total_put_oi_change"))
    oi_wall_ready = _safe_bool(oi.get("oi_wall_ready"))
    near_any_wall = _safe_bool(oi.get("near_any_wall"))

    direction_sign = _side_direction(side)
    direction_alignment_score = _clamp(0.5 + 0.5 * direction_sign * _safe_float(fut_direction))
    ofi_alignment_score = _clamp(0.5 + 0.5 * direction_sign * _safe_float(fut_weighted_ofi))

    freshness_penalty = 0.45 if stale else 0.0
    provider_penalty = 0.35 if not provider_ready else 0.0
    present_penalty = 0.20 if not present else 0.0

    quote_freshness_score = _clamp(1.0 - freshness_penalty - provider_penalty - present_penalty)
    liquidity_score = _clamp(
        0.35 * _clamp(_safe_float(depth_total) / 250.0)
        + 0.35 * _clamp(_safe_float(opt_response) / 0.5)
        + 0.30 * (1.0 - _clamp(_safe_float(opt_spread_ratio) / 2.0))
    )
    volume_quality_score = _clamp(0.55 * _norm_abs(fut_volume_norm, 2.0) + 0.45 * _norm_abs(fut_event_spike, 2.0))
    vwap_context_score = _clamp(1.0 - _norm_abs(fut_vwap_distance, 120.0))
    momentum_score = _clamp(0.45 * _norm_abs(fut_velocity, 2.0) + 0.30 * _norm_abs(opt_velocity, 2.0) + 0.25 * direction_alignment_score)
    oi_alignment_score = _clamp(0.50 + 0.25 * direction_sign * oi_bias_score + 0.25 * _clamp(abs(total_put_oi_change - total_call_oi_change) / 100000.0))
    wall_risk_score = _clamp((0.35 if oi_wall_ready else 0.0) + (0.45 if near_any_wall else 0.0))

    regime = _safe_text(regime_s.get("regime") or surface.get("regime") or "UNKNOWN").upper()
    if regime in {"", "NORMAL"}:
        if _safe_float(fut_event_spike) >= 1.5 or _safe_float(fut_velocity) >= 1.5:
            regime = "FAST"
        elif abs(_safe_float(fut_velocity)) >= 0.7 and volume_quality_score >= 0.35:
            regime = "TREND"
        elif volume_quality_score <= 0.10 and abs(_safe_float(fut_velocity)) <= 0.20:
            regime = "LOWVOL"
        else:
            regime = "NORMAL"

    context_score = _clamp(
        0.18 * quote_freshness_score
        + 0.17 * liquidity_score
        + 0.16 * volume_quality_score
        + 0.14 * momentum_score
        + 0.13 * direction_alignment_score
        + 0.12 * ofi_alignment_score
        + 0.10 * vwap_context_score
        - 0.08 * wall_risk_score
    )

    entry_block_reasons = []
    if not present:
        entry_block_reasons.append("surface_not_present")
    if not provider_ready:
        entry_block_reasons.append("provider_not_ready")
    if stale:
        entry_block_reasons.append("stale_surface")
    if quote_freshness_score < 0.55:
        entry_block_reasons.append("quote_freshness_weak")
    if liquidity_score < 0.35:
        entry_block_reasons.append("liquidity_weak")
    if volume_quality_score < 0.10:
        entry_block_reasons.append("volume_context_weak")
    if context_score < 0.45:
        entry_block_reasons.append("context_score_low")

    if context_score >= 0.68 and not entry_block_reasons:
        entry_quality = "PASS"
    elif context_score >= 0.45:
        entry_quality = "WARN"
    else:
        entry_quality = "FAIL"

    return {
        "memory_context_version": R38SK_MARKER,
        "family_id": family,
        "side": side,
        "observe_only": True,
        "advisory_only": True,
        "hard_gate": False,
        "promotion_decision_owner": "external",
        "live_route_decision_owner": "external",
        "present": present,
        "provider_ready": provider_ready,
        "stale": stale,
        "regime": regime,
        "windows": {
            "30s": {
                "quote_freshness_score": round(quote_freshness_score, 4),
                "spread_shock_risk": round(_clamp(_safe_float(opt_spread_ratio) / 2.0), 4),
                "tape_speed_score": round(_norm_abs(fut_event_spike, 2.0), 4),
            },
            "1m": {
                "micro_momentum_score": round(momentum_score, 4),
                "direction_alignment_score": round(direction_alignment_score, 4),
                "ofi_alignment_score": round(ofi_alignment_score, 4),
            },
            "3m": {
                "entry_timing_score": round(_clamp(0.45 * momentum_score + 0.35 * liquidity_score + 0.20 * quote_freshness_score), 4),
                "fake_spike_risk": round(_clamp(_norm_abs(fut_event_spike, 2.0) * (1.0 - liquidity_score)), 4),
            },
            "5m": {
                "sweep_followthrough_score": round(_clamp(0.45 * momentum_score + 0.35 * volume_quality_score + 0.20 * direction_alignment_score), 4),
                "rejection_risk": round(_clamp((1.0 - direction_alignment_score) * 0.55 + wall_risk_score * 0.45), 4),
            },
            "15m": {
                "volume_quality_score": round(volume_quality_score, 4),
                "oi_alignment_score": round(oi_alignment_score, 4),
                "vwap_context_score": round(vwap_context_score, 4),
                "wall_risk_score": round(wall_risk_score, 4),
                "regime": regime,
            },
            "30m": {
                "day_bias": "CALL" if direction_alignment_score >= 0.60 else "PUT" if direction_alignment_score <= 0.40 else "NEUTRAL",
                "exhaustion_risk": round(_clamp(wall_risk_score * 0.50 + (1.0 - vwap_context_score) * 0.50), 4),
            },
        },
        "scores": {
            "context_score": round(context_score, 4),
            "quote_freshness_score": round(quote_freshness_score, 4),
            "liquidity_score": round(liquidity_score, 4),
            "volume_quality_score": round(volume_quality_score, 4),
            "momentum_score": round(momentum_score, 4),
            "oi_alignment_score": round(oi_alignment_score, 4),
            "vwap_context_score": round(vwap_context_score, 4),
            "wall_risk_score": round(wall_risk_score, 4),
        },
        "entry_quality": entry_quality,
        "entry_block_reasons": entry_block_reasons,
        "entry_block_reason": "|".join(entry_block_reasons),
    }


def build_family_memory_context(payload: Mapping[str, Any], family: str, side: str) -> Dict[str, Any]:
    """Build common observe-only memory context for one strategy family branch."""
    family_u = _safe_text(family).upper()
    side_u = _safe_text(side).upper()
    if family_u not in FAMILIES:
        return {
            "memory_context_version": R38SK_MARKER,
            "family_id": family_u,
            "side": side_u,
            "observe_only": True,
            "advisory_only": True,
        "hard_gate": False,
        "promotion_decision_owner": "external",
            "live_route_decision_owner": "external",
            "entry_quality": "FAIL",
            "entry_block_reason": "unsupported_family",
            "entry_block_reasons": ["unsupported_family"],
        }
    if side_u not in SIDES:
        return {
            "memory_context_version": R38SK_MARKER,
            "family_id": family_u,
            "side": side_u,
            "observe_only": True,
            "advisory_only": True,
        "hard_gate": False,
        "promotion_decision_owner": "external",
            "live_route_decision_owner": "external",
            "entry_quality": "FAIL",
            "entry_block_reason": "unsupported_side",
            "entry_block_reasons": ["unsupported_side"],
        }

    surface = _find_family_surface(payload, family_u, side_u)
    return _memory_from_surface(family_u, side_u, surface)


def build_all_family_memory_context(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Build observe-only memory context for every family/side branch."""
    result: Dict[str, Any] = {
        "memory_context_version": R38SK_MARKER,
        "observe_only": True,
        "advisory_only": True,
        "hard_gate": False,
        "promotion_decision_owner": "external",
        "live_route_decision_owner": "external",
        "families": {},
        "summary": {
            "family_count": len(FAMILIES),
            "branch_count": len(FAMILIES) * len(SIDES),
            "pass_count": 0,
            "warn_count": 0,
            "fail_count": 0,
            "best_family_id": "",
            "best_side": "",
            "best_context_score": 0.0,
        },
    }

    best_score = -1.0
    best_family = ""
    best_side = ""

    for family in FAMILIES:
        result["families"].setdefault(family, {})
        for side in SIDES:
            ctx = build_family_memory_context(payload, family, side)
            result["families"][family][side] = ctx
            quality = ctx.get("entry_quality")
            if quality == "PASS":
                result["summary"]["pass_count"] += 1
            elif quality == "WARN":
                result["summary"]["warn_count"] += 1
            else:
                result["summary"]["fail_count"] += 1
            score = _safe_float(_get(ctx, "scores", "context_score", default=0.0))
            if score > best_score:
                best_score = score
                best_family = family
                best_side = side

    result["summary"]["best_family_id"] = best_family
    result["summary"]["best_side"] = best_side
    result["summary"]["best_context_score"] = round(max(0.0, best_score), 4)
    return result


def attach_memory_context(payload: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Attach observe-only all-family memory context to a mutable payload and return it."""
    payload["multi_window_memory_context"] = build_all_family_memory_context(payload)
    payload["r38sk_memory_attached"] = True
    payload["r38sk_observe_only"] = True
    payload["r38sk_advisory_only"] = True
    payload["r38sk_hard_gate"] = False
    payload["r38sk_promotion_decision_owner"] = "external"
    return payload


__all__ = [
    "R38SK_MARKER",
    "FAMILIES",
    "SIDES",
    "WINDOWS",
    "build_family_memory_context",
    "build_all_family_memory_context",
    "attach_memory_context",
]
