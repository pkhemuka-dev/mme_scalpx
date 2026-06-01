# B1-PROFIT-LIVE-R38ZC_offline_projection_selected_option_timestamp_alignment_after_r38zb_no_patch_no_order_20260531_212929

## Verdict
`REVIEW_R38ZC_PATCH_DID_NOT_PRODUCE_VALID_VIEW_OFFLINE`

## Meaning
R38ZC projects sealed feature records through the R38ZB timestamp-propagation repair using nearest selected-option ticks. No patch was applied.

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_execution: ``

## Counts
- feature_records: `446`
- option_records: `801`
- futures_records: `218`
- projected_total: `446`
- before_data_valid_true: `0`
- after_data_valid_true: `0`
- after_snapshot_sync_valid_true: `0`
- after_provider_ready_classic_true: `0`
- ts_propagated: `446`
- missing_not_faked: `0`
- valid_after_ratio: `0.0`

## Skew buckets
`{'opt_>3000ms': 446}`

## Rule
Offline projection only. No paper/risk/execution/order/broker call was started.

## Next
- If PASS: tomorrow live observe-only verification should confirm `VIEW_DATA_INVALID` drops.
- If REVIEW: inspect live `_family_features` call path and `shared_core` selected-option propagation.
