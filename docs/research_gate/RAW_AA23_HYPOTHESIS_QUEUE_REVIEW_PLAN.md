# RAW-AA23 — Hypothesis Queue Review & Non-Mutating Analysis Plan

generated_at_utc: 2026-05-02T07:38:00.355710+00:00

## Verdict

Hypothesis queue reviewed. No hypothesis was tested in this batch.

## Summary

- hypothesis_count: `6`
- allowed_without_gated_count: `5`
- blocked_or_manual_authority_count: `1`

## Allowed next analysis

- RAW-AA24 may run only non-mutating descriptive analysis for allowed hypotheses.

## Safety

- No hypothesis testing in RAW-AA23.
- No row mutation.
- No reward_cost_ratio derivation.
- No OI wall derivation.
- No PnL reconstruction.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Outputs

- review_json: `run/research_gate/raw_aa23_hypothesis_queue_review_plan_20260502_130800/raw_aa23_hypothesis_queue_review.json`
- analysis_plan_json: `run/research_gate/raw_aa23_hypothesis_queue_review_plan_20260502_130800/raw_aa23_non_mutating_analysis_plan.json`
- analysis_plan_csv: `run/research_gate/raw_aa23_hypothesis_queue_review_plan_20260502_130800/raw_aa23_non_mutating_analysis_plan.csv`
- safety_policy: `etc/research_gate/raw_aa23_hypothesis_analysis_safety_policy.json`
