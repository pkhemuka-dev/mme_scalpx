# Batch 30J-R4L Runbook

Final pre-execution safety gate for the guarded offline replay command.

This batch validates installed metadata, planned command safety, argparse compatibility, runtime isolation, Redis health, order safety, and replay compile status.

It does not execute replay_run.py. If REVIEW/GREEN with no blockers, next is 30J-R5 guarded offline replay execution attempt with pre/post safety checks and no broker/order/live.
