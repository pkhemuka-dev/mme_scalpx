# LANE-X-R31G_STRATEGY_BRIDGE_AND_CONTRACT_ERROR_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_104135
2026-06-08T10:41:35+05:30

LAW=READONLY_SEAM_AUDIT_ONLY_NO_PATCH_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31F proof
R31F=run/proofs/LANE-X-R31F_30MIN_DEEP_CANDIDATE_BLOCKER_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_100811.json
{
  "tag": "LANE-X-R31F_30MIN_DEEP_CANDIDATE_BLOCKER_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_100811",
  "classification": "PASS_R31F_NO_CANDIDATE_YET_DEEP_BLOCKER_MAP_READY",
  "patch_applied": false,
  "started_runtime": false,
  "stopped_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "report": "run/audits/LANE-X-R31F_30MIN_DEEP_CANDIDATE_BLOCKER_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_100811_report.md"
}

## Safety before readonly audit
54524 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## pcheck snapshot
[2J[HScalpX MME live observer | now=2026-06-08 10:41:36 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=feeds:mme-scalpx:54524 ttl=23980ms
lock:strategy: owner=- ttl=missing
lock:execution: owner=execution:mme-scalpx:54524 ttl=24915ms

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: status=OK service=feeds instance=feeds:mme-scalpx:54524 age=2.48s ttl=3599ms message=-
health:features: status=OK service=features instance=features:mme-scalpx:54524 age=0.07s ttl=14939ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:54524 age=1.02s ttl=13982ms message=-
health:risk: status=WARN service=risk instance=risk:mme-scalpx:54524 age=2.10s ttl=8746ms message=CONTROLLED_PAPER_NOT_ARMED
health:execution: status=OK service=execution instance=execution:mme-scalpx:54524 age=0.97s ttl=9033ms message=-
health:monitor: status=WARN service=monitor instance=monitor:mme-scalpx:54524 age=0.02s ttl=7667ms message=report:missing_heartbeat,runtime_mode=live
health:provider:runtime: status=WARN service=feeds instance=feeds:mme-scalpx:54524 age=2.48s ttl=3773ms message=-
health:zerodha:marketdata: status=OK service=feeds instance=feeds:mme-scalpx:54524 age=2.48s ttl=3600ms message=-
health:zerodha:execution: status=OK service=feeds instance=feeds:mme-scalpx:54524 age=2.48s ttl=3603ms message=-
health:dhan:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:54524 age=2.48s ttl=3612ms message=-
health:dhan:execution: status=OK service=feeds instance=feeds:mme-scalpx:54524 age=2.49s ttl=3702ms message=-
health:dhan:auth: status=OK service=feeds instance=feeds:mme-scalpx:54524 age=2.49s ttl=3659ms message=-

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
updated_at=2026-06-08 16:11:30 age=0.00s
frame_id=frame-1780895495424897858
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=4000
future_json: symbol=NIFTY26JUNFUT ltp=23275.0 bid=23275.0 ask=23276.8 bid_qty_5=780 ask_qty_5=715 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23276.8
ask_qty_5=715
bid=23275.0
bid_qty_5=780
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780895495424897858
ltp=23275.0
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780915290000000000
ts_frame_ns=1780895495424897858

[state:snapshot:mme:opt:selected]
updated_at=2026-06-08 10:41:35 age=0.73s
frame_id=frame-1780895495424897858
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=4000
ce_atm_json: symbol=NIFTY2660923200CE ltp=134.35 bid=134.0 ask=134.35 bid_qty_5=8580 ask_qty_5=7345 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=108.35 bid=108.35 ask=108.6 bid_qty_5=8450 ask_qty_5=3900 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=109.35 bid=109.35 ask=109.65 bid_qty_5=8775 ask_qty_5=11960 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=88.7 bid=88.5 ask=88.8 bid_qty_5=12285 ask_qty_5=19240 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780895495424897858

[state:snapshot:mme:fut:active]
updated_at=2026-06-08 16:11:30 age=0.00s
frame_id=frame-1780895495424897858
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=4000
future_json: symbol=NIFTY26JUNFUT ltp=23275.0 bid=23275.0 ask=23276.8 bid_qty_5=780 ask_qty_5=715 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23276.8
ask_qty_5=715
bid=23275.0
bid_qty_5=780
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780895495424897858
ltp=23275.0
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780915290000000000
ts_frame_ns=1780895495424897858

[state:snapshot:mme:opt:selected:active]
updated_at=2026-06-08 10:41:35 age=0.73s
frame_id=frame-1780895495424897858
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=4000
ce_atm_json: symbol=NIFTY2660923200CE ltp=134.35 bid=134.0 ask=134.35 bid_qty_5=8580 ask_qty_5=7345 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=108.35 bid=108.35 ask=108.6 bid_qty_5=8450 ask_qty_5=3900 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=109.35 bid=109.35 ask=109.65 bid_qty_5=8775 ask_qty_5=11960 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=88.7 bid=88.5 ask=88.8 bid_qty_5=12285 ask_qty_5=19240 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780895495424897858

[state:snapshot:mme:fut:zerodha]
updated_at=2026-06-08 16:11:30 age=0.00s
frame_id=frame-1780895491052659537
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=2000
sync_ok=0
ts_span_ms=2000
future_json: symbol=NIFTY26JUNFUT ltp=23275.0 bid=23275.0 ask=23276.8 bid_qty_5=780 ask_qty_5=715 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23276.8
ask_qty_5=715
bid=23275.0
bid_qty_5=780
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780895491052659537
ltp=23275.0
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780915290000000000
ts_frame_ns=1780895491052659537

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
updated_at=2026-06-08 10:41:35 age=0.72s
frame_id=frame-1780895495438732325
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=4000
sync_ok=0
ts_span_ms=4000
ce_atm_json: symbol=NIFTY2660923200CE ltp=134.35 bid=134.0 ask=134.35 bid_qty_5=8580 ask_qty_5=7345 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=108.35 bid=108.35 ask=108.6 bid_qty_5=8450 ask_qty_5=3900 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=109.35 bid=109.35 ask=109.65 bid_qty_5=8775 ask_qty_5=11960 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=88.7 bid=88.5 ask=88.8 bid_qty_5=12285 ask_qty_5=19240 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780895495438732325

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
updated_at=2026-06-08 10:41:35 age=0.22s
futures_marketdata_provider_id=ZERODHA
selected_option_marketdata_provider_id=ZERODHA
option_context_provider_id=DHAN
execution_primary_provider_id=ZERODHA
execution_fallback_provider_id=DHAN
family_runtime_mode=OBSERVE_ONLY
failover_mode=MANUAL
override_mode=AUTO
transition_reason=BOOTSTRAP
provider_transition_seq=474
execution_fallback_status=DISABLED
execution_primary_status=HEALTHY
failover_active=True
futures_marketdata_status=HEALTHY
last_update_ns=1780895495940456312
message=Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled
option_context_status=UNAVAILABLE
pending_failover=False
selected_option_marketdata_status=FAILOVER_ACTIVE
ts_event_ns=1780895495940456312

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-06-08 10:41:31 age=4.52s
frame_id=features-1780895491656780457
feature_state_json: {"frame_id":"features-1780895491656780457","frame_ts_ns":1780895491656780457,"frame_valid":true,"warmup_complete":true,"regime":"FAST","selected_option":{"side":"CALL","ltp":110.0,"spread":0.20000000000000284,"spread_ratio":0.0018264840182648661,"depth_total":455.0,"depth_ok":true,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":-5.650000000000006,"response_efficiency":16.142857142857423,"tradability_ok":true}}
family_frames_json: {"mist_call":{"frame_id":"mist_call-1780895491656780457","frame_ts_ns":1780895491656780457,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"10824706","instrument_token":"10824706","option_symbol":"NIFTY2660923200CE","strike":23200.0,"option_price":133.65,"tick_size":0.05,"target_points...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1780895491656780457,"frame_id":"features-1780895491656780457","frame_ts_ns":1780895491656780457,"ts_event_ns":1780895491656780457,"frame_valid":true,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1780895491656780544,"snapshot":{"valid":true,"validity":"OK","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1780895491656780457
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1780895491656780457
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-08 10:41:31 age=4.63s
family_features_version=1.1
frame_ts_ns=1780895491656780457
regime=FAST

[state:option:confirm]
updated_at=2026-06-08 10:41:31 age=4.63s
frame_ts_ns=1780895491656780457

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1780895491019-0 | ts=2026-06-08 16:11:30 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23275.0 | bid=23275.0 | ask=23276.8
id=1780895487400-0 | ts=2026-06-08 16:11:26 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23277.0 | bid=23275.0 | ask=23277.9

[ticks:mme:opt:stream]
id=1780895495437-0 | ts=2026-06-08 16:11:34 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923250CE | instrument_token=10825218 | trading_symbol=NIFTY2660923250CE | instrument_role=CE_ATM1 | ltp=108.35 | bid=108.35 | ask=108.6
id=1780895495216-0 | ts=2026-06-08 16:11:34 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200PE | instrument_token=10824962 | trading_symbol=NIFTY2660923200PE | instrument_role=PE_ATM | ltp=109.35 | bid=109.35 | ask=109.65

[features:mme:stream]
id=1780895492220-0 | ts=2026-06-08 10:41:31 | age=4.64s | frame_id=features-1780895491656780457
id=1780895487671-0 | ts=2026-06-08 10:41:26 | age=9.30s | frame_id=features-1780895486997934405

[system:health:stream]
id=1780895496148-0 | ts=2026-06-08 10:41:36 | age=0.22s | instance_id=features:mme-scalpx:54524 | status=OK | detail=features_ok
id=1780895496085-0 | ts=2026-06-08 10:41:36 | age=0.21s | service_name=feeds | instance_id=feeds:mme-scalpx:54524 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1780895307444-0 | ts=2026-06-08 10:38:27 | age=188.85s | instance_id=execution:mme-scalpx:42167
id=1780895307428-0 | ts=2026-06-08 10:38:27 | age=189.22s | instance_id=strategy:mme-scalpx:42167 | error_type=TimeoutError

[ticks:mme:fut:zerodha:stream]
id=1780895490952-0 | ts=2026-06-08 16:11:30 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23275.0 | bid=23275.0 | ask=23276.8
id=1780895487358-0 | ts=2026-06-08 16:11:26 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23277.0 | bid=23275.0 | ask=23277.9

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1780895495426-0 | ts=2026-06-08 16:11:34 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923250CE | instrument_token=10825218 | trading_symbol=NIFTY2660923250CE | instrument_role=CE_ATM1 | ltp=108.35 | bid=108.35 | ask=108.6
id=1780895495214-0 | ts=2026-06-08 16:11:34 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200PE | instrument_token=10824962 | trading_symbol=NIFTY2660923200PE | instrument_role=PE_ATM | ltp=109.35 | bid=109.35 | ask=109.65

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1780895496078-0 | ts=2026-06-08 10:41:35 | age=0.36s | family_runtime_mode=OBSERVE_ONLY
id=1780895495574-0 | ts=2026-06-08 10:41:35 | age=0.87s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1780895307444-0 | ts=2026-06-08 10:38:27 | age=188.88s | instance_id=execution:mme-scalpx:42167
id=1780895307428-0 | ts=2026-06-08 10:38:27 | age=189.25s | instance_id=strategy:mme-scalpx:42167 | error_type=TimeoutError
id=1780895307425-0 | ts=2026-06-08 10:38:24 | age=191.46s | service_name=feeds | instance_id=feeds:mme-scalpx:42167 | error_type=feeds_service_loop_error | detail=StreamTransportError:Failed to XADD to 'ticks:mme:fut:zer... | selection_version=mme-instruments-v1
id=1780895305079-0 | ts=2026-06-08 10:38:24 | age=191.46s | service_name=feeds | instance_id=feeds:mme-scalpx:42167 | error_type=feeds_service_loop_error | detail=StreamTransportError:Failed to XADD to 'ticks:mme:fut:zer... | selection_version=mme-instruments-v1
id=1780894486439-0 | ts=2026-06-08 10:24:45 | age=1010.89s | service_name=monitor | event_type=system_error
id=1780894056216-0 | ts=2026-06-08 10:17:36 | age=1440.11s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894055709-0 | ts=2026-06-08 10:17:35 | age=1440.62s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894055155-0 | ts=2026-06-08 10:17:35 | age=1441.18s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894054515-0 | ts=2026-06-08 10:17:34 | age=1441.81s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894054050-0 | ts=2026-06-08 10:17:34 | age=1442.28s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError

## Strategy bridge / contract error / payload seam audit
{
  "decisions": {
    "actions": {
      "HOLD": 1347
    },
    "activation_report_keys": [
      "action",
      "activation_mode",
      "blocked",
      "branch_count",
      "candidates",
      "family_count",
      "hold",
      "live_orders_allowed",
      "metadata",
      "no_signal",
      "promoted",
      "reason",
      "safe_to_promote",
      "selected",
      "strategy_report_only",
      "strategy_ts_ns"
    ],
    "bridge_good_but_hold_rows": 1099,
    "candidate_rows_count": 0,
    "diagnostics_keys": [
      "activation_bridge_report_only",
      "activation_candidate_count",
      "activation_mode",
      "activation_reason",
      "activation_selected_branch_id",
      "activation_selected_family_id",
      "branch_frame_count",
      "bridge",
      "broker_side_effects_allowed",
      "doctrine_leaves_active",
      "doctrine_leaves_observed",
      "families",
      "hold_only",
      "live_orders_allowed"
    ],
    "max_activation_candidate_count": 0,
    "non_hold_count": 0,
    "rows_sampled": 1347,
    "sample_good_hold_decision": {
      "action": "HOLD",
      "activation_candidate_count": "0",
      "activation_reason": "no_candidate",
      "activation_selected_branch_id": "",
      "activation_selected_family_id": "",
      "activation_selected_score": "",
      "data_valid": "1",
      "has_activation_report_json": true,
      "has_diagnostics_json": true,
      "has_family_scope_candidates_json": true,
      "hold_only": "1",
      "id": "1780895496213-0",
      "provider_ready_classic": "1",
      "reason": "hold_only_family_features_consumer_bridge",
      "safe_to_consume": "1"
    },
    "scope_candidates_len": null,
    "scope_candidates_type": "dict",
    "top_activation_reasons": {
      "no_candidate": 1099,
      "view_data_invalid": 248
    },
    "top_reasons": {
      "hold_only_family_features_consumer_bridge": 1347
    }
  },
  "errors": {
    "error_services": {
      "execution": 2,
      "feeds": 2,
      "monitor": 2,
      "strategy": 6
    },
    "error_types": {
      "FeatureFamilyContractError": 5,
      "TimeoutError": 1,
      "UNKNOWN": 2,
      "feeds_service_loop_error": 2,
      "system_error": 2
    },
    "feature_family_contract_error_seen": true,
    "recent_examples": [
      {
        "detail": "",
        "error_type": "UNKNOWN",
        "id": "1780895307444-0",
        "service": "execution",
        "where": null
      },
      {
        "detail": "Timeout reading from socket",
        "error_type": "TimeoutError",
        "id": "1780895307428-0",
        "service": "strategy",
        "where": "strategy_hold_bridge_loop_error"
      },
      {
        "detail": "StreamTransportError:Failed to XADD to 'ticks:mme:fut:zerodha:stream': Timeout reading from socket",
        "error_type": "feeds_service_loop_error",
        "id": "1780895307425-0",
        "service": "feeds",
        "where": null
      },
      {
        "detail": "StreamTransportError:Failed to XADD to 'ticks:mme:fut:zerodha:stream': Timeout reading from socket",
        "error_type": "feeds_service_loop_error",
        "id": "1780895305079-0",
        "service": "feeds",
        "where": null
      },
      {
        "detail": "",
        "error_type": "system_error",
        "id": "1780894486439-0",
        "service": "monitor",
        "where": null
      },
      {
        "detail": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')",
        "error_type": "FeatureFamilyContractError",
        "id": "1780894056216-0",
        "service": "strategy",
        "where": "strategy_hold_bridge_loop_error"
      },
      {
        "detail": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')",
        "error_type": "FeatureFamilyContractError",
        "id": "1780894055709-0",
        "service": "strategy",
        "where": "strategy_hold_bridge_loop_error"
      },
      {
        "detail": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')",
        "error_type": "FeatureFamilyContractError",
        "id": "1780894055155-0",
        "service": "strategy",
        "where": "strategy_hold_bridge_loop_error"
      },
      {
        "detail": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')",
        "error_type": "FeatureFamilyContractError",
        "id": "1780894054515-0",
        "service": "strategy",
        "where": "strategy_hold_bridge_loop_error"
      },
      {
        "detail": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')",
        "error_type": "FeatureFamilyContractError",
        "id": "1780894054050-0",
        "service": "strategy",
        "where": "strategy_hold_bridge_loop_error"
      },
      {
        "detail": "",
        "error_type": "system_error",
        "id": "1780894033321-0",
        "service": "monitor",
        "where": null
      },
      {
        "detail": "",
        "error_type": "UNKNOWN",
        "id": "1780894033064-0",
        "service": "execution",
        "where": null
      }
    ],
    "rows_sampled": 12,
    "strategy_bridge_error_seen": false
  },
  "features": {
    "rows_sampled": 273,
    "surface_root_keys_examples": [
      {
        "field": "consumer_view_json",
        "keys": [
          "action",
          "branch_frames",
          "common",
          "data_valid",
          "family_frames",
          "family_status",
          "family_surfaces",
          "features_generated_at_ns",
          "frame_id",
          "frame_ts_ns",
          "hold_only",
          "mapping_repair",
          "market",
          "provider_ready_classic",
          "provider_ready_miso",
          "provider_runtime",
          "reason",
          "regime",
          "safe_to_consume",
          "stage_flags",
          "view_version",
          "warmup_complete"
        ]
      },
      {
        "field": "family_features_json",
        "keys": [
          "common",
          "families",
          "family_features_version",
          "generated_at_ns",
          "market",
          "provider_runtime",
          "r38zb_selected_option_ts_status",
          "r38zf_futures_ts_status",
          "schema_version",
          "service",
          "snapshot",
          "stage_flags"
        ]
      },
      {
        "field": "family_surfaces_json",
        "keys": [
          "builder_abi_audit",
          "contract_note",
          "families",
          "generated_at_ns",
          "provider_runtime",
          "schema_version",
          "service",
          "shared_core",
          "surface_version",
          "surfaces_by_branch"
        ]
      },
      {
        "field": "consumer_view_json",
        "keys": [
          "action",
          "branch_frames",
          "common",
          "data_valid",
          "family_frames",
          "family_status",
          "family_surfaces",
          "features_generated_at_ns",
          "frame_id",
          "frame_ts_ns",
          "hold_only",
          "mapping_repair",
          "market",
          "provider_ready_classic",
          "provider_ready_miso",
          "provider_runtime",
          "reason",
          "regime",
          "safe_to_consume",
          "stage_flags",
          "view_version",
          "warmup_complete"
        ]
      },
      {
        "field": "family_features_json",
        "keys": [
          "common",
          "families",
          "family_features_version",
          "generated_at_ns",
          "market",
          "provider_runtime",
          "r38zb_selected_option_ts_status",
          "r38zf_futures_ts_status",
          "schema_version",
          "service",
          "snapshot",
          "stage_flags"
        ]
      },
      {
        "field": "family_surfaces_json",
        "keys": [
          "builder_abi_audit",
          "contract_note",
          "families",
          "generated_at_ns",
          "provider_runtime",
          "schema_version",
          "service",
          "shared_core",
          "surface_version",
          "surfaces_by_branch"
        ]
      },
      {
        "field": "consumer_view_json",
        "keys": [
          "action",
          "branch_frames",
          "common",
          "data_valid",
          "family_frames",
          "family_status",
          "family_surfaces",
          "features_generated_at_ns",
          "frame_id",
          "frame_ts_ns",
          "hold_only",
          "mapping_repair",
          "market",
          "provider_ready_classic",
          "provider_ready_miso",
          "provider_runtime",
          "reason",
          "regime",
          "safe_to_consume",
          "stage_flags",
          "view_version",
          "warmup_complete"
        ]
      },
      {
        "field": "family_features_json",
        "keys": [
          "common",
          "families",
          "family_features_version",
          "generated_at_ns",
          "market",
          "provider_runtime",
          "r38zb_selected_option_ts_status",
          "r38zf_futures_ts_status",
          "schema_version",
          "service",
          "snapshot",
          "stage_flags"
        ]
      },
      {
        "field": "family_surfaces_json",
        "keys": [
          "builder_abi_audit",
          "contract_note",
          "families",
          "generated_at_ns",
          "provider_runtime",
          "schema_version",
          "service",
          "shared_core",
          "surface_version",
          "surfaces_by_branch"
        ]
      },
      {
        "field": "consumer_view_json",
        "keys": [
          "action",
          "branch_frames",
          "common",
          "data_valid",
          "family_frames",
          "family_status",
          "family_surfaces",
          "features_generated_at_ns",
          "frame_id",
          "frame_ts_ns",
          "hold_only",
          "mapping_repair",
          "market",
          "provider_ready_classic",
          "provider_ready_miso",
          "provider_runtime",
          "reason",
          "regime",
          "safe_to_consume",
          "stage_flags",
          "view_version",
          "warmup_complete"
        ]
      }
    ],
    "top_candidate_like_fields": {
      "common.futures.ofi_persist_score=0.0": 546,
      "families.MISB.eligible=False": 546,
      "families.MISC.eligible=False": 546,
      "families.MISO.eligible=False": 546,
      "families.MISR.eligible=False": 546,
      "families.MIST.eligible=False": 546,
      "family_status.MISB.contract_eligible=False": 273,
      "family_status.MISB.surface_eligible=False": 273,
      "family_status.MISC.contract_eligible=False": 273,
      "family_status.MISC.surface_eligible=False": 273,
      "family_status.MISO.contract_eligible=False": 273,
      "family_status.MISO.surface_eligible=False": 273,
      "family_status.MISR.contract_eligible=False": 273,
      "family_status.MISR.surface_eligible=False": 273,
      "family_status.MIST.contract_eligible=False": 273,
      "family_status.MIST.surface_eligible=False": 273,
      "family_surfaces.shared_core.futures.active.contradiction_score_call=-0.0": 273,
      "family_surfaces.shared_core.futures.active.contradiction_score_put=0.0": 273,
      "family_surfaces.shared_core.futures.active.direction_score=0.0": 273,
      "family_surfaces.shared_core.futures.active.trend_score=0.0": 273,
      "family_surfaces.shared_core.futures.dhan.context_score=0.0": 273,
      "family_surfaces.shared_core.futures.dhan.contradiction_score_call=-0.0": 273,
      "family_surfaces.shared_core.futures.dhan.contradiction_score_put=0.0": 273,
      "family_surfaces.shared_core.futures.dhan.direction_score=0.0": 273,
      "family_surfaces.shared_core.futures.dhan.trend_score=0.0": 273,
      "family_surfaces.shared_core.strike_selection.classic_call.oi_bias_score=0.0": 273,
      "family_surfaces.shared_core.strike_selection.classic_call.oi_wall_summary.oi_bias_score=0.0": 273,
      "family_surfaces.shared_core.strike_selection.classic_put.oi_bias_score=0.0": 273,
      "family_surfaces.shared_core.strike_selection.ladder_surface.oi_wall_summary.oi_bias_score=0.0": 273,
      "stage_flags.session_eligible=True": 546
    },
    "top_stage_failures": {
      "branch_frames.miso_call.surface.failed_stage=runtime_disabled": 273,
      "branch_frames.miso_call.surface.pre_batch9_failed_stage=strike_bundle_present": 273,
      "branch_frames.miso_put.surface.failed_stage=runtime_disabled": 273,
      "branch_frames.miso_put.surface.pre_batch9_failed_stage=strike_bundle_present": 273,
      "families.MISO.branches.CALL.failed_stage=runtime_disabled": 273,
      "families.MISO.branches.CALL.pre_batch9_failed_stage=strike_bundle_present": 273,
      "families.MISO.call.failed_stage=runtime_disabled": 273,
      "families.MISO.call.pre_batch9_failed_stage=strike_bundle_present": 273,
      "families.MISO.put.failed_stage=runtime_disabled": 273,
      "families.MISO.put.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_frames.miso_call.surface.failed_stage=runtime_disabled": 273,
      "family_frames.miso_call.surface.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_frames.miso_put.surface.failed_stage=runtime_disabled": 273,
      "family_frames.miso_put.surface.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.families.MISO.branches.CALL.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.branches.CALL.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.families.MISO.branches.PUT.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.branches.PUT.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.families.MISO.call.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.call.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.families.MISO.call_support.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.call_support.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.families.MISO.put.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.put.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.families.MISO.put_support.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.put_support.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.surfaces_by_branch.miso_call.failed_stage=runtime_disabled": 273,
      "family_surfaces.surfaces_by_branch.miso_call.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.surfaces_by_branch.miso_put.failed_stage=runtime_disabled": 273,
      "family_surfaces.surfaces_by_branch.miso_put.pre_batch9_failed_stage=strike_bundle_present": 273
    },
    "top_surface_blockers": {
      "families.MISO.call_support.futures_contradiction_blocked=False": 546,
      "families.MISO.call_support.queue_reload_blocked=False": 546,
      "families.MISO.put_support.futures_contradiction_blocked=False": 546,
      "families.MISO.put_support.queue_reload_blocked=False": 546,
      "family_surfaces.families.MISO.call.batch9_freeze_blocked_reason=runtime_disabled": 273,
      "family_surfaces.families.MISO.call.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.call.futures_contradiction_blocked=False": 273,
      "family_surfaces.families.MISO.call.microstructure.queue_reload_blocked=False": 273,
      "family_surfaces.families.MISO.call.pre_batch9_failed_stage=strike_bundle_present": 273,
      "family_surfaces.families.MISO.call.queue_reload_blocked=False": 273,
      "family_surfaces.families.MISO.put.failed_stage=runtime_disabled": 273,
      "family_surfaces.families.MISO.put.futures_contradiction_blocked=False": 273,
      "family_surfaces.families.MISO.put.microstructure.queue_reload_blocked=False": 273,
      "family_surfaces.families.MISO.put.queue_reload_blocked=False": 273,
      "family_surfaces.families.MIST.branches.CALL.micro_trap_blocked=True": 273,
      "family_surfaces.families.MIST.branches.PUT.micro_trap_blocked=True": 273,
      "family_surfaces.families.MIST.call.micro_trap_blocked=True": 273,
      "family_surfaces.families.MIST.put.micro_trap_blocked=True": 273,
      "family_surfaces.provider_runtime.failover_mode=MANUAL": 273,
      "family_surfaces.provider_runtime.pending_failover=False": 273,
      "family_surfaces.provider_runtime.transition_reason=BOOTSTRAP": 273,
      "family_surfaces.shared_core.provider_runtime.failover_mode=MANUAL": 273,
      "family_surfaces.shared_core.provider_runtime.pending_failover=False": 273,
      "family_surfaces.shared_core.provider_runtime.transition_reason=BOOTSTRAP": 273,
      "provider_runtime.failover_active=True": 816,
      "provider_runtime.failover_mode=MANUAL": 819,
      "provider_runtime.pending_failover=False": 819,
      "provider_runtime.provider_runtime_blocked=False": 816,
      "provider_runtime.transition_reason=BOOTSTRAP": 819,
      "reason=features_consumer_view_mapping_repair_o16": 273
    }
  },
  "interpretation": {
    "candidate_positive": false,
    "probable_next_seam": "strategy_bridge_or_family_contract_error"
  }
}
AUDIT_RC=0

## Safety after readonly audit
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=PASS_R31G_BRIDGE_OR_CONTRACT_ERROR_SEAM_IDENTIFIED_NO_PATCH_YET
