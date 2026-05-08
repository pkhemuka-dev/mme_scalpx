BATCH 29AW-R8 POST-R7 EMISSION OUTPUT-ROOT AUDIT

generated_at_utc: 2026-05-02T08:00:12.629044+00:00
verdict: PASS_POST_R7_EMISSION_OUTPUT_ROOT_AUDIT_29AW_R8
guarded_retry_returncode_from_29aw_r7: 0
provider_feature_summary_found_from_29aw_r7: False
r7_output_artifact_target_count: 0
global_target_artifact_hit_count: 0
r7_marker_count: 1
success_print_count: 1
failure_classification: EMIT_BLOCK_PRESENT_BUT_HELPER_NOT_WRITING_OR_OUTPUT_ROOT_WRONG
repair_path: INSTRUMENT_HELPER_RESULT_AND_FORCE_OUTPUT_ROOT_READY
post_r7_audit_complete: True
full_live_replay_parity: NOT_PROVEN_IN_29AW_R8
next_batch: Batch 29AW-R9 — patch replay-only guarded script to include provider-feature summary path in stdout result and force write under args.output_root.

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
- run/proofs/proof_post_r7_emission_output_root_audit_29aw_r8.json
- run/proofs/proof_post_r7_emission_output_root_audit_29aw_r8_latest.json
- run/proofs/batch29aw_r8_post_r7_emission_output_root_audit_20260502_132932_driver_proof.json
- etc/replay/parity/post_r7_emission_output_root_audit_29aw_r8.json
