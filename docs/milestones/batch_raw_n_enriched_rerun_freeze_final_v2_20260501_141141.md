# Milestone — Batch RAW-N Enriched Rerun v2

Date: 2026-05-01
Generated UTC: 2026-05-01T08:41:41.396503+00:00
Batch tag: batch_raw_n_enriched_rerun_freeze_final_v2_20260501_141141

Achieved:
- Added RAW-N enriched rerun module and CLI.
- Consumed RAW-M enriched replay records.
- Produced RAW-D through RAW-J style reports in isolated RAW-N run directory.
- Did not overwrite old RAW-D/J proofs.
- Preserved non-live, non-mutating safety posture.

RAW-N verdict:
- dataset_verdict: DATASET_PASS
- data_quality_score: 1.0
- trade_count: 22
- net_pnl_after_costs: 2280.75
- rank_verdict: RANK_INSUFFICIENT_FAMILY_LABELS
- oi_verdict: OI_IMPACT_INSUFFICIENT_OI_EVIDENCE
- forensics_verdict: FORENSICS_CONTEXT_FOUND_NO_OUTCOME_LABELS
- replay_verdict: INCONCLUSIVE_FOR_PROMOTION
- promotion_verdict: PROMOTION_REJECTED_BY_EVIDENCE
- promotion_allowed: False
- paper_live_allowed: False

Next:
Review RAW-N verdict. If still blocked, patch upstream replay producers closer to true family/outcome sources.
