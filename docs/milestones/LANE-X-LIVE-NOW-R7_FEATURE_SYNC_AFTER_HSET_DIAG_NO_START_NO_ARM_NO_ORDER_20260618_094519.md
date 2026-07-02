# Lane X R7 Feature Sync After HSET Diagnostic

- timestamp: 2026-06-18T09:45:19+05:30
- mode: NO_START_NO_ARM_NO_ORDER
- purpose: inspect why feature sync remains false after selected-option active hash has fields

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=***MASKED***
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== PROCESS SNAPSHOT ===
=== FEATURE SYNC AFTER HSET DIAG ===
diag_rc=0
=== PSTATUS AFTER ===
=== FINAL PROCESS SNAPSHOT ===

## R7 verdict
REVIEW_R7_FEATURE_SYNC_FALSE_DUE_FUT_OPT_SKEW_NO_START_NO_ARM_NO_ORDER
- feature_core: {'market.selected_option_ltp': 128.7, 'provider_runtime.provider_ready_classic': False, 'provider_runtime.provider_ready_miso': False, 'snapshot.active_snapshot_ns': 1781775917000000000, 'snapshot.freshness_ok': True, 'snapshot.fut_opt_skew_ms': 127000, 'snapshot.futures_snapshot_ns': 1781775917000000000, 'snapshot.max_member_age_ms': 0, 'snapshot.packet_gap_ok': True, 'snapshot.selected_option_snapshot_ns': 1781775790000000000, 'snapshot.sync_ok': False, 'snapshot.valid': False, 'snapshot.validity': 'MARKETDATA_INCOMPLETE_OR_UNSYNCED', 'snapshot.warmup_ok': True, 'stage_flags.provider_ready_classic': False, 'stage_flags.provider_ready_miso': False, 'stage_flags.tradability_ok': False}
- skews: {'feature_active_vs_opt_skew_ms': 127000.0, 'feature_fut_opt_skew_ms': 127000.0, 'redis_fut_opt_skew_ms': 128000.0}
- diag_rc=0
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO
