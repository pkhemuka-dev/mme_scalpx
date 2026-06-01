# B3-R3_OFFLINE_REPLAY_DRY_RUN_FROM_CAPTURED_SURFACES_ZERODHA_ONLY_NO_BROKER_NO_ORDER_run_or_block_offline_replay_mvp_dry_run_from_b3_r2_manifest_without_broker_order_pnl_20260521_102211 next route

classification: `PASS_B3_R3_REPLAY_MVP_DRY_COMPATIBILITY_PROOF_READY_FOR_DETERMINISTIC_OFFLINE_REPLAY_NO_ORDER`
mvp_result: `DRY_COMPAT_PASS_NO_REPLAY_EXECUTION`

If PASS:
Review dryrun_log and then run B3-R4 deterministic offline replay execution dry-only, no broker/order.

If REVIEW:
Patch/adapt replay MVP dataset loader after-market.

Hard rules:
- no broker order
- no paper/live
- no live Redis replay source
- no PnL claim
