BATCH 29AW REPLAY-ONLY GUARDED PROVIDER-FEATURE SUMMARY PATCH

generated_at_utc: 2026-05-02T07:25:00.754969+00:00
verdict: FAIL_29AW_GUARDED_DRY_RUN_OR_COMPILE_FAILED
patched_file: bin/guarded_replay_engine_execute_dry_run_29g.py
patch_applied: None
target_surface: guarded_replay_provider_feature_summary
target_artifact_name: 06_guarded_replay_provider_feature_summary.json
guarded_retry_returncode: 2
provider_feature_summary_found: False
provider_feature_field_count: None
known_boolean_count: None
null_value_count: None
provider_feature_value_comparison_ready: False
full_live_replay_parity: NOT_PROVEN_IN_29AW
repair_path: PATCH_RESCUE_REQUIRED
next_batch: Batch 29AW-R1 — rescue guarded script patch using backup and exact failure output.

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
- run/proofs/proof_replay_only_guarded_provider_feature_summary_patch_29aw.json
- run/proofs/proof_replay_only_guarded_provider_feature_summary_patch_29aw_latest.json
- run/proofs/batch29aw_replay_only_guarded_provider_feature_summary_patch_20260502_125500_driver_proof.json
- etc/replay/parity/replay_only_guarded_provider_feature_summary_patch_29aw.json
