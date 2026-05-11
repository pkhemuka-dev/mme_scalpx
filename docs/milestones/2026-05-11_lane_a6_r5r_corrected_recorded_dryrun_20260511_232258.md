# A6-R5R — Corrected recorded-live dry-run one-active-scope route selection / no broker / no Redis trading write

Generated IST: `2026-05-11T23:22:58.177499+05:30`

## Verdict

`PASS_A6_R5R_CORRECTED_RECORDED_DRYRUN_ONE_ACTIVE_SCOPE_FAILCLOSED_NO_BROKER_NO_REDIS_WRITE`

## What A6-R5R corrected

A6-R5D proved A6-R5 under-counted eligible records. A6-R5R reran the dry-run using recorded explicit eligibility as the dry-run scope-signal input.

This is not live action forcing. The proof remains no-order, no-broker, fail-closed without paper backend.

## Recorded evidence basis

- recorded_candidate_count: `2901`
- eligible_candidate_count: `55`
- eligible_records_loaded_from_A6_R5D_sample: `20`
- family_coverage: `MISB, MISC, MISO, MISR, MIST`
- all_five_seen: `True`

## Assertions

- compile_ok: `True`
- import_ok: `True`
- single_scope_ok: `True`
- multiple_fail_closed_ok: `True`
- no_signal_ok: `True`
- preflight_fail_closed_ok: `True`
- backend_fail_closed_ok: `True`
- order_sent_false: `True`
- broker_calls_executed_false: `True`
- redis_trading_write_attempted_false: `True`

## Safety

- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- order_attempted: false
- order_created: false
- order_sent: false
- broker_calls_executed: false
- redis_trading_stream_write_attempted: false
- controlled_paper_status: `STILL_BLOCKED_AFTER_A6_R5R_DRYRUN`
- orders_xlen_after: `0`
- orders_growth_2s: `0`
- position_flat: `True`
- risk_execution_pids: `0`

## Next

`A6-R6 tomorrow live-session runbook / fresh approval gate / no enablement`
