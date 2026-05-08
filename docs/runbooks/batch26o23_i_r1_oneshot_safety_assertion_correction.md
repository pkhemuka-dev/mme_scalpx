# 26-O23-I-R1 — one-shot safety assertion correction

- generated_at_utc: 2026-05-07T08:51:24.794679+00:00
- proof: `run/proofs/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json`
- correction: `run/live_capture/batch26o23_i_r1_oneshot_safety_assertion_correction_20260507_142123/controlled_paper_o23i_r1_corrected_oneshot_safety.json`
- scenario_review: `run/live_capture/batch26o23_i_r1_oneshot_safety_assertion_correction_20260507_142123/controlled_paper_o23i_r1_scenario_review.json`
- next_decision: `run/live_capture/batch26o23_i_r1_oneshot_safety_assertion_correction_20260507_142123/controlled_paper_o23i_r1_next_decision.json`
- backup_dir: `run/_code_backups/batch26o23_i_r1_oneshot_safety_assertion_correction_20260507_142123`

## Purpose
- Correct O23-I false-negative safety assertion.
- Preserve O23-H source exactly; no source patch in this batch.
- Do not start services.
- Do not approve real live.

## Corrected safety law
- Unsafe means the helper creates a positive candidate from zero/empty, or increases activation_candidate_count.
- Preserving an unchanged existing BUY candidate is not candidate creation.

## Correction record
```json
{
  "batch": "26-O23-I-R1",
  "classification": "O23I_FALSE_NEGATIVE_ASSERTION_CORRECTED",
  "corrected_candidate_safety": {
    "corrected_no_positive_candidate_created": true,
    "definition": "PASS means the helper did not increase activation_candidate_count and did not turn zero/empty candidate count into positive. Preserving an unchanged existing BUY candidate is allowed.",
    "scenario_reviews": [
      {
        "changed_buy_entry_action": false,
        "corrected_no_candidate_creation_or_increase": true,
        "created_positive_from_zero": false,
        "increased_candidate_count": false,
        "input_action": "HOLD",
        "input_candidate_count": 0,
        "input_candidate_count_norm": 0,
        "name": "valid_consumer_view_bridge_hold_no_candidate_promotes_validity_only",
        "output_action": "HOLD",
        "output_candidate_count": 0,
        "output_candidate_count_norm": 0,
        "scenario_ok": true
      },
      {
        "changed_buy_entry_action": false,
        "corrected_no_candidate_creation_or_increase": true,
        "created_positive_from_zero": false,
        "increased_candidate_count": false,
        "input_action": "HOLD",
        "input_candidate_count": 0,
        "input_candidate_count_norm": 0,
        "name": "invalid_consumer_view_does_not_promote",
        "output_action": "HOLD",
        "output_candidate_count": 0,
        "output_candidate_count_norm": 0,
        "scenario_ok": true
      },
      {
        "changed_buy_entry_action": false,
        "corrected_no_candidate_creation_or_increase": true,
        "created_positive_from_zero": false,
        "increased_candidate_count": false,
        "input_action": "HOLD",
        "input_candidate_count": 0,
        "input_candidate_count_norm": 0,
        "name": "non_bridge_reason_unchanged",
        "output_action": "HOLD",
        "output_candidate_count": 0,
        "output_candidate_count_norm": 0,
        "scenario_ok": true
      },
      {
        "changed_buy_entry_action": false,
        "corrected_no_candidate_creation_or_increase": true,
        "created_positive_from_zero": false,
        "increased_candidate_count": false,
        "input_action": "BUY",
        "input_candidate_count": 1,
        "input_candidate_count_norm": 1,
        "name": "entry_action_never_modified",
        "output_action": "BUY",
        "output_candidate_count": 1,
        "output_candidate_count_norm": 1,
        "scenario_ok": true
      },
      {
        "changed_buy_entry_action": false,
        "corrected_no_candidate_creation_or_increase": true,
        "created_positive_from_zero": false,
        "increased_candidate_count": false,
        "input_action": "HOLD",
        "input_candidate_count": "0",
        "input_candidate_count_norm": 0,
        "name": "json_encoded_consumer_view_supported",
        "output_action": "HOLD",
        "output_candidate_count": 0,
        "output_candidate_count_norm": 0,
        "scenario_ok": true
      }
    ]
  },
  "corrected_interpretation": [
    "O23-I helper matrix passed all scenarios.",
    "The failed key treated an unchanged BUY scenario with pre-existing activation_candidate_count=1 as positive candidate creation.",
    "Correct safety law is no creation and no increase of candidate count.",
    "Under corrected law, preserving an existing unchanged BUY candidate is safe and not candidate creation."
  ],
  "generated_at_utc": "2026-05-07T08:51:24.778162+00:00",
  "original_all_helpers_present": true,
  "original_all_scenarios_passed": true,
  "original_o23i_false_keys": [
    "oneshot_no_positive_candidate_created"
  ],
  "original_o23i_final_verdict": "FAIL_O23_I_STATIC_ONESHOT_BRIDGE_PROOF_NOT_PROVEN",
  "real_live_approval": false,
  "service_started": false,
  "source_patch_applied": false
}
```

## Verdict
- final_verdict: `PASS_O23_I_R1_ONESHOT_SAFETY_ASSERTION_CORRECTION_OK_NO_START_NO_REAL_LIVE`
- false_keys: `[]`
- next_recommended_batch: `STOP unless user explicitly approves O23-J post-repair bounded controlled-paper observation.`

## Required verdicts
```json
{
  "all_corrected_scenario_rows_present": true,
  "broker_call_false": true,
  "compile_pass": true,
  "corrected_no_positive_candidate_created": true,
  "correction_json_written": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "no_controlled_pids_now": true,
  "o23h_pass_loaded": true,
  "o23i_failed_only_on_false_negative_assertion": true,
  "oneshot_all_helpers_present": true,
  "oneshot_all_scenarios_passed": true,
  "oneshot_artifact_found": true,
  "order_write_false": true,
  "orders_zero_now": true,
  "original_o23i_static_required_keys_ok_except_false_assertion": true,
  "position_flat_now": true,
  "production_source_patch_false": true,
  "real_live_approval_false": true,
  "risk_execution_not_running_now": true,
  "scenario_review_json_written": true,
  "service_start_false": true,
  "threshold_relaxation_false": true
}
```