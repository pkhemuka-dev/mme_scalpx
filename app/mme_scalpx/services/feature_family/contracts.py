from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/contracts.py

Frozen family-facing feature contract surfaces for ScalpX MME.

Purpose
-------
This module OWNS:
- the canonical family_features payload contract consumed by strategy-family
- frozen top-level key surfaces and subtree key surfaces
- family / branch coverage rules
- deterministic scaffold builders for proofs/tests
- thin structural + semantic validators for feature-family publication
- publishable payload guards that prevent placeholder scaffolds from leaking live

This module DOES NOT own:
- Redis reads or writes
- service loops or runtime polling
- provider selection / failover policy
- strategy doctrine logic
- cooldown / proof-window / entry / exit decisions
- feature publication side effects
- market-data normalization
- deep numeric feature computation

Design law
----------
- services/features.py publishes the family_features payload
- services/feature_family/* provides contract + helper surfaces only
- services/strategy_family/* consumes these frozen surfaces
- classic families remain futures-led / option-confirmed
- MISO remains option-led and is not forced into the classic branch shape
- missing data in scaffold builders must be explicit via False / None
- publishable payload validation must reject placeholder scaffold values
- all family and branch identities must anchor to core.names
"""

from types import MappingProxyType
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

# ============================================================================
# Exceptions
# ============================================================================


class FeatureFamilyContractError(ValueError):
    """Raised when the feature-family contract is invalid or internally inconsistent."""


# ============================================================================
# Contract identity
# ============================================================================

FAMILY_FEATURES_VERSION: Final[str] = "1.1"


# Batch 25G contract-registry version. This is a field-name freeze only;
# service adapter behavior is intentionally patched in later batches.
CONTRACT_FIELD_REGISTRY_VERSION: Final[str] = "25G.1"

# ============================================================================
# Canonical vocabularies anchored to names.py
# ============================================================================

FAMILY_ID_MIST: Final[str] = N.STRATEGY_FAMILY_MIST
FAMILY_ID_MISB: Final[str] = N.STRATEGY_FAMILY_MISB
FAMILY_ID_MISC: Final[str] = N.STRATEGY_FAMILY_MISC
FAMILY_ID_MISR: Final[str] = N.STRATEGY_FAMILY_MISR
FAMILY_ID_MISO: Final[str] = N.STRATEGY_FAMILY_MISO

FAMILY_IDS: Final[tuple[str, ...]] = (
    FAMILY_ID_MIST,
    FAMILY_ID_MISB,
    FAMILY_ID_MISC,
    FAMILY_ID_MISR,
    FAMILY_ID_MISO,
)

CLASSIC_FAMILY_IDS: Final[tuple[str, ...]] = (
    FAMILY_ID_MIST,
    FAMILY_ID_MISB,
    FAMILY_ID_MISC,
    FAMILY_ID_MISR,
)

BRANCH_CALL: Final[str] = N.BRANCH_CALL
BRANCH_PUT: Final[str] = N.BRANCH_PUT

BRANCH_IDS: Final[tuple[str, ...]] = (
    BRANCH_CALL,
    BRANCH_PUT,
)

OPTION_SIDE_IDS: Final[tuple[str, ...]] = (
    N.SIDE_CALL,
    N.SIDE_PUT,
)

ALLOWED_PROVIDER_IDS: Final[tuple[str, ...]] = tuple(N.ALLOWED_PROVIDER_IDS)
ALLOWED_PROVIDER_STATUSES: Final[tuple[str, ...]] = tuple(N.ALLOWED_PROVIDER_STATUSES)
ALLOWED_FAMILY_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(N.ALLOWED_FAMILY_RUNTIME_MODES)
ALLOWED_STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = tuple(
    N.ALLOWED_STRATEGY_RUNTIME_MODES
)

CLASSIC_ALLOWED_STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = (
    N.STRATEGY_RUNTIME_MODE_NORMAL,
    N.STRATEGY_RUNTIME_MODE_DHAN_DEGRADED,
    N.STRATEGY_RUNTIME_MODE_DISABLED,
)

MISO_ALLOWED_STRATEGY_RUNTIME_MODES: Final[tuple[str, ...]] = (
    N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
    N.STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED,
    N.STRATEGY_RUNTIME_MODE_DISABLED,
)

REGIME_LOWVOL: Final[str] = "LOWVOL"
REGIME_NORMAL: Final[str] = "NORMAL"
REGIME_FAST: Final[str] = "FAST"

ALLOWED_REGIMES: Final[tuple[str, ...]] = (
    REGIME_LOWVOL,
    REGIME_NORMAL,
    REGIME_FAST,
)

# ============================================================================
# Frozen top-level payload keys
# ============================================================================

KEY_SCHEMA_VERSION: Final[str] = "schema_version"
KEY_SERVICE: Final[str] = "service"
KEY_FAMILY_FEATURES_VERSION: Final[str] = "family_features_version"
KEY_GENERATED_AT_NS: Final[str] = "generated_at_ns"
KEY_SNAPSHOT: Final[str] = "snapshot"
KEY_PROVIDER_RUNTIME: Final[str] = "provider_runtime"
KEY_MARKET: Final[str] = "market"
KEY_COMMON: Final[str] = "common"
KEY_STAGE_FLAGS: Final[str] = "stage_flags"
KEY_FAMILIES: Final[str] = "families"

TOP_LEVEL_KEYS: Final[tuple[str, ...]] = (
    KEY_SCHEMA_VERSION,
    KEY_SERVICE,
    KEY_FAMILY_FEATURES_VERSION,
    KEY_GENERATED_AT_NS,
    KEY_SNAPSHOT,
    KEY_PROVIDER_RUNTIME,
    KEY_MARKET,
    KEY_COMMON,
    KEY_STAGE_FLAGS,
    KEY_FAMILIES,
)

# ============================================================================
# Frozen subtree keys
# ============================================================================

SNAPSHOT_KEYS: Final[tuple[str, ...]] = (
    "valid",
    "validity",
    "sync_ok",
    "freshness_ok",
    "packet_gap_ok",
    "warmup_ok",
    "active_snapshot_ns",
    "futures_snapshot_ns",
    "selected_option_snapshot_ns",
    "dhan_futures_snapshot_ns",
    "dhan_option_snapshot_ns",
    "max_member_age_ms",
    "fut_opt_skew_ms",
    "hard_packet_gap_ms",
    "samples_seen",
)

PROVIDER_RUNTIME_CANONICAL_KEYS: Final[tuple[str, ...]] = tuple(
    N.CONTRACT_PROVIDER_RUNTIME_KEYS
)

PROVIDER_RUNTIME_COMPATIBILITY_KEYS: Final[tuple[str, ...]] = (
    "active_futures_provider_id",
    "active_selected_option_provider_id",
    "active_option_context_provider_id",
    "active_execution_provider_id",
    "fallback_execution_provider_id",
    "provider_runtime_mode",
    "futures_provider_status",
    "selected_option_provider_status",
    "option_context_provider_status",
    "execution_provider_status",
)

PROVIDER_RUNTIME_KEYS: Final[tuple[str, ...]] = tuple(
    dict.fromkeys(
        (
            *PROVIDER_RUNTIME_CANONICAL_KEYS,
            *PROVIDER_RUNTIME_COMPATIBILITY_KEYS,
        )
    )
)


MARKET_KEYS: Final[tuple[str, ...]] = (
    "atm_strike",
    "selected_call_strike",
    "selected_put_strike",
    "active_branch_hint",
    "futures_ltp",
    "call_ltp",
    "put_ltp",
    "selected_option_ltp",
    "premium_floor_ok",
)

COMMON_KEYS: Final[tuple[str, ...]] = (
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals",
)

STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (
    "data_valid",
    "data_quality_ok",
    "session_eligible",
    "warmup_complete",
    "risk_veto_active",
    "reconciliation_lock_active",
    "active_position_present",
    "provider_ready_classic",
    "provider_ready_miso",
    "dhan_context_fresh",
    "selected_option_present",
    "futures_present",
    "call_present",
    "put_present",
)

COMMON_FUTURES_KEYS: Final[tuple[str, ...]] = (
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "top5_bid_qty",
    "top5_ask_qty",
    "ofi_ratio_proxy",
    "ofi_persist_score",
    "microprice",
    "micro_edge",
    "vwap",
    "vwap_dist_pct",
    "ema_9",
    "ema_21",
    "ema9_slope",
    "ema21_slope",
    "delta_3",
    "vel_3",
    "vel_ratio",
    "vol_delta",
    "vol_norm",
    "range_fast",
    "range_slow",
    "range_ratio",
    "above_vwap",
    "below_vwap",
)

COMMON_OPTION_KEYS: Final[tuple[str, ...]] = (
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "top5_bid_qty",
    "top5_ask_qty",
    "ofi_ratio_proxy",
    "microprice",
    "micro_edge",
    "delta_3",
    "response_efficiency",
    "tradability_ok",
    "tick_size",
    "lot_size",
    "strike",
)

COMMON_SELECTED_OPTION_KEYS: Final[tuple[str, ...]] = (
    "side",
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "ofi_ratio_proxy",
    "microprice",
    "micro_edge",
    "delta_3",
    "response_efficiency",
    "tradability_ok",
)

COMMON_CROSS_OPTION_KEYS: Final[tuple[str, ...]] = (
    "call_minus_put_ltp",
    "call_put_depth_ratio",
    "call_put_spread_ratio",
)

COMMON_ECONOMICS_KEYS: Final[tuple[str, ...]] = (
    "premium_floor_ok",
    "target_points",
    "stop_points",
    "target_pct",
    "stop_pct",
    "economic_viability_ok",
)

COMMON_SIGNALS_KEYS: Final[tuple[str, ...]] = (
    "four_pillar_signal",
    "four_pillar_score",
    "delta_proxy_norm",
    "futures_contradiction_flag",
    "queue_reload_veto_flag",
)

MIST_BRANCH_KEYS: Final[tuple[str, ...]] = (
    "trend_confirmed",
    "futures_impulse_ok",
    "pullback_detected",
    "resume_confirmed",
    "context_pass",
    "option_tradability_pass",
)

MISB_BRANCH_KEYS: Final[tuple[str, ...]] = (
    "shelf_confirmed",
    "breakout_triggered",
    "breakout_accepted",
    "context_pass",
    "option_tradability_pass",
)

MISC_BRANCH_KEYS: Final[tuple[str, ...]] = (
    "compression_detected",
    "directional_breakout_triggered",
    "expansion_accepted",
    "retest_monitor_active",
    "retest_valid",
    "hesitation_valid",
    "resume_confirmed",
    "context_pass",
    "option_tradability_pass",
)

MISR_ACTIVE_ZONE_KEYS: Final[tuple[str, ...]] = (
    "zone_id",
    "zone_type",
    "zone_level",
    "zone_low",
    "zone_high",
    "quality_score",
    "expires_ts_ns",
)

MISR_BRANCH_KEYS: Final[tuple[str, ...]] = (
    "active_zone_valid",
    "fake_break_triggered",
    "absorption_pass",
    "range_reentry_confirmed",
    "flow_flip_confirmed",
    "hold_inside_range_proved",
    "no_mans_land_cleared",
    "reversal_impulse_confirmed",
    "context_pass",
    "option_tradability_pass",
)

MISO_ROOT_KEYS: Final[tuple[str, ...]] = (
    "eligible",
    "mode",
    "chain_context_ready",
    "selected_side",
    "selected_strike",
    "shadow_call_strike",
    "shadow_put_strike",
    "call_support",
    "put_support",
)

MISO_SIDE_SUPPORT_KEYS: Final[tuple[str, ...]] = (
    "burst_detected",
    "aggression_ok",
    "tape_speed_ok",
    "imbalance_persist_ok",
    "queue_reload_blocked",
    "futures_vwap_align_ok",
    "futures_contradiction_blocked",
    "tradability_pass",
)


# Batch 25M: canonical support alias and eligibility registry.
# These are contract bridge aliases only. New producers should publish canonical
# keys directly after Batch 25M.
FAMILY_SUPPORT_ALIAS_MAP: Final[Mapping[str, Mapping[str, tuple[str, ...]]]] = MappingProxyType(
    {
        FAMILY_ID_MIST: MappingProxyType(
            {
                "trend_confirmed": ("trend_confirmed", "futures_bias_ok", "trend_direction_ok", "trend_ok"),
                "futures_impulse_ok": ("futures_impulse_ok", "impulse_ok", "futures_ok"),
                "pullback_detected": ("pullback_detected", "pullback_ok", "pullback_present"),
                "micro_trap_resolved": ("micro_trap_resolved", "micro_trap_clear", "micro_trap_blocked"),
                "resume_confirmed": ("resume_confirmed", "resume_support", "resume_confirmation_ok"),
                "context_pass": ("context_pass", "oi_context_pass"),
                "option_tradability_pass": ("option_tradability_pass", "tradability_pass", "option_tradability_ok"),
            }
        ),
        FAMILY_ID_MISB: MappingProxyType(
            {
                "shelf_confirmed": ("shelf_confirmed", "shelf_valid", "shelf_ok", "shelf_score_ok"),
                "breakout_triggered": ("breakout_triggered", "breakout_trigger", "breakout_trigger_ok"),
                "breakout_accepted": ("breakout_accepted", "breakout_acceptance", "breakout_acceptance_ok"),
                "context_pass": ("context_pass", "oi_context_pass"),
                "option_tradability_pass": ("option_tradability_pass", "tradability_pass", "option_tradability_ok"),
            }
        ),
        FAMILY_ID_MISC: MappingProxyType(
            {
                "compression_detected": ("compression_detected", "compression_detection", "compression_ok"),
                "directional_breakout_triggered": ("directional_breakout_triggered", "breakout_trigger", "breakout_triggered"),
                "expansion_accepted": ("expansion_accepted", "breakout_acceptance", "expansion_acceptance_ok"),
                "retest_monitor_active": ("retest_monitor_active", "retest_monitor_alive"),
                "retest_valid": ("retest_valid", "retest_ok"),
                "hesitation_valid": ("hesitation_valid", "hesitation_ok"),
                "resume_confirmed": ("resume_confirmed", "resume_support", "resume_confirmation_ok"),
                "context_pass": ("context_pass", "oi_context_pass"),
                "option_tradability_pass": ("option_tradability_pass", "tradability_pass", "option_tradability_ok"),
            }
        ),
        FAMILY_ID_MISR: MappingProxyType(
            {
                "active_zone_valid": ("active_zone_valid", "zone_valid", "active_zone_ready"),
                "active_zone": ("active_zone",),
                "trap_event_id": ("trap_event_id",),
                "fake_break_triggered": ("fake_break_triggered", "fake_break", "trap_detected", "fake_break_detected"),
                "absorption_pass": ("absorption_pass", "absorption", "absorption_ok", "absorption_confirmed"),
                "range_reentry_confirmed": ("range_reentry_confirmed", "range_reentry", "reentry_ok"),
                "flow_flip_confirmed": ("flow_flip_confirmed", "flow_flip", "flow_flip_ok"),
                "hold_inside_range_proved": ("hold_inside_range_proved", "hold_proof", "hold_proof_ok"),
                "no_mans_land_cleared": ("no_mans_land_cleared", "no_mans_land_clear"),
                "reversal_impulse_confirmed": ("reversal_impulse_confirmed", "reversal_impulse", "reversal_impulse_ok"),
                "context_pass": ("context_pass", "oi_context_pass"),
                "option_tradability_pass": ("option_tradability_pass", "tradability_pass", "option_tradability_ok"),
            }
        ),
        FAMILY_ID_MISO: MappingProxyType(
            {
                "burst_detected": ("burst_detected", "burst_valid"),
                "aggression_ok": ("aggression_ok", "aggressive_flow"),
                "tape_speed_ok": ("tape_speed_ok", "tape_urgency_ok", "tape_speed_pass"),
                "imbalance_persist_ok": ("imbalance_persist_ok", "persistence_ok", "imbalance_persistence_ok"),
                "queue_reload_blocked": ("queue_reload_blocked", "queue_reload_veto"),
                "queue_reload_clear": ("queue_ok", "queue_clear", "queue_reload_clear"),
                "futures_vwap_align_ok": ("futures_vwap_align_ok", "futures_alignment_ok", "futures_vwap_alignment_ok"),
                "futures_contradiction_blocked": ("futures_contradiction_blocked", "futures_contradiction_veto"),
                "tradability_pass": ("tradability_pass", "option_tradability_pass", "option_tradability_ok"),
            }
        ),
    }
)

FAMILY_SUPPORT_INVERTED_ALIAS_MAP: Final[Mapping[str, Mapping[str, tuple[str, ...]]]] = MappingProxyType(
    {
        FAMILY_ID_MISO: MappingProxyType(
            {
                "queue_reload_blocked": ("queue_ok",),
                "futures_contradiction_blocked": ("futures_veto_clear",),
            }
        )
    }
)

FAMILY_BRANCH_ELIGIBILITY_KEYS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        FAMILY_ID_MIST: (
            "trend_confirmed",
            "futures_impulse_ok",
            "pullback_detected",
            "micro_trap_resolved",
            "resume_confirmed",
            "option_tradability_pass",
        ),
        FAMILY_ID_MISB: (
            "shelf_confirmed",
            "breakout_triggered",
            "breakout_accepted",
            "option_tradability_pass",
        ),
        FAMILY_ID_MISC: (
            "compression_detected",
            "directional_breakout_triggered",
            "expansion_accepted",
            "retest_monitor_active",
            "resume_confirmed",
            "option_tradability_pass",
        ),
        FAMILY_ID_MISR: (
            "active_zone_valid",
            "fake_break_triggered",
            "absorption_pass",
            "range_reentry_confirmed",
            "flow_flip_confirmed",
            "hold_inside_range_proved",
            "no_mans_land_cleared",
            "reversal_impulse_confirmed",
            "option_tradability_pass",
        ),
        FAMILY_ID_MISO: (
            "burst_detected",
            "aggression_ok",
            "tape_speed_ok",
            "imbalance_persist_ok",
            "tradability_pass",
        ),
    }
)


# Canonical cross-service field registry anchored to core.names. Existing payload
# validators above remain unchanged in Batch 25G to avoid mixing contract freeze
# with live service behavior. Runtime adapters are repaired in subsequent batches.
CANONICAL_PROVIDER_RUNTIME_KEYS: Final[tuple[str, ...]] = tuple(N.CONTRACT_PROVIDER_RUNTIME_KEYS)
CANONICAL_FEED_SNAPSHOT_KEYS: Final[tuple[str, ...]] = tuple(N.CONTRACT_FEED_SNAPSHOT_KEYS)
CANONICAL_DHAN_CONTEXT_KEYS: Final[tuple[str, ...]] = tuple(N.CONTRACT_DHAN_CONTEXT_KEYS)
CANONICAL_FAMILY_SUPPORT_KEYS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {family_id: tuple(keys) for family_id, keys in N.CONTRACT_FAMILY_SUPPORT_KEYS.items()}
)
CANONICAL_EXECUTION_ENTRY_TOP_LEVEL_KEYS: Final[tuple[str, ...]] = tuple(
    N.CONTRACT_EXECUTION_ENTRY_TOP_LEVEL_KEYS
)
CANONICAL_EXECUTION_ENTRY_METADATA_KEYS: Final[tuple[str, ...]] = tuple(
    N.CONTRACT_EXECUTION_ENTRY_METADATA_KEYS
)
CANONICAL_EXECUTION_ENTRY_KEYS: Final[tuple[str, ...]] = tuple(N.CONTRACT_EXECUTION_ENTRY_KEYS)
CANONICAL_CONTRACT_FIELD_REGISTRY: Final[Mapping[str, tuple[str, ...] | Mapping[str, tuple[str, ...]]]] = MappingProxyType(
    {
        "provider_runtime": CANONICAL_PROVIDER_RUNTIME_KEYS,
        "feed_snapshot": CANONICAL_FEED_SNAPSHOT_KEYS,
        "dhan_context": CANONICAL_DHAN_CONTEXT_KEYS,
        "family_support": CANONICAL_FAMILY_SUPPORT_KEYS,
        "execution_entry_top_level": CANONICAL_EXECUTION_ENTRY_TOP_LEVEL_KEYS,
        "execution_entry_metadata": CANONICAL_EXECUTION_ENTRY_METADATA_KEYS,
        "execution_entry": CANONICAL_EXECUTION_ENTRY_KEYS,
    }
)
CANONICAL_FIELD_COMPATIBILITY_ALIASES: Final[Mapping[str, str]] = MappingProxyType(
    dict(N.CONTRACT_FIELD_COMPATIBILITY_ALIASES)
)

# ============================================================================
# Internal validation helpers
# ============================================================================


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FeatureFamilyContractError(message)


def _require_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise FeatureFamilyContractError(f"{field_name} must be bool")
    return value


def _require_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise FeatureFamilyContractError(f"{field_name} must be str")
    cleaned = value.strip()
    if not cleaned:
        raise FeatureFamilyContractError(f"{field_name} must be non-empty str")
    return cleaned


def _require_int(value: Any, *, field_name: str, min_value: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise FeatureFamilyContractError(f"{field_name} must be int")
    if min_value is not None and value < min_value:
        raise FeatureFamilyContractError(
            f"{field_name} must be >= {min_value}, got {value}"
        )
    return value


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FeatureFamilyContractError(f"{field_name} must be a mapping")
    return value


def _require_optional_literal(
    value: Any,
    *,
    field_name: str,
    allowed: tuple[str, ...],
) -> str | None:
    if value is None:
        return None
    text = _require_str(value, field_name=field_name)
    if text not in allowed:
        raise FeatureFamilyContractError(
            f"{field_name} must be one of {allowed!r} or None, got {text!r}"
        )
    return text


def _require_literal(
    value: Any,
    *,
    field_name: str,
    allowed: tuple[str, ...],
) -> str:
    text = _require_str(value, field_name=field_name)
    if text not in allowed:
        raise FeatureFamilyContractError(
            f"{field_name} must be one of {allowed!r}, got {text!r}"
        )
    return text


def _require_optional_non_empty_str(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_str(value, field_name=field_name)


def _require_exact_keys(
    mapping: Mapping[str, Any],
    *,
    required_keys: tuple[str, ...],
    field_name: str,
) -> None:
    actual = tuple(mapping.keys())
    expected = tuple(required_keys)
    if actual != expected:
        raise FeatureFamilyContractError(
            f"{field_name} keys mismatch. expected={expected!r} actual={actual!r}"
        )


def _validate_family_identities() -> None:
    _require(
        FAMILY_IDS == ("MIST", "MISB", "MISC", "MISR", "MISO"),
        f"Unexpected family identities anchored from names.py: {FAMILY_IDS!r}",
    )
    _require(
        BRANCH_IDS == ("CALL", "PUT"),
        f"Unexpected branch identities anchored from names.py: {BRANCH_IDS!r}",
    )


def _validate_bool_mapping_fields(
    mapping: Mapping[str, Any],
    *,
    field_name: str,
    bool_keys: tuple[str, ...],
) -> None:
    for key in bool_keys:
        _require_bool(mapping[key], field_name=f"{field_name}.{key}")


# ============================================================================
# Deterministic scaffold builders
# ============================================================================


def build_empty_snapshot_block() -> dict[str, Any]:
    return {
        "valid": False,
        "validity": "UNAVAILABLE",
        "sync_ok": False,
        "freshness_ok": False,
        "packet_gap_ok": False,
        "warmup_ok": False,
        "active_snapshot_ns": None,
        "futures_snapshot_ns": None,
        "selected_option_snapshot_ns": None,
        "dhan_futures_snapshot_ns": None,
        "dhan_option_snapshot_ns": None,
        "max_member_age_ms": None,
        "fut_opt_skew_ms": None,
        "hard_packet_gap_ms": None,
        "samples_seen": 0,
    }


def build_empty_provider_runtime_block() -> dict[str, Any]:
    return {
        # Canonical Batch 25G provider-runtime keys.
        "futures_marketdata_provider_id": None,
        "selected_option_marketdata_provider_id": None,
        "option_context_provider_id": None,
        "execution_primary_provider_id": None,
        "execution_fallback_provider_id": None,
        "futures_marketdata_status": None,
        "selected_option_marketdata_status": None,
        "option_context_status": None,
        "execution_primary_status": None,
        "execution_fallback_status": None,
        "family_runtime_mode": N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        "failover_mode": N.PROVIDER_FAILOVER_MODE_MANUAL,
        "override_mode": N.PROVIDER_OVERRIDE_MODE_AUTO,
        "transition_reason": N.PROVIDER_TRANSITION_REASON_BOOTSTRAP,
        "provider_transition_seq": 0,
        "failover_active": False,
        "pending_failover": False,

        # Compatibility keys consumed by existing strategy-family surfaces.
        "active_futures_provider_id": None,
        "active_selected_option_provider_id": None,
        "active_option_context_provider_id": None,
        "active_execution_provider_id": None,
        "fallback_execution_provider_id": None,
        "provider_runtime_mode": None,
        "futures_provider_status": None,
        "selected_option_provider_status": None,
        "option_context_provider_status": None,
        "execution_provider_status": None,
    }


def build_empty_market_block() -> dict[str, Any]:
    return {
        "atm_strike": None,
        "selected_call_strike": None,
        "selected_put_strike": None,
        "active_branch_hint": None,
        "futures_ltp": None,
        "call_ltp": None,
        "put_ltp": None,
        "selected_option_ltp": None,
        "premium_floor_ok": False,
    }


def build_empty_common_futures_block() -> dict[str, Any]:
    return {
        "ltp": None,
        "spread": None,
        "spread_ratio": None,
        "depth_total": None,
        "depth_ok": False,
        "top5_bid_qty": None,
        "top5_ask_qty": None,
        "ofi_ratio_proxy": None,
        "ofi_persist_score": None,
        "microprice": None,
        "micro_edge": None,
        "vwap": None,
        "vwap_dist_pct": None,
        "ema_9": None,
        "ema_21": None,
        "ema9_slope": None,
        "ema21_slope": None,
        "delta_3": None,
        "vel_3": None,
        "vel_ratio": None,
        "vol_delta": None,
        "vol_norm": None,
        "range_fast": None,
        "range_slow": None,
        "range_ratio": None,
        "above_vwap": None,
        "below_vwap": None,
    }


def build_empty_common_option_block() -> dict[str, Any]:
    return {
        "ltp": None,
        "spread": None,
        "spread_ratio": None,
        "depth_total": None,
        "depth_ok": False,
        "top5_bid_qty": None,
        "top5_ask_qty": None,
        "ofi_ratio_proxy": None,
        "microprice": None,
        "micro_edge": None,
        "delta_3": None,
        "response_efficiency": None,
        "tradability_ok": False,
        "tick_size": None,
        "lot_size": None,
        "strike": None,
    }


def build_empty_selected_option_block() -> dict[str, Any]:
    return {
        "side": None,
        "ltp": None,
        "spread": None,
        "spread_ratio": None,
        "depth_total": None,
        "depth_ok": False,
        "ofi_ratio_proxy": None,
        "microprice": None,
        "micro_edge": None,
        "delta_3": None,
        "response_efficiency": None,
        "tradability_ok": False,
    }


def build_empty_cross_option_block() -> dict[str, Any]:
    return {
        "call_minus_put_ltp": None,
        "call_put_depth_ratio": None,
        "call_put_spread_ratio": None,
    }


def build_empty_economics_block() -> dict[str, Any]:
    return {
        "premium_floor_ok": False,
        "target_points": None,
        "stop_points": None,
        "target_pct": None,
        "stop_pct": None,
        "economic_viability_ok": False,
    }


def build_empty_signals_block() -> dict[str, Any]:
    return {
        "four_pillar_signal": None,
        "four_pillar_score": None,
        "delta_proxy_norm": None,
        "futures_contradiction_flag": False,
        "queue_reload_veto_flag": False,
    }


def build_empty_common_block() -> dict[str, Any]:
    return {
        "regime": "",
        "strategy_runtime_mode_classic": None,
        "strategy_runtime_mode_miso": None,
        "futures": build_empty_common_futures_block(),
        "call": build_empty_common_option_block(),
        "put": build_empty_common_option_block(),
        "selected_option": build_empty_selected_option_block(),
        "cross_option": build_empty_cross_option_block(),
        "economics": build_empty_economics_block(),
        "signals": build_empty_signals_block(),
    }


def build_empty_stage_flags_block() -> dict[str, Any]:
    return {
        "data_valid": False,
        "data_quality_ok": False,
        "session_eligible": False,
        "warmup_complete": False,
        "risk_veto_active": False,
        "reconciliation_lock_active": False,
        "active_position_present": False,
        "provider_ready_classic": False,
        "provider_ready_miso": False,
        "dhan_context_fresh": False,
        "selected_option_present": False,
        "futures_present": False,
        "call_present": False,
        "put_present": False,
    }


def build_empty_mist_branch_support() -> dict[str, Any]:
    return {
        "trend_confirmed": False,
        "futures_impulse_ok": False,
        "pullback_detected": False,
        "resume_confirmed": False,
        "context_pass": False,
        "option_tradability_pass": False,
    }


def build_empty_misb_branch_support() -> dict[str, Any]:
    return {
        "shelf_confirmed": False,
        "breakout_triggered": False,
        "breakout_accepted": False,
        "context_pass": False,
        "option_tradability_pass": False,
    }


def build_empty_misc_branch_support() -> dict[str, Any]:
    return {
        "compression_detected": False,
        "directional_breakout_triggered": False,
        "expansion_accepted": False,
        "retest_monitor_active": False,
        "retest_valid": False,
        "hesitation_valid": False,
        "resume_confirmed": False,
        "context_pass": False,
        "option_tradability_pass": False,
    }


def build_empty_misr_active_zone() -> dict[str, Any]:
    return {
        "zone_id": None,
        "zone_type": None,
        "zone_level": None,
        "zone_low": None,
        "zone_high": None,
        "quality_score": None,
        "expires_ts_ns": None,
    }


def build_empty_misr_branch_support() -> dict[str, Any]:
    return {
        "active_zone_valid": False,
        "fake_break_triggered": False,
        "absorption_pass": False,
        "range_reentry_confirmed": False,
        "flow_flip_confirmed": False,
        "hold_inside_range_proved": False,
        "no_mans_land_cleared": False,
        "reversal_impulse_confirmed": False,
        "context_pass": False,
        "option_tradability_pass": False,
    }


def build_empty_miso_side_support() -> dict[str, Any]:
    return {
        "burst_detected": False,
        "aggression_ok": False,
        "tape_speed_ok": False,
        "imbalance_persist_ok": False,
        "queue_reload_blocked": False,
        "futures_vwap_align_ok": False,
        "futures_contradiction_blocked": False,
        "tradability_pass": False,
    }


def build_empty_mist_family_support() -> dict[str, Any]:
    return {
        "eligible": False,
        "branches": {
            BRANCH_CALL: build_empty_mist_branch_support(),
            BRANCH_PUT: build_empty_mist_branch_support(),
        },
    }


def build_empty_misb_family_support() -> dict[str, Any]:
    return {
        "eligible": False,
        "branches": {
            BRANCH_CALL: build_empty_misb_branch_support(),
            BRANCH_PUT: build_empty_misb_branch_support(),
        },
    }


def build_empty_misc_family_support() -> dict[str, Any]:
    return {
        "eligible": False,
        "branches": {
            BRANCH_CALL: build_empty_misc_branch_support(),
            BRANCH_PUT: build_empty_misc_branch_support(),
        },
    }


def build_empty_misr_family_support() -> dict[str, Any]:
    return {
        "eligible": False,
        "active_zone": build_empty_misr_active_zone(),
        "branches": {
            BRANCH_CALL: build_empty_misr_branch_support(),
            BRANCH_PUT: build_empty_misr_branch_support(),
        },
    }


def build_empty_miso_family_support() -> dict[str, Any]:
    return {
        "eligible": False,
        "mode": None,
        "chain_context_ready": False,
        "selected_side": None,
        "selected_strike": None,
        "shadow_call_strike": None,
        "shadow_put_strike": None,
        "call_support": build_empty_miso_side_support(),
        "put_support": build_empty_miso_side_support(),
    }


def build_empty_families_block() -> dict[str, Any]:
    return {
        FAMILY_ID_MIST: build_empty_mist_family_support(),
        FAMILY_ID_MISB: build_empty_misb_family_support(),
        FAMILY_ID_MISC: build_empty_misc_family_support(),
        FAMILY_ID_MISR: build_empty_misr_family_support(),
        FAMILY_ID_MISO: build_empty_miso_family_support(),
    }


def build_empty_family_features_payload(
    *,
    schema_version: int = N.DEFAULT_SCHEMA_VERSION,
    service: str = N.SERVICE_FEATURES,
    family_features_version: str = FAMILY_FEATURES_VERSION,
    generated_at_ns: int = 0,
) -> dict[str, Any]:
    """
    Scaffold-safe builder for proofs/tests.

    This builder is intentionally not publishable by default because provider/runtime
    fields may remain None. Use validate_publishable_family_features_payload() to
    guard runtime publication.
    """
    return {
        "schema_version": schema_version,
        "service": service,
        "family_features_version": family_features_version,
        "generated_at_ns": generated_at_ns,
        "snapshot": build_empty_snapshot_block(),
        "provider_runtime": build_empty_provider_runtime_block(),
        "market": build_empty_market_block(),
        "common": build_empty_common_block(),
        "stage_flags": build_empty_stage_flags_block(),
        "families": build_empty_families_block(),
    }


# ============================================================================
# Validators
# ============================================================================


def validate_snapshot_block(snapshot: Mapping[str, Any]) -> None:
    _require_exact_keys(snapshot, required_keys=SNAPSHOT_KEYS, field_name="snapshot")
    for key in ("valid", "sync_ok", "freshness_ok", "packet_gap_ok", "warmup_ok"):
        _require_bool(snapshot[key], field_name=f"snapshot.{key}")
    _require_int(snapshot["samples_seen"], field_name="snapshot.samples_seen", min_value=0)


def validate_provider_runtime_block(
    provider_runtime: Mapping[str, Any],
    *,
    publishable: bool = False,
) -> None:
    _require_exact_keys(
        provider_runtime,
        required_keys=PROVIDER_RUNTIME_KEYS,
        field_name="provider_runtime",
    )

    canonical_provider_fields = (
        "futures_marketdata_provider_id",
        "selected_option_marketdata_provider_id",
        "option_context_provider_id",
        "execution_primary_provider_id",
        "execution_fallback_provider_id",
    )
    compatibility_provider_fields = (
        "active_futures_provider_id",
        "active_selected_option_provider_id",
        "active_option_context_provider_id",
        "active_execution_provider_id",
        "fallback_execution_provider_id",
    )
    canonical_status_fields = (
        "futures_marketdata_status",
        "selected_option_marketdata_status",
        "option_context_status",
        "execution_primary_status",
        "execution_fallback_status",
    )
    compatibility_status_fields = (
        "futures_provider_status",
        "selected_option_provider_status",
        "option_context_provider_status",
        "execution_provider_status",
    )

    for field_name in canonical_provider_fields + compatibility_provider_fields:
        value = provider_runtime[field_name]
        if publishable and field_name in (
            "futures_marketdata_provider_id",
            "selected_option_marketdata_provider_id",
            "active_futures_provider_id",
            "active_selected_option_provider_id",
        ):
            _require_literal(
                value,
                field_name=f"provider_runtime.{field_name}",
                allowed=ALLOWED_PROVIDER_IDS,
            )
        else:
            _require_optional_literal(
                value,
                field_name=f"provider_runtime.{field_name}",
                allowed=ALLOWED_PROVIDER_IDS,
            )

    for field_name in canonical_status_fields + compatibility_status_fields:
        value = provider_runtime[field_name]
        if publishable and field_name in (
            "futures_marketdata_status",
            "selected_option_marketdata_status",
            "futures_provider_status",
            "selected_option_provider_status",
        ):
            _require_literal(
                value,
                field_name=f"provider_runtime.{field_name}",
                allowed=ALLOWED_PROVIDER_STATUSES,
            )
        else:
            _require_optional_literal(
                value,
                field_name=f"provider_runtime.{field_name}",
                allowed=ALLOWED_PROVIDER_STATUSES,
            )

    if publishable:
        _require_literal(
            provider_runtime["family_runtime_mode"],
            field_name="provider_runtime.family_runtime_mode",
            allowed=ALLOWED_FAMILY_RUNTIME_MODES,
        )
    else:
        _require_optional_literal(
            provider_runtime["family_runtime_mode"],
            field_name="provider_runtime.family_runtime_mode",
            allowed=ALLOWED_FAMILY_RUNTIME_MODES,
        )

    _require_optional_non_empty_str(
        provider_runtime["provider_runtime_mode"],
        field_name="provider_runtime.provider_runtime_mode",
    )

    _require_literal(
        provider_runtime["failover_mode"],
        field_name="provider_runtime.failover_mode",
        allowed=N.ALLOWED_PROVIDER_FAILOVER_MODES,
    )
    _require_literal(
        provider_runtime["override_mode"],
        field_name="provider_runtime.override_mode",
        allowed=N.ALLOWED_PROVIDER_OVERRIDE_MODES,
    )
    _require_literal(
        provider_runtime["transition_reason"],
        field_name="provider_runtime.transition_reason",
        allowed=N.ALLOWED_PROVIDER_TRANSITION_REASONS,
    )
    _require_int(
        provider_runtime["provider_transition_seq"],
        field_name="provider_runtime.provider_transition_seq",
        min_value=0,
    )
    _require_bool(
        provider_runtime["failover_active"],
        field_name="provider_runtime.failover_active",
    )
    _require_bool(
        provider_runtime["pending_failover"],
        field_name="provider_runtime.pending_failover",
    )

    # Compatibility value-equivalence guards. These catch producer/consumer drift.
    equivalence_pairs = (
        ("futures_marketdata_provider_id", "active_futures_provider_id"),
        ("selected_option_marketdata_provider_id", "active_selected_option_provider_id"),
        ("option_context_provider_id", "active_option_context_provider_id"),
        ("execution_primary_provider_id", "active_execution_provider_id"),
        ("execution_fallback_provider_id", "fallback_execution_provider_id"),
        ("futures_marketdata_status", "futures_provider_status"),
        ("selected_option_marketdata_status", "selected_option_provider_status"),
        ("option_context_status", "option_context_provider_status"),
        ("execution_primary_status", "execution_provider_status"),
    )
    for canonical_key, compatibility_key in equivalence_pairs:
        canonical_value = provider_runtime[canonical_key]
        compatibility_value = provider_runtime[compatibility_key]
        if canonical_value is not None or compatibility_value is not None:
            _require(
                canonical_value == compatibility_value,
                "provider_runtime compatibility drift: "
                f"{canonical_key}={canonical_value!r} "
                f"{compatibility_key}={compatibility_value!r}",
            )


def validate_market_block(market: Mapping[str, Any]) -> None:
    _require_exact_keys(market, required_keys=MARKET_KEYS, field_name="market")
    _require_bool(market["premium_floor_ok"], field_name="market.premium_floor_ok")
    _require_optional_literal(
        market["active_branch_hint"],
        field_name="market.active_branch_hint",
        allowed=BRANCH_IDS,
    )


def validate_common_block(common: Mapping[str, Any]) -> None:
    _require_exact_keys(common, required_keys=COMMON_KEYS, field_name="common")

    futures = _require_mapping(common["futures"], field_name="common.futures")
    call = _require_mapping(common["call"], field_name="common.call")
    put = _require_mapping(common["put"], field_name="common.put")
    selected_option = _require_mapping(
        common["selected_option"],
        field_name="common.selected_option",
    )
    cross_option = _require_mapping(
        common["cross_option"],
        field_name="common.cross_option",
    )
    economics = _require_mapping(common["economics"], field_name="common.economics")
    signals = _require_mapping(common["signals"], field_name="common.signals")

    _require_exact_keys(
        futures,
        required_keys=COMMON_FUTURES_KEYS,
        field_name="common.futures",
    )
    _require_exact_keys(
        call,
        required_keys=COMMON_OPTION_KEYS,
        field_name="common.call",
    )
    _require_exact_keys(
        put,
        required_keys=COMMON_OPTION_KEYS,
        field_name="common.put",
    )
    _require_exact_keys(
        selected_option,
        required_keys=COMMON_SELECTED_OPTION_KEYS,
        field_name="common.selected_option",
    )
    _require_exact_keys(
        cross_option,
        required_keys=COMMON_CROSS_OPTION_KEYS,
        field_name="common.cross_option",
    )
    _require_exact_keys(
        economics,
        required_keys=COMMON_ECONOMICS_KEYS,
        field_name="common.economics",
    )
    _require_exact_keys(
        signals,
        required_keys=COMMON_SIGNALS_KEYS,
        field_name="common.signals",
    )

    regime = common["regime"]
    if regime == "":
        pass
    else:
        _require_literal(regime, field_name="common.regime", allowed=ALLOWED_REGIMES)

    _require_optional_literal(
        common["strategy_runtime_mode_classic"],
        field_name="common.strategy_runtime_mode_classic",
        allowed=CLASSIC_ALLOWED_STRATEGY_RUNTIME_MODES,
    )
    _require_optional_literal(
        common["strategy_runtime_mode_miso"],
        field_name="common.strategy_runtime_mode_miso",
        allowed=MISO_ALLOWED_STRATEGY_RUNTIME_MODES,
    )
    _require_optional_literal(
        selected_option["side"],
        field_name="common.selected_option.side",
        allowed=OPTION_SIDE_IDS,
    )

    _require_bool(call["tradability_ok"], field_name="common.call.tradability_ok")
    _require_bool(put["tradability_ok"], field_name="common.put.tradability_ok")
    _require_bool(
        selected_option["tradability_ok"],
        field_name="common.selected_option.tradability_ok",
    )
    _require_bool(
        economics["premium_floor_ok"],
        field_name="common.economics.premium_floor_ok",
    )
    _require_bool(
        economics["economic_viability_ok"],
        field_name="common.economics.economic_viability_ok",
    )
    _require_bool(
        signals["futures_contradiction_flag"],
        field_name="common.signals.futures_contradiction_flag",
    )
    _require_bool(
        signals["queue_reload_veto_flag"],
        field_name="common.signals.queue_reload_veto_flag",
    )


def validate_stage_flags_block(stage_flags: Mapping[str, Any]) -> None:
    _require_exact_keys(
        stage_flags,
        required_keys=STAGE_FLAG_KEYS,
        field_name="stage_flags",
    )
    for key in STAGE_FLAG_KEYS:
        _require_bool(stage_flags[key], field_name=f"stage_flags.{key}")


def validate_mist_family_support(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        required_keys=("eligible", "branches"),
        field_name="families.MIST",
    )
    _require_bool(value["eligible"], field_name="families.MIST.eligible")
    branches = _require_mapping(value["branches"], field_name="families.MIST.branches")
    _require_exact_keys(
        branches,
        required_keys=BRANCH_IDS,
        field_name="families.MIST.branches",
    )
    for branch_id in BRANCH_IDS:
        branch = _require_mapping(
            branches[branch_id],
            field_name=f"families.MIST.branches.{branch_id}",
        )
        _require_exact_keys(
            branch,
            required_keys=MIST_BRANCH_KEYS,
            field_name=f"families.MIST.branches.{branch_id}",
        )
        _validate_bool_mapping_fields(
            branch,
            field_name=f"families.MIST.branches.{branch_id}",
            bool_keys=MIST_BRANCH_KEYS,
        )


def validate_misb_family_support(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        required_keys=("eligible", "branches"),
        field_name="families.MISB",
    )
    _require_bool(value["eligible"], field_name="families.MISB.eligible")
    branches = _require_mapping(value["branches"], field_name="families.MISB.branches")
    _require_exact_keys(
        branches,
        required_keys=BRANCH_IDS,
        field_name="families.MISB.branches",
    )
    for branch_id in BRANCH_IDS:
        branch = _require_mapping(
            branches[branch_id],
            field_name=f"families.MISB.branches.{branch_id}",
        )
        _require_exact_keys(
            branch,
            required_keys=MISB_BRANCH_KEYS,
            field_name=f"families.MISB.branches.{branch_id}",
        )
        _validate_bool_mapping_fields(
            branch,
            field_name=f"families.MISB.branches.{branch_id}",
            bool_keys=MISB_BRANCH_KEYS,
        )


def validate_misc_family_support(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        required_keys=("eligible", "branches"),
        field_name="families.MISC",
    )
    _require_bool(value["eligible"], field_name="families.MISC.eligible")
    branches = _require_mapping(value["branches"], field_name="families.MISC.branches")
    _require_exact_keys(
        branches,
        required_keys=BRANCH_IDS,
        field_name="families.MISC.branches",
    )
    for branch_id in BRANCH_IDS:
        branch = _require_mapping(
            branches[branch_id],
            field_name=f"families.MISC.branches.{branch_id}",
        )
        _require_exact_keys(
            branch,
            required_keys=MISC_BRANCH_KEYS,
            field_name=f"families.MISC.branches.{branch_id}",
        )
        _validate_bool_mapping_fields(
            branch,
            field_name=f"families.MISC.branches.{branch_id}",
            bool_keys=MISC_BRANCH_KEYS,
        )


def validate_misr_family_support(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        required_keys=("eligible", "active_zone", "branches"),
        field_name="families.MISR",
    )
    _require_bool(value["eligible"], field_name="families.MISR.eligible")
    active_zone = _require_mapping(
        value["active_zone"],
        field_name="families.MISR.active_zone",
    )
    _require_exact_keys(
        active_zone,
        required_keys=MISR_ACTIVE_ZONE_KEYS,
        field_name="families.MISR.active_zone",
    )
    branches = _require_mapping(value["branches"], field_name="families.MISR.branches")
    _require_exact_keys(
        branches,
        required_keys=BRANCH_IDS,
        field_name="families.MISR.branches",
    )
    for branch_id in BRANCH_IDS:
        branch = _require_mapping(
            branches[branch_id],
            field_name=f"families.MISR.branches.{branch_id}",
        )
        _require_exact_keys(
            branch,
            required_keys=MISR_BRANCH_KEYS,
            field_name=f"families.MISR.branches.{branch_id}",
        )
        _validate_bool_mapping_fields(
            branch,
            field_name=f"families.MISR.branches.{branch_id}",
            bool_keys=MISR_BRANCH_KEYS,
        )


def validate_miso_family_support(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        required_keys=MISO_ROOT_KEYS,
        field_name="families.MISO",
    )
    _require(
        "branches" not in value,
        "families.MISO must never expose classic branches; use call_support/put_support only",
    )
    _require_bool(value["eligible"], field_name="families.MISO.eligible")
    _require_bool(
        value["chain_context_ready"],
        field_name="families.MISO.chain_context_ready",
    )
    _require_optional_literal(
        value["selected_side"],
        field_name="families.MISO.selected_side",
        allowed=BRANCH_IDS,
    )
    _require_optional_literal(
        value["mode"],
        field_name="families.MISO.mode",
        allowed=MISO_ALLOWED_STRATEGY_RUNTIME_MODES,
    )

    call_support = _require_mapping(
        value["call_support"],
        field_name="families.MISO.call_support",
    )
    put_support = _require_mapping(
        value["put_support"],
        field_name="families.MISO.put_support",
    )
    _require_exact_keys(
        call_support,
        required_keys=MISO_SIDE_SUPPORT_KEYS,
        field_name="families.MISO.call_support",
    )
    _require_exact_keys(
        put_support,
        required_keys=MISO_SIDE_SUPPORT_KEYS,
        field_name="families.MISO.put_support",
    )
    _validate_bool_mapping_fields(
        call_support,
        field_name="families.MISO.call_support",
        bool_keys=MISO_SIDE_SUPPORT_KEYS,
    )
    _validate_bool_mapping_fields(
        put_support,
        field_name="families.MISO.put_support",
        bool_keys=MISO_SIDE_SUPPORT_KEYS,
    )


def validate_families_block(families: Mapping[str, Any]) -> None:
    _require_exact_keys(
        families,
        required_keys=FAMILY_IDS,
        field_name="families",
    )

    validate_mist_family_support(
        _require_mapping(families[FAMILY_ID_MIST], field_name="families.MIST")
    )
    validate_misb_family_support(
        _require_mapping(families[FAMILY_ID_MISB], field_name="families.MISB")
    )
    validate_misc_family_support(
        _require_mapping(families[FAMILY_ID_MISC], field_name="families.MISC")
    )
    validate_misr_family_support(
        _require_mapping(families[FAMILY_ID_MISR], field_name="families.MISR")
    )
    validate_miso_family_support(
        _require_mapping(families[FAMILY_ID_MISO], field_name="families.MISO")
    )


def validate_family_features_payload(payload: Mapping[str, Any]) -> None:
    """
    Structural + semantic validation suitable for scaffold objects and non-publishable
    intermediate payloads.

    This validator:
    - rejects key drift
    - rejects invalid canonical literals when values are present
    - allows scaffold placeholders such as None in provider/runtime fields
    """
    _validate_family_identities()
    _require_exact_keys(payload, required_keys=TOP_LEVEL_KEYS, field_name="payload")

    schema_version = _require_int(
        payload["schema_version"],
        field_name="payload.schema_version",
        min_value=1,
    )
    service = _require_str(payload["service"], field_name="payload.service")
    family_features_version = _require_str(
        payload["family_features_version"],
        field_name="payload.family_features_version",
    )
    generated_at_ns = _require_int(
        payload["generated_at_ns"],
        field_name="payload.generated_at_ns",
        min_value=0,
    )

    _require(
        service == N.SERVICE_FEATURES,
        f"payload.service must equal {N.SERVICE_FEATURES!r}, got {service!r}",
    )
    _require(schema_version >= 1, "payload.schema_version must be >= 1")
    _require(
        family_features_version == FAMILY_FEATURES_VERSION,
        "payload.family_features_version mismatch: "
        f"expected {FAMILY_FEATURES_VERSION!r}, got {family_features_version!r}",
    )
    _require(generated_at_ns >= 0, "payload.generated_at_ns must be >= 0")

    validate_snapshot_block(
        _require_mapping(payload["snapshot"], field_name="payload.snapshot")
    )
    validate_provider_runtime_block(
        _require_mapping(
            payload["provider_runtime"],
            field_name="payload.provider_runtime",
        ),
        publishable=False,
    )
    validate_market_block(
        _require_mapping(payload["market"], field_name="payload.market")
    )
    validate_common_block(
        _require_mapping(payload["common"], field_name="payload.common")
    )
    validate_stage_flags_block(
        _require_mapping(payload["stage_flags"], field_name="payload.stage_flags")
    )
    validate_families_block(
        _require_mapping(payload["families"], field_name="payload.families")
    )


def validate_publishable_family_features_payload(payload: Mapping[str, Any]) -> None:
    """
    Runtime-publication validator.

    Publishable means structurally safe for Redis publication to live/replay
    consumers. It does not mean entry-eligible. A publishable payload may still
    carry snapshot.valid=False, UNAVAILABLE provider statuses, and all entry
    stage flags false so strategy can deterministically HOLD.

    This validator is intentionally stricter than validate_family_features_payload():
    it forbids scaffold placeholders in provider/runtime surfaces and requires the
    payload to be publication-safe for live/replay consumers.
    """
    validate_family_features_payload(payload)

    validate_provider_runtime_block(
        _require_mapping(
            payload["provider_runtime"],
            field_name="payload.provider_runtime",
        ),
        publishable=True,
    )

    snapshot = _require_mapping(payload["snapshot"], field_name="payload.snapshot")
    _require_int(
        payload["generated_at_ns"],
        field_name="payload.generated_at_ns",
        min_value=1,
    )
    _require_int(
        snapshot["samples_seen"],
        field_name="payload.snapshot.samples_seen",
        min_value=1,
    )


def assert_valid_family_features_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_family_features_payload(payload)
    return payload


def assert_publishable_family_features_payload(
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    validate_publishable_family_features_payload(payload)
    return payload


# ============================================================================
# Frozen readonly registries
# ============================================================================

FAMILY_TO_EMPTY_BUILDER: Final[Mapping[str, Any]] = MappingProxyType(
    {
        FAMILY_ID_MIST: build_empty_mist_family_support,
        FAMILY_ID_MISB: build_empty_misb_family_support,
        FAMILY_ID_MISC: build_empty_misc_family_support,
        FAMILY_ID_MISR: build_empty_misr_family_support,
        FAMILY_ID_MISO: build_empty_miso_family_support,
    }
)

FAMILY_TO_VALIDATOR: Final[Mapping[str, Any]] = MappingProxyType(
    {
        FAMILY_ID_MIST: validate_mist_family_support,
        FAMILY_ID_MISB: validate_misb_family_support,
        FAMILY_ID_MISC: validate_misc_family_support,
        FAMILY_ID_MISR: validate_misr_family_support,
        FAMILY_ID_MISO: validate_miso_family_support,
    }
)

# ============================================================================
# Import-time contract self-check
# ============================================================================


def validate_contract_field_registry() -> None:
    """Validate Batch 25G field registry alignment with core.names."""

    N.validate_contract_field_registry()

    def _require_tuple_match(local: tuple[str, ...], upstream: tuple[str, ...], label: str) -> None:
        if tuple(local) != tuple(upstream):
            raise FeatureFamilyContractError(
                f"{label} drift: local={tuple(local)!r} upstream={tuple(upstream)!r}"
            )

    _require_tuple_match(
        CANONICAL_PROVIDER_RUNTIME_KEYS,
        N.CONTRACT_PROVIDER_RUNTIME_KEYS,
        "CANONICAL_PROVIDER_RUNTIME_KEYS",
    )
    _require_tuple_match(
        CANONICAL_FEED_SNAPSHOT_KEYS,
        N.CONTRACT_FEED_SNAPSHOT_KEYS,
        "CANONICAL_FEED_SNAPSHOT_KEYS",
    )
    _require_tuple_match(
        CANONICAL_DHAN_CONTEXT_KEYS,
        N.CONTRACT_DHAN_CONTEXT_KEYS,
        "CANONICAL_DHAN_CONTEXT_KEYS",
    )
    _require_tuple_match(
        CANONICAL_EXECUTION_ENTRY_KEYS,
        N.CONTRACT_EXECUTION_ENTRY_KEYS,
        "CANONICAL_EXECUTION_ENTRY_KEYS",
    )

    if tuple(CANONICAL_FAMILY_SUPPORT_KEYS.keys()) != tuple(N.CONTRACT_FAMILY_SUPPORT_KEYS.keys()):
        raise FeatureFamilyContractError("CANONICAL_FAMILY_SUPPORT_KEYS family coverage drift")

    for family_id, keys in CANONICAL_FAMILY_SUPPORT_KEYS.items():
        _require_tuple_match(
            tuple(keys),
            tuple(N.CONTRACT_FAMILY_SUPPORT_KEYS[family_id]),
            f"CANONICAL_FAMILY_SUPPORT_KEYS[{family_id}]",
        )

    if dict(CANONICAL_FIELD_COMPATIBILITY_ALIASES) != dict(N.CONTRACT_FIELD_COMPATIBILITY_ALIASES):
        raise FeatureFamilyContractError("CANONICAL_FIELD_COMPATIBILITY_ALIASES drift")



_validate_family_identities()
validate_family_features_payload(build_empty_family_features_payload())
validate_contract_field_registry()

# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "FeatureFamilyContractError",
    "FAMILY_FEATURES_VERSION",
    "CONTRACT_FIELD_REGISTRY_VERSION",
    "FAMILY_ID_MIST",
    "FAMILY_ID_MISB",
    "FAMILY_ID_MISC",
    "FAMILY_ID_MISR",
    "FAMILY_ID_MISO",
    "FAMILY_IDS",
    "CLASSIC_FAMILY_IDS",
    "BRANCH_CALL",
    "BRANCH_PUT",
    "BRANCH_IDS",
    "ALLOWED_PROVIDER_IDS",
    "ALLOWED_PROVIDER_STATUSES",
    "ALLOWED_FAMILY_RUNTIME_MODES",
    "ALLOWED_STRATEGY_RUNTIME_MODES",
    "CLASSIC_ALLOWED_STRATEGY_RUNTIME_MODES",
    "MISO_ALLOWED_STRATEGY_RUNTIME_MODES",
    "REGIME_LOWVOL",
    "REGIME_NORMAL",
    "REGIME_FAST",
    "ALLOWED_REGIMES",
    "KEY_SCHEMA_VERSION",
    "KEY_SERVICE",
    "KEY_FAMILY_FEATURES_VERSION",
    "KEY_GENERATED_AT_NS",
    "KEY_SNAPSHOT",
    "KEY_PROVIDER_RUNTIME",
    "KEY_MARKET",
    "KEY_COMMON",
    "KEY_STAGE_FLAGS",
    "KEY_FAMILIES",
    "TOP_LEVEL_KEYS",
    "SNAPSHOT_KEYS",
    "PROVIDER_RUNTIME_CANONICAL_KEYS",
    "PROVIDER_RUNTIME_COMPATIBILITY_KEYS",
    "PROVIDER_RUNTIME_KEYS",
    "MARKET_KEYS",
    "COMMON_KEYS",
    "STAGE_FLAG_KEYS",
    "COMMON_FUTURES_KEYS",
    "COMMON_OPTION_KEYS",
    "COMMON_SELECTED_OPTION_KEYS",
    "COMMON_CROSS_OPTION_KEYS",
    "COMMON_ECONOMICS_KEYS",
    "COMMON_SIGNALS_KEYS",
    "MIST_BRANCH_KEYS",
    "MISB_BRANCH_KEYS",
    "MISC_BRANCH_KEYS",
    "MISR_ACTIVE_ZONE_KEYS",
    "MISR_BRANCH_KEYS",
    "MISO_ROOT_KEYS",
    "MISO_SIDE_SUPPORT_KEYS",
    "FAMILY_SUPPORT_ALIAS_MAP",
    "FAMILY_SUPPORT_INVERTED_ALIAS_MAP",
    "FAMILY_BRANCH_ELIGIBILITY_KEYS",
    "CANONICAL_PROVIDER_RUNTIME_KEYS",
    "CANONICAL_FEED_SNAPSHOT_KEYS",
    "CANONICAL_DHAN_CONTEXT_KEYS",
    "CANONICAL_FAMILY_SUPPORT_KEYS",
    "CANONICAL_EXECUTION_ENTRY_TOP_LEVEL_KEYS",
    "CANONICAL_EXECUTION_ENTRY_METADATA_KEYS",
    "CANONICAL_EXECUTION_ENTRY_KEYS",
    "CANONICAL_CONTRACT_FIELD_REGISTRY",
    "CANONICAL_FIELD_COMPATIBILITY_ALIASES",
    "build_empty_snapshot_block",
    "build_empty_provider_runtime_block",
    "build_empty_market_block",
    "build_empty_common_futures_block",
    "build_empty_common_option_block",
    "build_empty_selected_option_block",
    "build_empty_cross_option_block",
    "build_empty_economics_block",
    "build_empty_signals_block",
    "build_empty_common_block",
    "build_empty_stage_flags_block",
    "build_empty_mist_branch_support",
    "build_empty_misb_branch_support",
    "build_empty_misc_branch_support",
    "build_empty_misr_active_zone",
    "build_empty_misr_branch_support",
    "build_empty_miso_side_support",
    "build_empty_mist_family_support",
    "build_empty_misb_family_support",
    "build_empty_misc_family_support",
    "build_empty_misr_family_support",
    "build_empty_miso_family_support",
    "build_empty_families_block",
    "build_empty_family_features_payload",
    "validate_snapshot_block",
    "validate_provider_runtime_block",
    "validate_market_block",
    "validate_common_block",
    "validate_stage_flags_block",
    "validate_mist_family_support",
    "validate_misb_family_support",
    "validate_misc_family_support",
    "validate_misr_family_support",
    "validate_miso_family_support",
    "validate_families_block",
    "validate_family_features_payload",
    "validate_contract_field_registry",
    "validate_publishable_family_features_payload",
    "assert_valid_family_features_payload",
    "assert_publishable_family_features_payload",
    "FAMILY_TO_EMPTY_BUILDER",
    "FAMILY_TO_VALIDATOR",
]


# ============================================================================
# Batch 25H canonical provider-runtime bridge
# ============================================================================
#
# Purpose
# -------
# Batch 25G froze canonical provider-runtime field names in core.names.
# Existing strategy-family consumers still use the older active_* compatibility
# fields. This bridge keeps the family_features provider_runtime block
# compatible while making canonical producer truth explicit.
#
# This is a contract seam only:
# - no provider failover is performed here
# - no strategy promotion is enabled here
# - no execution arming is enabled here
# - observe_only remains the safe default family runtime mode

_BATCH25H_ORIGINAL_BUILD_EMPTY_PROVIDER_RUNTIME_BLOCK = build_empty_provider_runtime_block
_BATCH25H_ORIGINAL_VALIDATE_PROVIDER_RUNTIME_BLOCK = validate_provider_runtime_block

_BATCH25H_CANONICAL_TO_COMPAT: Final[dict[str, str]] = {
    "futures_marketdata_provider_id": "active_futures_provider_id",
    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
    "option_context_provider_id": "active_option_context_provider_id",
    "execution_primary_provider_id": "active_execution_provider_id",
    "execution_fallback_provider_id": "fallback_execution_provider_id",
    "futures_marketdata_status": "futures_provider_status",
    "selected_option_marketdata_status": "selected_option_provider_status",
    "option_context_status": "option_context_provider_status",
    "execution_primary_status": "execution_provider_status",
}


def _batch25h_provider_default(key: str) -> Any:
    if key in {"failover_active", "pending_failover"}:
        return False
    if key == "provider_transition_seq":
        return 0
    if key.endswith("_status"):
        return getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
    if key == "family_runtime_mode":
        return getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only")
    return None


def build_empty_provider_runtime_block() -> dict[str, Any]:
    out = dict(_BATCH25H_ORIGINAL_BUILD_EMPTY_PROVIDER_RUNTIME_BLOCK())

    for key in getattr(N, "CONTRACT_PROVIDER_RUNTIME_KEYS", ()):
        out.setdefault(key, _batch25h_provider_default(key))

    for canonical, compat in _BATCH25H_CANONICAL_TO_COMPAT.items():
        out.setdefault(compat, out.get(canonical))

    out.setdefault("provider_runtime_mode", None)
    out.setdefault("provider_runtime_blocked", True)
    out.setdefault("provider_runtime_block_reason", "empty_provider_runtime_block")
    out.setdefault("provider_runtime_missing_keys", tuple(getattr(N, "CONTRACT_PROVIDER_RUNTIME_KEYS", ())))

    return out


def validate_provider_runtime_block(
    provider_runtime: Mapping[str, Any],
    *,
    field_name: str = "provider_runtime",
) -> None:
    if not isinstance(provider_runtime, Mapping):
        raise FeatureFamilyContractError(f"{field_name} must be a mapping")

    required_keys = set(_BATCH25H_ORIGINAL_BUILD_EMPTY_PROVIDER_RUNTIME_BLOCK().keys())
    required_keys.update(getattr(N, "CONTRACT_PROVIDER_RUNTIME_KEYS", ()))
    required_keys.update(_BATCH25H_CANONICAL_TO_COMPAT.values())
    required_keys.update(
        {
            "provider_runtime_blocked",
            "provider_runtime_block_reason",
            "provider_runtime_missing_keys",
        }
    )

    missing = sorted(key for key in required_keys if key not in provider_runtime)
    if missing:
        raise FeatureFamilyContractError(f"{field_name} missing provider-runtime keys: {missing!r}")

    for key in getattr(N, "CONTRACT_PROVIDER_RUNTIME_KEYS", ()):
        value = provider_runtime.get(key)
        if key in {"failover_active", "pending_failover"}:
            if not isinstance(value, bool):
                raise FeatureFamilyContractError(f"{field_name}.{key} must be bool")
            continue
        if key == "provider_transition_seq":
            if not isinstance(value, int):
                raise FeatureFamilyContractError(f"{field_name}.{key} must be int")
            continue
        if value is not None and not isinstance(value, str):
            raise FeatureFamilyContractError(f"{field_name}.{key} must be str or None")

    for canonical, compat in _BATCH25H_CANONICAL_TO_COMPAT.items():
        compat_value = provider_runtime.get(compat)
        canonical_value = provider_runtime.get(canonical)
        if compat_value is not None and not isinstance(compat_value, str):
            raise FeatureFamilyContractError(f"{field_name}.{compat} must be str or None")
        if canonical_value is not None and compat_value is not None and compat_value != canonical_value:
            raise FeatureFamilyContractError(
                f"{field_name}.{compat} drift: compat={compat_value!r} canonical={canonical_value!r}"
            )

    if not isinstance(provider_runtime.get("provider_runtime_blocked"), bool):
        raise FeatureFamilyContractError(f"{field_name}.provider_runtime_blocked must be bool")

    if not isinstance(provider_runtime.get("provider_runtime_block_reason"), str):
        raise FeatureFamilyContractError(f"{field_name}.provider_runtime_block_reason must be str")

    missing_keys = provider_runtime.get("provider_runtime_missing_keys")
    if not isinstance(missing_keys, (tuple, list)):
        raise FeatureFamilyContractError(f"{field_name}.provider_runtime_missing_keys must be tuple/list")


def build_batch25h_provider_runtime_contract_block(values: Mapping[str, Any] | None = None) -> dict[str, Any]:
    out = build_empty_provider_runtime_block()
    out.update(dict(values or {}))
    validate_provider_runtime_block(out)
    return out


# ============================================================================
# Batch 25H-C final provider-runtime contract surface
# ============================================================================
#
# Corrective purpose
# ------------------
# 25H proved canonical/compat alias derivation, but the family-feature
# provider_runtime subtree still needs a single validator surface that accepts:
# - Batch 25G canonical provider-runtime keys
# - existing compatibility keys consumed by strategy-family surfaces
# - explicit blocker metadata for missing required runtime signals
#
# This remains a contract/adapter seam only:
# - no provider failover is performed here
# - no strategy promotion is enabled here
# - no execution arming is enabled here
# - observe_only remains the default family runtime mode

PROVIDER_RUNTIME_CANONICAL_KEYS: Final[tuple[str, ...]] = tuple(
    N.CONTRACT_PROVIDER_RUNTIME_KEYS
)

PROVIDER_RUNTIME_COMPATIBILITY_KEYS: Final[tuple[str, ...]] = (
    "active_futures_provider_id",
    "active_selected_option_provider_id",
    "active_option_context_provider_id",
    "active_execution_provider_id",
    "fallback_execution_provider_id",
    "provider_runtime_mode",
    "futures_provider_status",
    "selected_option_provider_status",
    "option_context_provider_status",
    "execution_provider_status",
    "execution_fallback_provider_status",
)

PROVIDER_RUNTIME_BLOCKER_KEYS: Final[tuple[str, ...]] = (
    "provider_ready_classic",
    "provider_ready_miso",
    "provider_runtime_blocked",
    "provider_runtime_block_reason",
    "provider_runtime_missing_keys",
)

PROVIDER_RUNTIME_KEYS = tuple(
    dict.fromkeys(
        (
            *PROVIDER_RUNTIME_CANONICAL_KEYS,
            *PROVIDER_RUNTIME_COMPATIBILITY_KEYS,
            *PROVIDER_RUNTIME_BLOCKER_KEYS,
        )
    )
)

_BATCH25HC_CANONICAL_TO_COMPAT: Final[dict[str, str]] = {
    "futures_marketdata_provider_id": "active_futures_provider_id",
    "selected_option_marketdata_provider_id": "active_selected_option_provider_id",
    "option_context_provider_id": "active_option_context_provider_id",
    "execution_primary_provider_id": "active_execution_provider_id",
    "execution_fallback_provider_id": "fallback_execution_provider_id",
    "futures_marketdata_status": "futures_provider_status",
    "selected_option_marketdata_status": "selected_option_provider_status",
    "option_context_status": "option_context_provider_status",
    "execution_primary_status": "execution_provider_status",
    "execution_fallback_status": "execution_fallback_provider_status",
}


def _batch25hc_provider_status_unavailable() -> str:
    return getattr(N, "PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")


def _batch25hc_default_provider_runtime_value(key: str) -> Any:
    if key in {"failover_active", "pending_failover"}:
        return False
    if key == "provider_transition_seq":
        return 0
    if key.endswith("_status") or key.endswith("_provider_status"):
        return _batch25hc_provider_status_unavailable()
    if key == "family_runtime_mode":
        return getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only")
    if key == "failover_mode":
        return getattr(N, "PROVIDER_FAILOVER_MODE_MANUAL", "MANUAL")
    if key == "override_mode":
        return getattr(N, "PROVIDER_OVERRIDE_MODE_AUTO", "AUTO")
    if key == "transition_reason":
        return getattr(N, "PROVIDER_TRANSITION_REASON_BOOTSTRAP", "BOOTSTRAP")
    if key in {"provider_ready_classic", "provider_ready_miso"}:
        return False
    if key == "provider_runtime_blocked":
        return True
    if key == "provider_runtime_block_reason":
        return "empty_provider_runtime_block"
    if key == "provider_runtime_missing_keys":
        return tuple(PROVIDER_RUNTIME_CANONICAL_KEYS)
    return None


def build_empty_provider_runtime_block() -> dict[str, Any]:
    out = {key: _batch25hc_default_provider_runtime_value(key) for key in PROVIDER_RUNTIME_KEYS}

    for canonical, compat in _BATCH25HC_CANONICAL_TO_COMPAT.items():
        out[compat] = out.get(canonical)

    return out


def validate_provider_runtime_block(
    provider_runtime: Mapping[str, Any],
    *,
    publishable: bool = False,
) -> None:
    if not isinstance(provider_runtime, Mapping):
        raise FeatureFamilyContractError("provider_runtime must be a mapping")

    missing = [key for key in PROVIDER_RUNTIME_KEYS if key not in provider_runtime]
    if missing:
        raise FeatureFamilyContractError(f"provider_runtime missing keys: {missing!r}")

    for key in PROVIDER_RUNTIME_CANONICAL_KEYS:
        value = provider_runtime[key]

        if key in {"failover_active", "pending_failover"}:
            if not isinstance(value, bool):
                raise FeatureFamilyContractError(f"provider_runtime.{key} must be bool")
            continue

        if key == "provider_transition_seq":
            if isinstance(value, bool) or not isinstance(value, int):
                raise FeatureFamilyContractError(f"provider_runtime.{key} must be int")
            continue

        if key == "family_runtime_mode":
            if value not in ALLOWED_FAMILY_RUNTIME_MODES:
                raise FeatureFamilyContractError(
                    f"provider_runtime.{key} invalid family runtime mode: {value!r}"
                )
            continue

        if key.endswith("_status"):
            if value is not None and not isinstance(value, str):
                raise FeatureFamilyContractError(f"provider_runtime.{key} must be str or None")
            continue

        if value is not None and not isinstance(value, str):
            raise FeatureFamilyContractError(f"provider_runtime.{key} must be str or None")

    for canonical, compat in _BATCH25HC_CANONICAL_TO_COMPAT.items():
        canonical_value = provider_runtime.get(canonical)
        compat_value = provider_runtime.get(compat)

        if compat_value is not None and not isinstance(compat_value, str):
            raise FeatureFamilyContractError(f"provider_runtime.{compat} must be str or None")

        if canonical_value is not None and compat_value is not None and compat_value != canonical_value:
            raise FeatureFamilyContractError(
                f"provider_runtime.{compat} drift: canonical={canonical_value!r} compat={compat_value!r}"
            )

    if not isinstance(provider_runtime["provider_ready_classic"], bool):
        raise FeatureFamilyContractError("provider_runtime.provider_ready_classic must be bool")

    if not isinstance(provider_runtime["provider_ready_miso"], bool):
        raise FeatureFamilyContractError("provider_runtime.provider_ready_miso must be bool")

    if not isinstance(provider_runtime["provider_runtime_blocked"], bool):
        raise FeatureFamilyContractError("provider_runtime.provider_runtime_blocked must be bool")

    if not isinstance(provider_runtime["provider_runtime_block_reason"], str):
        raise FeatureFamilyContractError("provider_runtime.provider_runtime_block_reason must be str")

    if not isinstance(provider_runtime["provider_runtime_missing_keys"], (tuple, list)):
        raise FeatureFamilyContractError("provider_runtime.provider_runtime_missing_keys must be tuple/list")

    if publishable:
        required_publishable = (
            "futures_marketdata_provider_id",
            "selected_option_marketdata_provider_id",
            "futures_marketdata_status",
            "selected_option_marketdata_status",
        )
        for key in required_publishable:
            value = provider_runtime.get(key)
            if value in (None, ""):
                raise FeatureFamilyContractError(f"publishable provider_runtime.{key} is required")


def validate_family_features_payload(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, Mapping):
        raise FeatureFamilyContractError("family_features payload must be a mapping")

    expected_top = set(TOP_LEVEL_KEYS)
    actual_top = set(payload.keys())
    if actual_top != expected_top:
        raise FeatureFamilyContractError(
            f"family_features top-level key drift: missing={sorted(expected_top - actual_top)!r} "
            f"extra={sorted(actual_top - expected_top)!r}"
        )

    validate_snapshot_block(payload[KEY_SNAPSHOT])
    validate_provider_runtime_block(payload[KEY_PROVIDER_RUNTIME])
    validate_market_block(payload[KEY_MARKET])
    validate_common_block(payload[KEY_COMMON])
    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])
    validate_families_block(payload[KEY_FAMILIES])


def assert_valid_family_features_payload(payload: Mapping[str, Any]) -> None:
    validate_family_features_payload(payload)


def build_batch25h_provider_runtime_contract_block(values: Mapping[str, Any] | None = None) -> dict[str, Any]:
    out = build_empty_provider_runtime_block()
    out.update(dict(values or {}))

    for canonical, compat in _BATCH25HC_CANONICAL_TO_COMPAT.items():
        out[compat] = out.get(canonical)

    validate_provider_runtime_block(out)
    return out


try:
    __all__ = list(
        dict.fromkeys(
            [
                *__all__,
                "PROVIDER_RUNTIME_CANONICAL_KEYS",
                "PROVIDER_RUNTIME_COMPATIBILITY_KEYS",
                "PROVIDER_RUNTIME_BLOCKER_KEYS",
                "build_batch25h_provider_runtime_contract_block",
            ]
        )
    )
except NameError:
    pass

# ============================================================================
# Batch 26H surface-kind consolidation contract
# ============================================================================

from types import MappingProxyType as _Batch26H_MappingProxyType
from typing import Any as _Batch26H_Any
from typing import Final as _Batch26H_Final
from typing import Mapping as _Batch26H_Mapping


BATCH26H_EXPECTED_BRANCH_SURFACE_KINDS: _Batch26H_Final[_Batch26H_Mapping[str, str]] = _Batch26H_MappingProxyType(
    {
        FAMILY_ID_MIST: "mist_branch",
        FAMILY_ID_MISB: "misb_branch",
        FAMILY_ID_MISC: "misc_branch",
        FAMILY_ID_MISR: "misr_branch",
        FAMILY_ID_MISO: "miso_branch",
    }
)

BATCH26H_EXPECTED_FAMILY_SURFACE_KINDS: _Batch26H_Final[_Batch26H_Mapping[str, str]] = _Batch26H_MappingProxyType(
    {
        FAMILY_ID_MIST: "mist_family",
        FAMILY_ID_MISB: "misb_family",
        FAMILY_ID_MISC: "misc_family",
        FAMILY_ID_MISR: "misr_family",
        FAMILY_ID_MISO: "miso_family",
    }
)


def batch26h_expected_branch_surface_kind(family_id: str) -> str:
    return BATCH26H_EXPECTED_BRANCH_SURFACE_KINDS[str(family_id).strip().upper()]


def batch26h_expected_family_surface_kind(family_id: str) -> str:
    return BATCH26H_EXPECTED_FAMILY_SURFACE_KINDS[str(family_id).strip().upper()]


def validate_batch26h_surface_kinds(family_surfaces: _Batch26H_Mapping[str, _Batch26H_Any]) -> None:
    families = family_surfaces.get("families", {})
    if not isinstance(families, _Batch26H_Mapping):
        raise FeatureFamilyContractError("Batch26H family_surfaces.families must be a mapping")

    surfaces_by_branch = family_surfaces.get("surfaces_by_branch", {})
    if not isinstance(surfaces_by_branch, _Batch26H_Mapping):
        raise FeatureFamilyContractError("Batch26H family_surfaces.surfaces_by_branch must be a mapping")

    for family_id in FAMILY_IDS:
        family = families.get(family_id)
        if not isinstance(family, _Batch26H_Mapping):
            raise FeatureFamilyContractError(f"Batch26H missing family surface: {family_id}")

        expected_family_kind = batch26h_expected_family_surface_kind(family_id)
        actual_family_kind = family.get("surface_kind")
        if actual_family_kind != expected_family_kind:
            raise FeatureFamilyContractError(
                f"Batch26H family surface_kind mismatch for {family_id}: "
                f"expected {expected_family_kind!r}, got {actual_family_kind!r}"
            )

        branches = family.get("branches", {})
        if not isinstance(branches, _Batch26H_Mapping):
            raise FeatureFamilyContractError(f"Batch26H {family_id}.branches must be a mapping")

        expected_branch_kind = batch26h_expected_branch_surface_kind(family_id)
        for branch_id in BRANCH_IDS:
            branch = branches.get(branch_id)
            if not isinstance(branch, _Batch26H_Mapping):
                raise FeatureFamilyContractError(f"Batch26H missing branch surface: {family_id}.{branch_id}")

            actual_branch_kind = branch.get("surface_kind")
            if actual_branch_kind != expected_branch_kind:
                raise FeatureFamilyContractError(
                    f"Batch26H branch surface_kind mismatch for {family_id}.{branch_id}: "
                    f"expected {expected_branch_kind!r}, got {actual_branch_kind!r}"
                )

            branch_key = f"{family_id.lower()}_{str(branch_id).lower()}"
            flat_branch = surfaces_by_branch.get(branch_key)
            if not isinstance(flat_branch, _Batch26H_Mapping):
                raise FeatureFamilyContractError(f"Batch26H missing surfaces_by_branch key: {branch_key}")

            flat_kind = flat_branch.get("surface_kind")
            if flat_kind != expected_branch_kind:
                raise FeatureFamilyContractError(
                    f"Batch26H surfaces_by_branch surface_kind mismatch for {branch_key}: "
                    f"expected {expected_branch_kind!r}, got {flat_kind!r}"
                )


__all__ = tuple(
    sorted(
        set(globals().get("__all__", ()))
        | {
            "BATCH26H_EXPECTED_BRANCH_SURFACE_KINDS",
            "BATCH26H_EXPECTED_FAMILY_SURFACE_KINDS",
            "batch26h_expected_branch_surface_kind",
            "batch26h_expected_family_surface_kind",
            "validate_batch26h_surface_kinds",
        }
    )
)

# ============================================================================
# Batch 26I-R1 — MISO inverted alias settlement
# ============================================================================
#
# These aliases are family-scoped inverted aliases only. They must not be
# inserted into non-inverting global alias maps.

from types import MappingProxyType as _Batch26IR1_MappingProxyType

_batch26ir1_existing_inverted_alias_map = dict(globals().get("FAMILY_SUPPORT_INVERTED_ALIAS_MAP", {}))
_batch26ir1_miso_inverted_aliases = dict(_batch26ir1_existing_inverted_alias_map.get("MISO", {}))

_batch26ir1_miso_inverted_aliases["queue_reload_blocked"] = tuple(
    dict.fromkeys(
        tuple(_batch26ir1_miso_inverted_aliases.get("queue_reload_blocked", ()))
        + ("queue_ok", "queue_clear", "queue_reload_clear")
    )
)
_batch26ir1_miso_inverted_aliases["futures_contradiction_blocked"] = tuple(
    dict.fromkeys(
        tuple(_batch26ir1_miso_inverted_aliases.get("futures_contradiction_blocked", ()))
        + ("futures_veto_clear", "futures_clear")
    )
)

_batch26ir1_existing_inverted_alias_map["MISO"] = _Batch26IR1_MappingProxyType(_batch26ir1_miso_inverted_aliases)
FAMILY_SUPPORT_INVERTED_ALIAS_MAP = _Batch26IR1_MappingProxyType(_batch26ir1_existing_inverted_alias_map)
