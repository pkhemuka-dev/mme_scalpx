# A6-FEED-R5A_read_only_feeds_start_exit_triage_after_stream_growth_but_process_not_visible_no_restart_no_order_no_paper_20260513_144139

Batch: A6-FEED-R5A

Purpose: read_only_feeds_start_exit_triage_after_stream_growth_but_process_not_visible_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5A_READ_ONLY_EXIT_LOG_TRIAGE_CAPTURED_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only triage only; no restart, no stop, no patch, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "features_visible_now": true,
  "feeds_visible_now": false,
  "likely_condition": "FEEDS_STARTED_PUBLISHED_SOME_STREAMS_THEN_EXITED_WITH_LOGGED_ERROR",
  "log_classification": {
    "credential_or_token_seen": false,
    "exception_seen": true,
    "import_error_seen": false,
    "normal_exit_hint_seen": true,
    "redis_error_seen": false,
    "traceback_seen": true
  },
  "r5_failed_only_on_feeds_process_visible_after": true,
  "r5_stream_growth": {
    "orders:mme:stream": {
      "after": null,
      "before": null,
      "delta": null
    },
    "system:errors:stream": {
      "after": 10001,
      "before": 10003,
      "delta": -2
    },
    "system:health:stream": {
      "after": 8106,
      "before": 8053,
      "delta": 53
    },
    "ticks:mme:fut:dhan:stream": {
      "after": 3,
      "before": 2,
      "delta": 1
    },
    "ticks:mme:fut:zerodha:stream": {
      "after": 2,
      "before": null,
      "delta": null
    },
    "ticks:mme:opt:context:dhan:stream": {
      "after": 7,
      "before": 3,
      "delta": 4
    },
    "ticks:mme:opt:selected:dhan:stream": {
      "after": 157,
      "before": 153,
      "delta": 4
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "after": 521,
      "before": 511,
      "delta": 10
    }
  },
  "strategy_visible_now": true
}
```

Services running:

```json
[
  "features",
  "strategy"
]
```

Required checks:

```json
{
  "latest_r5_proof_found": true,
  "no_broker_order": true,
  "no_order_broker_marker_visible": true,
  "no_paper_live": true,
  "no_redis_hash_write": true,
  "no_restart_stop_patch": true,
  "no_risk_execution_process_visible": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5A_read_only_feeds_start_exit_triage_after_stream_growth_but_process_not_visible_no_restart_no_order_no_paper_20260513_144139.json
