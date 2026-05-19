# A6-FEED-R4_read_only_live_feed_readiness_after_bad_quote_quarantine_static_pass_no_start_no_order_no_paper_20260513_105848

Batch: A6-FEED-R4

Purpose: read_only_live_feed_readiness_after_bad_quote_quarantine_static_pass_no_start_no_order_no_paper

Final verdict: FAIL_A6_FEED_R4_READ_ONLY_LIVE_FEED_READINESS_BLOCKED

Safety: read-only proof only; no source patch, no restore, no service start/stop, no Redis hash write, no paper/live, no risk/execution, no broker/order.

Required checks:

```json
{
  "decisions_stream_present": false,
  "dhan_option_context_stream_present": false,
  "features_stream_present": true,
  "feed_service_seen_or_existing_streams_present": true,
  "feeds_py_compiles": true,
  "feeds_py_unchanged_by_batch": true,
  "futures_feed_recent_any_provider": true,
  "models_py_compiles": true,
  "models_py_unchanged_by_batch": true,
  "no_broker_order": true,
  "no_paper_live": true,
  "no_redis_hash_write": true,
  "no_risk_execution_order_pid": true,
  "no_service_start_stop": true,
  "no_source_patch": true,
  "orders_mme_stream_zero": true,
  "position_flat": true,
  "previous_static_pass_found": true,
  "redis_ping_ok": true,
  "selected_option_feed_recent_any_provider": true
}
```

Failures:

```json
[
  "dhan_option_context_stream_present",
  "decisions_stream_present"
]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R4_read_only_live_feed_readiness_after_bad_quote_quarantine_static_pass_no_start_no_order_no_paper_20260513_105848.json
