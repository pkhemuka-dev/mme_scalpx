# A6-FEED-R5-M — Option-context active readiness field mapping patch plan

Generated IST: `2026-05-13T09:30:08.795976+05:30`

## Verdict

`PASS_A6_FEED_R5_M_OPTION_CONTEXT_READY_FIELD_PATCH_PLAN_READY_NO_PATCH_NO_ORDER`

## Root cause

`OPTION_CONTEXT_ACTIVE_READY_FIELD_COLLISION_CONFIRMED`

## Current bad value

`state:feed:option_context:active.ready = selected_put_iv`

## Expected value

`ready = 1`

## Next

`A6-FEED-R5-N source patch fix option-context active ready field collision / requires explicit approval`

## Fresh approval required

`I APPROVE A6-FEED-R5-N SOURCE PATCH: FIX OPTION-CONTEXT ACTIVE READY FIELD COLLISION ONLY, NO PAPER, NO LIVE, NO BROKER ORDER, NO RISK/EXECUTION START, NO STRATEGY THRESHOLD CHANGE`

## Safety

- source_patch_applied: false
- service_start_attempted: false
- service_stop_attempted: false
- hash_publish_attempted: false
- helper_publish_attempted: false
- broker_order_executed: false
- order_sent: false
- paper_start_attempted: false
- real_live_trading_attempted: false
- strategy_threshold_change_attempted: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
