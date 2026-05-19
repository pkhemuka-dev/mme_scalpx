# A6-FEED-R5Q-R3_corrected_read_only_extended_readiness_classify_dhan_context_and_stale_decisions_no_patch_no_restart_no_order_no_paper_20260515_100117

Batch: A6-FEED-R5Q-R3

Purpose: corrected_read_only_extended_readiness_classify_dhan_context_and_stale_decisions_no_patch_no_restart_no_order_no_paper

Final verdict: BLOCKED_A6_FEED_R5Q_R3_READINESS_INCOMPLETE_CLASSIFIED_NO_ORDER_NO_PAPER

Safety: corrected read-only readiness classification only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "likely_condition": "DECISIONS_STREAM_PRESENT_BUT_STALE",
  "next_action": "Inspect strategy decision producer recency/logs read-only. No paper/live.",
  "prior_r5q_r2_failure_classification": "proof_shape_bug_for_r5o_ownership_fields_plus_real_readiness_failures",
  "prior_r5q_r2_final_verdict": "FAIL_A6_FEED_R5Q_R2_SAFETY_OR_PRECONDITION_CHECK",
  "prior_r5q_r2_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5Q-R2_corrected_read_only_extended_feed_feature_decision_readiness_consolidation_fixed_redaction_no_patch_no_restart_no_order_no_paper_20260515_095822.json",
  "r5o_risk_has_a6_artifacts_resolved": true,
  "r5o_risk_has_other_lane_artifacts_resolved": false,
  "r5p_condition": "FEATURES_AND_DECISIONS_PRESENT",
  "readiness_failures": [
    "decisions_stream_recent"
  ],
  "safety_failures": [],
  "standard_services_post": [],
  "standard_services_pre": [],
  "stream_growth": {
    "decisions:mme:stream": {
      "after": 1684,
      "before": 1684,
      "delta": 0
    },
    "features:mme:stream": {
      "after": 4279,
      "before": 4277,
      "delta": 2
    },
    "orders:mme:stream": {
      "after": null,
      "before": null,
      "delta": null
    },
    "system:errors:stream": {
      "after": 10023,
      "before": 10024,
      "delta": -1
    },
    "system:health:stream": {
      "after": 5684,
      "before": 5618,
      "delta": 66
    },
    "ticks:mme:fut:dhan:stream": {
      "after": 35,
      "before": 34,
      "delta": 1
    },
    "ticks:mme:fut:zerodha:stream": {
      "after": 78,
      "before": 73,
      "delta": 5
    },
    "ticks:mme:opt:context:dhan:stream": {
      "after": 169,
      "before": 161,
      "delta": 8
    },
    "ticks:mme:opt:selected:dhan:stream": {
      "after": 141,
      "before": 135,
      "delta": 6
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "after": 332,
      "before": 318,
      "delta": 14
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
  "prior_r5q_r2_found": true,
  "r5o_risk_dirty_a6_owned_no_other_lane": true,
  "r5p_features_and_decisions_present": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Safety/precondition failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5Q-R3_corrected_read_only_extended_readiness_classify_dhan_context_and_stale_decisions_no_patch_no_restart_no_order_no_paper_20260515_100117.json
