# LANE-X-R32I_AUTO_MATERIALIZE_INTERNAL_ORDER_INTENT_FROM_REPLAY_RESULTS_NO_BROKER_NO_ORDER_add_offline_materializer_for_replay_strategy_decisions_to_r32d_r32g_internal_ledgers_20260611_231914

classification: PASS_R32I_REPLAY_RESULTS_AUTO_MATERIALIZED_INTERNAL_ORDER_INTENT_NO_BROKER_NO_ORDER

## What R32I changed

R32I added an offline materializer that reads replay `strategy_decisions.json` artifacts and automatically writes R32D/R32G internal ledgers.

This removes the need for one-off proof scripts to bridge replay results into order-intent ledgers.

## Result

- source_path: `run/replay/lane_x_r31a_r9x/LANE-X-R31A-R9X_MICRO_REPLAY_AFTER_RISK_ACTION_PATCH_INSPECT_EXECUTION_SHADOW_FILL_PNL_NO_ORDER_micro_replay_verify_candidate_to_risk_execution_shadow_fill_and_pnl_surfaces_20260607_225533/replay_locked_single_day_lane-x-r31a-r9x_micro_replay_after_risk_action_patch_inspect_execution_shadow_fill_pnl_no_order_20260607_172535_e4d110fc/artifacts/strategy_decisions.json`
- candidate_count_materialized: `200`
- candidate_intent_count: `200`
- risk_accept_shadow_count: `200`
- risk_reject_shadow_count: `0`
- execution_sim_filled_count: `200`
- order_intent_recorded_count: `200`
- would_have_order_count: `200`
- real_order_sent_count: `0`
- broker_calls_executed_count: `0`

## Broker hard block

- dangerous_env_blocked: `True`
- forbidden_broker_call_names_in_materializer: `[]`
- broker_transport_block_reason: `R32D_BROKER_TRANSPORT_HARD_BLOCKED_NO_SEND`

## Safety

- orders_before: `0`
- risk_before: `0`
- execution_before: `0`
- orders_after: `0`
- risk_after: `0`
- execution_after: `0`

## Boundary

- no replay started
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete
- no live/paper broker transport
