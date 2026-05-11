# A6-R5D — Recorded-evidence eligible-scope locator / no source patch / no broker call

Generated IST: `2026-05-11T23:17:38.481565+05:30`

## Verdict

`PASS_A6_R5D_RECORDED_EVIDENCE_LOCATOR_FOUND_ELIGIBLE_SCOPE_NO_PATCH_NO_BROKER`

## Locator classification

- locator_classification: `ELIGIBLE_SCOPE_FOUND_BY_R5D_PARSER`
- root_cause: A6-R5 parser/proof path under-counted eligible candidates.

## Candidate evidence

- candidate_count: `2901`
- eligible_candidate_count: `55`
- explicit_eligible_candidate_count: `55`
- action_eligible_candidate_count: `0`
- family_coverage: `MISB, MISC, MISO, MISR, MIST`
- all_five_seen: `True`
- action_counts: `{'': 2835, 'HOLD': 66}`
- blocker_counts: `{'ACTION_BLOCKLIST_OR_HOLD': 2901, 'NO_EXPLICIT_ELIGIBLE_TRUE_FIELD': 2846, 'NOT_ELIGIBLE_BY_A6_R5_NORMALIZER': 2846}`

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
- controlled_paper_status: `STILL_BLOCKED_AFTER_A6_R5D_LOCATOR`
- orders_xlen_after: `0`
- orders_growth_2s: `0`
- position_flat: `True`
- risk_execution_pids: `0`

## Next

`A6-R5R rerun recorded-live dry-run with corrected evidence parser / no source patch / no broker call`
