# RAW-AA13B-R2 Input Artifact Resolver

created_at_utc: 2026-05-02T05:44:27.032495+00:00
verdict: `RAW_AA13B_R2_INPUT_ARTIFACT_RESOLVER_READY`
blockers: `[]`
next_recommendation: `RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER`

## Previous AA13B correction

- previous_invalid_for_promotion: `True`
- reasons: `['previous_selected_discovery_manifest_not_row_level_trade_dataset', 'previous_no_recognized_family_rows', 'previous_all_rows_false_ready']`

## Selected input

- selected_input_csv: `run/research_gate/raw_g_oi_wall_impact_20260501_130854/oi_wall_context_matrix.csv`
- derived_output_csv: `run/research_gate/raw_aa13b_r2_input_artifact_resolver_20260502_111427/oi_wall_context_matrix_aa13b_r2_economics_derived.csv`

## Safety

- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Outputs

- proof: `run/proofs/proof_raw_aa13b_r2_input_artifact_resolver.json`
- freeze: `run/proofs/proof_raw_aa13b_r2_freeze_final.json`
- doc: `docs/research_gate/RAW_AA13B_R2_INPUT_ARTIFACT_RESOLVER.md`
- milestone: `docs/milestones/batch_raw_aa13b_r2_input_artifact_resolver_20260502_111427.md`
- run_dir: `run/research_gate/raw_aa13b_r2_input_artifact_resolver_20260502_111427`
- resolver_tool: `bin/raw_aa13b_r2_input_artifact_resolver.py`
- derived_output_csv: `run/research_gate/raw_aa13b_r2_input_artifact_resolver_20260502_111427/oi_wall_context_matrix_aa13b_r2_economics_derived.csv`
