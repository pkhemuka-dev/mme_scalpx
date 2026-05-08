Batch 29Q OfflineReplayStage order_index alias repair

Date: 2026-05-02

Verdict:
DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_ORDER_INDEX_ALIAS_REPAIR_29Q

Accepted for:
OFFLINE_STAGE_ORDER_INDEX_ALIAS_REPAIR_ONLY

Source:
- 29P proof: run/proofs/proof_offline_stage_order_index_runtime_gap_audit_29p_latest.json
- prior runtime gap: ReplayEngineStageError: replay engine failed for run_id=offline_replay_a96ef007910c5d56: 'OfflineReplayStage' object has no attribute 'order_index'
- target file: app/mme_scalpx/replay/offline_context_shim.py

Result:
order_index_patch_applied=true
order_index_alias_present=true
existing_surfaces_preserved=true
order_index_gap_resolved=true
retry_returncode=2
retry_runtime_error=ReplayEngineStageError: replay engine failed for run_id=offline_replay_a96ef007910c5d56: 'OfflineReplayStage' object has no attribute 'terminal_stage'
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
full_live_replay_parity=NOT_PROVEN_IN_29Q

Next:
Batch 29R — audit/classify next guarded ReplayEngine runtime gap after order_index alias repair, still not paper/live enablement.
