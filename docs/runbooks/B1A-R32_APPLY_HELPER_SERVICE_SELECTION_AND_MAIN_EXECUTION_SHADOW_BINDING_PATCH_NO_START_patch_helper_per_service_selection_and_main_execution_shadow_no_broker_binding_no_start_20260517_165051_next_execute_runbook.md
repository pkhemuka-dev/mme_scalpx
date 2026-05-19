# B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START next execute route

Classification: `PASS_R32_PATCH_COMPILE_DRY_RUN_READY_NO_START`

## Next route

`B1A-R33_RETRY_HELPER_EXECUTE_AFTER_R32_PATCH_APPROVAL_REQUIRED`

If PASS, next batch may run guarded helper execute with exact approval:

`I APPROVE B1 OBSERVE-ONLY STACK START HELPER EXECUTE: NO PAPER, NO LIVE, NO BROKER ORDER, NO REPLAY, NO PNL, START FEATURES/STRATEGY/RISK/EXECUTION OBSERVE-ONLY ONLY`

The next execute batch must verify:

- selected per-service commands
- `SCALPX_OBSERVE_ONLY=1`
- forbidden env vars unset
- no order stream growth
- risk stream presence/growth
- execution stream presence/growth
- process snapshot
- helper execute report
