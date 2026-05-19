# A6-FEED-R5G_read_only_extract_new_feeds_failure_after_lock_clear_feeds_start_no_restart_no_order_no_paper_20260513_134059

Batch: A6-FEED-R5G

Purpose: read_only_extract_new_feeds_failure_after_lock_clear_feeds_start_no_restart_no_order_no_paper

Final verdict: TRIAGE_A6_FEED_R5G_NEW_FEEDS_FAILURE_EXTRACTED_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only extraction only; no lock delete, no source patch, no service start/stop/restart, no Redis write, no paper/live, no risk/execution, no broker/order.

R5F failures:

```json
[
  "lock_feeds_deleted_or_replaced_by_new_running_feeds",
  "feeds_service_running_after"
]
```

Error markers:

```json
[
  "traceback",
  "unhandled_fatal_error",
  "feedstartuperror",
  "singleton lock",
  "bootstrap_provider_dhan_live_unavailable",
  "missing dhan_client_id",
  "zerodha",
  "dhan",
  "error",
  "warning"
]
```

Error blocks:

```json
[
  {
    "marker_line_index": 7,
    "start_line_index": 0,
    "end_line_index": 9,
    "line": "{\"level\":\"ERROR\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"unhandled_fatal_error error=feeds singleton lock not acquired\\nTraceback (most recent call last):\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1895, in main\\n    return run_service(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1637, in run_service\\n    return _run_service_once(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1623, in _run_service_once\\n    result = runner(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\\\", line 2687, in run\\n    raise FeedStartupError(\\\"feeds singleton lock not acquired\\\")\\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\\n\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:49.419855+00:00\"}",
    "block": [
      "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"logging_configured level=INFO format=json\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:38.321135+00:00\"}",
      "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.domain.instruments\",\"message\":\"instrument_repository_loaded path=/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv format=csv records=43288 futures=6 calls=1651 puts=1673\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:43.864299+00:00\"}",
      "{\"level\":\"WARNING\",\"logger\":\"app.mme_scalpx.integrations.bootstrap_provider\",\"message\":\"bootstrap_provider_dhan_live_unavailable error=missing DHAN_CLIENT_ID / MME_DHAN_CLIENT_ID\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:48.932623+00:00\"}",
      "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:49.207747+00:00\"}",
      "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=0 dhan_context_adapter=0 broker=1\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:49.211687+00:00\"}",
      "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"consumer_group_bootstrap_disabled\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:49.355020+00:00\"}",
      "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"runtime_service_starting service=feeds module=app.mme_scalpx.services.feeds instance_id=feeds:mme-scalpx:42577 replay=False\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:49.355467+00:00\"}",
      "{\"level\":\"ERROR\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"unhandled_fatal_error error=feeds singleton lock not acquired\\nTraceback (most recent call last):\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1895, in main\\n    return run_service(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1637, in run_service\\n    return _run_service_once(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\", line 1623, in _run_service_once\\n    result = runner(context)\\n  File \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\\\", line 2687, in run\\n    raise FeedStartupError(\\\"feeds singleton lock not acquired\\\")\\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\\n\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:49.419855+00:00\"}",
      "{\"level\":\"INFO\",\"logger\":\"app.mme_scalpx.main\",\"message\":\"shutdown_completed_cleanly\",\"process\":42577,\"thread\":\"MainThread\",\"ts\":\"2026-05-13T08:07:49.420671+00:00\"}"
    ]
  }
]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5G_read_only_extract_new_feeds_failure_after_lock_clear_feeds_start_no_restart_no_order_no_paper_20260513_134059.json
