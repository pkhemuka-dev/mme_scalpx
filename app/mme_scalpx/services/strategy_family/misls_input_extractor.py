"""
app/mme_scalpx/services/strategy_family/misls_input_extractor.py

MISLS R5C read-only input extractor.

This module is intentionally:
- pure
- read-only
- dormant
- no wiring
- no Redis
- no broker
- no paper/live
- no risk/execution
- no registry/FAMILY_ORDER/activation change

It only normalizes already-built in-memory feature surfaces into a MISLS input
snapshot that later logger/evaluator tests can consume.
"""

import math
from typing import Any, Mapping


BRANCH_CALL = "CALL"
BRANCH_PUT = "PUT"
SUPPORTED_BRANCHES = (BRANCH_CALL, BRANCH_PUT)

DEFAULT_SOURCE_FAMILIES = ("MISO", "MISR", "MIST", "MISB", "MISC")


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        out = float(str(value).strip())
    except Exception:
        return default
    return out if math.isfinite(out) else default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "pass", "passed", "healthy", "available"}:
        return True
    if text in {"0", "false", "no", "n", "off", "fail", "failed", "none", "null", "unavailable"}:
        return False
    return default


def as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def nested(root: Any, *keys: str, default: Any = None) -> Any:
    cur = root
    for key in keys:
        cur_map = as_mapping(cur)
        if key not in cur_map:
            return default
        cur = cur_map.get(key)
    return cur


def pick(mapping: Mapping[str, Any] | None, *keys: str, default: Any = None) -> Any:
    item = as_mapping(mapping)
    for key in keys:
        if key in item and item.get(key) not in (None, ""):
            return item.get(key)
    return default


def merge_maps(*items: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in items:
        m = as_mapping(item)
        if m:
            out.update(m)
    return out


def normalize_branch(value: Any) -> str | None:
    text = safe_str(value).upper()
    if text in {"CALL", "CE", "C"}:
        return BRANCH_CALL
    if text in {"PUT", "PE", "P"}:
        return BRANCH_PUT
    return None


def opposite_branch(branch_id: str) -> str:
    branch = normalize_branch(branch_id)
    if branch == BRANCH_CALL:
        return BRANCH_PUT
    if branch == BRANCH_PUT:
        return BRANCH_CALL
    raise ValueError(f"unsupported branch_id: {branch_id!r}")


def branch_keys(family_id: str, branch_id: str) -> tuple[str, ...]:
    fam = safe_str(family_id).lower()
    branch = normalize_branch(branch_id) or safe_str(branch_id).upper()
    return (
        f"{fam}_{branch.lower()}",
        f"{safe_str(family_id).upper()}_{branch}",
        f"{safe_str(family_id)}_{branch}",
        branch,
        branch.lower(),
    )


def surface_for_branch(
    family_surfaces: Mapping[str, Any] | None,
    *,
    branch_id: str,
    source_families: tuple[str, ...] = DEFAULT_SOURCE_FAMILIES,
) -> dict[str, Any]:
    fs = as_mapping(family_surfaces)
    by_branch = as_mapping(fs.get("surfaces_by_branch"))

    for family_id in source_families:
        for key in branch_keys(family_id, branch_id):
            surface = as_mapping(by_branch.get(key))
            if surface:
                return surface

    families = as_mapping(fs.get("families"))
    for family_id in source_families:
        fam = as_mapping(families.get(family_id))
        branches = as_mapping(fam.get("branches"))
        for key in (normalize_branch(branch_id), safe_str(branch_id).lower()):
            surface = as_mapping(branches.get(key))
            if surface:
                return surface

    return {}


def quote_snapshot(option: Mapping[str, Any] | None) -> dict[str, Any]:
    opt = as_mapping(option)
    bid = safe_float(pick(opt, "bid", "best_bid", "bid_price"), 0.0)
    ask = safe_float(pick(opt, "ask", "best_ask", "ask_price"), 0.0)
    bid_qty = safe_float(pick(opt, "bid_qty", "bid_qty_5", "best_bid_qty", "top5_bid_qty"), 0.0)
    ask_qty = safe_float(pick(opt, "ask_qty", "ask_qty_5", "best_ask_qty", "top5_ask_qty"), 0.0)
    ltp = safe_float(pick(opt, "ltp", "last_price", "price", "last_traded_price"), 0.0)
    age_ms = safe_float(pick(opt, "age_ms", "quote_age_ms", "selected_option_quote_age_ms"), 0.0)
    spread = safe_float(pick(opt, "spread"), max(0.0, ask - bid) if bid > 0.0 and ask > 0.0 else 0.0)

    return {
        "present": bool(ltp > 0.0 or bid > 0.0 or ask > 0.0),
        "symbol": safe_str(pick(opt, "option_symbol", "trading_symbol", "symbol", "instrument_key", "instrument_token")),
        "instrument_token": safe_str(pick(opt, "instrument_token", "option_token", "token")),
        "ltp": ltp,
        "bid": bid,
        "ask": ask,
        "bid_qty": bid_qty,
        "ask_qty": ask_qty,
        "age_ms": age_ms,
        "spread": spread,
        "spread_ratio": safe_float(pick(opt, "spread_ratio"), 0.0),
        "depth_total": safe_float(pick(opt, "depth_total", "touch_depth"), bid_qty + ask_qty),
        "tradability_ok": safe_bool(pick(opt, "tradability_ok", "entry_pass"), False),
        "depth_ok": safe_bool(pick(opt, "depth_ok"), (bid_qty + ask_qty) > 0.0),
        "response_efficiency": safe_float(pick(opt, "response_efficiency", "option_response_efficiency"), 0.0),
        "velocity_ratio": safe_float(pick(opt, "velocity_ratio", "vel_ratio"), 1.0),
        "weighted_ofi_persist": safe_float(pick(opt, "weighted_ofi_persist", "ofi_persist_score"), 0.0),
        "raw": opt,
    }


def futures_snapshot(futures: Mapping[str, Any] | None) -> dict[str, Any]:
    fut = as_mapping(futures)
    return {
        "present": bool(safe_float(pick(fut, "ltp", "last_price", "price"), 0.0) > 0.0),
        "symbol": safe_str(pick(fut, "trading_symbol", "symbol", "instrument_key", "instrument_token")),
        "ltp": safe_float(pick(fut, "ltp", "last_price", "price"), 0.0),
        "velocity_ratio": safe_float(pick(fut, "velocity_ratio", "vel_ratio"), 1.0),
        "flow_score": safe_float(pick(fut, "flow_score", "futures_flow_score", "weighted_ofi", "ofi_ratio_proxy"), 0.0),
        "ofi_ratio_proxy": safe_float(pick(fut, "ofi_ratio_proxy", "ofi", "nof"), 0.0),
        "delta_3": safe_float(pick(fut, "delta_3", "ltp_delta_3"), 0.0),
        "raw": fut,
    }


def extract_shared_core(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    p = as_mapping(payload)
    return as_mapping(p.get("shared_core")) or as_mapping(nested(p, "family_surfaces", "shared_core", default={}))


def extract_family_features(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    p = as_mapping(payload)
    return as_mapping(p.get("family_features")) or as_mapping(nested(p, "consumer_view", "family_features", default={}))


def extract_family_surfaces(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    p = as_mapping(payload)
    return as_mapping(p.get("family_surfaces")) or as_mapping(nested(p, "consumer_view", "family_surfaces", default={}))


def extract_selected_option(payload: Mapping[str, Any] | None, branch_id: str) -> dict[str, Any]:
    ff = extract_family_features(payload)
    fs = extract_family_surfaces(payload)
    common = as_mapping(ff.get("common"))
    selected_abi = as_mapping(common.get("selected_option"))
    selected_rich = as_mapping(common.get("selected_option_rich"))

    surface = surface_for_branch(fs, branch_id=branch_id)
    surface_selected = merge_maps(
        surface.get("selected_features"),
        surface.get("option_features"),
        surface.get("primary_features"),
    )

    return merge_maps(selected_abi, selected_rich, surface_selected)


def extract_paired_option(payload: Mapping[str, Any] | None, branch_id: str) -> dict[str, Any]:
    fs = extract_family_surfaces(payload)
    pair_branch = opposite_branch(branch_id)
    pair_surface = surface_for_branch(fs, branch_id=pair_branch)
    return merge_maps(
        pair_surface.get("selected_features"),
        pair_surface.get("option_features"),
        pair_surface.get("primary_features"),
    )


def extract_tradability(payload: Mapping[str, Any] | None, branch_id: str) -> dict[str, Any]:
    fs = extract_family_surfaces(payload)
    surface = surface_for_branch(fs, branch_id=branch_id)
    return as_mapping(surface.get("tradability"))


def extract_trap_context(payload: Mapping[str, Any] | None, branch_id: str) -> dict[str, Any]:
    shared = extract_shared_core(payload)
    branch = normalize_branch(branch_id) or safe_str(branch_id).upper()
    branch_key = branch.lower()
    return merge_maps(
        nested(shared, "trap_events", branch, default={}),
        nested(shared, "trap_events", branch_key, default={}),
        nested(shared, "misr", "event_state", branch, default={}),
        nested(shared, "family_state", "MISR", branch, default={}),
    )


def extract_shadow_microstructure(payload: Mapping[str, Any] | None, branch_id: str) -> dict[str, Any]:
    shared = extract_shared_core(payload)
    fs = extract_family_surfaces(payload)
    branch = normalize_branch(branch_id) or safe_str(branch_id).upper()
    branch_key = branch.lower()
    surface = surface_for_branch(fs, branch_id=branch)
    return merge_maps(
        surface.get("shadow_features"),
        nested(shared, "miso_shadow_microstructure", branch, default={}),
        nested(shared, "miso_shadow_microstructure", branch_key, default={}),
        nested(shared, "microstructure", "miso_shadow", branch, default={}),
        nested(shared, "microstructure", "miso_shadow", branch_key, default={}),
        nested(shared, "options", branch_key, "shadow_features", default={}),
    )


def input_quality(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    item = as_mapping(snapshot)
    selected = as_mapping(item.get("selected_option"))
    paired = as_mapping(item.get("paired_option"))
    futures = as_mapping(item.get("futures"))
    trap = as_mapping(item.get("trap_context"))
    shadow = as_mapping(item.get("shadow_microstructure"))
    trad = as_mapping(item.get("tradability"))

    selected_quote_valid = bool(
        safe_float(selected.get("bid"), 0.0) > 0.0
        and safe_float(selected.get("ask"), 0.0) > safe_float(selected.get("bid"), 0.0)
        and safe_float(selected.get("bid_qty"), 0.0) > 0.0
        and safe_float(selected.get("ask_qty"), 0.0) > 0.0
        and safe_float(selected.get("age_ms"), 999999.0) <= 250.0
    )

    paired_quote_valid = bool(
        safe_float(paired.get("bid"), 0.0) > 0.0
        and safe_float(paired.get("ask"), 0.0) > safe_float(paired.get("bid"), 0.0)
        and safe_float(paired.get("bid_qty"), 0.0) > 0.0
        and safe_float(paired.get("ask_qty"), 0.0) > 0.0
    )

    tradability_ok = bool(
        safe_bool(trad.get("entry_pass"), False)
        or safe_bool(trad.get("tradability_ok"), False)
        or safe_bool(selected.get("tradability_ok"), False)
    )

    trap_context_present = bool(trap)
    shadow_context_present = bool(shadow)
    futures_present = bool(futures.get("present") and safe_float(futures.get("ltp"), 0.0) > 0.0)

    return {
        "futures_present": futures_present,
        "selected_quote_valid": selected_quote_valid,
        "paired_quote_valid": paired_quote_valid,
        "tradability_ok": tradability_ok,
        "trap_context_present": trap_context_present,
        "shadow_context_present": shadow_context_present,
        "ready_for_offline_logger_fixture": bool(
            futures_present
            and selected_quote_valid
            and paired_quote_valid
            and tradability_ok
        ),
    }


def extract_misls_read_only_inputs(
    payload: Mapping[str, Any] | None,
    *,
    branch_id: str,
) -> dict[str, Any]:
    branch = normalize_branch(branch_id)
    if branch not in SUPPORTED_BRANCHES:
        raise ValueError(f"unsupported branch_id: {branch_id!r}")

    selected = quote_snapshot(extract_selected_option(payload, branch))
    paired = quote_snapshot(extract_paired_option(payload, branch))
    futures = futures_snapshot(
        nested(extract_family_features(payload), "common", "futures", default={})
        or nested(extract_shared_core(payload), "futures", "active", default={})
        or nested(extract_shared_core(payload), "futures", default={})
    )
    tradability = extract_tradability(payload, branch)
    trap = extract_trap_context(payload, branch)
    shadow = extract_shadow_microstructure(payload, branch)

    snapshot = {
        "schema_version": "misls_r5c_read_only_input_snapshot_v1",
        "family_id": "MISLS",
        "branch_id": branch,
        "side": branch,
        "source_module": "misls_input_extractor",
        "read_only": True,
        "futures": futures,
        "selected_option": selected,
        "paired_option": paired,
        "tradability": tradability,
        "trap_context": trap,
        "shadow_microstructure": shadow,
    }
    snapshot["quality"] = input_quality(snapshot)
    return snapshot


def to_logger_kwargs(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    item = as_mapping(snapshot)
    branch = normalize_branch(item.get("branch_id"))
    selected = as_mapping(item.get("selected_option"))
    paired = as_mapping(item.get("paired_option"))
    futures = as_mapping(item.get("futures"))
    trap = as_mapping(item.get("trap_context"))
    shadow = as_mapping(item.get("shadow_microstructure"))

    return {
        "branch_id": branch,
        "event_ns": int(safe_float(pick(trap, "trap_event_extreme_ts_ns", "fake_break_extreme_ts_ns", "event_ns"), 0.0)) or 0,
        "symbol": safe_str(futures.get("symbol")),
        "option_symbol": safe_str(selected.get("symbol")),
        "shadow_entry_price": safe_float(selected.get("ltp"), 0.0),
        "shadow_entry_underlying_price": safe_float(futures.get("ltp"), 0.0),
        "selected_option_bid_post": safe_float(selected.get("bid"), 0.0),
        "selected_option_ask_post": safe_float(selected.get("ask"), 0.0),
        "selected_option_bid_qty_post": safe_float(selected.get("bid_qty"), 0.0),
        "selected_option_ask_qty_post": safe_float(selected.get("ask_qty"), 0.0),
        "selected_option_quote_age_ms": safe_float(selected.get("age_ms"), 999999.0),
        "paired_option_bid_post": safe_float(paired.get("bid"), 0.0),
        "paired_option_ask_post": safe_float(paired.get("ask"), 0.0),
        "paired_option_bid_qty_post": safe_float(paired.get("bid_qty"), 0.0),
        "paired_option_ask_qty_post": safe_float(paired.get("ask_qty"), 0.0),
        "score": safe_float(pick(shadow, "misls_score", "score", "trap_score"), 0.0),
        "level_type": safe_str(pick(trap, "level_type", "sweep_level_type"), "UNKNOWN"),
        "variant": "R5C_READ_ONLY_INPUT_EXTRACTOR",
    }


__all__ = [
    "extract_misls_read_only_inputs",
    "input_quality",
    "to_logger_kwargs",
    "extract_selected_option",
    "extract_paired_option",
    "extract_tradability",
    "extract_trap_context",
    "extract_shadow_microstructure",
]
# === MISLS_R2A_RESEARCH_INPUT_CONTRACT_APPEND_ONLY ===
# Additive helper block. It only normalizes MISLS research/shadow inputs.
# It does not publish production actions and always returns HOLD.

def _misls_r2a_is_mapping(value):
    return hasattr(value, "get") and hasattr(value, "keys")


def _misls_r2a_first_mapping(*values):
    for value in values:
        if _misls_r2a_is_mapping(value):
            return value
    return {}


def _misls_r2a_get_nested(source, path, default=None):
    cur = source
    for part in path:
        if not _misls_r2a_is_mapping(cur):
            return default
        cur = cur.get(part)
        if cur is None:
            return default
    return cur


def _misls_r2a_float(value, default=None):
    if value is None:
        return default
    try:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return default
        return float(value)
    except Exception:
        return default


def _misls_r2a_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "pass", "ok"}
    return default


def _misls_r2a_first_value(*sources_and_names):
    for source, names in sources_and_names:
        if not _misls_r2a_is_mapping(source):
            continue
        for name in names:
            value = source.get(name)
            if value is not None:
                return value
    return None


def misls_r2a_extract_signal_contract(event):
    """
    Normalize available MISLS research surfaces into one safe shadow contract.

    Output action is always HOLD. This helper is for offline/shadow analysis only.
    """
    if not _misls_r2a_is_mapping(event):
        return {
            "schema": "misls_r2a_signal_contract_v1",
            "family": "MISLS",
            "research_only": True,
            "action": "HOLD",
            "blocker_reasons": ["INPUT_NOT_MAPPING"],
            "quality_score": 0.0,
        }

    direct = event
    metadata = _misls_r2a_first_mapping(event.get("metadata"), event.get("meta"))
    features = _misls_r2a_first_mapping(event.get("features"), event.get("feature"), event.get("feature_row"))
    misls_direct = _misls_r2a_first_mapping(
        event.get("misls"),
        event.get("MISLS"),
        event.get("misls_event"),
        event.get("misls_features"),
        event.get("misls_surface"),
    )
    family_features = _misls_r2a_first_mapping(
        _misls_r2a_get_nested(event, ("family_features", "MISLS")),
        _misls_r2a_get_nested(event, ("family_surfaces", "MISLS")),
        _misls_r2a_get_nested(event, ("families", "MISLS")),
        _misls_r2a_get_nested(metadata, ("MISLS",)),
        _misls_r2a_get_nested(metadata, ("misls",)),
    )

    sources = [misls_direct, family_features, features, metadata, direct]

    def first(names):
        for source in sources:
            value = _misls_r2a_first_value((source, names))
            if value is not None:
                return value
        return None

    ts = first(("ts", "timestamp", "event_ts", "exchange_ts", "created_at"))
    side_raw = first(("side", "option_side", "option_type", "sweep_side", "direction"))
    side = str(side_raw or "").upper()
    if side in {"CE", "CALLS"}:
        side = "CALL"
    if side in {"PE", "PUTS"}:
        side = "PUT"
    if side not in {"CALL", "PUT"}:
        side = "UNKNOWN"

    fut_ltp = _misls_r2a_float(first(("futures_ltp", "future_ltp", "underlying_ltp", "spot_ltp", "ltp", "price")))
    recent_high = _misls_r2a_float(first(("recent_high", "swing_high", "liquidity_high", "shelf_high", "prior_high")))
    recent_low = _misls_r2a_float(first(("recent_low", "swing_low", "liquidity_low", "shelf_low", "prior_low")))
    session_high = _misls_r2a_float(first(("session_high", "day_high")))
    session_low = _misls_r2a_float(first(("session_low", "day_low")))

    high_level = recent_high if recent_high is not None else session_high
    low_level = recent_low if recent_low is not None else session_low

    sweep_side = "NONE"
    sweep_level = None
    if fut_ltp is not None and high_level is not None and fut_ltp >= high_level:
        sweep_side = "HIGH_SWEEP"
        sweep_level = high_level
    if fut_ltp is not None and low_level is not None and fut_ltp <= low_level:
        sweep_side = "LOW_SWEEP"
        sweep_level = low_level

    reclaim_flag = _misls_r2a_bool(first(("reclaim_confirmed", "reject_confirmed", "rejection_confirmed")), False)
    if not reclaim_flag:
        reclaim_hint = str(first(("reclaim_status", "reject_status", "sweep_state", "state")) or "").upper()
        reclaim_flag = reclaim_hint in {"RECLAIM", "REJECT", "CONFIRMED", "RECLAIM_CONFIRMED", "REJECT_CONFIRMED"}

    futures_speed = _misls_r2a_float(first(("futures_speed", "futures_velocity", "micro_futures_velocity", "velocity", "speed")), 0.0)
    futures_delta = _misls_r2a_float(first(("futures_delta", "delta", "delta_3", "micro_delta")), 0.0)
    option_response = _misls_r2a_float(first(("option_response_efficiency", "response_efficiency", "selected_option_response_efficiency")), 0.0)
    spread_ratio = _misls_r2a_float(first(("spread_ratio", "selected_option_spread_ratio", "option_spread_ratio")), None)
    depth_total = _misls_r2a_float(first(("depth_total", "selected_option_depth_total", "bid_ask_depth_total", "depth")), 0.0)
    bid_qty = _misls_r2a_float(first(("bid_qty", "best_bid_qty", "selected_bid_qty")), 0.0)
    ask_qty = _misls_r2a_float(first(("ask_qty", "best_ask_qty", "selected_ask_qty")), 0.0)
    age_ms = _misls_r2a_float(first(("age_ms", "quote_age_ms", "selected_option_age_ms")), None)
    stale = _misls_r2a_bool(first(("stale", "is_stale", "quote_stale")), False)

    blockers = []
    if side == "UNKNOWN":
        blockers.append("SIDE_UNKNOWN")
    if sweep_side == "NONE":
        blockers.append("NO_SWEEP_LEVEL_TOUCH")
    if not reclaim_flag:
        blockers.append("NO_RECLAIM_REJECT_CONFIRMATION")
    if spread_ratio is None:
        blockers.append("SPREAD_RATIO_MISSING")
    elif spread_ratio > 0.012:
        blockers.append("SPREAD_TOO_WIDE")
    if depth_total <= 0 and (bid_qty <= 0 or ask_qty <= 0):
        blockers.append("DEPTH_OR_QUOTE_QTY_MISSING")
    if stale:
        blockers.append("QUOTE_STALE")
    if age_ms is not None and age_ms > 3000:
        blockers.append("QUOTE_TOO_OLD")
    if option_response is not None and option_response < 0:
        blockers.append("OPTION_RESPONSE_NEGATIVE")

    tradability_pass = not any(x in blockers for x in ("SPREAD_TOO_WIDE", "DEPTH_OR_QUOTE_QTY_MISSING", "QUOTE_STALE", "QUOTE_TOO_OLD"))
    sweep_ready = sweep_side != "NONE" and reclaim_flag
    confirmation_score = 0.0
    if sweep_ready:
        confirmation_score += 0.35
    if abs(futures_speed or 0.0) > 0:
        confirmation_score += 0.20
    if abs(futures_delta or 0.0) > 0:
        confirmation_score += 0.15
    if option_response and option_response > 0:
        confirmation_score += 0.15
    if tradability_pass:
        confirmation_score += 0.15

    quality_score = max(0.0, min(1.0, confirmation_score))
    research_candidate = bool(sweep_ready and tradability_pass and quality_score >= 0.50)

    return {
        "schema": "misls_r2a_signal_contract_v1",
        "family": "MISLS",
        "research_only": True,
        "action": "HOLD",
        "timestamp": ts,
        "side": side,
        "sweep_side": sweep_side,
        "sweep_level": sweep_level,
        "recent_high": high_level,
        "recent_low": low_level,
        "futures_ltp": fut_ltp,
        "reclaim_reject_confirmed": bool(reclaim_flag),
        "futures_speed": futures_speed,
        "futures_delta": futures_delta,
        "option_response_efficiency": option_response,
        "spread_ratio": spread_ratio,
        "depth_total": depth_total,
        "bid_qty": bid_qty,
        "ask_qty": ask_qty,
        "quote_age_ms": age_ms,
        "quote_stale": stale,
        "tradability_pass": bool(tradability_pass),
        "research_candidate": research_candidate,
        "quality_score": quality_score,
        "blocker_reasons": blockers,
        "source_surface_present": {
            "direct": bool(direct),
            "metadata": bool(metadata),
            "features": bool(features),
            "misls_direct": bool(misls_direct),
            "family_features": bool(family_features),
        },
    }
# === /MISLS_R2A_RESEARCH_INPUT_CONTRACT_APPEND_ONLY ===
