# B3-R24A_SLIM_DATASET_EVENT_TIME_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R24A_FILES_MONOTONIC_BUT_REPLAY_NEEDS_MERGED_TIME_SORT`  
Created: `2026-05-28T23:02:34.221283+05:30`

## Dataset

- Dataset root: `run/replay/staging/B3-R23B_R37M_SLIM_REPLAY_DATASET_EXPORT_NO_PATCH_NO_REPLAY_NO_ORDER_create_slim_replay_dataset_from_r23_by_dropping_large_nested_json_fields_20260528_222645`
- Session date: `2026-05-27`
- Day dir: `run/replay/staging/B3-R23B_R37M_SLIM_REPLAY_DATASET_EXPORT_NO_PATCH_NO_REPLAY_NO_ORDER_create_slim_replay_dataset_from_r23_by_dropping_large_nested_json_fields_20260528_222645/2026-05-27`

## Ordering result

- Non-monotonic files: `[]`
- Concat violations: `[{'file': 'opt_ticks', 'line': 1, 'event_time': '2026-05-27T03:53:23.634000Z', 'event_ms': 1779854003634, 'previous_file': 'fut_ticks', 'previous_event_time': '2026-05-27T04:11:30.243000Z', 'previous_event_ms': 1779855090243}, {'file': 'features', 'line': 1, 'event_time': '2026-05-27T03:51:34.786000Z', 'event_ms': 1779853894786, 'previous_file': 'fut_ticks', 'previous_event_time': '2026-05-27T04:11:30.243000Z', 'previous_event_ms': 1779855090243}, {'file': 'decisions', 'line': 1, 'event_time': '2026-05-27T03:52:40.926000Z', 'event_ms': 1779853960926, 'previous_file': 'fut_ticks', 'previous_event_time': '2026-05-27T04:11:30.243000Z', 'previous_event_ms': 1779855090243}]`

## Safety

Read-only. No replay. No patch. No delete. No broker. No paper/live. No risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R24A_SLIM_DATASET_EVENT_TIME_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_find_non_monotonic_event_time_rows_blocking_r24_replay_20260528_230233.json`
- Latest proof: `run/proofs/B3_R24A_latest.json`
- Audit: `run/audits/B3-R24A_SLIM_DATASET_EVENT_TIME_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_find_non_monotonic_event_time_rows_blocking_r24_replay_20260528_230233_audit.json`
