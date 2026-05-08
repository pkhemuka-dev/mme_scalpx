# Batch 30J-R4F-R1A Runbook

Use after 30J-R4F-R1 when cleanup actions are marked failed although post-process and post-lock state are clean.

This batch classifies stale PIDs/zombies/PID reuse and verifies a quiet runtime window. It is read-only.

If GREEN_CONTINUE, rerun 30J-R4F trace under clean offline isolation.
