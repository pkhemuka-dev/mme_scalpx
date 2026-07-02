#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import py_compile
import re
import time

from app.mme_scalpx.core import names as N
from app.mme_scalpx.replay import feature_adapter
from app.mme_scalpx.replay import strategy_adapter
from app.mme_scalpx.services.strategy_family import miv_r_contract as MIV


def base_row(**overrides):
    row = {
        "schema_version": "miv_research_candidate_v0_1",
        "contract_version": MIV.MIV_CONTRACT_VERSION,
        "run_id": "proof_run",
        "dataset_id": "proof_dataset",
        "family_id": MIV.MIV_FAMILY_ID,
        "research_mode": "MIV_ZERODHA_LITE",
        "candidate_type": "CALL_PRESSURE_BURST",
        "miv_candidate_id": "miv_proof_1",
        "event_ts": "2026-06-11T23:00:00+05:30",
        "event_ns": 1,
        "window_start_ns": 1,
        "window_end_ns": 2,
        "symbol": "NIFTY_PROOF_CE",
        "option_symbol": "NIFTY_PROOF_CE",
        "side": "CALL",
        "action": "ENTRY",
        "qty": 75,
        "price": 100.0,
        "score": 5.5,
        "research_shadow_only": True,
        "label_only": False,
        "trade_shadow_eligible": True,
        "route_to_candidate_audit": True,
        "route_to_risk_shadow": True,
        "route_to_execution_shadow": True,
        "route_to_order_intent_ledger": True,
        "order_allowed": False,
        "broker_send_enabled": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
        "dhan_context_status": "UNAVAILABLE",
        "dhan_full_enabled": False,
        "hard_blocked": False,
        "hard_block_reasons": (),
        "soft_block_reasons": (),
        "tradability_ok": True,
        "freshness_ok": True,
    }
    row.update(overrides)
    return row


def main() -> None:
    module_path = pathlib.Path("app/mme_scalpx/services/strategy_family/miv_r_contract.py")
    proof_path = pathlib.Path(__file__)

    py_compile.compile(str(module_path), doraise=True)
    py_compile.compile(str(proof_path), doraise=True)

    production_families = tuple(getattr(N, "STRATEGY_FAMILY_IDS", ()))
    doctrine_ids = tuple(getattr(N, "DOCTRINE_IDS", ()))
    replay_feature_families = tuple(getattr(feature_adapter, "REPLAY_FEATURE_FAMILIES", ()))
    replay_strategy_families = tuple(getattr(strategy_adapter, "REPLAY_STRATEGY_FAMILIES", ()))

    valid_call = MIV.validate_miv_candidate_row(base_row())
    valid_neutral = MIV.validate_miv_candidate_row(base_row(
        candidate_type="NEUTRAL_ACTIVE_LABEL",
        side="",
        action="LABEL_ONLY",
        score=5.2,
        label_only=True,
        trade_shadow_eligible=False,
        route_to_risk_shadow=False,
        route_to_execution_shadow=False,
        route_to_order_intent_ledger=False,
    ))
    invalid_live = MIV.validate_miv_candidate_row(base_row(order_allowed=True))
    invalid_dhan_full = MIV.validate_miv_candidate_row(base_row(
        research_mode="MIV_DHAN_FULL",
        dhan_context_status="UNAVAILABLE",
        dhan_full_enabled=False,
    ))
    invalid_missing_symbol = MIV.validate_miv_candidate_row(base_row(symbol="", option_symbol=""))

    text = module_path.read_text(encoding="utf-8")
    forbidden_call_patterns = [
        r"\bplace_order\s*\(",
        r"\bkite\.place_order\b",
        r"\bdhan.*place_order\b",
        r"\border_send\s*\(",
    ]
    forbidden_hits = [
        pattern for pattern in forbidden_call_patterns
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]

    checks = {
        "miv_contract_inside_strategy_family": module_path.exists(),
        "miv_not_in_strategy_family_ids": MIV.MIV_FAMILY_ID not in production_families,
        "miv_not_in_doctrine_ids": MIV.MIV_FAMILY_ID not in doctrine_ids,
        "miv_not_in_replay_feature_families": MIV.MIV_FAMILY_ID not in replay_feature_families,
        "miv_not_in_replay_strategy_families": MIV.MIV_FAMILY_ID not in replay_strategy_families,
        "miv_dormant_not_active_production": MIV.MIV_IS_ACTIVE_PRODUCTION_FAMILY is False,
        "miv_research_shadow_only": MIV.MIV_RESEARCH_SHADOW_ONLY is True,
        "valid_call_candidate_ok": valid_call["ok"] is True,
        "valid_neutral_label_ok": valid_neutral["ok"] is True,
        "live_order_allowed_rejected": invalid_live["ok"] is False,
        "dhan_full_without_dhan_rejected": invalid_dhan_full["ok"] is False,
        "missing_symbol_rejected": invalid_missing_symbol["ok"] is False,
        "no_forbidden_broker_call_patterns": not forbidden_hits,
    }

    classification = "PASS_MIV_R1A_STRATEGY_FAMILY_DORMANT_CONTRACT_PATCH_NO_REPLAY_NO_ORDER" if all(checks.values()) else "FAIL_MIV_R1A_STRATEGY_FAMILY_DORMANT_CONTRACT"

    print(json.dumps({
        "batch": "LANE-MIV-R1A_STRATEGY_FAMILY_DORMANT_CONTRACT_PATCH_NO_REPLAY_NO_ORDER",
        "classification": classification,
        "created_at_epoch": time.time(),
        "checks": checks,
        "contract_summary": MIV.contract_summary(),
        "valid_call": valid_call,
        "valid_neutral": valid_neutral,
        "invalid_live": invalid_live,
        "invalid_dhan_full": invalid_dhan_full,
        "invalid_missing_symbol": invalid_missing_symbol,
        "forbidden_hits": forbidden_hits,
        "safety": {
            "source_patch": True,
            "strategy_family_contract_only": True,
            "active_registry_change": False,
            "evaluator_added": False,
            "replay_execution": False,
            "broker_order": False,
            "risk_service_start": False,
            "execution_service_start": False,
            "redis_delete": False,
            "lock_delete": False,
            "paper_live_enabled": False,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
