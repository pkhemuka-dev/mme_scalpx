# RAW-AA13B-R3 True Row Artifact Resolver

created_at_utc: 2026-05-02T05:46:36.750437+00:00
verdict: `RAW_AA13B_R3_TRUE_ROW_ARTIFACT_RESOLVER_DEFERRED`
blockers: `['NO_TRUE_ROW_LEVEL_FAMILY_DATASET_FOUND']`
next_recommendation: `RAW_AA13B_R4_EXPLICIT_AA11_AA12_OUTPUT_EXPORT_REQUIRED`

## Previous R2 correction

- previous_r2_invalid_for_aa14: `True`
- reasons: `['previous_selected_tiny_matrix_not_row_level_dataset', 'previous_recognized_family_rows_too_small', 'previous_zero_true_ready_rows']`

## Selected input

- selected_input_csv: `None`
- derived_output_csv: `None`

## Safety

- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Outputs

- proof: `run/proofs/proof_raw_aa13b_r3_true_row_artifact_resolver.json`
- freeze: `run/proofs/proof_raw_aa13b_r3_freeze_final.json`
- doc: `docs/research_gate/RAW_AA13B_R3_TRUE_ROW_ARTIFACT_RESOLVER.md`
- milestone: `docs/milestones/batch_raw_aa13b_r3_true_row_artifact_resolver_20260502_111636.md`
- run_dir: `run/research_gate/raw_aa13b_r3_true_row_artifact_resolver_20260502_111636`
- resolver_tool: `bin/raw_aa13b_r3_true_row_artifact_resolver.py`
- derived_output_csv: `None`
