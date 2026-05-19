# B1-R22F Helper Execute Failure Final Review

Safety: final review only. No patch, no service start, no replay, no Redis write/delete, no broker call, no order, no paper/live, no PnL.

Classification: `MAIN_CLI_REJECTS_HELPER_ARGUMENTS`

Selected command: `/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --observe-only --services features,strategy,risk,execution`

Start returncode: `2`

## stderr tail

```text
usage: python -m app.mme_scalpx.main [-h] [--service SERVICE]
                                     [--bootstrap-provider BOOTSTRAP_PROVIDER]
                                     [--doctor] [--skip-group-bootstrap]
                                     [--replay-start-wall-time-ns REPLAY_START_WALL_TIME_NS]
python -m app.mme_scalpx.main: error: unrecognized arguments: --observe-only --services features,strategy,risk,execution

```

## Next

`B1-R23_INTEGRATED_START_HELPER_ARG_SHAPE_PATCH_NO_START`

Audit: `run/audits/B1-R22F_HELPER_EXECUTE_FAILURE_FINAL_REVIEW_NO_REPLAY_NO_PNL_extract_exact_main_cli_error_and_final_route_20260512_221048_audit.json`
