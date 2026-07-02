from __future__ import annotations

from typing import Any, Mapping


MIV_CONTRACT_VERSION = "miv_research_contract_v0_1_r1a_strategy_family_dormant"

MIV_FAMILY_ID = "MIV_R"
MIV_DISPLAY_NAME = "Market Imbalance Volume Research Family"

MIV_IS_STRATEGY_FAMILY_SOURCE_MODULE = True
MIV_IS_ACTIVE_PRODUCTION_FAMILY = False
MIV_IS_DORMANT_RESEARCH_FAMILY = True
MIV_RESEARCH_SHADOW_ONLY = True

MIV_MODE_ZERODHA_LITE = "MIV_ZERODHA_LITE"
MIV_MODE_DHAN_FULL = "MIV_DHAN_FULL"
MIV_RESEARCH_MODES = (MIV_MODE_ZERODHA_LITE, MIV_MODE_DHAN_FULL)

MIV_CALL_PRESSURE_BURST = "CALL_PRESSURE_BURST"
MIV_PUT_PRESSURE_BURST = "PUT_PRESSURE_BURST"
MIV_NEUTRAL_ACTIVE_LABEL = "NEUTRAL_ACTIVE_LABEL"

MIV_CANDIDATE_TYPES = (
    MIV_CALL_PRESSURE_BURST,
    MIV_PUT_PRESSURE_BURST,
    MIV_NEUTRAL_ACTIVE_LABEL,
)

MIV_TRADE_SHADOW_CANDIDATE_TYPES = (
    MIV_CALL_PRESSURE_BURST,
    MIV_PUT_PRESSURE_BURST,
)

MIV_OUTPUT_ARTIFACTS = (
    "miv_research_candidates.json",
    "miv_candidate_audit.csv",
    "miv_factor_surface.csv",
    "miv_blocker_surface.csv",
    "miv_shadow_decisions.json",
    "miv_shadow_pnl.csv",
)

MIV_REQUIRED_CANDIDATE_FIELDS = (
    "schema_version",
    "contract_version",
    "run_id",
    "dataset_id",
    "family_id",
    "research_mode",
    "candidate_type",
    "miv_candidate_id",
    "event_ts",
    "event_ns",
    "window_start_ns",
    "window_end_ns",

    # Internal order-intent / R32D bridge compatibility.
    "symbol",
    "option_symbol",
    "side",
    "action",
    "qty",
    "price",
    "score",

    # Research routing.
    "research_shadow_only",
    "label_only",
    "trade_shadow_eligible",
    "route_to_candidate_audit",
    "route_to_risk_shadow",
    "route_to_execution_shadow",
    "route_to_order_intent_ledger",

    # Safety flags.
    "order_allowed",
    "broker_send_enabled",
    "real_order_sent",
    "broker_calls_executed",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",

    # Provider/data status.
    "dhan_context_status",
    "dhan_full_enabled",
    "hard_blocked",
    "hard_block_reasons",
    "soft_block_reasons",
    "tradability_ok",
    "freshness_ok",
)

MIV_SCORE_MIN_RESEARCH = 5.0
MIV_SCORE_MIN_STRONG = 7.0

_DHAN_HEALTHY_VALUES = {"HEALTHY", "OK", "READY", "FRESH", "AVAILABLE", "TRUE", "1"}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _str(value: Any) -> str:
    return "" if value is None else str(value)


def validate_miv_candidate_row(row: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(k for k in MIV_REQUIRED_CANDIDATE_FIELDS if k not in row)
    hard_errors: list[str] = []

    family_id = _str(row.get("family_id"))
    mode = _str(row.get("research_mode"))
    candidate_type = _str(row.get("candidate_type"))
    side = _str(row.get("side")).upper()
    action = _str(row.get("action")).upper()
    symbol = _str(row.get("symbol") or row.get("option_symbol"))
    score = _float(row.get("score"), 0.0)

    if family_id != MIV_FAMILY_ID:
        hard_errors.append("family_id_must_be_MIV_R")

    if mode not in MIV_RESEARCH_MODES:
        hard_errors.append("invalid_research_mode")

    if candidate_type not in MIV_CANDIDATE_TYPES:
        hard_errors.append("invalid_candidate_type")

    if row.get("research_shadow_only") is not True:
        hard_errors.append("research_shadow_only_must_be_true")

    if row.get("order_allowed") is not False:
        hard_errors.append("order_allowed_must_be_false")

    if row.get("broker_send_enabled") is not False:
        hard_errors.append("broker_send_enabled_must_be_false")

    if row.get("real_order_sent") is not False:
        hard_errors.append("real_order_sent_must_be_false")

    if row.get("broker_calls_executed") is not False:
        hard_errors.append("broker_calls_executed_must_be_false")

    if row.get("paper_armed_approved") is not False:
        hard_errors.append("paper_armed_approved_must_be_false")

    if row.get("live_trading_approved") is not False:
        hard_errors.append("live_trading_approved_must_be_false")

    if row.get("production_doctrine_changed") is not False:
        hard_errors.append("production_doctrine_changed_must_be_false")

    if mode == MIV_MODE_DHAN_FULL:
        status = _str(row.get("dhan_context_status")).upper()
        if status not in _DHAN_HEALTHY_VALUES or row.get("dhan_full_enabled") is not True:
            hard_errors.append("miv_dhan_full_requires_healthy_dhan_context")

    if candidate_type == MIV_NEUTRAL_ACTIVE_LABEL:
        if row.get("label_only") is not True:
            hard_errors.append("neutral_label_must_be_label_only")
        if row.get("trade_shadow_eligible") is not False:
            hard_errors.append("neutral_label_trade_shadow_must_be_false")
        if row.get("route_to_risk_shadow") is not False:
            hard_errors.append("neutral_label_risk_route_must_be_false")
        if row.get("route_to_execution_shadow") is not False:
            hard_errors.append("neutral_label_execution_route_must_be_false")
        if row.get("route_to_order_intent_ledger") is not False:
            hard_errors.append("neutral_label_order_intent_route_must_be_false")
    else:
        if side not in {"CALL", "PUT", "CE", "PE"}:
            hard_errors.append("trade_candidate_side_missing_or_invalid")
        if action not in {"ENTRY", "ENTER", "BUY", "LONG", "ENTER_CALL", "ENTER_PUT"}:
            hard_errors.append("trade_candidate_action_not_entry_compatible")
        if not symbol:
            hard_errors.append("trade_candidate_symbol_missing")
        if score < MIV_SCORE_MIN_RESEARCH:
            hard_errors.append("trade_candidate_score_below_research_min")
        if row.get("label_only") is not False:
            hard_errors.append("trade_candidate_label_only_must_be_false")
        if row.get("trade_shadow_eligible") is not True:
            hard_errors.append("trade_candidate_shadow_eligible_must_be_true")

    ok = bool(not missing and not hard_errors)
    return {
        "ok": ok,
        "contract_version": MIV_CONTRACT_VERSION,
        "missing": missing,
        "hard_errors": tuple(hard_errors),
        "family_id": family_id,
        "research_mode": mode,
        "candidate_type": candidate_type,
        "score": score,
    }


def contract_summary() -> dict[str, Any]:
    return {
        "contract_version": MIV_CONTRACT_VERSION,
        "family_id": MIV_FAMILY_ID,
        "display_name": MIV_DISPLAY_NAME,
        "strategy_family_source_module": MIV_IS_STRATEGY_FAMILY_SOURCE_MODULE,
        "active_production_family": MIV_IS_ACTIVE_PRODUCTION_FAMILY,
        "dormant_research_family": MIV_IS_DORMANT_RESEARCH_FAMILY,
        "research_shadow_only": MIV_RESEARCH_SHADOW_ONLY,
        "research_modes": MIV_RESEARCH_MODES,
        "candidate_types": MIV_CANDIDATE_TYPES,
        "trade_shadow_candidate_types": MIV_TRADE_SHADOW_CANDIDATE_TYPES,
        "output_artifacts": MIV_OUTPUT_ARTIFACTS,
        "required_candidate_fields": MIV_REQUIRED_CANDIDATE_FIELDS,
        "score_min_research": MIV_SCORE_MIN_RESEARCH,
        "score_min_strong": MIV_SCORE_MIN_STRONG,
        "production_family_registry_allowed": False,
        "replay_mis_family_adapter_allowed": False,
        "broker_send_allowed": False,
        "paper_live_allowed": False,
    }


__all__ = (
    "MIV_CONTRACT_VERSION",
    "MIV_FAMILY_ID",
    "MIV_RESEARCH_MODES",
    "MIV_CANDIDATE_TYPES",
    "MIV_OUTPUT_ARTIFACTS",
    "MIV_REQUIRED_CANDIDATE_FIELDS",
    "validate_miv_candidate_row",
    "contract_summary",
)
