# Batch 30H Runbook

Audits replay dry-run adapter compatibility and writes a guarded dry-run plan under the selected dataset folder.

This batch does not execute replay, does not materialize data, does not start services, does not write/delete Redis keys, does not enable paper/live, and does not send orders.

If GREEN_CONTINUE, proceed to 30I guarded replay dry-run preflight command construction, still no replay execution.
