# Batch 30J-R5 Runbook

Runs the first guarded offline replay execution attempt using the exact command passed by 30J-R4L-R3.

Preconditions: clean runtime, all locks absent, no risk/execution, orders zero, position flat, metadata installed from 30J-R4K, command safety passed.

Postconditions: no orders, no runtime locks/processes, position flat, run-root artifacts classified. If execution fails, diagnose before any next parity step.
