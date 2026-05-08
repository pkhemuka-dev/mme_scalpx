BATCH 29U OFFLINE STAGE CALLABLE MATERIALIZATION REPAIR

generated_at_utc: 2026-05-02T05:36:27.409892+00:00
verdict: FAIL_29U_DICT_CALLABLE_GAP_NOT_RESOLVED
runtime_gap_kind_before: OFFLINE_REPLAY_STAGE_EXECUTOR_DICT_NOT_CALLABLE_GAP
failing_stage_name_before: offline_replay_input_load
callable_attrs_repaired: ['executor']
patch_applied: True
dict_callable_gap_resolved: False
retry_returncode: 2
retry_runtime_error: ReplayEngineStageError: stage execution failed at 'offline_replay_input_load': 'dict' object is not callable
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29U
repair_path: CALLABLE_MATERIALIZATION_NOT_PROVEN
next_batch: Repair offline stage callable materialization before advancing.

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
- run/proofs/proof_offline_stage_callable_materialization_repair_29u.json
- run/proofs/proof_offline_stage_callable_materialization_repair_29u_latest.json
- run/proofs/batch29u_offline_stage_callable_materialization_repair_20260502_110626_driver_proof.json
- etc/replay/parity/offline_stage_callable_materialization_repair_29u.json
