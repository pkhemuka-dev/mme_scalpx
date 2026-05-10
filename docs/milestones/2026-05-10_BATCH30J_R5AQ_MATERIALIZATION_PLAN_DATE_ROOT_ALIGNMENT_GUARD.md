# Batch 30J-R5AQ — Materialization Plan Date-Root Alignment Guard

Verdict: `REVIEW_BASIC_DATE_ALIGNED_CANDIDATE_WITH_OPTIONAL_GAPS`
Classification: `BASIC_MATERIALIZATION_CANDIDATE_ALIGNED_BUT_NOT_STRONG`

Repository dates:
[
  "2026-04-17"
]

Plan count:
`36`

Accepted staging plan count:
`2`

Strict-ready staging count:
`0`

Date mismatch count:
`23`

Invalid date count:
`3`

Best accepted candidate:
{
  "date": "2026-05-08",
  "group_root": "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17",
  "planned_dataset_id": "historic_candidate_20260508",
  "planned_stage_root_no_write": "run/replay/staging/r5ap_plan_only/historic_candidate_20260508",
  "planned_final_repository_root_no_write": "run/replay/2026-05-08",
  "date_valid": true,
  "repo_date_already_present": false,
  "group_root_dates": [
    "2026-04-17",
    "2026-05-08"
  ],
  "planned_stage_dates": [
    "2026-05-08"
  ],
  "planned_final_dates": [
    "2026-05-08"
  ],
  "file_dates": [
    "2026-04-17",
    "2026-05-08"
  ],
  "all_context_dates": [
    "2026-04-17",
    "2026-05-08"
  ],
  "same_date_in_group_root": true,
  "same_date_in_file_paths_or_metadata": true,
  "group_root_has_other_specific_date": false,
  "materializable": true,
  "strong_materializable": false,
  "usable_file_count": 14,
  "rejected_file_count": 2,
  "usable_counts_by_surface": {
    "dhan_context": 0,
    "execution_shadow": 4,
    "family_surfaces": 0,
    "features": 2,
    "feed_snapshot": 0,
    "orders_no_order": 0,
    "provider_runtime": 0,
    "risk": 2,
    "strategy": 2
  },
  "required_presence": {
    "execution_shadow": true,
    "features": true,
    "risk": true,
    "strategy": true
  },
  "optional_presence": {
    "dhan_context": false,
    "family_surfaces": false,
    "feed_snapshot": false,
    "orders_no_order": false,
    "provider_runtime": false
  },
  "required_count": 4,
  "optional_count": 0,
  "accepted_for_staging_plan": true,
  "strict_ready_for_staging_materialization": false,
  "rejection_reasons": [],
  "warnings": [
    "OPTIONAL_PROVIDER_CONTEXT_GAPS",
    "NO_OPTIONAL_PROVIDER_FEED_CONTEXT"
  ],
  "source_paths_sample": [
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate_v2.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate_v2.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/features_rows_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/features_rows_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/risk_outputs_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/risk_outputs_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/strategy_decisions_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/strategy_decisions_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate_v2.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate_v2.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/strategy_decisions_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/strategy_decisions_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/risk_outputs_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/risk_outputs_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/features_rows_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/features_rows_candidate.csv",
    "run/replay/parity/offline_materialization/session_exports_canonical_candidate_2026

No replay execution.
No repository mutation.
No staging materialization.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Inspect accepted candidates; staging-only materialization may proceed only if optional context gaps are accepted.
