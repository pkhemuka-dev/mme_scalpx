BATCH 29U-R1 STAGE_EXECUTOR DICT-CALLABLE AUDIT

generated_at_utc: 2026-05-02T05:40:15.856157+00:00
verdict: PASS_STAGE_EXECUTOR_DICT_CALLABLE_AUDIT_29U_R1
runtime_gap_kind: STAGE_EXECUTOR_OBJECT_MATERIALIZED_AS_DICT_NOT_CALLABLE
failing_stage_name: offline_replay_input_load
stage_executor_materialized_as_dict: True
stage_executor_callable: False
retry_runtime_error: ReplayEngineStageError: stage execution failed at 'offline_replay_input_load': 'dict' object is not callable
repair_path: REPAIR_GUARDED_STAGE_EXECUTOR_MAPPING_WRAPPER
next_batch: Batch 29U-R2 — repair guarded offline stage_executor mapping-to-callable wrapper, still not paper/live enablement.

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
- run/proofs/proof_stage_executor_dict_callable_audit_29u_r1.json
- run/proofs/proof_stage_executor_dict_callable_audit_29u_r1_latest.json
- run/proofs/batch29u_r1_stage_executor_dict_callable_audit_20260502_111015_driver_proof.json
- etc/replay/parity/stage_executor_dict_callable_audit_29u_r1.json
