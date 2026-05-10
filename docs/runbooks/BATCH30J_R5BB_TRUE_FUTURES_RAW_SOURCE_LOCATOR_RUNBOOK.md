# Batch 30J-R5BB Runbook

Purpose:
Locate real `2026-04-18` futures rows because R5BA-R2 proved `fut_ticks.jsonl` is hard-required before staging replay execution.

Proof:
`run/proofs/proof_batch30j_r5bb_true_futures_raw_source_locator_latest.json`

True futures sources:
`run/audits/batch30j_r5bb_true_futures_raw_source_locator_20260510_120513/ranked_true_future_sources.json`

Option-context-only sources:
`run/audits/batch30j_r5bb_true_futures_raw_source_locator_20260510_120513/option_context_only_sources_sample.json`

Candidate staging plan:
`run/audits/batch30j_r5bb_true_futures_raw_source_locator_20260510_120513/candidate_staging_plan_no_write.json`

Next:
Do not execute replay. Either collect real futures ticks or write explicit option-only compatibility proof as separate no-execution audit.
