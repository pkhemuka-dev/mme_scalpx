# Lane X Live Now R3 Provider + Snapshot Sync Diagnostic

- timestamp: 2026-06-18T09:36:09+05:30
- mode: NO_START_NO_ARM_NO_ORDER
- purpose: diagnose MARKETDATA_INCOMPLETE_OR_UNSYNCED / provider_ready=false

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=***MASKED***
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== PROCESS SNAPSHOT ===
=== PROVIDER + SNAPSHOT REDIS DIAG ===
diag_rc=0
=== PSTATUS AFTER ===
=== FINAL PROCESS SNAPSHOT ===

## R3 verdict
PASS_R3_MARKETDATA_SYNC_NOT_CURRENT_BLOCKER_NO_START_NO_ARM_NO_ORDER
- sync: {'feature_active_snapshot_ns': None, 'feature_freshness_ok': None, 'feature_futures_snapshot_ns': None, 'feature_packet_gap_ok': None, 'feature_selected_option_snapshot_ns': None, 'feature_snapshot_valid': None, 'feature_snapshot_validity': None, 'feature_sync_ok': None, 'feature_warmup_ok': None, 'redis_fut_active_ts_ns': 1781774928000000000, 'redis_fut_opt_skew_ms': None, 'redis_fut_opt_skew_ns': None, 'redis_opt_active_ts_ns': None}
- diag_rc=0
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO
