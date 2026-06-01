# B3-R36A_RESTORE_AND_SAFE_LATE_EXPORT_CALL_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R36A_RESTORED_AND_LATE_EXPORT_CALL_PATCHED_COMPILE_OK_NO_REPLAY_NO_ORDER`  
Created: `2026-05-31T21:28:06.516843+05:30`

## Recovery

- Restored from R36 backup: `run/_code_backups/B3-R36_LATE_REPLAY_EXPORT_CALL_AFTER_ROW_ARTIFACTS_NO_REPLAY_NO_ORDER_patch_replay_run_call_b3_exports_after_strategy_decisions_and_features_rows_are_written_compile_only_20260531_212507_replay_run.py.bak`
- Broken file saved to: `run/_code_backups/B3-R36A_RESTORE_AND_SAFE_LATE_EXPORT_CALL_PATCH_NO_REPLAY_NO_ORDER_restore_broken_r36_replay_run_backup_then_insert_late_b3_export_call_after_write_text_closure_compile_only_20260531_212805_broken_replay_run.py.bak`

## Patch

- Target: `bin/replay_run.py`
- Diff: `run/audits/B3-R36A_RESTORE_AND_SAFE_LATE_EXPORT_CALL_PATCH_NO_REPLAY_NO_ORDER_restore_broken_r36_replay_run_backup_then_insert_late_b3_export_call_after_write_text_closure_compile_only_20260531_212805_patch.diff`
- Changed: `True`
- Insertion line: `2999`
- replay_run compile OK: `True`
- replay_run AST OK: `True`
- artifacts.py compile OK: `True`

## Safety

Restore + one-file compile-only patch. No Redis. No replay. No service action. No broker/order/paper/live/risk/execution.

## Next

Rerun B3-R35 smoke test.
