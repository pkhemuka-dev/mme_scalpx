# Batch 30J-R4E — Date Provenance Validation

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: MARKET_DATE_PROVEN_OR_PARTIALLY_PROVEN_REQUIRES_OPERATOR_REVIEW

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

R4D candidate dates: [
  "2026-05-01",
  "2026-05-02",
  "2026-04-30",
  "2026-05-03",
  "2026-04-16"
]

Provenance verdict: MARKET_DATE_PROVEN_OR_PARTIALLY_PROVEN

Evidence counts: {
  "WEAK_ARTIFACT_METADATA_DATE": 80
}

Repair files: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/date_provenance_validation_30j_r4e/00_market_date_provenance_validation.json"
]

Blockers: []

Review: []

Next: Review 30J-R4E market-date evidence before selector metadata validation.

Safety: provenance validation only; no selector metadata install, no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
