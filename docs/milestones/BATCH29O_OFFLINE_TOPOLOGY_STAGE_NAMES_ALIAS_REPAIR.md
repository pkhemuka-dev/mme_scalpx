Batch 29O OfflineReplayTopologyPlan stage_names alias repair

Date: 2026-05-02

Verdict:
DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_STAGE_NAMES_ALIAS_REPAIR_29O

Accepted for:
OFFLINE_TOPOLOGY_STAGE_NAMES_ALIAS_REPAIR_ONLY

Source:
- 29N proof: run/proofs/proof_offline_topology_stage_names_runtime_gap_audit_29n_latest.json
- prior runtime gap: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'stage_names'
- target file: app/mme_scalpx/replay/offline_context_shim.py

Result:
topology_alias_patch_applied=true
stage_names_alias_present=true
existing_surfaces_preserved=true
stage_names_gap_resolved=true
retry_returncode=2
retry_runtime_error=ReplayEngineStageError: replay engine failed for run_id=offline_replay_a96ef007910c5d56: 'OfflineReplayStage' object has no attribute 'order_index'
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
full_live_replay_parity=NOT_PROVEN_IN_29O

Next:
Batch 29P — audit/classify next guarded ReplayEngine runtime gap after stage_names alias repair, still not paper/live enablement.
