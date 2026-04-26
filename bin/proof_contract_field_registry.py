#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from dataclasses import MISSING, fields
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import models as M
from app.mme_scalpx.services.feature_family import contracts as C


EXPECTED_PROVIDER_RUNTIME_KEYS = (
    "futures_marketdata_provider_id",
    "selected_option_marketdata_provider_id",
    "option_context_provider_id",
    "execution_primary_provider_id",
    "execution_fallback_provider_id",
    "futures_marketdata_status",
    "selected_option_marketdata_status",
    "option_context_status",
    "execution_primary_status",
    "execution_fallback_status",
    "family_runtime_mode",
    "failover_mode",
    "override_mode",
    "transition_reason",
    "provider_transition_seq",
    "failover_active",
    "pending_failover",
)

EXPECTED_SNAPSHOT_KEYS = (
    "future_json",
    "selected_call_json",
    "selected_put_json",
    "ce_atm_json",
    "ce_atm1_json",
    "pe_atm_json",
    "pe_atm1_json",
    "bid_qty_5",
    "ask_qty_5",
    "provider_id",
    "context_status",
    "selected_call_instrument_key",
    "selected_put_instrument_key",
)

EXPECTED_DHAN_CONTEXT_KEYS = (
    "option_chain_ladder_json",
    "strike_ladder_json",
    "oi_wall_summary_json",
    "selected_call_context_json",
    "selected_put_context_json",
    "nearest_call_oi_resistance_strike",
    "nearest_put_oi_support_strike",
    "call_wall_strength_score",
    "put_wall_strength_score",
    "oi_bias",
)

EXPECTED_FAMILY_SUPPORT_KEYS = {
    N.STRATEGY_FAMILY_MIST: (
        "trend_confirmed",
        "futures_impulse_ok",
        "pullback_detected",
        "resume_confirmed",
        "context_pass",
        "option_tradability_pass",
    ),
    N.STRATEGY_FAMILY_MISB: (
        "shelf_confirmed",
        "breakout_triggered",
        "breakout_accepted",
        "context_pass",
        "option_tradability_pass",
    ),
    N.STRATEGY_FAMILY_MISC: (
        "compression_detected",
        "directional_breakout_triggered",
        "expansion_accepted",
        "retest_monitor_active",
        "retest_valid",
        "hesitation_valid",
        "resume_confirmed",
        "context_pass",
        "option_tradability_pass",
    ),
    N.STRATEGY_FAMILY_MISR: (
        "active_zone_valid",
        "fake_break_triggered",
        "absorption_pass",
        "range_reentry_confirmed",
        "flow_flip_confirmed",
        "hold_inside_range_proved",
        "no_mans_land_cleared",
        "reversal_impulse_confirmed",
        "context_pass",
        "option_tradability_pass",
    ),
    N.STRATEGY_FAMILY_MISO: (
        "burst_detected",
        "aggression_ok",
        "tape_speed_ok",
        "imbalance_persist_ok",
        "queue_reload_blocked",
        "futures_vwap_align_ok",
        "futures_contradiction_blocked",
        "tradability_pass",
    ),
}

EXPECTED_EXECUTION_ENTRY_TOP_LEVEL_KEYS = (
    "action",
    "side",
    "position_effect",
    "quantity_lots",
    "instrument_key",
    "entry_mode",
)

EXPECTED_EXECUTION_ENTRY_METADATA_KEYS = (
    "option_symbol",
    "option_token",
    "strike",
    "limit_price",
    "provider_id",
    "execution_provider_id",
    "strategy_family",
    "strategy_branch",
    "doctrine_id",
    "candidate_id",
)

EXPECTED_EXECUTION_ENTRY_KEYS = (
    *EXPECTED_EXECUTION_ENTRY_TOP_LEVEL_KEYS,
    *(f"metadata.{key}" for key in EXPECTED_EXECUTION_ENTRY_METADATA_KEYS),
)


def _ok_tuple(actual: tuple[str, ...], expected: tuple[str, ...]) -> bool:
    return tuple(actual) == tuple(expected)


def _no_dupes(values: tuple[str, ...]) -> bool:
    return len(values) == len(set(values))


def _field_names(cls: type[Any]) -> tuple[str, ...]:
    return tuple(field.name for field in fields(cls))


def _surface_dupe_report(registry: Mapping[str, Any]) -> dict[str, bool]:
    report: dict[str, bool] = {}
    for surface, values in registry.items():
        if isinstance(values, Mapping):
            for family_id, family_values in values.items():
                report[f"{surface}.{family_id}"] = _no_dupes(tuple(family_values))
        else:
            report[surface] = _no_dupes(tuple(values))
    return report


def _alias_covered(canonical_key: str, model_fields: tuple[str, ...], alias_map: Mapping[str, str]) -> bool:
    if canonical_key in model_fields:
        return True
    return any(alias in model_fields and target == canonical_key for alias, target in alias_map.items())


def _required_init_fields(cls: type[Any]) -> tuple[str, ...]:
    required: list[str] = []
    for field in fields(cls):
        if not field.init:
            continue
        if field.default is MISSING and field.default_factory is MISSING:  # type: ignore[attr-defined]
            required.append(field.name)
    return tuple(required)


def _constant(name: str) -> Any:
    if not hasattr(N, name):
        raise RuntimeError(f"Missing required names constant: {name}")
    return getattr(N, name)


def _build_strategy_order_intent(generated_at_ns: int) -> Any:
    base_values: dict[str, Any] = {
        "decision_id": "proof-decision-25g",
        "candidate_id": "proof-candidate-25g",
        "ts_event_ns": generated_at_ns,
        "action": _constant("ACTION_ENTER_CALL"),
        "side": _constant("SIDE_CALL"),
        "position_effect": _constant("POSITION_EFFECT_OPEN"),
        "quantity_lots": 1,
        "instrument_key": _constant("IK_MME_CE"),
        "strategy_family_id": _constant("STRATEGY_FAMILY_MIST"),
        "doctrine_id": _constant("DOCTRINE_MIST"),
        "branch_id": _constant("BRANCH_CALL"),
        "family_runtime_mode": _constant("FAMILY_RUNTIME_MODE_OBSERVE_ONLY"),
        "option_symbol": "NIFTY_PROOF_CE",
        "option_token": "123456",
        "strike": 25000.0,
        "limit_price": 100.0,
        "entry_mode": _constant("ENTRY_MODE_ATM"),
        "system_state": _constant("STATE_IDLE"),
        "reason_code": "BATCH25G_PROOF",
        "strategy_runtime_mode": _constant("STRATEGY_RUNTIME_MODE_NORMAL"),
        "active_futures_provider_id": _constant("PROVIDER_ZERODHA"),
        "active_selected_option_provider_id": _constant("PROVIDER_DHAN"),
        "active_option_context_provider_id": _constant("PROVIDER_DHAN"),
        "execution_primary_provider_id": _constant("PROVIDER_ZERODHA"),
        "execution_fallback_provider_id": _constant("PROVIDER_DHAN"),
        "confidence": 1.0,
    }

    accepted = {field.name for field in fields(M.StrategyOrderIntent) if field.init}
    required = _required_init_fields(M.StrategyOrderIntent)

    missing = [name for name in required if name not in base_values]
    if missing:
        raise RuntimeError(f"Proof constructor missing explicit values for required fields: {missing!r}")

    kwargs = {name: value for name, value in base_values.items() if name in accepted}
    return M.StrategyOrderIntent(**kwargs)


def main() -> int:
    generated_at_ns = time.time_ns()
    errors: list[str] = []
    checks: dict[str, bool] = {}

    try:
        N.validate_names_contract()
        C.validate_contract_field_registry()
        C.validate_family_features_payload(C.build_empty_family_features_payload())
        checks["imports_and_self_validation_ok"] = True
    except Exception as exc:
        checks["imports_and_self_validation_ok"] = False
        errors.append(f"self_validation_failed: {exc}")

    registry = N.get_contract_field_registry()
    alias_map = N.get_contract_field_compatibility_aliases()
    dupe_report = _surface_dupe_report(registry)

    checks["provider_runtime_keys_complete"] = _ok_tuple(
        N.CONTRACT_PROVIDER_RUNTIME_KEYS, EXPECTED_PROVIDER_RUNTIME_KEYS
    ) and _ok_tuple(C.CANONICAL_PROVIDER_RUNTIME_KEYS, EXPECTED_PROVIDER_RUNTIME_KEYS)

    checks["snapshot_keys_complete"] = _ok_tuple(
        N.CONTRACT_FEED_SNAPSHOT_KEYS, EXPECTED_SNAPSHOT_KEYS
    ) and _ok_tuple(C.CANONICAL_FEED_SNAPSHOT_KEYS, EXPECTED_SNAPSHOT_KEYS)

    checks["dhan_context_keys_complete"] = _ok_tuple(
        N.CONTRACT_DHAN_CONTEXT_KEYS, EXPECTED_DHAN_CONTEXT_KEYS
    ) and _ok_tuple(C.CANONICAL_DHAN_CONTEXT_KEYS, EXPECTED_DHAN_CONTEXT_KEYS)

    checks["family_support_keys_complete"] = (
        dict(N.CONTRACT_FAMILY_SUPPORT_KEYS) == EXPECTED_FAMILY_SUPPORT_KEYS
        and dict(C.CANONICAL_FAMILY_SUPPORT_KEYS) == EXPECTED_FAMILY_SUPPORT_KEYS
    )

    checks["execution_entry_keys_complete"] = (
        _ok_tuple(N.CONTRACT_EXECUTION_ENTRY_TOP_LEVEL_KEYS, EXPECTED_EXECUTION_ENTRY_TOP_LEVEL_KEYS)
        and _ok_tuple(N.CONTRACT_EXECUTION_ENTRY_METADATA_KEYS, EXPECTED_EXECUTION_ENTRY_METADATA_KEYS)
        and _ok_tuple(N.CONTRACT_EXECUTION_ENTRY_KEYS, EXPECTED_EXECUTION_ENTRY_KEYS)
        and _ok_tuple(C.CANONICAL_EXECUTION_ENTRY_KEYS, EXPECTED_EXECUTION_ENTRY_KEYS)
    )

    checks["no_duplicate_contract_keys"] = all(dupe_report.values())

    provider_runtime_fields = _field_names(M.ProviderRuntimeState)
    dhan_event_fields = _field_names(M.DhanContextEvent)
    dhan_state_fields = _field_names(M.DhanContextState)
    order_intent_fields = _field_names(M.StrategyOrderIntent)

    provider_runtime_canonical_ready = all(
        key in provider_runtime_fields for key in EXPECTED_PROVIDER_RUNTIME_KEYS
    )
    provider_runtime_contract_covered = all(
        _alias_covered(key, provider_runtime_fields, alias_map)
        for key in EXPECTED_PROVIDER_RUNTIME_KEYS
    )

    checks["provider_runtime_model_fields_contract_covered"] = provider_runtime_contract_covered

    checks["dhan_context_model_fields_complete"] = all(
        key in dhan_event_fields and key in dhan_state_fields for key in EXPECTED_DHAN_CONTEXT_KEYS
    )

    checks["strategy_order_intent_model_fields_complete"] = all(
        key in order_intent_fields
        for key in (
            "action",
            "side",
            "position_effect",
            "quantity_lots",
            "instrument_key",
            "entry_mode",
            "option_symbol",
            "option_token",
            "strike",
            "limit_price",
            "candidate_id",
            "execution_primary_provider_id",
        )
    )

    try:
        intent = _build_strategy_order_intent(generated_at_ns)
        payload = intent.to_strategy_decision_payload()
        metadata = payload.get("metadata", {})

        checks["strategy_order_intent_payload_contains_execution_keys"] = all(
            key in payload for key in EXPECTED_EXECUTION_ENTRY_TOP_LEVEL_KEYS
        ) and all(key in metadata for key in EXPECTED_EXECUTION_ENTRY_METADATA_KEYS)

    except Exception as exc:
        checks["strategy_order_intent_payload_contains_execution_keys"] = False
        errors.append(f"strategy_order_intent_payload_failed: {exc}")

    gating_check_names = (
        "imports_and_self_validation_ok",
        "provider_runtime_keys_complete",
        "snapshot_keys_complete",
        "dhan_context_keys_complete",
        "family_support_keys_complete",
        "execution_entry_keys_complete",
        "no_duplicate_contract_keys",
        "provider_runtime_model_fields_contract_covered",
        "dhan_context_model_fields_complete",
        "strategy_order_intent_model_fields_complete",
        "strategy_order_intent_payload_contains_execution_keys",
    )

    contract_field_registry_ok = all(checks.get(name) for name in gating_check_names) and not errors

    proof = {
        "proof_name": "proof_contract_field_registry",
        "batch": "25G-C",
        "generated_at_ns": generated_at_ns,
        "contract_field_registry_ok": contract_field_registry_ok,
        "provider_runtime_keys_complete": checks["provider_runtime_keys_complete"],
        "snapshot_keys_complete": checks["snapshot_keys_complete"],
        "dhan_context_keys_complete": checks["dhan_context_keys_complete"],
        "family_support_keys_complete": checks["family_support_keys_complete"],
        "execution_entry_keys_complete": checks["execution_entry_keys_complete"],
        "no_duplicate_contract_keys": checks["no_duplicate_contract_keys"],
        "provider_runtime_model_fields_contract_covered": provider_runtime_contract_covered,
        "provider_runtime_model_canonical_fields_ready": provider_runtime_canonical_ready,
        "provider_runtime_model_canonical_fields_ready_note": (
            "false is allowed in 25G-C only when explicit compatibility aliases cover the contract; "
            "canonical producer/consumer repair remains Batch 25H."
        ),
        "gating_check_names": gating_check_names,
        "checks": checks,
        "duplicate_report": dupe_report,
        "expected": {
            "provider_runtime_keys": EXPECTED_PROVIDER_RUNTIME_KEYS,
            "snapshot_keys": EXPECTED_SNAPSHOT_KEYS,
            "dhan_context_keys": EXPECTED_DHAN_CONTEXT_KEYS,
            "family_support_keys": EXPECTED_FAMILY_SUPPORT_KEYS,
            "execution_entry_top_level_keys": EXPECTED_EXECUTION_ENTRY_TOP_LEVEL_KEYS,
            "execution_entry_metadata_keys": EXPECTED_EXECUTION_ENTRY_METADATA_KEYS,
            "execution_entry_keys": EXPECTED_EXECUTION_ENTRY_KEYS,
        },
        "actual": {
            "names_contract_field_registry": registry,
            "field_compatibility_aliases": alias_map,
            "feature_family_canonical_registry": {
                "provider_runtime": C.CANONICAL_PROVIDER_RUNTIME_KEYS,
                "feed_snapshot": C.CANONICAL_FEED_SNAPSHOT_KEYS,
                "dhan_context": C.CANONICAL_DHAN_CONTEXT_KEYS,
                "family_support": dict(C.CANONICAL_FAMILY_SUPPORT_KEYS),
                "execution_entry": C.CANONICAL_EXECUTION_ENTRY_KEYS,
            },
            "model_field_coverage": {
                "ProviderRuntimeState": provider_runtime_fields,
                "DhanContextEvent": dhan_event_fields,
                "DhanContextState": dhan_state_fields,
                "StrategyOrderIntent": order_intent_fields,
            },
        },
        "errors": errors,
    }

    out = Path("run/proofs/proof_contract_field_registry.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "contract_field_registry_ok": proof["contract_field_registry_ok"],
        "provider_runtime_keys_complete": checks["provider_runtime_keys_complete"],
        "snapshot_keys_complete": checks["snapshot_keys_complete"],
        "dhan_context_keys_complete": checks["dhan_context_keys_complete"],
        "family_support_keys_complete": checks["family_support_keys_complete"],
        "execution_entry_keys_complete": checks["execution_entry_keys_complete"],
        "no_duplicate_contract_keys": checks["no_duplicate_contract_keys"],
        "provider_runtime_model_fields_contract_covered": provider_runtime_contract_covered,
        "provider_runtime_model_canonical_fields_ready": provider_runtime_canonical_ready,
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof["contract_field_registry_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
