# Lane X R8 Selected Option Refresh + Skew Probe

- timestamp: 2026-06-18T09:47:14+05:30
- mode: HSET_ONLY_NO_START_NO_ARM_NO_ORDER
- purpose: test if latest option tick stream can keep selected-option active snapshot synced with futures

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=***MASKED***
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== PROCESS SNAPSHOT BEFORE ===
=== R8 HSET-ONLY REFRESH LOOP ===
r8_rc=0
=== PSTATUS AFTER ===
=== FINAL PROCESS SNAPSHOT ===

## R8 verdict
PASS_R8_SELECTED_OPTION_REFRESH_CAN_SYNC_WITH_FUTURES_HSET_ONLY_NO_ORDER
- min_skew_ms: 0.0
- last_skew_ms: 0.0
- feature_core_after: {'market.selected_option_ltp': 119.6, 'provider_runtime.provider_ready_classic': False, 'provider_runtime.provider_ready_miso': False, 'snapshot.fut_opt_skew_ms': 0, 'snapshot.futures_snapshot_ns': 1781776094000000000, 'snapshot.selected_option_snapshot_ns': 1781776094000000000, 'snapshot.sync_ok': True, 'snapshot.valid': True, 'snapshot.validity': 'OK', 'stage_flags.provider_ready_classic': False, 'stage_flags.provider_ready_miso': False, 'stage_flags.tradability_ok': False}
- decision_after: {'action': 'HOLD', 'activation_candidate_count': None, 'activation_reason': None, 'candidate_present_shadow': None, 'candidate_true_shadow': None, 'reason': 'no_candidate'}
- r8_rc=0
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO
