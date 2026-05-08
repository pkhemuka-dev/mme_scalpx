# RAW-AA14 PnL Cost Model Source Resolver

created_at_utc: 2026-05-02T05:58:15.217935+00:00
verdict: `RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER_READY`
blockers: `[]`
next_recommendation: `RAW_AA15_REWARD_COST_RATIO_DERIVATION_PLAN`

## Source

- AA13B-R4 derived output: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized_economics_derived.csv`

## Resolution

```json
{
  "gross_pnl_cost_components": "available",
  "net_pnl_after_costs": "observed_source_available",
  "next_allowed": "source_resolved_only_no_ratio_yet",
  "pnl_reconstruction": "not_reconstructable_from_entry_exit_qty_costs",
  "reward_cost_ratio": "not_derived_in_aa14"
}
```

## Key counts

- rows: `55677`
- recognized_family_rows: `29109`
- pnl_observed_net_rows: `2750`
- pnl_reconstructable_rows: `0`
- cost_component_rows: `2750`
- reward_cost_ratio_present_rows: `0`

## Safety

- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Outputs

- proof: `run/proofs/proof_raw_aa14_pnl_cost_model_source_resolver.json`
- freeze: `run/proofs/proof_raw_aa14_freeze_final.json`
- doc: `docs/research_gate/RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER.md`
- milestone: `docs/milestones/batch_raw_aa14_pnl_cost_model_source_resolver_20260502_112815.md`
- run_dir: `run/research_gate/raw_aa14_pnl_cost_model_source_resolver_20260502_112815`
