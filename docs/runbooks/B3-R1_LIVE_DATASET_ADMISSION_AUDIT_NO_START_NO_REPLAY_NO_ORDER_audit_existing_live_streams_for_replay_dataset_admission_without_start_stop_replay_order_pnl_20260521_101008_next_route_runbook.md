# B3-R1_LIVE_DATASET_ADMISSION_AUDIT_NO_START_NO_REPLAY_NO_ORDER_audit_existing_live_streams_for_replay_dataset_admission_without_start_stop_replay_order_pnl_20260521_101008 next route

classification: `REVIEW_B3_R1_DATASET_ADMISSION_INCOMPLETE_NO_REPLAY_NO_ORDER`
admission: `NOT_ACCEPTED_YET`
next_route: `READ_ONLY_TRIAGE_MISSING_SURFACE`

Fast closure plan:
1. If partial admission passes, stop live probing.
2. After-market, run B3-R2 offline replay dry-run using captured Zerodha/features/decisions surfaces.
3. Keep broker/order/paper/live disabled.
4. Close replay module as MVP if deterministic dry-run + no-side-effect proof passes.

Still not full production-grade until:
- service identity is clean
- Dhan context route is resolved
- clean observe-only pstack proof passes
