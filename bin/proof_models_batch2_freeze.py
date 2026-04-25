#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import models as M
from app.mme_scalpx.core import names


def _expect_reject(label: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        fn()
    except M.ModelValidationError as exc:
        return {"case": label, "status": "PASS", "error": str(exc)}
    except Exception as exc:
        return {"case": label, "status": "FAIL", "error": f"wrong exception: {type(exc).__name__}: {exc}"}
    return {"case": label, "status": "FAIL", "error": "accepted invalid payload"}


def _base_intent(**overrides: Any) -> dict[str, Any]:
    raw: dict[str, Any] = {
        "decision_id": "d-call-1",
        "ts_event_ns": 1,
        "ts_expiry_ns": 10,
        "action": names.ACTION_ENTER_CALL,
        "side": names.SIDE_CALL,
        "position_effect": names.POSITION_EFFECT_OPEN,
        "quantity_lots": 1,
        "instrument_key": "NFO:NIFTY:CE:ATM",
        "strategy_family_id": names.STRATEGY_FAMILY_MIST,
        "doctrine_id": names.STRATEGY_FAMILY_MIST,
        "branch_id": names.BRANCH_CALL,
        "family_runtime_mode": names.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        "strategy_runtime_mode": names.STRATEGY_RUNTIME_MODE_NORMAL,
        "option_symbol": "NIFTYTESTCE",
        "option_token": "123456",
        "strike": 22500.0,
        "limit_price": 101.25,
        "entry_mode": names.ENTRY_MODE_ATM,
        "system_state": names.STATE_ARMED,
        "reason_code": "TEST_PROMOTION",
        "active_futures_provider_id": names.PROVIDER_ZERODHA,
        "active_selected_option_provider_id": names.PROVIDER_DHAN,
        "active_option_context_provider_id": names.PROVIDER_DHAN,
        "execution_primary_provider_id": names.PROVIDER_ZERODHA,
        "execution_fallback_provider_id": names.PROVIDER_DHAN,
        "confidence": 0.75,
        "metadata": {"source": "proof"},
    }
    raw.update(overrides)
    return raw


def _prove() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    required_models = (
        "StrategyOrderIntent",
        "StrategyFamilyCandidate",
        "ProviderInstrumentRef",
        "EffectiveRuntimeConfigState",
    )

    missing_exports = [name for name in required_models if not hasattr(M, name)]
    missing_registry = [
        getattr(M, name)._TYPE
        for name in required_models
        if hasattr(M, name) and getattr(M, name)._TYPE not in M.MODEL_REGISTRY
    ]

    # Valid CALL intent.
    call_intent = M.StrategyOrderIntent.from_mapping(_base_intent())
    call_payload = call_intent.to_strategy_decision_payload()
    call_decision = call_intent.to_strategy_decision()
    cases.append(
        {
            "case": "valid_enter_call_promotes_to_strategy_decision",
            "status": "PASS",
            "decision_action": call_decision.action,
            "metadata_keys": sorted(call_payload["metadata"].keys()),
        }
    )

    # Valid PUT intent.
    put_intent = M.StrategyOrderIntent.from_mapping(
        _base_intent(
            decision_id="d-put-1",
            action=names.ACTION_ENTER_PUT,
            side=names.SIDE_PUT,
            branch_id=names.BRANCH_PUT,
            instrument_key="NFO:NIFTY:PE:ATM",
            option_symbol="NIFTYTESTPE",
            option_token="654321",
            strategy_family_id=names.STRATEGY_FAMILY_MISB,
            doctrine_id=names.STRATEGY_FAMILY_MISB,
        )
    )
    cases.append(
        {
            "case": "valid_enter_put_promotes_to_strategy_decision",
            "status": "PASS",
            "decision_action": put_intent.to_strategy_decision().action,
        }
    )

    # Valid family candidate.
    candidate = M.StrategyFamilyCandidate.from_mapping(
        {
            "candidate_id": "c-1",
            "ts_event_ns": 1,
            "strategy_family_id": names.STRATEGY_FAMILY_MISC,
            "doctrine_id": names.STRATEGY_FAMILY_MISC,
            "branch_id": names.BRANCH_CALL,
            "side": names.SIDE_CALL,
            "family_runtime_mode": names.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
            "strategy_runtime_mode": names.STRATEGY_RUNTIME_MODE_NORMAL,
            "score": 0.8,
            "confidence": 0.7,
            "reason_code": "CANDIDATE_OK",
        }
    )
    cases.append({"case": "strategy_family_candidate_valid", "status": "PASS", "candidate_id": candidate.candidate_id})

    # Valid provider instrument ref.
    ref = M.ProviderInstrumentRef.from_mapping(
        {
            "option_side": names.SIDE_CALL,
            "instrument_key": "NFO:NIFTY:CE:ATM",
            "option_symbol": "NIFTYTESTCE",
            "option_token": "123456",
            "strike": 22500.0,
            "provider_id": names.PROVIDER_DHAN,
            "provider_exchange_segment": "NSE_FNO",
            "dhan_security_id": "987654",
            "zerodha_token": "123456",
        }
    )
    cases.append({"case": "provider_instrument_ref_valid", "status": "PASS", "option_symbol": ref.option_symbol})

    # Valid Dhan context token equivalence fields.
    dhan = M.DhanContextState.from_mapping(
        {
            "ts_event_ns": 1,
            "provider_id": names.PROVIDER_DHAN,
            "context_status": names.PROVIDER_STATUS_HEALTHY,
            "selected_call_instrument_key": "NFO:NIFTY:CE:ATM",
            "selected_call_option_symbol": "NIFTYTESTCE",
            "selected_call_option_token": "123456",
            "selected_call_dhan_security_id": "987654",
            "selected_call_zerodha_token": "123456",
            "provider_exchange_segment": "NSE_FNO",
        }
    )
    cases.append(
        {
            "case": "dhan_context_equivalence_fields_valid",
            "status": "PASS",
            "selected_call_option_symbol": dhan.selected_call_option_symbol,
        }
    )

    # Valid provider transition safety fields.
    transition = M.ProviderTransitionEvent.from_mapping(
        {
            "ts_event_ns": 1,
            "role": names.PROVIDER_ROLE_EXECUTION_PRIMARY,
            "to_provider_id": names.PROVIDER_DHAN,
            "from_provider_id": names.PROVIDER_ZERODHA,
            "reason": names.PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED,
            "has_open_position": True,
            "setup_invalidated": True,
            "switch_allowed": False,
            "blocked_reason": "OPEN_POSITION_NO_MIGRATION",
        }
    )
    cases.append({"case": "provider_transition_safety_valid", "status": "PASS", "switch_allowed": transition.switch_allowed})

    # Valid execution route state.
    execution_state = M.ExecutionState.from_mapping(
        {
            "execution_mode": names.EXECUTION_MODE_NORMAL,
            "entry_pending": False,
            "exit_pending": False,
            "family_runtime_mode": names.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
            "execution_primary_provider_id": names.PROVIDER_ZERODHA,
            "execution_fallback_provider_id": names.PROVIDER_DHAN,
            "active_execution_provider_id": names.PROVIDER_ZERODHA,
            "last_execution_provider_id": names.PROVIDER_ZERODHA,
            "last_broker_order_id": "bo-1",
            "provider_failover_used": False,
            "provider_route_reason": "PRIMARY_HEALTHY",
        }
    )
    cases.append({"case": "execution_state_provider_route_valid", "status": "PASS", "active": execution_state.active_execution_provider_id})

    # Valid effective runtime config state.
    runtime = M.EffectiveRuntimeConfigState.from_mapping(
        {
            "ts_event_ns": 1,
            "runtime_mode": "paper",
            "trading_enabled": False,
            "allow_live_orders": False,
            "provider_runtime_enabled": True,
            "bootstrap_groups_on_start": False,
            "source_of_truth": "runtime_yaml",
            "config_file_runtime_mode": "paper",
            "env_runtime_mode": "paper",
            "settings_runtime_mode": "live",
            "family_runtime_mode": names.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        }
    )
    cases.append({"case": "effective_runtime_config_state_valid", "status": "PASS", "runtime_mode": runtime.runtime_mode})

    # Rejection cases required by Batch 2.
    bad_missing_symbol = _base_intent()
    bad_missing_symbol.pop("option_symbol")
    cases.append(_expect_reject("missing_option_symbol_rejected", lambda: M.StrategyOrderIntent.from_mapping(bad_missing_symbol)))

    bad_missing_token = _base_intent()
    bad_missing_token.pop("option_token")
    cases.append(_expect_reject("missing_option_token_rejected", lambda: M.StrategyOrderIntent.from_mapping(bad_missing_token)))

    cases.append(_expect_reject("qty_zero_rejected", lambda: M.StrategyOrderIntent.from_mapping(_base_intent(quantity_lots=0))))
    cases.append(_expect_reject("action_side_mismatch_rejected", lambda: M.StrategyOrderIntent.from_mapping(_base_intent(action=names.ACTION_ENTER_CALL, side=names.SIDE_PUT))))
    cases.append(_expect_reject("branch_side_mismatch_rejected", lambda: M.StrategyOrderIntent.from_mapping(_base_intent(branch_id=names.BRANCH_PUT))))
    cases.append(
        _expect_reject(
            "miso_invalid_runtime_rejected",
            lambda: M.StrategyOrderIntent.from_mapping(
                _base_intent(
                    strategy_family_id=names.STRATEGY_FAMILY_MISO,
                    doctrine_id=names.STRATEGY_FAMILY_MISO,
                    strategy_runtime_mode=names.STRATEGY_RUNTIME_MODE_NORMAL,
                )
            ),
        )
    )
    cases.append(
        _expect_reject(
            "non_miso_invalid_runtime_rejected",
            lambda: M.StrategyOrderIntent.from_mapping(
                _base_intent(
                    strategy_family_id=names.STRATEGY_FAMILY_MIST,
                    doctrine_id=names.STRATEGY_FAMILY_MIST,
                    strategy_runtime_mode=names.STRATEGY_RUNTIME_MODE_DEPTH20_ENHANCED,
                )
            ),
        )
    )
    cases.append(
        _expect_reject(
            "provider_transition_blocked_without_reason_rejected",
            lambda: M.ProviderTransitionEvent.from_mapping(
                {
                    "ts_event_ns": 1,
                    "role": names.PROVIDER_ROLE_EXECUTION_PRIMARY,
                    "to_provider_id": names.PROVIDER_DHAN,
                    "reason": names.PROVIDER_TRANSITION_REASON_FAILOVER_ACTIVATED,
                    "switch_allowed": False,
                }
            ),
        )
    )
    cases.append(
        _expect_reject(
            "effective_runtime_invalid_mode_rejected",
            lambda: M.EffectiveRuntimeConfigState.from_mapping(
                {
                    "ts_event_ns": 1,
                    "runtime_mode": "LIVE_ORDERS_UNKNOWN",
                    "trading_enabled": False,
                    "allow_live_orders": False,
                    "provider_runtime_enabled": True,
                    "bootstrap_groups_on_start": False,
                    "source_of_truth": "proof",
                }
            ),
        )
    )
    cases.append(
        _expect_reject(
            "schema_unknown_field_rejected",
            lambda: M.StrategyOrderIntent.from_mapping({**_base_intent(), "unknown_field": 1}),
        )
    )

    failed_cases = [case for case in cases if case.get("status") != "PASS"]
    proof = {
        "proof": "models_batch2_freeze",
        "status": "FAIL" if missing_exports or missing_registry or failed_cases else "PASS",
        "missing_exports": missing_exports,
        "missing_registry": missing_registry,
        "case_count": len(cases),
        "failed_cases": failed_cases,
        "cases": cases,
        "model_registry_size": len(M.MODEL_REGISTRY),
    }
    return proof


def main() -> int:
    proof = _prove()
    out = PROJECT_ROOT / "run" / "proofs" / "models_batch2_freeze.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 1 if proof["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
