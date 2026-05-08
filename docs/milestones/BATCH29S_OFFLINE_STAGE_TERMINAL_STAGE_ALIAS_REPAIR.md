BATCH 29S OFFLINE STAGE TERMINAL_STAGE ALIAS REPAIR

generated_at_utc: 2026-05-02T05:28:45.902325+00:00
verdict: FAIL_OFFLINE_STAGE_TERMINAL_STAGE_ALIAS_REPAIR_STATIC_PROOF_FAILED_29S
target_file: app/mme_scalpx/replay/offline_context_shim.py
patch_applied: True
terminal_stage_alias_present: True
terminal_stage_gap_resolved: False
retry_returncode: None
retry_runtime_error: None
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29S
next_batch: Repair static/import failure before retrying ReplayEngine dry-run.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Changed files:
- app/mme_scalpx/replay/offline_context_shim.py

Proofs:
- run/proofs/proof_offline_stage_terminal_stage_alias_repair_29s.json
- run/proofs/proof_offline_stage_terminal_stage_alias_repair_29s_latest.json
- run/proofs/batch29s_offline_stage_terminal_stage_alias_repair_20260502_105845_driver_proof.json
- etc/replay/parity/offline_stage_terminal_stage_alias_repair_29s.json
