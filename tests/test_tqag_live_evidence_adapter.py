from app.mme_scalpx.services.tqag_live_evidence_adapter import (
    derive_tqag_live_evidence,
)


def test_depth_and_symbol_fields_can_pass_when_complete():
    now_ns = 1_000_000_000_000

    selected = {
        "trading_symbol": "NIFTY2672124300CE",
        "instrument_token": "12345",
        "bids": '[{"price":137.0,"quantity":910}]',
        "asks": '[{"price":137.4,"quantity":2665}]',
        "ts_event_ns": str(now_ns - 1_000_000_000),
    }

    candidate = {
        "symbol": "NIFTY2672124300CE",
        "underlying_option_aligned": 1,
        "no_chase": 1,
        "expected_move_points": 5,
        "conservative_breakeven_points": 1,
        "timeframe_complete": 1,
    }

    provider = {"provider_ready_classic": 1}

    evidence = derive_tqag_live_evidence(
        selected_option=selected,
        candidate=candidate,
        provider_runtime=provider,
        now_ns=now_ns,
    )

    assert evidence.quote_fresh is True
    assert evidence.bid_qty_valid is True
    assert evidence.ask_qty_valid is True
    assert evidence.spread_acceptable is True
    assert evidence.instrument_lock_valid is True
    assert evidence.option_symbol_stable is True
    assert evidence.underlying_option_aligned is True
    assert evidence.no_chase is True
    assert evidence.edge_after_cost_positive is True
    assert evidence.timeframe_complete is True
    assert evidence.data_gap_present is False


def test_missing_alignment_no_chase_edge_and_timeframe_stay_blocked():
    now_ns = 1_000_000_000_000

    selected = {
        "trading_symbol": "NIFTY2672124300CE",
        "instrument_token": "12345",
        "bid_qty": "910",
        "ask_qty": "2665",
        "best_bid": "137.0",
        "best_ask": "137.4",
        "ts_event_ns": str(now_ns - 1_000_000_000),
    }

    candidate = {"symbol": "NIFTY2672124300CE"}
    provider = {"provider_ready_classic": 1}

    evidence = derive_tqag_live_evidence(
        selected_option=selected,
        candidate=candidate,
        provider_runtime=provider,
        now_ns=now_ns,
    )

    assert evidence.bid_qty_valid is True
    assert evidence.ask_qty_valid is True
    assert evidence.spread_acceptable is True
    assert evidence.instrument_lock_valid is True
    assert evidence.option_symbol_stable is True
    assert evidence.underlying_option_aligned is False
    assert evidence.no_chase is False
    assert evidence.edge_after_cost_positive is False
    assert evidence.timeframe_complete is False
    assert "UNDERLYING_OPTION_ALIGNED" in evidence.reasons
    assert "NO_CHASE" in evidence.reasons
    assert "EDGE_AFTER_COST_POSITIVE" in evidence.reasons
    assert "TIMEFRAME_COMPLETE" in evidence.reasons


def test_stale_quote_blocks_data_gap():
    now_ns = 1_000_000_000_000

    evidence = derive_tqag_live_evidence(
        selected_option={
            "trading_symbol": "NIFTY2672124300CE",
            "instrument_token": "12345",
            "bid_qty": "10",
            "ask_qty": "10",
            "best_bid": "100",
            "best_ask": "100.5",
            "ts_event_ns": str(now_ns - 10_000_000_000),
        },
        candidate={"symbol": "NIFTY2672124300CE"},
        provider_runtime={"provider_ready_classic": 1},
        now_ns=now_ns,
    )

    assert evidence.quote_fresh is False
    assert evidence.data_gap_present is True
    assert "QUOTE_FRESH" in evidence.reasons
