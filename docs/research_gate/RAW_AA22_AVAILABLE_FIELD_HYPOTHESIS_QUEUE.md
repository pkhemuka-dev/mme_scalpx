# RAW-AA22 — Available Field Hypothesis Queue

generated_at_utc: 2026-05-02T07:36:21.234581+00:00

## Verdict

Hypothesis queue generated from available RAW fields only.

## Scope

- Queue-only.
- Not tested.
- Not promoted.
- No row mutation.
- No gated-field derivation.

## Hypotheses

### RAW-HYP-001 — Recognized-family coverage is sufficient for descriptive family distribution analysis, but UNKNOWN remains material.

- priority: `HIGH`
- allowed_test: Compare descriptive counts across recognized families only; report UNKNOWN separately.
- forbidden_inference: Do not treat UNKNOWN rows as strategy failure or strategy opportunity without source authority.

### RAW-HYP-002 — Family-side distribution may reveal imbalance or dominance in available RAW evidence.

- priority: `MEDIUM`
- allowed_test: Rank family/side row counts and inspect whether concentration is expected from doctrine or source construction.
- forbidden_inference: Do not infer profitability, quality, or live readiness from row-count dominance.

### RAW-HYP-003 — Doctrine economics ticks appear analyzable as descriptive evidence across recognized families.

- priority: `HIGH`
- allowed_test: Check whether target/stop/reward tick sets match expected doctrine authority per family.
- forbidden_inference: Do not derive reward_cost_ratio or cost-adjusted expectancy.

### RAW-HYP-004 — Observed net_pnl_after_costs can be reviewed as observed-only signal, not reconstructed lifecycle truth.

- priority: `MEDIUM`
- allowed_test: Review observed-only net_pnl_after_costs by family/side with explicit caveat that lifecycle fields are unavailable.
- forbidden_inference: Do not reconstruct PnL, costs, fills, entry/exit, or trade quality from observed-only PnL.

### RAW-HYP-005 — Selected-leg partial coverage should be treated as diagnostic coverage, not full lifecycle authority.

- priority: `MEDIUM`
- allowed_test: Quantify selected_leg presence and identify which families/sides have partial selected-leg support.
- forbidden_inference: Do not use selected_leg partial coverage to reconstruct entry/exit or assume executable tradability.

### RAW-HYP-006 — Gated lanes define the next evidence requirements before any advanced economics analysis.

- priority: `HIGH`
- allowed_test: Prepare separate manual declaration review tasks if the user wants to unlock those lanes.
- forbidden_inference: Do not unblock, derive, backfill, or promote gated fields from available-field reports.

## Safety

- No reward_cost_ratio derivation.
- No OI wall derivation.
- No PnL reconstruction.
- No row mutation.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Outputs

- queue_json: `run/research_gate/raw_aa22_available_field_hypothesis_queue_20260502_130621/raw_aa22_available_field_hypothesis_queue.json`
- queue_csv: `run/research_gate/raw_aa22_available_field_hypothesis_queue_20260502_130621/raw_aa22_available_field_hypothesis_queue.csv`
- risk_register: `run/research_gate/raw_aa22_available_field_hypothesis_queue_20260502_130621/raw_aa22_hypothesis_safety_risk_register.json`
