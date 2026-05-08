BATCH 29AW-R4 PROVIDER-FEATURE EMISSION LOCATION AUDIT

generated_at_utc: 2026-05-02T07:42:49.117620+00:00
verdict: PASS_PROVIDER_FEATURE_EMISSION_LOCATION_AUDIT_29AW_R4
guarded_retry_returncode_from_29aw_r3: 0
provider_feature_summary_found_from_29aw_r3: False
r3_output_artifact_target_count: 0
call_marker_line: 518
call_enclosing_function: main
reachability_confidence: CALL_MAY_BE_AFTER_PRIOR_RETURN_OR_IN_UNREACHED_BRANCH
recommended_patch_path: MOVE_PROVIDER_FEATURE_EMIT_BEFORE_FINAL_RETURN_IN_MAIN_GUARDED_PATH
producer_consumer_audit_complete: True
full_live_replay_parity: NOT_PROVEN_IN_29AW_R4
repair_path: MOVE_EMISSION_CALL_BEFORE_RETURN_READY
next_batch: Batch 29AW-R5 — patch replay-only guarded script by moving provider-feature emission before final return/print path.

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
- run/proofs/proof_provider_feature_emission_location_audit_29aw_r4.json
- run/proofs/proof_provider_feature_emission_location_audit_29aw_r4_latest.json
- run/proofs/batch29aw_r4_provider_feature_emission_location_audit_20260502_131248_driver_proof.json
- etc/replay/parity/provider_feature_emission_location_audit_29aw_r4.json
