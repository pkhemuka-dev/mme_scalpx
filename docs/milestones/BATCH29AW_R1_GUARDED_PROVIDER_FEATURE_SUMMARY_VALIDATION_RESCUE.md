BATCH 29AW-R1 GUARDED PROVIDER-FEATURE SUMMARY VALIDATION RESCUE

generated_at_utc: 2026-05-02T07:31:46.998376+00:00
verdict: FAIL_29AW_R1_GUARDED_VALIDATION_RUNTIME_FAILED
patched_file: bin/guarded_replay_engine_execute_dry_run_29g.py
patch_marker_present: True
call_marker_present: True
recovered_cli_args_complete: True
guarded_retry_returncode: 1
provider_feature_summary_found: False
provider_feature_summary_path: None
provider_feature_field_count: 0
known_boolean_count: None
null_value_count: None
provider_summary_valid_shape: False
provider_feature_value_comparison_ready: False
full_live_replay_parity: NOT_PROVEN_IN_29AW_R1
repair_path: PATCH_RUNTIME_RESCUE_REQUIRED
next_batch: Batch 29AW-R2 — rescue guarded script patch using exact runtime stderr/stdout and 29AW backup.

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
- run/proofs/proof_guarded_provider_feature_summary_validation_rescue_29aw_r1.json
- run/proofs/proof_guarded_provider_feature_summary_validation_rescue_29aw_r1_latest.json
- run/proofs/batch29aw_r1_guarded_provider_feature_summary_validation_rescue_20260502_125719_driver_proof.json
- etc/replay/parity/guarded_provider_feature_summary_validation_rescue_29aw_r1.json
