# Batch 30J-R4L-R3 Runbook

Reruns the final replay-command safety gate after the post-cleanup quiet-window classifier passed with no blockers.

This batch validates installed metadata, planned command safety, argparse compatibility, runtime isolation, Redis health, order safety, and replay compile status.

It does not execute replay_run.py. If REVIEW/GREEN with no blockers, next is 30J-R5 guarded offline replay execution attempt with pre/post safety checks and no broker/order/live.
