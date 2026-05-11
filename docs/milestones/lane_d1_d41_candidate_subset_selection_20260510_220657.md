# LANE D1 D41 — Candidate Subset Selection / Execution Handoff Manifest / No Execution

Created at: 2026-05-10T16:36:57.673240+00:00

## Verdict

PASS — First 5-candidate subset selected and execution handoff manifest created.

## Evidence Chain

- D32 candidate replay binding plan PASS observed.
- D37 Lane C/E handoff PASS observed.
- D39 execution package requirement PASS observed.
- D40 execution package requirement validator PASS observed.

## Output

- Artifact root: `/home/Lenovo/scalpx/projects/mme_scalpx/run/replay_optimization/d41_candidate_subset_selection_probe_20260510_220657`
- Subset rows: `/home/Lenovo/scalpx/projects/mme_scalpx/run/replay_optimization/d41_candidate_subset_selection_probe_20260510_220657/44_candidate_subset_rows.json`
- Handoff manifest: `/home/Lenovo/scalpx/projects/mme_scalpx/run/replay_optimization/d41_candidate_subset_selection_probe_20260510_220657/44_execution_handoff_manifest.json`
- Selected candidates: `['D2_add5825e65636e0b54af', 'D2_14ac3261c713c11d1875', 'D2_01968fce63c622f3cf1d', 'D2_932cf9f09060ced12f30', 'D2_abcf7839fadbf797ec8c']`

## Safety

- Full universe preserved: true / 810 candidates
- First subset count: 5 candidates
- Replay execution performed: false
- Result pack created: false
- Label binding allowed: false
- PnL calculation performed: false
- ML training/prediction performed: false
- Broker calls / live Redis / paper-live enablement: false

## Next

LANE-D1-D42_POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION
