# B1-PROFIT-LIVE-R38X-R2_strict_json_sealed_export_candidate_audit_no_patch_no_order_no_paper_20260531_195424

## Verdict
`NO_TRUE_CLASSIC_TRADE_CANDIDATE_ONLY_HOLD_SURFACES`

## Meaning
This is a strict JSON audit of the sealed export. It does not rely on loose regex matching.

## Sealed export
`run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260529_153921`

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_execution: ``

## Counts
- total_payloads: `998`
- hold_no_candidate: `8`
- entry_like: `0`
- safe_to_promote: `0`
- true_classic_trade_candidates: `0`
- mist_surface_rows: `998`

## Top reasons
`{'HOLD_ONLY_FAMILY_FEATURES_CONSUMER_BRIDGE': 998}`

## Top activation reasons
`{'NO_CANDIDATE': 8, 'VIEW_DATA_INVALID': 990}`

## Interpretation
- If `true_classic_trade_candidates` is `0`, then the previous R38X result was only a loose candidate-surface hit, not a real paper-ready trade candidate.
- Fresh live observe-only candidate proof is still required before controlled paper.

## Rule
Offline analysis only. No paper/risk/execution/order/broker call was started.
