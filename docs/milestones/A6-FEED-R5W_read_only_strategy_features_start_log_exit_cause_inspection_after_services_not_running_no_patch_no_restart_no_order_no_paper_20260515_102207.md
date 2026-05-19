# A6-FEED-R5W_read_only_strategy_features_start_log_exit_cause_inspection_after_services_not_running_no_patch_no_restart_no_order_no_paper_20260515_102207

Batch: A6-FEED-R5W

Purpose: read_only_strategy_features_start_log_exit_cause_inspection_after_services_not_running_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5W_STRATEGY_FEATURES_EXIT_CAUSE_EVIDENCE_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only strategy/features start-log and exit-cause extraction only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "decisions_present": true,
  "decisions_recent": false,
  "decisions_stream_age_ms": 1749087,
  "decisions_stream_xlen": 1684,
  "features_recent": true,
  "features_stream_age_ms": 270502,
  "features_stream_xlen": 91,
  "likely_condition": "STRATEGY_NOT_RUNNING_WITH_LOGGED_EXIT_OR_ERROR_EVIDENCE",
  "log_findings_count": 9,
  "next_action": "Review extracted log findings; if source patch is needed, produce patch plan first. No restart/paper/live.",
  "r5u_final_verdict": "BLOCKED_A6_FEED_R5U_STARTED_OR_ATTEMPTED_BUT_READINESS_INCOMPLETE_NO_ORDER_NO_PAPER",
  "r5u_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101356.json",
  "r5u_start_plan": null,
  "r5u_start_results": null,
  "r5v_final_verdict": "PASS_A6_FEED_R5V_STRATEGY_LOG_AND_FEATURE_CONSUMER_GATE_INSPECTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5v_likely_condition": "STRATEGY_NOT_RUNNING_AFTER_START_WINDOW",
  "r5v_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5V_read_only_strategy_log_and_feature_consumer_gate_inspection_after_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_101833.json",
  "standard_services": []
}
```

Log findings summary:

```json
[
  {
    "exception_seen": true,
    "exit_seen": true,
    "mtime_iso_utc": "2026-05-15T04:47:53.901807+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236.features.log",
    "size": 2862,
    "traceback_seen": false
  },
  {
    "exception_seen": true,
    "exit_seen": true,
    "mtime_iso_utc": "2026-05-15T04:47:48.150314+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236.strategy.log",
    "size": 1995922,
    "traceback_seen": true
  },
  {
    "exception_seen": true,
    "exit_seen": false,
    "mtime_iso_utc": "2026-05-13T02:24:28.012913+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5G-R2_approved_observe_only_stack_recovery_after_r5g_shell_expansion_abort_no_order_no_broker_20260513_075338_strategy.log",
    "size": 384,
    "traceback_seen": false
  },
  {
    "exception_seen": true,
    "exit_seen": false,
    "mtime_iso_utc": "2026-05-13T02:24:20.002185+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5G-R2_approved_observe_only_stack_recovery_after_r5g_shell_expansion_abort_no_order_no_broker_20260513_075338_features.log",
    "size": 384,
    "traceback_seen": false
  },
  {
    "exception_seen": true,
    "exit_seen": false,
    "mtime_iso_utc": "2026-05-13T02:10:26.938450+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5F_approved_observe_only_features_strategy_reload_after_provider_mapping_patch_no_order_no_broker_20260513_074011_strategy.log",
    "size": 384,
    "traceback_seen": false
  },
  {
    "exception_seen": true,
    "exit_seen": false,
    "mtime_iso_utc": "2026-05-13T02:10:21.977998+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5F_approved_observe_only_features_strategy_reload_after_provider_mapping_patch_no_order_no_broker_20260513_074011_features.log",
    "size": 384,
    "traceback_seen": false
  },
  {
    "exception_seen": true,
    "exit_seen": false,
    "mtime_iso_utc": "2026-05-13T02:10:17.575598+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5F_approved_observe_only_features_strategy_reload_after_provider_mapping_patch_no_order_no_broker_20260513_074011.log",
    "size": 1016,
    "traceback_seen": false
  },
  {
    "exception_seen": true,
    "exit_seen": true,
    "mtime_iso_utc": "2026-05-13T04:02:06.767587+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/pstrategy_20260513_093158.log",
    "size": 2450,
    "traceback_seen": true
  },
  {
    "exception_seen": true,
    "exit_seen": true,
    "mtime_iso_utc": "2026-05-13T04:01:58.619846+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/pfeatures_20260513_093158.log",
    "size": 2450,
    "traceback_seen": true
  }
]
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5u_proof_found": true,
  "latest_r5v_proof_found": true,
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
  "r5v_strategy_not_running_condition_found": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5W_read_only_strategy_features_start_log_exit_cause_inspection_after_services_not_running_no_patch_no_restart_no_order_no_paper_20260515_102207.json
