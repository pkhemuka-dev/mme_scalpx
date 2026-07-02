# LANE-X-R31L_LIVE_SESSION_COMPACT_VALIDITY_PROVIDER_READY_MONITOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260608_114324
2026-06-08T11:43:24+05:30

LAW=LIVE_SESSION_ONLY_COMPACT_MONITOR_NO_PATCH_NO_SOURCE_AUDIT_NO_REPLAY_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_PAPER_NO_RISK_NO_EXECUTION

## Safety
59317 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Compact pcheck
[2J[HScalpX MME live observer | now=2026-06-08 11:43:25 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=feeds:mme-scalpx:59317 ttl=26435ms
lock:strategy: owner=- ttl=missing
lock:execution: owner=execution:mme-scalpx:59317 ttl=20795ms

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: status=OK service=feeds instance=feeds:mme-scalpx:59317 age=1.02s ttl=5007ms message=-
health:features: status=OK service=features instance=features:mme-scalpx:59317 age=1.59s ttl=13413ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:59317 age=2.14s ttl=12881ms message=-
health:risk: status=WARN service=risk instance=risk:mme-scalpx:59317 age=3.10s ttl=7636ms message=CONTROLLED_PAPER_NOT_ARMED
health:execution: status=OK service=execution instance=execution:mme-scalpx:59317 age=0.22s ttl=9801ms message=-
health:monitor: status=WARN service=monitor instance=monitor:mme-scalpx:59317 age=0.40s ttl=9606ms message=report:missing_heartbeat,runtime_mode=live
health:provider:runtime: status=WARN service=feeds instance=feeds:mme-scalpx:59317 age=1.02s ttl=5150ms message=-
health:zerodha:marketdata: status=OK service=feeds instance=feeds:mme-scalpx:59317 age=1.02s ttl=5008ms message=-
health:zerodha:execution: status=OK service=feeds instance=feeds:mme-scalpx:59317 age=1.02s ttl=5017ms message=-
health:dhan:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:59317 age=1.02s ttl=5021ms message=-
health:dhan:execution: status=OK service=feeds instance=feeds:mme-scalpx:59317 age=1.02s ttl=5068ms message=-
health:dhan:auth: status=OK service=feeds instance=feeds:mme-scalpx:59317 age=1.02s ttl=5024ms message=-

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
updated_at=2026-06-08 17:13:21 age=0.00s
frame_id=frame-1780899204945141847
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
future_json: symbol=NIFTY26JUNFUT ltp=23264.0 bid=23264.1 ask=23265.0 bid_qty_5=6110 ask_qty_5=845 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23265.0
ask_qty_5=845
bid=23264.1
bid_qty_5=6110
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780899204945141847
ltp=23264.0
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780919001000000000
ts_frame_ns=1780899204945141847

[state:snapshot:mme:opt:selected]
updated_at=2026-06-08 11:43:24 age=0.22s
frame_id=frame-1780899204945141847
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
ce_atm_json: symbol=NIFTY2660923200CE ltp=126.0 bid=125.75 ask=126.0 bid_qty_5=8125 ask_qty_5=3380 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=100.35 bid=100.4 ask=100.65 bid_qty_5=5525 ask_qty_5=7410 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=109.8 bid=109.5 ask=109.8 bid_qty_5=9750 ask_qty_5=9945 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=88.55 bid=87.85 ask=88.0 bid_qty_5=13260 ask_qty_5=6435 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780899204945141847

[state:snapshot:mme:fut:active]
updated_at=2026-06-08 17:13:21 age=0.00s
frame_id=frame-1780899204945141847
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
future_json: symbol=NIFTY26JUNFUT ltp=23264.0 bid=23264.1 ask=23265.0 bid_qty_5=6110 ask_qty_5=845 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23265.0
ask_qty_5=845
bid=23264.1
bid_qty_5=6110
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780899204945141847
ltp=23264.0
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780919001000000000
ts_frame_ns=1780899204945141847

[state:snapshot:mme:opt:selected:active]
updated_at=2026-06-08 11:43:24 age=0.22s
frame_id=frame-1780899204945141847
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
ce_atm_json: symbol=NIFTY2660923200CE ltp=126.0 bid=125.75 ask=126.0 bid_qty_5=8125 ask_qty_5=3380 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=100.35 bid=100.4 ask=100.65 bid_qty_5=5525 ask_qty_5=7410 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=109.8 bid=109.5 ask=109.8 bid_qty_5=9750 ask_qty_5=9945 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=88.55 bid=87.85 ask=88.0 bid_qty_5=13260 ask_qty_5=6435 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780899204945141847

[state:snapshot:mme:fut:zerodha]
updated_at=2026-06-08 17:13:21 age=0.00s
frame_id=frame-1780899202730732616
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=3000
sync_ok=0
ts_span_ms=3000
future_json: symbol=NIFTY26JUNFUT ltp=23264.0 bid=23264.1 ask=23265.0 bid_qty_5=6110 ask_qty_5=845 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23265.0
ask_qty_5=845
bid=23264.1
bid_qty_5=6110
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780899202730732616
ltp=23264.0
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780919001000000000
ts_frame_ns=1780899202730732616

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
updated_at=2026-06-08 11:43:24 age=0.19s
frame_id=frame-1780899204977642756
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=2000
sync_ok=0
ts_span_ms=2000
ce_atm_json: symbol=NIFTY2660923200CE ltp=126.0 bid=125.75 ask=126.0 bid_qty_5=8125 ask_qty_5=3380 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=100.35 bid=100.4 ask=100.65 bid_qty_5=5525 ask_qty_5=7410 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=109.8 bid=109.5 ask=109.8 bid_qty_5=9750 ask_qty_5=9945 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=88.55 bid=87.85 ask=88.0 bid_qty_5=13260 ask_qty_5=6435 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780899204977642756

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
updated_at=2026-06-08 11:43:24 age=0.23s
futures_marketdata_provider_id=ZERODHA
selected_option_marketdata_provider_id=ZERODHA
option_context_provider_id=DHAN
execution_primary_provider_id=ZERODHA
execution_fallback_provider_id=DHAN
family_runtime_mode=OBSERVE_ONLY
failover_mode=MANUAL
override_mode=AUTO
transition_reason=BOOTSTRAP
provider_transition_seq=1549
execution_fallback_status=DISABLED
execution_primary_status=HEALTHY
failover_active=True
futures_marketdata_status=HEALTHY
last_update_ns=1780899204945141847
message=Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled
option_context_status=UNAVAILABLE
pending_failover=False
selected_option_marketdata_status=FAILOVER_ACTIVE
ts_event_ns=1780899204945141847

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-06-08 11:43:23 age=1.50s
frame_id=features-1780899203697951798
feature_state_json: {"frame_id":"features-1780899203697951798","frame_ts_ns":1780899203697951798,"frame_valid":true,"warmup_complete":true,"regime":"LOWVOL","selected_option":{"side":"CALL","ltp":110.35,"spread":0.20000000000000284,"spread_ratio":0.0018148820326679023,"depth_total":975,"depth_ok":true,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":-0.5999999999999943,"response_efficiency":2.3999999999999773,"tradability_ok":true,"instrument_key":"NFO:NIFTY2660923200PE","instrument_token":"1...
family_frames_json: {"mist_call":{"frame_id":"mist_call-1780899203697951798","frame_ts_ns":1780899203697951798,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"10824706","instrument_token":"10824706","option_symbol":"NIFTY2660923200CE","strike":23200.0,"option_price":125.65,"tick_size":0.05,"target_points...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1780899203697951798,"frame_id":"features-1780899203697951798","frame_ts_ns":1780899203697951798,"ts_event_ns":1780899203697951798,"frame_valid":true,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1780899203697951744,"snapshot":{"valid":true,"validity":"OK","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1780899203697951798
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1780899203697951798
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-08 11:43:23 age=1.59s
family_features_version=1.1
frame_ts_ns=1780899203697951798
regime=LOWVOL

[state:option:confirm]
updated_at=2026-06-08 11:43:23 age=1.59s
frame_ts_ns=1780899203697951798

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1780899202729-0 | ts=2026-06-08 17:13:21 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23264.0 | bid=23264.1 | ask=23265.0
id=1780899199885-0 | ts=2026-06-08 17:13:18 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23264.1 | bid=23264.1 | ask=23265.0

[ticks:mme:opt:stream]
id=1780899204974-0 | ts=2026-06-08 17:13:23 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200CE | instrument_token=10824706 | trading_symbol=NIFTY2660923200CE | instrument_role=CE_ATM | ltp=126.0 | bid=125.75 | ask=126.0
id=1780899204495-0 | ts=2026-06-08 17:13:23 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200PE | instrument_token=10824962 | trading_symbol=NIFTY2660923200PE | instrument_role=PE_ATM | ltp=109.8 | bid=109.5 | ask=109.8

[features:mme:stream]
id=1780899204203-0 | ts=2026-06-08 11:43:23 | age=1.60s | frame_id=features-1780899203697951798
id=1780899199088-0 | ts=2026-06-08 11:43:18 | age=6.75s | frame_id=features-1780899198545376002

[system:health:stream]
id=1780899205248-0 | ts=2026-06-08 11:43:25 | age=0.06s | instance_id=strategy:mme-scalpx:59317 | status=OK | detail=strategy_hold_bridge_ok
id=1780899205038-0 | ts=2026-06-08 11:43:25 | age=0.26s | service_name=feeds | instance_id=feeds:mme-scalpx:59317 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1780898715443-0 | ts=2026-06-08 11:35:15 | age=489.86s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError
id=1780898715073-0 | ts=2026-06-08 11:35:15 | age=490.23s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError

[ticks:mme:fut:zerodha:stream]
id=1780899202728-0 | ts=2026-06-08 17:13:21 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23264.0 | bid=23264.1 | ask=23265.0
id=1780899199849-0 | ts=2026-06-08 17:13:18 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23264.1 | bid=23264.1 | ask=23265.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1780899204964-0 | ts=2026-06-08 17:13:23 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200CE | instrument_token=10824706 | trading_symbol=NIFTY2660923200CE | instrument_role=CE_ATM | ltp=126.0 | bid=125.75 | ask=126.0
id=1780899204451-0 | ts=2026-06-08 17:13:23 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200PE | instrument_token=10824962 | trading_symbol=NIFTY2660923200PE | instrument_role=PE_ATM | ltp=109.8 | bid=109.5 | ask=109.8

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1780899205036-0 | ts=2026-06-08 11:43:24 | age=0.36s | family_runtime_mode=OBSERVE_ONLY
id=1780899204547-0 | ts=2026-06-08 11:43:24 | age=0.85s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1780898715443-0 | ts=2026-06-08 11:35:15 | age=489.86s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError
id=1780898715073-0 | ts=2026-06-08 11:35:15 | age=490.23s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError
id=1780898714540-0 | ts=2026-06-08 11:35:14 | age=490.77s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError
id=1780898714105-0 | ts=2026-06-08 11:35:14 | age=491.20s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError
id=1780898713696-0 | ts=2026-06-08 11:35:13 | age=491.61s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError
id=1780898713223-0 | ts=2026-06-08 11:35:13 | age=492.08s | instance_id=strategy:mme-scalpx:59317 | error_type=FeatureFamilyContractError
id=1780898712647-0 | ts=2026-06-08 11:35:12 | age=492.66s | instance_id=strategy:mme-scalpx:59317 | error_type=StrategyBridgeError
id=1780898712167-0 | ts=2026-06-08 11:35:12 | age=493.14s | instance_id=strategy:mme-scalpx:59317 | error_type=StrategyBridgeError

## Latest 200 decision validity/provider/candidate summary
{
  "actions": {
    "HOLD": 200
  },
  "data_valid_true": 167,
  "decision_rows_sampled": 200,
  "hold_only_false": 0,
  "latest": {
    "action": "HOLD",
    "activation_candidate_count": "0",
    "activation_selected_family_id": "",
    "activation_selected_score": "",
    "data_valid": "0",
    "hold_only": "1",
    "provider_ready_classic": "0",
    "reason": "hold_only_family_features_consumer_bridge",
    "safe_to_consume": "1"
  },
  "max_activation_candidate_count": 0,
  "max_activation_selected_score": 0.0,
  "provider_ready_classic_true": 167,
  "safe_to_consume_true": 200,
  "top_reasons": {
    "hold_only_family_features_consumer_bridge": 200
  }
}
AUDIT_RC=0

## Stream sizes
fut_zerodha_xlen=125
opt_selected_xlen=945
features_xlen=104
decisions_xlen=513

orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0
CLASSIFICATION=PASS_R31L_LIVE_SESSION_VALIDITY_PROVIDER_READY_MONITOR_SAFE_CONTINUE_OBSERVE_ONLY
