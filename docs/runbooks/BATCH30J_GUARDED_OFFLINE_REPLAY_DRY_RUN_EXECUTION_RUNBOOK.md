# Batch 30J Runbook

Executes the repaired guarded offline replay command from 30I-R3 under strict no-broker/no-live/no-order checks.

Pre/post checks verify runtime locks, service processes, orders stream, position state, and Redis stream movement.

If GREEN_CONTINUE, proceed to 30K artifact integrity audit. If REVIEW_REQUIRED, inspect 30J artifacts in 30J-R2 first. If FAIL, do not continue parity work until blockers are resolved.
