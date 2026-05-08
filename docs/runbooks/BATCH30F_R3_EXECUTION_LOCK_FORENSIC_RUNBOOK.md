# Batch 30F-R3 Runbook

Read-only forensic classifier for `lock:execution` found by 30F-R2.

If lock is live or not proven safe, do not proceed. If stale/unowned, use a separate guarded cleanup package or wait for TTL expiry, then rerun 30F-R3 or 30F-R2 before 30G.
