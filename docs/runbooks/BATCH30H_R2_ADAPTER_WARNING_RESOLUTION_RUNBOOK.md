# Batch 30H-R2 Runbook

Resolves 30H adapter warnings by inspecting the actual replay source surfaces and existing replay entrypoints.

This batch does not execute replay, does not materialize data, does not start services, does not write/delete Redis keys, does not enable paper/live, and does not send orders.

If GREEN_CONTINUE, proceed to 30I guarded replay dry-run preflight command construction. 30I still must not execute replay.
