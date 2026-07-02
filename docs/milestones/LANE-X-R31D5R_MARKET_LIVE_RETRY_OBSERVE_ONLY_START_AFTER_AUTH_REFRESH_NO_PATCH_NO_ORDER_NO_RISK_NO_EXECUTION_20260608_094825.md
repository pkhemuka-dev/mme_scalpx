# LANE-X-R31D5R_MARKET_LIVE_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_094825
2026-06-08T09:48:25+05:30

LAW=MARKET_LIVE_OBSERVE_ONLY_RETRY_NO_PATCH_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior auth proof
R31D4R=run/proofs/LANE-X-R31D4R_CORRECTED_ZERODHA_AUTH_VALIDATION_NO_PATCH_NO_START_NO_ORDER_20260607_183846.json
R31D5A=run/proofs/LANE-X-R31D5A_OFFMARKET_FEED_DEAD_FREEZE_AND_SAFE_FEEDS_STOP_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_184214.json
{
  "tag": "LANE-X-R31D4R_CORRECTED_ZERODHA_AUTH_VALIDATION_NO_PATCH_NO_START_NO_ORDER_20260607_183846",
  "classification": "PASS_R31D4R_ZERODHA_AUTH_VALID_READY_TO_RETRY_OBSERVE_ONLY_START",
  "patch_applied": false,
  "started_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "secret_values_printed": false,
  "auth_rc": "0",
  "next_lane_x_batch": "LANE-X-R31D5_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION",
  "report": "run/audits/LANE-X-R31D4R_CORRECTED_ZERODHA_AUTH_VALIDATION_NO_PATCH_NO_START_NO_ORDER_20260607_183846_report.md"
}

## Safety before start
35846 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0

## Observe-only env
SCALPX_OBSERVE_ONLY=1
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=UNSET
SCALPX_ENABLE_PAPER=UNSET
SCALPX_ENABLE_LIVE=UNSET

## Start/reuse pfeeds
===== PFEEDS COMPREHENSIVE BACKGROUND START =====
project=/home/Lenovo/scalpx/projects/mme_scalpx
log=run/live_capture/pfeeds_live_raw_capture_20260608_094825.log
mode=normal

===== PREFLIGHT: ZERODHA SHARED TOKEN GUARD =====
ensure_zerodha_shared_token=PASS
shared_token_file= /home/Lenovo/scalpx/common/secrets/shared/tokens.json
before_broker= zerodha
after_broker= zerodha
access_token= <present>
api_key= missing
changed= False

===== PREFLIGHT: REDIS =====
redis_ping=True

===== PREFLIGHT: INSTRUMENT MASTER =====
instrument_file=/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv
instrument_age_sec=345299
instrument_refresh_threshold_sec=583200
instrument_status=FRESH

===== PREFLIGHT: EXISTING MME/FEEDS PROCESS =====

===== PREFLIGHT: CLEAR FEEDS LOCK ONLY =====
before lock:feeds = feeds:mme-scalpx:35846
before lock:feeds ttl = 20533
deleted lock:feeds = 1
after lock:feeds = None
lock:execution untouched = execution:mme-scalpx:35846

===== STARTING FEEDS IN BACKGROUND =====

===== STARTUP STRICT HEALTH CHECK =====
pid=36507
redis_ping=True
log=run/live_capture/pfeeds_live_raw_capture_20260608_094825.log
lock_feeds_owner=feeds:mme-scalpx:35846
lock_feeds_ttl_ms=20238
stream_lengths_after=
  fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=139 growth_8s=2
  fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0 growth_8s=0
  opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=758 growth_8s=15
  opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0 growth_8s=0
  opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0 growth_8s=0
  errors                   system:errors:stream                       xlen=10007 growth_8s=0
status=RUNNING_BUT_RECORDING_NOT_PROVEN
remark=pfeeds process is alive, but critical stream growth was not proven.

Terminal is free now. Use: pfeedcheck

## Feed growth check
===== PFEEDCHECK STRICT =====
2026-06-08T09:48:56+05:30

===== PROCESS STATUS =====
process_alive=False
pidfile_pid=36507

===== LATEST LOG =====
-rw-rw-r-- 1 Lenovo Lenovo 2.7K Jun  8 09:48 run/live_capture/pfeeds_live_raw_capture_20260608_094825.log
last_log_lines:
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:26.452477+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.domain.instruments","message":"instrument_repository_loaded path=/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv format=csv records=39402 futures=6 calls=1500 puts=1522","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:30.160261+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:40.768893+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:40.770230+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"consumer_group_bootstrap_disabled","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:40.908095+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"runtime_service_starting service=feeds module=app.mme_scalpx.services.feeds instance_id=feeds:mme-scalpx:36507 replay=False","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:40.908687+00:00"}
{"level":"ERROR","logger":"app.mme_scalpx.main","message":"unhandled_fatal_error error=feeds singleton lock not acquired\nTraceback (most recent call last):\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 2009, in main\n    return run_service(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 1751, in run_service\n    return _run_service_once(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 1737, in _run_service_once\n    result = runner(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\", line 2701, in run\n    raise FeedStartupError(\"feeds singleton lock not acquired\")\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\n","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:40.949713+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"shutdown_completed_cleanly","process":36507,"thread":"MainThread","ts":"2026-06-08T04:18:40.949971+00:00"}

===== REDIS STREAM RECORDING CHECK =====
redis_ping = True
lock_feeds_owner = feeds:mme-scalpx:35846
lock_feeds_ttl_ms = 20836

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=143      growth_5s=1
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=791      growth_5s=10
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=8936     growth_5s=19
errors                   system:errors:stream                       xlen=10007    growth_5s=0

classic_degraded_note=ZERODHA_CRITICAL_GROWTH_OK_DHAN_INCOMPLETE_MISO_BLOCKED
status=NOT_HEALTHY_PROCESS_DEAD
remark=pfeeds process is not alive.

## Start/reuse pstack only if feed gate allows
===== PSTACK OBSERVE-ONLY START / FAIL-CLOSED FEED GATE =====
services=feeds,features,strategy
execution=NOT_STARTED
risk=NOT_STARTED
stack_mode=observe_only_no_execution
settings_runtime_mode=live
2026-06-08T09:49:02+05:30

===== 0. PRECHECK: NO RISK / EXECUTION PROCESS =====

===== 1. START / VERIFY FEEDS =====
===== PFEEDS COMPREHENSIVE BACKGROUND START =====
project=/home/Lenovo/scalpx/projects/mme_scalpx
log=run/live_capture/pfeeds_live_raw_capture_20260608_094902.log
mode=normal

===== PREFLIGHT: ZERODHA SHARED TOKEN GUARD =====
ensure_zerodha_shared_token=PASS
shared_token_file= /home/Lenovo/scalpx/common/secrets/shared/tokens.json
before_broker= zerodha
after_broker= zerodha
access_token= <present>
api_key= missing
changed= False

===== PREFLIGHT: REDIS =====
redis_ping=True

===== PREFLIGHT: INSTRUMENT MASTER =====
instrument_file=/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv
instrument_age_sec=345336
instrument_refresh_threshold_sec=583200
instrument_status=FRESH

===== PREFLIGHT: EXISTING MME/FEEDS PROCESS =====

===== PREFLIGHT: CLEAR FEEDS LOCK ONLY =====
before lock:feeds = feeds:mme-scalpx:35846
before lock:feeds ttl = 25155
deleted lock:feeds = 1
after lock:feeds = None
lock:execution untouched = execution:mme-scalpx:35846

===== STARTING FEEDS IN BACKGROUND =====

===== STARTUP STRICT HEALTH CHECK =====
pid=36731
redis_ping=True
log=run/live_capture/pfeeds_live_raw_capture_20260608_094902.log
lock_feeds_owner=feeds:mme-scalpx:35846
lock_feeds_ttl_ms=25281
stream_lengths_after=
  fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=146 growth_8s=0
  fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0 growth_8s=0
  opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=825 growth_8s=16
  opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0 growth_8s=0
  opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0 growth_8s=0
  errors                   system:errors:stream                       xlen=10007 growth_8s=0
status=RUNNING_BUT_RECORDING_NOT_PROVEN
remark=pfeeds process is alive, but critical stream growth was not proven.

Terminal is free now. Use: pfeedcheck

===== 2. STRICT FEED GATE =====
===== PFEEDCHECK STRICT =====
2026-06-08T09:49:21+05:30

===== PROCESS STATUS =====
process_alive=False
pidfile_pid=36731

===== LATEST LOG =====
-rw-rw-r-- 1 Lenovo Lenovo 2.7K Jun  8 09:49 run/live_capture/pfeeds_live_raw_capture_20260608_094902.log
last_log_lines:
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:03.371103+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.domain.instruments","message":"instrument_repository_loaded path=/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv format=csv records=39402 futures=6 calls=1500 puts=1522","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:07.000792+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.630498+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.633280+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"consumer_group_bootstrap_disabled","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.791903+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"runtime_service_starting service=feeds module=app.mme_scalpx.services.feeds instance_id=feeds:mme-scalpx:36731 replay=False","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.792345+00:00"}
{"level":"ERROR","logger":"app.mme_scalpx.main","message":"unhandled_fatal_error error=feeds singleton lock not acquired\nTraceback (most recent call last):\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 2009, in main\n    return run_service(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 1751, in run_service\n    return _run_service_once(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 1737, in _run_service_once\n    result = runner(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\", line 2701, in run\n    raise FeedStartupError(\"feeds singleton lock not acquired\")\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\n","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.827514+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"shutdown_completed_cleanly","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.827764+00:00"}

===== REDIS STREAM RECORDING CHECK =====
redis_ping = True
lock_feeds_owner = feeds:mme-scalpx:35846
lock_feeds_ttl_ms = 26842

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=148      growth_5s=2
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=836      growth_5s=10
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=9034     growth_5s=21
errors                   system:errors:stream                       xlen=10007    growth_5s=0

classic_degraded_note=ZERODHA_CRITICAL_GROWTH_OK_DHAN_INCOMPLETE_MISO_BLOCKED
status=NOT_HEALTHY_PROCESS_DEAD
remark=pfeeds process is not alive.
pfeedcheck_rc=0

status=REFUSED
reason=pfeedcheck_not_healthy_recording
feed_gate_file=run/proofs/pstack_feed_gate_20260608_094921.txt
PSTACK_FAIL_CLOSED: features/strategy were NOT started.

## Stack health checks
===== PFEEDCHECK STRICT =====
2026-06-08T09:49:39+05:30

===== PROCESS STATUS =====
process_alive=False
pidfile_pid=36731

===== LATEST LOG =====
-rw-rw-r-- 1 Lenovo Lenovo 2.7K Jun  8 09:49 run/live_capture/pfeeds_live_raw_capture_20260608_094902.log
last_log_lines:
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:03.371103+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.domain.instruments","message":"instrument_repository_loaded path=/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv format=csv records=39402 futures=6 calls=1500 puts=1522","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:07.000792+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"bootstrap_provider_completed provider=app.mme_scalpx.integrations.bootstrap_provider:provide mode=returned_dict runtime_instruments=1 feed_adapter=1 market_data_adapter=0 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.630498+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"dependency_surfaces_resolved runtime_instruments=1 feed_adapter=1 market_data_adapter=1 feed_adapters=1 zerodha_feed_adapter=1 dhan_feed_adapter=1 dhan_context_adapter=1 broker=1","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.633280+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"consumer_group_bootstrap_disabled","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.791903+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"runtime_service_starting service=feeds module=app.mme_scalpx.services.feeds instance_id=feeds:mme-scalpx:36731 replay=False","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.792345+00:00"}
{"level":"ERROR","logger":"app.mme_scalpx.main","message":"unhandled_fatal_error error=feeds singleton lock not acquired\nTraceback (most recent call last):\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 2009, in main\n    return run_service(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 1751, in run_service\n    return _run_service_once(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\", line 1737, in _run_service_once\n    result = runner(context)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\", line 2701, in run\n    raise FeedStartupError(\"feeds singleton lock not acquired\")\napp.mme_scalpx.services.feeds.FeedStartupError: feeds singleton lock not acquired\n","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.827514+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"shutdown_completed_cleanly","process":36731,"thread":"MainThread","ts":"2026-06-08T04:19:17.827764+00:00"}

===== REDIS STREAM RECORDING CHECK =====
redis_ping = True
lock_feeds_owner = feeds:mme-scalpx:35846
lock_feeds_ttl_ms = 19681

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=156      growth_5s=3
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=867      growth_5s=9
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=9109     growth_5s=22
errors                   system:errors:stream                       xlen=10007    growth_5s=0

classic_degraded_note=ZERODHA_CRITICAL_GROWTH_OK_DHAN_INCOMPLETE_MISO_BLOCKED
status=NOT_HEALTHY_PROCESS_DEAD
remark=pfeeds process is not alive.

===== PSTACKCHECK =====
2026-06-08T09:49:44+05:30

===== PROCESS STATUS =====
--- feeds ---
not running
--- features ---
not running
--- strategy ---
not running
--- execution ---
not running
--- risk ---
not running
--- monitor ---
not running
--- report ---
not running

===== REDIS SURFACE CHECK =====
redis_ping = True

STREAM_TICKS_MME_FUT_ZERODHA           ticks:mme:fut:zerodha:stream                  xlen=158      growth_5s=2
STREAM_TICKS_MME_FUT_DHAN              ticks:mme:fut:dhan:stream                     xlen=0        growth_5s=0
STREAM_TICKS_MME_OPT_SELECTED_ZERODHA  ticks:mme:opt:selected:zerodha:stream         xlen=876      growth_5s=9
STREAM_TICKS_MME_OPT_SELECTED_DHAN     ticks:mme:opt:selected:dhan:stream            xlen=0        growth_5s=0
STREAM_TICKS_MME_OPT_CONTEXT_DHAN      ticks:mme:opt:context:dhan:stream             xlen=0        growth_5s=0
STREAM_FEATURES_MME                    features:mme:stream                           xlen=4321     growth_5s=1
STREAM_DECISIONS_MME                   decisions:mme:stream                          xlen=2179     growth_5s=5
STREAM_SYSTEM_HEALTH                   system:health:stream                          xlen=9128     growth_5s=18
STREAM_SYSTEM_ERRORS                   system:errors:stream                          xlen=10007    growth_5s=0

===== LATEST FEATURE / DECISION SAMPLE KEYS =====

STREAM_FEATURES_MME = features:mme:stream
  latest_id = 1780892387840-0
  field_keys = ['consumer_view_json', 'family_features_json', 'family_features_version', 'family_surfaces_json', 'frame_id', 'frame_ts_ns', 'o23p_r6b_r3_family_payload_publish_patch', 'schema_version', 'service']

STREAM_DECISIONS_MME = decisions:mme:stream
  latest_id = 1780892388835-0
  field_keys = ['action', 'activation_action', 'activation_bridge_enabled', 'activation_candidate_count', 'activation_mode', 'activation_observed_action', 'activation_promoted', 'activation_reason', 'activation_report_json', 'activation_report_only', 'activation_safe_to_promote', 'activation_selected_action', 'activation_selected_branch_id', 'activation_selected_family_id', 'activation_selected_score', 'branch_id', 'confidence', 'consumer_view_json', 'data_valid', 'decision_id', 'diagnostics_json', 'doctrine_id', 'family_features_json', 'family_frames_json', 'family_scope_candidates_json', 'family_surfaces_json', 'features_generated_at_ns', 'hold_only', 'instrument_key', 'instrument_token', 'o23p_r10_decision_family_payload_patch', 'o23p_r13_decision_family_payload_patch', 'o23q_r13_family_scope_candidates_projection_patch', 'option_symbol', 'order_type', 'payload_json', 'price', 'provider_ready_classic', 'provider_ready_miso', 'qty']
  action=HOLD
  reason=hold_only_family_features_consumer_bridge
  ts_event_ns=1780892388478745813
  ts_ns=1780892388478745813

STREAM_SYSTEM_ERRORS = system:errors:stream
  latest_id = 1780891924891-0
  field_keys = ['error', 'error_type', 'instance_id', 'service', 'ts_event_ns', 'ts_ns', 'where']
  instance_id=strategy:mme-scalpx:35846
  ts_event_ns=1780891924890571570
  ts_ns=1780891924890571570

===== LOCKS =====
KEY_LOCK_FEEDS           lock:feeds                     value=feeds:mme-scalpx:35846 ttl_ms=19574
KEY_LOCK_STRATEGY        lock:strategy                  value=None ttl_ms=-2
KEY_LOCK_EXECUTION       lock:execution                 value=execution:mme-scalpx:35846 ttl_ms=21544

[2J[HScalpX MME live observer | now=2026-06-08 09:49:50 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=feeds:mme-scalpx:35846 ttl=19128ms
lock:strategy: owner=- ttl=missing
lock:execution: owner=execution:mme-scalpx:35846 ttl=21098ms

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=0.51s ttl=5609ms message=-
health:features: status=OK service=features instance=features:mme-scalpx:35846 age=3.34s ttl=11668ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:35846 age=1.65s ttl=13388ms message=-
health:risk: status=WARN service=risk instance=risk:mme-scalpx:35846 age=4.46s ttl=6007ms message=CONTROLLED_PAPER_NOT_ARMED
health:execution: status=OK service=execution instance=execution:mme-scalpx:35846 age=0.12s ttl=9881ms message=-
health:monitor: status=WARN service=monitor instance=monitor:mme-scalpx:35846 age=1.85s ttl=8148ms message=report:missing_heartbeat,runtime_mode=live
health:provider:runtime: status=WARN service=feeds instance=feeds:mme-scalpx:35846 age=0.52s ttl=5878ms message=-
health:zerodha:marketdata: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=0.52s ttl=5622ms message=-
health:zerodha:execution: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=0.52s ttl=5700ms message=-
health:dhan:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:35846 age=0.52s ttl=5703ms message=-
health:dhan:execution: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=0.52s ttl=5770ms message=-
health:dhan:auth: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=0.52s ttl=5731ms message=-

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
updated_at=2026-06-08 15:19:44 age=0.00s
frame_id=frame-1780892389519040981
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INVALID_MEMBER
validity_reason=invalid_members:FUTURES
sync_ok=1
ts_span_ms=4000
future_json: symbol=NIFTY26JUNFUT ltp=23211.0 bid=23211.0 ask=23216.0 bid_qty_5=2925 ask_qty_5=1755 age_ms=0 validity=ANOMALY_CLAMPED strike=0.0
stale_mask_json: []
ask=23216.0
ask_qty_5=1755
bid=23211.0
bid_qty_5=2925
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780892389519040981
ltp=23211.0
provider_role=futures_marketdata
tick_validity=ANOMALY_CLAMPED
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780912184000000000
ts_frame_ns=1780892389519040981

[state:snapshot:mme:opt:selected]
updated_at=2026-06-08 09:49:49 age=0.99s
frame_id=frame-1780892389519040981
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INVALID_MEMBER
validity_reason=invalid_members:FUTURES
sync_ok=1
ts_span_ms=4000
ce_atm_json: symbol=NIFTY2660923150CE ltp=128.95 bid=129.05 ask=129.4 bid_qty_5=6110 ask_qty_5=5980 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=104.85 bid=104.85 ask=105.0 bid_qty_5=4875 ask_qty_5=8190 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=117.75 bid=117.5 ask=117.8 bid_qty_5=7995 ask_qty_5=8190 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=95.75 bid=95.25 ask=95.5 bid_qty_5=10530 ask_qty_5=17810 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780892389519040981

[state:snapshot:mme:fut:active]
updated_at=2026-06-08 15:19:44 age=0.00s
frame_id=frame-1780892389519040981
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INVALID_MEMBER
validity_reason=invalid_members:FUTURES
sync_ok=1
ts_span_ms=4000
future_json: symbol=NIFTY26JUNFUT ltp=23211.0 bid=23211.0 ask=23216.0 bid_qty_5=2925 ask_qty_5=1755 age_ms=0 validity=ANOMALY_CLAMPED strike=0.0
stale_mask_json: []
ask=23216.0
ask_qty_5=1755
bid=23211.0
bid_qty_5=2925
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780892389519040981
ltp=23211.0
provider_role=futures_marketdata
tick_validity=ANOMALY_CLAMPED
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780912184000000000
ts_frame_ns=1780892389519040981

[state:snapshot:mme:opt:selected:active]
updated_at=2026-06-08 09:49:49 age=0.99s
frame_id=frame-1780892389519040981
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INVALID_MEMBER
validity_reason=invalid_members:FUTURES
sync_ok=1
ts_span_ms=4000
ce_atm_json: symbol=NIFTY2660923150CE ltp=128.95 bid=129.05 ask=129.4 bid_qty_5=6110 ask_qty_5=5980 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=104.85 bid=104.85 ask=105.0 bid_qty_5=4875 ask_qty_5=8190 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=117.75 bid=117.5 ask=117.8 bid_qty_5=7995 ask_qty_5=8190 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=95.75 bid=95.25 ask=95.5 bid_qty_5=10530 ask_qty_5=17810 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780892389519040981

[state:snapshot:mme:fut:zerodha]
updated_at=2026-06-08 15:19:44 age=0.00s
frame_id=frame-1780892387086121800
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INVALID_MEMBER
validity_reason=invalid_members:FUTURES
sync_ok=0
ts_span_ms=3000
future_json: symbol=NIFTY26JUNFUT ltp=23211.0 bid=23211.0 ask=23216.0 bid_qty_5=2925 ask_qty_5=1755 age_ms=0 validity=ANOMALY_CLAMPED strike=0.0
stale_mask_json: []
ask=23216.0
ask_qty_5=1755
bid=23211.0
bid_qty_5=2925
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780892387086121800
ltp=23211.0
provider_role=futures_marketdata
tick_validity=ANOMALY_CLAMPED
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780912184000000000
ts_frame_ns=1780892387086121800

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
updated_at=2026-06-08 09:49:49 age=0.97s
frame_id=frame-1780892389544036691
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INVALID_MEMBER
validity_reason=invalid_members:FUTURES
sync_ok=0
ts_span_ms=4000
ce_atm_json: symbol=NIFTY2660923150CE ltp=128.95 bid=129.05 ask=129.4 bid_qty_5=6110 ask_qty_5=5980 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=104.85 bid=104.85 ask=105.0 bid_qty_5=4875 ask_qty_5=8190 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=117.75 bid=117.5 ask=117.8 bid_qty_5=7995 ask_qty_5=8190 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=95.75 bid=95.25 ask=95.5 bid_qty_5=10530 ask_qty_5=17810 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780892389544036691

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
updated_at=2026-06-08 09:49:49 age=0.53s
futures_marketdata_provider_id=ZERODHA
selected_option_marketdata_provider_id=ZERODHA
option_context_provider_id=DHAN
execution_primary_provider_id=ZERODHA
execution_fallback_provider_id=DHAN
family_runtime_mode=OBSERVE_ONLY
failover_mode=MANUAL
override_mode=AUTO
transition_reason=BOOTSTRAP
provider_transition_seq=1491
execution_fallback_status=DISABLED
execution_primary_status=HEALTHY
failover_active=True
futures_marketdata_status=HEALTHY
last_update_ns=1780892389986712249
message=Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled
option_context_status=UNAVAILABLE
pending_failover=False
selected_option_marketdata_status=FAILOVER_ACTIVE
ts_event_ns=1780892389986712249

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-06-08 09:49:47 age=3.26s
frame_id=features-1780892387294272447
feature_state_json: {"frame_id":"features-1780892387294272447","frame_ts_ns":1780892387294272447,"frame_valid":true,"warmup_complete":true,"regime":"FAST","selected_option":{"side":"CALL","ltp":95.25,"spread":0.04999999999999716,"spread_ratio":0.000521104742053123,"depth_total":9815.0,"depth_ok":true,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":-1.700000000000017,"response_efficiency":5.666666666666509,"tradability_ok":true},"selected_option_rich":{"side":"CALL","ltp":95.25,"spread":0.049...
family_frames_json: {"mist_call":{"frame_id":"mist_call-1780892387294272447","frame_ts_ns":1780892387294272447,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"10823170","instrument_token":"10823170","option_symbol":"NIFTY2660923150CE","strike":23150.0,"option_price":128.35,"tick_size":0.05,"target_points...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1780892387294272447,"frame_id":"features-1780892387294272447","frame_ts_ns":1780892387294272447,"ts_event_ns":1780892387294272447,"frame_valid":true,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1780892387294272512,"snapshot":{"valid":true,"validity":"OK","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1780892387294272447
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1780892387294272447
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-08 09:49:47 age=3.38s
family_features_version=1.1
frame_ts_ns=1780892387294272447
regime=FAST

[state:option:confirm]
updated_at=2026-06-08 09:49:47 age=3.38s
frame_ts_ns=1780892387294272447

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1780892387049-0 | ts=2026-06-08 15:19:45 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23211.0 | bid=23212.4 | ask=23216.0
id=1780892385669-0 | ts=2026-06-08 15:19:44 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23211.0 | bid=23211.0 | ask=23216.0

[ticks:mme:opt:stream]
id=1780892390643-0 | ts=2026-06-08 15:19:49 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923100PE | instrument_token=10821890 | trading_symbol=NIFTY2660923100PE | instrument_role=PE_ATM1 | ltp=95.75 | bid=95.4 | ask=95.7
id=1780892389527-0 | ts=2026-06-08 15:19:48 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923100PE | instrument_token=10821890 | trading_symbol=NIFTY2660923100PE | instrument_role=PE_ATM1 | ltp=95.75 | bid=95.25 | ask=95.5

[features:mme:stream]
id=1780892387840-0 | ts=2026-06-08 09:49:47 | age=3.40s | frame_id=features-1780892387294272447
id=1780892383202-0 | ts=2026-06-08 09:49:42 | age=8.07s | frame_id=features-1780892382615308846

[system:health:stream]
id=1780892390081-0 | ts=2026-06-08 09:49:50 | age=0.61s | service_name=feeds | instance_id=feeds:mme-scalpx:35846 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1
id=1780892389634-0 | ts=2026-06-08 09:49:49 | age=1.06s | service_name=feeds | instance_id=feeds:mme-scalpx:35846 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1780891924891-0 | ts=2026-06-08 09:42:04 | age=465.80s | instance_id=strategy:mme-scalpx:35846 | error_type=FeatureFamilyContractError
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=3003915.03s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

[ticks:mme:fut:zerodha:stream]
id=1780892387035-0 | ts=2026-06-08 15:19:45 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23211.0 | bid=23212.4 | ask=23216.0
id=1780892385621-0 | ts=2026-06-08 15:19:44 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23211.0 | bid=23211.0 | ask=23216.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1780892390549-0 | ts=2026-06-08 15:19:49 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923100PE | instrument_token=10821890 | trading_symbol=NIFTY2660923100PE | instrument_role=PE_ATM1 | ltp=95.75 | bid=95.4 | ask=95.7
id=1780892389520-0 | ts=2026-06-08 15:19:48 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923100PE | instrument_token=10821890 | trading_symbol=NIFTY2660923100PE | instrument_role=PE_ATM1 | ltp=95.75 | bid=95.25 | ask=95.5

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1780892390679-0 | ts=2026-06-08 09:49:50 | age=0.15s | family_runtime_mode=OBSERVE_ONLY
id=1780892390050-0 | ts=2026-06-08 09:49:49 | age=0.71s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1780891924891-0 | ts=2026-06-08 09:42:04 | age=465.80s | instance_id=strategy:mme-scalpx:35846 | error_type=FeatureFamilyContractError
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=3003915.03s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888475608-0 | ts=2026-05-04 15:24:33 | age=3003917.69s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=LockError:Failed to refresh lock 'lock:feeds': Timeout re... | selection_version=mme-instruments-v1
id=1777888201411-0 | ts=2026-05-04 15:20:01 | age=3004189.28s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201359-0 | ts=2026-05-04 15:20:01 | age=3004189.34s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201307-0 | ts=2026-05-04 15:20:01 | age=3004189.39s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201255-0 | ts=2026-05-04 15:20:01 | age=3004189.44s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201203-0 | ts=2026-05-04 15:20:01 | age=3004189.49s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201151-0 | ts=2026-05-04 15:20:01 | age=3004189.54s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201099-0 | ts=2026-05-04 15:20:01 | age=3004189.60s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

## Safety after start
35846 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=REVIEW_R31D5R_PSTACK_FAIL_CLOSED_DO_NOT_RUN_CANDIDATE_WATCH
