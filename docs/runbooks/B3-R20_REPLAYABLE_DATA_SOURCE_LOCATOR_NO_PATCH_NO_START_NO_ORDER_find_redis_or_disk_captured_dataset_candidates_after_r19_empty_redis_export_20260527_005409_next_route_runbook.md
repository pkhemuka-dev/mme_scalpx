# B3-R20_REPLAYABLE_DATA_SOURCE_LOCATOR_NO_PATCH_NO_START_NO_ORDER next route

1. If `FOUND_STRICT_REPLAY_DATASET_CANDIDATE_ON_DISK`, next B3 step should run replay against that existing disk dataset.
2. If `FOUND_REDIS_STREAM_DATA_BUT_R19_WINDOW_OR_EXTRACTION_MISSED`, next B3 step should export using actual Redis first/last ID range.
3. If `FOUND_RELATED_DISK_ARTIFACTS_BUT_NO_STRICT_DATASET_YET`, next B3 step should rebuild replay dataset from the best live_capture/proof/staging artifact.
4. If `BLOCKED_NO_REPLAYABLE_DATA_SOURCE_FOUND`, next B3 step should prepare tomorrow/live-session capture persistence checks.

Safety remains no broker, no paper/live, no risk/execution.
