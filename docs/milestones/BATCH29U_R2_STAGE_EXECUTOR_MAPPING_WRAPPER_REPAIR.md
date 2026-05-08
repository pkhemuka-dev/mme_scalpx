BATCH 29U-R2 STAGE_EXECUTOR MAPPING WRAPPER REPAIR

generated_at_utc: 2026-05-02T05:44:52.391116+00:00
verdict: DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_STAGE_EXECUTOR_WRAPPER_29U_R2
patch_applied: False
stage_executor_wrapper_probe_ok: True
dict_callable_gap_resolved: True
retry_returncode: 2
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'scope'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29U_R2
repair_path: NEXT_REPLAY_ENGINE_RUNTIME_GAP_AUDIT
next_batch: Batch 29V — audit/classify next guarded ReplayEngine runtime gap after stage_executor wrapper repair, still not paper/live enablement.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Files changed in this batch:
- none

Proofs:
- run/proofs/proof_stage_executor_mapping_wrapper_repair_29u_r2.json
- run/proofs/proof_stage_executor_mapping_wrapper_repair_29u_r2_latest.json
- run/proofs/batch29u_r2_stage_executor_mapping_wrapper_repair_20260502_111451_driver_proof.json
- etc/replay/parity/stage_executor_mapping_wrapper_repair_29u_r2.json
