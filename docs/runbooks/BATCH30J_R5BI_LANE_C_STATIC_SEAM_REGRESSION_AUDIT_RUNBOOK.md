# 30J-R5BI Runbook

Purpose: after-market Lane C hardening that Lane E is not doing.

This verifies the guarded `bin/replay_run.py` seam after R5BF/R5BH-R1 without running replay.

It is safe to run after market because it does not touch live services, broker/order paths, Redis mutation, or final replay repositories.

This batch does not authorize A64.
