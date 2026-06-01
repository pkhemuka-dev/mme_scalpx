# B3-R24A_SLIM_DATASET_EVENT_TIME_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

1. If classification is `BLOCKED_R24A_SOURCE_FILES_HAVE_NON_MONOTONIC_EVENT_TIME`, export a sorted slim dataset without patching code.
2. If classification is `PASS_R24A_FILES_MONOTONIC_BUT_REPLAY_NEEDS_MERGED_TIME_SORT`, inspect replay loader behavior before patching; a merged feed-stage ordering fix may be needed.
3. Continue no broker, no paper/live, no risk/execution.
