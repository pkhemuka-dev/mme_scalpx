# RAW-AA13B Economics Derivation Implementation

created_at_utc: 2026-05-02T05:42:29.813559+00:00
verdict: `RAW_AA13B_ECONOMICS_DERIVATION_READY`
blockers: `[]`
next_recommendation: `RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER`

## Safety

- RAW-only derivation tool
- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Selected input

- selected_input_csv: `run/research_gate/raw_aa5_existing_evidence_scaleup_discovery_20260501_180713/ranked_existing_evidence_datasets.csv`
- derived_output_csv: `run/research_gate/raw_aa13b_economics_derivation_implementation_20260502_111229/ranked_existing_evidence_datasets_aa13b_economics_derived.csv`

## Field resolution

- `target_ticks`: derived_from_authority_map
- `stop_ticks`: derived_from_authority_map
- `reward_ticks`: derived_from_authority_map_first_target_raw_economics_only
- `reward_cost_ratio`: left_empty_unavailable_until_cost_model
- `entry_mode`: preserved_from_source_if_present_otherwise_blocker_reason
- `selected_leg`: preserved_from_source_if_present_otherwise_blocker_reason
- `side`: preserved_from_source_if_present_otherwise_blocker_reason
- `oi_wall_strength`: not_derived
- `oi_wall_distance_points`: not_derived

## Outputs

- proof: `run/proofs/proof_raw_aa13b_economics_derivation_implementation.json`
- freeze: `run/proofs/proof_raw_aa13b_freeze_final.json`
- doc: `docs/research_gate/RAW_AA13B_ECONOMICS_DERIVATION_IMPLEMENTATION.md`
- milestone: `docs/milestones/batch_raw_aa13b_economics_derivation_implementation_20260502_111229.md`
- run_dir: `run/research_gate/raw_aa13b_economics_derivation_implementation_20260502_111229`
- tool: `bin/raw_aa13b_economics_derivation.py`
- derived_output_csv: `run/research_gate/raw_aa13b_economics_derivation_implementation_20260502_111229/ranked_existing_evidence_datasets_aa13b_economics_derived.csv`
