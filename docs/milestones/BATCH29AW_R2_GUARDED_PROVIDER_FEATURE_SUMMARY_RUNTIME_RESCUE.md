BATCH 29AW-R2 GUARDED PROVIDER-FEATURE SUMMARY RUNTIME RESCUE

generated_at_utc: 2026-05-02T07:37:04.933848+00:00
verdict: DEFERRED_29AW_R2_SUMMARY_NOT_FOUND_OR_INVALID_SHAPE
patched_file: bin/guarded_replay_engine_execute_dry_run_29g.py
runtime_patch_applied: True
guarded_retry_returncode: 0
provider_feature_summary_found: False
provider_feature_summary_path: None
provider_feature_field_count: 0
known_boolean_count: None
null_value_count: None
provider_summary_valid_shape: False
provider_feature_value_comparison_ready: False
full_live_replay_parity: NOT_PROVEN_IN_29AW_R2
repair_path: PROVIDER_FEATURE_SUMMARY_SHAPE_AUDIT_REQUIRED
next_batch: Batch 29AW-R3 — rescue provider-feature summary artifact emission/shape using exact 29AW-R2 outputs.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Files changed in this batch:
- bin/guarded_replay_engine_execute_dry_run_29g.py

Proofs:
- run/proofs/proof_guarded_provider_feature_summary_runtime_rescue_29aw_r2.json
- run/proofs/proof_guarded_provider_feature_summary_runtime_rescue_29aw_r2_latest.json
- run/proofs/batch29aw_r2_guarded_provider_feature_summary_runtime_rescue_20260502_130451_driver_proof.json
- etc/replay/parity/guarded_provider_feature_summary_runtime_rescue_29aw_r2.json
