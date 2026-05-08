# 26-O23-O-R3 — clean rerun read-only family surface sampler

- generated_at_utc: 2026-05-07T09:48:56.494603+00:00
- proof: `run/proofs/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.json`
- session: `run/live_capture/batch26o23_o_r3_clean_rerun_readonly_sampler_20260507_151317/controlled_paper_o23o_r3_readonly_surface_session.json`
- sample_review: `run/live_capture/batch26o23_o_r3_clean_rerun_readonly_sampler_20260507_151317/controlled_paper_o23o_r3_sample_review.json`
- surface_matrix: `run/live_capture/batch26o23_o_r3_clean_rerun_readonly_sampler_20260507_151317/controlled_paper_o23o_r3_family_surface_matrix.json`
- safety: `run/live_capture/batch26o23_o_r3_clean_rerun_readonly_sampler_20260507_151317/controlled_paper_o23o_r3_safety_readback.json`
- log_review: `run/live_capture/batch26o23_o_r3_clean_rerun_readonly_sampler_20260507_151317/controlled_paper_o23o_r3_log_review.json`
- next_decision: `run/live_capture/batch26o23_o_r3_clean_rerun_readonly_sampler_20260507_151317/controlled_paper_o23o_r3_next_decision.json`

## Scope
- Clean rerun after O23-O-R2 recovery.
- Starts feeds/features/strategy only.
- Does not start risk or execution.
- Paper disabled.
- Real live false.
- No order write.
- No source patch.

## Result
- final_verdict: `FAIL_O23_O_R3_READONLY_SURFACE_SAMPLER_NOT_PROVEN`
- classification: `O23O_R3_NO_STREAM_GROWTH_DURING_READONLY_SAMPLER`
- false_keys: `['log_review_json_written']`
- feature_entries_since_start: `0`
- decision_entries_since_start: `0`
- feature_payload_count: `0`
- decision_payload_count: `0`
- best_evidence_backed_scope: `None`
- next_recommended_batch: `Inspect false_keys; do not start paper or real live.`

## Required verdicts
```json
{
  "broker_call_false": true,
  "broker_calls_forbidden": true,
  "compile_pass": true,
  "controlled_paper_runtime_disabled": true,
  "disk_free_above_min": true,
  "execution_disabled": true,
  "family_side_matrix_complete": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "live_orders_forbidden": true,
  "log_review_json_written": false,
  "next_decision_json_written": true,
  "no_forced_candidate": true,
  "no_order_events_since_start": true,
  "no_threshold_relaxation": true,
  "o23k_pass_loaded": true,
  "o23m_pass_loaded": true,
  "o23n_pass_loaded": true,
  "o23o_r2_pass_loaded": true,
  "observe_only_env": true,
  "order_intent_disabled": true,
  "order_write_false": true,
  "paper_disabled": true,
  "paper_start_false": true,
  "post_no_forbidden_risk_execution": true,
  "post_no_mme_service_pids": true,
  "post_position_flat": true,
  "pre_no_mme_service_pids": true,
  "pre_no_risk_execution_pids": true,
  "pre_orders_zero": true,
  "pre_position_flat": true,
  "production_source_patch_false": true,
  "readonly_services_started_alive": true,
  "real_live_false": true,
  "real_live_false_after": true,
  "safety_json_written": true,
  "sample_review_json_written": true,
  "samples_captured": true,
  "session_json_written": true,
  "surface_matrix_json_written": true,
  "threshold_relaxation_false": true
}
```