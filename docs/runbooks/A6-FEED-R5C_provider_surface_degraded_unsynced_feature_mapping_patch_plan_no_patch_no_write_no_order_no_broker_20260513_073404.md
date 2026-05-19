# A6-FEED-R5C_provider_surface_degraded_unsynced_feature_mapping_patch_plan_no_patch_no_write_no_order_no_broker_20260513_073404 runbook

Next batch:
A6-FEED-R5D

A6-FEED-R5D must:
- patch features.py only unless inspection proves otherwise
- preserve MISO fail-closed when option context is degraded
- allow classic readiness when futures + selected option are healthy
- preserve observe_only
- not start risk/execution
- not send orders
- not enable paper/live
- not change thresholds

After R5D/R5E:
Rerun A6-FEED-R5 during live session.

Handoff:
Only if A6-FEED-R5 PASS, hand off to A6-PAPER post-feed activation watcher.
