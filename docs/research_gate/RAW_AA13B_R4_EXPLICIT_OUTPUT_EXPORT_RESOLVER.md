# RAW-AA13B-R4 Explicit Output Export Resolver

created_at_utc: 2026-05-02T05:48:28.605541+00:00
verdict: `RAW_AA13B_R4_EXPLICIT_OUTPUT_EXPORT_READY`
blockers: `[]`
next_recommendation: `RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER`

## Previous R3 correction

- previous_r3_invalid_for_aa14: `True`
- reasons: `['previous_r3_not_ready', 'previous_r3_no_eligible_true_row_dataset', 'previous_r3_no_derived_output_csv']`

## Selected artifact

- selected_source_artifact: `run/replay/raw_x_repair_source_row_lineage_20260501_154627_post_fix_export/enriched_replay_records.jsonl`
- normalized_input_csv: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized.csv`
- derived_output_csv: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized_economics_derived.csv`

## Missing export requirements if deferred

```json
{
  "acceptable_extensions": [
    ".csv",
    ".jsonl",
    ".ndjson",
    ".parquet"
  ],
  "must_not_be": [
    "ranked_existing_evidence_datasets",
    "source_artifact_breakdown",
    "family_side_matrix",
    "blocker_matrix",
    "oi_wall_context_matrix",
    "oi_wall_source_breakdown",
    "unknown_trade_source_gap_map",
    "unknown_trade_lineage_map",
    "candidate_profiles",
    "resolver_hits",
    "scorecard",
    "summary"
  ],
  "preferred_rows": "47919 enriched/backfilled rows or 2420 trade rows",
  "required_family_column_or_aliases": [
    "trade_family",
    "trade_family_after",
    "family",
    "family_after",
    "strategy_family",
    "strategy_id",
    "candidate_family",
    "rank_candidate_family"
  ],
  "required_family_diversity_min": 3,
  "required_family_rows_min": 500,
  "required_fields_for_full_ready_rows": [
    "side",
    "selected_leg",
    "entry_mode"
  ],
  "required_min_rows": 2400
}
```

## Safety

- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Outputs

- proof: `run/proofs/proof_raw_aa13b_r4_explicit_output_export_resolver.json`
- freeze: `run/proofs/proof_raw_aa13b_r4_freeze_final.json`
- doc: `docs/research_gate/RAW_AA13B_R4_EXPLICIT_OUTPUT_EXPORT_RESOLVER.md`
- milestone: `docs/milestones/batch_raw_aa13b_r4_explicit_output_export_resolver_20260502_111828.md`
- run_dir: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828`
- resolver_tool: `bin/raw_aa13b_r4_explicit_output_export_resolver.py`
- normalized_input_csv: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized.csv`
- derived_output_csv: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized_economics_derived.csv`
