# LANE-X-R32J_FULL_LIMIT_MATERIALIZER_LEDGER_SUMMARY_NO_PATCH_NO_REPLAY_NO_ORDER_run_existing_r32i_materializer_full_limit_and_compare_to_r9x_candidate_count_20260611_232148

classification: PASS_R32J_FULL_LIMIT_REPLAY_CANDIDATES_MATERIALIZED_TO_INTERNAL_LEDGER_NO_BROKER_NO_ORDER

## Purpose

Run the existing R32I materializer at full limit and compare materialized candidate count with the known R9X candidate count.

## Counts

- source_path: `run/replay/lane_x_r31a_r9x/LANE-X-R31A-R9X_MICRO_REPLAY_AFTER_RISK_ACTION_PATCH_INSPECT_EXECUTION_SHADOW_FILL_PNL_NO_ORDER_micro_replay_verify_candidate_to_risk_execution_shadow_fill_and_pnl_surfaces_20260607_225533/replay_locked_single_day_lane-x-r31a-r9x_micro_replay_after_risk_action_patch_inspect_execution_shadow_fill_pnl_no_order_20260607_172535_e4d110fc/artifacts/strategy_decisions.json`
- candidate_count_materialized: `211`
- expected_candidate_count_from_r9x_proof: `211`
- expected_count_match: `True`
- risk_accept_shadow_count: `211`
- execution_sim_filled_count: `211`
- would_have_order_count: `211`
- real_order_sent_count: `0`
- broker_calls_executed_count: `0`

## Ledger distribution

- ledger_summary: `run/audits/LANE-X-R32J_FULL_LIMIT_MATERIALIZER_LEDGER_SUMMARY_NO_PATCH_NO_REPLAY_NO_ORDER_run_existing_r32i_materializer_full_limit_and_compare_to_r9x_candidate_count_20260611_232148/ledger_summary.json`

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Boundary

- no patch
- no replay start
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete
