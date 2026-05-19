# A6-LIVE-R2I-D next runbook

## Current status

`PASS_A6_LIVE_R2I_D_VIEW_DATA_INVALID_ROOT_CAUSE_CLASSIFIED_NO_SOURCE_PATCH_NO_ORDER_NO_BROKER`

## Root cause

`VIEW_DATA_INVALID_DUE_SAFE_TO_CONSUME_FALSE`

## Next

`A6-LIVE-R2I-E readiness/provider specific diagnostic / no source patch / no order / no broker call`

## Rule

No order-cycle until activation_candidate_count > 0, activation_safe_to_promote = true, side is CALL/PUT, and the gate prints a fresh approval phrase.
