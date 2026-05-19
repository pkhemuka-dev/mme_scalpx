# A6-FEED-R5F_approved_clear_stale_lock_feeds_only_no_service_start_no_order_no_paper_20260513_150033

Batch: A6-FEED-R5F

Purpose: approved_clear_stale_lock_feeds_only_no_service_start_no_order_no_paper

Final verdict: PASS_A6_FEED_R5F_STALE_LOCK_FEEDS_CLEARED_ONLY_NO_START_NO_ORDER_NO_PAPER

Safety: approved clear of Redis key `lock:feeds` only; no service start, no service stop, no source patch, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "delete_attempted": true,
  "delete_result": {
    "args": [
      "redis-cli",
      "DEL",
      "lock:feeds"
    ],
    "ok": true,
    "rc": 0,
    "stderr": "",
    "stdout": "1"
  },
  "delete_skipped_reason": null,
  "final_condition": "STALE_LOCK_FEEDS_CLEARED_READY_FOR_APPROVED_FEEDS_ONLY_RESTART_PROOF",
  "latest_r5d_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5D_read_only_print_feeds_exit_log_error_hits_from_r5c_r2_no_patch_no_restart_no_order_no_paper_20260513_145051.json",
  "latest_r5e_likely_condition": "FEEDS_LOCK_PRESENT_BUT_NO_FEEDS_PROCESS_VISIBLE_STALE_LOCK_CANDIDATE",
  "latest_r5e_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5E_read_only_inspect_feeds_singleton_lock_after_lock_not_acquired_no_clear_no_restart_no_order_no_paper_20260513_145511.json",
  "next_action": "Next batch may be approved feeds-only restart/readiness proof. Do not start paper/live/risk/execution.",
  "post_lock": {
    "key": "lock:feeds",
    "ttl_info": {
      "pttl": "-2",
      "ttl": "-2"
    },
    "type": "none",
    "value_sample_redacted": null
  },
  "post_services_running": [
    "features",
    "strategy"
  ],
  "pre_lock": {
    "key": "lock:feeds",
    "ttl_info": {
      "pttl": "28308",
      "ttl": "28"
    },
    "type": "string",
    "value_sample_redacted": "feeds:mme-scalpx:43795"
  },
  "pre_services_running": [
    "features",
    "strategy"
  ]
}
```

Required checks:

```json
{
  "checked_sources_unchanged_by_batch": true,
  "delete_attempted_only_for_lock_feeds": true,
  "delete_removed_one_or_zero": true,
  "delete_result_ok": true,
  "explicit_approval_captured": true,
  "latest_r5e_proof_found": true,
  "no_broker_order": true,
  "no_paper_live": true,
  "no_risk_execution_start": true,
  "no_service_start": true,
  "no_service_stop": true,
  "no_source_patch": true,
  "post_clear_lock_feeds_absent": true,
  "post_clear_no_order_broker_marker_visible": true,
  "post_clear_no_risk_execution_process_visible": true,
  "post_clear_orders_zero_or_absent": true,
  "post_clear_position_flat": true,
  "pre_clear_lock_existed": true,
  "pre_clear_lock_key_was_lock_feeds": true,
  "pre_clear_no_feeds_process_visible": true,
  "pre_clear_no_order_broker_marker_visible": true,
  "pre_clear_no_risk_execution_process_visible": true,
  "pre_clear_orders_zero_or_absent": true,
  "pre_clear_position_flat": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5F_approved_clear_stale_lock_feeds_only_no_service_start_no_order_no_paper_20260513_150033.json
