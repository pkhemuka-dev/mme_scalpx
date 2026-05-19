# A6-FEED-R5AT-R5_current_runtime_truth_static_closure_after_r5at_chain_no_patch_no_restart_no_order_no_paper_20260517_161801 Current Runtime Truth Closure

Batch: A6-FEED-R5AT-R5

Verdict: FAIL_A6_FEED_R5AT_R5_CURRENT_RUNTIME_TRUTH_CLOSURE_CHECK

Safety: after-market read-only runtime truth closure only; no patch, no restore, no service start/restart/stop, no Redis write, no paper/live, no broker/order, no risk/execution.

Classification:

```json
{
  "decisions_stream_age_ms": 1126406427,
  "decisions_stream_xlen": 1682,
  "features_stream_age_ms": 1126680601,
  "features_stream_xlen": 4220,
  "likely_condition": "CURRENT_RUNTIME_TRUTH_CLOSURE_INCOMPLETE",
  "next_action": "Stop and review proof. No restart/paper/live.",
  "r5at_r3_final_verdict": "FAIL_A6_FEED_R5AT_R3_RUNTIME_STATIC_CLOSURE_CHECK",
  "r5at_r3_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AT-R3_corrected_aftermarket_runtime_payload_static_closure_after_r5at_noop_no_patch_no_restart_no_order_no_paper_20260517_161523.json",
  "r5at_r4_failures": [
    "r5at_r3_failed_only_stale_precondition"
  ],
  "r5at_r4_final_verdict": "FAIL_A6_FEED_R5AT_R4_RUNTIME_VALIDATION_ACCEPTANCE_CHECK",
  "r5at_r4_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AT-R4_corrected_accept_runtime_payload_validation_closure_after_stale_r5at_precondition_no_patch_no_restart_no_order_no_paper_20260517_161646.json",
  "r5at_r4_runtime_payload_validation_ok": null,
  "runtime_probe": {
    "ok": true,
    "parsed": {
      "contracts_file": "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py",
      "ok": true,
      "payload_stage_flags_count": 15,
      "payload_stage_flags_extra_vs_contract": [],
      "payload_stage_flags_has_tradability": true,
      "payload_stage_flags_keys": [
        "active_position_present",
        "call_present",
        "data_quality_ok",
        "data_valid",
        "dhan_context_fresh",
        "futures_present",
        "provider_ready_classic",
        "provider_ready_miso",
        "put_present",
        "reconciliation_lock_active",
        "risk_veto_active",
        "selected_option_present",
        "session_eligible",
        "tradability_ok",
        "warmup_complete"
      ],
      "payload_stage_flags_missing_vs_contract": [],
      "payload_stage_flags_tradability_value": false,
      "payload_validation_error": null,
      "payload_validation_ok": true,
      "stage_flag_keys": [
        "data_valid",
        "data_quality_ok",
        "session_eligible",
        "warmup_complete",
        "tradability_ok",
        "risk_veto_active",
        "reconciliation_lock_active",
        "active_position_present",
        "provider_ready_classic",
        "provider_ready_miso",
        "dhan_context_fresh",
        "selected_option_present",
        "futures_present",
        "call_present",
        "put_present"
      ],
      "stage_flag_keys_count": 15,
      "stage_flag_keys_has_tradability": true,
      "stage_flag_keys_tradability_count": 1,
      "stage_flag_keys_unique_count": 15,
      "strategy_file": "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py"
    },
    "rc": 0,
    "stderr_tail": "",
    "stdout_tail": "{\"contracts_file\": \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", \"ok\": true, \"payload_stage_flags_count\": 15, \"payload_stage_flags_extra_vs_contract\": [], \"payload_stage_flags_has_tradability\": true, \"payload_stage_flags_keys\": [\"active_position_present\", \"call_present\", \"data_quality_ok\", \"data_valid\", \"dhan_context_fresh\", \"futures_present\", \"provider_ready_classic\", \"provider_ready_miso\", \"put_present\", \"reconciliation_lock_active\", \"risk_veto_active\", \"selected_option_present\", \"session_eligible\", \"tradability_ok\", \"warmup_complete\"], \"payload_stage_flags_missing_vs_contract\": [], \"payload_stage_flags_tradability_value\": false, \"payload_validation_error\": null, \"payload_validation_ok\": true, \"stage_flag_keys\": [\"data_valid\", \"data_quality_ok\", \"session_eligible\", \"warmup_complete\", \"tradability_ok\", \"risk_veto_active\", \"reconciliation_lock_active\", \"active_position_present\", \"provider_ready_classic\", \"provider_ready_miso\", \"dhan_context_fresh\", \"selected_option_present\", \"futures_present\", \"call_present\", \"put_present\"], \"stage_flag_keys_count\": 15, \"stage_flag_keys_has_tradability\": true, \"stage_flag_keys_tradability_count\": 1, \"stage_flag_keys_unique_count\": 15, \"strategy_file\": \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\"}"
  },
  "services": []
}
```

Required checks:

```json
{
  "all_feature_family_sources_compile": true,
  "all_watched_sources_compile": true,
  "current_payload_stage_flags_has_tradability": true,
  "current_payload_stage_flags_no_missing_vs_contract": true,
  "current_payload_stage_flags_tradability_false": true,
  "current_payload_validation_ok": true,
  "current_runtime_probe_ok": true,
  "current_stage_flag_keys_has_tradability_once": true,
  "current_stage_flag_keys_unique": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "prior_r5at_r4_found_with_good_runtime_evidence": false,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[
  "prior_r5at_r4_found_with_good_runtime_evidence"
]
```

Conclusion:
- This closes the R5AT contract payload chain only if PASS.
- It is still after-market static closure, not live readiness.
