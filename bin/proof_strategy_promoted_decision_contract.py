#!/usr/bin/env python3
from __future__ import annotations

from _final_static_proof_helpers import contains_all, contains_any, emit, exists_nonempty

FILES = [
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/execution.py",
]

checks = [exists_nonempty(f) for f in FILES]
checks += [
    contains_any(
        "strategy_order_intent_or_promoted_decision_surface",
        FILES,
        ["StrategyOrderIntent", "PromotedDecision", "promoted", "order_intent"],
    ),
    contains_all(
        "required_execution_metadata_terms",
        FILES,
        ["option_symbol", "option_token", "limit_price", "strike"],
    ),
    contains_any(
        "candidate_cannot_directly_become_order",
        FILES,
        ["promotion", "activation_promoted", "live_orders_allowed", "report_only"],
    ),
    contains_any(
        "missing_metadata_rejected_language",
        FILES,
        ["reject", "missing", "invalid", "required"],
    ),
    contains_any(
        "payload_json_action_contract",
        FILES,
        ["payload_json", "action"],
    ),
]

raise SystemExit(emit(
    "proof_strategy_promoted_decision_contract",
    checks,
    does_not_prove=["paper_armed_activation_readiness", "live_order_routing"],
))
