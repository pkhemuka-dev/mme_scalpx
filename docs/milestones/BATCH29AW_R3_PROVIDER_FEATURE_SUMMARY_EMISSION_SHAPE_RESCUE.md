BATCH 29AW-R3 PROVIDER-FEATURE SUMMARY EMISSION SHAPE RESCUE

generated_at_utc: 2026-05-02T07:40:41.585517+00:00
verdict: DEFERRED_29AW_R3_SUMMARY_STILL_NOT_FOUND_OR_INVALID_SHAPE
patched_file: bin/guarded_replay_engine_execute_dry_run_29g.py
emission_shape_patch_applied: True
guarded_retry_returncode: 0
provider_feature_summary_found: False
provider_feature_summary_path: None
provider_feature_field_count: 0
known_boolean_count: None
null_value_count: None
provider_summary_valid_shape: False
provider_feature_value_comparison_ready: False
full_live_replay_parity: NOT_PROVEN_IN_29AW_R3
repair_path: PROVIDER_FEATURE_SUMMARY_EMISSION_ARTIFACT_AUDIT_REQUIRED
next_batch: Batch 29AW-R4 — audit exact patched script emission location and provider summary payload.

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
- run/proofs/proof_provider_feature_summary_emission_shape_rescue_29aw_r3.json
- run/proofs/proof_provider_feature_summary_emission_shape_rescue_29aw_r3_latest.json
- run/proofs/batch29aw_r3_provider_feature_summary_emission_shape_rescue_20260502_131040_driver_proof.json
- etc/replay/parity/provider_feature_summary_emission_shape_rescue_29aw_r3.json
