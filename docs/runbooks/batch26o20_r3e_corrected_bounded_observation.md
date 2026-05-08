# 26-O20-R3E — corrected bounded observation after source-level validity repair

- generated_at_utc: 2026-05-06T05:39:42.063675+00:00
- tag: `batch26o20_r3e_corrected_bounded_observation_20260506_110807`
- proof: `run/proofs/proof_batch26o20_r3e_corrected_bounded_observation.json`
- manifest: `run/proofs/manifest_batch26o20_r3e_corrected_bounded_observation.json`
- backup_dir: `run/_code_backups/batch26o20_r3e_corrected_bounded_observation_20260506_110807`

## Safety boundary
- No real-live enablement.
- No paper restart.
- No broker call.
- No order write.
- No threshold relaxation.
- No forced candidate.
- Risk/execution not started.
- Any features probe started by this package is stopped at the end.

## Verdict
- final_verdict: `FAIL_O20_R3E_CORRECTED_BOUNDED_OBSERVATION_NOT_PROVEN`
- false_keys: `['consumer_view_data_valid_in_samples', 'consumer_view_safe_to_consume_in_samples', 'consumer_view_structural_valid_in_samples', 'payload_structural_valid_in_samples', 'top_structural_valid_in_samples', 'all_10_branch_frames_in_samples', 'mist_call_visible_in_samples']`
- next_recommended_batch: `Inspect false_keys and write smallest Lane-A diagnostic/repair package only; do not jump lanes`

## Required checks
```json
{
  "all_10_branch_frames_in_samples": false,
  "compile_before_pass": true,
  "consumer_view_data_valid_in_samples": false,
  "consumer_view_safe_to_consume_in_samples": false,
  "consumer_view_structural_valid_in_samples": false,
  "decisions_hold_only": true,
  "decisions_present": true,
  "execution_not_running_after": true,
  "feature_stream_grew_or_available": true,
  "features_present_in_samples": true,
  "import_before_pass": true,
  "latest_orders_empty": true,
  "mist_call_visible_in_samples": false,
  "no_broker_call": true,
  "no_forced_candidate": true,
  "no_order_write_intent": true,
  "no_paper_start": true,
  "no_promoted_branch": true,
  "no_threshold_relaxation": true,
  "orders_zero": true,
  "payload_structural_valid_in_samples": false,
  "position_flat": true,
  "prior_r2b_pass": true,
  "real_live_false": true,
  "risk_not_running_after": true,
  "sample_count_reached": true,
  "started_features_stopped_after_probe": true,
  "strategy_hold_only_no_candidate": true,
  "strategy_one_shot_attempted": true,
  "strategy_one_shot_ok_or_decision_available": true,
  "top_structural_valid_in_samples": false
}
```
