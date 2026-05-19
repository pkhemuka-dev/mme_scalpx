# A6-AFTERMARKET-R0 — Post live-session consolidation and tomorrow handoff

Generated IST: `2026-05-13T07:30:06.477210+05:30`

## Verdict

`PASS_A6_AFTERMARKET_R0_HANDOFF_READY_NO_PATCH_NO_ORDER`

## Continuation status

`A6_FEED_R5_L_OUTPUT_MISSING`

## Paper status

`A6_PAPER_STILL_BLOCKED_UNTIL_A6_FEED_R5_READINESS_PASS`

## Next market-open batch

`Paste/run A6-FEED-R5-L result first; then continue based on verdict`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_order_executed: false
- order_sent: false
- paper_start_attempted: false
- real_live_trading_attempted: false

## Source

- feeds_compile_ok: `True`
- feeds_import_ok: `True`
- a6_r5l_helper_present: `False`

## Hash state now

- present: `{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`
- ready: `{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`

## Consumer blockers

- provider_blocker_count: `0`

## Rules for market open

1. A6-PAPER remains blocked until A6-FEED readiness passes.
2. Do not run all strategies in execution mode.
3. Monitor all families, arm one scoped signal only.
4. 1 lot only, paper/sandbox only.
5. Real live forbidden.
