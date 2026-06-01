# B3-R55_AGGREGATE_HELPER_FILE_DISCOVERY_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R55_FILE_DISCOVERY_PATCH_PLAN_READY_NO_PATCH`

Root cause: helper chose artifacts directory for all files, but R47 candidate audit is at run root.

Allowed patch file: `app/mme_scalpx/replay/artifacts.py` only.

Forbidden now: bin/replay_run.py hook, strategy/risk/execution/provider changes, Redis/live/order paths.

Next: B3-R56 one-file discovery patch, compile-only.
