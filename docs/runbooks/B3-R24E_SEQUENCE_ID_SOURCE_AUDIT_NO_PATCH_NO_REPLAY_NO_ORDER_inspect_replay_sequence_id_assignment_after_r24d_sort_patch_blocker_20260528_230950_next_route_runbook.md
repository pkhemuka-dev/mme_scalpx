# B3-R24E_SEQUENCE_ID_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

Recommended next batch:

`B3-R24F_NORMALIZE_SEQUENCE_ID_AFTER_EVENT_TIME_SORT_NO_REPLAY_NO_ORDER`

Patch law:

1. Do not weaken injector validation.
2. Keep event_time global sort.
3. After sorting, rewrite/reassign `sequence_id` as 1..N in sorted order.
4. Patch only `bin/replay_run.py`.
5. Compile/AST proof only.
6. Then rerun replay as B3-R24G.
