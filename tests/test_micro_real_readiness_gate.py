from app.mme_scalpx.services.micro_real_readiness_gate import (
    CostBreakdown,
    MicroRealDecision,
    MicroRealReadinessInputs,
    evaluate_micro_real_readiness,
)


def base_inputs(**overrides):
    data = dict(
        fresh_monday_preflight=True,
        market_session_open=True,
        daily_stop_not_fired=True,
        broker_session_healthy=True,
        broker_flat=True,
        active_broker_orders_zero=True,
        sufficient_margin=True,
        provider_ready_classic=True,
        safe_to_consume=True,
        quote_fresh=True,
        tqag_decision="AUTHORIZE",
        tqag_hard_veto_count=0,
        bid_qty_valid=True,
        ask_qty_valid=True,
        spread_acceptable=True,
        instrument_lock_valid=True,
        option_symbol_stable=True,
        underlying_option_aligned=True,
        no_chase=True,
        edge_after_cost_positive=True,
        timeframe_complete=True,
        data_gap_present=False,
        pending_order_present=False,
        entry_cutoff_passed=False,
        charges_configured=True,
        conservative_breakeven_points=1.0,
        expected_move_points=3.0,
        order_type="MARKETABLE_LIMIT",
        max_order_attempts=1,
        retry_count=0,
        replacement_count=0,
        averaging_allowed=False,
        max_lots=1,
        max_positions=1,
        max_events=1,
        explicit_user_authorization=True,
    )
    data.update(overrides)
    return MicroRealReadinessInputs(**data)


def test_clean_synthetic_case_reaches_manual_authorization_only():
    result = evaluate_micro_real_readiness(base_inputs())
    record = result.to_record()
    assert result.decision == MicroRealDecision.READY_FOR_MANUAL_AUTHORIZATION
    assert record["can_create_order"] is False
    assert record["can_route_order"] is False
    assert record["can_send_broker_order"] is False


def test_missing_quality_fields_block():
    result = evaluate_micro_real_readiness(
        base_inputs(
            bid_qty_valid=False,
            ask_qty_valid=False,
            spread_acceptable=False,
            underlying_option_aligned=False,
            no_chase=False,
            edge_after_cost_positive=False,
        )
    )
    assert result.decision == MicroRealDecision.BLOCK
    assert "BID_QTY_VALID" in result.blockers
    assert "EDGE_AFTER_COST_POSITIVE" in result.blockers


def test_daily_stop_blocks_real_event():
    result = evaluate_micro_real_readiness(base_inputs(daily_stop_not_fired=False))
    assert result.decision == MicroRealDecision.BLOCK
    assert "DAILY_STOP_NOT_FIRED" in result.blockers


def test_tqag_veto_blocks():
    result = evaluate_micro_real_readiness(
        base_inputs(tqag_decision="VETO", tqag_hard_veto_count=2)
    )
    assert result.decision == MicroRealDecision.BLOCK
    assert "TQAG_NOT_AUTHORIZE" in result.blockers
    assert "TQAG_HARD_VETO_PRESENT" in result.blockers


def test_first_real_policy_is_strict():
    result = evaluate_micro_real_readiness(
        base_inputs(
            order_type="MARKET",
            max_order_attempts=2,
            retry_count=1,
            replacement_count=1,
            averaging_allowed=True,
            max_lots=2,
            max_positions=2,
            max_events=2,
        )
    )
    assert result.decision == MicroRealDecision.BLOCK
    assert "ORDER_TYPE_NOT_MARKETABLE_LIMIT" in result.blockers
    assert "MAX_EVENTS_NOT_ONE" in result.blockers


def test_cost_breakdown_breakeven():
    costs = CostBreakdown(
        brokerage=20,
        stt_ctt=10,
        exchange_transaction=5,
        gst=5,
        sebi=1,
        stamp_duty=2,
        estimated_slippage=22,
    )
    assert costs.total_cost_rupees == 65
    assert costs.breakeven_points(65) == 1
