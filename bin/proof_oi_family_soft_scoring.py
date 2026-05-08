#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROOF_PATH = ROOT / "run/proofs/proof_oi_family_soft_scoring.json"

LEAVES = {
    "MIST": "app.mme_scalpx.services.strategy_family.mist",
    "MISB": "app.mme_scalpx.services.strategy_family.misb",
    "MISC": "app.mme_scalpx.services.strategy_family.misc",
    "MISR": "app.mme_scalpx.services.strategy_family.misr",
    "MISO": "app.mme_scalpx.services.strategy_family.miso",
}

LEAF_FILES = {
    "MIST": "app/mme_scalpx/services/strategy_family/mist.py",
    "MISB": "app/mme_scalpx/services/strategy_family/misb.py",
    "MISC": "app/mme_scalpx/services/strategy_family/misc.py",
    "MISR": "app/mme_scalpx/services/strategy_family/misr.py",
    "MISO": "app/mme_scalpx/services/strategy_family/miso.py",
}

POLICY_EXPECTED = {
    "MIST": "pullback_resume_quality_context_only",
    "MISB": "wall_break_acceptance_context_only",
    "MISC": "compression_retest_wall_context_only",
    "MISR": "registered_zone_support_context_only",
    "MISO": "ladder_shadow_strike_quality_context_only",
}

STATIC_TARGETS = [
    "app/mme_scalpx/services/feature_family/strike_selection.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/order_intent.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def file_info(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        return {"path": rel, "present": False}
    text = read(rel)
    return {
        "path": rel,
        "present": True,
        "line_count": len(text.splitlines()),
        "sha256": sha(text),
    }


def any_token(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


def false_checks(checks: dict[str, bool]) -> dict[str, bool]:
    return {k: v for k, v in checks.items() if v is False}


def build_oi_context() -> dict[str, Any]:
    return {
        "distance_strikes": 0.5,
        "wall_strength": 0.99,
        "wall_strength_score": 0.99,
        "supportive": False,
        "canonical": True,
        "law": "context_not_trigger",
    }


def build_supportive_oi_context() -> dict[str, Any]:
    return {
        "distance_strikes": 0.5,
        "wall_strength": 0.85,
        "wall_strength_score": 0.85,
        "supportive": True,
        "canonical": True,
        "law": "context_not_trigger",
    }


def smoke_context_score(family: str, mod: Any) -> dict[str, Any]:
    branch_call = getattr(mod, "BRANCH_CALL", "CALL")
    min_context = float(getattr(mod, "MIN_CONTEXT_SCORE", 0.0))
    hostile_wall = build_oi_context()
    supportive_wall = build_supportive_oi_context()

    surface = {"oi_wall_context": hostile_wall}
    view = {
        "oi_wall_context": {
            "call": hostile_wall,
            "put": hostile_wall,
        },
        "shared_core": {
            "oi_wall_context": {
                "call": hostile_wall,
                "put": hostile_wall,
            },
            "strike_selection": {
                "oi_wall_context": {
                    "call": hostile_wall,
                    "put": hostile_wall,
                }
            },
        },
        "common": {
            "cross_option": {
                "call_oi_wall_context": hostile_wall,
                "put_oi_wall_context": hostile_wall,
            }
        },
    }

    score, passed, reason = mod.context_score(view, branch_call, surface)

    supportive_surface = {"oi_wall_context": supportive_wall}
    supportive_view = {
        "oi_wall_context": {
            "call": supportive_wall,
            "put": supportive_wall,
        },
        "shared_core": {
            "oi_wall_context": {
                "call": supportive_wall,
                "put": supportive_wall,
            }
        },
    }
    supportive_score, supportive_passed, supportive_reason = mod.context_score(
        supportive_view,
        branch_call,
        supportive_surface,
    )

    return {
        "family": family,
        "min_context_score": min_context,
        "hostile_wall_score": score,
        "hostile_wall_passed": bool(passed),
        "hostile_wall_reason": reason,
        "hostile_wall_score_at_or_above_min": float(score) >= min_context,
        "supportive_wall_score": supportive_score,
        "supportive_wall_passed": bool(supportive_passed),
        "supportive_wall_reason": supportive_reason,
        "soft_policy": getattr(mod, "_BATCH26_OI_C_SOFT_POLICY", None),
        "soft_policy_description": getattr(mod, "_BATCH26_OI_C_SOFT_POLICY_DESCRIPTION", None),
    }


def main() -> int:
    generated_at_ns = time.time_ns()

    files_inspected = [
        file_info(path)
        for path in list(LEAF_FILES.values()) + STATIC_TARGETS
    ]

    leaf_static: dict[str, Any] = {}
    leaf_smoke: dict[str, Any] = {}

    for family, rel in LEAF_FILES.items():
        text = read(rel)
        checks = {
            "wrapper_marker_present": "BATCH26_OI_C_FAMILY_SOFT_SCORING_ONLY START" in text,
            "original_context_score_preserved": "_BATCH26_OI_C_ORIGINAL_CONTEXT_SCORE = context_score" in text,
            "soft_policy_present": f'_BATCH26_OI_C_SOFT_POLICY = "{POLICY_EXPECTED[family]}"' in text,
            "soft_context_floor_present": "soft_only_oi_context_floor" in text,
            "soft_only_blocker_present": "soft_only_" in text,
            "no_redis_side_effect_added": ".xadd(" not in text and "STREAM_ORDERS_MME" not in text,
            "no_broker_call_added": "place_entry_order" not in text and "place_exit_order" not in text,
        }
        leaf_static[family] = {
            "file": rel,
            "checks": checks,
            "false_checks": false_checks(checks),
        }

    for family, mod_name in LEAVES.items():
        try:
            mod = importlib.import_module(mod_name)
            leaf_smoke[family] = smoke_context_score(family, mod)
        except Exception as exc:
            leaf_smoke[family] = {
                "family": family,
                "error": repr(exc),
                "hostile_wall_passed": False,
                "hostile_wall_score_at_or_above_min": False,
                "supportive_wall_passed": False,
            }

    strike_selection = read("app/mme_scalpx/services/feature_family/strike_selection.py")
    features = read("app/mme_scalpx/services/features.py")
    feeds = read("app/mme_scalpx/services/feeds.py")
    strategy = read("app/mme_scalpx/services/strategy.py")
    order_intent = read("app/mme_scalpx/services/strategy_family/order_intent.py")
    execution = read("app/mme_scalpx/services/execution.py")
    risk = read("app/mme_scalpx/services/risk.py")

    canonical_wall_authority_checks = {
        "strike_selection_has_build_oi_wall_summary": "def build_oi_wall_summary" in strike_selection,
        "strike_selection_declares_no_trigger_law": "OI may never be treated as immediate trigger truth" in strike_selection,
        "features_no_local_nearest_wall": "def _nearest_wall" not in features and "self._nearest_wall" not in features,
        "features_publishes_wall_authority": "wall_authority" in features,
        "feeds_no_local_wall_function": "def _wall(" not in feeds,
        "feeds_delegates_wall_calculation": "wall_calculation_delegated" in feeds,
    }

    strategy_hold_only_checks = {
        "strategy_mentions_hold_only": "HOLD-only" in strategy,
        "strategy_has_hold_publish_guard": "_validate_hold_decision_for_publish" in strategy,
        "strategy_refuses_non_hold_action": "refused non-HOLD action" in strategy,
        "strategy_refuses_non_zero_qty": "refused non-zero qty" in strategy,
        "strategy_order_intent_adapter_disabled": "STRATEGY_ORDER_INTENT_ADAPTER_ENABLED" in strategy and "False" in strategy,
        "strategy_order_intent_publication_disabled": "STRATEGY_ORDER_INTENT_PUBLICATION_ENABLED" in strategy and "False" in strategy,
        "strategy_activation_promotion_disabled": "ACTIVATION_ALLOW_CANDIDATE_PROMOTION" in strategy and "False" in strategy,
        "strategy_no_orders_stream": "STREAM_ORDERS_MME" not in strategy,
        "strategy_no_broker_call": "place_entry_order" not in strategy and "place_exit_order" not in strategy,
    }

    live_order_bypass_checks = {
        "strategy_no_orders_stream": "STREAM_ORDERS_MME" not in strategy,
        "strategy_no_broker_call": "place_entry_order" not in strategy and "place_exit_order" not in strategy,
        "order_intent_preview_disabled": any_token(order_intent, ["disabled_preview_only", "publish forbidden", "return False"]),
        "execution_remains_order_owner": any_token(execution, ["STREAM_ORDERS_MME", "place_entry_order"]),
        "risk_veto_surface_present": any_token(risk, ["veto_reason", "risk_veto", "broker_disconnected"]),
    }

    trigger_pattern = re.compile(
        r"(trigger|burst|fake_break|breakout|resume|impulse).*="
        r".*\\boi\\b|\\boi\\b.*=.*(trigger|burst|fake_break|breakout|resume|impulse)",
        re.IGNORECASE,
    )
    suspicious_trigger_lines: list[dict[str, Any]] = []
    for rel in list(LEAF_FILES.values()) + [
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/feature_family/strike_selection.py",
    ]:
        text = read(rel)
        for idx, line in enumerate(text.splitlines(), 1):
            if trigger_pattern.search(line):
                lower = line.lower()
                if any(word in lower for word in ["context", "wall", "bias", "score", "penalty", "metadata", "comment", "soft"]):
                    continue
                suspicious_trigger_lines.append({"path": rel, "line": idx, "text": line.strip()})

    family_static_ok = all(not item["false_checks"] for item in leaf_static.values())
    family_smoke_ok = all(
        bool(item.get("hostile_wall_passed"))
        and bool(item.get("hostile_wall_score_at_or_above_min"))
        and bool(item.get("supportive_wall_passed"))
        and item.get("soft_policy") == POLICY_EXPECTED[family]
        for family, item in leaf_smoke.items()
    )

    blocking_checks = {
        "family_static_wrappers_ok": family_static_ok,
        "family_dynamic_soft_scoring_ok": family_smoke_ok,
        "canonical_wall_authority_preserved": all(canonical_wall_authority_checks.values()),
        "strategy_hold_only_preserved": all(strategy_hold_only_checks.values()),
        "live_order_bypass_absent": all(live_order_bypass_checks.values()),
        "oi_not_used_as_trigger": not suspicious_trigger_lines,
    }

    blocking_failures = false_checks(blocking_checks)
    final_verdict = "PASS" if not blocking_failures else "FAIL"

    recommended_next_batch = (
        "Batch 26-OI-D — replay/report impact proof: compare candidate counts, family score movement, blocker counts, and no-order safety before any hard veto."
        if final_verdict == "PASS"
        else "Stop. Fix blocking failures before Batch 26-OI-D."
    )

    proof = {
        "proof_name": "proof_oi_family_soft_scoring",
        "batch": "26-OI-C",
        "generated_at_ns": generated_at_ns,
        "final_verdict": final_verdict,
        "files_inspected": files_inspected,
        "family_static": leaf_static,
        "family_smoke": leaf_smoke,
        "canonical_wall_authority_checks": canonical_wall_authority_checks,
        "strategy_hold_only_checks": strategy_hold_only_checks,
        "live_order_bypass_checks": live_order_bypass_checks,
        "live_order_bypass_detected": not all(live_order_bypass_checks.values()),
        "oi_used_as_trigger_detected": bool(suspicious_trigger_lines),
        "oi_trigger_suspicious_lines": suspicious_trigger_lines,
        "blocking_checks": blocking_checks,
        "blocking_failures": blocking_failures,
        "recommended_next_batch": recommended_next_batch,
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "batch": "26-OI-C",
        "final_verdict": final_verdict,
        "family_static_wrappers_ok": family_static_ok,
        "family_dynamic_soft_scoring_ok": family_smoke_ok,
        "canonical_wall_authority_preserved": all(canonical_wall_authority_checks.values()),
        "strategy_hold_only_preserved": all(strategy_hold_only_checks.values()),
        "live_order_bypass_detected": proof["live_order_bypass_detected"],
        "oi_used_as_trigger_detected": bool(suspicious_trigger_lines),
        "blocking_failures": blocking_failures,
        "proof_path": str(PROOF_PATH),
        "recommended_next_batch": recommended_next_batch,
    }, indent=2, sort_keys=True))

    return 0 if final_verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
