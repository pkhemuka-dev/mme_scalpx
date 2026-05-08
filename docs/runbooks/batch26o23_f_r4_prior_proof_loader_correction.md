# 26-O23-F-R4 — prior-proof loader correction / F-R3 equivalence

- generated_at_utc: 2026-05-07T08:10:48.646669+00:00
- proof: `run/proofs/proof_batch26o23_f_r4_prior_proof_loader_correction.json`
- corrected_equivalence: `run/live_capture/batch26o23_f_r4_prior_proof_loader_correction_20260507_133747/controlled_paper_o23f_r4_corrected_f_r3_equivalence.json`
- prior_loader: `run/live_capture/batch26o23_f_r4_prior_proof_loader_correction_20260507_133747/controlled_paper_o23f_r4_prior_loader_audit.json`
- next_decision: `run/live_capture/batch26o23_f_r4_prior_proof_loader_correction_20260507_133747/controlled_paper_o23f_r4_next_decision.json`
- backup_dir: `run/_code_backups/batch26o23_f_r4_prior_proof_loader_correction_20260507_133747`

## Purpose
- Correct O23-F-R3 prior-proof loader false negatives.
- Reuse F-R3 bridge audit artifacts.
- Do not start services, patch source, relax thresholds, force candidates, or approve real live.

## Corrected equivalence
```json
{
  "classification": "F_R3_EQUIVALENT_PASS_AFTER_PRIOR_PROOF_LOADER_CORRECTION",
  "corrected_false_keys": [],
  "f_r3_bridge_audit_preserved": {
    "classification": "MEMORY_SAFE_DATA_VALID_ACTIVATION_BRIDGE_AUDIT_RETRY_OK_NO_PATCH",
    "decision_nested_hits": [],
    "feature_nested_hits": [],
    "feature_payload_summary": [],
    "generated_at_utc": "2026-05-07T08:05:58.454218+00:00",
    "interpretation": [
      "This retry did not copy large historical evidence and did not deep-dump AST/source.",
      "Runtime remains safe: no orders, FLAT position, no controlled PIDs.",
      "The repeated controlled-paper symptom remains HOLD/no-candidate.",
      "The source contains the relevant bridge terms for data_valid, safe_to_consume, structural_valid, consumer_view/family features, and activation candidates.",
      "Next should be narrow diagnostic/repair only around features->strategy consumer-view bridge; no threshold relaxation and no forced candidate."
    ],
    "observed_decision_bridge": {
      "actions": [],
      "activation_candidate_count_values": [],
      "candidate_zero_or_empty": true,
      "data_valid_values": [],
      "data_valid_zero_observed": false,
      "decision_payload_count": 0,
      "hold_bridge_reason_observed": false,
      "reasons": [],
      "safe_to_consume_true_observed": false,
      "safe_to_consume_values": [],
      "safe_true_but_data_valid_zero_split": false,
      "structural_missing_or_false": true,
      "structural_valid_values": []
    },
    "patch_applied": false,
    "runtime_safety": {
      "no_controlled_pids": true,
      "orders_zero": true,
      "position_flat": true,
      "risk_execution_not_running": true
    },
    "source_bridge_summary": {
      "has_activation_candidate_count_terms": true,
      "has_consumer_view_terms": true,
      "has_data_valid_terms": true,
      "has_family_features_terms": true,
      "has_family_surfaces_terms": true,
      "has_hold_bridge_reason_terms": true,
      "has_mist_call_terms": true,
      "has_safe_to_consume_terms": true,
      "has_structural_valid_terms": true
    }
  },
  "f_r3_source_bridge_summary_preserved": {
    "has_activation_candidate_count_terms": true,
    "has_consumer_view_terms": true,
    "has_data_valid_terms": true,
    "has_family_features_terms": true,
    "has_family_surfaces_terms": true,
    "has_hold_bridge_reason_terms": true,
    "has_mist_call_terms": true,
    "has_safe_to_consume_terms": true,
    "has_structural_valid_terms": true
  },
  "generated_at_utc": "2026-05-07T08:10:48.645943+00:00",
  "loader_correction": {
    "corrected_o23d_pass": true,
    "corrected_o23e_pass": true,
    "o23d_final_verdict": "PASS_O23_D_SECOND_SESSION_EVIDENCE_REVIEW_OK_NO_REAL_LIVE",
    "o23e_final_verdict": "PASS_O23_E_NO_CANDIDATE_ROOT_CAUSE_REVIEW_OK_NO_REAL_LIVE",
    "old_failure": "O23-F-R3 failed only because O23-E and O23-D prior proof loader checks were false."
  },
  "original_f_r3_false_keys": [
    "o23e_pass_loaded",
    "o23d_pass_loaded"
  ],
  "original_f_r3_final_verdict": "FAIL_O23_F_R3_MEMORY_SAFE_BRIDGE_AUDIT_RETRY_NOT_PROVEN",
  "patch_applied": false,
  "real_live_approval": false,
  "runtime_safety_now": {
    "no_controlled_pids": true,
    "orders_zero": true,
    "position_flat": true,
    "risk_execution_not_running": true
  },
  "service_started": false
}
```

## Verdict
- final_verdict: `PASS_O23_F_R4_PRIOR_PROOF_LOADER_CORRECTION_OK_NO_REAL_LIVE`
- false_keys: `[]`
- next_recommended_batch: `26-O23-G narrow data_valid / consumer-view bridge diagnostic or repair, features/strategy only, no service start, no real live.`

## Required verdicts
```json
{
  "broker_call_false": true,
  "compile_pass": true,
  "corrected_equivalence_json_written": true,
  "disk_free_above_2gb": true,
  "f_r3_bridge_audit_present": true,
  "f_r3_failed_only_on_loader_keys": true,
  "f_r3_loaded": true,
  "f_r3_source_bridge_summary_present": true,
  "f_r3_source_has_activation_candidate_count_terms": true,
  "f_r3_source_has_consumer_view_terms": true,
  "f_r3_source_has_data_valid_terms": true,
  "f_r3_source_has_safe_to_consume_terms": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "no_controlled_pids_now": true,
  "no_full_evidence_copy_policy_followed": true,
  "o23b_r2_pass_loaded": true,
  "o23c_r1_pass_loaded": true,
  "o23d_pass_loaded_corrected": true,
  "o23e_pass_loaded_corrected": true,
  "o23f_r2_pass_loaded": true,
  "order_write_false": true,
  "orders_zero_now": true,
  "position_flat_now": true,
  "prior_loader_json_written": true,
  "production_source_patch_false": true,
  "real_live_approval_false": true,
  "risk_execution_not_running_now": true,
  "service_start_false": true,
  "threshold_relaxation_false": true
}
```