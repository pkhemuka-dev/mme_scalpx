# A6-FEED-R5F_approved_stale_lock_clear_then_feeds_only_observe_start_no_risk_execution_no_order_no_paper_20260513_133734

Batch: A6-FEED-R5F

Purpose: approved_stale_lock_clear_then_feeds_only_observe_start_no_risk_execution_no_order_no_paper

Final verdict: PARTIAL_A6_FEED_R5F_LOCK_CLEARED_FEEDS_START_ATTEMPTED_READINESS_STILL_BLOCKED_NO_ORDER_NO_PAPER

Safety:
- Approved Redis write: DEL lock:feeds only if no feeds PID exists
- Approved service start: feeds only
- Kept features/strategy as-is
- Forbidden: risk/execution/paper/live/broker order/order routing
- orders:mme:stream after: 0
- position flat after: True
- paper_live_status: A6-PAPER_BLOCKED_NO_PAPER_NO_LIVE

Required checks:

```json
{
  "approved_redis_write_limited_to_lock_feeds_del": true,
  "dhan_option_context_stream_present": true,
  "features_service_running_after": true,
  "feed_stream_recent_any_provider": true,
  "feeds_service_running_after": false,
  "lock_delete_attempted_only_after_no_feeds_pid": true,
  "lock_feeds_deleted_or_replaced_by_new_running_feeds": false,
  "no_broker_order": true,
  "no_paper_live": true,
  "no_risk_execution_order_pid_after": true,
  "no_source_patch": true,
  "orders_mme_stream_zero_after": true,
  "position_flat_after": true,
  "preflight_features_service_running_before": true,
  "preflight_feeds_py_compiles": true,
  "preflight_feeds_service_not_running_before": true,
  "preflight_latest_r5e_confirmed_lock_stuck_or_renewing": true,
  "preflight_latest_r5e_found": true,
  "preflight_lock_feeds_exists_before": true,
  "preflight_lock_value_has_old_failed_feed_identity": true,
  "preflight_main_py_compiles": true,
  "preflight_no_risk_execution_order_pid_before": true,
  "preflight_orders_mme_stream_zero_before": true,
  "preflight_paper_live_env_not_enabled": true,
  "preflight_position_flat_before": true,
  "preflight_redis_ping_ok": true,
  "preflight_strategy_service_running_before": true,
  "selected_option_stream_recent_any_provider": true,
  "source_files_unchanged": true,
  "strategy_service_running_after": true
}
```

Failures:

```json
[
  "lock_feeds_deleted_or_replaced_by_new_running_feeds",
  "feeds_service_running_after"
]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5F_approved_stale_lock_clear_then_feeds_only_observe_start_no_risk_execution_no_order_no_paper_20260513_133734.json
