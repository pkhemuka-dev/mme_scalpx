Batch 29M OfflineReplayStage stage_name alias repair

Date: 2026-05-01

Verdict:
DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_STAGE_NAME_ALIAS_REPAIR_29M

Accepted for:
OFFLINE_STAGE_NAME_ALIAS_REPAIR_ONLY

Source:
- 29L proof: run/proofs/proof_offline_stage_name_runtime_gap_audit_29l_latest.json
- prior runtime gap: AttributeError: 'OfflineReplayStage' object has no attribute 'stage_name'
- target file: app/mme_scalpx/replay/offline_context_shim.py

Result:
stage_alias_patch_applied=true
stage_name_alias_present=true
existing_surfaces_preserved=true
stage_name_gap_resolved=true
retry_returncode=2
retry_runtime_error=AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'stage_names'
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
full_live_replay_parity=NOT_PROVEN_IN_29M

Next:
Batch 29N — audit/classify next guarded ReplayEngine runtime gap after stage_name alias repair, still not paper/live enablement.
