# Batch 30J-R2 Runbook

Retries 30J after correcting the 30J parser bug that failed to read the nested 30I-R3 `entrypoint.direct_broker_order_path=false` field.

Executes the repaired guarded offline replay command only after preflight safety checks pass.

Pre/post checks verify runtime locks, service processes, orders stream, position state, and Redis stream movement.

If GREEN_CONTINUE, proceed to 30K artifact integrity audit. If REVIEW_REQUIRED, inspect 30J-R2 artifacts first. If FAIL, do not continue parity work until blockers are resolved.
