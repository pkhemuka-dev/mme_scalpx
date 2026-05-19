# A6-FEED-R5G_approved_observe_only_feeds_restart_after_lock_clear_readiness_probe_no_paper_no_order_no_risk_execution_20260513_150825

Batch: A6-FEED-R5G

Purpose: approved_observe_only_feeds_restart_after_lock_clear_readiness_probe_no_paper_no_order_no_risk_execution

Final verdict: FAIL_A6_FEED_R5G_SAFETY_CHECK_FAILED_NO_PAPER_NO_ORDER

Safety: approved feeds-only observe-only restart after stale lock clear; no source patch, no service stop, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "latest_r5e_likely_condition": "FEEDS_LOCK_PRESENT_BUT_NO_FEEDS_PROCESS_VISIBLE_STALE_LOCK_CANDIDATE",
  "latest_r5f_final_verdict": "PASS_A6_FEED_R5F_STALE_LOCK_FEEDS_CLEARED_ONLY_NO_START_NO_ORDER_NO_PAPER",
  "latest_r5f_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5F_approved_clear_stale_lock_feeds_only_no_service_start_no_order_no_paper_20260513_150033.json",
  "likely_condition": "FEEDS_START_ATTEMPT_DID_NOT_LEAVE_VISIBLE_PROCESS",
  "next_action": "Inspect proof/log. Do not start paper/live/risk/execution.",
  "post_lock": {
    "key": "lock:feeds",
    "ttl_info": {
      "pttl": "23588",
      "ttl": "24"
    },
    "type": "string",
    "value_sample_redacted": "feeds:mme-scalpx:44118"
  },
  "post_services_running": [],
  "pre_lock": {
    "key": "lock:feeds",
    "ttl_info": {
      "pttl": "27485",
      "ttl": "27"
    },
    "type": "string",
    "value_sample_redacted": "feeds:mme-scalpx:44118"
  },
  "pre_services_running": [],
  "readiness_failures": [
    "feeds_process_visible_after",
    "decisions_stream_present"
  ],
  "safety_failures": [
    "pre_start_lock_feeds_absent",
    "start_attempted_feeds_only"
  ],
  "start_attempted": false,
  "start_command": [
    ".venv/bin/python",
    "-m",
    "app.mme_scalpx.main",
    "--service",
    "feeds",
    "--bootstrap-provider",
    "app.mme_scalpx.integrations.bootstrap_provider:provide",
    "--skip-group-bootstrap"
  ],
  "start_error": null,
  "start_pid": null,
  "start_skipped_reason": "PRE_START_SAFETY_CHECK_FAILED",
  "stream_growth": {
    "decisions:mme:stream": {
      "after": 0,
      "before": 0,
      "delta": 0
    },
    "features:mme:stream": {
      "after": 240,
      "before": 235,
      "delta": 5
    },
    "orders:mme:stream": {
      "after": null,
      "before": null,
      "delta": null
    },
    "system:errors:stream": {
      "after": 6406,
      "before": 6298,
      "delta": 108
    },
    "system:health:stream": {
      "after": 3422,
      "before": 3313,
      "delta": 109
    },
    "ticks:mme:fut:dhan:stream": {
      "after": 58,
      "before": 56,
      "delta": 2
    },
    "ticks:mme:fut:zerodha:stream": {
      "after": 136,
      "before": 129,
      "delta": 7
    },
    "ticks:mme:opt:context:dhan:stream": {
      "after": 368,
      "before": 353,
      "delta": 15
    },
    "ticks:mme:opt:selected:dhan:stream": {
      "after": 238,
      "before": 225,
      "delta": 13
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "after": 1582,
      "before": 1554,
      "delta": 28
    }
  }
}
```

Safety checks:

```json
{
  "compile_checks_ok": true,
  "explicit_approval_captured": true,
  "latest_r5f_lock_clear_pass_found": true,
  "no_broker_order": true,
  "no_paper_live": true,
  "no_risk_execution_start": true,
  "post_no_risk_execution_order_process_visible": true,
  "post_orders_zero_or_absent": true,
  "post_position_flat": true,
  "pre_start_lock_feeds_absent": false,
  "pre_start_no_feeds_process_visible": true,
  "pre_start_no_risk_execution_order_process_visible": true,
  "pre_start_orders_zero_or_absent": true,
  "pre_start_position_flat": true,
  "source_files_unchanged_by_batch": true,
  "start_attempted_feeds_only": false,
  "start_error_absent": true
}
```

Readiness checks:

```json
{
  "decisions_stream_present": false,
  "dhan_option_context_stream_present": true,
  "dhan_option_context_stream_recent": true,
  "features_stream_present": true,
  "feeds_process_visible_after": false,
  "futures_feed_recent_any_provider": true,
  "lock_feeds_reacquired_or_owned_after_start": true,
  "selected_option_feed_recent_any_provider": true
}
```

Safety failures:

```json
[
  "pre_start_lock_feeds_absent",
  "start_attempted_feeds_only"
]
```

Readiness failures:

```json
[
  "feeds_process_visible_after",
  "decisions_stream_present"
]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5G_approved_observe_only_feeds_restart_after_lock_clear_readiness_probe_no_paper_no_order_no_risk_execution_20260513_150825.json

Log:
- /home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5G_approved_observe_only_feeds_restart_after_lock_clear_readiness_probe_no_paper_no_order_no_risk_execution_20260513_150825.feeds.log
