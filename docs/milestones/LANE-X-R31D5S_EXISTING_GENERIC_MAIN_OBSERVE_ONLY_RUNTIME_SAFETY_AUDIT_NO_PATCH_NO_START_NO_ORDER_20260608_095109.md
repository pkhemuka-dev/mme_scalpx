# LANE-X-R31D5S_EXISTING_GENERIC_MAIN_OBSERVE_ONLY_RUNTIME_SAFETY_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_095109
2026-06-08T09:51:09+05:30

LAW=EXISTING_RUNTIME_AUDIT_ONLY_NO_PATCH_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER

## Prior R31D5R proof
R31D5R=run/proofs/LANE-X-R31D5R_MARKET_LIVE_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_094825.json
{
  "tag": "LANE-X-R31D5R_MARKET_LIVE_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_094825",
  "classification": "REVIEW_R31D5R_PSTACK_FAIL_CLOSED_DO_NOT_RUN_CANDIDATE_WATCH",
  "patch_applied": false,
  "started_or_reused_observe_only": true,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "next_lane_x_batch_if_pass": "LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION",
  "report": "run/audits/LANE-X-R31D5R_MARKET_LIVE_RETRY_OBSERVE_ONLY_START_AFTER_AUTH_REFRESH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_094825_report.md"
}

## Process and lock audit
35846 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main

lock_feeds=feeds:mme-scalpx:35846
lock_strategy=
lock_risk=
lock_execution=execution:mme-scalpx:35846
lock_execution_ttl=24

## Hard stream safety
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Growth and health via pcheck
[2J[HScalpX MME live observer | now=2026-06-08 09:51:10 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=feeds:mme-scalpx:35846 ttl=25073ms
lock:strategy: owner=- ttl=missing
lock:execution: owner=execution:mme-scalpx:35846 ttl=23573ms

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=3.27s ttl=2836ms message=-
health:features: status=OK service=features instance=features:mme-scalpx:35846 age=1.83s ttl=13180ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:35846 age=2.67s ttl=12333ms message=-
health:risk: status=WARN service=risk instance=risk:mme-scalpx:35846 age=3.18s ttl=7353ms message=CONTROLLED_PAPER_NOT_ARMED
health:execution: status=OK service=execution instance=execution:mme-scalpx:35846 age=3.52s ttl=6478ms message=-
health:monitor: status=WARN service=monitor instance=monitor:mme-scalpx:35846 age=1.97s ttl=8030ms message=report:missing_heartbeat,runtime_mode=live
health:provider:runtime: status=WARN service=feeds instance=feeds:mme-scalpx:35846 age=3.27s ttl=3296ms message=-
health:zerodha:marketdata: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=3.27s ttl=2929ms message=-
health:zerodha:execution: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=3.27s ttl=2973ms message=-
health:dhan:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:35846 age=3.27s ttl=3020ms message=-
health:dhan:execution: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=3.27s ttl=3200ms message=-
health:dhan:auth: status=OK service=feeds instance=feeds:mme-scalpx:35846 age=3.27s ttl=3157ms message=-

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
updated_at=2026-06-08 15:21:08 age=0.00s
frame_id=frame-1780892469571440564
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=3000
future_json: symbol=NIFTY26JUNFUT ltp=23210.2 bid=23205.2 ask=23211.2 bid_qty_5=2600 ask_qty_5=1560 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23211.2
ask_qty_5=1560
bid=23205.2
bid_qty_5=2600
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780892469571440564
ltp=23210.2
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780912268000000000
ts_frame_ns=1780892469571440564

[state:snapshot:mme:opt:selected]
updated_at=2026-06-08 09:51:09 age=0.78s
frame_id=frame-1780892469571440564
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=3000
ce_atm_json: symbol=NIFTY2660923150CE ltp=127.65 bid=127.8 ask=128.15 bid_qty_5=3575 ask_qty_5=4550 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=103.55 bid=103.55 ask=103.8 bid_qty_5=5330 ask_qty_5=5200 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=117.15 bid=116.75 ask=117.05 bid_qty_5=6175 ask_qty_5=7020 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=97.2 bid=96.6 ask=96.9 bid_qty_5=8905 ask_qty_5=8905 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780892469571440564

[state:snapshot:mme:fut:active]
updated_at=2026-06-08 15:21:08 age=0.00s
frame_id=frame-1780892469571440564
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=3000
future_json: symbol=NIFTY26JUNFUT ltp=23210.2 bid=23205.2 ask=23211.2 bid_qty_5=2600 ask_qty_5=1560 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23211.2
ask_qty_5=1560
bid=23205.2
bid_qty_5=2600
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780892469571440564
ltp=23210.2
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780912268000000000
ts_frame_ns=1780892469571440564

[state:snapshot:mme:opt:selected:active]
updated_at=2026-06-08 09:51:09 age=0.78s
frame_id=frame-1780892469571440564
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=3000
ce_atm_json: symbol=NIFTY2660923150CE ltp=127.65 bid=127.8 ask=128.15 bid_qty_5=3575 ask_qty_5=4550 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=103.55 bid=103.55 ask=103.8 bid_qty_5=5330 ask_qty_5=5200 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=117.15 bid=116.75 ask=117.05 bid_qty_5=6175 ask_qty_5=7020 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=97.2 bid=96.6 ask=96.9 bid_qty_5=8905 ask_qty_5=8905 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780892469571440564

[state:snapshot:mme:fut:zerodha]
updated_at=2026-06-08 15:21:08 age=0.00s
frame_id=frame-1780892469106070607
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=3000
sync_ok=0
ts_span_ms=3000
future_json: symbol=NIFTY26JUNFUT ltp=23210.2 bid=23205.2 ask=23211.2 bid_qty_5=2600 ask_qty_5=1560 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23211.2
ask_qty_5=1560
bid=23205.2
bid_qty_5=2600
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780892469106070607
ltp=23210.2
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780912268000000000
ts_frame_ns=1780892469106070607

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
updated_at=2026-06-08 09:51:10 age=0.18s
frame_id=frame-1780892470174417758
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=INVALID_MEMBER
validity_reason=invalid_members:PE_ATM
sync_ok=0
ts_span_ms=3000
ce_atm_json: symbol=NIFTY2660923150CE ltp=127.65 bid=127.8 ask=128.15 bid_qty_5=3575 ask_qty_5=4550 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=103.55 bid=103.55 ask=103.8 bid_qty_5=5330 ask_qty_5=5200 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=117.15 bid=116.75 ask=117.05 bid_qty_5=6175 ask_qty_5=7020 age_ms=0 validity=ANOMALY_CLAMPED strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=97.2 bid=96.6 ask=96.9 bid_qty_5=8905 ask_qty_5=8905 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780892470174417758

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
updated_at=2026-06-08 09:51:10 age=0.30s
futures_marketdata_provider_id=ZERODHA
selected_option_marketdata_provider_id=ZERODHA
option_context_provider_id=DHAN
execution_primary_provider_id=ZERODHA
execution_fallback_provider_id=DHAN
family_runtime_mode=OBSERVE_ONLY
failover_mode=MANUAL
override_mode=AUTO
transition_reason=BOOTSTRAP
provider_transition_seq=1744
execution_fallback_status=DISABLED
execution_primary_status=HEALTHY
failover_active=True
futures_marketdata_status=HEALTHY
last_update_ns=1780892470054159367
message=Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled
option_context_status=UNAVAILABLE
pending_failover=False
selected_option_marketdata_status=FAILOVER_ACTIVE
ts_event_ns=1780892470054159367

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-06-08 09:51:08 age=1.74s
frame_id=features-1780892468637229028
feature_state_json: {"frame_id":"features-1780892468637229028","frame_ts_ns":1780892468637229028,"frame_valid":true,"warmup_complete":true,"regime":"FAST","selected_option":{"side":"CALL","ltp":103.55,"spread":0.25,"spread_ratio":0.0024142926122646064,"depth_total":650,"depth_ok":true,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":3.700000000000003,"response_efficiency":10.571428571428322,"tradability_ok":true,"instrument_key":"NFO:NIFTY2660923200CE","instrument_token":"10824706","option_to...
family_frames_json: {"mist_call":{"frame_id":"mist_call-1780892468637229028","frame_ts_ns":1780892468637229028,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"10823170","instrument_token":"10823170","option_symbol":"NIFTY2660923150CE","strike":23150.0,"option_price":127.75,"tick_size":0.05,"target_points...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1780892468637229028,"frame_id":"features-1780892468637229028","frame_ts_ns":1780892468637229028,"ts_event_ns":1780892468637229028,"frame_valid":true,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1780892468637229056,"snapshot":{"valid":true,"validity":"OK","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1780892468637229028
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1780892468637229028
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-08 09:51:08 age=1.84s
family_features_version=1.1
frame_ts_ns=1780892468637229028
regime=FAST

[state:option:confirm]
updated_at=2026-06-08 09:51:08 age=1.84s
frame_ts_ns=1780892468637229028

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1780892469105-0 | ts=2026-06-08 15:21:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23210.2 | bid=23205.2 | ask=23211.2
id=1780892462733-0 | ts=2026-06-08 15:21:02 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23204.2 | bid=23200.0 | ask=23206.0

[ticks:mme:opt:stream]
id=1780892470086-0 | ts=2026-06-08 15:21:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150PE | instrument_token=10823426 | trading_symbol=NIFTY2660923150PE | instrument_role=PE_ATM | ltp=120.15 | bid=118.4 | ask=118.65
id=1780892469606-0 | ts=2026-06-08 15:21:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150CE | instrument_token=10823170 | trading_symbol=NIFTY2660923150CE | instrument_role=CE_ATM | ltp=127.65 | bid=127.8 | ask=128.15

[features:mme:stream]
id=1780892469102-0 | ts=2026-06-08 09:51:08 | age=1.85s | frame_id=features-1780892468637229028
id=1780892464428-0 | ts=2026-06-08 09:51:03 | age=6.53s | frame_id=features-1780892463954593322

[system:health:stream]
id=1780892470400-0 | ts=2026-06-08 09:51:10 | age=0.09s | service_name=feeds | instance_id=feeds:mme-scalpx:35846 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1
id=1780892469755-0 | ts=2026-06-08 09:51:09 | age=0.73s | service_name=feeds | instance_id=feeds:mme-scalpx:35846 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1780891924891-0 | ts=2026-06-08 09:42:04 | age=545.60s | instance_id=strategy:mme-scalpx:35846 | error_type=FeatureFamilyContractError
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=3003994.83s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

[ticks:mme:fut:zerodha:stream]
id=1780892469104-0 | ts=2026-06-08 15:21:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23210.2 | bid=23205.2 | ask=23211.2
id=1780892462714-0 | ts=2026-06-08 15:21:02 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23204.2 | bid=23200.0 | ask=23206.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1780892470056-0 | ts=2026-06-08 15:21:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150PE | instrument_token=10823426 | trading_symbol=NIFTY2660923150PE | instrument_role=PE_ATM | ltp=120.15 | bid=118.4 | ask=118.65
id=1780892469579-0 | ts=2026-06-08 15:21:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150CE | instrument_token=10823170 | trading_symbol=NIFTY2660923150CE | instrument_role=CE_ATM | ltp=127.65 | bid=127.8 | ask=128.15

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1780892470299-0 | ts=2026-06-08 09:51:10 | age=0.44s | family_runtime_mode=OBSERVE_ONLY
id=1780892469733-0 | ts=2026-06-08 09:51:09 | age=0.92s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1780891924891-0 | ts=2026-06-08 09:42:04 | age=545.60s | instance_id=strategy:mme-scalpx:35846 | error_type=FeatureFamilyContractError
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=3003994.83s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888475608-0 | ts=2026-05-04 15:24:33 | age=3003997.49s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=LockError:Failed to refresh lock 'lock:feeds': Timeout re... | selection_version=mme-instruments-v1
id=1777888201411-0 | ts=2026-05-04 15:20:01 | age=3004269.08s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201359-0 | ts=2026-05-04 15:20:01 | age=3004269.13s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201307-0 | ts=2026-05-04 15:20:01 | age=3004269.19s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201255-0 | ts=2026-05-04 15:20:01 | age=3004269.24s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201203-0 | ts=2026-05-04 15:20:01 | age=3004269.29s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201151-0 | ts=2026-05-04 15:20:01 | age=3004269.34s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201099-0 | ts=2026-05-04 15:20:01 | age=3004269.39s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

## Direct latest decision/feature consumer audit
{
  "feature_has_consumer_view": false,
  "feature_has_family_features": false,
  "feature_has_family_surfaces": false,
  "latest_decision_action": null,
  "latest_decision_activation_candidate_count": null,
  "latest_decision_activation_selected_family_id": null,
  "latest_decision_activation_selected_score": null,
  "latest_decision_data_valid": null,
  "latest_decision_hold_only": null,
  "latest_decision_provider_ready_classic": null,
  "latest_decision_reason": null,
  "latest_decision_safe_to_consume": null,
  "stream_safety": {
    "execution": "0",
    "orders": "0",
    "risk": "0"
  }
}
AUDIT_RC=0

CLASSIFICATION=PASS_R31D5S_EXISTING_GENERIC_MAIN_OBSERVE_ONLY_SAFE_FOR_R31E_CANDIDATE_WATCH
