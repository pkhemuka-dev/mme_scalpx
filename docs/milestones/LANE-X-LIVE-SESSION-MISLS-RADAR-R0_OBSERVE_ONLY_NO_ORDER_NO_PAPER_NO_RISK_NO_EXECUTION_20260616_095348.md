# LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348

## Proof

```json
{
  "category_growth": {
    "decision_candidate": 164,
    "futures": 304,
    "health_snapshot": -9,
    "option_selected": 1870,
    "rich_feature_surface": 44
  },
  "classification": "PASS_LIVE_SESSION_MISLS_RADAR_READY_SNAPSHOTS_FOUND_NO_ORDER",
  "danger_env_absent": true,
  "disk_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348_disk.txt",
  "git_status_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348_git_status.txt",
  "misls_counts": {
    "call_event_valid": 80,
    "call_hold_blocked": 80,
    "call_ready": 80,
    "entries_seen": 80,
    "paired_quote_invalid": 0,
    "payloads_parsed": 80,
    "put_event_valid": 80,
    "put_hold_blocked": 80,
    "put_ready": 80,
    "selected_quote_invalid": 0,
    "shadow_missing": 0,
    "tradability_not_ok": 0,
    "trap_missing": 0
  },
  "misls_samples_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348_misls_live_quality_samples.json",
  "next_step": "If PASS ready snapshots found: continue observe-only and later pseal/export. If REVIEW no full ready: inspect rejection counts; do not enable paper.",
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
  "payload_summary_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348_payload_tail_summary.json",
  "process_present": true,
  "rich_markers": {
    "consumer_view": true,
    "family_features": true,
    "family_surfaces": true,
    "miso_shadow_or_shadow_features": true,
    "selected_option": true,
    "tradability": true,
    "trap_events": false
  },
  "rich_visible": true,
  "safety_growth_keys": {},
  "start_rc": 0,
  "start_status": "already_running",
  "status_after_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348_status_after.txt",
  "status_before_file": "run/audits/LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348_status_before.txt",
  "tag": "LANE-X-LIVE-SESSION-MISLS-RADAR-R0_OBSERVE_ONLY_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_095348",
  "top_growth": {
    "decisions:mme:stream": {
      "after": 2860,
      "before": 2696,
      "category": "decision_candidate",
      "delta": 164,
      "type": "stream"
    },
    "features:mme:stream": {
      "after": 282,
      "before": 238,
      "category": "rich_feature_surface",
      "delta": 44,
      "type": "stream"
    },
    "system:health:stream": {
      "after": 10017,
      "before": 10026,
      "category": "health_snapshot",
      "delta": -9,
      "type": "stream"
    },
    "ticks:mme:fut:stream": {
      "after": 933,
      "before": 781,
      "category": "futures",
      "delta": 152,
      "type": "stream"
    },
    "ticks:mme:fut:zerodha:stream": {
      "after": 2568,
      "before": 2416,
      "category": "futures",
      "delta": 152,
      "type": "stream"
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "after": 12352,
      "before": 11417,
      "category": "option_selected",
      "delta": 935,
      "type": "stream"
    },
    "ticks:mme:opt:stream": {
      "after": 12348,
      "before": 11413,
      "category": "option_selected",
      "delta": 935,
      "type": "stream"
    }
  }
}
```

## Status after excerpt

```text
BSERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"12956418","instrument_token":"12956418","option_symbol":"NIFTY2661623900CE","strike":23900.0,"option_price":66.8,"tick_size":0.05,"target_points":...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1781584019998169794,"frame_id":"features-1781584019998169794","frame_ts_ns":1781584019998169794,"ts_event_ns":1781584019998169794,"frame_valid":true,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1781584019998169856,"snapshot":{"valid":true,"validity":"OK","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1781584019998169794
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1781584019998169794
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-16 09:56:59 age=3.76s
family_features_version=1.1
frame_ts_ns=1781584019998169794
regime=FAST

[state:option:confirm]
updated_at=2026-06-16 09:56:59 age=3.76s
frame_ts_ns=1781584019998169794

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1781584023584-0 | ts=2026-06-16 15:27:03 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23963.2 | bid=23961.4 | ask=23968.0
id=1781584021806-0 | ts=2026-06-16 15:27:01 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23963.2 | bid=23960.7 | ask=23968.0

[ticks:mme:opt:stream]
id=1781584023604-0 | ts=2026-06-16 15:27:03 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623900PE | instrument_token=12956674 | trading_symbol=NIFTY2661623900PE | instrument_role=PE_ATM | ltp=32.1 | bid=31.95 | ask=32.05
id=1781584023568-0 | ts=2026-06-16 15:27:03 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623950CE | instrument_token=12956930 | trading_symbol=NIFTY2661623950CE | instrument_role=CE_ATM1 | ltp=40.6 | bid=40.5 | ask=40.6

[features:mme:stream]
id=1781584020656-0 | ts=2026-06-16 09:56:59 | age=3.78s | frame_id=features-1781584019998169794
id=1781584015889-0 | ts=2026-06-16 09:56:55 | age=8.30s | frame_id=features-1781584015478660447

[system:health:stream]
id=1781584023733-0 | ts=2026-06-16 09:57:03 | age=0.05s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1
id=1781584023676-0 | ts=2026-06-16 09:57:03 | age=0.10s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1781584019599-0 | ts=2026-06-16 09:56:59 | age=4.85s | service_name=monitor | event_type=system_error
id=1781583955614-0 | ts=2026-06-16 09:55:54 | age=69.15s | service_name=monitor | event_type=system_error

[ticks:mme:fut:zerodha:stream]
id=1781584023582-0 | ts=2026-06-16 15:27:03 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23963.2 | bid=23961.4 | ask=23968.0
id=1781584021803-0 | ts=2026-06-16 15:27:01 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23963.2 | bid=23960.7 | ask=23968.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1781584023602-0 | ts=2026-06-16 15:27:03 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623900PE | instrument_token=12956674 | trading_symbol=NIFTY2661623900PE | instrument_role=PE_ATM | ltp=32.1 | bid=31.95 | ask=32.05
id=1781584023566-0 | ts=2026-06-16 15:27:03 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623950CE | instrument_token=12956930 | trading_symbol=NIFTY2661623950CE | instrument_role=CE_ATM1 | ltp=40.6 | bid=40.5 | ask=40.6

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1781584023860-0 | ts=2026-06-16 09:57:03 | age=0.04s | family_runtime_mode=OBSERVE_ONLY
id=1781584023798-0 | ts=2026-06-16 09:57:03 | age=0.11s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1781584019599-0 | ts=2026-06-16 09:56:59 | age=5.13s | service_name=monitor | event_type=system_error
id=1781583955614-0 | ts=2026-06-16 09:55:54 | age=69.43s | service_name=monitor | event_type=system_error
id=1781583918522-0 | ts=2026-06-16 09:55:17 | age=106.18s | service_name=monitor | event_type=system_error
id=1781583830943-0 | ts=2026-06-16 09:53:50 | age=193.93s | service_name=monitor | event_type=system_error
id=1781583778562-0 | ts=2026-06-16 09:52:57 | age=246.17s | service_name=monitor | event_type=system_error
id=1781583750542-0 | ts=2026-06-16 09:52:29 | age=274.17s | service_name=monitor | event_type=system_error
id=1781583718969-0 | ts=2026-06-16 09:51:58 | age=305.98s | service_name=monitor | event_type=system_error
id=1781583688955-0 | ts=2026-06-16 09:51:27 | age=336.30s | service_name=monitor | event_type=system_error
id=1781583656846-0 | ts=2026-06-16 09:50:56 | age=368.03s | service_name=monitor | event_type=system_error
id=1781583600592-0 | ts=2026-06-16 09:49:59 | age=424.68s | service_name=monitor | event_type=system_error

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
