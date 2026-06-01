# B3-R24C_MERGED_EVENT_TIME_SORT_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R24C_MERGED_EVENT_TIME_SORT_PATCH_APPLIED_NO_REPLAY_NO_ORDER`  
Created: `2026-05-28T23:05:28.700337+05:30`

## Patch

- Target: `bin/replay_run.py`
- Backup: `run/_code_backups/B3-R24C_MERGED_EVENT_TIME_SORT_PATCH_NO_REPLAY_NO_ORDER_patch_replay_run_stage_executor_sort_events_before_injector_validation_20260528_230528_bin_replay_run.py.bak`
- Diff: `run/audits/B3-R24C_MERGED_EVENT_TIME_SORT_PATCH_NO_REPLAY_NO_ORDER_patch_replay_run_stage_executor_sort_events_before_injector_validation_20260528_230528_patch.diff`
- Changed: `True`
- Compile OK: `True`
- AST OK: `True`
- Markers: `{'helper_marker': True, 'call_marker': True, 'injector_validation_not_modified': True}`

## Safety

Offline replay patch only. No replay. No service start/kill. No Redis delete. No broker. No paper/live. No risk/execution.

## Rule preserved

Injector validation was not weakened. Patch sorts the assembled event batch before `injector.inject_batch`.

## Next

Run B3-R24D replay retry against the same R23B slim dataset.
