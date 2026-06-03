# B1-PROFIT-LIVE-R39WA_VOLATILE_MARKET_ZERO_CANDIDATE_ROOT_CAUSE_NO_PATCH_NO_START_NO_ORDER_audit_raw_market_move_vs_feature_regime_score_response_for_zero_candidate_in_volatile_market_20260603_133915

Classification: `BLOCKED_R39WA_MARKET_MOVE_NOT_REFLECTED_IN_SCORE_OR_REGIME_NO_PATCH`

## What this audit answers
Does raw live market movement reach the feature/regime/score surfaces, or are strategy scores flat/stale despite volatility?

## Counts
- fut_entries: 1200
- opt_entries: 2400
- feature_entries: 275
- decision_entries: 500
- candidate_positive: 0
- classic_runtime_disabled: 0

## Futures raw movement
```json
{
  "change": 27.400000000001455,
  "first": 23402.3,
  "last": 23429.7,
  "max": 23439.0,
  "mean": 23420.66258333337,
  "min": 23400.0,
  "n": 1200,
  "range": 39.0
}
```

## Option movement by role
```json
{
  "CE_ATM": {
    "change": 9.449999999999989,
    "first": 270.75,
    "last": 280.2,
    "max": 283.1,
    "mean": 272.9367720465891,
    "min": 261.1,
    "n": 601,
    "range": 22.0
  },
  "CE_ATM1": {
    "change": 8.050000000000011,
    "first": 240.95,
    "last": 249.0,
    "max": 252.25,
    "mean": 242.69081632653044,
    "min": 231.65,
    "n": 588,
    "range": 20.599999999999994
  },
  "PE_ATM": {
    "change": -5.700000000000017,
    "first": 134.8,
    "last": 129.1,
    "max": 140.45,
    "mean": 133.70575657894756,
    "min": 127.5,
    "n": 608,
    "range": 12.949999999999989
  },
  "PE_ATM1": {
    "change": -5.75,
    "first": 117.75,
    "last": 112.0,
    "max": 122.2,
    "mean": 116.29593698175789,
    "min": 110.65,
    "n": 603,
    "range": 11.549999999999997
  }
}
```

## Regime counts from decision metadata
- LOWVOL: 1516

## Leaf/no-signal reasons
- score_below_threshold: 1516
- directional_breakout_not_confirmed: 758
- reversal_direction_not_confirmed: 758
- stage_provider_ready_miso_failed: 758

## Best nearest miss
```json
{
  "branch_id": "CALL",
  "breakout_score": 0.004615384615384616,
  "bucket": "no_signal",
  "context_score": 0.62,
  "decision_id": "1780474160247-0",
  "family_id": "MISB",
  "futures_bias_ok": true,
  "futures_impulse_score": null,
  "gap": 0.2800615384615385,
  "min_score": 0.64,
  "option_confirmation_score": 0.5,
  "pullback_resume_score": null,
  "reason": "score_below_threshold",
  "regime": "LOWVOL",
  "score": 0.35993846153846154
}
```

## Score variation by family/branch
- MISB::CALL: n=379 min=0.35993846153846154 max=0.35993846153846154 range=0.0 first=0.35993846153846154 last=0.35993846153846154
- MISB::PUT: n=379 min=0.19493846153846156 max=0.19493846153846156 range=0.0 first=0.19493846153846156 last=0.19493846153846156
- MIST::CALL: n=379 min=0.2325 max=0.2325 range=0.0 first=0.2325 last=0.2325
- MIST::PUT: n=379 min=0.12 max=0.12 range=0.0 first=0.12 last=0.12

## Red flags
- raw_futures_moved_but_strategy_regime_still_LOWVOL
- nearest_candidate_far_from_threshold
- score_surface_constant_for_many_decisions:MIST::CALL,MIST::PUT,MISB::CALL,MISB::PUT
- breakout_score_near_zero_despite_claimed_volatility
- futures_impulse_score_missing_for_nearest_miss

## Current feature snapshot
```json
{
  "feature_state_frame_valid": true,
  "feature_state_regime": "LOWVOL",
  "selected_option": {
    "delta_3": null,
    "depth_ok": true,
    "depth_total": 195.0,
    "ltp": 246.6,
    "micro_edge": null,
    "microprice": null,
    "ofi_ratio_proxy": null,
    "response_efficiency": 0.0,
    "side": "CALL",
    "spread": 0.3499999999999943,
    "spread_ratio": 0.001419302514193002,
    "tradability_ok": true
  },
  "selected_option_rich": {
    "anomaly_clamped": false,
    "ask_qty_5": 130,
    "best_ask": 246.95,
    "best_bid": 246.6,
    "bid_qty_5": 65,
    "book_present": true,
    "delta_3": null,
    "depth_ok": true,
    "depth_total": 195,
    "expiry": "2026-06-09",
    "fresh": true,
    "instrument_key": "NFO:NIFTY2660923300CE",
    "instrument_token": "10825730",
    "ltp": 246.6,
    "micro_edge": null,
    "microprice": null,
    "mid": 246.77499999999998,
    "ofi_ratio_proxy": null,
    "option_side": "CALL",
    "option_symbol": "NIFTY2660923300CE",
    "option_token": "10825730",
    "present": true,
    "provider_id": "ZERODHA",
    "quote_present": true,
    "raw_source": {
      "_stream_id": "1780474166424-0",
      "_stream_key": "ticks:mme:opt:selected:zerodha:stream",
      "ask": "246.95",
      "ask_qty": "130",
      "asks": "[{\"price\":246.95,\"quantity\":130,\"orders\":2},{\"price\":247.05,\"quantity\":195,\"orders\":3},{\"price\":247.1,\"quantity\":1170,\"orders\":9},{\"price\":247.15,\"quantity\":195,\"orders\":3},{\"price\":247.2,\"quantity\":1300,\"orders\":9}]",
      "bid": "246.6",
      "bid_qty": "65",
      "bids": "[{\"price\":246.6,\"quantity\":65,\"orders\":1},{\"price\":246.45,\"quantity\":260,\"orders\":4},{\"price\":246.4,\"quantity\":260,\"orders\":3},{\"price\":246.35,\"quantity\":390,\"orders\":3},{\"price\":246.3,\"quantity\":975,\"orders\":6}]",
      "exchange": "NFO",
      "expiry": "2026-06-09",
      "instrument_key": "NFO:NIFTY2660923300CE",
      "instrument_role": "CE_ATM1",
      "instrument_token": "10825730",
      "is_selected_option": "False",
      "is_shadow_option": "False",
      "last_qty": "",
      "ltp": "246.6",
      "oi": "",
      "option_side": "CALL",
      "provider_id": "ZERODHA",
      "provider_role": "selected_option_marketdata",
      "reject_reason": "",
      "seq_no": "",
      "strike": "23300.0",
      "tick_validity": "OK",
      "trading_symbol": "NIFTY2660923300CE",
      "ts_event_ns": "1780493966000000000",
      "ts_provider_ns": "1780493966000000000",
      "ts_recv_ns": "1780474166423259123",
      "volume": "0"
    },
    "reject_reason": "",
    "response_efficiency": 0.0,
    "selected_option_present": true,
    "selected_option_tradability_ok": true,
    "side": "CALL",
    "source_bridge": "batch26o16h_r2",
    "spread": 0.3499999999999943,
    "spread_ratio": 0.001419302514193002,
    "stale": false,
    "strike": 23300.0,
    "tick_validity": "OK",
    "timestamp_present": true,
    "tradability_ok": true,
    "trading_symbol": "NIFTY2660923300CE"
  },
  "snapshot": {
    "active_snapshot_ns": 1780493965000000000,
    "dhan_futures_snapshot_ns": null,
    "dhan_option_snapshot_ns": null,
    "freshness_ok": true,
    "fut_opt_skew_ms": null,
    "futures_snapshot_ns": 1780493965000000000,
    "hard_packet_gap_ms": 1000,
    "max_member_age_ms": 0,
    "packet_gap_ok": true,
    "samples_seen": 1,
    "selected_option_snapshot_ns": null,
    "sync_ok": false,
    "valid": true,
    "validity": "OK",
    "warmup_ok": true
  }
}
```

## Next route
- If raw futures/options moved but score/regime stayed flat, audit feature computation/staleness, not strategy thresholds.
- If score varied naturally but stayed far below min_score, then no paper; continue only after opportunity proof.
- If candidate_positive appears, run controlled-paper readiness preflight, still no paper without approval.
- Do not tune thresholds live from this output alone.