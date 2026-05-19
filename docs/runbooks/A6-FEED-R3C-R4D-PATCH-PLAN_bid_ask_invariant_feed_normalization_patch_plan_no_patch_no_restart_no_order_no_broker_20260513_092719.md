# A6-FEED-R3C-R4D-PATCH-PLAN_bid_ask_invariant_feed_normalization_patch_plan_no_patch_no_restart_no_order_no_broker_20260513_092719 runbook

Next batch:
A6-FEED-R3C-R4E

A6-FEED-R3C-R4E must:
- patch app/mme_scalpx/services/feeds.py only
- preserve app/mme_scalpx/core/models.py unchanged
- quarantine/drop inverted bid/ask quote before FeedTick construction
- not swap/clamp bid/ask silently
- not enable paper/live
- not start risk/execution
- not send broker orders
- not change thresholds or candidates

After patch:
A6-FEED-R3C-R4F static proof, then A6-FEED-R3C-R3-LIVE-OPEN-R3 live feed proof.
