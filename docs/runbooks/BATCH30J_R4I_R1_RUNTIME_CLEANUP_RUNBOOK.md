# Batch 30J-R4I-R1 Runbook

Use after 30J-R4I when source-specific selector probe is blocked only by runtime contamination.

This batch stops app.mme_scalpx.main runtime owners under strict guards and waits for locks to expire naturally. It does not delete Redis keys or locks.

If GREEN_CONTINUE, rerun source-specific selector probe under clean offline isolation.
