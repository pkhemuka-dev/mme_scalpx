# LANE-F-R4R18A_AFTERMARKET_RAW_DIAGNOSTIC_PATCH_HANDOFF_BUNDLE_NO_START next live-session runbook

classification: `PASS_LANE_F_R4R18A_AFTERMARKET_HANDOFF_BUNDLE_READY_NEXT_LIVE_SESSION`

Next route: `WAIT_FOR_NEXT_LIVE_SESSION_R4R18_OBSERVE_ONLY_STACK_RESTART_PREFLIGHT`

At next live session:

1. Run R4R18 preflight first.
2. If clean, approve observe-only restart of feeds/features/strategy only.
3. Do not start risk or execution.
4. Do not enable paper/live.
5. Do not run replay or PnL.
