Batch 29I Offline run_context run_id repair

Date: 2026-05-01

Verdict:
DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_RUN_ID_REPAIR_29I

Accepted for:
OFFLINE_RUN_CONTEXT_RUN_ID_REPAIR_ONLY

Source:
- 29H-R2 proof: run/proofs/proof_guarded_replay_engine_runtime_gap_audit_29h_r2_latest.json
- prior runtime gap: AttributeError: 'OfflineReplayRunContext' object has no attribute 'run_id'
- target file: app/mme_scalpx/replay/offline_context_shim.py
- guarded retry script: bin/guarded_replay_engine_execute_dry_run_29g.py

Generated:
- etc/replay/parity/offline_run_context_run_id_repair_29i.json
- run/proofs/proof_offline_run_context_run_id_repair_29i.json
- run/proofs/proof_offline_run_context_run_id_repair_29i_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/offline_run_context_run_id_repair_29i/
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_engine_execute_retry_29i/

Result:
patch_applied=true
run_id_support_present=true
run_id_gap_resolved=true
retry_returncode=2
retry_runtime_error=AttributeError: 'ReplayTopologyBuilder' object has no attribute 'stages'
execution_ok=false
replay_core_executed=false
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
full_live_replay_parity=NOT_PROVEN_IN_29I

Next:
Batch 29J — audit/classify next guarded ReplayEngine runtime gap after run_id repair, still not paper/live enablement.
