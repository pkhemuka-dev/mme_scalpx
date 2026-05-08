# RAW-AA15-R2 Cost Model Authority Resolver

created_at_utc: 2026-05-02T06:03:39.926868+00:00
verdict: `RAW_AA15_R2_COST_MODEL_AUTHORITY_RESOLVER_DEFERRED`
blockers: `['EXPLICIT_COST_MODEL_CANDIDATE_REQUIRES_MANUAL_REVIEW']`
next_recommendation: `RAW_AA15_R3_COST_MODEL_DECLARATION_DRAFT_OR_UPLOAD_REQUIRED`

## Result

`reward_cost_ratio` remains unavailable. No row data was mutated.

## Cost model resolution

```json
{
  "cost_model_authority_found": true,
  "reason": "explicit cost model not accepted by AA15-R2 unless it has numeric brokerage/slippage/fee basis and row-level cost mapping",
  "required_next_declaration": {
    "must_state": [
      "whether cost is per round-trip or per leg",
      "whether cost is points, ticks, rupees, or percent",
      "how option lot size and quantity enter the formula",
      "how existing net_pnl_after_costs should be interpreted",
      "whether historical rows can be backfilled without entry/exit/qty"
    ],
    "required_fields": [
      "cost_model_id",
      "cost_model_version",
      "cost_per_trade_or_per_leg",
      "brokerage_basis",
      "fees_taxes_basis",
      "slippage_basis",
      "point_value_or_lot_basis",
      "formula_for_cost_ticks",
      "formula_for_reward_cost_ratio",
      "applicability_scope"
    ]
  },
  "reward_cost_ratio_derivable_now": false,
  "safe_formula_status": "not_authorized"
}
```

## Safety

- no reward_cost_ratio write
- no row mutation
- no replay execution
- no broker IO
- no live Redis writes
- no order sending
- no paper/live enablement

## Outputs

- proof: `run/proofs/proof_raw_aa15_r2_cost_model_authority_resolver.json`
- freeze: `run/proofs/proof_raw_aa15_r2_freeze_final.json`
- doc: `docs/research_gate/RAW_AA15_R2_COST_MODEL_AUTHORITY_RESOLVER.md`
- milestone: `docs/milestones/batch_raw_aa15_r2_cost_model_authority_resolver_20260502_113339.md`
- run_dir: `run/research_gate/raw_aa15_r2_cost_model_authority_resolver_20260502_113339`
