# LANE-X-R31D5_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_183935
2026-06-07T18:39:35+05:30

LAW=OBSERVE_ONLY_RETRY_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior auth proof
R31D4R=run/proofs/LANE-X-R31D4R_CORRECTED_ZERODHA_AUTH_VALIDATION_NO_PATCH_NO_START_NO_ORDER_20260607_183846.json
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
ACTIVE_RUNTIME_PROCESSES_BEFORE:
NONE

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
log=run/live_capture/pfeeds_live_raw_capture_20260607_183935.log
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
instrument_age_sec=290770
instrument_refresh_threshold_sec=583200
instrument_status=FRESH

===== PREFLIGHT: EXISTING MME/FEEDS PROCESS =====

===== PREFLIGHT: CLEAR FEEDS LOCK ONLY =====
before lock:feeds = None
before lock:feeds ttl = -2
deleted lock:feeds = 0
after lock:feeds = None
lock:execution untouched = None

===== STARTING FEEDS IN BACKGROUND =====

===== STARTUP STRICT HEALTH CHECK =====
pid=26823
redis_ping=True
log=run/live_capture/pfeeds_live_raw_capture_20260607_183935.log
lock_feeds_owner=None
lock_feeds_ttl_ms=-2
stream_lengths_after=
  fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=1 growth_8s=1
  fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0 growth_8s=0
  opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=4 growth_8s=4
  opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0 growth_8s=0
  opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0 growth_8s=0
  errors                   system:errors:stream                       xlen=10006 growth_8s=0
status=RUNNING_BUT_RECORDING_NOT_PROVEN
remark=pfeeds process is alive, but critical stream growth was not proven.

Terminal is free now. Use: pfeedcheck

## Start/reuse pstack
===== PSTACK OBSERVE-ONLY START / FAIL-CLOSED FEED GATE =====
services=feeds,features,strategy
execution=NOT_STARTED
risk=NOT_STARTED
stack_mode=observe_only_no_execution
settings_runtime_mode=live
2026-06-07T18:40:00+05:30

===== 0. PRECHECK: NO RISK / EXECUTION PROCESS =====

===== 1. START / VERIFY FEEDS =====
===== PFEEDS COMPREHENSIVE BACKGROUND START =====
project=/home/Lenovo/scalpx/projects/mme_scalpx
log=run/live_capture/pfeeds_live_raw_capture_20260607_184000.log
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
instrument_age_sec=290794
instrument_refresh_threshold_sec=583200
instrument_status=FRESH

===== PREFLIGHT: EXISTING MME/FEEDS PROCESS =====
status=ALREADY_RUNNING
pid=26823
remark=pfeeds already running. Use pfeedcheck or pfeeds --force.

===== 2. STRICT FEED GATE =====
===== PFEEDCHECK STRICT =====
2026-06-07T18:40:00+05:30

===== PROCESS STATUS =====
process_alive=True
    PID    PPID STAT %CPU %MEM     ELAPSED CMD
  26823   26777 Sl+  56.2  0.5       00:24 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap

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
lock_feeds_ttl_ms = 29063

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=1        growth_5s=0
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=4        growth_5s=0
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=4634     growth_5s=95
errors                   system:errors:stream                       xlen=10006    growth_5s=0

status=RUNNING_BUT_RECORDING_NOT_PROVEN
remark=process alive, but Zerodha critical stream growth was not proven in this check window.
pfeedcheck_rc=0

status=REFUSED
reason=pfeedcheck_not_healthy_recording
feed_gate_file=run/proofs/pstack_feed_gate_20260607_184000.txt
PSTACK_FAIL_CLOSED: features/strategy were NOT started.

## Post-start health checks
===== PFEEDCHECK STRICT =====
2026-06-07T18:40:16+05:30

===== PROCESS STATUS =====
process_alive=True
    PID    PPID STAT %CPU %MEM     ELAPSED CMD
  26823   26777 Sl+  36.0  0.5       00:39 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap

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
lock_feeds_ttl_ms = 23637

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=1        growth_5s=0
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=4        growth_5s=0
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=4928     growth_5s=95
errors                   system:errors:stream                       xlen=10006    growth_5s=0

status=RUNNING_BUT_RECORDING_NOT_PROVEN
remark=process alive, but Zerodha critical stream growth was not proven in this check window.

===== PSTACKCHECK =====
2026-06-07T18:40:21+05:30

===== PROCESS STATUS =====
--- feeds ---
Lenovo     26823   26777 32 18:39 pts/0    00:00:14 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap
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

STREAM_TICKS_MME_FUT_ZERODHA           ticks:mme:fut:zerodha:stream                  xlen=1        growth_5s=0
STREAM_TICKS_MME_FUT_DHAN              ticks:mme:fut:dhan:stream                     xlen=0        growth_5s=0
STREAM_TICKS_MME_OPT_SELECTED_ZERODHA  ticks:mme:opt:selected:zerodha:stream         xlen=4        growth_5s=0
STREAM_TICKS_MME_OPT_SELECTED_DHAN     ticks:mme:opt:selected:dhan:stream            xlen=0        growth_5s=0
STREAM_TICKS_MME_OPT_CONTEXT_DHAN      ticks:mme:opt:context:dhan:stream             xlen=0        growth_5s=0
STREAM_FEATURES_MME                    features:mme:stream                           xlen=4220     growth_5s=0
STREAM_DECISIONS_MME                   decisions:mme:stream                          xlen=1682     growth_5s=0
STREAM_SYSTEM_HEALTH                   system:health:stream                          xlen=5032     growth_5s=95
STREAM_SYSTEM_ERRORS                   system:errors:stream                          xlen=10006    growth_5s=0

===== LATEST FEATURE / DECISION SAMPLE KEYS =====

STREAM_FEATURES_MME = features:mme:stream
  latest_id = 1777888201390-0
  field_keys = ['family_features_json', 'family_features_version', 'family_surfaces_json', 'frame_id', 'frame_ts_ns', 'schema_version', 'service']

STREAM_DECISIONS_MME = decisions:mme:stream
  latest_id = 1777888475610-0
  field_keys = ['action', 'activation_action', 'activation_bridge_enabled', 'activation_candidate_count', 'activation_mode', 'activation_observed_action', 'activation_promoted', 'activation_reason', 'activation_report_json', 'activation_report_only', 'activation_safe_to_promote', 'activation_selected_action', 'activation_selected_branch_id', 'activation_selected_family_id', 'activation_selected_score', 'branch_id', 'confidence', 'consumer_view_json', 'data_valid', 'decision_id', 'diagnostics_json', 'doctrine_id', 'features_generated_at_ns', 'hold_only', 'instrument_key', 'instrument_token', 'option_symbol', 'order_type', 'payload_json', 'price', 'provider_ready_classic', 'provider_ready_miso', 'qty', 'reason', 'regime', 'safe_to_consume', 'schema_version', 'service', 'side', 'strategy_family_id']
  action=HOLD
  reason=hold_only_family_features_consumer_bridge
  ts_event_ns=1777888201413466932
  ts_ns=1777888201413466932

STREAM_SYSTEM_ERRORS = system:errors:stream
  latest_id = 1777888475661-0
  field_keys = ['detail', 'error_type', 'instance_id', 'selection_version', 'service_name', 'ts_ns']
  service_name=feeds
  instance_id=feeds:mme-scalpx:22458
  detail=FeedStartupError:feeds singleton lock refresh failed
  ts_ns=1777888475660662884

===== LOCKS =====
KEY_LOCK_FEEDS           lock:feeds                     value=feeds:mme-scalpx:26823 ttl_ms=23163
KEY_LOCK_STRATEGY        lock:strategy                  value=None ttl_ms=-2
KEY_LOCK_EXECUTION       lock:execution                 value=None ttl_ms=-2

[2J[HScalpX MME live observer | now=2026-06-07 18:40:27 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=feeds:mme-scalpx:26823 ttl=22743ms
lock:strategy: owner=- ttl=missing
lock:execution: owner=- ttl=missing

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: status=ERROR service=feeds instance=feeds:mme-scalpx:26823 age=0.37s ttl=5630ms message=-
health:features: MISSING (ttl=missing)
health:strategy: MISSING (ttl=missing)
health:risk: MISSING (ttl=missing)
health:execution: MISSING (ttl=missing)
health:monitor: MISSING (ttl=missing)
health:provider:runtime: status=ERROR service=feeds instance=feeds:mme-scalpx:26823 age=0.38s ttl=5632ms message=-
health:zerodha:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:26823 age=0.38s ttl=5629ms message=-
health:zerodha:execution: status=OK service=feeds instance=feeds:mme-scalpx:26823 age=0.38s ttl=5628ms message=-
health:dhan:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:26823 age=0.38s ttl=5629ms message=-
health:dhan:execution: status=OK service=feeds instance=feeds:mme-scalpx:26823 age=0.38s ttl=5630ms message=-
health:dhan:auth: status=OK service=feeds instance=feeds:mme-scalpx:26823 age=0.38s ttl=5629ms message=-

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
updated_at=2026-06-07 18:39:50 age=36.87s
frame_id=frame-1780837790464982874
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INCOMPLETE
validity_reason=missing_members:future,ce_atm,ce_atm1,pe_atm,pe_atm1
sync_ok=0
future_json: None
ts_frame_ns=1780837790464982874

[state:snapshot:mme:opt:selected]
updated_at=2026-06-07 18:39:50 age=36.87s
frame_id=frame-1780837790464982874
selection_version=mme-instruments-v1
provider_id=DHAN
validity=INCOMPLETE
validity_reason=missing_members:future,ce_atm,ce_atm1,pe_atm,pe_atm1
sync_ok=0
ts_span_ms=0
ce_atm_json: None
ce_atm1_json: None
pe_atm_json: None
pe_atm1_json: None
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780837790464982874

[state:snapshot:mme:fut:active]
updated_at=2026-06-07 18:39:50 age=36.87s
frame_id=frame-1780837790464982874
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INCOMPLETE
validity_reason=missing_members:future,ce_atm,ce_atm1,pe_atm,pe_atm1
sync_ok=0
future_json: None
ts_frame_ns=1780837790464982874

[state:snapshot:mme:opt:selected:active]
updated_at=2026-06-07 18:39:50 age=36.87s
frame_id=frame-1780837790464982874
selection_version=mme-instruments-v1
provider_id=DHAN
validity=INCOMPLETE
validity_reason=missing_members:future,ce_atm,ce_atm1,pe_atm,pe_atm1
sync_ok=0
ts_span_ms=0
ce_atm_json: None
ce_atm1_json: None
pe_atm_json: None
pe_atm1_json: None
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780837790464982874

[state:snapshot:mme:fut:zerodha]
updated_at=2026-06-07 18:39:50 age=36.89s
frame_id=frame-1780837790445147329
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INCOMPLETE
validity_reason=missing_members:future,ce_atm,ce_atm1,pe_atm,pe_atm1
sync_ok=0
future_json: None
ts_frame_ns=1780837790445147329

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
updated_at=2026-06-07 18:39:50 age=36.87s
frame_id=frame-1780837790465920535
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INCOMPLETE
validity_reason=missing_members:future,ce_atm,ce_atm1,pe_atm,pe_atm1
sync_ok=0
ts_span_ms=0
ce_atm_json: None
ce_atm1_json: None
pe_atm_json: None
pe_atm1_json: None
stale_mask_json: []
is_active_provider_snapshot=0
ts_frame_ns=1780837790465920535

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
updated_at=2026-06-07 18:40:27 age=0.01s
futures_marketdata_provider_id=ZERODHA
selected_option_marketdata_provider_id=DHAN
option_context_provider_id=DHAN
execution_primary_provider_id=ZERODHA
execution_fallback_provider_id=DHAN
family_runtime_mode=OBSERVE_ONLY
failover_mode=MANUAL
override_mode=AUTO
transition_reason=BOOTSTRAP
provider_transition_seq=5
execution_fallback_status=DISABLED
execution_primary_status=UNAVAILABLE
failover_active=False
futures_marketdata_status=UNAVAILABLE
last_update_ns=1780837827331429914
message=Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled
option_context_status=UNAVAILABLE
pending_failover=False
selected_option_marketdata_status=UNAVAILABLE
ts_event_ns=1780837827331429914

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-05-04 15:20:01 age=2949626.03s
frame_id=features-1777888201323397710
feature_state_json: {"frame_id":"features-1777888201323397710","frame_ts_ns":1777888201323397710,"frame_valid":false,"warmup_complete":true,"regime":"NORMAL","selected_option":{"side":"CALL","ltp":0.0,"spread":0.0,"spread_ratio":0.0,"depth_total":0.0,"depth_ok":false,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":null,"response_efficiency":null,"tradability_ok":false}}
family_frames_json: {"mist_call":{"frame_id":"mist_call-1777888201323397710","frame_ts_ns":1777888201323397710,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":null,"active_selected_option_provider_id":null,"active_option_context_provider_id":null,"instrument_key":null,"instrument_token":null,"option_symbol":null,"strike":null,"option_price":null,"tick_size":0.05,"target_points":5.0,"stop_points":4.0,"eligible":false,"tr...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1777888201323397710,"frame_id":"features-1777888201323397710","frame_ts_ns":1777888201323397710,"ts_event_ns":1777888201323397710,"frame_valid":false,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1777888201323397632,"snapshot":{"valid":false,"validity":"MARKETDATA_INCOMPLETE_OR_UNSYNCED","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmu...
family_features_version=1.1
frame_ts_ns=1777888201323397710
frame_valid=0
strategy_mode=AUTO
system_state=DISABLED
ts_event_ns=1777888201323397710
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-05-04 15:20:01 age=2949626.05s
family_features_version=1.1
frame_ts_ns=1777888201323397710
regime=NORMAL

[state:option:confirm]
updated_at=2026-05-04 15:20:01 age=2949626.05s
frame_ts_ns=1777888201323397710

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1780837790444-0 | ts=2026-06-05 22:25:12 | age=159315.38s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23440.0 | bid= | ask=

[ticks:mme:opt:stream]
no entries

[features:mme:stream]
id=1777888201390-0 | ts=2026-05-04 15:20:01 | age=2949626.06s | frame_id=features-1777888201323397710
id=1777888201221-0 | ts=2026-05-04 15:20:01 | age=2949626.22s | frame_id=features-1777888201156516724

[system:health:stream]
id=1780837827333-0 | ts=2026-06-07 18:40:27 | age=0.05s | service_name=feeds | instance_id=feeds:mme-scalpx:26823 | status=ERROR | detail=tick_flow_dead | selection_version=mme-instruments-v1
id=1780837827280-0 | ts=2026-06-07 18:40:27 | age=0.10s | service_name=feeds | instance_id=feeds:mme-scalpx:26823 | status=ERROR | detail=tick_flow_dead | selection_version=mme-instruments-v1

[system:errors:stream]
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=2949351.72s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888475608-0 | ts=2026-05-04 15:24:33 | age=2949354.37s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=LockError:Failed to refresh lock 'lock:feeds': Timeout re... | selection_version=mme-instruments-v1

[ticks:mme:fut:zerodha:stream]
id=1780837790444-0 | ts=2026-06-05 22:25:12 | age=159315.38s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23440.0 | bid= | ask=

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1780837790465-0 | ts=2026-06-05 22:39:17 | age=158470.38s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923300PE | instrument_token=10825986 | trading_symbol=NIFTY2660923300PE | instrument_role=PE_ATM1 | ltp=84.7 | bid= | ask=
id=1780837790458-0 | ts=2026-06-05 22:39:17 | age=158470.38s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923350PE | instrument_token=10827010 | trading_symbol=NIFTY2660923350PE | instrument_role=PE_ATM | ltp=105.7 | bid= | ask=

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1780837790354-0 | ts=2026-06-07 18:39:50 | age=37.06s | family_runtime_mode=OBSERVE_ONLY
id=1780837790353-0 | ts=2026-06-07 18:39:50 | age=37.06s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=2949351.72s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888475608-0 | ts=2026-05-04 15:24:33 | age=2949354.38s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=LockError:Failed to refresh lock 'lock:feeds': Timeout re... | selection_version=mme-instruments-v1
id=1777888201411-0 | ts=2026-05-04 15:20:01 | age=2949625.97s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201359-0 | ts=2026-05-04 15:20:01 | age=2949626.03s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201307-0 | ts=2026-05-04 15:20:01 | age=2949626.08s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201255-0 | ts=2026-05-04 15:20:01 | age=2949626.13s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201203-0 | ts=2026-05-04 15:20:01 | age=2949626.18s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201151-0 | ts=2026-05-04 15:20:01 | age=2949626.23s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201099-0 | ts=2026-05-04 15:20:01 | age=2949626.29s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201047-0 | ts=2026-05-04 15:20:01 | age=2949626.34s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

## Safety after start
ACTIVE_RUNTIME_PROCESSES_AFTER:
26823 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap

orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=REVIEW_R31D5_PSTACK_FAIL_CLOSED_DO_NOT_RUN_CANDIDATE_WATCH
