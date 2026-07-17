from app.mme_scalpx.services.trade_quality_authorization_gate import (
    TQAGCosts,
    TQAGDecision,
    evaluate_trade_quality_authorization,
)


BASE_PASS = {
    "QUOTE_FRESH": 1,
    "BID_QTY_VALID": 1,
    "ASK_QTY_VALID": 1,
    "SPREAD_ACCEPTABLE": 1,
    "OPTION_SYMBOL_STABLE": 1,
    "INSTRUMENT_LOCK_VALID": 1,
    "UNDERLYING_OPTION_ALIGNED": 1,
    "NO_CHASE": 1,
    "EDGE_AFTER_COST_POSITIVE": 1,
    "BROKER_FLAT": 1,
    "ACTIVE_BROKER_ORDERS_ZERO": 1,
    "RISK_GATE_OPEN": 1,
    "TIMEFRAME_COMPLETE": 1,
    "DATA_GAP_PRESENT": 0,
    "PENDING_ORDER_PRESENT": 0,
    "ENTRY_CUTOFF_PASSED": 0,
    "regime_15m": 15,
    "setup_5m": 15,
    "trigger_3m": 15,
    "option_microstructure": 15,
    "liquidity_execution": 15,
    "instrument_lock_state": "MICRO_OBSERVATION_COMPLETE",
}


def test_authorizes_only_when_no_veto_and_score_passes():
    result = evaluate_trade_quality_authorization(
        BASE_PASS,
        conservative_costs=TQAGCosts(expected_gross_move=10, minimum_required_net_edge=1),
    )
    assert result.decision == TQAGDecision.AUTHORIZE
    record = result.to_record()
    assert record["can_create_order"] is False
    assert record["can_route_order"] is False
    assert record["can_send_broker_order"] is False


def test_any_hard_veto_blocks_score_override():
    raw = dict(BASE_PASS)
    raw["QUOTE_FRESH"] = 0
    raw["regime_15m"] = 20
    raw["setup_5m"] = 20
    raw["trigger_3m"] = 20
    raw["option_microstructure"] = 20
    raw["liquidity_execution"] = 20
    result = evaluate_trade_quality_authorization(
        raw,
        conservative_costs=TQAGCosts(expected_gross_move=100, minimum_required_net_edge=1),
    )
    assert result.decision == TQAGDecision.VETO
    assert "QUOTE_FRESH" in result.hard_vetoes


def test_negative_veto_blocks_authorization():
    raw = dict(BASE_PASS)
    raw["PENDING_ORDER_PRESENT"] = 1
    result = evaluate_trade_quality_authorization(
        raw,
        conservative_costs=TQAGCosts(expected_gross_move=10, minimum_required_net_edge=1),
    )
    assert result.decision == TQAGDecision.VETO
    assert "PENDING_ORDER_PRESENT" in result.hard_vetoes


def test_low_component_holds_even_if_total_high_enough():
    raw = dict(BASE_PASS)
    raw["trigger_3m"] = 5
    raw["regime_15m"] = 20
    raw["setup_5m"] = 20
    raw["option_microstructure"] = 20
    raw["liquidity_execution"] = 20
    result = evaluate_trade_quality_authorization(
        raw,
        conservative_costs=TQAGCosts(expected_gross_move=10, minimum_required_net_edge=1),
    )
    assert result.total_score >= 75
    assert result.decision == TQAGDecision.HOLD


def test_symbol_change_resets_observation():
    raw = dict(BASE_PASS)
    raw["symbol_changed"] = 1
    result = evaluate_trade_quality_authorization(
        raw,
        conservative_costs=TQAGCosts(expected_gross_move=10, minimum_required_net_edge=1),
    )
    assert result.decision == TQAGDecision.RESET_OBSERVATION
    assert "SYMBOL_CHANGED" in result.reset_reasons


def test_edge_after_cost_vetoes_when_net_edge_not_enough():
    raw = dict(BASE_PASS)
    result = evaluate_trade_quality_authorization(
        raw,
        conservative_costs=TQAGCosts(
            expected_gross_move=3,
            entry_half_spread_or_full_crossing_cost=1,
            expected_exit_spread=1,
            estimated_slippage=1,
            brokerage=0.5,
            taxes_and_exchange_charges=0.5,
            minimum_required_net_edge=1,
        ),
    )
    assert result.decision == TQAGDecision.VETO
    assert "EDGE_AFTER_COST_POSITIVE" in result.hard_vetoes
