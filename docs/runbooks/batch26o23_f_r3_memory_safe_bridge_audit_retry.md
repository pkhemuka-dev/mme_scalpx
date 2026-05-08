# 26-O23-F-R3 — memory-safe bridge audit retry

- generated_at_utc: 2026-05-07T08:05:58.454662+00:00
- proof: `run/proofs/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json`
- bridge_audit: `run/live_capture/batch26o23_f_r3_memory_safe_bridge_audit_retry_20260507_133326/controlled_paper_o23f_r3_bridge_audit.json`
- source_slices: `run/live_capture/batch26o23_f_r3_memory_safe_bridge_audit_retry_20260507_133326/controlled_paper_o23f_r3_source_slices.json`
- runtime_slice: `run/live_capture/batch26o23_f_r3_memory_safe_bridge_audit_retry_20260507_133326/controlled_paper_o23f_r3_runtime_slice.json`
- next_decision: `run/live_capture/batch26o23_f_r3_memory_safe_bridge_audit_retry_20260507_133326/controlled_paper_o23f_r3_next_decision.json`
- backup_dir: `run/_code_backups/batch26o23_f_r3_memory_safe_bridge_audit_retry_20260507_133326`

## Purpose
- Retry O23-F after O23-F-R2 disk recovery.
- Use hash/slice backup policy only.
- Audit data_valid / safe_to_consume / structural_valid / consumer_view / activation_candidate bridge.
- No service start, no source patch, no order write, no real live.

## Bridge audit
```json
{
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
}
```

## Verdict
- final_verdict: `FAIL_O23_F_R3_MEMORY_SAFE_BRIDGE_AUDIT_RETRY_NOT_PROVEN`
- false_keys: `['o23e_pass_loaded', 'o23d_pass_loaded']`
- next_recommended_batch: `Inspect false_keys; no controlled-paper restart.`

## Required verdicts
```json
{
  "bridge_audit_json_written": true,
  "broker_call_false": true,
  "compile_pass": true,
  "disk_free_above_min": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "no_controlled_pids_now": true,
  "no_full_evidence_copy_policy_followed": true,
  "o23d_pass_loaded": false,
  "o23e_pass_loaded": false,
  "o23f_r2_pass_loaded": true,
  "order_write_false": true,
  "orders_zero_now": true,
  "position_flat_now": true,
  "production_source_patch_false": true,
  "real_live_approval_false": true,
  "risk_execution_not_running_now": true,
  "runtime_slice_written": true,
  "service_start_false": true,
  "source_has_activation_candidate_count_terms": true,
  "source_has_consumer_view_terms": true,
  "source_has_data_valid_terms": true,
  "source_has_safe_to_consume_terms": true,
  "source_slice_written": true,
  "threshold_relaxation_false": true
}
```