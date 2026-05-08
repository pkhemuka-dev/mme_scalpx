# Batch 30J-R4J Runbook

Creates a reversible metadata install plan and validates planned replay_run.py CLI arguments using a local argparse mirror only.

This batch does not copy metadata into the dataset root, does not execute replay_run.py, does not start services, and does not write/delete Redis keys.

If REVIEW/GREEN with no blockers, the next step is 30J-R4K: guarded reversible metadata install plus immediate dry CLI selector validation only, still no replay execution.
