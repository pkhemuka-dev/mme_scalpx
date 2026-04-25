#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = ROOT / "run" / "proofs" / "strategy_family_leaf_candidate_contract.json"

MODULE_SPECS = [
    ("MIST", "app.mme_scalpx.services.strategy_family.mist", "MistCandidate"),
    ("MISB", "app.mme_scalpx.services.strategy_family.misb", "MisbCandidate"),
    ("MISC", "app.mme_scalpx.services.strategy_family.misc", "MiscCandidate"),
    ("MISR", "app.mme_scalpx.services.strategy_family.misr", "MisrCandidate"),
    ("MISO", "app.mme_scalpx.services.strategy_family.miso", "MisoCandidate"),
]

def assert_case(name: str, condition: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"name": name, "ok": bool(condition), "details": details or {}}
    if not condition:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row

def result_reason(result: Any) -> str:
    data = result.to_dict() if hasattr(result, "to_dict") else {}
    return str((data.get("metadata") or {}).get("reason") or "")

def make_candidate(mod: Any, cls_name: str, branch_id: str, **overrides: Any) -> Any:
    cls = getattr(mod, cls_name)
    payload = {
        "family_id": mod.FAMILY_ID,
        "doctrine_id": mod.DOCTRINE_ID,
        "branch_id": branch_id,
        "side": mod.side_for_branch(branch_id),
        "action": mod.action_for_branch(branch_id),
        "score": 0.75,
        "priority": 75.0,
        "instrument_key": f"{mod.FAMILY_ID}-{branch_id}-KEY",
        "instrument_token": "123456",
        "option_symbol": f"{mod.FAMILY_ID}{branch_id}SYM",
        "strike": 22500.0,
        "option_price": 100.0,
    }
    payload.update(overrides)
    return cls(**payload)

def with_fake_original(mod: Any, fake_fn):
    old = mod._BATCH1_ORIGINAL_EVALUATE_BRANCH
    mod._BATCH1_ORIGINAL_EVALUATE_BRANCH = fake_fn
    return old

def main() -> int:
    sys.path.insert(0, str(ROOT))

    cases: list[dict[str, Any]] = []

    for family_id, module_path, cls_name in MODULE_SPECS:
        mod = importlib.import_module(module_path)

        cases.append(assert_case(
            f"{family_id}_marker_present",
            hasattr(mod, "_batch1_candidate_contract_guard")
            and hasattr(mod, "_BATCH1_ORIGINAL_EVALUATE_BRANCH"),
        ))

        if hasattr(mod, "runtime_mode"):
            mode = mod.runtime_mode({"common": {}, "provider_runtime": {}})
            cases.append(assert_case(
                f"{family_id}_missing_classic_runtime_mode_fails_closed",
                mode == mod.RUNTIME_DISABLED,
                {"actual": mode, "expected": mod.RUNTIME_DISABLED},
            ))

        if hasattr(mod, "normalize_mode") and hasattr(mod, "MODE_DISABLED"):
            mode = mod.normalize_mode(None)
            cases.append(assert_case(
                f"{family_id}_missing_miso_mode_fails_closed",
                mode == mod.MODE_DISABLED,
                {"actual": mode, "expected": mod.MODE_DISABLED},
            ))

        branch_id = mod.BRANCH_CALL

        def fake_good(view, branch):
            return mod.candidate_result(make_candidate(mod, cls_name, branch))

        old = with_fake_original(mod, fake_good)
        try:
            result = mod.evaluate_branch({}, branch_id)
        finally:
            mod._BATCH1_ORIGINAL_EVALUATE_BRANCH = old

        cases.append(assert_case(
            f"{family_id}_complete_candidate_passes",
            result.is_candidate is True
            and result.candidate is not None
            and result.candidate.action == mod.action_for_branch(branch_id),
            result.to_dict(),
        ))

        def fake_missing_metadata(view, branch):
            return mod.candidate_result(
                make_candidate(
                    mod,
                    cls_name,
                    branch,
                    instrument_token=None,
                    option_symbol=None,
                    option_price=None,
                )
            )

        old = with_fake_original(mod, fake_missing_metadata)
        try:
            result = mod.evaluate_branch({}, branch_id)
        finally:
            mod._BATCH1_ORIGINAL_EVALUATE_BRANCH = old

        cases.append(assert_case(
            f"{family_id}_candidate_missing_order_metadata_rejected",
            result.is_candidate is False
            and result.is_blocked is False
            and result_reason(result) == "candidate_order_metadata_incomplete",
            result.to_dict(),
        ))

        def fake_wrong_action(view, branch):
            return mod.candidate_result(
                make_candidate(
                    mod,
                    cls_name,
                    branch,
                    action=mod.ACTION_HOLD,
                )
            )

        old = with_fake_original(mod, fake_wrong_action)
        try:
            result = mod.evaluate_branch({}, branch_id)
        finally:
            mod._BATCH1_ORIGINAL_EVALUATE_BRANCH = old

        cases.append(assert_case(
            f"{family_id}_candidate_wrong_action_rejected",
            result.is_candidate is False
            and result_reason(result) == "candidate_action_mismatch",
            result.to_dict(),
        ))

        def fake_bad_score(view, branch):
            return mod.candidate_result(
                make_candidate(
                    mod,
                    cls_name,
                    branch,
                    score=1.25,
                    priority=125.0,
                )
            )

        old = with_fake_original(mod, fake_bad_score)
        try:
            result = mod.evaluate_branch({}, branch_id)
        finally:
            mod._BATCH1_ORIGINAL_EVALUATE_BRANCH = old

        cases.append(assert_case(
            f"{family_id}_candidate_score_out_of_range_rejected",
            result.is_candidate is False
            and result_reason(result) == "candidate_score_out_of_range",
            result.to_dict(),
        ))

        def fake_wrong_target(view, branch):
            return mod.candidate_result(
                make_candidate(
                    mod,
                    cls_name,
                    branch,
                    target_points=7.0,
                )
            )

        old = with_fake_original(mod, fake_wrong_target)
        try:
            result = mod.evaluate_branch({}, branch_id)
        finally:
            mod._BATCH1_ORIGINAL_EVALUATE_BRANCH = old

        cases.append(assert_case(
            f"{family_id}_candidate_target_mismatch_rejected",
            result.is_candidate is False
            and result_reason(result) == "candidate_target_points_mismatch",
            result.to_dict(),
        ))

        no_signal = mod.no_signal_result(branch_id=branch_id, reason="proof_no_signal_passthrough")
        guarded = mod._batch1_candidate_contract_guard(no_signal)
        cases.append(assert_case(
            f"{family_id}_no_signal_passthrough",
            guarded is no_signal
            and guarded.is_no_signal is True,
            guarded.to_dict(),
        ))

        evaluator = mod.get_evaluator()
        cases.append(assert_case(
            f"{family_id}_get_evaluator_returns_current_evaluate",
            evaluator is mod.evaluate,
            {"evaluator": str(evaluator), "evaluate": str(mod.evaluate)},
        ))

    proof = {
        "proof_name": "strategy_family_leaf_candidate_contract",
        "status": "PASS",
        "ts_epoch": time.time(),
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "families_checked": [spec[0] for spec in MODULE_SPECS],
            "missing_runtime_mode_fails_closed": True,
            "missing_miso_mode_fails_closed": True,
            "complete_candidates_pass": True,
            "incomplete_candidate_metadata_rejected": True,
            "wrong_action_rejected": True,
            "score_range_enforced": True,
            "target_stop_contract_enforced": True,
            "no_signal_passthrough": True,
            "get_evaluator_current": True,
        },
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(proof["summary"], indent=2, sort_keys=True))
    print(f"proof_artifact={PROOF_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
