# A6-FEED-R3C-R2_approved_observe_only_feed_recovery_retry_lock_stability_no_hash_write_no_order_no_broker_20260512_133212 runbook

Next depends on verdict:
- PASS_A6_FEED_R3C_R2_FEED_RECOVERY_LOCK_STABLE_RUN_R4D_NEXT -> A6-FEED-R4D
- BLOCKED_A6_FEED_R3C_R2_FEED_LOCK_NOT_STABLE -> A6-FEED-R3D

Still forbidden:
- no paper/live enablement
- no broker order
- no risk/execution start
- no source patch unless separately approved
- no Redis canonical hash write unless guarded R4D passes health gate
