BATCH 29AW-R5 MOVE PROVIDER-FEATURE EMIT BEFORE RETURN

generated_at_utc: 2026-05-02T07:47:38.979904+00:00
verdict: DEFERRED_29AW_R5_SUMMARY_STILL_NOT_FOUND_OR_INVALID_SHAPE
patched_file: bin/guarded_replay_engine_execute_dry_run_29g.py
move_emit_patch_applied: True
guarded_retry_returncode: 0
provider_feature_summary_found: False
provider_feature_summary_path: None
provider_feature_field_count: 0
known_boolean_count: None
null_value_count: None
provider_summary_valid_shape: False
provider_feature_value_comparison_ready: False
full_live_replay_parity: NOT_PROVEN_IN_29AW_R5
repair_path: PROVIDER_FEATURE_SUMMARY_EMISSION_REACHABILITY_AUDIT_REQUIRED
next_batch: Batch 29AW-R6 — audit exact post-R5 emission reachability and artifact path.

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
- run/proofs/proof_move_provider_feature_emit_before_return_29aw_r5.json
- run/proofs/proof_move_provider_feature_emit_before_return_29aw_r5_latest.json
- run/proofs/batch29aw_r5_move_provider_feature_emit_before_return_20260502_131501_driver_proof.json
- etc/replay/parity/move_provider_feature_emit_before_return_29aw_r5.json
