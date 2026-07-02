# LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435

## Proof

```json
{
  "classification": "PASS_LIVE_RICH_DATA_OBSERVE_ENABLEMENT_STARTED_NO_ORDER",
  "danger_env_absent": true,
  "disk_file": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_disk.txt",
  "env_file": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_env.txt",
  "git_status_file": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_git_status.txt",
  "next_step": "After 3-5 minutes, run growth audit: feeds/features/decisions/consumer_view/rich surfaces. Do not enable paper until pstatus/paper_status gate passes.",
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
  "process_present": true,
  "ps_after": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_ps_after.txt",
  "ps_before": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_ps_before.txt",
  "redis_keys_file": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_redis_keys.txt",
  "redis_streams_file": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_redis_streams.txt",
  "rich_key_markers": {
    "consumer": false,
    "decision_or_candidate": true,
    "family": false,
    "feature": true,
    "selected_option": false,
    "surface": false
  },
  "start_rc": 0,
  "start_status": "already_running",
  "status_file": "run/audits/LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435_status.txt",
  "tag": "LANE-X-LIVE-RICH-DATA-OBSERVE-ENABLEMENT-R0_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082435"
}
```

## Status excerpt

```text
===========================================================================================

[state:features:mme:fut]
updated_at=2026-06-16 08:25:39 age=1.74s
frame_id=features-1781578539657220168
feature_state_json: {"frame_id":"features-1781578539657220168","frame_ts_ns":1781578539657220168,"frame_valid":false,"warmup_complete":true,"regime":"NORMAL","selected_option":{"side":"CALL","ltp":0.0,"spread":0.0,"spread_ratio":0.0,"depth_total":0.0,"depth_ok":false,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":null,"response_efficiency":0.0,"tradability_ok":false}}
family_frames_json: {"mist_call":{"frame_id":"mist_call-1781578539657220168","frame_ts_ns":1781578539657220168,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":null,"active_selected_option_provider_id":null,"active_option_context_provider_id":null,"instrument_key":null,"instrument_token":null,"option_symbol":null,"strike":null,"option_price":null,"tick_size":0.05,"target_points":5.0,"stop_points":4.0,"eligible":false,"tr...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1781578539657220168,"frame_id":"features-1781578539657220168","frame_ts_ns":1781578539657220168,"ts_event_ns":1781578539657220168,"frame_valid":false,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1781578539657220096,"snapshot":{"valid":false,"validity":"MARKETDATA_COMPOSITION_FAIL","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":...
family_features_version=1.1
frame_ts_ns=1781578539657220168
frame_valid=0
strategy_mode=AUTO
system_state=DISABLED
ts_event_ns=1781578539657220168
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-16 08:25:39 age=1.80s
family_features_version=1.1
frame_ts_ns=1781578539657220168
regime=NORMAL

[state:option:confirm]
updated_at=2026-06-16 08:25:39 age=1.80s
frame_ts_ns=1781578539657220168

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
no entries

[ticks:mme:opt:stream]
no entries

[features:mme:stream]
id=1781578539857-0 | ts=2026-06-16 08:25:39 | age=1.81s | frame_id=features-1781578539657220168
id=1781578538082-0 | ts=2026-06-16 08:25:37 | age=3.60s | frame_id=features-1781578537864150386

[system:health:stream]
id=1781578539565-0 | ts=2026-06-16 08:25:39 | age=1.90s | instance_id=strategy:mme-scalpx:1636 | status=OK | detail=strategy_hold_bridge_ok
id=1781578537763-0 | ts=2026-06-16 08:25:37 | age=3.70s | instance_id=features:mme-scalpx:1635 | status=OK | detail=features_ok

[system:errors:stream]
id=1781577796981-0 | ts=2026-06-16 08:13:16 | age=744.48s | instance_id=strategy:mme-scalpx:1636 | error_type=FeatureFamilyContractError
id=1781577796804-0 | ts=2026-06-16 08:13:16 | age=744.66s | instance_id=strategy:mme-scalpx:1636 | error_type=FeatureFamilyContractError

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
id=1781577796981-0 | ts=2026-06-16 08:13:16 | age=744.49s | instance_id=strategy:mme-scalpx:1636 | error_type=FeatureFamilyContractError
id=1781577796804-0 | ts=2026-06-16 08:13:16 | age=744.66s | instance_id=strategy:mme-scalpx:1636 | error_type=FeatureFamilyContractError
id=1777888475661-0 | ts=2026-05-04 15:24:35 | age=3690065.81s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888475608-0 | ts=2026-05-04 15:24:33 | age=3690068.46s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=LockError:Failed to refresh lock 'lock:feeds': Timeout re... | selection_version=mme-instruments-v1
id=1777888201411-0 | ts=2026-05-04 15:20:01 | age=3690340.06s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201359-0 | ts=2026-05-04 15:20:01 | age=3690340.11s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201307-0 | ts=2026-05-04 15:20:01 | age=3690340.16s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201255-0 | ts=2026-05-04 15:20:01 | age=3690340.21s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201203-0 | ts=2026-05-04 15:20:01 | age=3690340.27s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1777888201151-0 | ts=2026-05-04 15:20:01 | age=3690340.32s | service_name=feeds | instance_id=feeds:mme-scalpx:22458 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

```

## Redis stream/key excerpt

```text
===== stream lengths, likely keys only =====
state:option:confirm hash_len=3
features:mme:stream stream_len=4617
decisions:mme:stream stream_len=1560
state:baselines:mme:fut hash_len=3
health:strategy hash_len=6
system:health:stream stream_len=286
state:features:mme:fut hash_len=24
health:features hash_len=6

===== redis ping =====
PONG

===== likely useful keys =====
state:option:confirm
features:mme:stream
decisions:mme:stream
state:baselines:mme:fut
health:strategy
system:health:stream
state:features:mme:fut
health:features

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
