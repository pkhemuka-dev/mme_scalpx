# B1-R23 Start Helper Arg-Shape Patch

Safety: helper arg-shape patch and dry-run proof only. No service start, no replay, no Redis write/delete, no broker call, no order, no paper/live, no PnL.

Classification: `HELPER_ARG_SHAPE_PATCH_DRY_RUN_PROOF_OK_NO_SERVICE_START`

Selected future command: `/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --service strategy --service risk --service execution`

Selection reason: `main.py supports singular --service; observe-only enforced by SCALPX_OBSERVE_ONLY=1 env`

## Future execute approval text

`I APPROVE B1 OBSERVE-ONLY STACK START HELPER EXECUTE: NO PAPER, NO LIVE, NO BROKER ORDER, NO REPLAY, NO PNL, START FEATURES/STRATEGY/RISK/EXECUTION OBSERVE-ONLY ONLY`

Only `--dry-run` was executed in B1-R23.

Audit: `run/audits/B1-R23_INTEGRATED_START_HELPER_ARG_SHAPE_PATCH_NO_START_patch_helper_to_main_cli_service_arg_shape_20260512_221243_audit.json`
