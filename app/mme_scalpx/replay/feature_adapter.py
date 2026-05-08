from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from app.mme_scalpx.replay.live_adapter import publish_replay_live_shape
from app.mme_scalpx.replay.transport import LocalReplayTransport


REPLAY_FEATURE_ADAPTER_CONTRACT_VERSION = "replay_feature_family_adapter_v1"

REPLAY_FEATURE_FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
REPLAY_FEATURE_SIDES = ("CALL", "PUT")

REPLAY_FEATURE_REQUIRED_PAYLOAD_FIELDS = (
    "schema_version",
    "run_id",
    "family_features",
    "family_surfaces",
    "family_features_json",
    "family_surfaces_json",
    "family_frames_json",
    "provider_ready_miso",
    "dhan_context_fresh",
    "oi_context_fresh",
    "branch_side",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)

REPLAY_FAMILY_REQUIRED_SURFACE_TERMS = {
    "MIST": (
        "trend_confirmed",
        "pullback_detected",
        "resume_confirmed",
        "micro_trap_flag",
        "futures_impulse_ok",
    ),
    "MISB": (
        "shelf_confirmed",
        "breakout_triggered",
        "breakout_accepted",
        "shelf_high",
        "shelf_low",
    ),
    "MISC": (
        "compression_detected",
        "directional_breakout_triggered",
        "expansion_accepted",
        "retest_monitor_active",
        "hesitation_retest",
    ),
    "MISR": (
        "active_zone_valid",
        "active_zone",
        "fake_break",
        "range_reentry",
        "flow_flip",
        "trap_event_id",
    ),
    "MISO": (
        "burst_detected",
        "burst_event_id",
        "aggression_ok",
        "tape_speed_ok",
        "imbalance_persistence_ok",
        "queue_reload_veto",
        "provider_ready_miso",
        "oi_wall_context",
    ),
}


@dataclass(frozen=True)
class ReplayFeatureAdapterResult:
    schema_version: str
    run_id: str
    payload: dict[str, Any]
    family_features_json: str
    family_surfaces_json: str
    family_frames_json: str
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    production_doctrine_changed: bool = False


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _row_get(row: Mapping[str, Any], key: str, default: Any = None) -> Any:
    return row[key] if key in row else default


def _bool_row(row: Mapping[str, Any], key: str, default: bool = False) -> bool:
    value = _row_get(row, key, default)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "ok", "pass"}
    return bool(value)


def _family_side_surface(row: Mapping[str, Any], *, family: str, side: str) -> dict[str, Any]:
    prefix = f"{family.lower()}_{side.lower()}_"
    common = {
        "family": family,
        "branch_side": side,
        "side": side,
        "surface_kind": "replay_feature_family_surface",
        "replay_only": True,
        "source": "replay_feature_adapter",
        "full_live_feature_computation_parity": "NOT_PROVEN_IN_27G",
        "strategy_decision_generated": False,
    }

    if family == "MIST":
        specific = {
            "trend_confirmed": _bool_row(row, prefix + "trend_confirmed", _bool_row(row, "trend_confirmed", False)),
            "pullback_detected": _bool_row(row, prefix + "pullback_detected", _bool_row(row, "pullback_detected", False)),
            "resume_confirmed": _bool_row(row, prefix + "resume_confirmed", _bool_row(row, "resume_confirmed", False)),
            "micro_trap_flag": _bool_row(row, prefix + "micro_trap_flag", _bool_row(row, "micro_trap_flag", False)),
            "futures_impulse_ok": _bool_row(row, prefix + "futures_impulse_ok", _bool_row(row, "futures_impulse_ok", False)),
        }
    elif family == "MISB":
        specific = {
            "shelf_confirmed": _bool_row(row, prefix + "shelf_confirmed", _bool_row(row, "shelf_confirmed", False)),
            "breakout_triggered": _bool_row(row, prefix + "breakout_triggered", _bool_row(row, "breakout_triggered", False)),
            "breakout_accepted": _bool_row(row, prefix + "breakout_accepted", _bool_row(row, "breakout_accepted", False)),
            "shelf_high": _row_get(row, prefix + "shelf_high", _row_get(row, "shelf_high")),
            "shelf_low": _row_get(row, prefix + "shelf_low", _row_get(row, "shelf_low")),
        }
    elif family == "MISC":
        specific = {
            "compression_detected": _bool_row(row, prefix + "compression_detected", _bool_row(row, "compression_detected", False)),
            "directional_breakout_triggered": _bool_row(row, prefix + "directional_breakout_triggered", _bool_row(row, "directional_breakout_triggered", False)),
            "expansion_accepted": _bool_row(row, prefix + "expansion_accepted", _bool_row(row, "expansion_accepted", False)),
            "retest_monitor_active": _bool_row(row, prefix + "retest_monitor_active", _bool_row(row, "retest_monitor_active", False)),
            "hesitation_retest": _bool_row(row, prefix + "hesitation_retest", _bool_row(row, "hesitation_retest", False)),
        }
    elif family == "MISR":
        specific = {
            "active_zone_valid": _bool_row(row, prefix + "active_zone_valid", _bool_row(row, "active_zone_valid", False)),
            "active_zone": _row_get(row, prefix + "active_zone", _row_get(row, "active_zone")),
            "fake_break": _bool_row(row, prefix + "fake_break", _bool_row(row, "fake_break", False)),
            "range_reentry": _bool_row(row, prefix + "range_reentry", _bool_row(row, "range_reentry", False)),
            "flow_flip": _bool_row(row, prefix + "flow_flip", _bool_row(row, "flow_flip", False)),
            "trap_event_id": _row_get(row, prefix + "trap_event_id", _row_get(row, "trap_event_id")),
        }
    elif family == "MISO":
        specific = {
            "burst_detected": _bool_row(row, prefix + "burst_detected", _bool_row(row, "burst_detected", False)),
            "burst_event_id": _row_get(row, prefix + "burst_event_id", _row_get(row, "burst_event_id")),
            "aggression_ok": _bool_row(row, prefix + "aggression_ok", _bool_row(row, "aggression_ok", False)),
            "tape_speed_ok": _bool_row(row, prefix + "tape_speed_ok", _bool_row(row, "tape_speed_ok", False)),
            "imbalance_persistence_ok": _bool_row(row, prefix + "imbalance_persistence_ok", _bool_row(row, "imbalance_persistence_ok", False)),
            "queue_reload_veto": _bool_row(row, prefix + "queue_reload_veto", _bool_row(row, "queue_reload_veto", False)),
            "provider_ready_miso": _bool_row(row, "provider_ready_miso", False),
            "oi_wall_context": _row_get(row, "oi_wall_context", {
                "nearest_call_wall": _row_get(row, "nearest_call_wall"),
                "nearest_put_wall": _row_get(row, "nearest_put_wall"),
                "oi_wall_strength": _row_get(row, "oi_wall_strength"),
            }),
        }
    else:
        raise KeyError(f"unknown replay feature family: {family}")

    common.update(specific)
    return common


def build_replay_family_surfaces(row: Mapping[str, Any]) -> dict[str, Any]:
    family_surfaces: dict[str, Any] = {}
    for family in REPLAY_FEATURE_FAMILIES:
        family_surfaces[family] = {}
        for side in REPLAY_FEATURE_SIDES:
            family_surfaces[family][side] = _family_side_surface(row, family=family, side=side)
    return family_surfaces


def build_replay_family_features(row: Mapping[str, Any]) -> dict[str, Any]:
    surfaces = build_replay_family_surfaces(row)
    return {
        "schema_version": "replay_family_features_v1",
        "replay_only": True,
        "families": tuple(REPLAY_FEATURE_FAMILIES),
        "sides": tuple(REPLAY_FEATURE_SIDES),
        "provider_ready_miso": _bool_row(row, "provider_ready_miso", False),
        "dhan_context_fresh": _bool_row(row, "chain_context_fresh", _bool_row(row, "dhan_context_fresh", False)),
        "oi_context_fresh": _bool_row(row, "oi_context_fresh", False),
        "selected_option_identity": {
            "security_id": _row_get(row, "selected_security_id", _row_get(row, "security_id")),
            "tradingsymbol": _row_get(row, "selected_tradingsymbol", _row_get(row, "tradingsymbol")),
            "expiry": _row_get(row, "selected_expiry", _row_get(row, "expiry")),
            "strike": _row_get(row, "selected_strike", _row_get(row, "strike")),
            "option_type": _row_get(row, "selected_option_type", _row_get(row, "option_type")),
        },
        "family_surfaces": surfaces,
    }


def build_replay_feature_payload(
    *,
    run_id: str,
    row: Mapping[str, Any],
    branch_side: str = "BOTH",
) -> ReplayFeatureAdapterResult:
    family_surfaces = build_replay_family_surfaces(row)
    family_features = build_replay_family_features(row)
    family_frames = {
        "schema_version": "replay_family_frames_v1",
        "replay_only": True,
        "row": deepcopy(dict(row)),
        "surface_count": len(REPLAY_FEATURE_FAMILIES) * len(REPLAY_FEATURE_SIDES),
    }

    family_features_json = _canonical_json(family_features)
    family_surfaces_json = _canonical_json(family_surfaces)
    family_frames_json = _canonical_json(family_frames)

    payload = {
        "schema_version": REPLAY_FEATURE_ADAPTER_CONTRACT_VERSION,
        "run_id": str(run_id),
        "branch_side": str(branch_side),
        "family_features": family_features,
        "family_surfaces": family_surfaces,
        "family_frames": family_frames,
        "family_features_json": family_features_json,
        "family_surfaces_json": family_surfaces_json,
        "family_frames_json": family_frames_json,
        "provider_ready_miso": family_features["provider_ready_miso"],
        "dhan_context_fresh": family_features["dhan_context_fresh"],
        "oi_context_fresh": family_features["oi_context_fresh"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "strategy_decision_generated": False,
        "production_doctrine_changed": False,
    }

    return ReplayFeatureAdapterResult(
        schema_version=REPLAY_FEATURE_ADAPTER_CONTRACT_VERSION,
        run_id=str(run_id),
        payload=payload,
        family_features_json=family_features_json,
        family_surfaces_json=family_surfaces_json,
        family_frames_json=family_frames_json,
    )


def publish_replay_feature_payload(
    transport: LocalReplayTransport,
    *,
    run_id: str,
    row: Mapping[str, Any],
    branch_side: str = "BOTH",
    event_ts_ns: int | None = None,
    sequence_id: int | None = None,
) -> dict[str, Any]:
    result = build_replay_feature_payload(run_id=run_id, row=row, branch_side=branch_side)
    return publish_replay_live_shape(
        transport,
        surface="feature_payload",
        row=result.payload,
        event_ts_ns=event_ts_ns,
        sequence_id=sequence_id,
    )


def validate_replay_feature_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(name for name in REPLAY_FEATURE_REQUIRED_PAYLOAD_FIELDS if name not in payload)
    family_surfaces = payload.get("family_surfaces") or {}
    family_features_json = payload.get("family_features_json")
    family_surfaces_json = payload.get("family_surfaces_json")
    family_frames_json = payload.get("family_frames_json")

    family_missing: dict[str, Any] = {}
    for family in REPLAY_FEATURE_FAMILIES:
        if family not in family_surfaces:
            family_missing[family] = {"family_missing": True}
            continue
        family_missing[family] = {}
        for side in REPLAY_FEATURE_SIDES:
            surface = family_surfaces.get(family, {}).get(side, {})
            missing_terms = tuple(
                term for term in REPLAY_FAMILY_REQUIRED_SURFACE_TERMS[family]
                if term not in surface
            )
            family_missing[family][side] = missing_terms

    call_put_ok = all(
        family in family_surfaces
        and all(side in family_surfaces[family] for side in REPLAY_FEATURE_SIDES)
        for family in REPLAY_FEATURE_FAMILIES
    )

    family_terms_ok = all(
        not terms
        for family_value in family_missing.values()
        if isinstance(family_value, dict)
        for terms in family_value.values()
        if isinstance(terms, tuple)
    )

    json_ok = all(isinstance(x, str) and len(x) > 2 for x in (
        family_features_json,
        family_surfaces_json,
        family_frames_json,
    ))

    no_approval_ok = (
        payload.get("paper_armed_approved") is False
        and payload.get("live_trading_approved") is False
        and payload.get("execution_arming_created") is False
        and payload.get("strategy_decision_generated") is False
        and payload.get("production_doctrine_changed") is False
    )

    ok = bool(not missing and call_put_ok and family_terms_ok and json_ok and no_approval_ok)
    return {
        "ok": ok,
        "missing_payload_fields": missing,
        "call_put_ok": call_put_ok,
        "family_terms_ok": family_terms_ok,
        "family_missing": family_missing,
        "json_ok": json_ok,
        "no_approval_ok": no_approval_ok,
    }


def replay_feature_adapter_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_FEATURE_ADAPTER_CONTRACT_VERSION,
        "families": REPLAY_FEATURE_FAMILIES,
        "sides": REPLAY_FEATURE_SIDES,
        "required_payload_fields": REPLAY_FEATURE_REQUIRED_PAYLOAD_FIELDS,
        "required_surface_terms": REPLAY_FAMILY_REQUIRED_SURFACE_TERMS,
        "full_live_feature_computation_parity": "NOT_PROVEN_IN_27G",
        "strategy_family_decision_parity": "NOT_PROVEN_IN_27G",
        "safe_payload_shape_parity": "PROVEN_BY_27G",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_FEATURE_ADAPTER_CONTRACT_VERSION",
    "REPLAY_FEATURE_FAMILIES",
    "REPLAY_FEATURE_SIDES",
    "REPLAY_FEATURE_REQUIRED_PAYLOAD_FIELDS",
    "REPLAY_FAMILY_REQUIRED_SURFACE_TERMS",
    "ReplayFeatureAdapterResult",
    "build_replay_family_surfaces",
    "build_replay_family_features",
    "build_replay_feature_payload",
    "publish_replay_feature_payload",
    "validate_replay_feature_payload",
    "replay_feature_adapter_contract_summary",
)))
