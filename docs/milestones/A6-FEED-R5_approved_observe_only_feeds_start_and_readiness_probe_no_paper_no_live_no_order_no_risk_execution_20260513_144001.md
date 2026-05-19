# A6-FEED-R5_approved_observe_only_feeds_start_and_readiness_probe_no_paper_no_live_no_order_no_risk_execution_20260513_144001

Batch: A6-FEED-R5

Purpose: approved_observe_only_feeds_start_and_readiness_probe_no_paper_no_live_no_order_no_risk_execution

Final verdict: FAIL_A6_FEED_R5_OBSERVE_ONLY_FEEDS_START_OR_READINESS_BLOCKED_NO_ORDER_NO_PAPER

Safety: approved feeds-only observe-only start; no source patch, no restore, no service stop, no paper/live, no risk/execution start, no broker/order.

Start:

```json
{
  "command": [
    ".venv/bin/python",
    "-m",
    "app.mme_scalpx.main",
    "--service",
    "feeds",
    "--bootstrap-provider",
    "app.mme_scalpx.integrations.bootstrap_provider:provide",
    "--skip-group-bootstrap"
  ],
  "error": null,
  "log": "/home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5_approved_observe_only_feeds_start_and_readiness_probe_no_paper_no_live_no_order_no_risk_execution_20260513_144001.feeds.log",
  "observe_seconds": 20,
  "pid": 43466,
  "skipped_reason": null
}
```

Required checks:

```json
{
  "dhan_option_context_stream_present": true,
  "explicit_approval_captured": true,
  "feeds_process_visible_after": false,
  "futures_feed_recent_any_provider": true,
  "main_feeds_models_unchanged_by_batch": true,
  "no_broker_order": true,
  "no_paper_live": true,
  "no_risk_execution_order_process_visible_after": true,
  "no_risk_execution_start": true,
  "orders_mme_stream_remained_zero": true,
  "position_remained_flat": true,
  "pre_start_safety_ok": true,
  "selected_option_feed_recent_any_provider": true
}
```

Failures:

```json
[
  "feeds_process_visible_after"
]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5_approved_observe_only_feeds_start_and_readiness_probe_no_paper_no_live_no_order_no_risk_execution_20260513_144001.json

Log:
- /home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5_approved_observe_only_feeds_start_and_readiness_probe_no_paper_no_live_no_order_no_risk_execution_20260513_144001.feeds.log
