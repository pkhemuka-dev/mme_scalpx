# A6-FEED-R5D_approved_minimal_features_provider_mapping_patch_no_order_no_broker_no_threshold_change_20260513_073613 runbook

Next batch:
A6-FEED-R5E

A6-FEED-R5E must prove:
- features.py compiles
- patch exists exactly once
- MISO readiness still uses _batch26c_miso_provider_ready
- no broker/order/risk/execution/paper/live surfaces were added
- no threshold or forced-candidate changes were made

Live-session continuation:
After R5E PASS, reload/restart the relevant observe-only feature/strategy stack only when approved, then rerun A6-FEED-R5.

Handoff:
Only after A6-FEED-R5 PASS, hand off to A6-PAPER post-feed activation watcher.
