# Batch 30J-R4A — Selector Available-Dates Audit

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: SELECTOR_AVAILABLE_DATE_NOT_PROVEN

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Requested day rejected by selector: 2026-05-03

Actual available dates: []

Chosen actual date: None

Confidence: NONE

Repair dir: None

Files changed: []

Blockers: [
  "ACTUAL_AVAILABLE_DATES_FOUND_BLOCKER",
  "ACTUAL_AVAILABLE_DATE_CONFIDENCE_MEDIUM_OR_HIGH_BLOCKER"
]

Review: []

Next: Do not run replay. Run 30J-R4B dataset inventory/selector source deep audit; likely dataset metadata must be rebuilt with selectable dates.

Safety: audit/contract repair only; no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
