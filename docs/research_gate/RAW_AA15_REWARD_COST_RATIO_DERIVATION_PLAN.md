# RAW-AA15 Reward/Cost Ratio Derivation Plan

created_at_utc: 2026-05-02T06:00:26.102303+00:00
verdict: `RAW_AA15_REWARD_COST_RATIO_DERIVATION_PLAN_DEFERRED`
blockers: `['COSTS_FIELD_EMPTY', 'NO_ROWS_HAVE_REWARD_TICKS_AND_COSTS', 'AA14_PNL_NOT_RECONSTRUCTABLE_FROM_ENTRY_EXIT_QTY_COSTS']`
next_recommendation: `RAW_AA15_R2_COST_MODEL_DECLARATION_OR_COST_FIELD_BACKFILL_REQUIRED`

## Source

- AA13B derived output: `run/research_gate/raw_aa13b_r4_explicit_output_export_resolver_20260502_111828/enriched_replay_records_aa13b_r4_input_normalized_economics_derived.csv`

## Resolution

```json
{
  "allowed_now": "plan_only_no_row_mutation",
  "reward_cost_ratio_blocker_basis": "costs field and explicit transaction cost model are unavailable",
  "reward_cost_ratio_derivable_now": false,
  "reward_cost_ratio_formula_status": "unproven",
  "reward_ticks_available": true,
  "risk_reward_ratio_preview_formula": "reward_ticks / stop_ticks",
  "risk_reward_ratio_preview_possible": true,
  "risk_reward_ratio_preview_value_expected": "1.25 when reward_ticks=100 and stop_ticks=80",
  "stop_ticks_available": true
}
```

## Key counts

- rows: `55677`
- recognized_family_rows: `29109`
- reward_ticks_non_null: `29109`
- stop_ticks_non_null: `29109`
- risk_reward_ratio_candidate_rows: `29109`
- costs_non_null: `0`
- cost_model_candidate_rows: `0`
- reward_cost_ratio_existing_non_null: `0`

## Important distinction

`reward_ticks / stop_ticks` is only a risk/reward preview. It is not written into `reward_cost_ratio`.
`reward_cost_ratio` remains unavailable until an explicit cost model or cost field is proven.

## Safety

- no row mutation
- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Outputs

- proof: `run/proofs/proof_raw_aa15_reward_cost_ratio_derivation_plan.json`
- freeze: `run/proofs/proof_raw_aa15_freeze_final.json`
- doc: `docs/research_gate/RAW_AA15_REWARD_COST_RATIO_DERIVATION_PLAN.md`
- milestone: `docs/milestones/batch_raw_aa15_reward_cost_ratio_derivation_plan_20260502_113026.md`
- run_dir: `run/research_gate/raw_aa15_reward_cost_ratio_derivation_plan_20260502_113026`
