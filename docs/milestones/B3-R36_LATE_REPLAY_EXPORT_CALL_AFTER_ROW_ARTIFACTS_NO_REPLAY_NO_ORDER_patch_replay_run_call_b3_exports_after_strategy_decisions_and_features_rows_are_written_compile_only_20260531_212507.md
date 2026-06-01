# B3-R36_LATE_REPLAY_EXPORT_CALL_AFTER_ROW_ARTIFACTS_NO_REPLAY_NO_ORDER

Classification: `BLOCKED_R36_PATCH_VALIDATION_FAILED_REVIEW_BACKUP`  
Created: `2026-05-31T21:25:07.628075+05:30`

## Patch

- Target: `bin/replay_run.py`
- Backup: `run/_code_backups/B3-R36_LATE_REPLAY_EXPORT_CALL_AFTER_ROW_ARTIFACTS_NO_REPLAY_NO_ORDER_patch_replay_run_call_b3_exports_after_strategy_decisions_and_features_rows_are_written_compile_only_20260531_212507_replay_run.py.bak`
- Diff: `run/audits/B3-R36_LATE_REPLAY_EXPORT_CALL_AFTER_ROW_ARTIFACTS_NO_REPLAY_NO_ORDER_patch_replay_run_call_b3_exports_after_strategy_decisions_and_features_rows_are_written_compile_only_20260531_212507_patch.diff`
- Changed: `True`
- Insertion line: `2998`
- Compile OK: `False`
- AST OK: `False`

## Safety

One-file `bin/replay_run.py` patch only. No Redis. No replay. No service action. No broker/order/paper/live/risk/execution.

## Next

Rerun B3-R35 smoke.
