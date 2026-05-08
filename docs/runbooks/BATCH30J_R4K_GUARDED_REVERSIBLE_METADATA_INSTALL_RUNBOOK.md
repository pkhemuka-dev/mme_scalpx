# Batch 30J-R4K Runbook

Performs the first guarded reversible metadata install into the selected replay dataset root.

It backs up existing targets when present, installs candidate metadata, validates installed metadata through selector API and dry argparse mirror, and rolls back automatically if validation fails.

This batch does not execute replay_run.py, does not start services, does not write/delete Redis keys, and does not enable paper/live.

If REVIEW/GREEN with no blockers, proceed to 30J-R4L final replay-command safety gate before any guarded offline replay execution attempt.
