#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = PROJECT_ROOT / "run/proofs/proof_oi_context_surface_audit.json"

REQUIRED_TARGETS = [
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feature_family/strike_selection.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/services/feature_family/misb_surface.py",
    "app/mme_scalpx/services/feature_family/misc_surface.py",
    "app/mme_scalpx/services/feature_family/misr_surface.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/mist.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
]

RELATED_TARGETS = [
    "app/mme_scalpx/services/strategy_family/order_intent.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/risk.py",
]

FAMILY_SURFACE_FILES = {
    "MIST": "app/mme_scalpx/services/feature_family/mist_surface.py",
    "MISB": "app/mme_scalpx/services/feature_family/misb_surface.py",
    "MISC": "app/mme_scalpx/services/feature_family/misc_surface.py",
    "MISR": "app/mme_scalpx/services/feature_family/misr_surface.py",
    "MISO": "app/mme_scalpx/services/feature_family/miso_surface.py",
}

STRATEGY_LEAF_FILES = {
    "MIST": "app/mme_scalpx/services/strategy_family/mist.py",
    "MISB": "app/mme_scalpx/services/strategy_family/misb.py",
    "MISC": "app/mme_scalpx/services/strategy_family/misc.py",
    "MISR": "app/mme_scalpx/services/strategy_family/misr.py",
    "MISO": "app/mme_scalpx/services/strategy_family/miso.py",
}

CANONICAL_OI_SCHEMA_KEYS = [
    "nearest_call_oi_resistance_strike",
    "nearest_put_oi_support_strike",
    "call_wall_strength_score",
    "put_wall_strength_score",
    "call_wall_near",
    "put_wall_near",
    "total_call_oi",
    "total_put_oi",
    "total_call_oi_change",
    "total_put_oi_change",
    "oi_ratio_put_to_call",
    "oi_bias",
    "oi_wall_ready",
]


def read_text(rel: str) -> str:
    return (PROJECT_ROOT / rel).read_text(encoding="utf-8", errors="replace")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def line_numbers(text: str, needle: str) -> list[int]:
    return [
        idx
        for idx, line in enumerate(text.splitlines(), start=1)
        if needle in line
    ]


def regex_lines(text: str, pattern: str) -> list[dict[str, Any]]:
    rx = re.compile(pattern, re.IGNORECASE)
    out: list[dict[str, Any]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if rx.search(line):
            out.append({"line": idx, "text": line.strip()})
    return out


def inspect_file(rel: str) -> dict[str, Any]:
    path = PROJECT_ROOT / rel
    if not path.exists():
        return {"path": rel, "present": False}
    text = read_text(rel)
    return {
        "path": rel,
        "present": True,
        "line_count": len(text.splitlines()),
        "sha256": sha256_text(text),
    }


def any_token(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


def all_tokens(text: str, tokens: list[str]) -> bool:
    return all(token in text for token in tokens)


def false_checks(checks: dict[str, bool]) -> dict[str, bool]:
    return {k: v for k, v in checks.items() if v is False}


def find_related_artifacts() -> dict[str, Any]:
    proof_dir = PROJECT_ROOT / "run/proofs"
    bin_dir = PROJECT_ROOT / "bin"

    proof_scripts = sorted(
        str(path.relative_to(PROJECT_ROOT))
        for pattern in ("proof_*oi*.py", "proof_*dhan*.py", "proof_*strategy*activation*.py", "proof_*order_intent*.py")
        for path in bin_dir.glob(pattern)
    )
    proof_artifacts = sorted(
        str(path.relative_to(PROJECT_ROOT))
        for pattern in ("proof_*oi*.json", "proof_*dhan*.json", "proof_*strategy*activation*.json", "proof_*order_intent*.json")
        for path in proof_dir.glob(pattern)
    )

    return {
        "proof_scripts": sorted(set(proof_scripts)),
        "proof_artifacts": sorted(set(proof_artifacts)),
        "dhan_oi_ladder_persistence_script_exists": (
            bin_dir / "proof_dhan_oi_ladder_persistence.py"
        ).exists(),
        "dhan_oi_ladder_persistence_proof_exists": (
            proof_dir / "proof_dhan_oi_ladder_persistence.json"
        ).exists(),
        "strategy_activation_report_only_script_exists": (
            bin_dir / "proof_strategy_activation_report_only.py"
        ).exists(),
        "order_intent_adapter_disabled_script_exists": (
            bin_dir / "proof_order_intent_adapter_disabled.py"
        ).exists(),
    }


def main() -> int:
    generated_at_ns = time.time_ns()

    all_targets = list(dict.fromkeys(REQUIRED_TARGETS + RELATED_TARGETS))
    files_inspected = [inspect_file(rel) for rel in all_targets]
    missing_required = [
        item["path"]
        for item in files_inspected[: len(REQUIRED_TARGETS)]
        if not item.get("present")
    ]

    sources = {
        rel: read_text(rel)
        for rel in all_targets
        if (PROJECT_ROOT / rel).exists()
    }

    feeds = sources.get("app/mme_scalpx/services/feeds.py", "")
    features = sources.get("app/mme_scalpx/services/features.py", "")
    strike_selection = sources.get(
        "app/mme_scalpx/services/feature_family/strike_selection.py", ""
    )
    strategy = sources.get("app/mme_scalpx/services/strategy.py", "")
    order_intent = sources.get("app/mme_scalpx/services/strategy_family/order_intent.py", "")
    execution = sources.get("app/mme_scalpx/services/execution.py", "")
    risk = sources.get("app/mme_scalpx/services/risk.py", "")
    models = sources.get("app/mme_scalpx/core/models.py", "")
    names = sources.get("app/mme_scalpx/core/names.py", "")

    related_artifacts = find_related_artifacts()

    dhan_ladder_producer_checks = {
        "feeds_has_raw_dhan_context": "RawDhanContext" in feeds,
        "feeds_has_normalize_dhan_context": "normalize_dhan_context" in feeds,
        "feeds_has_dhan_ladder_context_builder": "_build_dhan_ladder_context" in feeds,
        "feeds_accepts_dhan_context_adapter": "dhan_context_adapter" in feeds,
        "feeds_has_option_chain_ladder_json": "option_chain_ladder_json" in feeds,
        "feeds_has_strike_ladder_json": "strike_ladder_json" in feeds,
        "feeds_has_oi_wall_summary_json": "oi_wall_summary_json" in feeds,
        "models_has_dhan_context_state_or_event": any_token(
            models,
            ["DhanContextState", "DhanContextEvent"],
        ),
        "names_has_dhan_provider_or_context": any_token(
            names,
            ["PROVIDER_DHAN", "DHAN", "Dhan"],
        ),
    }

    dhan_ladder_producer_found = {
        "ok": all(dhan_ladder_producer_checks.values()),
        "checks": dhan_ladder_producer_checks,
        "false_checks": false_checks(dhan_ladder_producer_checks),
        "producer_file": "app/mme_scalpx/services/feeds.py",
    }

    dhan_ladder_normalizer_checks = {
        "strike_selection_has_normalize_strike_ladder_rows": "normalize_strike_ladder_rows" in strike_selection,
        "strike_selection_has_build_strike_ladder_surface": "build_strike_ladder_surface" in strike_selection,
        "strike_selection_has_build_oi_wall_summary": "build_oi_wall_summary" in strike_selection,
        "features_imports_or_calls_build_strike_ladder_surface": "build_strike_ladder_surface" in features,
        "features_imports_or_calls_build_oi_wall_summary": "build_oi_wall_summary" in features,
        "features_publishes_oi_wall_context": "oi_wall_context" in features,
    }

    dhan_ladder_normalizer_found = {
        "ok": all(dhan_ladder_normalizer_checks.values()),
        "checks": dhan_ladder_normalizer_checks,
        "false_checks": false_checks(dhan_ladder_normalizer_checks),
        "normalizer_file": "app/mme_scalpx/services/feature_family/strike_selection.py",
    }

    canonical_authority_checks = {
        "strike_selection_declares_canonical_surface": "Canonical strike-selection" in strike_selection,
        "strike_selection_declares_ownership": "This module OWNS" in strike_selection,
        "strike_selection_declares_oi_no_trigger_law": "OI may never be treated as immediate trigger truth" in strike_selection,
        "strike_selection_has_wall_builder": "build_oi_wall_summary" in strike_selection,
    }

    canonical_oi_wall_authority = {
        "path": "app/mme_scalpx/services/feature_family/strike_selection.py",
        "ok": all(canonical_authority_checks.values()),
        "checks": canonical_authority_checks,
        "false_checks": false_checks(canonical_authority_checks),
        "evidence_lines": {
            "canonical_header": line_numbers(strike_selection, "Canonical strike-selection"),
            "ownership": line_numbers(strike_selection, "This module OWNS"),
            "oi_no_trigger_law": line_numbers(
                strike_selection,
                "OI may never be treated as immediate trigger truth",
            ),
            "build_oi_wall_summary": line_numbers(strike_selection, "build_oi_wall_summary"),
        },
    }

    wall_logic_locations: list[dict[str, Any]] = []

    if "_build_dhan_ladder_context" in feeds and "wall_strength" in feeds:
        wall_logic_locations.append({
            "path": "app/mme_scalpx/services/feeds.py",
            "surface": "producer-side Dhan ladder / wall summary construction",
            "lines": line_numbers(feeds, "_build_dhan_ladder_context") + line_numbers(feeds, "def _wall("),
            "role": "producer-side preliminary context",
        })

    if "_nearest_wall" in features and "wall_strength" in features:
        wall_logic_locations.append({
            "path": "app/mme_scalpx/services/features.py",
            "surface": "features fallback nearest-wall calculation",
            "lines": line_numbers(features, "_nearest_wall"),
            "role": "fallback wall logic",
        })

    if "build_oi_wall_summary" in strike_selection:
        wall_logic_locations.append({
            "path": "app/mme_scalpx/services/feature_family/strike_selection.py",
            "surface": "build_oi_wall_summary",
            "lines": line_numbers(strike_selection, "build_oi_wall_summary"),
            "role": "declared canonical authority",
        })

    duplicate_wall_logic_detected = any(
        item["path"] != "app/mme_scalpx/services/feature_family/strike_selection.py"
        for item in wall_logic_locations
    )

    schema_presence = {key: key in strike_selection for key in CANONICAL_OI_SCHEMA_KEYS}
    published_context_checks = {
        "features_has_oi_wall_context": "oi_wall_context" in features,
        "features_marks_context_not_trigger": any_token(
            features,
            ["context_not_trigger", "shared_context_quality_surface_not_trigger", "not trigger"],
        ),
        "features_has_nearest_call_oi_resistance": "nearest_call_oi_resistance" in features,
        "features_has_nearest_put_oi_support": "nearest_put_oi_support" in features,
        "features_has_oi_bias": "oi_bias" in features,
    }

    canonical_oi_context_schema = {
        "authority": "app/mme_scalpx/services/feature_family/strike_selection.py",
        "schema_keys": CANONICAL_OI_SCHEMA_KEYS,
        "schema_keys_present_in_authority": schema_presence,
        "all_schema_keys_present_in_authority": all(schema_presence.values()),
        "published_context_checks": published_context_checks,
        "published_context_false_checks": false_checks(published_context_checks),
        "published_context_ok": all(published_context_checks.values()),
    }

    family_surface_consumers: dict[str, Any] = {}
    for family, rel in FAMILY_SURFACE_FILES.items():
        text = sources.get(rel, "")
        checks = {
            "present": bool(text),
            "consumes_oi_or_wall_context": any_token(
                text,
                ["oi_wall_context", "oi_context", "oi_bias", "same_side_wall", "wall_strength", "wall_context"],
            ),
            "uses_context_score_or_penalty": any_token(
                text,
                ["context_score", "oi_context_score", "near_wall_penalty", "wall_penalty", "same_side_wall_near"],
            ),
            "declares_not_decision_owner": any_token(
                text,
                ["DOES NOT own", "does not own", "entry / exit decisions"],
            ),
        }
        family_surface_consumers[family] = {
            "path": rel,
            **checks,
            "false_checks": false_checks(checks),
            "evidence_lines": line_numbers(text, "oi_bias")[:8]
            + line_numbers(text, "oi_wall")[:8]
            + line_numbers(text, "same_side_wall")[:8],
        }

    family_surface_consumers_ok = all(
        info["present"] and info["consumes_oi_or_wall_context"]
        for info in family_surface_consumers.values()
    )

    strategy_family_consumers: dict[str, Any] = {}
    for family, rel in STRATEGY_LEAF_FILES.items():
        text = sources.get(rel, "")
        direct_side_effects = any_token(
            text,
            [
                ".xadd(",
                ".xgroup_create(",
                "place_entry_order",
                "place_exit_order",
                "send_order",
                "STREAM_ORDERS_MME",
            ],
        )
        checks = {
            "present": bool(text),
            "declares_candidate_only_or_no_publish_decision": any_token(
                text,
                [
                    "does not publish decisions",
                    "candidate support only",
                    "does not own execution",
                    "no broker",
                ],
            ),
            "consumes_oi_or_wall_context": any_token(
                text,
                ["oi_wall_context", "oi_context", "oi_bias", "same_side_wall", "wall_strength"],
            ),
            "no_direct_redis_or_broker_side_effects": not direct_side_effects,
        }
        strategy_family_consumers[family] = {
            "path": rel,
            **checks,
            "direct_redis_or_broker_side_effects_detected": direct_side_effects,
            "false_checks": false_checks(checks),
            "evidence_lines": line_numbers(text, "oi_wall_context")[:8]
            + line_numbers(text, "oi_bias")[:8]
            + line_numbers(text, "does not publish decisions")[:4],
        }

    strategy_family_consumers_ok = all(
        info["present"] and info["no_direct_redis_or_broker_side_effects"]
        for info in strategy_family_consumers.values()
    )

    suspicious_trigger_lines: list[dict[str, Any]] = []
    trigger_pattern = (
        r"(trigger|burst|fake_break|breakout|resume|impulse).*="
        r".*\boi\b|\boi\b.*=.*(trigger|burst|fake_break|breakout|resume|impulse)"
    )

    for rel in list(FAMILY_SURFACE_FILES.values()) + list(STRATEGY_LEAF_FILES.values()):
        for item in regex_lines(sources.get(rel, ""), trigger_pattern):
            lower = item["text"].lower()
            if any(word in lower for word in ["context", "wall", "bias", "metadata", "comment", "score", "penalty"]):
                continue
            suspicious_trigger_lines.append({"path": rel, **item})

    oi_used_as_trigger_detected = bool(suspicious_trigger_lines)

    miso_surface = sources.get("app/mme_scalpx/services/feature_family/miso_surface.py", "")
    miso_leaf = sources.get("app/mme_scalpx/services/strategy_family/miso.py", "")

    miso_chain_live_checks = {
        "surface_mentions_chain_selection_layer": any_token(
            miso_surface,
            ["Chain data is selection-layer truth only", "selection-layer", "chain_context_ready"],
        ),
        "surface_mentions_live_trigger_truth": any_token(
            miso_surface,
            ["Live trigger truth", "selected option live feed", "shadow"],
        ),
        "surface_has_chain_context_ready": "chain_context_ready" in miso_surface,
        "surface_has_shadow_support": "shadow" in miso_surface and "support" in miso_surface,
        "leaf_has_option_led_or_burst_logic": any_token(
            miso_leaf,
            ["option-led", "burst_score", "burst"],
        ),
        "leaf_has_futures_veto_or_alignment": any_token(
            miso_leaf,
            ["futures_veto", "vwap", "contradiction"],
        ),
    }

    miso_chain_live_separation_ok = {
        "ok": all(miso_chain_live_checks.values()),
        "checks": miso_chain_live_checks,
        "false_checks": false_checks(miso_chain_live_checks),
    }

    misr_surface = sources.get("app/mme_scalpx/services/feature_family/misr_surface.py", "")
    misr_leaf = sources.get("app/mme_scalpx/services/strategy_family/misr.py", "")

    misr_zone_checks = {
        "surface_has_orb_swing_zone_types": all_tokens(
            misr_surface,
            ["ORB_HIGH", "ORB_LOW", "SWING_HIGH", "SWING_LOW"],
        ),
        "surface_has_zone_registry_builder": "zone_registry" in misr_surface or "build_misr_zone" in misr_surface,
        "leaf_resolves_active_zone": "active_zone" in misr_leaf,
        "leaf_uses_oi_as_context": any_token(misr_leaf, ["oi_wall_context", "oi_bias", "wall_strength"]),
        "no_oi_wall_zone_type_declared": not any_token(
            misr_surface + "\n" + misr_leaf,
            ["OI_WALL_ZONE", "ZONE_OI_WALL"],
        ),
    }

    misr_registered_zone_law_ok = {
        "ok": all(misr_zone_checks.values()),
        "checks": misr_zone_checks,
        "false_checks": false_checks(misr_zone_checks),
    }

    strategy_hold_checks = {
        "strategy_mentions_hold_only": "HOLD-only" in strategy,
        "strategy_mentions_family_consumer_bridge": any_token(strategy, ["family_features consumer bridge", "consumer bridge"]),
        "validate_hold_guard_exists": "_validate_hold_decision_for_publish" in strategy,
        "refuses_non_hold_action": "refused non-HOLD action" in strategy,
        "refuses_non_zero_qty": "refused non-zero qty" in strategy,
        "requires_hold_only": "requires hold_only" in strategy or '"hold_only": 1' in strategy,
        "requires_activation_report_only": "requires activation_report_only" in strategy or '"activation_report_only": 1' in strategy,
        "refuses_live_orders_allowed": "refused live_orders_allowed truthy" in strategy or '"live_orders_allowed": False' in strategy,
        "builds_action_hold": '"action": ACTION_HOLD' in strategy or "'action': ACTION_HOLD" in strategy,
        "builds_zero_qty_or_sentinel_zero": any_token(
            strategy,
            ['"qty": 0', "'qty': 0", '"quantity_lots": 0', "'quantity_lots': 0"],
        ),
        "activation_promotion_disabled": "ACTIVATION_ALLOW_CANDIDATE_PROMOTION" in strategy and "False" in strategy,
        "order_intent_adapter_disabled": "STRATEGY_ORDER_INTENT_ADAPTER_ENABLED" in strategy and "False" in strategy,
        "order_intent_publication_disabled": "STRATEGY_ORDER_INTENT_PUBLICATION_ENABLED" in strategy and "False" in strategy,
    }

    strategy_hold_only_ok = {
        "ok": all(strategy_hold_checks.values()),
        "checks": strategy_hold_checks,
        "false_checks": false_checks(strategy_hold_checks),
        "evidence_lines": {
            "hold_only": line_numbers(strategy, "HOLD-only")[:10],
            "validate_guard": line_numbers(strategy, "_validate_hold_decision_for_publish"),
            "non_hold_refusal": line_numbers(strategy, "refused non-HOLD action"),
            "non_zero_refusal": line_numbers(strategy, "refused non-zero qty"),
            "live_orders_refusal": line_numbers(strategy, "live_orders_allowed"),
            "adapter_disabled": line_numbers(strategy, "STRATEGY_ORDER_INTENT_ADAPTER_ENABLED"),
            "publication_disabled": line_numbers(strategy, "STRATEGY_ORDER_INTENT_PUBLICATION_ENABLED"),
        },
    }

    live_order_bypass_checks = {
        "strategy_does_not_write_orders_stream": "STREAM_ORDERS_MME" not in strategy,
        "strategy_does_not_call_entry_order": "place_entry_order" not in strategy,
        "strategy_does_not_call_exit_order": "place_exit_order" not in strategy,
        "strategy_has_decision_stream_validation": "_validate_decision_stream_fields" in strategy,
        "order_intent_default_disabled_or_preview_only": any_token(
            order_intent,
            ["disabled_preview_only", "publish forbidden", "return False"],
        ),
        "execution_remains_order_owner": any_token(execution, ["place_entry_order", "STREAM_ORDERS_MME"]),
        "risk_has_veto_surface": any_token(risk, ["veto_reason", "risk_veto", "broker_disconnected"]),
        "strategy_family_no_direct_side_effects": all(
            info["no_direct_redis_or_broker_side_effects"]
            for info in strategy_family_consumers.values()
        ),
    }

    live_order_bypass_detected = not all(live_order_bypass_checks.values())

    blocking_checks = {
        "missing_required_files_absent": not missing_required,
        "dhan_ladder_producer_found": dhan_ladder_producer_found["ok"],
        "dhan_ladder_normalizer_found": dhan_ladder_normalizer_found["ok"],
        "canonical_oi_wall_authority_ok": canonical_oi_wall_authority["ok"],
        "canonical_schema_present": canonical_oi_context_schema["all_schema_keys_present_in_authority"],
        "published_context_ok": canonical_oi_context_schema["published_context_ok"],
        "family_surface_consumers_ok": family_surface_consumers_ok,
        "strategy_family_consumers_no_side_effects_ok": strategy_family_consumers_ok,
        "oi_not_used_as_trigger": not oi_used_as_trigger_detected,
        "miso_chain_live_separation_ok": miso_chain_live_separation_ok["ok"],
        "misr_registered_zone_law_ok": misr_registered_zone_law_ok["ok"],
        "strategy_hold_only_ok": strategy_hold_only_ok["ok"],
        "live_order_bypass_absent": not live_order_bypass_detected,
    }

    blocking_failures = false_checks(blocking_checks)

    if blocking_failures:
        final_verdict = "FAIL"
        recommended_next_batch = "Stop. Fix blocking proof/safety failures before Batch 26-OI-B."
    elif duplicate_wall_logic_detected:
        final_verdict = "PASS_WITH_SURFACE_DRIFT_FINDING"
        recommended_next_batch = (
            "Batch 26-OI-B — canonicalize OI wall authority so strike_selection.py is the sole "
            "wall calculator and features.py only publishes canonical context. Preserve HOLD/report-only safety."
        )
    else:
        final_verdict = "PASS"
        recommended_next_batch = (
            "Batch 26-OI-B — canonical Option Context Layer publication proof. Preserve HOLD/report-only safety."
        )

    proof = {
        "proof_name": "proof_oi_context_surface_audit",
        "batch": "26-OI-A",
        "revision": "R2",
        "generated_at_ns": generated_at_ns,
        "final_verdict": final_verdict,
        "files_inspected": files_inspected,
        "missing_required_files": missing_required,
        "related_artifacts": related_artifacts,
        "dhan_ladder_producer_found": dhan_ladder_producer_found,
        "dhan_ladder_normalizer_found": dhan_ladder_normalizer_found,
        "canonical_oi_wall_authority": canonical_oi_wall_authority,
        "duplicate_wall_logic_detected": duplicate_wall_logic_detected,
        "duplicate_wall_logic_locations": wall_logic_locations,
        "canonical_oi_context_schema": canonical_oi_context_schema,
        "family_surface_consumers": family_surface_consumers,
        "family_surface_consumers_all_canonical_context": family_surface_consumers_ok,
        "strategy_family_consumers": strategy_family_consumers,
        "strategy_family_consumers_all_context_only_no_side_effects": strategy_family_consumers_ok,
        "oi_used_as_trigger_detected": oi_used_as_trigger_detected,
        "oi_trigger_suspicious_lines": suspicious_trigger_lines,
        "miso_chain_live_separation_ok": miso_chain_live_separation_ok,
        "misr_registered_zone_law_ok": misr_registered_zone_law_ok,
        "strategy_hold_only_ok": strategy_hold_only_ok,
        "live_order_bypass_detected": live_order_bypass_detected,
        "live_order_bypass_checks": live_order_bypass_checks,
        "blocking_checks": blocking_checks,
        "blocking_failures": blocking_failures,
        "recommended_next_batch": recommended_next_batch,
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": "proof_oi_context_surface_audit",
        "revision": "R2",
        "batch": "26-OI-A",
        "final_verdict": final_verdict,
        "blocking_failures": blocking_failures,
        "duplicate_wall_logic_detected": duplicate_wall_logic_detected,
        "oi_used_as_trigger_detected": oi_used_as_trigger_detected,
        "strategy_hold_only_ok": strategy_hold_only_ok["ok"],
        "live_order_bypass_detected": live_order_bypass_detected,
        "proof_path": str(PROOF_PATH),
        "recommended_next_batch": recommended_next_batch,
    }, indent=2, sort_keys=True))

    return 0 if final_verdict in {"PASS", "PASS_WITH_SURFACE_DRIFT_FINDING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
