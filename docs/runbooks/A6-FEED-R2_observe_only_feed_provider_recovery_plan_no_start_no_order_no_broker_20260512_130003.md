# A6-FEED-R2_observe_only_feed_provider_recovery_plan_no_start_no_order_no_broker_20260512_130003 runbook

## Branch
A6-FEED only.

## Current status
R2 recovery plan only. No service action was performed.

## Next batch
A6-FEED-R3 approved observe-only feed/provider recovery action.

## Explicit approval required before R3
User must approve observe-only feed/provider recovery.

## R3 allowed only after approval
- confirm no risk/execution process
- confirm orders:mme:stream unchanged
- gracefully stop unhealthy/orphaned feeds process if still present
- start/restart observe-only feeds/provider runtime using existing project entrypoint
- run immediate read-only canonical stream/hash proof

## R3 forbidden
- no paper/live enablement
- no broker order
- no order placement
- no risk/execution start
- no activation/order-cycle work
- no threshold relaxation
- no forced candidate
- no source patch unless separately approved
