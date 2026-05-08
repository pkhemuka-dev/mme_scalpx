# Batch 30G-R2 — Freeze Refined Dataset Candidate Contract

Verdict: PASS_GREEN_CONTINUE

Health: GREEN_CONTINUE

Classification: REFINED_DATASET_CONTRACT_FROZEN_READY_FOR_30H

Dataset path: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Contract dir: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/refined_dataset_candidate_contract_30g_r2

Files changed: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/refined_dataset_candidate_contract_30g_r2/00_refined_dataset_candidate_contract.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/refined_dataset_candidate_contract_30g_r2/01_refined_dataset_validation_summary.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/refined_dataset_candidate_contract_30g_r2/02_next_replay_dry_run_plan_contract.json"
]

Blockers: []

Review: []

Next: Batch 30H — replay dry-run plan/adapter compatibility audit, offline only; no replay execution yet.

Safety: artifact-only; no production code patch, no replay execution, no materialization, no Redis write/delete, no service start/stop, no paper/live, no orders.
