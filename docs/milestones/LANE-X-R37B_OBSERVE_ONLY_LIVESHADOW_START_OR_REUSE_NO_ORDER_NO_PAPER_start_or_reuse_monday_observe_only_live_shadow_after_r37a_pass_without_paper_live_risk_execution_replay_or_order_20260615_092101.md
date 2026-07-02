# LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101

classification: **REVIEW**

## Important verdict
Observe-only live-shadow start/reuse only. This does **not** authorize paper, live trading, broker order, risk service, execution service, or replay.

## Safety pre/post
- pre: R37A-style safety rechecked before start/reuse
- post: pstatus/streams/procs rechecked after start/reuse

## Pre safety
- pstatus rc: `0`
- paper_route_allowed_norm: `false`
- orders/risk/execution streams: `0/0/0`
- risk/execution/replay procs: `0/0/0`

## Start/reuse action
- action: `REUSE_EXISTING_MAIN`
- action_rc: `0`
- action_reason: `existing app.mme_scalpx.main process found; reused without starting new process`
- main_pids_before: `1301`
- main_pids_after: `1301`
- runtime_present_after: `true`

## Post safety
- pstatus rc: `0`
- paper_route_allowed_norm: `false`
- paper_reason: ``
- orders/risk/execution streams: `0/0/0`
- risk/execution/replay procs: `0/0/0`

## Live capture growth
- latest_dir_before: `run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653`
- latest_dir_after: `run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653`
- size_before: `100889139`
- size_after: `100889139`
- size_delta: `0`
- growth_status: `NO_GROWTH`

## pauto_start output
```text
```

## pauto_status after
```text
latest=run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023
status=NOT_RUNNING pid=6433

state:
{
  "action_mode": "apply",
  "actions": [
    "feed_stale_fut=1739960_opt=1740002",
    "started_feeds_pid_757622"
  ],
  "freshness": {
    "decisions": {
      "age_ms": 612,
      "latest_id": "1781260223520-0",
      "stream": "decisions:mme:stream"
    },
    "features": {
      "age_ms": 1817,
      "latest_id": "1781260222167-0",
      "stream": "features:mme:stream"
    },
    "fut": {
      "age_ms": 1738704,
      "latest_id": "1781258485102-0",
      "stream": "ticks:mme:fut:zerodha:stream"
    },
    "opt": {
      "age_ms": 1738742,
      "latest_id": "1781258485127-0",
      "stream": "ticks:mme:opt:selected:zerodha:stream"
    }
  },
  "outdir": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023",
  "post_action_freshness": {
    "decisions": {
      "age_ms": 1188,
      "latest_id": "1781260224913-0",
      "stream": "decisions:mme:stream"
    },
    "features": {
      "age_ms": 3812,
      "latest_id": "1781260222167-0",
      "stream": "features:mme:stream"
    },
    "fut": {
      "age_ms": 1740694,
      "latest_id": "1781258485102-0",
      "stream": "ticks:mme:fut:zerodha:stream"
    },
    "opt": {
      "age_ms": 1740731,
      "latest_id": "1781258485127-0",
      "stream": "ticks:mme:opt:selected:zerodha:stream"
    }
  },
  "post_action_service_counts": {
    "features": 1,
    "feeds_service": 9,
    "generic_main": 0,
    "recorder": 1,
    "strategy": 1
  },
  "provider": {
    "context_status": "UNAVAILABLE",
    "futures_status": "HEALTHY",
    "mode": "OBSERVE_ONLY",
    "selected_status": "FAILOVER_ACTIVE"
  },
  "read_only_safety": {
    "execution_start_allowed": false,
    "order_allowed": false,
    "redis_delete_allowed": false,
    "risk_start_allowed": false
  },
  "safety": {
    "execution": 0,
    "execution_pids": 0,
    "orders": 0,
    "risk": 0,
    "risk_pids": 0
  },
  "service_counts": {
    "features": 1,
    "feeds_service": 8,
    "generic_main": 0,
    "recorder": 1,
    "strategy": 1
  },
  "ts_utc": "2026-06-12T10:30:23.270245+00:00"
}
files:
total 2.7M
-rw------- 1 Lenovo Lenovo 548K Jun 12 16:00 feeds_supervisor_start.log
-rw------- 1 Lenovo Lenovo   22 Jun 12 09:40 supervisor.log
-rw------- 1 Lenovo Lenovo    5 Jun 12 09:40 supervisor.pid
-rw------- 1 Lenovo Lenovo 2.2M Jun 12 16:00 supervisor_events.jsonl
-rw------- 1 Lenovo Lenovo 2.1K Jun 12 16:00 supervisor_state.json

log_tail:
nohup: ignoring input
```

## Recent live capture files after
```text
1781272088.3345006110 1078 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/pseal.log
1781272088.2854947000 2272 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/streams_summary.tsv
1781272088.2594915630 112359 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/errors.redisraw.gz
1781272088.1534787760 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/errors.err
1781272080.1455128450 55237093 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/decisions.redisraw.gz
1781272049.2917912340 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/decisions.err
1781272042.1855204400 45532131 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/features.redisraw.gz
1781272014.0293154450 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/features.err
1781272014.0123135090 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_context_dhan.redisraw.gz
1781272014.0073129400 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_context_dhan.err
1781272013.9903110050 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_selected_dhan.redisraw.gz
1781272013.9843103220 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_selected_dhan.err
1781272013.9683085000 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_selected_zerodha.redisraw.gz
1781272013.9633079310 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_selected_zerodha.err
1781272013.9463059960 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/fut_dhan.redisraw.gz
1781272013.9413054270 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/fut_dhan.err
1781272013.9033011010 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/fut_zerodha.redisraw.gz
1781272013.8973004180 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/fut_zerodha.err
1781272013.7742864150 5 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/pseal.pid
```

## Reasons
observe-only runtime safe but live_capture growth not proven in 45s

## Artifact paths
- proof path: `run/proofs/LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101.json`
- report path: `run/audits/LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101_report.md`
- milestone path: `docs/milestones/LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101.md`
- runbook path: `docs/runbooks/LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101_runbook.md`
- handoff path: `run/handoffs/LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101_handoff.md`
- raw dir: `run/audits/LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101_raw`

## Next recommended batch
`Resolve R37B FAIL/REVIEW reason before R37C`
