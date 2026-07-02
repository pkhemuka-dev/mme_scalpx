# Runbook — LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739
Allowed: one pauto_start under observe-only env, pstatus, Redis xlen/xrevrange, process snapshot, live_capture listing.
Forbidden: pauto_status, pauto_stop, pfeeds, pfeedstop, pstack, patch, paper, live, broker order, risk service, execution service, replay, Redis delete, lock delete, stream delete.
