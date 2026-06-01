# B3-R24F_NORMALIZE_SEQUENCE_ID_AFTER_EVENT_TIME_SORT_NO_REPLAY_NO_ORDER

Classification: `PASS_R24F_SEQUENCE_ID_NORMALIZATION_PATCH_APPLIED_NO_REPLAY_NO_ORDER`  
Created: `2026-05-28T23:11:59.797124+05:30`

## Patch

- Target: `bin/replay_run.py`
- Backup: `run/_code_backups/B3-R24F_NORMALIZE_SEQUENCE_ID_AFTER_EVENT_TIME_SORT_NO_REPLAY_NO_ORDER_extend_replay_run_sort_helper_to_reassign_sequence_id_after_event_time_sort_20260528_231159_bin_replay_run.py.bak`
- Diff: `run/audits/B3-R24F_NORMALIZE_SEQUENCE_ID_AFTER_EVENT_TIME_SORT_NO_REPLAY_NO_ORDER_extend_replay_run_sort_helper_to_reassign_sequence_id_after_event_time_sort_20260528_231159_patch.diff`
- Changed: `True`
- Compile OK: `True`
- AST OK: `True`
- Markers: `{'r24c_helper': True, 'r24c_call_marker': True, 'r24f_sequence_marker': True, 'injector_validation_not_modified': True}`

## Safety

Offline replay patch only. No replay. No service start/kill. No Redis delete. No broker. No paper/live. No risk/execution.

## Rule preserved

Injector validation was not weakened. Sequence IDs are normalized before injector validation.

## Next

Run B3-R24G replay retry against the same R23B slim dataset.
