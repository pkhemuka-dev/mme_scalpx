# B2-R2A_READ_ONLY_LOCK_AND_FEED_FAILURE_FORENSIC_NO_START_NO_STOP_NO_DELETE_NO_ORDER_inspect_stale_feeds_execution_locks_and_pfeeds_failure_without_start_stop_delete_patch_order_20260521_094412 next route

classification: `REVIEW_B2_R2A_STALE_FEEDS_LOCK_SUSPECTED_NO_DELETE_NO_START_NO_ORDER`

next_route: `B2-R2B_DRY_PLAN_SAFE_STALE_LOCK_CLEARANCE_OR_HELPER_FIX_NO_DELETE_YET`

Do not clear locks yet unless a later batch proves the owner PID is dead and writes a dry plan first.

Recommended next step depends on classification:
- stale feeds/execution lock suspected: create dry-plan clearance batch, no delete yet.
- feeds running partial growth: run read-only gate recheck.
- safety violation: stop and triage before any further B2 work.
