# Batch 30J-R4L-R1 Runbook

Use after 30J-R4L when final replay-command safety gate is blocked by runtime contamination.

This batch stops app.mme_scalpx.main runtime owners under strict guards and waits for locks to expire naturally. It does not delete Redis keys or locks and does not mutate replay metadata.

If GREEN_CONTINUE, rerun 30J-R4L final safety gate under clean offline isolation.
