# Batch 30F-R7 Runbook

Guarded cleanup for a generic `python -m app.mme_scalpx.main` process refreshing `lock:execution`.

This batch sends SIGTERM only when strict safety conditions pass. It does not delete `lock:execution`; it waits for natural TTL expiry after the owner exits.

If GREEN, rerun Lane-C mapping/safety recheck before dataset validation.
