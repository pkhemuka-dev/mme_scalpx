# LANE-MIV-LIVE-R3_OBSERVE_ONLY_CAPTURE_RESTART_REUSE_AFTER_STALE_TAPE_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_restart_or_reuse_observe_only_capture_after_r2_found_durable_tape_present_but_not_growing_20260612_094011 Runbook

If PASS:
- leave observe-only capture running

If REVIEW still not growing:
- diagnose provider/auth/feed lock
- do not start risk/execution
- do not enable paper/live
- do not delete Redis/locks
