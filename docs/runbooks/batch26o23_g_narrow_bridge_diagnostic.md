# 26-O23-G — narrow data_valid / consumer-view bridge diagnostic

- generated_at_utc: 2026-05-07T08:36:06.390688+00:00
- proof: `run/proofs/proof_batch26o23_g_narrow_bridge_diagnostic.json`
- bridge_diagnostic: `run/live_capture/batch26o23_g_narrow_bridge_diagnostic_20260507_140257/controlled_paper_o23g_bridge_diagnostic.json`
- source_seams: `run/live_capture/batch26o23_g_narrow_bridge_diagnostic_20260507_140257/controlled_paper_o23g_source_seams.json`
- patch_plan: `run/live_capture/batch26o23_g_narrow_bridge_diagnostic_20260507_140257/controlled_paper_o23g_patch_plan_if_proven.json`
- next_decision: `run/live_capture/batch26o23_g_narrow_bridge_diagnostic_20260507_140257/controlled_paper_o23g_next_decision.json`
- backup_dir: `run/_code_backups/batch26o23_g_narrow_bridge_diagnostic_20260507_140257`

## Purpose
- Locate the exact features/strategy bridge seam causing HOLD/no-candidate.
- No patch in this batch.
- No service start.
- No real live.
- No threshold relaxation or forced candidate.

## Bridge diagnostic
```json
{
  "classification": "NARROW_FEATURES_STRATEGY_BRIDGE_SEAM_IDENTIFIED",
  "confidence": "MEDIUM_HIGH",
  "generated_at_utc": "2026-05-07T08:36:06.389906+00:00",
  "likely_factors": [
    "features_and_strategy_have_consumer_view_bridge_with_hold_reason",
    "data_valid_is_produced_and_consumed_in_features_strategy",
    "strategy_has_candidate_count_surface",
    "recent_feature_payload_unparseable_or_not_present_in_latest_slice",
    "runtime_payload_contains_validity_split_surface"
  ],
  "patch_applied": false,
  "prior_f_r3_status": {
    "false_keys": [
      "o23e_pass_loaded",
      "o23d_pass_loaded"
    ],
    "final_verdict": "FAIL_O23_F_R3_MEMORY_SAFE_BRIDGE_AUDIT_RETRY_NOT_PROVEN"
  },
  "prior_f_r4_status": {
    "false_keys": [],
    "final_verdict": "PASS_O23_F_R4_PRIOR_PROOF_LOADER_CORRECTION_OK_NO_REAL_LIVE"
  },
  "real_live_approval": false,
  "runtime_presence": {
    "runtime_decision_consumer_view": true,
    "runtime_decision_data_valid": true,
    "runtime_has_decision_payload": false,
    "runtime_has_feature_payload": false,
    "runtime_has_safe_to_consume": true,
    "runtime_has_structural_valid": true
  },
  "runtime_safety": {
    "no_controlled_pids": true,
    "orders_zero": true,
    "position_flat": true,
    "risk_execution_not_running": true
  },
  "service_started": false,
  "source_presence": {
    "source_has_feature_data_valid": true,
    "source_has_features_consumer_view": true,
    "source_has_strategy_bridge_reason": true,
    "source_has_strategy_candidate_count": true,
    "source_has_strategy_consumer_view": true,
    "source_has_strategy_data_valid": true
  }
}
```

## Patch plan if proven
```json
{
  "allowed_files_if_next_patch_needed": [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py"
  ],
  "batch": "26-O23-G",
  "candidate_next_repair": [
    "If strategy consumes a top-level data_valid while features publishes valid consumer_view.data_valid, normalize strategy consumer-view extraction.",
    "If features publishes consumer_view_json but strategy expects consumer_view dict, add bounded parse/bridge in strategy only.",
    "If structural_valid is computed but not surfaced to decision payload, propagate without changing thresholds.",
    "If activation_candidate_count is zero because branch frames are unparseable, repair branch-frame parse/shape only."
  ],
  "confidence": "MEDIUM_HIGH",
  "forbidden_files_for_next_patch_without_new_evidence": [
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py"
  ],
  "generated_at_utc": "2026-05-07T08:36:06.390320+00:00",
  "repair_principles": [
    "Do not relax strategy thresholds.",
    "Do not force candidate creation.",
    "Do not change MIST/MISB/MISC/MISR/MISO doctrine.",
    "Do not start services during patch proof.",
    "Repair only proven serialization/consumer-view/validity propagation gap.",
    "Preserve HOLD/fail-closed behavior when consumer view is absent or invalid."
  ],
  "repair_readiness": "NARROW_FEATURES_STRATEGY_BRIDGE_SEAM_IDENTIFIED",
  "status": "PATCH_PLAN_ONLY_NO_SOURCE_MUTATION"
}
```

## Verdict
- final_verdict: `PASS_O23_G_NARROW_BRIDGE_DIAGNOSTIC_OK_NO_PATCH_NO_REAL_LIVE`
- false_keys: `[]`
- next_recommended_batch: `26-O23-H narrow data_valid / consumer-view bridge repair, features/strategy only, no service start, no real live.`

## Required verdicts
```json
{
  "bridge_diagnostic_json_written": true,
  "broker_call_false": true,
  "compile_pass": true,
  "diagnostic_confidence_not_low": true,
  "f_r3_loaded": true,
  "f_r4_pass_loaded": true,
  "features_py_scanned": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "no_controlled_pids_now": true,
  "order_write_false": true,
  "orders_zero_now": true,
  "patch_plan_json_written": true,
  "position_flat_now": true,
  "production_source_patch_false": true,
  "real_live_approval_false": true,
  "risk_execution_not_running_now": true,
  "service_start_false": true,
  "source_has_feature_data_valid": true,
  "source_has_features_consumer_view": true,
  "source_has_strategy_bridge_reason": true,
  "source_has_strategy_candidate_count": true,
  "source_has_strategy_consumer_view": true,
  "source_has_strategy_data_valid": true,
  "source_seams_json_written": true,
  "strategy_py_scanned": true,
  "threshold_relaxation_false": true
}
```