# RAW-AA25 — Available Analysis Review / Declaration Input Gate

generated_at_utc: 2026-05-02T07:42:32.308737+00:00

## Verdict

RAW-AA24-R2 available-field analysis has been reviewed as research-only and not promotable.

## Coverage

- rows: `55677`
- recognized_family_rows: `29109`
- recognized_pct: `52.2819`
- unknown_rows: `26568`
- unknown_pct: `47.7181`
- finding_count: `6`
- descriptive_finding_count: `5`
- manual_authority_blocked_count: `1`

## Decision

Allowed next now:

- RAW-AA26 final research bundle / continuation prompt.

Blocked until authorized declaration input:

- reward_cost_ratio / cost-adjusted economics
- OI wall strength/distance
- reconstructed PnL lifecycle

## Safety

- No row mutation.
- No reward_cost_ratio derivation.
- No OI wall derivation.
- No PnL reconstruction.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Outputs

- review_json: `run/research_gate/raw_aa25_available_analysis_review_gate_20260502_131232/raw_aa25_available_analysis_review.json`
- decision_json: `run/research_gate/raw_aa25_available_analysis_review_gate_20260502_131232/raw_aa25_declaration_input_gate_decision.json`
- policy: `etc/research_gate/raw_aa25_research_gate_declaration_input_policy.json`
