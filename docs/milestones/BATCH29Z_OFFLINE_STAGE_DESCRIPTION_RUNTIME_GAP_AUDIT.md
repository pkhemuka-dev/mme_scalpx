BATCH 29Z OFFLINE STAGE DESCRIPTION RUNTIME GAP AUDIT

generated_at_utc: 2026-05-02T06:23:46.784708+00:00
verdict: PASS_OFFLINE_STAGE_DESCRIPTION_RUNTIME_GAP_AUDIT_29Z
runtime_gap_kind: OFFLINE_REPLAY_STAGE_DESCRIPTION_ATTRIBUTE_GAP
retry_runtime_error: AttributeError: 'OfflineReplayStage' object has no attribute 'description'
stage_description_gap_confirmed: True
engine_consumes_stage_description: False
canonical_stage_description_present: False
offline_stage_description_present: False
repair_path: REPAIR_OFFLINE_STAGE_DESCRIPTION_ALIAS
next_batch: Batch 29AA — repair OfflineReplayStage.description alias in offline_context_shim.py only, still not paper/live enablement.

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
- run/proofs/proof_offline_stage_description_runtime_gap_audit_29z.json
- run/proofs/proof_offline_stage_description_runtime_gap_audit_29z_latest.json
- run/proofs/batch29z_offline_stage_description_runtime_gap_audit_20260502_115346_driver_proof.json
- etc/replay/parity/offline_stage_description_runtime_gap_audit_29z.json
