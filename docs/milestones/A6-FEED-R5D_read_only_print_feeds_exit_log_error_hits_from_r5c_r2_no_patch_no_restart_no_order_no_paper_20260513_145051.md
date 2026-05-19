# A6-FEED-R5D_read_only_print_feeds_exit_log_error_hits_from_r5c_r2_no_patch_no_restart_no_order_no_paper_20260513_145051

Batch: A6-FEED-R5D

Purpose: read_only_print_feeds_exit_log_error_hits_from_r5c_r2_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5D_ERROR_HITS_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only extraction only; no restart, no stop, no patch, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "extracted_error_hit_count": 3,
  "main_log_error_hit_count": 3,
  "r5_failures": [
    "feeds_process_visible_after"
  ],
  "r5_final_verdict": "FAIL_A6_FEED_R5_OBSERVE_ONLY_FEEDS_START_OR_READINESS_BLOCKED_NO_ORDER_NO_PAPER",
  "r5a_likely_condition": "FEEDS_STARTED_PUBLISHED_SOME_STREAMS_THEN_EXITED_WITH_LOGGED_ERROR",
  "r5c_r2_failures": [
    "prior_r5c_failed_as_tooling_redaction_error"
  ],
  "r5c_r2_final_verdict": "FAIL_A6_FEED_R5C_R2_SAFETY_OR_EVIDENCE_CAPTURE",
  "r5c_r2_likely_condition": "NO_TRACEBACK_BUT_ERROR_OR_EXIT_LINES_FOUND_IN_FEEDS_LOG",
  "r5c_r2_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5C-R2_corrected_read_only_broader_feeds_exit_evidence_extract_fixed_redaction_no_patch_no_restart_no_order_no_paper_20260513_144740.json",
  "services_running": [
    "features",
    "strategy"
  ],
  "traceback_count": 0
}
```

Error hits:

```json
[
  {
    "context": [
      {
        "line": 1,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"logging_configured level=INFO format=json\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:02.262906+00:00\"}"
      },
      {
        "line": 2,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.domain.instruments\",\"message\":\"instrument_repository_loaded <REDACTED_SECRET_OR_TOKEN> format=csv records=43288 futures=6 calls=1651 puts=1673\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:07.284125+00:00\"}"
      },
      {
        "line": 3,
        "text": "{\"level\":\"WARNING\",\"logger\":\"app.mme_scalpx.integrations.bootstrap_provider\",\"message\":\"bootstrap_provider_dhan_live_unavailable error=missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:11.936896+00:00\"}"
      },
      {
        "line": 4,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.139078+00:00\"}"
      },
      {
        "line": 5,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.140594+00:00\"}"
      },
      {
        "line": 6,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"consumer_group_bootstrap_disabled\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.249773+00:00\"}"
      }
    ],
    "line": 3,
    "match": "{\"level\":\"WARNING\",\"logger\":\"app.mme_scalpx.integrations.bootstrap_provider\",\"message\":\"bootstrap_provider_dhan_live_unavailable error=missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:11.936896+00:00\"}"
  },
  {
    "context": [
      {
        "line": 5,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.140594+00:00\"}"
      },
      {
        "line": 6,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"consumer_group_bootstrap_disabled\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.249773+00:00\"}"
      },
      {
        "line": 7,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"runtime_service_starting service=feeds module=app.mme_scalpx.services.feeds instance_id=feeds:mme-scalpx:43466 replay=False\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.250225+00:00\"}"
      },
      {
        "line": 8,
        "text": "{\"level\":\"ERROR\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"unhandled_fatal_error error=feeds singleton lock not acquired\\nTraceback (most recent call last):\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1895, in main\\n    return run_service(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1637, in run_service\\n    return _run_service_once(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1623, in _run_service_once\\n    result = runner(context)\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 2687, in run\\n    raise FeedStartupError(\\\"feeds singleton lock not acquired\\\")\\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\\n\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.306039+00:00\"}"
      },
      {
        "line": 9,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"shutdown_completed_cleanly\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.306313+00:00\"}"
      }
    ],
    "line": 8,
    "match": "{\"level\":\"ERROR\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"unhandled_fatal_error error=feeds singleton lock not acquired\\nTraceback (most recent call last):\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1895, in main\\n    return run_service(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1637, in run_service\\n    return _run_service_once(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1623, in _run_service_once\\n    result = runner(context)\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 2687, in run\\n    raise FeedStartupError(\\\"feeds singleton lock not acquired\\\")\\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\\n\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.306039+00:00\"}"
  },
  {
    "context": [
      {
        "line": 6,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"consumer_group_bootstrap_disabled\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.249773+00:00\"}"
      },
      {
        "line": 7,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"runtime_service_starting service=feeds module=app.mme_scalpx.services.feeds instance_id=feeds:mme-scalpx:43466 replay=False\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.250225+00:00\"}"
      },
      {
        "line": 8,
        "text": "{\"level\":\"ERROR\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"unhandled_fatal_error error=feeds singleton lock not acquired\\nTraceback (most recent call last):\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1895, in main\\n    return run_service(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1637, in run_service\\n    return _run_service_once(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1623, in _run_service_once\\n    result = runner(context)\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 2687, in run\\n    raise FeedStartupError(\\\"feeds singleton lock not acquired\\\")\\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\\n\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.306039+00:00\"}"
      },
      {
        "line": 9,
        "text": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"shutdown_completed_cleanly\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.306313+00:00\"}"
      }
    ],
    "line": 9,
    "match": "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"shutdown_completed_cleanly\",\"process\":43466,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T09:10:12.306313+00:00\"}"
  }
]
```

Required checks:

```json
{
  "error_hits_extracted": true,
  "no_broker_order": true,
  "no_order_broker_marker_visible": true,
  "no_paper_live": true,
  "no_redis_hash_write": true,
  "no_restart_stop_patch": true,
  "no_risk_execution_process_visible": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "r5c_r2_proof_found": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5D_read_only_print_feeds_exit_log_error_hits_from_r5c_r2_no_patch_no_restart_no_order_no_paper_20260513_145051.json
