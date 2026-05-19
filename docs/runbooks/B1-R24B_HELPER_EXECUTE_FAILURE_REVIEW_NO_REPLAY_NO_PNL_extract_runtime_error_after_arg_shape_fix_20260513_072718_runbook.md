# B1-R24B Helper Execute Failure Review

Safety: review only. No patch, no service start, no replay, no Redis write/delete, no broker call, no order, no paper/live, no PnL.

Classification: `MAIN_RETURNED_RUNTIME_FAILURE_CODE_1`

Selected command: `/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --service strategy --service risk --service execution`

Start returncode: `1`

## stdout tail

```text
{"level":"INFO","logger":"app.mme_scalpx.main","message":"logging_configured level=INFO format=json","process":8375,"thread":"MainThread","ts":"2026-05-12T16:44:48.170922+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"bootstrap_provider_not_configured","process":8375,"thread":"MainThread","ts":"2026-05-12T16:44:48.171485+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"dependency_surfaces_resolved runtime_instruments=0 feed_adapter=0 market_data_adapter=0 feed_adapters=0 zerodha_feed_adapter=0 dhan_feed_adapter=0 dhan_context_adapter=0 broker=0","process":8375,"thread":"MainThread","ts":"2026-05-12T16:44:48.225685+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"consumer_group_bootstrap_completed replay=False stream_count=7","process":8375,"thread":"MainThread","ts":"2026-05-12T16:44:48.908435+00:00"}
{"level":"ERROR","logger":"app.mme_scalpx.main","message":"bootstrap_orchestration_failed error=execution service requires registered broker. Use register_bootstrap_dependencies(broker=...).","process":8375,"thread":"MainThread","ts":"2026-05-12T16:44:48.908717+00:00"}
{"level":"INFO","logger":"app.mme_scalpx.main","message":"shutdown_completed_cleanly","process":8375,"thread":"MainThread","ts":"2026-05-12T16:44:48.909156+00:00"}

```

## stderr tail

```text

```

## Next

`B1-R25_INTEGRATED_MAIN_RUNTIME_FAILURE_REVIEW_NO_START`

Audit: `run/audits/B1-R24B_HELPER_EXECUTE_FAILURE_REVIEW_NO_REPLAY_NO_PNL_extract_runtime_error_after_arg_shape_fix_20260513_072718_audit.json`
