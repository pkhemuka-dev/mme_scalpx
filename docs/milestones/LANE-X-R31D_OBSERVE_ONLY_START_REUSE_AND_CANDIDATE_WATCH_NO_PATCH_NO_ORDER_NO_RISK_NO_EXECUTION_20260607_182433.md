# LANE-X-R31D_OBSERVE_ONLY_START_REUSE_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260607_182433
2026-06-07T18:24:33+05:30

LAW=OBSERVE_ONLY_START_REUSE_NO_PATCH_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31C proof
R31C=run/proofs/LANE-X-R31C_MONDAY_OBSERVE_ONLY_PREMARKET_SAFETY_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_20260607_175928.json
{
  "tag": "LANE-X-R31C_MONDAY_OBSERVE_ONLY_PREMARKET_SAFETY_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_20260607_175928",
  "classification": "PASS_LANE_X_R31C_PREMARKET_SAFETY_AND_CANDIDATE_WATCH_READY_FOR_OBSERVE_ONLY_START_REUSE",
  "patch_applied": false,
  "started_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "compile_rc": "0",
  "next_lane_x_batch": "LANE-X-R31D_OBSERVE_ONLY_START_REUSE_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION",
  "report": "run/audits/LANE-X-R31C_MONDAY_OBSERVE_ONLY_PREMARKET_SAFETY_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_20260607_175928_report.md"
}

## Hard safety before start/reuse
ACTIVE_RUNTIME_PROCESSES_BEFORE:
NONE

STREAM_SAFETY_BEFORE:
orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0

## Helper availability
FOUND_HELPER pfeeds
FOUND_HELPER pstack
FOUND_HELPER pcheck
FOUND_HELPER pfeedcheck
FOUND_HELPER pstackcheck

## Export observe-only safety env
SCALPX_OBSERVE_ONLY=1
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=UNSET
SCALPX_ENABLE_PAPER=UNSET
SCALPX_ENABLE_LIVE=UNSET

## Start/reuse pfeeds
===== PFEEDS COMPREHENSIVE BACKGROUND START =====
project=/home/Lenovo/scalpx/projects/mme_scalpx
log=run/live_capture/pfeeds_live_raw_capture_20260607_182433.log
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
instrument_age_sec=289868
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
status=FAILED
pid=26121
remark=pfeeds exited during startup.
log=run/live_capture/pfeeds_live_raw_capture_20260607_182433.log
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":26121,"thread":"MainThread","ts":"2026-06-07T12:54:34.964023+00:00"}
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 188, in fetch_underlying_ltp
    payload = kite.ltp([instrument_key])
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 622, in ltp
    return self._get("market.quote.ltp", params={"i": ins})
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 872, in _get
    return self._request(route, "GET", url_args=url_args, params=params, is_json=is_json)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 948, in _request
    raise exp(data["message"], code=r.status_code)
kiteconnect.exceptions.TokenException: Incorrect `api_key` or `access_token`.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/lib/python3.10/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 2053, in <module>
    raise SystemExit(main())
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 1948, in main
    maybe_register_bootstrap_dependencies(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 861, in maybe_register_bootstrap_dependencies
    result = provider()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 225, in provide
    return build_bootstrap_payload()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 206, in build_bootstrap_payload
    built = build_runtime_instruments()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/runtime_instruments_factory.py", line 265, in build_runtime_instruments
    quote = fetch_underlying_ltp(quote_key)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 192, in fetch_underlying_ltp
    raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc
app.mme_scalpx.integrations.bootstrap_quote.QuoteFetchError: kite.ltp('NSE:NIFTY 50') failed: Incorrect `api_key` or `access_token`.

## Start/reuse pstack
===== PSTACK OBSERVE-ONLY START / FAIL-CLOSED FEED GATE =====
services=feeds,features,strategy
execution=NOT_STARTED
risk=NOT_STARTED
stack_mode=observe_only_no_execution
settings_runtime_mode=live
2026-06-07T18:24:47+05:30

===== 0. PRECHECK: NO RISK / EXECUTION PROCESS =====

===== 1. START / VERIFY FEEDS =====
===== PFEEDS COMPREHENSIVE BACKGROUND START =====
project=/home/Lenovo/scalpx/projects/mme_scalpx
log=run/live_capture/pfeeds_live_raw_capture_20260607_182447.log
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
instrument_age_sec=289882
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
status=FAILED
pid=26160
remark=pfeeds exited during startup.
log=run/live_capture/pfeeds_live_raw_capture_20260607_182447.log
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":26160,"thread":"MainThread","ts":"2026-06-07T12:54:48.891209+00:00"}
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 188, in fetch_underlying_ltp
    payload = kite.ltp([instrument_key])
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 622, in ltp
    return self._get("market.quote.ltp", params={"i": ins})
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 872, in _get
    return self._request(route, "GET", url_args=url_args, params=params, is_json=is_json)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 948, in _request
    raise exp(data["message"], code=r.status_code)
kiteconnect.exceptions.TokenException: Incorrect `api_key` or `access_token`.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/lib/python3.10/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 2053, in <module>
    raise SystemExit(main())
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 1948, in main
    maybe_register_bootstrap_dependencies(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 861, in maybe_register_bootstrap_dependencies
    result = provider()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 225, in provide
    return build_bootstrap_payload()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 206, in build_bootstrap_payload
    built = build_runtime_instruments()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/runtime_instruments_factory.py", line 265, in build_runtime_instruments
    quote = fetch_underlying_ltp(quote_key)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 192, in fetch_underlying_ltp
    raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc
app.mme_scalpx.integrations.bootstrap_quote.QuoteFetchError: kite.ltp('NSE:NIFTY 50') failed: Incorrect `api_key` or `access_token`.

===== 2. STRICT FEED GATE =====
===== PFEEDCHECK STRICT =====
2026-06-07T18:24:58+05:30

===== PROCESS STATUS =====
process_alive=False
pidfile_pid=26160

===== LATEST LOG =====
-rw-rw-r-- 1 Lenovo Lenovo 2.6K Jun  7 18:24 run/live_capture/pfeeds_live_raw_capture_20260607_182447.log
last_log_lines:
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":26160,"thread":"MainThread","ts":"2026-06-07T12:54:48.891209+00:00"}
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 188, in fetch_underlying_ltp
    payload = kite.ltp([instrument_key])
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 622, in ltp
    return self._get("market.quote.ltp", params={"i": ins})
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 872, in _get
    return self._request(route, "GET", url_args=url_args, params=params, is_json=is_json)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 948, in _request
    raise exp(data["message"], code=r.status_code)
kiteconnect.exceptions.TokenException: Incorrect `api_key` or `access_token`.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/lib/python3.10/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 2053, in <module>
    raise SystemExit(main())
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 1948, in main
    maybe_register_bootstrap_dependencies(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 861, in maybe_register_bootstrap_dependencies
    result = provider()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 225, in provide
    return build_bootstrap_payload()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 206, in build_bootstrap_payload
    built = build_runtime_instruments()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/runtime_instruments_factory.py", line 265, in build_runtime_instruments
    quote = fetch_underlying_ltp(quote_key)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 192, in fetch_underlying_ltp
    raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc
app.mme_scalpx.integrations.bootstrap_quote.QuoteFetchError: kite.ltp('NSE:NIFTY 50') failed: Incorrect `api_key` or `access_token`.

===== REDIS STREAM RECORDING CHECK =====
redis_ping = True
lock_feeds_owner = None
lock_feeds_ttl_ms = -2

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=0        growth_5s=0
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=0        growth_5s=0
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=4332     growth_5s=0
errors                   system:errors:stream                       xlen=10006    growth_5s=0

status=NOT_HEALTHY_PROCESS_DEAD
remark=pfeeds process is not alive.
pfeedcheck_rc=0

status=REFUSED
reason=pfeedcheck_not_healthy_recording
feed_gate_file=run/proofs/pstack_feed_gate_20260607_182458.txt
PSTACK_FAIL_CLOSED: features/strategy were NOT started.

## Post-start helper checks
===== PFEEDCHECK STRICT =====
2026-06-07T18:25:09+05:30

===== PROCESS STATUS =====
process_alive=False
pidfile_pid=26160

===== LATEST LOG =====
-rw-rw-r-- 1 Lenovo Lenovo 2.6K Jun  7 18:24 run/live_capture/pfeeds_live_raw_capture_20260607_182447.log
last_log_lines:
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":26160,"thread":"MainThread","ts":"2026-06-07T12:54:48.891209+00:00"}
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 188, in fetch_underlying_ltp
    payload = kite.ltp([instrument_key])
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 622, in ltp
    return self._get("market.quote.ltp", params={"i": ins})
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 872, in _get
    return self._request(route, "GET", url_args=url_args, params=params, is_json=is_json)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/lib/python3.10/site-packages/kiteconnect/connect.py", line 948, in _request
    raise exp(data["message"], code=r.status_code)
kiteconnect.exceptions.TokenException: Incorrect `api_key` or `access_token`.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/lib/python3.10/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 2053, in <module>
    raise SystemExit(main())
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 1948, in main
    maybe_register_bootstrap_dependencies(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py", line 861, in maybe_register_bootstrap_dependencies
    result = provider()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 225, in provide
    return build_bootstrap_payload()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_provider.py", line 206, in build_bootstrap_payload
    built = build_runtime_instruments()
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/runtime_instruments_factory.py", line 265, in build_runtime_instruments
    quote = fetch_underlying_ltp(quote_key)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/integrations/bootstrap_quote.py", line 192, in fetch_underlying_ltp
    raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc
app.mme_scalpx.integrations.bootstrap_quote.QuoteFetchError: kite.ltp('NSE:NIFTY 50') failed: Incorrect `api_key` or `access_token`.

===== REDIS STREAM RECORDING CHECK =====
redis_ping = True
lock_feeds_owner = None
lock_feeds_ttl_ms = -2

fut_zerodha              ticks:mme:fut:zerodha:stream               xlen=0        growth_5s=0
fut_dhan                 ticks:mme:fut:dhan:stream                  xlen=0        growth_5s=0
opt_selected_zerodha     ticks:mme:opt:selected:zerodha:stream      xlen=0        growth_5s=0
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=4332     growth_5s=0
errors                   system:errors:stream                       xlen=10006    growth_5s=0

status=NOT_HEALTHY_PROCESS_DEAD
remark=pfeeds process is not alive.

===== PSTACKCHECK =====
2026-06-07T18:25:14+05:30

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

STREAM_TICKS_MME_FUT_ZERODHA           ticks:mme:fut:zerodha:stream                  xlen=0        growth_5s=0
STREAM_TICKS_MME_FUT_DHAN              ticks:mme:fut:dhan:stream                     xlen=0        growth_5s=0
STREAM_TICKS_MME_OPT_SELECTED_ZERODHA  ticks:mme:opt:selected:zerodha:stream         xlen=0        growth_5s=0
STREAM_TICKS_MME_OPT_SELECTED_DHAN     ticks:mme:opt:selected:dhan:stream            xlen=0        growth_5s=0
STREAM_TICKS_MME_OPT_CONTEXT_DHAN      ticks:mme:opt:context:dhan:stream             xlen=0        growth_5s=0
STREAM_FEATURES_MME                    features:mme:stream                           xlen=4220     growth_5s=0
STREAM_DECISIONS_MME                   decisions:mme:stream                          xlen=1682     growth_5s=0
STREAM_SYSTEM_HEALTH                   system:health:stream                          xlen=4332     growth_5s=0
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
KEY_LOCK_FEEDS           lock:feeds                     value=None ttl_ms=-2
KEY_LOCK_STRATEGY        lock:strategy                  value=None ttl_ms=-2
KEY_LOCK_EXECUTION       lock:execution                 value=None ttl_ms=-2

[2J[HScalpX MME live observer | now=2026-06-07 18:25:20 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=- ttl=missing
lock:strategy: owner=- ttl=missing
lock:execution: owner=- ttl=missing

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: MISSING (ttl=missing)
health:features: MISSING (ttl=missing)
health:strategy: MISSING (ttl=missing)
health:risk: MISSING (ttl=missing)
health:execution: MISSING (ttl=missing)
health:monitor: MISSING (ttl=missing)
health:provider:runtime: MISSING (ttl=missing)
health:zerodha:marketdata: MISSING (ttl=missing)
health:zerodha:execution: MISSING (ttl=missing)
health:dhan:marketdata: MISSING (ttl=missing)
health:dhan:execution: MISSING (ttl=missing)
health:dhan:auth: MISSING (ttl=missing)

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
MISSING

[state:snapshot:mme:opt:selected]
MISSING

[state:snapshot:mme:fut:active]
MISSING

[state:snapshot:mme:opt:selected:active]
MISSING

[state:snapshot:mme:fut:zerodha]
MISSING

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
MISSING

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
MISSING

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-05-04 15:20:01 age=2948719.11s
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
updated_at=2026-05-04 15:20:01 age=2948719.14s
family_features_version=1.1
frame_ts_ns=1777888201323397710
regime=NORMAL

[state:option:confirm]
updated_at=2026-05-04 15:20:01 age=2948719.14s
frame_ts_ns=1777888201323397710

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
no entries

[ticks:mme:opt:stream]
no entries

[features:mme:stream]
id=1777888201390-0 | ts=2026-05-04 15:20:01 | age=2948719.14s | frame_id=features-1777888201323397710
id=1777888201221-0 | ts=2026-05-04 15:20:01 | age=2948719.31s | frame_id=features-1777888201156516724

[system:health:stream]
id=1777888475604-0 | ts=2026-05-04 15:24:23 | age=2948457.10s | instance_id=strategy:mme-scalpx:14091 | status=ERROR | detail=loop_error:StrategyBridgeError
id=1777888201393-0 | ts=2026-05-04 15:20:01 | age=2948719.07s | instance_id=features:mme-scalpx:14086 | status=OK | detail=features_ok

[system:errors:stream]
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=2948444.81s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888475608-0 | ts=2026-05-04 15:24:33 | age=2948447.46s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=LockError:Failed to refresh lock 'lock:feeds': Timeout re... | selection_version=mme-instruments-v1

[ticks:mme:fut:zerodha:stream]
no entries

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
no entries

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
no entries

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=2948444.81s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888475608-0 | ts=2026-05-04 15:24:33 | age=2948447.46s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=LockError:Failed to refresh lock 'lock:feeds': Timeout re... | selection_version=mme-instruments-v1
id=1777888201411-0 | ts=2026-05-04 15:20:01 | age=2948719.06s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201359-0 | ts=2026-05-04 15:20:01 | age=2948719.11s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201307-0 | ts=2026-05-04 15:20:01 | age=2948719.16s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201255-0 | ts=2026-05-04 15:20:01 | age=2948719.22s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201203-0 | ts=2026-05-04 15:20:01 | age=2948719.27s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201151-0 | ts=2026-05-04 15:20:01 | age=2948719.32s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201099-0 | ts=2026-05-04 15:20:01 | age=2948719.37s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201047-0 | ts=2026-05-04 15:20:01 | age=2948719.42s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

## Hard safety after start/reuse
ACTIVE_RUNTIME_PROCESSES_AFTER:
NONE

STREAM_SAFETY_AFTER:
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=PASS_R31D_OBSERVE_ONLY_START_REUSE_DONE_SAFETY_ZERO_READY_FOR_CANDIDATE_WATCH_WINDOW
