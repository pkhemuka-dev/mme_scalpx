Batch 28U-R1 Rescue explicit offline replay callable import/signature

Date: 2026-05-01

Verdict:
PASS_EXPLICIT_OFFLINE_REPLAY_CALLABLE_SURFACE_28U_R1

Accepted for:
EXPLICIT_OFFLINE_REPLAY_CALLABLE_SURFACE_IMPORT_SIGNATURE_RESCUE_ONLY

Reason:
28U wrote app/mme_scalpx/replay/offline_callable.py but failed callable import/signature proof.
28U-R1 rewrites the callable surface with a minimal compatibility-safe implementation and proves direct/package import diagnostics.

Generated / changed:
- app/mme_scalpx/replay/offline_callable.py
- etc/replay/parity/explicit_offline_replay_callable_surface_28u_r1.json
- run/proofs/proof_explicit_offline_replay_callable_surface_28u_r1.json
- run/proofs/proof_explicit_offline_replay_callable_surface_28u_r1_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/explicit_offline_replay_callable_surface_28u_r1/

Result:
callable_surface_added=true
callable_import_ok=true
callable_signature_ok=true
direct_import_ok=true
package_import_ok=false
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
full_live_replay_parity=NOT_PROVEN_IN_28U_R1

Next:
Batch 28V — execute explicit offline replay callable dry-run, still not paper/live enablement.
