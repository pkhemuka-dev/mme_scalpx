#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family import activation as A
from app.mme_scalpx.services.strategy_family import arbitration as ARB
from app.mme_scalpx.services.strategy_family import cooldowns as CD
from app.mme_scalpx.services.strategy_family import decisions as D
from app.mme_scalpx.services.strategy_family import eligibility as E
from app.mme_scalpx.services.strategy_family import registry as R
from app.mme_scalpx.services.strategy_family.doctrine_runtime import (
    DoctrineSignalCandidate,
    candidate_result,
)


def _candidate(
    *,
    family_id: str,
    branch_id: str,
    score: float,
    priority: float,
    metadata: dict[str, Any] | None = None,
) -> DoctrineSignalCandidate:
    side = N.SIDE_CALL if branch_id == N.BRANCH_CALL else N.SIDE_PUT
    return DoctrineSignalCandidate(
        family_id=family_id,
        doctrine_id=family_id,
        branch_id=branch_id,
        side=side,
        instrument_key=f"{family_id}:{branch_id}:INST",
        entry_mode=N.ENTRY_MODE_ATM,
        family_runtime_mode=N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        strategy_runtime_mode=N.STRATEGY_RUNTIME_MODE_NORMAL
        if family_id != N.STRATEGY_FAMILY_MISO
        else N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
        score=score,
        priority=priority,
        setup_kind="proof",
        target_points=5.0,
        stop_points=4.0,
        tick_size=0.05,
        quantity_lots_hint=1,
        metadata=dict(metadata or {}),
    )


def main() -> int:
    cases: list[dict[str, Any]] = []

    high = _candidate(
        family_id=N.STRATEGY_FAMILY_MIST,
        branch_id=N.BRANCH_CALL,
        score=0.90,
        priority=90.0,
    )
    low = _candidate(
        family_id=N.STRATEGY_FAMILY_MISB,
        branch_id=N.BRANCH_CALL,
        score=0.50,
        priority=50.0,
    )

    selected = ARB.select_best_candidate([low, high])
    cases.append(
        {
            "case": "arbitration_higher_priority_wins",
            "status": "PASS" if selected is high else "FAIL",
            "selected": None if selected is None else selected.family_id,
        }
    )

    frames = [
        A._evaluation_to_frame(candidate_result(low), family_id=low.family_id, branch_id=low.branch_id),
        A._evaluation_to_frame(candidate_result(high), family_id=high.family_id, branch_id=high.branch_id),
    ]
    act_selected = A.rank_activation_candidates(frames)[0]
    cases.append(
        {
            "case": "activation_and_arbitration_select_same_candidate",
            "status": "PASS"
            if selected is not None
            and act_selected.family_id == selected.family_id
            and act_selected.branch_id == selected.branch_id
            else "FAIL",
            "activation_selected": act_selected.family_id,
            "arbitration_selected": None if selected is None else selected.family_id,
        }
    )

    frame = A._evaluation_to_frame(candidate_result(high), family_id=high.family_id, branch_id=high.branch_id)
    cases.append(
        {
            "case": "doctrine_evaluation_result_dataclass_normalizes",
            "status": "PASS"
            if frame.is_candidate
            and frame.candidate is not None
            and frame.action == N.ACTION_ENTER_CALL
            and frame.candidate.get("score") == 0.90
            and frame.candidate.get("priority") == 90.0
            else "FAIL",
            "frame": frame.to_dict(),
        }
    )

    try:
        parity = A.validate_registry_activation_parity()
        cases.append(
            {
                "case": "activation_registry_path_parity",
                "status": "PASS",
                "paths": parity,
            }
        )
    except Exception as exc:
        cases.append(
            {
                "case": "activation_registry_path_parity",
                "status": "FAIL",
                "error": str(exc),
            }
        )

    bad_view = {
        "hold_only": True,
        "safe_to_consume": True,
        "data_valid": False,
        "warmup_complete": True,
    }
    decision = A.build_activation_decision(
        bad_view,
        config=A.StrategyFamilyActivationConfig(
            activation_mode=A.ACTIVATION_MODE_DRY_RUN,
            allow_candidate_promotion=True,
        ),
    )
    cases.append(
        {
            "case": "global_gate_failure_skips_leaf_evaluation",
            "status": "PASS"
            if decision.hold
            and decision.reason == "view_data_invalid"
            and decision.metadata.get("leaf_evaluation_skipped") is True
            and decision.candidates == ()
            else "FAIL",
            "decision": decision.to_dict(),
        }
    )

    promoted_without_contract = A.StrategyFamilyActivationDecision(
        activation_mode=A.ACTIVATION_MODE_PAPER_ARMED,
        action=N.ACTION_ENTER_CALL,
        hold=False,
        promoted=True,
        safe_to_promote=True,
        reason="paper_candidate_promoted",
        selected=frame,
        candidates=(frame,),
        blocked=(),
        no_signal=(),
        family_count=1,
        branch_count=1,
        metadata={},
    )
    cases.append(
        {
            "case": "promotion_contract_checker_rejects_missing_order_intent_metadata",
            "status": "PASS" if not A._batch11_candidate_has_order_intent_contract(promoted_without_contract.selected) else "FAIL",
        }
    )

    try:
        D.build_entry_decision(
            now_ns=1,
            quantity_lots=1,
            candidate=high,
        )
    except Exception as exc:
        cases.append(
            {
                "case": "entry_decision_missing_execution_metadata_rejected",
                "status": "PASS",
                "error": str(exc),
            }
        )
    else:
        cases.append(
            {
                "case": "entry_decision_missing_execution_metadata_rejected",
                "status": "FAIL",
                "error": "accepted missing execution metadata",
            }
        )

    ready_meta = {
        "option_symbol": "NIFTY_TEST_CE",
        "option_token": "12345",
        "strike": 22500.0,
        "limit_price": 100.0,
        "active_futures_provider_id": N.PROVIDER_DHAN,
        "active_selected_option_provider_id": N.PROVIDER_DHAN,
        "active_option_context_provider_id": N.PROVIDER_DHAN,
        "strategy_order_intent_valid": True,
        "execution_contract_ready": True,
        "risk_gate_ready": True,
        "provider_identity_ready": True,
    }
    ready_candidate = _candidate(
        family_id=N.STRATEGY_FAMILY_MIST,
        branch_id=N.BRANCH_CALL,
        score=0.95,
        priority=95.0,
        metadata=ready_meta,
    )
    try:
        entry_decision = D.build_entry_decision(
            now_ns=1,
            quantity_lots=1,
            candidate=ready_candidate,
        )
        cases.append(
            {
                "case": "entry_decision_with_execution_metadata_passes",
                "status": "PASS" if entry_decision.metadata.get("option_token") == "12345" else "FAIL",
                "metadata": dict(entry_decision.metadata),
            }
        )
    except Exception as exc:
        cases.append(
            {
                "case": "entry_decision_with_execution_metadata_passes",
                "status": "FAIL",
                "error": str(exc),
            }
        )

    cooldown_cases = [
        ("misr_proof_failure_10", "proof_failure_exit", 10.0, False),
        ("misr_liquidity_12", "liquidity_exit", 12.0, False),
        ("misr_feed_failure_15", "feed_failure_exit", 15.0, False),
        ("misr_reconciliation_15", "reconciliation_exit", 15.0, False),
        ("misr_session_end_reset", "session_end_flatten_exit", 0.0, True),
    ]
    for label, reason, expected_seconds, expected_session_reset in cooldown_cases:
        cd = CD.route_cooldown(
            family_id=N.STRATEGY_FAMILY_MISR,
            exit_reason=reason,
            regime="NORMAL",
            params={},
        )
        cases.append(
            {
                "case": label,
                "status": "PASS"
                if cd.seconds == expected_seconds and cd.session_reset_required is expected_session_reset
                else "FAIL",
                "cooldown": cd.to_dict(),
            }
        )

    cases.append(
        {
            "case": "mist_micro_trap_resolved_prefers_new_field",
            "status": "PASS"
            if E.mist_micro_trap_resolved({"micro_trap_resolved": True, "micro_trap_blocked": False}) is True
            else "FAIL",
        }
    )

    # Build a lightweight BranchEligibilityResult directly to prove the annotation
    # is report-only and does not turn MISC/MISR support into activation readiness
    # without a sequence flag.
    misc_result = E.BranchEligibilityResult(
        family_id=N.STRATEGY_FAMILY_MISC,
        branch_id=N.BRANCH_CALL,
        eligible=True,
        global_gate_pass=True,
        family_gate_pass=True,
        context_pass=True,
        option_tradability_pass=True,
        structural_pass=True,
        blocked_reasons=(),
        regime="NORMAL",
        strategy_runtime_mode=N.STRATEGY_RUNTIME_MODE_NORMAL,
        family_runtime_mode=N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        support={},
    )
    misc_annotation = E.annotate_activation_readiness(misc_result, support={})
    cases.append(
        {
            "case": "misc_support_without_sequence_not_activation_eligible",
            "status": "PASS"
            if misc_annotation["structural_support_pass"] is True
            and misc_annotation["state_machine_sequence_pass"] is False
            and misc_annotation["activation_eligible"] is False
            else "FAIL",
            "annotation": misc_annotation,
        }
    )

    misr_result = E.BranchEligibilityResult(
        family_id=N.STRATEGY_FAMILY_MISR,
        branch_id=N.BRANCH_CALL,
        eligible=True,
        global_gate_pass=True,
        family_gate_pass=True,
        context_pass=True,
        option_tradability_pass=True,
        structural_pass=True,
        blocked_reasons=(),
        regime="NORMAL",
        strategy_runtime_mode=N.STRATEGY_RUNTIME_MODE_NORMAL,
        family_runtime_mode=N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        support={"state_machine_sequence_pass": True},
    )
    misr_annotation = E.annotate_activation_readiness(misr_result, support=misr_result.support)
    cases.append(
        {
            "case": "misr_sequence_support_becomes_activation_eligible",
            "status": "PASS"
            if misr_annotation["activation_eligible"] is True
            and misr_annotation["state_machine_sequence_pass"] is True
            else "FAIL",
            "annotation": misr_annotation,
        }
    )

    import app.mme_scalpx.services.strategy_family as SF

    for name in (
        "FAMILY_ORDER",
        "get_family_evaluator",
        "pre_entry_gate",
        "select_best_candidate",
        "build_activation_decision",
        "build_entry_decision",
        "route_cooldown",
    ):
        cases.append(
            {
                "case": f"package_exports_{name}",
                "status": "PASS" if hasattr(SF, name) else "FAIL",
            }
        )

    failed = [case for case in cases if case.get("status") != "PASS"]
    proof = {
        "proof": "strategy_family_shared_layer_contracts",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out = PROJECT_ROOT / "run" / "proofs" / "strategy_family_shared_layer_contracts.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
