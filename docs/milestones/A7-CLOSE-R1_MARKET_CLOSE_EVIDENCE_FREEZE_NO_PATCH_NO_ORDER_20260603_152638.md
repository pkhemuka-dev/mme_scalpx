# A7-CLOSE-R1_MARKET_CLOSE_EVIDENCE_FREEZE_NO_PATCH_NO_ORDER_20260603_152638

Classification: `PASS_A7_CLOSE_EVIDENCE_FROZEN_R39WE_PRESENT_R39WK_ROLLED_BACK_NO_ORDER`

## Close status
- orders_clean: True
- risk_clean: True
- execution_clean: True
- r39we_present: True
- r39wk_present: False
- candidate_positive: 0
- classic_disabled_hits: 0

## Decision reasons
```json
{
  "hold_only_family_features_consumer_bridge": 1000
}
```

## Activation reasons
```json
{
  "no_candidate": 739,
  "view_data_invalid": 261
}
```

## Leaf reasons
```json
{
  "directional_breakout_not_confirmed": 1478,
  "reversal_direction_not_confirmed": 1478,
  "score_below_threshold": 2956,
  "stage_provider_ready_miso_failed": 1478
}
```

## Nearest miss
```json
{
  "branch_id": "CALL",
  "breakout_score": 0.004615384615384616,
  "family_id": "MISB",
  "futures_impulse_score": null,
  "gap": 0.2800615384615385,
  "min_score": 0.64,
  "option_confirmation_score": 0.5,
  "reason": "score_below_threshold",
  "regime": "LOWVOL",
  "score": 0.35993846153846154
}
```

## Next route
- Do not patch during closing minutes.
- After market: apply R39WM using R39WL valid local insertion lines only.
- Then compile/import/self-test, targeted reload tomorrow/live only if needed, and rerun R39WH/R39WI.
- Paper remains blocked.