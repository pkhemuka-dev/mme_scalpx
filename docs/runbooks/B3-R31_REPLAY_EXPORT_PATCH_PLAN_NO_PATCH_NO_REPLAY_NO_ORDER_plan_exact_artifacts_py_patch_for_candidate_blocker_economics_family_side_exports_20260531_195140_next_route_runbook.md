# B3-R31_REPLAY_EXPORT_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER next route

Recommended next:

`B3-R32_REPLAY_ANALYSIS_EXPORTS_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER`

Patch only:

`app/mme_scalpx/replay/artifacts.py`

Do not touch:

- strategy
- risk
- execution
- provider runtime
- live services
- broker/order/paper/live

Validation:

- backup
- compile
- AST
- proof
- no replay in patch batch

Then use B3-R33 to replay/smoke-test exports.
