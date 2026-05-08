# Batch 30J-R4H — Non-Mutating Selector Readability Probe

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: STATIC_SELECTOR_COMPATIBLE_DYNAMIC_ACCEPTANCE_NOT_PROVEN

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Static probe: {
  "available_dates_present_in_candidate": true,
  "selector_source_mentions_available_dates": true,
  "selector_source_mentions_single_day": true,
  "selector_source_mentions_unavailable_error": true,
  "static_compatible": true
}

Dynamic accepted: False

Probe files: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/05_non_mutating_selector_readability_probe.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/06_30j_r4i_readiness.json"
]

Blockers: []

Review: [
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_REVIEW",
  "DYNAMIC_SELECTOR_CALLABLE_ACCEPTANCE_NOT_PROVEN_STATIC_ONLY_REVIEW"
]

Next: Batch 30J-R4I — source-specific selector probe/adapter validation, no replay execution.

Safety: no metadata install, no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
