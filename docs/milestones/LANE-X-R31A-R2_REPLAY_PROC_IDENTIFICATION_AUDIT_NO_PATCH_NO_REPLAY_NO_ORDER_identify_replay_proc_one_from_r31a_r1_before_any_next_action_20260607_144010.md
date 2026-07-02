# LANE-X-R31A-R2_REPLAY_PROC_IDENTIFICATION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_replay_proc_one_from_r31a_r1_before_any_next_action_20260607_144010

classification: REVIEW_LANE_X_R31A_R2_REAL_REPLAY_PROC_PRESENT_STOP_NO_PATCH_NO_REPLAY_NO_ORDER

- redis_ok: 1
- orders: 0
- risk_stream: 0
- execution_stream: 0
- match_count: 2
- real_replay_count: 1
- false_positive_count: 1

## Matches

  23521   23515      64 S+   bash run/patches/LANE-B-R5C_BASELINE_SHADOW_DRY_RUN_PACKAGE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143758_r5d_reversible_baseline_shadow_plan.sh
  23530   23521      63 R+   .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337 --selection-mode single_day --single-day 2026-06-02 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --fill-model immediate_market --run-label LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907_BASELINE_PRE_R27E_R27G --run-root run/replay/lane_b_r5d/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907/baseline_pre_r27e_r27g

process_snapshot: `run/audits/LANE-X-R31A-R2_REPLAY_PROC_IDENTIFICATION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_replay_proc_one_from_r31a_r1_before_any_next_action_20260607_144010_process_snapshot.txt`
matches: `run/audits/LANE-X-R31A-R2_REPLAY_PROC_IDENTIFICATION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_replay_proc_one_from_r31a_r1_before_any_next_action_20260607_144010_replay_proc_matches.txt`

Boundary: no patch, no replay, no order, no paper/live, no risk/execution, no Redis delete, no lock delete.
