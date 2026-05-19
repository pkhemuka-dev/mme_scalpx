# A6-LIVE-R2I next runbook

## Current status

`BLOCKED_A6_LIVE_R2I_NO_LIVE_SCOPE_READY_YET_GATE_FAIL_CLOSED_NO_ORDER_NO_BROKER`

## Next

`A6-LIVE-R2 watcher rerun / wait for activation_safe_to_promote true`

## Fresh approval phrase if ready

`None`

## Rule

Do not run any order-cycle unless the exact fresh approval phrase is provided and the next batch preflight again proves:
- orders stream zero
- position flat
- real live forbidden
- one selected scope only
