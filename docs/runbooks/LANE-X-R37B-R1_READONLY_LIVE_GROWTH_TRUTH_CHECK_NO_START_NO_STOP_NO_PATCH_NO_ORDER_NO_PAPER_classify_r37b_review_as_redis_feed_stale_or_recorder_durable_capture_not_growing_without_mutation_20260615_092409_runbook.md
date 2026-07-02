# Runbook — LANE-X-R37B-R1_READONLY_LIVE_GROWTH_TRUTH_CHECK_NO_START_NO_STOP_NO_PATCH_NO_ORDER_NO_PAPER_classify_r37b_review_as_redis_feed_stale_or_recorder_durable_capture_not_growing_without_mutation_20260615_092409
Allowed: read-only Redis xlen/xrevrange, pstatus, process snapshot, live_capture size listing.
Forbidden: pauto_status, pauto_start, pauto_stop, pfeeds, pfeedstop, pstack, patch, start, stop, order, paper, live, risk, execution, replay, Redis delete, lock delete, stream delete.
