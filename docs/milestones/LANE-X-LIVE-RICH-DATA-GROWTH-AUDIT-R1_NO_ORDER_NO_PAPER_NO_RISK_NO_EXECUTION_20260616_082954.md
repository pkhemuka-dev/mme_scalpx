# LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954

## Proof

```json
{
  "after_key_count": 8,
  "before_key_count": 8,
  "category_growth": {
    "decision_candidate": 1035,
    "health_snapshot": 187,
    "rich_feature_surface": -4652
  },
  "classification": "REVIEW_LIVE_GROWTH_BASE_OK_RICH_SURFACES_NOT_VISIBLE_YET_NO_ORDER",
  "danger_env_absent": true,
  "growth_key_count": 3,
  "live_files_after": "run/audits/LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954_live_files_after.txt",
  "live_files_before": "run/audits/LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954_live_files_before.txt",
  "next_step": "If PASS: keep observe-only running and later run pseal/export. If REVIEW rich-only: locate exact feature hash/stream keys; do not enable paper yet.",
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
  "rich_marker_presence": {
    "consumer": false,
    "decision_or_candidate": true,
    "family": false,
    "feature": true,
    "selected_option": true,
    "surface": false
  },
  "safety_growth_keys": {},
  "snapshot_after": "run/audits/LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954_redis_snapshot_after.json",
  "snapshot_before": "run/audits/LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954_redis_snapshot_before.json",
  "status_after_file": "run/audits/LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954_status_after.txt",
  "status_before_file": "run/audits/LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954_status_before.txt",
  "tag": "LANE-X-LIVE-RICH-DATA-GROWTH-AUDIT-R1_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_082954",
  "top_growth": {
    "decisions:mme:stream": {
      "after": 3793,
      "before": 2758,
      "category": "decision_candidate",
      "delta": 1035,
      "type": "stream"
    },
    "features:mme:stream": {
      "after": 118,
      "before": 4770,
      "category": "rich_feature_surface",
      "delta": -4652,
      "type": "stream"
    },
    "system:health:stream": {
      "after": 692,
      "before": 505,
      "category": "health_snapshot",
      "delta": 187,
      "type": "stream"
    }
  }
}
```

## Status after excerpt

```text
:selected:zerodha:stream      xlen=0        growth_5s=0
opt_selected_dhan        ticks:mme:opt:selected:dhan:stream         xlen=0        growth_5s=0
opt_context_dhan         ticks:mme:opt:context:dhan:stream          xlen=0        growth_5s=0
health                   system:health:stream                       xlen=690      growth_5s=3
errors                   system:errors:stream                       xlen=0        growth_5s=0

status=NOT_HEALTHY_PROCESS_DEAD
remark=pfeeds process is not alive.

===== pcheck after =====
[2J[HScalpX MME live observer | now=2026-06-16 08:34:34 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

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
health:features: status=OK service=features instance=features:mme-scalpx:1635 age=0.36s ttl=14640ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:1636 age=2.03s ttl=12970ms message=-
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
updated_at=2026-06-16 08:34:34 age=0.28s
frame_id=features-1781579074083736319
feature_state_json: {"frame_id":"features-1781579074083736319","frame_ts_ns":1781579074083736319,"frame_valid":false,"warmup_complete":true,"regime":"NORMAL","selected_option":{"side":"CALL","ltp":0.0,"spread":0.0,"spread_ratio":0.0,"depth_total":0.0,"depth_ok":false,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":null,"response_efficiency":null,"tradability_ok":false}}
family_frames_json: {"mist_call":{"frame_id":"mist_call-1781579074083736319","frame_ts_ns":1781579074083736319,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":null,"active_selected_option_provider_id":null,"active_option_context_provider_id":null,"instrument_key":null,"instrument_token":null,"option_symbol":null,"strike":null,"option_price":null,"tick_size":0.05,"target_points":5.0,"stop_points":4.0,"eligible":false,"tr...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1781579074083736319,"frame_id":"features-1781579074083736319","frame_ts_ns":1781579074083736319,"ts_event_ns":1781579074083736319,"frame_valid":false,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1781579074083736320,"snapshot":{"valid":false,"validity":"MARKETDATA_INCOMPLETE_OR_UNSYNCED","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmu...
family_features_version=1.1
frame_ts_ns=1781579074083736319
frame_valid=0
strategy_mode=AUTO
system_state=DISABLED
ts_event_ns=1781579074083736319
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-16 08:34:34 age=0.32s
family_features_version=1.1
frame_ts_ns=1781579074083736319
regime=NORMAL

[state:option:confirm]
updated_at=2026-06-16 08:34:34 age=0.32s
frame_ts_ns=1781579074083736319

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
no entries

[ticks:mme:opt:stream]
no entries

[features:mme:stream]
id=1781579074326-0 | ts=2026-06-16 08:34:34 | age=0.33s | frame_id=features-1781579074083736319
id=1781579072349-0 | ts=2026-06-16 08:34:31 | age=2.42s | frame_id=features-1781579071988729848

[system:health:stream]
id=1781579074361-0 | ts=2026-06-16 08:34:34 | age=0.05s | instance_id=strategy:mme-scalpx:1636 | status=OK | detail=strategy_hold_bridge_ok
id=1781579073983-0 | ts=2026-06-16 08:34:33 | age=0.43s | instance_id=features:mme-scalpx:1635 | status=OK | detail=features_ok

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
