# A6-FEED-R5BE-R6_repair_stage_flags_validator_and_builder_same_live_order_static_validation_no_restart_no_order_no_paper_20260518_103030

Verdict: `BLOCKED_A6_FEED_R5BE_R6_STATIC_VALIDATION_FAILED_REVERTED_NO_RESTART`

Lane: A6-FEED only.

Aligned `validate_stage_flags_block()` and `build_empty_stage_flags_block()` to live order: `snapshot_sync_valid`, then `classic_provider_degraded_safe`.

No restart, no paper/live, no broker/order, no risk/execution.

Safety after:
- orders zero: `True`
- position flat: `True`
- risk/execution absent: `True`
- app services absent: `True`
