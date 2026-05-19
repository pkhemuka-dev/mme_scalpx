# B1-R23 Start Helper Arg-Shape Patch

Created UTC: 2026-05-12T16:42:44.437252+00:00

classification: `HELPER_ARG_SHAPE_PATCH_DRY_RUN_PROOF_OK_NO_SERVICE_START`

patch_pass: `True`

selected_future_command: `/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --service strategy --service risk --service execution`

selection_reason: `main.py supports singular --service; observe-only enforced by SCALPX_OBSERVE_ONLY=1 env`

removed_unsupported_args: `['--observe-only', '--services']`

uses_repeated_service_arg: `True`

py_compile_ok: `True`

dry_run_classification: `DRY_RUN_ONLY_NO_SERVICE_START`

stream_deltas: `{'features': 0, 'decisions': 0, 'risk': 0, 'execution': 0, 'orders': 0}`

true_backtest_pnl_still_blocked: `True`

Next: `B1-R24_RETRY_HELPER_EXECUTE_AFTER_ARG_SHAPE_PATCH_APPROVAL_REQUIRED`

Proof: `run/proofs/B1-R23_INTEGRATED_START_HELPER_ARG_SHAPE_PATCH_NO_START_patch_helper_to_main_cli_service_arg_shape_20260512_221243_proof.json`
