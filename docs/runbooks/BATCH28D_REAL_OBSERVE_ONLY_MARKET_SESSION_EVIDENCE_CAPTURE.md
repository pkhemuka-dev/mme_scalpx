Batch 28D Real observe_only Market-session Evidence Capture Runbook

Date: 2026-05-01

Purpose:
Prepare a future real observe_only market-session evidence capture for replay/live parity audit.

Safety:
No paper_armed approval.
No live trading approval.
No broker calls.
No live Redis writes.
No runtime promotion.
No production doctrine change.
Full replay/live parity remains NOT_PROVEN_IN_28D.

Future operator command:
cd /home/Lenovo/scalpx/projects/mme_scalpx
.venv/bin/python bin/observe_only_market_session_capture_operator.py --session-id observe_only_YYYYMMDD --root run/replay/parity/live_session_operator/observe_only_YYYYMMDD

Required future evidence:
provider_runtime
feed_snapshot
feature_payload
family_surfaces
strategy_activation
no_order_sent
live_capture_log
live_stream_inventory
live_hash_inventory
provider_health_snapshot
selected_option_context
dhan_oi_ladder_context_if_available
