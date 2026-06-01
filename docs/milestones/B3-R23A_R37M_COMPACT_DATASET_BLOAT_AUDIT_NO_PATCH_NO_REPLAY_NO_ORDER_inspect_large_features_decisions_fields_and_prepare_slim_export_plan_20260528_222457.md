# B3-R23A_R37M_COMPACT_DATASET_BLOAT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R23A_BLOAT_AUDIT_READY_FOR_SLIM_EXPORT_PLAN`  
Bloat classification: `BLOAT_FROM_LARGE_NESTED_JSON_FIELDS`  
Created: `2026-05-28T22:24:59.983749+05:30`

## Source

- R23 dataset root: `run/replay/staging/B3-R23_R37M_COMPACT_REPLAY_DATASET_EXPORT_NO_PATCH_NO_REPLAY_NO_ORDER_export_time_aligned_compact_dataset_from_r37m_recorder_for_next_replay_20260528_220545`
- Day dir: `run/replay/staging/B3-R23_R37M_COMPACT_REPLAY_DATASET_EXPORT_NO_PATCH_NO_REPLAY_NO_ORDER_export_time_aligned_compact_dataset_from_r37m_recorder_for_next_replay_20260528_220545/2026-05-27`
- R23 counts: `{'decisions': 1844, 'features': 397, 'fut_ticks': 650, 'opt_ticks': 2996}`

## File sizes

- fut_ticks: `270005`
- opt_ticks: `1291824`
- features: `1445257472`
- decisions: `6488143412`

## Likely bloat fields

`['consumer_view_json', 'consumer_view_json.branch_frames', 'consumer_view_json.family_frames', 'consumer_view_json.family_surfaces', 'family_surfaces_json', 'family_surfaces_json.families', 'family_surfaces_json.surfaces_by_branch', 'payload_json', 'payload_json.consumer_view_json']`

## Safety

Read-only. No slim export yet. No replay. No patch. No delete. No broker. No paper/live. No risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R23A_R37M_COMPACT_DATASET_BLOAT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_large_features_decisions_fields_and_prepare_slim_export_plan_20260528_222457.json`
- Latest proof: `run/proofs/B3_R23A_latest.json`
- Audit: `run/audits/B3-R23A_R37M_COMPACT_DATASET_BLOAT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_large_features_decisions_fields_and_prepare_slim_export_plan_20260528_222457_audit.json`
