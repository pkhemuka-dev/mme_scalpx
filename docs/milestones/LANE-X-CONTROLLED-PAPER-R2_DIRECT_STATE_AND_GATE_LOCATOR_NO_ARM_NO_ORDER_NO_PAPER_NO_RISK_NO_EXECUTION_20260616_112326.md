# LANE-X-CONTROLLED-PAPER-R2_DIRECT_STATE_AND_GATE_LOCATOR_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_112326

```json
{
  "classification": "REVIEW_CONTROLLED_PAPER_R2_NO_EXPLICIT_FLAT_POSITION_PROOF_NO_ARM_NO_ORDER",
  "danger_env_absent": true,
  "execution_candidate_keys": [
    "health:dhan:execution",
    "health:zerodha:execution"
  ],
  "execution_safe_proof_keys": [
    "health:dhan:execution",
    "health:zerodha:execution"
  ],
  "flat_proof_keys": [],
  "gate_visible": false,
  "helper_found": {
    "paper_status": false,
    "pstatus": false
  },
  "matched_key_count": 16,
  "next_step": "No paper arming unless route/gate is proven and user gives explicit separate approval.",
  "no_execution_start": true,
  "no_order": true,
  "no_paper_armed": true,
  "no_redis_delete": true,
  "no_risk_start": true,
  "no_source_patch": true,
  "observe_env_ok": true,
  "paper_candidate_keys": [],
  "position_candidate_keys": [],
  "process_present": true,
  "risk_candidate_keys": [],
  "risk_fail_closed_proof_keys": [],
  "route_allowed_visible": false,
  "source_file": "run/audits/LANE-X-CONTROLLED-PAPER-R2_DIRECT_STATE_AND_GATE_LOCATOR_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_112326_source_locator.txt",
  "state_file": "run/audits/LANE-X-CONTROLLED-PAPER-R2_DIRECT_STATE_AND_GATE_LOCATOR_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_112326_state_locator.json",
  "status_file": "run/audits/LANE-X-CONTROLLED-PAPER-R2_DIRECT_STATE_AND_GATE_LOCATOR_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_112326_status.txt",
  "tag": "LANE-X-CONTROLLED-PAPER-R2_DIRECT_STATE_AND_GATE_LOCATOR_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_112326"
}
```

## Status excerpt

```text
ing_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23954.1 | bid=23949.9 | ask=23952.0
id=1781589205070-0 | ts=2026-06-16 16:53:24 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23952.0 | bid=23949.9 | ask=23952.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1781589206829-0 | ts=2026-06-16 16:53:26 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623950CE | instrument_token=12956930 | trading_symbol=NIFTY2661623950CE | instrument_role=CE_ATM1 | ltp=29.25 | bid=29.25 | ask=29.35
id=1781589206806-0 | ts=2026-06-16 16:53:26 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623900CE | instrument_token=12956418 | trading_symbol=NIFTY2661623900CE | instrument_role=CE_ATM | ltp=55.35 | bid=55.35 | ask=55.5

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1781589206835-0 | ts=2026-06-16 11:23:26 | age=0.01s | family_runtime_mode=OBSERVE_ONLY
id=1781589206813-0 | ts=2026-06-16 11:23:26 | age=0.03s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1781589023320-0 | ts=2026-06-16 11:20:23 | age=183.59s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=StreamTransportError:Failed to XADD to 'system:health:str... | selection_version=mme-instruments-v1
id=1781588942224-0 | ts=2026-06-16 11:19:01 | age=264.97s | instance_id=strategy:mme-scalpx:1636 | error_type=StrategyBridgeError
id=1781588942223-0 | ts=2026-06-16 11:19:01 | age=265.10s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=HashTransportError:Failed to write hash 'state:provider:r... | selection_version=mme-instruments-v1

===== pauto_status =====
latest=run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260616_081314
status=RUNNING pid=1452

state:
{
  "action_mode": "apply",
  "actions": [],
  "freshness": {
    "decisions": {
      "age_ms": 915,
      "latest_id": "1781589203628-0",
      "stream": "decisions:mme:stream"
    },
    "features": {
      "age_ms": 1390,
      "latest_id": "1781589203101-0",
      "stream": "features:mme:stream"
    },
    "fut": {
      "age_ms": 1615,
      "latest_id": "1781589202799-0",
      "stream": "ticks:mme:fut:zerodha:stream"
    },
    "opt": {
      "age_ms": 135,
      "latest_id": "1781589204303-0",
      "stream": "ticks:mme:opt:selected:zerodha:stream"
    }
  },
  "outdir": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260616_081314",
  "post_action_freshness": {
    "decisions": {
      "age_ms": 1499,
      "latest_id": "1781589203628-0",
      "stream": "decisions:mme:stream"
    },
    "features": {
      "age_ms": 1970,
      "latest_id": "1781589203101-0",
      "stream": "features:mme:stream"
    },
    "fut": {
      "age_ms": 189,
      "latest_id": "1781589204820-0",
      "stream": "ticks:mme:fut:zerodha:stream"
    },
    "opt": {
      "age_ms": 724,
      "latest_id": "1781589204303-0",
      "stream": "ticks:mme:opt:selected:zerodha:stream"
    }
  },
  "post_action_service_counts": {
    "features": 1,
    "feeds_service": 1,
    "generic_main": 0,
    "recorder": 1,
    "strategy": 1
  },
  "provider": {
    "context_status": "UNAVAILABLE",
    "futures_status": "HEALTHY",
    "mode": "OBSERVE_ONLY",
    "selected_status": "FAILOVER_ACTIVE"
  },
  "read_only_safety": {
    "execution_start_allowed": false,
    "order_allowed": false,
    "redis_delete_allowed": false,
    "risk_start_allowed": false
  },
  "safety": {
    "execution": 0,
    "execution_pids": 0,
    "orders": 0,
    "risk": 0,
    "risk_pids": 0
  },
  "service_counts": {
    "features": 1,
    "feeds_service": 1,
    "generic_main": 0,
    "recorder": 1,
    "strategy": 1
  },
  "ts_utc": "2026-06-16T05:53:24.245153+00:00"
}
files:
total 3.5M
drwxrwxr-x 2 Lenovo Lenovo 4.0K Jun 16 11:23 durable_capture
-rw-rw-r-- 1 Lenovo Lenovo 1.3K Jun 16 08:13 features_supervisor_start.log
-rw-rw-r-- 1 Lenovo Lenovo 2.3M Jun 16 11:20 feeds_supervisor_start.log
-rw-rw-r-- 1 Lenovo Lenovo  35K Jun 16 11:19 strategy_supervisor_start.log
-rw-rw-r-- 1 Lenovo Lenovo   22 Jun 16 08:13 supervisor.log
-rw-rw-r-- 1 Lenovo Lenovo    5 Jun 16 08:13 supervisor.pid
-rw-rw-r-- 1 Lenovo Lenovo 1.1M Jun 16 11:23 supervisor_events.jsonl
-rw-rw-r-- 1 Lenovo Lenovo 2.0K Jun 16 11:23 supervisor_state.json

log_tail:
nohup: ignoring input

===== pstatus =====
Command 'pstatus' not found, did you mean:
  command 'qstatus' from deb gridengine-client (8.1.9+dfsg-10build1)
Try: apt install <deb name>

===== paper_status =====
paper_status: command not found

```

## Source locator excerpt

```text
===== source locator =====
app/mme_scalpx/core/names.py:782:HASH_STATE_RISK: Final[str] = "state:risk"
app/mme_scalpx/core/names.py:783:HASH_STATE_POSITION_MME: Final[str] = "state:position:mme"
app/mme_scalpx/core/names.py:784:HASH_STATE_EXECUTION: Final[str] = "state:execution"
app/mme_scalpx/main.py:127:        and not os.environ.get("SCALPX_PAPER_ARMED")
app/mme_scalpx/main.py:128:        and not os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME")
app/mme_scalpx/main.py:1131:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/main.py:1132:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/main.py:1133:        "SCALPX_PAPER_ARMED",
app/mme_scalpx/integrations/bootstrap_quote.py:78:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/integrations/bootstrap_quote.py:79:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/integrations/broker_api.py:1437:_A6_R3_ALLOWED_CONTROLLED_PAPER_ROUTES = frozenset(("paper", "sandbox"))
app/mme_scalpx/integrations/broker_api.py:1492:def submit_controlled_paper_sandbox_order(
app/mme_scalpx/integrations/broker_api.py:1511:        "controlled_paper": True,
app/mme_scalpx/integrations/broker_api.py:1540:    if route not in _A6_R3_ALLOWED_CONTROLLED_PAPER_ROUTES:
app/mme_scalpx/integrations/broker_api.py:1543:            status="FAIL_CLOSED_INVALID_CONTROLLED_PAPER_ROUTE",
app/mme_scalpx/ops_dashboard/server.py:44:    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/ops_dashboard/server.py:45:    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/ops_dashboard/server.py:49:    "SCALPX_PAPER_ARMED",
app/mme_scalpx/ops_dashboard/server.py:536:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/ops_dashboard/server.py:537:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/ops_dashboard/server.py:541:        "SCALPX_PAPER_ARMED",
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:172:        from app.mme_scalpx.services.controlled_paper_runtime import (
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2084:        _forbidden = ['SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME', 'SCALPX_CONTROLLED_PAPER_SCOPE_ACK', 'SCALPX_REAL_LIVE_ALLOWED', 'SCALPX_ALLOW_REAL_LIVE', 'SCALPX_ALLOW_BROKER_ORDERS', 'SCALPX_PAPER_ARMED', 'SCALPX_ENABLE_PAPER', 'SCALPX_ENABLE_LIVE']
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2159:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2160:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2164:        "SCALPX_PAPER_ARMED",
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2642:CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN = "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2643:CONTROLLED_PAPER_SANDBOX_BACKEND_REQUIRED = "CONTROLLED_PAPER_SANDBOX_BACKEND_REQUIRED"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2644:CONTROLLED_PAPER_SCOPE_REQUIRED = "CONTROLLED_PAPER_SCOPE_REQUIRED"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2645:CONTROLLED_PAPER_SCOPE_MISMATCH = "CONTROLLED_PAPER_SCOPE_MISMATCH"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2646:CONTROLLED_PAPER_QTY_CAP_FAIL = "CONTROLLED_PAPER_QTY_CAP_FAIL"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2647:CONTROLLED_PAPER_POSITION_NOT_FLAT = "CONTROLLED_PAPER_POSITION_NOT_FLAT"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2648:CONTROLLED_PAPER_INVALID_ROUTE = "CONTROLLED_PAPER_INVALID_ROUTE"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2649:CONTROLLED_PAPER_PREFLIGHT_OK = "CONTROLLED_PAPER_PREFLIGHT_OK"
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2674:def controlled_paper_order_cycle_preflight(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2698:        "controlled_paper": True,
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2722:            "reason": CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN,
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2727:        return {**base, "status": "FAIL_CLOSED", "reason": CONTROLLED_PAPER_INVALID_ROUTE}
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2730:        return {**base, "status": "FAIL_CLOSED", "reason": CONTROLLED_PAPER_SCOPE_REQUIRED}
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2738:            "reason": CONTROLLED_PAPER_SCOPE_MISMATCH,
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2744:        return {**base, "status": "FAIL_CLOSED", "reason": CONTROLLED_PAPER_QTY_CAP_FAIL}
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2747:        return {**base, "status": "FAIL_CLOSED", "reason": CONTROLLED_PAPER_POSITION_NOT_FLAT}
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:2753:            "reason":
```
