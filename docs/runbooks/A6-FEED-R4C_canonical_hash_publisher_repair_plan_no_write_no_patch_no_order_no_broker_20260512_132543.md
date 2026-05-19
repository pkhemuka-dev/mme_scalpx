# A6-FEED-R4C_canonical_hash_publisher_repair_plan_no_write_no_patch_no_order_no_broker_20260512_132543 runbook

Next depends on R4C verdict:
- PASS_A6_FEED_R4C_EXISTING_HASH_PUBLISHER_SCRIPTS_FOUND_REPAIR_PLAN_READY_NO_WRITE_NO_PATCH -> A6-FEED-R4D
- BLOCKED_A6_FEED_R4C_NO_EXISTING_HASH_PUBLISHER_SCRIPT_FOUND -> A6-FEED-R4D-SOURCE-PLAN

Still forbidden:
- no paper/live enablement
- no broker order
- no risk/execution start
- no source patch unless separately approved
- no Redis canonical hash write unless explicitly approved in R4D
