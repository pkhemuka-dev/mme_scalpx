# DATAKEEP-B2 — Live Session Validity Gate Runbook

Purpose: prepare one safe live-session test to prove PnL/backtest-grade capture.

Safety:
- No paper
- No live
- No broker order
- No risk/execution start
- No source patch
- No replay
- No PnL calculation in this gate

Goal verdict:
- PASS_VALID_LIVE_DATA_READY_FOR_QEDGE
- BLOCKED_AT_FEEDS
- BLOCKED_AT_FEATURES
- BLOCKED_AT_STRATEGY_VIEW
- BLOCKED_AT_SAFETY

Required live proof:
1. pfeedcheck = HEALTHY_RECORDING
2. futures tick stream growing
3. selected option tick stream growing
4. provider_runtime hash populated/current
5. active_fut hash populated with ltp > 0
6. active_selected_option hash populated with ltp > 0
7. features:mme:stream growing
8. feature snapshot_valid/data_valid = true
9. decisions:mme:stream growing
10. activation_reason is not only view_data_invalid
11. orders:mme:stream unchanged / zero
12. position remains FLAT

Live-session sequence:
1. Run: pdisk and df -h .
2. Run: pfeeds
3. Wait 60–120 seconds
4. Run: pfeedcheck
5. Continue only if pfeedcheck is HEALTHY_RECORDING
6. Run: pstack
7. Wait 60–120 seconds
8. Run: pstackcheck
9. Run DATAKEEP-B3 live validity gate
10. Stop if any blocker appears

Do not move to paper trading until PASS_VALID_LIVE_DATA_READY_FOR_QEDGE is achieved.
