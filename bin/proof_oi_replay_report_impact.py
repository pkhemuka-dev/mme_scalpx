#!/usr/bin/env python3
from __future__ import annotations

import csv
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

PROOF_PATH = ROOT / "run/proofs/proof_oi_replay_report_impact.json"
MATRIX_PATH = ROOT / "run/proofs/proof_oi_replay_report_impact_matrix.csv"

PREREQ_PROOFS = {
    "26-OI-A": ROOT / "run/proofs/proof_oi_context_surface_audit.json",
    "26-OI-B": ROOT / "run/proofs/proof_oi_wall_authority_canonicalized.json",
    "26-OI-C": ROOT / "run/proofs/proof_oi_family_soft_scoring.json",
}

FAMILY_MODULES = {
    "MIST": "app.mme_scalpx.services.strategy_family.mist",
    "MISB": "app.mme_scalpx.services.strategy_family.misb",
    "MISC": "app.mme_scalpx.services.strategy_family.misc",
    "MISR": "app.mme_scalpx.services.strategy_family.misr",
    "MISO": "app.mme_scalpx.services.strategy_family.miso",
}

FAMILY_FILES = {
    "MIST": "app/mme_scalpx/services/strategy_family/mist.py",
    "MISB": "app/mme_scalpx/services/strategy_family/misb.py",
    "MISC": "app/mme_scalpx/services/strategy_family/misc.py",
    "MISR": "app/mme_scalpx/services/strategy_family/misr.py",
    "MISO": "app/mme_scalpx/services/strategy_family/miso.py",
}

STATIC_FILES = [
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

POLICY_EXPECTED = {
    "MIST": "pullback_resume_quality_context_only",
    "MISB": "wall_break_acceptance_context_only",
    "MISC": "compression_retest_wall_context_only",
    "MISR": "registered_zone_support_context_only",
    "MISO": "ladder_shadow_strike_quality_context_only",
}


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


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"present": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_present"] = True
        return data
    except Exception as exc:
        return {"present": True, "parse_error": repr(exc)}


def prereq_status() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for batch, path in PREREQ_PROOFS.items():
        data = load_json(path)
        final = data.get("final_verdict")
        if batch == "26-OI-A":
            ok = final in {"PASS", "PASS_WITH_SURFACE_DRIFT_FINDING"}
        else:
            ok = final == "PASS"
        out[batch] = {
            "path": str(path.relative_to(ROOT)),
            "present": path.exists(),
            "final_verdict": final,
            "ok": ok,
        }
    return out


def wall_context(strength: float, supportive: bool, distance: float = 0.5) -> dict[str, Any]:
    return {
        "distance_strikes": distance,
        "distance_points": 25.0 * distance,
        "wall_strength": strength,
        "wall_strength_score": strength,
        "strength": strength,
        "supportive": supportive,
        "canonical": True,
        "law": "context_not_trigger",
        "wall_authority": "app.mme_scalpx.services.feature_family.strike_selection.build_oi_wall_summary",
    }


def scenario_payload(scenario: str, branch_side: str) -> tuple[dict[str, Any], dict[str, Any]]:
    side_key = "call" if branch_side.upper() == "CALL" else "put"

    hostile_extreme = wall_context(0.99, supportive=False, distance=0.25)
    hostile_strong = wall_context(0.82, supportive=False, distance=0.75)
    supportive_strong = wall_context(0.85, supportive=True, distance=0.75)
    neutral = wall_context(0.35, supportive=False, distance=3.0)

    if scenario == "no_oi_context":
        surface = {}
        view = {}
        return view, surface

    if scenario == "neutral_far_wall":
        active = neutral
    elif scenario == "supportive_near_wall":
        active = supportive_strong
    elif scenario == "hostile_near_strong_wall":
        active = hostile_strong
    elif scenario == "hostile_near_extreme_wall":
        active = hostile_extreme
    else:
        raise ValueError(f"unknown scenario {scenario}")

    surface = {
        "oi_wall_context": active,
        "context": {
            "oi_wall_context": active,
        },
    }
    view = {
        "oi_wall_context": {
            side_key: active,
            "call": active,
            "put": active,
        },
        "shared_core": {
            "oi_wall_context": {
                side_key: active,
                "call": active,
                "put": active,
            },
            "strike_selection": {
                "oi_wall_context": {
                    side_key: active,
                    "call": active,
                    "put": active,
                }
            },
        },
        "common": {
            "cross_option": {
                f"{side_key}_oi_wall_context": active,
                "call_oi_wall_context": active,
                "put_oi_wall_context": active,
            }
        },
        "family_surfaces": {
            "families": {},
            "surfaces_by_branch": {},
        },
    }
    return view, surface


def normalize_result(result: Any) -> tuple[float, bool, str]:
    if not isinstance(result, tuple) or len(result) < 3:
        return 0.0, False, f"invalid_result:{type(result).__name__}"
    score, passed, reason = result[0], result[1], result[2]
    try:
        score_f = float(score)
    except Exception:
        score_f = 0.0
    return score_f, bool(passed), str(reason or "")


def is_oi_reason(reason: str) -> bool:
    text = str(reason or "").lower()
    return any(token in text for token in ("oi", "wall", "dhan", "ladder"))


def evaluate_family(family: str, mod: Any) -> dict[str, Any]:
    branch_call = getattr(mod, "BRANCH_CALL", "CALL")
    branch_put = getattr(mod, "BRANCH_PUT", "PUT")
    min_context = float(getattr(mod, "MIN_CONTEXT_SCORE", 0.0))

    original = getattr(mod, "_BATCH26_OI_C_ORIGINAL_CONTEXT_SCORE", None)
    current = getattr(mod, "context_score", None)

    rows: list[dict[str, Any]] = []
    counts = {
        "original_pass_count": 0,
        "current_pass_count": 0,
        "original_fail_count": 0,
        "current_fail_count": 0,
        "current_oi_hard_veto_count": 0,
        "oi_soft_recovered_count": 0,
        "score_increase_count": 0,
        "score_decrease_count": 0,
        "score_unchanged_count": 0,
    }
    blocker_counts: dict[str, dict[str, int]] = {
        "original": {},
        "current": {},
    }

    scenarios = [
        "no_oi_context",
        "neutral_far_wall",
        "supportive_near_wall",
        "hostile_near_strong_wall",
        "hostile_near_extreme_wall",
    ]

    branches = [
        ("CALL", branch_call),
        ("PUT", branch_put),
    ]

    for branch_label, branch_id in branches:
        for scenario in scenarios:
            view, surface = scenario_payload(scenario, branch_label)

            if callable(original):
                try:
                    original_result = normalize_result(original(view, branch_id, surface))
                except Exception as exc:
                    original_result = (0.0, False, f"original_exception:{repr(exc)}")
            else:
                original_result = (0.0, False, "missing_original_context_score")

            if callable(current):
                try:
                    current_result = normalize_result(current(view, branch_id, surface))
                except Exception as exc:
                    current_result = (0.0, False, f"current_exception:{repr(exc)}")
            else:
                current_result = (0.0, False, "missing_current_context_score")

            original_score, original_passed, original_reason = original_result
            current_score, current_passed, current_reason = current_result

            score_delta = current_score - original_score
            if abs(score_delta) < 1e-12:
                counts["score_unchanged_count"] += 1
            elif score_delta > 0:
                counts["score_increase_count"] += 1
            else:
                counts["score_decrease_count"] += 1

            if original_passed:
                counts["original_pass_count"] += 1
            else:
                counts["original_fail_count"] += 1
                blocker_counts["original"][original_reason] = blocker_counts["original"].get(original_reason, 0) + 1

            if current_passed:
                counts["current_pass_count"] += 1
            else:
                counts["current_fail_count"] += 1
                blocker_counts["current"][current_reason] = blocker_counts["current"].get(current_reason, 0) + 1
                if is_oi_reason(current_reason):
                    counts["current_oi_hard_veto_count"] += 1

            if (not original_passed) and current_passed and is_oi_reason(original_reason + " " + current_reason):
                counts["oi_soft_recovered_count"] += 1

            rows.append({
                "family": family,
                "branch": branch_label,
                "scenario": scenario,
                "min_context_score": min_context,
                "original_score": original_score,
                "original_passed": original_passed,
                "original_reason": original_reason,
                "current_score": current_score,
                "current_passed": current_passed,
                "current_reason": current_reason,
                "score_delta": score_delta,
                "current_score_at_or_above_min": current_score >= min_context,
                "oi_hard_veto_detected": (not current_passed and is_oi_reason(current_reason)),
                "soft_recovered": (not original_passed and current_passed),
            })

    total = len(rows)
    deltas = [float(row["score_delta"]) for row in rows]
    result = {
        "family": family,
        "policy": getattr(mod, "_BATCH26_OI_C_SOFT_POLICY", None),
        "policy_expected": POLICY_EXPECTED[family],
        "policy_ok": getattr(mod, "_BATCH26_OI_C_SOFT_POLICY", None) == POLICY_EXPECTED[family],
        "min_context_score": min_context,
        "total_cases": total,
        "counts": counts,
        "blocker_counts": blocker_counts,
        "candidate_count_delta_current_minus_original": counts["current_pass_count"] - counts["original_pass_count"],
        "score_delta_min": min(deltas) if deltas else 0.0,
        "score_delta_max": max(deltas) if deltas else 0.0,
        "score_delta_sum": sum(deltas),
        "score_delta_mean": (sum(deltas) / len(deltas)) if deltas else 0.0,
        "rows": rows,
    }
    return result


def write_matrix(rows: list[dict[str, Any]]) -> None:
    MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "family",
        "branch",
        "scenario",
        "min_context_score",
        "original_score",
        "original_passed",
        "original_reason",
        "current_score",
        "current_passed",
        "current_reason",
        "score_delta",
        "current_score_at_or_above_min",
        "oi_hard_veto_detected",
        "soft_recovered",
    ]
    with MATRIX_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def main() -> int:
    generated_at_ns = time.time_ns()

    files_inspected = [
        file_info(path)
        for path in list(FAMILY_FILES.values()) + STATIC_FILES
    ]

    prereqs = prereq_status()

    family_results: dict[str, Any] = {}
    matrix_rows: list[dict[str, Any]] = []

    for family, module_name in FAMILY_MODULES.items():
        try:
            mod = importlib.import_module(module_name)
            result = evaluate_family(family, mod)
        except Exception as exc:
            result = {
                "family": family,
                "error": repr(exc),
                "policy_ok": False,
                "counts": {
                    "current_oi_hard_veto_count": 999,
                    "current_pass_count": 0,
                    "original_pass_count": 0,
                },
                "rows": [],
            }
        family_results[family] = {k: v for k, v in result.items() if k != "rows"}
        matrix_rows.extend(result.get("rows", []))

    write_matrix(matrix_rows)

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
    for rel in list(FAMILY_FILES.values()) + [
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

    aggregate = {
        "families": len(FAMILY_MODULES),
        "matrix_rows": len(matrix_rows),
        "original_pass_count": sum(r.get("counts", {}).get("original_pass_count", 0) for r in family_results.values()),
        "current_pass_count": sum(r.get("counts", {}).get("current_pass_count", 0) for r in family_results.values()),
        "original_fail_count": sum(r.get("counts", {}).get("original_fail_count", 0) for r in family_results.values()),
        "current_fail_count": sum(r.get("counts", {}).get("current_fail_count", 0) for r in family_results.values()),
        "current_oi_hard_veto_count": sum(r.get("counts", {}).get("current_oi_hard_veto_count", 0) for r in family_results.values()),
        "oi_soft_recovered_count": sum(r.get("counts", {}).get("oi_soft_recovered_count", 0) for r in family_results.values()),
        "score_increase_count": sum(r.get("counts", {}).get("score_increase_count", 0) for r in family_results.values()),
        "score_decrease_count": sum(r.get("counts", {}).get("score_decrease_count", 0) for r in family_results.values()),
        "score_unchanged_count": sum(r.get("counts", {}).get("score_unchanged_count", 0) for r in family_results.values()),
    }
    aggregate["candidate_count_delta_current_minus_original"] = (
        aggregate["current_pass_count"] - aggregate["original_pass_count"]
    )

    family_policy_ok = all(r.get("policy_ok") for r in family_results.values())
    family_impact_ok = (
        aggregate["matrix_rows"] == len(FAMILY_MODULES) * 2 * 5
        and aggregate["current_oi_hard_veto_count"] == 0
        and aggregate["current_pass_count"] >= aggregate["original_pass_count"]
    )

    prereq_ok = all(item.get("ok") for item in prereqs.values())

    blocking_checks = {
        "prereq_oi_proofs_ok": prereq_ok,
        "family_policy_ok": family_policy_ok,
        "family_impact_matrix_complete": aggregate["matrix_rows"] == len(FAMILY_MODULES) * 2 * 5,
        "family_impact_no_oi_hard_veto": aggregate["current_oi_hard_veto_count"] == 0,
        "family_impact_candidate_count_not_reduced_by_oi_soft_layer": aggregate["current_pass_count"] >= aggregate["original_pass_count"],
        "canonical_wall_authority_preserved": all(canonical_wall_authority_checks.values()),
        "strategy_hold_only_preserved": all(strategy_hold_only_checks.values()),
        "live_order_bypass_absent": all(live_order_bypass_checks.values()),
        "oi_not_used_as_trigger": not suspicious_trigger_lines,
        "matrix_csv_written": MATRIX_PATH.exists(),
    }

    blocking_failures = false_checks(blocking_checks)
    final_verdict = "PASS" if not blocking_failures else "FAIL"

    recommended_next_batch = (
        "Batch 26-OI-E is NOT recommended yet for hard veto. First run market-session/replay candidate-impact observation using this matrix and compare real candidate counts."
        if final_verdict == "PASS"
        else "Stop. Fix blocking failures before any further OI scoring or hard-veto work."
    )

    proof = {
        "proof_name": "proof_oi_replay_report_impact",
        "batch": "26-OI-D",
        "generated_at_ns": generated_at_ns,
        "final_verdict": final_verdict,
        "files_inspected": files_inspected,
        "prereq_status": prereqs,
        "aggregate": aggregate,
        "family_results": family_results,
        "matrix_csv_path": str(MATRIX_PATH.relative_to(ROOT)),
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
        "batch": "26-OI-D",
        "final_verdict": final_verdict,
        "prereq_oi_proofs_ok": prereq_ok,
        "matrix_rows": aggregate["matrix_rows"],
        "original_pass_count": aggregate["original_pass_count"],
        "current_pass_count": aggregate["current_pass_count"],
        "candidate_count_delta_current_minus_original": aggregate["candidate_count_delta_current_minus_original"],
        "current_oi_hard_veto_count": aggregate["current_oi_hard_veto_count"],
        "oi_soft_recovered_count": aggregate["oi_soft_recovered_count"],
        "score_increase_count": aggregate["score_increase_count"],
        "score_decrease_count": aggregate["score_decrease_count"],
        "score_unchanged_count": aggregate["score_unchanged_count"],
        "canonical_wall_authority_preserved": all(canonical_wall_authority_checks.values()),
        "strategy_hold_only_preserved": all(strategy_hold_only_checks.values()),
        "live_order_bypass_detected": proof["live_order_bypass_detected"],
        "oi_used_as_trigger_detected": bool(suspicious_trigger_lines),
        "blocking_failures": blocking_failures,
        "proof_path": str(PROOF_PATH),
        "matrix_csv_path": str(MATRIX_PATH),
        "recommended_next_batch": recommended_next_batch,
    }, indent=2, sort_keys=True))

    return 0 if final_verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
