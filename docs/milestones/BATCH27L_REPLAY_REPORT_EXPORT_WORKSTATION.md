# Batch 27L — Replay Report / Export Workstation

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_REPORT_EXPORT_WORKSTATION
```

## Scope

Batch 27L creates replay-only CSV/JSON report/export workstation surfaces under run/replay/<run_id>/exports/.

It does not send orders.
It does not arm execution.
It does not approve paper/live.
It does not prove full report semantic accuracy.
It does not prove full live replay parity.

## Safety result

```text
paper_armed: NOT APPROVED
live trading: NOT APPROVED
execution arming: NOT CREATED
real order sent: NO
broker APIs executed: NO
live Redis writes executed: NO
services started: NO
production doctrine changed: NO
export root: run/replay/<run_id>/exports/
```

## Files created / refreshed

```text
app/mme_scalpx/replay/report_exporter.py
etc/replay/schemas/replay_report_export_contract_v1.json
etc/replay/forensics/replay_report_export_manifest_v1.json
bin/replay_export_reports.py
bin/proof_replay_report_exports.py
bin/proof_replay_baseline_shadow_comparison.py
```

## Files patched additively

```text
app/mme_scalpx/replay/contracts.py
app/mme_scalpx/replay/reports.py
app/mme_scalpx/replay/comparison_artifacts.py
bin/replay_run.py
```

## Replay exports proven

```text
00_export_manifest.json
01_trade_log.csv
01_trade_log.json
02_candidate_log.csv
02_candidate_log.json
03_blocker_chain.csv
03_blocker_chain.json
04_side_split_summary.csv
04_side_split_summary.json
05_family_split_summary.csv
05_family_split_summary.json
06_scenario_summary.csv
06_scenario_summary.json
07_pnl_execution_shadow_summary.csv
07_pnl_execution_shadow_summary.json
08_baseline_vs_shadow_comparison.json
09_export_reproducibility.json
```

## Proof artifacts

```text
run/proofs/proof_replay_report_exports.json
run/proofs/proof_replay_baseline_shadow_comparison.json
run/proofs/proof_replay_report_export_workstation.json
run/proofs/proof_replay_report_export_workstation_latest.json
run/proofs/proof_replay_no_broker_call.json
run/proofs/proof_replay_no_live_redis_write.json
run/proofs/proof_replay_no_runtime_promotion.json
run/proofs/proof_replay_batch_runner.json
run/proofs/proof_replay_artifact_materialization.json
```

## Confirmed pass condition

```text
report_export_workstation_ok = true
report_exports_ok = true
baseline_shadow_comparison_ok = true
required_exports_ok = true
trade_log_ok = true
candidate_log_ok = true
blocker_chain_ok = true
side_split_ok = true
family_split_ok = true
scenario_summary_ok = true
pnl_summary_ok = true
comparison_ok = true
reproducibility_ok = true
replay_safety_firewall_ok = true
broker_call_reachable = false
live_redis_write_reachable = false
runtime_promotion_reachable = false
paper_armed_approved = false
live_trading_approved = false
real_order_sent = false
production_doctrine_changed = false
```

## Explicit not-proven boundary

```text
report_export_shape = PROVEN_BY_27L
baseline_shadow_comparison_shape = PROVEN_BY_27L
export_reproducibility_hash = PROVEN_BY_27L
full_report_semantic_accuracy = NOT_PROVEN_IN_27L
full_live_replay_parity = NOT_PROVEN_IN_27L
```

## Meaning

Replay now has a safe report/export workstation surface for CSV/JSON analysis.

This is still not a complete final replay workstation because differential/parameter-sweep/baseline-shadow experiment orchestration and full replay/live parity are not yet proven.

## Next batch

```text
Batch 27M — Replay differential / parameter-sweep experiment workstation
```

27M should add experiment profiles for baseline-vs-shadow, parameter sweep, threshold sweep, family enable/disable, side-only, and replay comparison reports.
