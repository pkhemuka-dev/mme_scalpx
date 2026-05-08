BATCH 29Y-R2 SCOPE PROPERTY EXCEPTION REPAIR

generated_at_utc: 2026-05-02T06:15:32.455064+00:00
verdict: DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_SCOPE_PROPERTY_EXCEPTION_REPAIR_29Y_R2
patch_applied: True
scope_property_exception_resolved: True
scope_value_probe_ok: True
scope_value_gap_resolved: True
retry_returncode: 2
retry_runtime_error: AttributeError: 'OfflineReplayStage' object has no attribute 'description'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29Y_R2
repair_path: NEXT_REPLAY_ENGINE_RUNTIME_GAP_AUDIT
next_batch: Batch 29Z — audit/classify next guarded ReplayEngine runtime gap after scope property exception repair, still not paper/live enablement.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Files changed in this batch:
- app/mme_scalpx/replay/offline_context_shim.py

Proofs:
- run/proofs/proof_scope_property_exception_repair_29y_r2.json
- run/proofs/proof_scope_property_exception_repair_29y_r2_latest.json
- run/proofs/batch29y_r2_scope_property_exception_repair_20260502_114531_driver_proof.json
- etc/replay/parity/scope_property_exception_repair_29y_r2.json
