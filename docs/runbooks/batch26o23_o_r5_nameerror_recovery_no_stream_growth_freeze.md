# 26-O23-O-R5 — O23-O-R4 NameError recovery / O23-O-R3 no-stream-growth freeze

- generated_at_utc: 2026-05-07T09:54:19.696086+00:00
- proof: `run/proofs/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.json`
- r3_review: `run/live_capture/batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze_20260507_152417/controlled_paper_o23o_r5_o23o_r3_review.json`
- r4_review: `run/live_capture/batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze_20260507_152417/controlled_paper_o23o_r5_o23o_r4_nameerror_review.json`
- reconstructed_log_review: `run/live_capture/batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze_20260507_152417/controlled_paper_o23o_r5_reconstructed_log_review.json`
- no_stream_growth: `run/live_capture/batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze_20260507_152417/controlled_paper_o23o_r5_no_stream_growth_freeze.json`
- safety: `run/live_capture/batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze_20260507_152417/controlled_paper_o23o_r5_safety_readback.json`
- next_decision: `run/live_capture/batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze_20260507_152417/controlled_paper_o23o_r5_next_decision.json`

## Scope
- No service start.
- No paper start.
- No real live.
- No source patch.
- Recover O23-O-R4 script helper bug only in this proof script.
- Freeze O23-O-R3 substantive no-stream-growth result.

## Result
- final_verdict: `FAIL_O23_O_R5_NAMEERROR_RECOVERY_NOT_PROVEN`
- classification: `O23O_R5_NAMEERROR_RECOVERY_NOT_PROVEN`
- false_keys: `['safety_json_written']`
- r3_false_keys: `['log_review_json_written']`
- feature_entries_since_start: `0`
- decision_entries_since_start: `0`
- feature_payload_count: `0`
- decision_payload_count: `0`
- next_recommended_batch: `Inspect false_keys; do not start paper or real live.`

## Required verdicts
```json
{
  "broker_call_false": true,
  "compile_pass": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "no_stream_json_written": true,
  "o23n_pass_loaded": true,
  "o23o_r2_pass_loaded": true,
  "o23o_r3_failed_only_on_log_review_json_written": true,
  "o23o_r3_proof_exists": true,
  "o23o_r4_nameerror_classified": true,
  "o23o_r5_helper_defined": true,
  "order_write_false": true,
  "paper_start_false": true,
  "production_source_patch_false": true,
  "r3_no_payloads_confirmed": true,
  "r3_no_stream_growth_confirmed": true,
  "r3_review_json_written": true,
  "r3_safety_present": true,
  "r3_sample_review_present": true,
  "r3_surface_matrix_present": true,
  "r4_review_json_written": true,
  "real_live_false": true,
  "reconstructed_log_review_json_written": true,
  "runtime_no_mme_service_pids": true,
  "runtime_no_risk_execution_pids": true,
  "runtime_orders_zero": true,
  "runtime_position_flat": true,
  "safety_json_written": false,
  "service_start_false": true,
  "threshold_relaxation_false": true
}
```