BATCH 29AW-R6 POST-R5 EMISSION REACHABILITY / ARTIFACT AUDIT

generated_at_utc: 2026-05-02T07:52:57.645500+00:00
verdict: PASS_POST_R5_EMISSION_REACHABILITY_ARTIFACT_AUDIT_29AW_R6
guarded_retry_returncode_from_29aw_r5: 0
provider_feature_summary_found_from_29aw_r5: False
r5_output_artifact_target_count: 0
r5_marker_line: 862
prior_return_count_before_r5: 0
stdout_prints_before_r5_count: 1
reachability_classification: R5_EMIT_AFTER_EXECUTED_SUCCESS_PRINT_OR_RETURN
recommended_patch_path: MOVE_EMIT_IMMEDIATELY_BEFORE_SUCCESS_STDOUT_PRINT_OR_SUCCESS_RETURN
post_r5_audit_complete: True
full_live_replay_parity: NOT_PROVEN_IN_29AW_R6
repair_path: SUCCESS_STDOUT_PRINT_EMISSION_PATCH_READY
next_batch: Batch 29AW-R7 — patch replay-only guarded script to emit provider-feature summary immediately before the executed success stdout print/return.

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
- run/proofs/proof_post_r5_emission_reachability_artifact_audit_29aw_r6.json
- run/proofs/proof_post_r5_emission_reachability_artifact_audit_29aw_r6_latest.json
- run/proofs/batch29aw_r6_post_r5_emission_reachability_artifact_audit_20260502_132256_driver_proof.json
- etc/replay/parity/post_r5_emission_reachability_artifact_audit_29aw_r6.json
