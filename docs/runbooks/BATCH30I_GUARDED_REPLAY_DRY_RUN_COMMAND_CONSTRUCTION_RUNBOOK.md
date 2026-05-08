# Batch 30I Runbook

Constructs the guarded replay dry-run command contract only.

This batch does not execute replay, does not materialize data, does not start services, does not write/delete Redis keys, does not enable paper/live, and does not send orders.

If GREEN_CONTINUE, proceed to 30J guarded replay dry-run execution with strict no-broker/no-live/no-order wrapper. If REVIEW_REQUIRED, inspect command flags in 30I-R2 before any execution.
