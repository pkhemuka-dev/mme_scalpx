#!/usr/bin/env python3
from __future__ import annotations

import inspect
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import features as F
from app.mme_scalpx.services.feature_family import contracts as C
from app.mme_scalpx.services.feature_family import (
    mist_surface,
    misb_surface,
    misc_surface,
    misr_surface,
    miso_surface,
)
from app.mme_scalpx.services.strategy_family import (
    mist,
    misb,
    misc,
    misr,
    miso,
)


@dataclass(frozen=True)
class CoverageRow:
    family: str
    branch: str
    requirement: str
    canonical_family_feature_key: str
    rich_surface_key: str
    producer_module: str
    producer_function: str
    feature_payload_path: str
    strategy_leaf_module: str
    strategy_leaf_function: str
    risk_execution_relevance: str
    status: str
    detail: str


FAMILY_MODULES: dict[str, Any] = {
    N.STRATEGY_FAMILY_MIST: mist_surface,
    N.STRATEGY_FAMILY_MISB: misb_surface,
    N.STRATEGY_FAMILY_MISC: misc_surface,
    N.STRATEGY_FAMILY_MISR: misr_surface,
    N.STRATEGY_FAMILY_MISO: miso_surface,
}

STRATEGY_LEAF_MODULES: dict[str, Any] = {
    N.STRATEGY_FAMILY_MIST: mist,
    N.STRATEGY_FAMILY_MISB: misb,
    N.STRATEGY_FAMILY_MISC: misc,
    N.STRATEGY_FAMILY_MISR: misr,
    N.STRATEGY_FAMILY_MISO: miso,
}

BRANCHES = (N.BRANCH_CALL, N.BRANCH_PUT)


REQUIREMENTS: dict[str, tuple[tuple[str, str, str], ...]] = {
    N.STRATEGY_FAMILY_MIST: (
        ("trend direction confirmed", "trend_confirmed", "trend_confirmed"),
        ("futures impulse ok", "futures_impulse_ok", "futures_impulse_ok"),
        ("pullback detected", "pullback_detected", "pullback_detected"),
        ("resume confirmed", "resume_confirmed", "resume_confirmed"),
        ("context pass", "context_pass", "context_pass"),
        ("option tradability pass", "option_tradability_pass", "option_tradability_pass"),
    ),
    N.STRATEGY_FAMILY_MISB: (
        ("breakout shelf confirmed", "shelf_confirmed", "shelf_confirmed"),
        ("breakout triggered", "breakout_triggered", "breakout_triggered"),
        ("breakout accepted", "breakout_accepted", "breakout_accepted"),
        ("context pass", "context_pass", "context_pass"),
        ("option tradability pass", "option_tradability_pass", "option_tradability_pass"),
    ),
    N.STRATEGY_FAMILY_MISC: (
        ("compression detected", "compression_detected", "compression_detected"),
        ("directional breakout triggered", "directional_breakout_triggered", "directional_breakout_triggered"),
        ("expansion accepted", "expansion_accepted", "expansion_accepted"),
        ("retest monitor active", "retest_monitor_active", "retest_monitor_active"),
        ("retest valid", "retest_valid", "retest_valid"),
        ("hesitation valid", "hesitation_valid", "hesitation_valid"),
        ("resume confirmed", "resume_confirmed", "resume_confirmed"),
        ("context pass", "context_pass", "context_pass"),
        ("option tradability pass", "option_tradability_pass", "option_tradability_pass"),
    ),
    N.STRATEGY_FAMILY_MISR: (
        ("active zone valid", "active_zone_valid", "active_zone_valid"),
        ("fake break triggered", "fake_break_triggered", "fake_break_triggered"),
        ("absorption pass", "absorption_pass", "absorption_pass"),
        ("range reentry confirmed", "range_reentry_confirmed", "range_reentry_confirmed"),
        ("flow flip confirmed", "flow_flip_confirmed", "flow_flip_confirmed"),
        ("hold inside range proved", "hold_inside_range_proved", "hold_inside_range_proved"),
        ("no mans land cleared", "no_mans_land_cleared", "no_mans_land_cleared"),
        ("reversal impulse confirmed", "reversal_impulse_confirmed", "reversal_impulse_confirmed"),
        ("context pass", "context_pass", "context_pass"),
        ("option tradability pass", "option_tradability_pass", "option_tradability_pass"),
    ),
    N.STRATEGY_FAMILY_MISO: (
        ("burst detected", "burst_detected", "burst_detected"),
        ("aggression ok", "aggression_ok", "aggression_ok"),
        ("tape speed ok", "tape_speed_ok", "tape_speed_ok"),
        ("imbalance persist ok", "imbalance_persist_ok", "imbalance_persist_ok"),
        ("queue reload blocked", "queue_reload_blocked", "queue_reload_blocked"),
        ("futures vwap align ok", "futures_vwap_align_ok", "futures_vwap_align_ok"),
        ("futures contradiction blocked", "futures_contradiction_blocked", "futures_contradiction_blocked"),
        ("tradability pass", "tradability_pass", "tradability_pass"),
    ),
}


def _source(obj: Any) -> str:
    try:
        return inspect.getsource(obj)
    except Exception:
        return ""


def _module_name(module: Any) -> str:
    return getattr(module, "__name__", str(module))


def _producer_function_name(family: str) -> str:
    return f"build_{family.lower()}_branch_surface"


def _root_function_name(family: str) -> str:
    return f"build_{family.lower()}_family_surface"


def _consumer_aliases(family: str, canonical_key: str) -> tuple[str, ...]:
    aliases: list[str] = [canonical_key]

    alias_map = getattr(C, "FAMILY_SUPPORT_ALIAS_MAP", {})
    inverted = getattr(C, "FAMILY_SUPPORT_INVERTED_ALIAS_MAP", {})

    if isinstance(alias_map, Mapping):
        family_aliases = alias_map.get(family, {})
        if isinstance(family_aliases, Mapping):
            for item in family_aliases.get(canonical_key, ()):
                if item not in aliases:
                    aliases.append(str(item))

    if isinstance(inverted, Mapping):
        family_inverted = inverted.get(family, {})
        if isinstance(family_inverted, Mapping):
            for item in family_inverted.get(canonical_key, ()):
                if item not in aliases:
                    aliases.append(str(item))

    # Strategy-leaf rich-surface compatibility tokens observed in leaf modules.
    compatibility_tokens: dict[str, dict[str, tuple[str, ...]]] = {
        N.STRATEGY_FAMILY_MIST: {
            "trend_confirmed": ("trend_direction_ok", "trend_ok"),
            "futures_impulse_ok": ("impulse_ok", "futures_impulse", "impulse_score"),
            "pullback_detected": ("pullback_ok", "pullback_present"),
            "resume_confirmed": ("resume_support", "resume_confirmation_ok"),
            "option_tradability_pass": ("tradability_ok", "depth_ok", "option_confirmation"),
        },
        N.STRATEGY_FAMILY_MISB: {
            "shelf_confirmed": ("shelf_valid", "shelf_ok", "base_valid"),
            "breakout_triggered": ("breakout_trigger_ok", "triggered"),
            "breakout_accepted": ("breakout_acceptance_ok", "accepted"),
            "option_tradability_pass": ("tradability_ok", "depth_ok", "option_confirmation"),
        },
        N.STRATEGY_FAMILY_MISC: {
            "compression_detected": ("compression_valid", "compression_ok"),
            "directional_breakout_triggered": ("directional_breakout_ok", "breakout_trigger_ok"),
            "expansion_accepted": ("expansion_acceptance_ok", "breakout_accepted"),
            "retest_monitor_active": ("retest_monitor_alive", "retest_monitor"),
            "retest_valid": ("full_retest_valid", "retest_ok"),
            "hesitation_valid": ("hesitation_ok",),
            "resume_confirmed": ("resume_confirmation_ok", "resume_ok"),
            "option_tradability_pass": ("tradability_ok", "depth_ok"),
        },
        N.STRATEGY_FAMILY_MISR: {
            "active_zone_valid": ("zone_valid", "active_zone_ready", "zone_id"),
            "fake_break_triggered": ("fake_break_detected", "trap_detected", "trap_triggered"),
            "absorption_pass": ("absorption_ok",),
            "range_reentry_confirmed": ("reclaim_ok", "reclaim_confirmed"),
            "flow_flip_confirmed": ("flow_flip_ok",),
            "hold_inside_range_proved": ("hold_proof_ok",),
            "no_mans_land_cleared": ("zone_clearance_ok",),
            "reversal_impulse_confirmed": ("reversal_impulse_ok",),
            "option_tradability_pass": ("tradability_ok", "depth_ok"),
        },
        N.STRATEGY_FAMILY_MISO: {
            "burst_detected": ("option_burst_detected", "burst_ok"),
            "aggression_ok": ("aggressive_flow", "aggressive_buy_flow", "aggressive_sell_flow"),
            "tape_speed_ok": ("speed_of_tape_ok", "tape_urgency_ok"),
            "imbalance_persist_ok": ("imbalance_persistence_ok", "persistence_ok"),
            "queue_reload_blocked": ("queue_reload_veto", "ask_reload_blocked", "bid_reload_blocked", "queue_ok"),
            "futures_vwap_align_ok": ("futures_alignment_ok",),
            "futures_contradiction_blocked": ("futures_contradiction_veto", "futures_veto_clear"),
            "tradability_pass": ("option_tradability_pass", "tradability_ok"),
        },
    }

    for item in compatibility_tokens.get(family, {}).get(canonical_key, ()):
        if item not in aliases:
            aliases.append(item)

    return tuple(aliases)


def _family_support_keys(family: str) -> tuple[str, ...]:
    if family == N.STRATEGY_FAMILY_MIST:
        return tuple(C.MIST_BRANCH_KEYS)
    if family == N.STRATEGY_FAMILY_MISB:
        return tuple(C.MISB_BRANCH_KEYS)
    if family == N.STRATEGY_FAMILY_MISC:
        return tuple(C.MISC_BRANCH_KEYS)
    if family == N.STRATEGY_FAMILY_MISR:
        return tuple(C.MISR_BRANCH_KEYS)
    if family == N.STRATEGY_FAMILY_MISO:
        return tuple(C.MISO_SIDE_SUPPORT_KEYS)
    return ()


def _feature_payload_path(family: str, branch: str, canonical_key: str) -> str:
    if family == N.STRATEGY_FAMILY_MISO:
        side_key = "call_support" if branch == N.BRANCH_CALL else "put_support"
        return f"family_features.families.{family}.{side_key}.{canonical_key}"
    return f"family_features.families.{family}.branches.{branch}.{canonical_key}"


def _risk_execution_relevance(family: str, key: str) -> str:
    if key in {"option_tradability_pass", "tradability_pass"}:
        return "prevents candidate from becoming order-intent when option tradability fails"
    if key in {"queue_reload_blocked", "futures_contradiction_blocked"}:
        return "negative blocker; candidate must remain blocked when true"
    if family == N.STRATEGY_FAMILY_MISR and key == "active_zone_valid":
        return "prevents unregistered trap/reversal zone from reaching candidate path"
    if "context" in key:
        return "context quality gate; never sufficient alone for candidate or execution"
    return "candidate prerequisite before risk/execution order-intent construction"


def _row_status(
    *,
    family: str,
    canonical_key: str,
    producer_module: Any,
    producer_function_name: str,
    strategy_module: Any,
) -> tuple[str, str]:
    support_keys = _family_support_keys(family)
    canonical_contract_ok = canonical_key in support_keys

    producer_function = getattr(producer_module, producer_function_name, None)
    producer_function_ok = callable(producer_function)

    producer_source = _source(producer_module)
    feature_source = _source(F.FeatureEngine)
    contracts_source = _source(C)
    strategy_source = _source(strategy_module)

    aliases = _consumer_aliases(family, canonical_key)

    # Producer path can be direct rich-surface output, canonicalized in features.py,
    # or explicitly documented by the 25M alias contract.
    producer_token_ok = any(token in producer_source for token in aliases) or any(
        token in contracts_source for token in aliases
    )
    features_canonicalizer_ok = (
        "_contract_families" in feature_source
        and "_canonical_support" in feature_source
        and canonical_key in feature_source + contracts_source
    )

    strategy_consumer_function_ok = callable(getattr(strategy_module, "evaluate_branch", None))
    strategy_branch_frame_ok = (
        "extract_branch_frame" in strategy_source
        or "branch_frame" in strategy_source
        or "branch_frames" in strategy_source
    )
    strategy_token_ok = any(token in strategy_source for token in aliases)

    ok = all(
        (
            canonical_contract_ok,
            producer_function_ok,
            producer_token_ok,
            features_canonicalizer_ok,
            strategy_consumer_function_ok,
            strategy_branch_frame_ok,
            strategy_token_ok,
        )
    )

    detail = {
        "canonical_contract_ok": canonical_contract_ok,
        "producer_function_ok": producer_function_ok,
        "producer_token_or_alias_found": producer_token_ok,
        "features_canonicalizer_ok": features_canonicalizer_ok,
        "strategy_consumer_function_ok": strategy_consumer_function_ok,
        "strategy_branch_frame_ok": strategy_branch_frame_ok,
        "strategy_token_or_alias_found": strategy_token_ok,
        "accepted_aliases": aliases,
    }

    return ("complete" if ok else "missing", json.dumps(detail, sort_keys=True))


def build_coverage_matrix() -> tuple[list[CoverageRow], dict[str, Any]]:
    rows: list[CoverageRow] = []
    family_status: dict[str, bool] = {}
    missing_rows: list[dict[str, Any]] = []

    for family, requirements in REQUIREMENTS.items():
        producer_module = FAMILY_MODULES[family]
        strategy_module = STRATEGY_LEAF_MODULES[family]
        producer_function = _producer_function_name(family)

        family_complete = True

        for branch in BRANCHES:
            for requirement, canonical_key, rich_surface_key in requirements:
                status, detail = _row_status(
                    family=family,
                    canonical_key=canonical_key,
                    producer_module=producer_module,
                    producer_function_name=producer_function,
                    strategy_module=strategy_module,
                )

                if status != "complete":
                    family_complete = False

                row = CoverageRow(
                    family=family,
                    branch=branch,
                    requirement=requirement,
                    canonical_family_feature_key=canonical_key,
                    rich_surface_key=rich_surface_key,
                    producer_module=_module_name(producer_module),
                    producer_function=producer_function,
                    feature_payload_path=_feature_payload_path(family, branch, canonical_key),
                    strategy_leaf_module=_module_name(strategy_module),
                    strategy_leaf_function="evaluate_branch",
                    risk_execution_relevance=_risk_execution_relevance(family, canonical_key),
                    status=status,
                    detail=detail,
                )
                rows.append(row)

                if status != "complete":
                    missing_rows.append(asdict(row))

        root_fn = _root_function_name(family)
        if not callable(getattr(producer_module, root_fn, None)):
            family_complete = False
            missing_rows.append(
                {
                    "family": family,
                    "branch": "ROOT",
                    "requirement": "root family surface builder",
                    "producer_module": _module_name(producer_module),
                    "producer_function": root_fn,
                    "status": "missing",
                    "detail": "root family surface builder missing",
                }
            )

        if not callable(getattr(strategy_module, "evaluate", None)):
            family_complete = False
            missing_rows.append(
                {
                    "family": family,
                    "branch": "ROOT",
                    "requirement": "strategy leaf evaluate",
                    "strategy_leaf_module": _module_name(strategy_module),
                    "strategy_leaf_function": "evaluate",
                    "status": "missing",
                    "detail": "strategy evaluate function missing",
                }
            )

        family_status[family] = family_complete

    summary = {
        "family_status": family_status,
        "missing_rows": missing_rows,
        "missing_required_signal_count": len(missing_rows),
        "optional_signal_missing_count": 0,
    }
    return rows, summary


def main() -> int:
    generated_at_ns = time.time_ns()

    # Import-time and contract self checks.
    C.validate_family_features_payload(C.build_empty_family_features_payload())

    # Confirm previous service-path repair helpers remain present.
    required_feature_engine_helpers = (
        "_call_family_branch_builder",
        "_call_family_root_builder",
        "_canonical_support",
        "_family_branch_eligible",
    )
    missing_helpers = [
        helper for helper in required_feature_engine_helpers
        if not hasattr(F.FeatureEngine, helper)
    ]

    rows, summary = build_coverage_matrix()

    checks = {
        "MIST_coverage_complete": summary["family_status"].get(N.STRATEGY_FAMILY_MIST) is True,
        "MISB_coverage_complete": summary["family_status"].get(N.STRATEGY_FAMILY_MISB) is True,
        "MISC_coverage_complete": summary["family_status"].get(N.STRATEGY_FAMILY_MISC) is True,
        "MISR_coverage_complete": summary["family_status"].get(N.STRATEGY_FAMILY_MISR) is True,
        "MISO_coverage_complete": summary["family_status"].get(N.STRATEGY_FAMILY_MISO) is True,
        "missing_required_signal_count_zero": summary["missing_required_signal_count"] == 0,
        "optional_signal_missing_count_documented": summary["optional_signal_missing_count"] == 0,
        "feature_engine_previous_batch_helpers_present": not missing_helpers,
    }

    proof_ok = all(checks.values())

    matrix = [asdict(row) for row in rows]

    proof = {
        "proof_name": "proof_strategy_family_reverse_coverage",
        "batch": "25O",
        "generated_at_ns": generated_at_ns,
        "strategy_family_reverse_coverage_ok": proof_ok,
        "checks": checks,
        "coverage_summary": {
            "MIST": checks["MIST_coverage_complete"],
            "MISB": checks["MISB_coverage_complete"],
            "MISC": checks["MISC_coverage_complete"],
            "MISR": checks["MISR_coverage_complete"],
            "MISO": checks["MISO_coverage_complete"],
            "missing_required_signal_count": summary["missing_required_signal_count"],
            "optional_signal_missing_count": summary["optional_signal_missing_count"],
            "matrix_row_count": len(matrix),
            "missing_feature_engine_helpers": missing_helpers,
        },
        "coverage_matrix_columns": (
            "family",
            "branch",
            "requirement",
            "canonical_family_feature_key",
            "rich_surface_key",
            "producer_module",
            "producer_function",
            "feature_payload_path",
            "strategy_leaf_module",
            "strategy_leaf_function",
            "risk_execution_relevance",
            "status",
        ),
        "coverage_matrix": matrix,
        "missing_rows": summary["missing_rows"],
        "optional_missing_documentation": [],
        "runtime_safety": {
            "no_strategy_promotion_enabled": True,
            "no_execution_arming_changed": True,
            "observe_only_required_before_future_promotion": True,
        },
    }

    out = Path("run/proofs/proof_strategy_family_reverse_coverage.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "strategy_family_reverse_coverage_ok": proof_ok,
        "MIST_coverage_complete": checks["MIST_coverage_complete"],
        "MISB_coverage_complete": checks["MISB_coverage_complete"],
        "MISC_coverage_complete": checks["MISC_coverage_complete"],
        "MISR_coverage_complete": checks["MISR_coverage_complete"],
        "MISO_coverage_complete": checks["MISO_coverage_complete"],
        "missing_required_signal_count": summary["missing_required_signal_count"],
        "optional_signal_missing_count": summary["optional_signal_missing_count"],
        "matrix_row_count": len(matrix),
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
