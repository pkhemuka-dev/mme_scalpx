BATCH 29S-R1 TERMINAL_STAGE IMPORT PROBE RESCUE

generated_at_utc: 2026-05-02T05:31:50.477631+00:00
verdict: DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_TERMINAL_STAGE_ALIAS_REPAIR_29S_R1
target_file: app/mme_scalpx/replay/offline_context_shim.py
code_patch_applied: False
valid_import_probe_ok: True
terminal_stage_alias_present: True
terminal_stage_gap_resolved: True
retry_returncode: 2
retry_runtime_error: ReplayEngineStageError: stage execution failed at 'offline_replay_input_load': 'dict' object is not callable
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29S_R1
next_batch: Batch 29T — audit/classify next guarded ReplayEngine runtime gap after terminal_stage alias repair, still not paper/live enablement.

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
- run/proofs/proof_offline_stage_terminal_stage_alias_repair_29s_r1.json
- run/proofs/proof_offline_stage_terminal_stage_alias_repair_29s_r1_latest.json
- run/proofs/batch29s_r1_terminal_stage_import_probe_rescue_20260502_110149_driver_proof.json
- etc/replay/parity/offline_stage_terminal_stage_alias_repair_29s_r1.json
