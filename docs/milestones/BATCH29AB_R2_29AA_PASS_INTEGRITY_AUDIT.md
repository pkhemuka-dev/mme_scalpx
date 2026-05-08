BATCH 29AB-R2 29AA PASS INTEGRITY AUDIT

generated_at_utc: 2026-05-02T06:31:22.693050+00:00
verdict: DEFERRED_29AB_R2_RETRY_ARTIFACTS_FOUND_BUT_NOT_READY_FOR_PARITY_INSPECTION
proof_29aa_verdict: PASS_OFFLINE_STAGE_DESCRIPTION_ALIAS_REPAIR_29AA
proof_29aa_pass_label: True
proof_29aa_structurally_complete: False
retry_artifact_root_found: True
selected_retry_root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_engine_execute_retry_29aa
selected_retry_runtime_error: AttributeError: 'OfflineReplayStage' object has no attribute 'owns_runtime_decisioning'
selected_retry_execution_ok: False
selected_retry_replay_run_completed: False
outputs_ready_for_inspection: False
repair_path: CLASSIFY_SELECTED_RETRY_ARTIFACT_FAILURE
next_batch: Batch 29AB-R3 — classify selected retry artifacts before any code patch.

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
- run/proofs/proof_29aa_pass_integrity_audit_29ab_r2.json
- run/proofs/proof_29aa_pass_integrity_audit_29ab_r2_latest.json
- run/proofs/batch29ab_r2_29aa_pass_integrity_audit_20260502_120122_driver_proof.json
- etc/replay/parity/proof_29aa_pass_integrity_audit_29ab_r2.json
