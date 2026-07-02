# LANE-X-LIVE-SESSION-MISLS-RADAR-R1_10MIN_COUNT_AUDIT_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_100159

## Proof

```json
{
  "branch_quality": {
    "CALL.futures_present.true": 149,
    "CALL.paired_quote_valid.true": 149,
    "CALL.ready_for_offline_logger_fixture.true": 149,
    "CALL.selected_quote_valid.true": 149,
    "CALL.shadow_context_present.false": 149,
    "CALL.tradability_ok.true": 149,
    "CALL.trap_context_present.false": 149,
    "PUT.futures_present.true": 149,
    "PUT.paired_quote_valid.true": 149,
    "PUT.ready_for_offline_logger_fixture.true": 149,
    "PUT.selected_quote_valid.true": 149,
    "PUT.shadow_context_present.false": 149,
    "PUT.tradability_ok.true": 149,
    "PUT.trap_context_present.false": 149
  },
  "classification": "PASS_MISLS_R1_10MIN_LIVE_RADAR_STABLE_READY_HOLD_BLOCKED_NO_ORDER",
  "counts": {
    "call_event_valid": 149,
    "call_hold_blocked": 149,
    "call_ready": 149,
    "entries_seen": 149,
    "payloads_parsed": 149,
    "put_event_valid": 149,
    "put_hold_blocked": 149,
    "put_ready": 149
  },
  "danger_env_absent": true,
  "hold_blocked_total": 298,
  "misls_samples_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R1_10MIN_COUNT_AUDIT_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_100159_misls_window_samples.json",
  "next_step": "Keep observe-only running. Later run pseal/export and evidence bundle. Do not enable paper/live from MISLS.",
  "no_activation_patch": true,
  "no_execution_start": true,
  "no_family_order_patch": true,
  "no_features_patch": true,
  "no_order": true,
  "no_paper": true,
  "no_redis_delete": true,
  "no_registry_patch": true,
  "no_risk_start": true,
  "no_source_patch": true,
  "no_strategy_patch": true,
  "observe_env_ok": true,
  "payload_summary_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R1_10MIN_COUNT_AUDIT_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_100159_payload_window_summary.json",
  "process_present": true,
  "ready_total": 298,
  "status_after_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R1_10MIN_COUNT_AUDIT_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_100159_status_after.txt",
  "tag": "LANE-X-LIVE-SESSION-MISLS-RADAR-R1_10MIN_COUNT_AUDIT_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_100159",
  "valid_total": 298,
  "window_end_ms": "1781584926851",
  "window_start_ms": "1781584326838"
}
```

## Status after excerpt

```text
ERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"12956418","instrument_token":"12956418","option_symbol":"NIFTY2661623900CE","strike":23900.0,"option_price":45.45,"tick_size":0.05,"target_points"...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1781584932336051010,"frame_id":"features-1781584932336051010","frame_ts_ns":1781584932336051010,"ts_event_ns":1781584932336051010,"frame_valid":false,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1781584932336050944,"snapshot":{"valid":false,"validity":"MARKETDATA_INCOMPLETE_OR_UNSYNCED","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmu...
family_features_version=1.1
frame_ts_ns=1781584932336051010
frame_valid=0
strategy_mode=AUTO
system_state=DISABLED
ts_event_ns=1781584932336051010
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-16 10:12:12 age=0.96s
family_features_version=1.1
frame_ts_ns=1781584932336051010
regime=FAST

[state:option:confirm]
updated_at=2026-06-16 10:12:12 age=0.96s
frame_ts_ns=1781584932336051010

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1781584932069-0 | ts=2026-06-16 15:42:11 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23932.0 | bid=23930.1 | ask=23938.0
id=1781584931100-0 | ts=2026-06-16 15:42:10 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23930.3 | bid=23930.3 | ask=23935.0

[ticks:mme:opt:stream]
id=1781584932858-0 | ts=2026-06-16 15:42:12 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623950CE | instrument_token=12956930 | trading_symbol=NIFTY2661623950CE | instrument_role=CE_ATM1 | ltp=24.9 | bid=24.95 | ask=25.05
id=1781584932827-0 | ts=2026-06-16 15:42:12 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623900CE | instrument_token=12956418 | trading_symbol=NIFTY2661623900CE | instrument_role=CE_ATM | ltp=45.2 | bid=45.1 | ask=45.2

[features:mme:stream]
id=1781584932937-0 | ts=2026-06-16 10:12:12 | age=0.98s | frame_id=features-1781584932336051010
id=1781584929162-0 | ts=2026-06-16 10:12:08 | age=4.75s | frame_id=features-1781584928571989578

[system:health:stream]
id=1781584933279-0 | ts=2026-06-16 10:12:13 | age=0.04s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1
id=1781584933225-0 | ts=2026-06-16 10:12:13 | age=0.09s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1781584890883-0 | ts=2026-06-16 10:11:30 | age=43.08s | service_name=monitor | event_type=system_error
id=1781584861743-0 | ts=2026-06-16 10:11:01 | age=72.31s | service_name=monitor | event_type=system_error

[ticks:mme:fut:zerodha:stream]
id=1781584932067-0 | ts=2026-06-16 15:42:11 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23932.0 | bid=23930.1 | ask=23938.0
id=1781584931098-0 | ts=2026-06-16 15:42:10 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23930.3 | bid=23930.3 | ask=23935.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1781584932853-0 | ts=2026-06-16 15:42:12 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623950CE | instrument_token=12956930 | trading_symbol=NIFTY2661623950CE | instrument_role=CE_ATM1 | ltp=24.9 | bid=24.95 | ask=25.05
id=1781584932824-0 | ts=2026-06-16 15:42:12 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623900CE | instrument_token=12956418 | trading_symbol=NIFTY2661623900CE | instrument_role=CE_ATM | ltp=45.2 | bid=45.1 | ask=45.2

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1781584933396-0 | ts=2026-06-16 10:12:13 | age=0.00s | family_runtime_mode=OBSERVE_ONLY
id=1781584933339-0 | ts=2026-06-16 10:12:13 | age=0.06s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1781584890883-0 | ts=2026-06-16 10:11:30 | age=43.42s | service_name=monitor | event_type=system_error
id=1781584861743-0 | ts=2026-06-16 10:11:01 | age=72.65s | service_name=monitor | event_type=system_error
id=1781584832664-0 | ts=2026-06-16 10:10:31 | age=101.95s | service_name=monitor | event_type=system_error
id=1781584803285-0 | ts=2026-06-16 10:10:02 | age=131.34s | service_name=monitor | event_type=system_error
id=1781584776446-0 | ts=2026-06-16 10:09:35 | age=157.78s | service_name=monitor | event_type=system_error
id=1781584749004-0 | ts=2026-06-16 10:09:08 | age=185.31s | service_name=monitor | event_type=system_error
id=1781584601465-0 | ts=2026-06-16 10:06:40 | age=333.05s | service_name=monitor | event_type=system_error
id=1781584512803-0 | ts=2026-06-16 10:05:11 | age=421.77s | service_name=monitor | event_type=system_error
id=1781584478934-0 | ts=2026-06-16 10:04:38 | age=455.39s | service_name=monitor | event_type=system_error
id=1781584447801-0 | ts=2026-06-16 10:04:06 | age=486.83s | service_name=monitor | event_type=system_error

```

## Safety

NO source patch
NO features.py patch
NO strategy.py patch
NO registry patch
NO activation patch
NO FAMILY_ORDER patch
NO broker order
NO paper
NO risk start
NO execution start
NO Redis delete
