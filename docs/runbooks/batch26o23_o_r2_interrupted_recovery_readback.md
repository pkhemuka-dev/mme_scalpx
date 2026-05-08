# 26-O23-O-R2 — interrupted O23-O-R1 recovery

- generated_at_utc: 2026-05-07T09:40:48.014818+00:00
- proof: `run/proofs/proof_batch26o23_o_r2_interrupted_recovery_readback.json`
- recovery: `run/live_capture/batch26o23_o_r2_interrupted_recovery_readback_20260507_151041/controlled_paper_o23o_r2_interruption_recovery.json`
- pid_readback: `run/live_capture/batch26o23_o_r2_interrupted_recovery_readback_20260507_151041/controlled_paper_o23o_r2_pid_readback.json`
- safety: `run/live_capture/batch26o23_o_r2_interrupted_recovery_readback_20260507_151041/controlled_paper_o23o_r2_safety_readback.json`
- interrupted_dir_review: `run/live_capture/batch26o23_o_r2_interrupted_recovery_readback_20260507_151041/controlled_paper_o23o_r2_interrupted_dir_review.json`
- next_decision: `run/live_capture/batch26o23_o_r2_interrupted_recovery_readback_20260507_151041/controlled_paper_o23o_r2_next_decision.json`

## Purpose
- Recover from system shutdown during O23-O-R1.
- Prove no leftover MME PIDs, zero orders, and FLAT/empty position.
- Do not start services.
- Do not patch source.
- Do not approve paper or real live.

## Result
- final_verdict: `PASS_O23_O_R2_INTERRUPTED_RECOVERY_CLEAN_OK_NO_START_NO_REAL_LIVE`
- classification: `POWER_LOSS_INTERRUPTED_O23O_R1_CLEAN_RECOVERY`
- false_keys: `[]`
- before_mme_pid_count: `0`
- cleanup_attempted_count: `0`
- after_no_mme_service_pids: `True`
- after_orders_zero: `True`
- after_position_flat: `True`
- next_recommended_batch: `26-O23-O-R3 clean rerun of live-session read-only family-surface sampler; feeds/features/strategy only; no paper; no real live.`

## Required verdicts
```json
{
  "after_no_mme_service_pids": true,
  "after_no_risk_execution_pids": true,
  "after_orders_zero": true,
  "after_position_flat": true,
  "after_snapshot_captured": true,
  "before_orders_zero": true,
  "before_position_flat": true,
  "before_snapshot_captured": true,
  "broker_call_false": true,
  "cleanup_allowed_if_pids_found": true,
  "compile_pass": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "interrupted_dir_review_json_written": true,
  "next_decision_json_written": true,
  "o23n_pass_loaded": true,
  "o23o_refused_on_pre_no_mme_service_pids": true,
  "o23or1_live_capture_dir_exists": true,
  "o23or1_proof_missing": true,
  "order_write_false": true,
  "paper_start_false": true,
  "pid_readback_json_written": true,
  "production_source_patch_false": true,
  "real_live_false": true,
  "recovery_json_written": true,
  "safety_json_written": true,
  "service_start_false": true,
  "threshold_relaxation_false": true
}
```