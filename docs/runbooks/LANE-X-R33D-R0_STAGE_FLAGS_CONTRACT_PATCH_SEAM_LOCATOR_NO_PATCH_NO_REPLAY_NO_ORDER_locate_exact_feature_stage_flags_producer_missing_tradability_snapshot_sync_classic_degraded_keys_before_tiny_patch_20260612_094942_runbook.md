# LANE-X-R33D-R0_STAGE_FLAGS_CONTRACT_PATCH_SEAM_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_exact_feature_stage_flags_producer_missing_tradability_snapshot_sync_classic_degraded_keys_before_tiny_patch_20260612_094942 Runbook

Do not patch broad provider logic first.

Patch scope for next batch:
- Add missing stage_flags keys only:
  - tradability_ok
  - snapshot_sync_valid
  - classic_provider_degraded_safe
- Conservative default false.
- No order.
- No replay.
- No risk/execution start.
- No paper/live.
