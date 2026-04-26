#!/usr/bin/env python3
from __future__ import annotations

import json
import time
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


def _engine() -> F.FeatureEngine:
    class StubRedis:
        def hgetall(self, key: str) -> dict[str, Any]:
            return {}
    return F.FeatureEngine(redis_client=StubRedis())


def _shared_core() -> dict[str, Any]:
    return {
        "runtime_modes": {
            "classic": {"mode": getattr(N, "STRATEGY_RUNTIME_MODE_NORMAL", "NORMAL")},
            "miso": {"mode": getattr(N, "STRATEGY_RUNTIME_MODE_BASE_5DEPTH", "BASE-5DEPTH")},
        },
        "strike_selection": {
            "chain_context_ready": True,
            "shadow_call_strike": 25000.0,
            "shadow_put_strike": 25000.0,
        },
        "options": {
            "selected": {"side": getattr(N, "BRANCH_CALL", "CALL"), "strike": 25000.0},
        },
    }


def _empty_family_surfaces() -> dict[str, Any]:
    return {
        "families": {
            getattr(N, "STRATEGY_FAMILY_MIST", "MIST"): {"branches": {"CALL": {}, "PUT": {}}},
            getattr(N, "STRATEGY_FAMILY_MISB", "MISB"): {"branches": {"CALL": {}, "PUT": {}}},
            getattr(N, "STRATEGY_FAMILY_MISC", "MISC"): {"branches": {"CALL": {}, "PUT": {}}},
            getattr(N, "STRATEGY_FAMILY_MISR", "MISR"): {
                "active_zone": {},
                "branches": {"CALL": {}, "PUT": {}},
            },
            getattr(N, "STRATEGY_FAMILY_MISO", "MISO"): {
                "call_support": {},
                "put_support": {},
            },
        }
    }


def _context_only_surfaces() -> dict[str, Any]:
    surfaces = _empty_family_surfaces()
    families = surfaces["families"]
    for family_id in (
        getattr(N, "STRATEGY_FAMILY_MIST", "MIST"),
        getattr(N, "STRATEGY_FAMILY_MISB", "MISB"),
        getattr(N, "STRATEGY_FAMILY_MISC", "MISC"),
        getattr(N, "STRATEGY_FAMILY_MISR", "MISR"),
    ):
        families[family_id]["branches"]["CALL"] = {"context_pass": True}
        families[family_id]["branches"]["PUT"] = {"context_pass": True}
    families[getattr(N, "STRATEGY_FAMILY_MISO", "MISO")]["call_support"] = {
        "chain_context_ready": True,
        "context_pass": True,
    }
    return surfaces


def _true_alias_branch(family_id: str) -> dict[str, Any]:
    if family_id == getattr(N, "STRATEGY_FAMILY_MIST", "MIST"):
        return {
            "futures_bias_ok": True,
            "impulse_ok": True,
            "pullback_ok": True,
            "resume_support": True,
            "context_pass": True,
            "tradability_pass": True,
        }

    if family_id == getattr(N, "STRATEGY_FAMILY_MISB", "MISB"):
        return {
            "shelf_valid": True,
            "breakout_trigger": True,
            "breakout_acceptance": True,
            "context_pass": True,
            "tradability_pass": True,
        }

    if family_id == getattr(N, "STRATEGY_FAMILY_MISC", "MISC"):
        return {
            "compression_detection": True,
            "breakout_trigger": True,
            "breakout_acceptance": True,
            "retest_monitor_alive": True,
            "retest_ok": True,
            "hesitation_ok": True,
            "resume_support": True,
            "context_pass": True,
            "tradability_pass": True,
        }

    if family_id == getattr(N, "STRATEGY_FAMILY_MISR", "MISR"):
        return {
            "active_zone_valid": True,
            "fake_break": True,
            "absorption": True,
            "range_reentry": True,
            "flow_flip": True,
            "hold_proof": True,
            "no_mans_land_clear": True,
            "reversal_impulse": True,
            "context_pass": True,
            "tradability_pass": True,
        }

    if family_id == getattr(N, "STRATEGY_FAMILY_MISO", "MISO"):
        return {
            "burst_valid": True,
            "aggression_ok": True,
            "tape_urgency_ok": True,
            "persistence_ok": True,
            "queue_ok": True,
            "futures_alignment_ok": True,
            "futures_veto_clear": True,
            "tradability_pass": True,
        }

    raise ValueError(f"unknown family_id={family_id!r}")


def _surfaces_with_one_true_family(family_id: str, *, branch: str = "CALL") -> dict[str, Any]:
    surfaces = _empty_family_surfaces()
    families = surfaces["families"]

    if family_id == getattr(N, "STRATEGY_FAMILY_MISO", "MISO"):
        key = "call_support" if branch == "CALL" else "put_support"
        families[family_id][key] = _true_alias_branch(family_id)
        return surfaces

    if family_id == getattr(N, "STRATEGY_FAMILY_MISR", "MISR"):
        families[family_id]["active_zone"] = {
            "zone_id": "proof-zone",
            "zone_type": "ORB_LOW",
            "zone_level": 25000.0,
            "zone_low": 24995.0,
            "zone_high": 25005.0,
            "quality_score": 1.0,
            "expires_ts_ns": None,
        }

    families[family_id]["branches"][branch] = _true_alias_branch(family_id)
    return surfaces


def _families(engine: F.FeatureEngine, surfaces: Mapping[str, Any]) -> dict[str, Any]:
    out = engine._contract_families(surfaces, _shared_core())
    C.validate_families_block(out)
    return out


def _family_eligible(families: Mapping[str, Any], family_id: str) -> bool:
    return bool(families[family_id]["eligible"])


def _branch_support(families: Mapping[str, Any], family_id: str, branch: str = "CALL") -> Mapping[str, Any]:
    if family_id == getattr(N, "STRATEGY_FAMILY_MISO", "MISO"):
        return families[family_id]["call_support" if branch == "CALL" else "put_support"]
    return families[family_id]["branches"][branch]


def main() -> int:
    now_ns = time.time_ns()
    engine = _engine()

    family_ids = (
        getattr(N, "STRATEGY_FAMILY_MIST", "MIST"),
        getattr(N, "STRATEGY_FAMILY_MISB", "MISB"),
        getattr(N, "STRATEGY_FAMILY_MISC", "MISC"),
        getattr(N, "STRATEGY_FAMILY_MISR", "MISR"),
        getattr(N, "STRATEGY_FAMILY_MISO", "MISO"),
    )

    empty_payload = C.build_empty_family_features_payload()
    empty_payload_all_families_eligible_false = all(
        not empty_payload["families"][family_id]["eligible"]
        for family_id in family_ids
    )

    context_only = _families(engine, _context_only_surfaces())
    context_pass_alone_does_not_make_family_eligible = all(
        not _family_eligible(context_only, family_id)
        for family_id in family_ids
    )

    alias_checks: dict[str, bool] = {}
    one_family_checks: dict[str, bool] = {}

    for family_id in family_ids:
        families = _families(engine, _surfaces_with_one_true_family(family_id, branch="CALL"))
        support = dict(_branch_support(families, family_id, "CALL"))

        if family_id == getattr(N, "STRATEGY_FAMILY_MISO", "MISO"):
            expected_true_keys = (
                "burst_detected",
                "aggression_ok",
                "tape_speed_ok",
                "imbalance_persist_ok",
                "futures_vwap_align_ok",
                "tradability_pass",
            )
            expected_false_keys = (
                "queue_reload_blocked",
                "futures_contradiction_blocked",
            )
            alias_checks[f"{family_id}_positive_aliases_mapped"] = all(
                support.get(key) is True for key in expected_true_keys
            )
            alias_checks[f"{family_id}_negative_aliases_inverted"] = all(
                support.get(key) is False for key in expected_false_keys
            )
        else:
            expected_keys = tuple(
                key for key, value in support.items()
                if key != "context_pass" and isinstance(value, bool)
            )
            alias_checks[f"{family_id}_canonical_aliases_mapped"] = all(
                support.get(key) is True for key in expected_keys
            )

        one_family_checks[f"{family_id}_only_expected_family_eligible"] = (
            _family_eligible(families, family_id)
            and all(
                not _family_eligible(families, other_family)
                for other_family in family_ids
                if other_family != family_id
            )
        )

        if family_id == getattr(N, "STRATEGY_FAMILY_MISO", "MISO"):
            one_family_checks[f"{family_id}_expected_call_support_only"] = (
                families[family_id]["call_support"]["burst_detected"] is True
                and families[family_id]["put_support"]["burst_detected"] is False
            )
        else:
            one_family_checks[f"{family_id}_expected_call_branch_only"] = (
                any(families[family_id]["branches"]["CALL"].values())
                and not any(families[family_id]["branches"]["PUT"].values())
            )

    miso_blocked_surface = _empty_family_surfaces()
    miso = getattr(N, "STRATEGY_FAMILY_MISO", "MISO")
    miso_blocked_surface["families"][miso]["call_support"] = {
        **_true_alias_branch(miso),
        "queue_ok": False,
        "futures_veto_clear": False,
    }
    miso_blocked = _families(engine, miso_blocked_surface)
    miso_negative_flags_inverted_correctly = (
        miso_blocked[miso]["call_support"]["queue_reload_blocked"] is True
        and miso_blocked[miso]["call_support"]["futures_contradiction_blocked"] is True
        and miso_blocked[miso]["eligible"] is False
    )

    canonical_aliases_all_mapped = all(alias_checks.values())
    synthetic_true_setup_marks_expected_family_branch_only = all(one_family_checks.values())

    checks = {
        "context_pass_alone_does_not_make_family_eligible": context_pass_alone_does_not_make_family_eligible,
        "canonical_aliases_all_mapped": canonical_aliases_all_mapped,
        "miso_negative_flags_inverted_correctly": miso_negative_flags_inverted_correctly,
        "empty_payload_all_families_eligible_false": empty_payload_all_families_eligible_false,
        "synthetic_true_setup_marks_expected_family_branch_only": synthetic_true_setup_marks_expected_family_branch_only,
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_family_features_canonical_support",
        "batch": "25M",
        "generated_at_ns": now_ns,
        "family_features_canonical_support_ok": proof_ok,
        "checks": checks,
        "alias_checks": alias_checks,
        "one_family_checks": one_family_checks,
        "context_only_families": context_only,
        "miso_blocked_family": miso_blocked[miso],
        "contract_keys": {
            "MIST_BRANCH_KEYS": C.MIST_BRANCH_KEYS,
            "MISB_BRANCH_KEYS": C.MISB_BRANCH_KEYS,
            "MISC_BRANCH_KEYS": C.MISC_BRANCH_KEYS,
            "MISR_BRANCH_KEYS": C.MISR_BRANCH_KEYS,
            "MISO_SIDE_SUPPORT_KEYS": C.MISO_SIDE_SUPPORT_KEYS,
        },
    }

    out = Path("run/proofs/proof_family_features_canonical_support.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "family_features_canonical_support_ok": proof_ok,
        **checks,
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
