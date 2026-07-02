# LANE-B-R2B_REPLAY_CLI_ABI_AND_EXACT_SMOKE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_135114

If PASS:
- Use replay_run.py help/argument clues from this report to write exact R2C offline replay smoke.
- R2C must use the fixed R2A dataset:
  run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/2026-06-02
- R2C must remain no Redis delete, no live, no paper, no broker/order, no risk/execution start.

If REVIEW:
- Do not replay.
- Inspect missing CLI ABI or missing dataset files first.
