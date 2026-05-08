# Batch 30J-R4I Runbook

Fixes the previous dynamic probe's import path issue by using PYTHONPATH and sys.path insertion, then performs source-specific selector/adapter validation.

This batch does not install metadata into the dataset root, does not execute replay_run.py, does not patch production source, and does not start services.

If GREEN_CONTINUE, proceed to a reversible metadata install plan and dry selector validation only. Replay execution remains blocked until dry selector validation passes.
