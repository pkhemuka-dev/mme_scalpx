# Batch 30J-R4 Runbook

Executes the 30J-R3B non-self date-source repaired offline replay command under guarded safety checks.

Pre/post checks verify runtime locks, service processes, orders stream, position state, and Redis stream movement.

No tar bundle is created to avoid disk pressure. If GREEN_CONTINUE, proceed to 30K artifact integrity audit. If REVIEW_REQUIRED, run 30J-R5 artifact/review inspection. If FAIL, diagnose blockers first.
