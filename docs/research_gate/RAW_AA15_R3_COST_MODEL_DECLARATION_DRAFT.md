# RAW-AA15-R3 — Cost Model Declaration Draft

generated_at_utc: 2026-05-02T07:20:26.773775+00:00

## Verdict

Cost model is **not authorized** in this batch.

RAW-AA15-R3 creates only:

- required cost-model declaration surface
- blank declaration template
- AA15-R2 candidate review pack
- reward_cost_ratio field status

## Hard rules

- No reward_cost_ratio derivation.
- No row mutation.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No order sending.
- No paper/live enablement.

## Required next input

A completed and explicitly authorized cost model declaration must be provided before RAW can derive cost ticks or reward_cost_ratio.

## Outputs

- required contract: `etc/research_gate/raw_cost_model_required_surface_contract.json`
- declaration template: `etc/research_gate/raw_cost_model_declaration_template.json`
- candidate review: `run/research_gate/raw_aa15_r3_cost_model_declaration_draft_20260502_125026/raw_aa15_r3_cost_model_candidate_review.json`
- field status: `run/research_gate/raw_aa15_r3_cost_model_declaration_draft_20260502_125026/raw_aa15_r3_reward_cost_ratio_field_status.json`