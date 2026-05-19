# A6-FEED-R5Q-R2_corrected_read_only_extended_feed_feature_decision_readiness_consolidation_fixed_redaction_no_patch_no_restart_no_order_no_paper_20260515_095822

Batch: A6-FEED-R5Q-R2

Purpose: corrected_read_only_extended_feed_feature_decision_readiness_consolidation_fixed_redaction_no_patch_no_restart_no_order_no_paper

Final verdict: FAIL_A6_FEED_R5Q_R2_SAFETY_OR_PRECONDITION_CHECK

Safety: corrected read-only extended readiness consolidation only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "likely_condition": "A6_FEED_CONSOLIDATION_SAFETY_OR_PRECONDITION_FAILED",
  "next_action": "Stop and review proof.",
  "prior_r5q_failure_classification": "tooling_redaction_regex_failure_not_source_failure",
  "r5o_final_verdict": "PASS_A6_FEED_R5O_EXACT_RISK_EXECUTION_DIRTY_OWNERSHIP_EXTRACTED_NO_PATCH_NO_RESTORE_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5o_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5O_read_only_exact_risk_execution_dirty_ownership_artifact_and_diff_extraction_no_patch_no_restore_no_restart_no_order_no_paper_20260513_152645.json",
  "r5o_risk_has_a6_artifacts": null,
  "r5o_risk_has_other_lane_artifacts": null,
  "r5p_final_verdict": "PASS_A6_FEED_R5P_DECISIONS_PRODUCER_BLOCKER_INSPECTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5p_likely_condition": "FEATURES_AND_DECISIONS_PRESENT",
  "r5p_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5P_read_only_decisions_producer_blocker_inspection_after_expected_a6_dirty_state_no_patch_no_restore_no_restart_no_order_no_paper_20260514_134031.json",
  "readiness_failures": [
    "decisions_stream_recent"
  ],
  "safety_failures": [
    "r5o_risk_dirty_a6_owned_no_other_lane"
  ],
  "standard_services_post": [],
  "standard_services_pre": [],
  "stream_growth": {
    "decisions:mme:stream": {
      "after": 1684,
      "before": 1684,
      "delta": 0
    },
    "features:mme:stream": {
      "after": 4262,
      "before": 4258,
      "delta": 4
    },
    "orders:mme:stream": {
      "after": null,
      "before": null,
      "delta": null
    },
    "system:errors:stream": {
      "after": 10024,
      "before": 10000,
      "delta": 24
    },
    "system:health:stream": {
      "after": 5276,
      "before": 5186,
      "delta": 90
    },
    "ticks:mme:fut:dhan:stream": {
      "after": 24,
      "before": 22,
      "delta": 2
    },
    "ticks:mme:fut:zerodha:stream": {
      "after": 55,
      "before": 49,
      "delta": 6
    },
    "ticks:mme:opt:context:dhan:stream": {
      "after": 114,
      "before": 102,
      "delta": 12
    },
    "ticks:mme:opt:selected:dhan:stream": {
      "after": 98,
      "before": 88,
      "delta": 10
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "after": 238,
      "before": 218,
      "delta": 20
    }
  }
}
```

Readiness checks:

```json
{
  "decisions_stream_present": true,
  "decisions_stream_recent": false,
  "dhan_option_context_stream_present": true,
  "dhan_option_context_stream_recent": true,
  "features_stream_present": true,
  "features_stream_recent": true,
  "futures_feed_present_any_provider": true,
  "futures_feed_recent_any_provider": true,
  "selected_option_feed_present_any_provider": true,
  "selected_option_feed_recent_any_provider": true
}
```

Readiness failures:

```json
[
  "decisions_stream_recent"
]
```

Required safety/precondition checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5o_proof_found": true,
  "latest_r5p_proof_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible_post": true,
  "no_risk_execution_order_process_visible_pre": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent_post": true,
  "orders_mme_stream_zero_or_absent_pre": true,
  "position_flat_post": true,
  "position_flat_pre": true,
  "prior_r5q_failed_as_tooling_redaction_error": true,
  "r5o_risk_dirty_a6_owned_no_other_lane": false,
  "r5p_features_and_decisions_present": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Safety/precondition failures:

```json
[
  "r5o_risk_dirty_a6_owned_no_other_lane"
]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5Q-R2_corrected_read_only_extended_feed_feature_decision_readiness_consolidation_fixed_redaction_no_patch_no_restart_no_order_no_paper_20260515_095822.json
