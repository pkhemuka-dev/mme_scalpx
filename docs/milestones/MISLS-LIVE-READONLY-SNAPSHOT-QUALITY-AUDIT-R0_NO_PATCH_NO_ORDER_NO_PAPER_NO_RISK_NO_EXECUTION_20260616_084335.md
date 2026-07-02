# MISLS-LIVE-READONLY-SNAPSHOT-QUALITY-AUDIT-R0_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_084335

## Proof

```json
{
  "classification": "REVIEW_MISLS_LIVE_READONLY_NO_FULL_READY_SNAPSHOT_YET_NO_ORDER",
  "counts": {
    "call_event_valid": 0,
    "call_hold_blocked": 0,
    "call_ready": 0,
    "entries_seen": 60,
    "paired_quote_invalid": 120,
    "payloads_parsed": 60,
    "put_event_valid": 0,
    "put_hold_blocked": 0,
    "put_ready": 0,
    "selected_quote_invalid": 120,
    "shadow_missing": 120,
    "tradability_not_ok": 120,
    "trap_missing": 120
  },
  "danger_env_absent": true,
  "feature_stream": "features:mme:stream",
  "next_step": "If PASS: keep observing and later run MISLS read-only count audit over longer window. If REVIEW no-ready: inspect samples_file rejection reasons.",
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
  "safety_lengths": {},
  "samples_file": "run/audits/MISLS-LIVE-READONLY-SNAPSHOT-QUALITY-AUDIT-R0_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_084335_misls_live_readonly_samples.json",
  "status_file": "run/audits/MISLS-LIVE-READONLY-SNAPSHOT-QUALITY-AUDIT-R0_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_084335_status.txt",
  "tag": "MISLS-LIVE-READONLY-SNAPSHOT-QUALITY-AUDIT-R0_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_084335"
}
```

## Status excerpt

```text
me:opt:selected:zerodha:stream      xlen=0        growth_5s=0
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=1106     growth_5s=3
errors                   system:errors:stream                       xlen=0        growth_5s=0

status=NOT_HEALTHY_PROCESS_DEAD
remark=pfeeds process is not alive.

===== pcheck =====
[2J[HScalpX MME live observer | now=2026-06-16 08:43:41 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

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
health:features: status=OK service=features instance=features:mme-scalpx:1635 age=2.48s ttl=12519ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:1636 age=1.39s ttl=13610ms message=-
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
updated_at=2026-06-16 08:43:40 age=0.61s
frame_id=features-1781579620665555767
feature_state_json: {"frame_id":"features-1781579620665555767","frame_ts_ns":1781579620665555767,"frame_valid":false,"warmup_complete":true,"regime":"NORMAL","selected_option":{"side":"CALL","ltp":0.0,"spread":0.0,"spread_ratio":0.0,"depth_total":0.0,"depth_ok":false,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":null,"response_efficiency":null,"tradability_ok":false}}
family_frames_json: {"mist_call":{"frame_id":"mist_call-1781579620665555767","frame_ts_ns":1781579620665555767,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":null,"active_selected_option_provider_id":null,"active_option_context_provider_id":null,"instrument_key":null,"instrument_token":null,"option_symbol":null,"strike":null,"option_price":null,"tick_size":0.05,"target_points":5.0,"stop_points":4.0,"eligible":false,"tr...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1781579620665555767,"frame_id":"features-1781579620665555767","frame_ts_ns":1781579620665555767,"ts_event_ns":1781579620665555767,"frame_valid":false,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1781579620665555712,"snapshot":{"valid":false,"validity":"MARKETDATA_INCOMPLETE_OR_QUALITY_FAIL","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"w...
family_features_version=1.1
frame_ts_ns=1781579620665555767
frame_valid=0
strategy_mode=AUTO
system_state=DISABLED
ts_event_ns=1781579620665555767
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-16 08:43:40 age=0.66s
family_features_version=1.1
frame_ts_ns=1781579620665555767
regime=NORMAL

[state:option:confirm]
updated_at=2026-06-16 08:43:40 age=0.66s
frame_ts_ns=1781579620665555767

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
no entries

[ticks:mme:opt:stream]
no entries

[features:mme:stream]
id=1781579620864-0 | ts=2026-06-16 08:43:40 | age=0.66s | frame_id=features-1781579620665555767
id=1781579619088-0 | ts=2026-06-16 08:43:38 | age=2.45s | frame_id=features-1781579618878560450

[system:health:stream]
id=1781579619869-0 | ts=2026-06-16 08:43:39 | age=1.46s | instance_id=strategy:mme-scalpx:1636 | status=OK | detail=strategy_hold_bridge_ok
id=1781579618778-0 | ts=2026-06-16 08:43:38 | age=2.55s | instance_id=features:mme-scalpx:1635 | status=OK | detail=features_ok

[system:errors:stream]
no entries

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
