BATCH 29AB-R1 RECONCILE 29AA PASS OUTPUTS

generated_at_utc: 2026-05-02T06:29:26.694876+00:00
verdict: DEFERRED_29AB_R1_29AA_PASS_CHAIN_NOT_FULLY_RECONCILED
proof_29aa_verdict: PASS_OFFLINE_STAGE_DESCRIPTION_ALIAS_REPAIR_29AA
proof_29aa_retry_runtime_error: None
retry_returncode: None
execution_ok: False
replay_core_executed: False
replay_run_completed: False
retry_artifacts_ok: False
outputs_ready_for_inspection: False
full_live_replay_parity: NOT_PROVEN_IN_29AB_R1
repair_path: RECHECK_29AA_PASS_CHAIN
next_batch: Inspect 29AA latest proof and retry artifacts before any patch or parity claim.

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
- run/proofs/proof_reconcile_29aa_pass_outputs_29ab_r1.json
- run/proofs/proof_reconcile_29aa_pass_outputs_29ab_r1_latest.json
- run/proofs/batch29ab_r1_reconcile_29aa_pass_outputs_20260502_115926_driver_proof.json
- etc/replay/parity/reconcile_29aa_pass_outputs_29ab_r1.json
