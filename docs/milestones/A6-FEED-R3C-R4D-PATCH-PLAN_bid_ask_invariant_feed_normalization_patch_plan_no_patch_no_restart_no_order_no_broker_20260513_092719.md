# A6-FEED-R3C-R4D-PATCH-PLAN_bid_ask_invariant_feed_normalization_patch_plan_no_patch_no_restart_no_order_no_broker_20260513_092719

## Purpose
Patch-plan only for live feed blocker where inverted bid/ask payloads are rejected by FeedTick validation.

## Blocker
POLLED_CORE_TICK_PAYLOAD_REJECTED_BY_FEEDTICK_ASK_MUST_BE_GTE_BID

## Planned correction
Patch feeds.py only:
- preserve FeedTick ask >= bid contract
- do not change core models.py
- do not swap or fake bid/ask values
- drop/quarantine invalid inverted bid/ask payload before FeedTick construction
- allow valid futures and selected-option ticks to continue publishing
- no paper/live, broker order, risk/execution, threshold, or candidate changes

## Safety
- source_patch_applied: false
- redis_hash_write_attempted: false
- service_start_attempted: false
- service_stop_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false

## Verdict
See proof: run/proofs/A6-FEED-R3C-R4D-PATCH-PLAN_bid_ask_invariant_feed_normalization_patch_plan_no_patch_no_restart_no_order_no_broker_20260513_092719.txt
