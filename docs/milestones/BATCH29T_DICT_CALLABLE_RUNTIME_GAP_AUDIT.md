BATCH 29T DICT-CALLABLE RUNTIME GAP AUDIT

generated_at_utc: 2026-05-02T05:33:30.287997+00:00
verdict: PASS_DICT_CALLABLE_RUNTIME_GAP_AUDIT_29T
runtime_gap_kind: OFFLINE_REPLAY_STAGE_EXECUTOR_DICT_NOT_CALLABLE_GAP
failing_stage_name: offline_replay_input_load
retry_runtime_error: ReplayEngineStageError: stage execution failed at 'offline_replay_input_load': 'dict' object is not callable
dict_callable_gap_confirmed: True
terminal_stage_gap_resolved: True
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29T
repair_path: REPAIR_OFFLINE_REPLAY_STAGE_CALLABLE_MATERIALIZATION
next_batch: Batch 29U — repair offline replay stage callable materialization for offline_replay_input_load, still not paper/live enablement.

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
- run/proofs/proof_dict_callable_runtime_gap_audit_29t.json
- run/proofs/proof_dict_callable_runtime_gap_audit_29t_latest.json
- run/proofs/batch29t_dict_callable_runtime_gap_audit_20260502_110330_driver_proof.json
- etc/replay/parity/dict_callable_runtime_gap_audit_29t.json
