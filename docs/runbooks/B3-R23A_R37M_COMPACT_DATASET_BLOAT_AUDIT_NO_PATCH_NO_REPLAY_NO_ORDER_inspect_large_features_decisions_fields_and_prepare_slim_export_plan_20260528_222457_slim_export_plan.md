# B3-R23A_R37M_COMPACT_DATASET_BLOAT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER slim export plan

## Next batch

`B3-R23B_R37M_SLIM_REPLAY_DATASET_EXPORT_NO_PATCH_NO_REPLAY_NO_ORDER`

## Design

Use the same R37M recorder and R23 window. Create a slim dataset that:

1. Keeps `fut_ticks.jsonl` and `opt_ticks.jsonl` scalar market fields.
2. For `features.jsonl` and `decisions.jsonl`, keeps only replay-critical scalar allowlist fields.
3. Drops or sidecars oversized fields:
   - family_features_json
   - family_surfaces_json
   - consumer_view_json
   - payload_json
   - snapshot_json
   - debug_json/debug/trace
4. Adds `slim_manifest.json` with:
   - original R23 dataset path
   - kept fields
   - dropped fields
   - source row counts
   - output row counts
   - file sizes before/after
5. Does not delete R23 dataset.

## Safety

No patch, no replay, no broker, no paper/live, no risk/execution.
