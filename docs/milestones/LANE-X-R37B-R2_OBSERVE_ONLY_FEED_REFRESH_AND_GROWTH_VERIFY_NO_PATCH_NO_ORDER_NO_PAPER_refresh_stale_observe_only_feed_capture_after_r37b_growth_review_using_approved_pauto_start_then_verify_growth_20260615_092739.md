# LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739

classification: **PASS**

## Important verdict
Observe-only feed/capture refresh only. This does **not** authorize paper, live trading, broker order, risk service, execution service, or replay.

## Pre safety
- pstatus rc: `0`
- paper_route_allowed_norm: `false`
- orders/risk/execution streams: `0/0/0`
- risk/execution/replay procs: `0/0/0`

## Refresh action
- action: `PAUTO_START_OBSERVE_ONLY_REFRESH`
- action_rc: `0`
- action_reason: `pauto_start invoked once under observe-only env to refresh stale feeds/capture`

## Post safety
- pstatus rc: `0`
- paper_route_allowed_norm: `false`
- paper_reason: ``
- orders/risk/execution streams: `0/0/0`
- risk/execution/replay procs: `0/0/0`

## Growth verdict
- growth_compare_rc: `0`
- fut_redis_grew: `true`
- opt_redis_grew: `true`
- features_redis_grew: `true`
- decisions_redis_grew: `true`
- durable_capture_grew: `true`

## pauto_start output
```text
===== PAUTO START / OBSERVE-ONLY CAPTURE SUPERVISOR =====
2026-06-15T09:27:40+05:30
outdir=run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740
safety: orders=0 risk=0 execution=0 risk_pids=0 execution_pids=0
[1] 2267
pid=2267
Run: pauto_status
```

## Growth comparison JSON
```json
{
  "stream_growth": {
    "decisions:mme:stream": {
      "type_pre": "stream",
      "type_post": "stream",
      "xlen_pre": 3215,
      "xlen_post": 17,
      "xlen_delta": -3198,
      "last_id_pre": "1781495859127-0",
      "last_id_post": "1781495979579-0",
      "last_id_changed": true
    },
    "errors:mme:stream": {
      "type_pre": "none",
      "type_post": "none",
      "xlen_pre": 0,
      "xlen_post": 0,
      "xlen_delta": 0,
      "last_id_pre": "NONE",
      "last_id_post": "NONE",
      "last_id_changed": false
    },
    "features:mme:stream": {
      "type_pre": "stream",
      "type_post": "stream",
      "xlen_pre": 3,
      "xlen_post": 6,
      "xlen_delta": 3,
      "last_id_pre": "1781495859722-0",
      "last_id_post": "1781495976331-0",
      "last_id_changed": true
    },
    "ticks:mme:fut:zerodha:stream": {
      "type_pre": "stream",
      "type_post": "stream",
      "xlen_pre": 260,
      "xlen_post": 287,
      "xlen_delta": 27,
      "last_id_pre": "1781495852272-0",
      "last_id_post": "1781495954445-0",
      "last_id_changed": true
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "type_pre": "stream",
      "type_post": "stream",
      "xlen_pre": 1350,
      "xlen_post": 1443,
      "xlen_delta": 93,
      "last_id_pre": "1781495859645-0",
      "last_id_post": "1781495956562-0",
      "last_id_changed": true
    }
  },
  "capture_growth": {
    "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653": {
      "size_pre": 1964006661,
      "size_post": 1964006661,
      "size_delta": 0
    },
    "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023": {
      "size_pre": 2793930,
      "size_post": 2793930,
      "size_delta": 0
    },
    "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740": {
      "size_pre": 0,
      "size_post": 13913205,
      "size_delta": 13913205
    },
    "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347": {
      "size_pre": 105920469,
      "size_post": 105920469,
      "size_delta": 0
    },
    "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625": {
      "size_pre": 104374596,
      "size_post": 104374596,
      "size_delta": 0
    },
    "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315": {
      "size_pre": 126617643,
      "size_post": 126617643,
      "size_delta": 0
    },
    "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653": {
      "size_pre": 100889139,
      "size_post": 100889139,
      "size_delta": 0
    }
  },
  "fut_redis_grew": true,
  "opt_redis_grew": true,
  "features_redis_grew": true,
  "decisions_redis_grew": true,
  "errors_redis_grew": false,
  "durable_capture_grew": true
}
```

## Growth comparison errors
```text
```

## Project processes post
```text
   2267    1254 S          02:01 .venv/bin/python bin/b1_profit_live_capture_supervisor.py --outdir run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740 --action-mode apply --interval-sec 15 --stale-after-ms 30000
   2406    2267 Ss         02:00 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python /home/Lenovo/scalpx/projects/mme_scalpx/bin/b1_profit_live_durable_capture.py --outdir run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture --no-backfill
   2437    2267 Rs         02:00 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --skip-group-bootstrap
   2438    2267 Rs         02:00 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --skip-group-bootstrap
   4205       1 Rs         00:15 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
```

## Recent capture files post
```text
# latest 80 live_capture files by mtime
1781495979.6746978580 9959070 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/decisions.jsonl.gz
1781495979.2346565460 2020270 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/health.jsonl.gz
1781495976.7894269830 1887981 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/features.jsonl.gz
1781495975.6653214500 699 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/state.json
1781495975.6623211680 1105 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/heartbeat.json
1781495974.1401782660 1974 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/supervisor_state.json
1781495974.1391781720 12937 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/supervisor_events.jsonl
1781495957.1805860660 446 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/errors.jsonl.gz
1781495957.1805860660 3800 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/provider_runtime.jsonl.gz
1781495957.1795859720 10033 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/opt_selected_zerodha.jsonl.gz
1781495955.0053818530 2875 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/fut_zerodha.jsonl.gz
1781495861.6376162170 1318 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/features_supervisor_start.log
1781495861.5326063580 1318 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/strategy_supervisor_start.log
1781495861.3025847630 1156 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/manifest_start.json
1781495860.6055193200 4 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/recorder.pid
1781495860.6045192260 0 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/recorder.log
1781495860.1364752850 22 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/supervisor.log
1781495860.1074725620 5 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/supervisor.pid
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
1781260255.2271158570 561143 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023/feeds_supervisor_start.log
1781260253.9940131280 17626800 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/feeds_supervisor_start.log
1781260237.2956219880 30135 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/strategy_supervisor_start.log
1781260235.1264412740 1904 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/supervisor_state.json
1781260235.1254411910 2246904 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/supervisor_events.jsonl
1781260234.7744119470 2058 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/features_supervisor_start.log
1781260233.0082648100 911 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/manifest_stop.json
1781260232.9902633100 8844196 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/errors.jsonl.gz
1781260232.9902633100 4291216 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/provider_runtime.jsonl.gz
1781260232.9902633100 173120238 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/health.jsonl.gz
1781260232.9892632260 919612 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/fut_zerodha.jsonl.gz
1781260232.9892632260 4635604 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/opt_selected_zerodha.jsonl.gz
1781260232.9892632260 279930008 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/features.jsonl.gz
1781260232.9892632260 1472345773 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/decisions.jsonl.gz
1781260229.4269664530 719 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/state.json
1781260229.4209659530 1129 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/heartbeat.json
1781260226.1016894250 2058 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023/supervisor_state.json
1781260226.1006893420 2226606 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023/supervisor_events.jsonl
1781243032.2892932110 75 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/recorder_errors.log
1781237423.5960091210 22 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023/supervisor.log
1781237423.5940089540 5 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_094023/supervisor.pid
1781237215.4716712880 1156 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/manifest_start.json
1781237214.5395936410 4 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/recorder.pid
1781237214.5385935580 0 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/recorder.log
1781237213.9325430710 22 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/supervisor.log
1781237213.9175418210 5 run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/supervisor.pid
1781171742.1259505270 1078 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/pseal.log
1781171742.0029427560 2256 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/streams_summary.tsv
1781171741.9839415550 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/errors.redisraw.gz
1781171741.9779411760 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/errors.err
1781171723.6627840970 126437155 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/decisions.redisraw.gz
1781171595.9087131020 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/decisions.err
1781171595.8887118380 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/features.redisraw.gz
1781171595.8827114590 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/features.err
1781171595.8627101960 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_context_dhan.redisraw.gz
1781171595.8567098170 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_context_dhan.err
1781171595.8377086160 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_selected_dhan.redisraw.gz
1781171595.8307081740 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_selected_dhan.err
1781171595.8017063420 172926 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_selected_zerodha.redisraw.gz
1781171595.6846989500 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_selected_zerodha.err
1781171595.6636976230 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/fut_dhan.redisraw.gz
1781171595.6586973070 0 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/fut_dhan.err
1781171595.6396961070 21 run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/fut_zerodha.redisraw.gz
```

## Reasons
fut/opt Redis growth and durable capture growth proven after observe-only refresh

## Artifact paths
- proof path: `run/proofs/LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739.json`
- report path: `run/audits/LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739_report.md`
- milestone path: `docs/milestones/LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739.md`
- runbook path: `docs/runbooks/LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739_runbook.md`
- handoff path: `run/handoffs/LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739_handoff.md`
- raw dir: `run/audits/LANE-X-R37B-R2_OBSERVE_ONLY_FEED_REFRESH_AND_GROWTH_VERIFY_NO_PATCH_NO_ORDER_NO_PAPER_refresh_stale_observe_only_feed_capture_after_r37b_growth_review_using_approved_pauto_start_then_verify_growth_20260615_092739_raw`

## Next recommended batch
`LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER`
