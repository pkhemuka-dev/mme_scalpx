# LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801

## Proof

```json
{
  "base_growth_ok": true,
  "category_growth": {
    "decision_candidate": 324,
    "feature": 40,
    "futures": 188,
    "health_status": -21,
    "option": 944
  },
  "classification": "REVIEW_CONTROLLED_PAPER_POSITION_OR_HOLDING_KEYS_NONEMPTY_NO_ARM_NO_ORDER",
  "danger_env_absent": true,
  "disk_file": "run/audits/LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801_disk.txt",
  "fail_closed_visible": false,
  "git_status": "run/audits/LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801_git_status.txt",
  "next_step": "Do not arm paper unless classification is PASS and user explicitly approves separate controlled-paper arming command. If FAIL_CLOSED, inspect pstatus/paper_status reason first.",
  "no_activation_patch": true,
  "no_execution_start": true,
  "no_family_order_patch": true,
  "no_features_patch": true,
  "no_order": true,
  "no_paper_armed": true,
  "no_paper_order": true,
  "no_redis_delete": true,
  "no_registry_patch": true,
  "no_risk_start": true,
  "no_source_patch": true,
  "no_strategy_patch": true,
  "observe_env_ok": true,
  "paper_gate_visible": true,
  "paper_status_terms": {
    "mentions_fail_closed": false,
    "mentions_flat": false,
    "mentions_order_zero": true,
    "mentions_paper": true,
    "mentions_pstatus": false,
    "mentions_route_allowed": false
  },
  "position_or_holding_keys_nonempty": {
    "state:position:mme": {
      "len": 14,
      "sample": "has_position\n0\nposition_side\nFLAT\nqty_lots\n0\nqty_units\n0\navg_price\n\nentry_ts_ns\n\nentry_option_symbol\n\nentry_option_token\n\nentry_strike\n\nentry_mode\n\ndecision_id\n\nbroker_order_id\n\nmark_price\n\nrealized_pnl_day\n0\n",
      "type": "hash"
    }
  },
  "process_present": true,
  "safety_growth_keys": {},
  "safety_keys": "run/audits/LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801_safety_keys.txt",
  "snap_after": "run/audits/LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801_redis_after.json",
  "snap_before": "run/audits/LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801_redis_before.json",
  "status_after": "run/audits/LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801_status_after.txt",
  "status_before": "run/audits/LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801_status_before.txt",
  "tag": "LANE-X-CONTROLLED-PAPER-TRIAL-READINESS-AUDIT-R0_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_104801",
  "top_growth": {
    "decisions:ack:stream": {
      "after": 512,
      "before": 384,
      "category": "decision_candidate",
      "delta": 128,
      "type": "stream"
    },
    "decisions:mme:stream": {
      "after": 2391,
      "before": 2195,
      "category": "decision_candidate",
      "delta": 196,
      "type": "stream"
    },
    "features:mme:stream": {
      "after": 86,
      "before": 46,
      "category": "feature",
      "delta": 40,
      "type": "stream"
    },
    "system:health:stream": {
      "after": 10002,
      "before": 10023,
      "category": "health_status",
      "delta": -21,
      "type": "stream"
    },
    "ticks:mme:fut:stream": {
      "after": 126,
      "before": 32,
      "category": "futures",
      "delta": 94,
      "type": "stream"
    },
    "ticks:mme:fut:zerodha:stream": {
      "after": 1987,
      "before": 1893,
      "category": "futures",
      "delta": 94,
      "type": "stream"
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "after": 11377,
      "before": 10905,
      "category": "option",
      "delta": 472,
      "type": "stream"
    },
    "ticks:mme:opt:stream": {
      "after": 618,
      "before": 146,
      "category": "option",
      "delta": 472,
      "type": "stream"
    }
  }
}
```

## Status after excerpt

```text
ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1781587214836713829
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1781587214836713829
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-16 10:50:14 age=1.75s
family_features_version=1.1
frame_ts_ns=1781587214836713829
regime=FAST

[state:option:confirm]
updated_at=2026-06-16 10:50:14 age=1.75s
frame_ts_ns=1781587214836713829

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1781587212583-0 | ts=2026-06-16 16:20:11 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23997.0 | bid=23997.0 | ask=23997.1
id=1781587211603-0 | ts=2026-06-16 16:20:11 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23998.1 | bid=23998.0 | ask=23999.0

[ticks:mme:opt:stream]
id=1781587216582-0 | ts=2026-06-16 16:20:16 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623950CE | instrument_token=12956930 | trading_symbol=NIFTY2661623950CE | instrument_role=CE_ATM1 | ltp=52.55 | bid=52.45 | ask=52.55
id=1781587215840-0 | ts=2026-06-16 16:20:15 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623850PE | instrument_token=12956162 | trading_symbol=NIFTY2661623850PE | instrument_role=PE_ATM1 | ltp=8.8 | bid=8.8 | ask=8.85

[features:mme:stream]
id=1781587215194-0 | ts=2026-06-16 10:50:14 | age=1.77s | frame_id=features-1781587214836713829
id=1781587211947-0 | ts=2026-06-16 10:50:11 | age=5.01s | frame_id=features-1781587211591227772

[system:health:stream]
id=1781587216586-0 | ts=2026-06-16 10:50:16 | age=0.02s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1
id=1781587216525-0 | ts=2026-06-16 10:50:16 | age=0.08s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1781587118263-0 | ts=2026-06-16 10:48:38 | age=98.35s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118211-0 | ts=2026-06-16 10:48:38 | age=98.40s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

[ticks:mme:fut:zerodha:stream]
id=1781587212582-0 | ts=2026-06-16 16:20:11 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23997.0 | bid=23997.0 | ask=23997.1
id=1781587211602-0 | ts=2026-06-16 16:20:11 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23998.1 | bid=23998.0 | ask=23999.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1781587216599-0 | ts=2026-06-16 16:20:16 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623900PE | instrument_token=12956674 | trading_symbol=NIFTY2661623900PE | instrument_role=PE_ATM | ltp=17.75 | bid=17.75 | ask=17.8
id=1781587216579-0 | ts=2026-06-16 16:20:16 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623950CE | instrument_token=12956930 | trading_symbol=NIFTY2661623950CE | instrument_role=CE_ATM1 | ltp=52.55 | bid=52.45 | ask=52.55

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1781587216605-0 | ts=2026-06-16 10:50:16 | age=0.02s | family_runtime_mode=OBSERVE_ONLY
id=1781587216585-0 | ts=2026-06-16 10:50:16 | age=0.04s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1781587118263-0 | ts=2026-06-16 10:48:38 | age=98.35s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118211-0 | ts=2026-06-16 10:48:38 | age=98.41s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118157-0 | ts=2026-06-16 10:48:38 | age=98.46s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118103-0 | ts=2026-06-16 10:48:38 | age=98.51s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118050-0 | ts=2026-06-16 10:48:38 | age=98.57s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117996-0 | ts=2026-06-16 10:48:37 | age=98.62s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117944-0 | ts=2026-06-16 10:48:37 | age=98.67s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117890-0 | ts=2026-06-16 10:48:37 | age=98.73s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117834-0 | ts=2026-06-16 10:48:37 | age=98.78s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117781-0 | ts=2026-06-16 10:48:37 | age=98.84s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

```

## Safety

NO source patch
NO features.py patch
NO strategy.py patch
NO registry patch
NO activation patch
NO FAMILY_ORDER patch
NO broker order
NO paper armed
NO paper order
NO risk start
NO execution start
NO Redis delete
