from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping


REPLAY_SCENARIO_CONTRACT_VERSION = "replay_scenario_profile_engine_v1"

REPLAY_REQUIRED_SCENARIOS = (
    "missing_futures_feed",
    "missing_selected_option_feed",
    "stale_futures_feed",
    "stale_selected_option_feed",
    "dhan_context_unavailable",
    "dhan_context_stale",
    "oi_ladder_missing",
    "oi_wall_shock",
    "wide_spread",
    "low_depth",
    "high_slippage",
    "packet_gaps",
    "timestamp_skew",
    "event_burst",
    "liquidity_shock",
    "forced_risk_veto",
    "full_fill",
    "partial_fill",
    "no_fill",
    "rejected",
    "forced_flatten",
    "session_close",
)

REPLAY_SCENARIO_REQUIRED_PROFILE_FIELDS = (
    "scenario_id",
    "family",
    "description",
    "row_effects",
    "risk_effects",
    "execution_effects",
    "manifest_tags",
    "explicit_assumption",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)


@dataclass(frozen=True)
class ReplayScenarioProfile:
    scenario_id: str
    family: str
    description: str
    row_effects: dict[str, Any]
    risk_effects: dict[str, Any]
    execution_effects: dict[str, Any]
    manifest_tags: tuple[str, ...]
    explicit_assumption: bool = True
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    broker_calls_allowed: bool = False
    live_redis_writes_allowed: bool = False
    production_doctrine_changed: bool = False


def _profile(
    scenario_id: str,
    family: str,
    description: str,
    *,
    row_effects: Mapping[str, Any] | None = None,
    risk_effects: Mapping[str, Any] | None = None,
    execution_effects: Mapping[str, Any] | None = None,
    manifest_tags: tuple[str, ...] | list[str] | None = None,
) -> ReplayScenarioProfile:
    return ReplayScenarioProfile(
        scenario_id=scenario_id,
        family=family,
        description=description,
        row_effects=dict(row_effects or {}),
        risk_effects=dict(risk_effects or {}),
        execution_effects=dict(execution_effects or {}),
        manifest_tags=tuple(str(x) for x in (manifest_tags or (scenario_id, family))),
    )


REPLAY_SCENARIO_PROFILES = {
    "missing_futures_feed": _profile(
        "missing_futures_feed",
        "feed_availability",
        "Simulate futures feed missing from replay row.",
        row_effects={
            "fut_missing": True,
            "fut_ltp": None,
            "fut_best_bid": None,
            "fut_best_ask": None,
            "fut_local_ts": None,
            "data_valid": False,
            "scenario_blocker": "missing_futures_feed",
        },
    ),
    "missing_selected_option_feed": _profile(
        "missing_selected_option_feed",
        "feed_availability",
        "Simulate selected option feed missing from replay row.",
        row_effects={
            "selected_option_missing": True,
            "opt_ltp": None,
            "opt_best_bid": None,
            "opt_best_ask": None,
            "opt_local_ts": None,
            "data_valid": False,
            "scenario_blocker": "missing_selected_option_feed",
        },
    ),
    "stale_futures_feed": _profile(
        "stale_futures_feed",
        "feed_freshness",
        "Simulate stale futures feed.",
        row_effects={
            "fut_stale": True,
            "fut_age_ms": 999999,
            "fut_local_ts": 0,
            "scenario_blocker": "stale_futures_feed",
        },
    ),
    "stale_selected_option_feed": _profile(
        "stale_selected_option_feed",
        "feed_freshness",
        "Simulate stale selected option feed.",
        row_effects={
            "selected_option_stale": True,
            "opt_age_ms": 999999,
            "opt_local_ts": 0,
            "scenario_blocker": "stale_selected_option_feed",
        },
    ),
    "dhan_context_unavailable": _profile(
        "dhan_context_unavailable",
        "provider_context",
        "Simulate unavailable Dhan context.",
        row_effects={
            "dhan_context_status": "UNAVAILABLE",
            "chain_context_fresh": False,
            "dhan_context_ready": False,
            "provider_ready_miso": False,
            "dhan_context_stale_reason": "scenario_dhan_context_unavailable",
        },
    ),
    "dhan_context_stale": _profile(
        "dhan_context_stale",
        "provider_context",
        "Simulate stale Dhan context.",
        row_effects={
            "dhan_context_status": "STALE",
            "chain_context_fresh": False,
            "dhan_context_age_ms": 999999,
            "dhan_context_stale_reason": "scenario_dhan_context_stale",
            "provider_ready_miso": False,
        },
    ),
    "oi_ladder_missing": _profile(
        "oi_ladder_missing",
        "oi_context",
        "Simulate missing OI ladder context.",
        row_effects={
            "oi_context_fresh": False,
            "call_oi_ladder_json": None,
            "put_oi_ladder_json": None,
            "nearest_call_wall": None,
            "nearest_put_wall": None,
            "oi_wall_strength": 0.0,
            "scenario_blocker": "oi_ladder_missing",
        },
    ),
    "oi_wall_shock": _profile(
        "oi_wall_shock",
        "oi_context",
        "Simulate sudden OI wall shock.",
        row_effects={
            "oi_context_fresh": True,
            "oi_wall_shock": True,
            "nearest_call_wall": 22600,
            "nearest_put_wall": 22400,
            "oi_wall_strength": 9.99,
            "oi_wall_blocking_side": "CALL",
            "oi_wall_context": {
                "shock": True,
                "nearest_call_wall": 22600,
                "nearest_put_wall": 22400,
                "oi_wall_strength": 9.99
            },
        },
    ),
    "wide_spread": _profile(
        "wide_spread",
        "liquidity",
        "Simulate wide selected option spread.",
        row_effects={
            "wide_spread": True,
            "opt_best_bid": 100.0,
            "opt_best_ask": 110.0,
            "opt_spread": 10.0,
            "spread_quality_ok": False,
        },
    ),
    "low_depth": _profile(
        "low_depth",
        "liquidity",
        "Simulate low selected option depth.",
        row_effects={
            "low_depth": True,
            "opt_bid_qty_1": 1,
            "opt_ask_qty_1": 1,
            "depth_quality_ok": False,
        },
    ),
    "high_slippage": _profile(
        "high_slippage",
        "execution_assumption",
        "Simulate high slippage assumption.",
        execution_effects={
            "slippage_points": 5.0,
            "fill_policy": "FULL_FILL",
        },
    ),
    "packet_gaps": _profile(
        "packet_gaps",
        "event_integrity",
        "Simulate packet gaps.",
        row_effects={
            "packet_gap_detected": True,
            "sequence_gap": 5,
            "event_integrity_ok": False,
        },
    ),
    "timestamp_skew": _profile(
        "timestamp_skew",
        "event_integrity",
        "Simulate timestamp skew.",
        row_effects={
            "timestamp_skew_detected": True,
            "exchange_ts_ns": 1,
            "local_ts_ns": 999999999999,
            "event_integrity_ok": False,
        },
    ),
    "event_burst": _profile(
        "event_burst",
        "event_integrity",
        "Simulate event burst.",
        row_effects={
            "event_burst": True,
            "events_in_window": 250,
            "event_burst_intensity": "HIGH",
        },
    ),
    "liquidity_shock": _profile(
        "liquidity_shock",
        "liquidity",
        "Simulate sudden liquidity shock.",
        row_effects={
            "liquidity_shock": True,
            "wide_spread": True,
            "low_depth": True,
            "opt_bid_qty_1": 1,
            "opt_ask_qty_1": 1,
            "opt_spread": 20.0,
            "depth_quality_ok": False,
            "spread_quality_ok": False,
        },
        execution_effects={
            "slippage_points": 8.0,
            "fill_policy": "PARTIAL_FILL",
            "partial_fill_ratio": 0.25,
        },
    ),
    "forced_risk_veto": _profile(
        "forced_risk_veto",
        "risk",
        "Force replay risk veto.",
        risk_effects={
            "force_veto_reasons": ("forced_replay_scenario_veto",),
        },
    ),
    "full_fill": _profile(
        "full_fill",
        "execution_assumption",
        "Force replay full-fill assumption.",
        execution_effects={
            "fill_policy": "FULL_FILL",
        },
    ),
    "partial_fill": _profile(
        "partial_fill",
        "execution_assumption",
        "Force replay partial-fill assumption.",
        execution_effects={
            "fill_policy": "PARTIAL_FILL",
            "partial_fill_ratio": 0.4,
        },
    ),
    "no_fill": _profile(
        "no_fill",
        "execution_assumption",
        "Force replay no-fill assumption.",
        execution_effects={
            "fill_policy": "NO_FILL",
        },
    ),
    "rejected": _profile(
        "rejected",
        "execution_assumption",
        "Force replay rejected-fill assumption.",
        execution_effects={
            "fill_policy": "REJECTED",
            "reject_reason": "scenario_rejected",
        },
    ),
    "forced_flatten": _profile(
        "forced_flatten",
        "session_control",
        "Simulate forced flatten scenario.",
        row_effects={
            "forced_flatten_requested": True,
            "flatten_reason": "scenario_forced_flatten",
        },
        risk_effects={
            "force_veto_reasons": ("forced_flatten_replay_only",),
        },
    ),
    "session_close": _profile(
        "session_close",
        "session_control",
        "Simulate session close scenario.",
        row_effects={
            "session_close": True,
            "session_close_lock": True,
            "last_fresh_entry_block": True,
            "flatten_reason": "scenario_session_close",
        },
        risk_effects={
            "force_veto_reasons": ("session_close_replay_only",),
        },
    ),
}


def replay_scenario_profile(scenario_id: str) -> dict[str, Any]:
    if scenario_id not in REPLAY_SCENARIO_PROFILES:
        raise KeyError(f"unknown replay scenario: {scenario_id}")
    profile = REPLAY_SCENARIO_PROFILES[scenario_id]
    return {
        "schema_version": REPLAY_SCENARIO_CONTRACT_VERSION,
        "scenario_id": profile.scenario_id,
        "family": profile.family,
        "description": profile.description,
        "row_effects": deepcopy(profile.row_effects),
        "risk_effects": deepcopy(profile.risk_effects),
        "execution_effects": deepcopy(profile.execution_effects),
        "manifest_tags": tuple(profile.manifest_tags),
        "explicit_assumption": profile.explicit_assumption,
        "paper_armed_approved": profile.paper_armed_approved,
        "live_trading_approved": profile.live_trading_approved,
        "execution_arming_created": profile.execution_arming_created,
        "broker_calls_allowed": profile.broker_calls_allowed,
        "live_redis_writes_allowed": profile.live_redis_writes_allowed,
        "production_doctrine_changed": profile.production_doctrine_changed,
    }


def validate_replay_scenario_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(field for field in REPLAY_SCENARIO_REQUIRED_PROFILE_FIELDS if field not in profile)
    no_live_ok = (
        profile.get("paper_armed_approved") is False
        and profile.get("live_trading_approved") is False
        and profile.get("execution_arming_created") is False
        and profile.get("broker_calls_allowed") is False
        and profile.get("live_redis_writes_allowed") is False
        and profile.get("production_doctrine_changed") is False
    )
    explicit_ok = profile.get("explicit_assumption") is True
    ok = bool(not missing and no_live_ok and explicit_ok)
    return {
        "ok": ok,
        "missing": missing,
        "no_live_ok": no_live_ok,
        "explicit_ok": explicit_ok,
    }


def list_replay_scenario_profiles() -> tuple[dict[str, Any], ...]:
    return tuple(replay_scenario_profile(scenario_id) for scenario_id in REPLAY_REQUIRED_SCENARIOS)


def apply_replay_scenario_to_row(row: Mapping[str, Any], scenario_id: str) -> dict[str, Any]:
    profile = replay_scenario_profile(scenario_id)
    new_row = dict(deepcopy(dict(row)))
    new_row.update(deepcopy(profile["row_effects"]))
    tags = list(new_row.get("scenario_tags") or [])
    tags.extend(profile["manifest_tags"])
    new_row["scenario_id"] = scenario_id
    new_row["scenario_tags"] = tuple(dict.fromkeys(str(x) for x in tags))
    new_row["explicit_assumption"] = True
    new_row["replay_only"] = True
    new_row["paper_armed_approved"] = False
    new_row["live_trading_approved"] = False
    new_row["production_doctrine_changed"] = False
    return new_row


def scenario_risk_effects(scenario_id: str) -> dict[str, Any]:
    return deepcopy(replay_scenario_profile(scenario_id)["risk_effects"])


def scenario_execution_effects(scenario_id: str) -> dict[str, Any]:
    return deepcopy(replay_scenario_profile(scenario_id)["execution_effects"])


def build_scenario_execution_assumption(
    scenario_id: str,
    *,
    base: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    assumption = {
        "fill_policy": "FULL_FILL",
        "requested_qty": 75,
        "partial_fill_ratio": 0.5,
        "entry_reference_price": 100.0,
        "exit_reference_price": 104.0,
        "slippage_points": 0.5,
        "transaction_cost_points": 0.25,
        "reject_reason": "replay_scenario_reject",
    }
    if base:
        assumption.update(dict(base))
    assumption.update(scenario_execution_effects(scenario_id))
    assumption["scenario_id"] = scenario_id
    assumption["explicit_assumption"] = True
    assumption["paper_armed_approved"] = False
    assumption["live_trading_approved"] = False
    assumption["real_order_sent"] = False
    assumption["broker_calls_executed"] = False
    assumption["production_doctrine_changed"] = False
    return assumption


def replay_scenario_manifest() -> dict[str, Any]:
    profiles = list_replay_scenario_profiles()
    return {
        "schema_version": "replay_scenario_profile_manifest_v1",
        "scenario_count": len(profiles),
        "required_scenarios": REPLAY_REQUIRED_SCENARIOS,
        "profiles": profiles,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
        "scenario_profile_shape": "PROVEN_BY_27J",
        "scenario_application_shape": "PROVEN_BY_27J",
        "full_replay_scenario_outcome_parity": "NOT_PROVEN_IN_27J",
    }


def replay_scenario_manifest_json() -> str:
    return json.dumps(replay_scenario_manifest(), indent=2, sort_keys=True, default=str)


def replay_scenario_engine_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_SCENARIO_CONTRACT_VERSION,
        "required_scenarios": REPLAY_REQUIRED_SCENARIOS,
        "required_profile_fields": REPLAY_SCENARIO_REQUIRED_PROFILE_FIELDS,
        "scenario_profile_shape": "PROVEN_BY_27J",
        "scenario_application_shape": "PROVEN_BY_27J",
        "full_replay_scenario_outcome_parity": "NOT_PROVEN_IN_27J",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_SCENARIO_CONTRACT_VERSION",
    "REPLAY_REQUIRED_SCENARIOS",
    "REPLAY_SCENARIO_REQUIRED_PROFILE_FIELDS",
    "ReplayScenarioProfile",
    "REPLAY_SCENARIO_PROFILES",
    "replay_scenario_profile",
    "validate_replay_scenario_profile",
    "list_replay_scenario_profiles",
    "apply_replay_scenario_to_row",
    "scenario_risk_effects",
    "scenario_execution_effects",
    "build_scenario_execution_assumption",
    "replay_scenario_manifest",
    "replay_scenario_manifest_json",
    "replay_scenario_engine_contract_summary",
)))
