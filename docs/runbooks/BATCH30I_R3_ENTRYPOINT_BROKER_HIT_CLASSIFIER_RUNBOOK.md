# Batch 30I-R3 Runbook

Classifies the static broker/order hits that blocked 30I-R2 and repairs the guarded replay command contract only if no direct broker/order path is found.

This batch may run `bin/replay_run.py --help` only. It does not execute replay, does not materialize data, does not start services, does not write/delete Redis keys, does not enable paper/live, and does not send orders.

If GREEN_CONTINUE, proceed to 30J guarded offline replay dry-run execution using only the repaired command contract.
