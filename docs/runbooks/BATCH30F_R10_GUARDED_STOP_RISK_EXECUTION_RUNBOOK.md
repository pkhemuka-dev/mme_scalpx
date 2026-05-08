# Batch 30F-R10 Runbook

Guarded stop for unintended risk/execution services found by 30F-R9.

Runs only if orders are zero, position is flat/absent, systemd manual mode is inactive, and execution lock owner matches the visible execution PID. Sends SIGTERM only and waits for natural lock expiry. It never deletes Redis keys.

If GREEN but features/strategy still run, proceed to a separate guarded feature/strategy cleanup before 30G.
