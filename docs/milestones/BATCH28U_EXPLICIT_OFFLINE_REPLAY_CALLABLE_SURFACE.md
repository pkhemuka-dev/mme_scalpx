Batch 28U Explicit offline replay callable surface

Date: 2026-05-01

Verdict:
FAIL_EXPLICIT_OFFLINE_REPLAY_CALLABLE_SURFACE_28U

Accepted for:
EXPLICIT_OFFLINE_REPLAY_CALLABLE_SURFACE_BUILD_ONLY

Reason:
28T safely deferred because no proven replay-engine callable was discoverable.
28U adds an explicit offline-only callable surface under app/mme_scalpx/replay/offline_callable.py.

Generated / changed:
- app/mme_scalpx/replay/offline_callable.py
- etc/replay/parity/explicit_offline_replay_callable_surface_28u.json
- run/proofs/proof_explicit_offline_replay_callable_surface_28u.json
- run/proofs/proof_explicit_offline_replay_callable_surface_28u_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/explicit_offline_replay_callable_surface_28u/

Result:
callable_surface_added=true
callable_import_ok=false
callable_signature_ok=false
replay_engine_invoked=false
replay_run_completed=false
comparison_completed=false

Safety:
starts_services=false
reads_live_redis=false
writes_live_redis=false
calls_broker_api=false
paper_armed_approved=false
live_trading_approved=false
execution_arming_created=false
real_order_sent=false
production_doctrine_changed=false
full_live_replay_parity=NOT_PROVEN_IN_28U

Next:
Batch 28V — execute explicit offline replay callable dry-run, still not paper/live enablement.
