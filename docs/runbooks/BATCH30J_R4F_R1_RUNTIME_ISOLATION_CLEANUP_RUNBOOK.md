# Batch 30J-R4F-R1 Runbook

Use when Lane C offline replay/parity work is blocked by runtime locks or active app.mme_scalpx.main service owners.

This batch stops only app.mme_scalpx.main runtime owners under strict guards: Redis OK, orders zero, position flat, systemd manual mode inactive, and prior 30J-R4F runtime-isolation blocker present.

It does not delete Redis keys or locks. It waits for locks to expire naturally after stopping process owners.

If GREEN_CONTINUE, rerun the strong market date trace under clean offline isolation.
