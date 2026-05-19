# A6-FEED-R3_approved_observe_only_feed_provider_recovery_action_no_order_no_broker_20260512_130536 runbook

## Branch
A6-FEED only.

## R3 result
BLOCKED_A6_FEED_R3_PFEED_OR_PFEEDSTOP_NOT_AVAILABLE_NO_FALLBACK_USED

## Next batch
A6-FEED-R4 post-recovery canonical stream/hash proof.

## R4 must prove
- futures canonical stream growing
- selected option canonical stream growing
- Dhan option context stream growing where required
- state:provider_runtime:mme present
- state:feed:futures:active present
- state:feed:selected_option:active present
- state:feed:option_context:active present
- orders:mme:stream unchanged
- position FLAT

## Still forbidden
- paper/live enablement
- broker order
- order placement
- risk/execution start
- activation/order-cycle work
- threshold relaxation
- forced candidate
- source patch unless separately approved
