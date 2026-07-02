# LANE-X-R31D5A_OFFMARKET_FEED_DEAD_FREEZE_AND_SAFE_FEEDS_STOP_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_184214
2026-06-07T18:42:14+05:30

LAW=OFFMARKET_FREEZE_AND_SAFE_FEEDS_STOP_ONLY_NO_PATCH_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31D5 proof
R31D5=run/proofs/LANE-X-R31D5_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_183935.json
{
  "tag": "LANE-X-R31D5_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_183935",
  "classification": "REVIEW_R31D5_PSTACK_FAIL_CLOSED_DO_NOT_RUN_CANDIDATE_WATCH",
  "patch_applied": false,
  "started_or_reused_observe_only": true,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "next_lane_x_batch": "LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION",
  "report": "run/audits/LANE-X-R31D5_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_183935_report.md"
}

## Current process/safety before stop
26823 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap
orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0

## Current pfeedcheck
===== PFEEDCHECK STRICT =====
2026-06-07T18:42:14+05:30

===== PROCESS STATUS =====
process_alive=True
    PID    PPID STAT %CPU %MEM     ELAPSED CMD
  26823       1 Sl   11.6  0.5       02:37 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap

===== LATEST LOG =====
-rw-rw-r-- 1 Lenovo Lenovo 1.7K Jun  7 18:39 run/live_capture/pfeeds_live_raw_capture_20260607_183935.log
last_log_lines:
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":26823,"thread":"MainThread","ts":"2026-06-07T13:09:37.065711+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.domain.instruments","message":"instrument_repository_loaded path=/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv format=csv records=39402 futures=6 calls=1500 puts=1522","process":26823,"thread":"MainThread","ts":"2026-06-07T13:09:40.601848+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":26823,"thread":"MainThread","ts":"2026-06-07T13:09:49.762506+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":26823,"thread":"MainThread","ts":"2026-06-07T13:09:49.764187+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"consumer_group_bootstrap_disabled","process":26823,"thread":"MainThread","ts":"2026-06-07T13:09:49.994480+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"runtime_service_starting service=feeds module=app.mme_scalpx.services.feeds instance_id=feeds:mme-scalpx:26823 replay=False","process":26823,"thread":"MainThread","ts":"2026-06-07T13:09:49.994974+00:00"}

===== REDIS STREAM RECORDING CHECK =====
redis_ping = True
lock_feeds_owner = feeds:mme-scalpx:26823
lock_feeds_ttl_ms = 25530

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=1        growth_5s=0
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=4        growth_5s=0
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=7187     growth_5s=96
errors                   system:errors:stream                       xlen=10006    growth_5s=0

status=RUNNING_BUT_RECORDING_NOT_PROVEN
remark=process alive, but Zerodha critical stream growth was not proven in this check window.

## Safe feeds stop if helper exists
===== PFEEDSTOP STRICT =====
stopping pid=26823
status=STOPPED_OR_STOP_REQUESTED

## Process/safety after stop
ACTIVE_RUNTIME_PROCESSES=NONE
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

## Decision
DECISION:
  Zerodha auth is valid.
  Sunday/off-market observe-only start produced no tick growth.
  pstack correctly fail-closed; features/strategy were not started.
  Candidate-watch is NOT ready until Monday market-time tick growth is proven.
  Retry R31D5 on Monday premarket/market time.

CLASSIFICATION=PASS_R31D5A_OFFMARKET_FEED_DEAD_FROZEN_SAFE_TO_RETRY_MONDAY_MARKET_TIME
