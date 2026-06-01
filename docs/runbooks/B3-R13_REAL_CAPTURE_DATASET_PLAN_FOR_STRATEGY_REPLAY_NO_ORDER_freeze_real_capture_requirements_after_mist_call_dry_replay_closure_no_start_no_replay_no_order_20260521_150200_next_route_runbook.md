# B3-R13_REAL_CAPTURE_DATASET_PLAN_FOR_STRATEGY_REPLAY_NO_ORDER_freeze_real_capture_requirements_after_mist_call_dry_replay_closure_no_start_no_replay_no_order_20260521_150200 next route

classification: `PASS_B3_R13_REAL_CAPTURE_DATASET_PLAN_READY_NO_ORDER`
plan_status: `REAL_CAPTURE_PLAN_READY`

Next:
`B3-R14_REAL_CAPTURE_READINESS_CHECK_NO_START_NO_ORDER`

B3-R14 should only check readiness for a real capture window.
It should not start services unless explicitly approved later.

Rules:
- no broker order
- no paper/live
- no PnL claim
- no all-family replay
- no source patch
