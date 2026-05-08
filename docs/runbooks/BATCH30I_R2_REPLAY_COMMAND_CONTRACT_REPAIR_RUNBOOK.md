# Batch 30I-R2 Runbook

Repairs the 30I guarded replay command contract. It maps confirmed `--run-root` as the replay output sink and explains the lack of an explicit dry-run flag as an offline replay entrypoint semantic.

This batch runs `bin/replay_run.py --help` only for CLI inspection. It does not execute replay, does not materialize data, does not start services, does not write/delete Redis keys, does not enable paper/live, and does not send orders.

If GREEN_CONTINUE, proceed to 30J guarded offline replay dry-run execution with strict no-broker/no-live/no-order wrapper.
