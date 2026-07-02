# LANE-X-R32E_REAL_CANDIDATE_TO_INTERNAL_ORDER_INTENT_BRIDGE_NO_PATCH_NO_REPLAY_NO_ORDER_feed_existing_r9x_candidate_positive_rows_into_r32d_internal_order_intent_pipeline_20260611_230113

classification: PASS_R32E_REAL_CANDIDATES_FED_TO_R32D_INTERNAL_ORDER_INTENT_NO_BROKER_NO_REPLAY_NO_ORDER

## Purpose

Feed existing real R9X candidate-positive evidence into the new R32D internal order-intent pipeline.

## Result

- candidate_count_loaded: `20`
- candidate_intent_count: `20`
- risk_accept_shadow_count: `0`
- risk_reject_shadow_count: `20`
- execution_sim_filled_count: `0`
- order_intent_recorded_count: `20`
- would_have_order_count: `0`
- real_order_sent_count: `0`
- broker_calls_executed_count: `0`

## Source

- r9x_proof: `run/proofs/LANE-X-R31A-R9X_MICRO_REPLAY_AFTER_RISK_ACTION_PATCH_INSPECT_EXECUTION_SHADOW_FILL_PNL_NO_ORDER_micro_replay_verify_candidate_to_risk_execution_shadow_fill_and_pnl_surfaces_20260607_225533.json`
- discovery: `run/audits/LANE-X-R32E_REAL_CANDIDATE_TO_INTERNAL_ORDER_INTENT_BRIDGE_NO_PATCH_NO_REPLAY_NO_ORDER_feed_existing_r9x_candidate_positive_rows_into_r32d_internal_order_intent_pipeline_20260611_230113/r9x_discovery.txt`
- candidates_json: `run/audits/LANE-X-R32E_REAL_CANDIDATE_TO_INTERNAL_ORDER_INTENT_BRIDGE_NO_PATCH_NO_REPLAY_NO_ORDER_feed_existing_r9x_candidate_positive_rows_into_r32d_internal_order_intent_pipeline_20260611_230113/real_candidates_for_r32d.json`

## Safety

- orders_before: `0`
- risk_before: `0`
- execution_before: `0`
- orders_after: `0`
- risk_after: `0`
- execution_after: `0`

## Boundary

- no source patch
- no replay
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete
