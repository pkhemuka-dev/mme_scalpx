# Batch 30F-R4 Runbook

Read-only TTL expiry recheck for `lock:execution` after 30F-R3.

If PASS_GREEN_CONTINUE, proceed to 30G selected dataset structure validator offline. If stale lock remains, do not delete it manually; use a guarded cleanup proposal batch.
