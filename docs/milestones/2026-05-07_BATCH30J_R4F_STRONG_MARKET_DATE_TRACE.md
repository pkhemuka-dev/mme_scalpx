# Batch 30J-R4F — Strong Market Date Source Trace

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: STRONG_MARKET_DATE_TRACE_BLOCKED

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Dates traced: [
  "2026-04-29",
  "2026-04-30"
]

Confirmed market-reference dates: [
  "2026-04-29"
]

Inventory-only market-like dates: []

Trace classifications: {
  "UNCONFIRMED_INVENTORY_EVIDENCE": 15,
  "TRACE_CONFIRMED_TO_MARKET_REFERENCE_FILE": 1
}

Repair files: []

Blockers: [
  "ALL_RUNTIME_LOCKS_ABSENT_BLOCKER",
  "RISK_EXECUTION_ABSENT_BLOCKER"
]

Review: [
  "FEEDS_RUNNING_DURING_STRONG_MARKET_DATE_TRACE",
  "FEATURES_OR_STRATEGY_RUNNING_DURING_STRONG_MARKET_DATE_TRACE"
]

Next: Do not install metadata or run replay. Resolve 30J-R4F blockers first.

Safety: trace only; no selector metadata install, no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
