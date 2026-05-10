# 26-O23-P-R14-R3-R9-R2 — R9 import failure classifier

- generated_at_utc: `2026-05-10T04:27:44.846531+00:00`
- final_verdict: `FAIL_O23_P_R14_R3_R9_R2_IMPORT_FAILURE_CLASSIFICATION_NOT_PROVEN`
- false_keys: `['manifest_written', 'milestone_written', 'proof_written', 'runbook_written']`
- classification: `R9_BOOTSTRAP_QUOTE_UNMAPPED_IMPORT_FAILURE`
- classification_supported: `True`
- r9_expected_import_only_failure: `True`
- source_ok: `True`
- compile_ok_now: `True`
- import_ok_now: `False`
- failed_modules: `['app.mme_scalpx.integrations.bootstrap_quote', 'app.mme_scalpx.integrations.bootstrap_provider', 'app.mme_scalpx.integrations.runtime_instruments_factory']`
- source_patch_applied: `False`
- service_start_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- risk_execution_not_running: `True`
- next_recommended_batch: `Inspect R9-R2 import traces and bootstrap_quote source; no service start, no paper/live.`
