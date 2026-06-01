# B3-R2_REPLAY_MVP_INPUT_BUNDLE_AND_DRY_RUN_PLAN_NO_REPLAY_NO_ORDER_inspect_b2_b3_artifacts_prepare_zerodha_only_replay_mvp_inputs_and_next_dry_run_plan_20260521_102011 next route

classification: `PASS_B3_R2_REPLAY_MVP_INPUTS_INDEXED_READY_FOR_B3_R3_OFFLINE_DRY_RUN_NO_ORDER`
mvp_status: `READY_FOR_OFFLINE_DRY_RUN`

If PASS:
Run B3-R3 offline replay dry-run from captured surfaces, Zerodha-only, no broker/order.

If REVIEW:
Create compact capture export from existing Redis/tail artifacts first.

Hard rules:
- no broker order
- no paper/live
- no replay against live Redis
- no PnL claim
- no production replay readiness claim
