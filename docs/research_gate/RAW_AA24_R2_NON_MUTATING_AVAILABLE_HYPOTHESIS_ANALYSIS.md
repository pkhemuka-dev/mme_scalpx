# RAW-AA24-R2 — Non-Mutating Available Hypothesis Analysis

generated_at_utc: 2026-05-02T07:41:00.631689+00:00

## Verdict

Allowed hypotheses were descriptively analyzed using available fields only.

## Coverage

- rows: `55677`
- recognized_family_rows: `29109`
- recognized_pct: `52.2819`
- unknown_rows: `26568`
- unknown_pct: `47.7181`

## Findings

- RAW-HYP-001: recognized-family coverage is measurable; UNKNOWN remains material.
- RAW-HYP-002: family-side distribution is measurable.
- RAW-HYP-003: doctrine economics ticks are descriptively rankable.
- RAW-HYP-004: observed net_pnl_after_costs is observed-only.
- RAW-HYP-005: selected_leg partial coverage is diagnostic only.
- RAW-HYP-006: gated-lane hypothesis remains blocked pending manual authority.

## Safety

- No row mutation.
- No reward_cost_ratio derivation.
- No OI wall derivation.
- No PnL reconstruction.
- Observed PnL remains observed-only.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Outputs

- analysis_json: `run/research_gate/raw_aa24_r2_non_mutating_available_hypothesis_analysis_20260502_131100/raw_aa24_r2_non_mutating_available_hypothesis_analysis.json`
- findings_csv: `run/research_gate/raw_aa24_r2_non_mutating_available_hypothesis_analysis_20260502_131100/raw_aa24_r2_hypothesis_findings.csv`
- coverage_csv: `run/research_gate/raw_aa24_r2_non_mutating_available_hypothesis_analysis_20260502_131100/raw_aa24_r2_family_coverage_findings.csv`
- economics_csv: `run/research_gate/raw_aa24_r2_non_mutating_available_hypothesis_analysis_20260502_131100/raw_aa24_r2_economics_consistency_findings.csv`
- observed_pnl_csv: `run/research_gate/raw_aa24_r2_non_mutating_available_hypothesis_analysis_20260502_131100/raw_aa24_r2_observed_only_pnl_findings.csv`
- safety_json: `run/research_gate/raw_aa24_r2_non_mutating_available_hypothesis_analysis_20260502_131100/raw_aa24_r2_analysis_safety_register.json`
