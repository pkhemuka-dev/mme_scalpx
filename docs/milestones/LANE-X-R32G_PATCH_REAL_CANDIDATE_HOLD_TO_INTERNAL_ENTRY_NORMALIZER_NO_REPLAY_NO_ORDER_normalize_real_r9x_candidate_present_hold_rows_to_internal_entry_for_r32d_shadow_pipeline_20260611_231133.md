# LANE-X-R32G_PATCH_REAL_CANDIDATE_HOLD_TO_INTERNAL_ENTRY_NORMALIZER_NO_REPLAY_NO_ORDER_normalize_real_r9x_candidate_present_hold_rows_to_internal_entry_for_r32d_shadow_pipeline_20260611_231133

classification: PASS_R32G_REAL_R9X_HOLD_CANDIDATES_NORMALIZED_TO_INTERNAL_ENTRY_NO_BROKER_NO_REPLAY_NO_ORDER

## What R32G changed

R32G patched the R32D internal pipeline normalizer.

It preserves real source action:

- source_action = HOLD

but for candidate-present / scored real R9X candidates, it maps internal shadow action to:

- action = ENTRY
- action_normalization_reason = r32g_candidate_present_hold_to_internal_entry_shadow_only

This is internal-only. Broker transport remains hard-blocked.

## Smoke result

- real_candidate_input_count: `20`
- total_candidate_input_count: `21`
- candidate_intent_count: `21`
- risk_accept_shadow_count: `20`
- risk_reject_shadow_count: `1`
- execution_sim_filled_count: `20`
- order_intent_recorded_count: `21`
- would_have_order_count: `20`
- real_order_sent_count: `0`
- broker_calls_executed_count: `0`
- r32g_action_normalized_count: `20`
- source_hold_count: `21`

## Broker hard block

- dangerous_env_blocked: `True`
- forbidden_broker_call_names_in_module: `[]`
- broker_transport_block_reason: `R32D_BROKER_TRANSPORT_HARD_BLOCKED_NO_SEND`

## Safety

- orders_before: `0`
- risk_before: `0`
- execution_before: `0`
- orders_after: `0`
- risk_after: `0`
- execution_after: `0`

## Boundary

- patch is internal shadow/order-intent normalizer only
- no replay
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete
- no live/paper broker transport
