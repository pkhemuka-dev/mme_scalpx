# Batch 30F-R6 Runbook

Read-only source/process owner audit for `lock:execution` refresh source.

If the owner is a generic `python -m app.mme_scalpx.main` process, use a separate guarded cleanup plan. Do not delete `lock:execution` directly while an owner PID is alive.
