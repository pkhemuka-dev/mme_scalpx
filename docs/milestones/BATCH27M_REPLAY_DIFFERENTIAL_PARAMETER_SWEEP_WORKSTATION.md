# Batch 27M — Replay Differential / Parameter-Sweep Experiment Workstation

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_DIFFERENTIAL_PARAMETER_SWEEP_WORKSTATION
```

## Scope

Batch 27M creates replay-only differential / parameter-sweep experiment workstation surfaces under run/replay/<experiment_id>/experiments/.

It does not send orders.
It does not arm execution.
It does not approve paper/live.
It does not prove production strategy improvement.
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
experiment root: run/replay/<experiment_id>/experiments/
```

## Files created / refreshed

```text
app/mme_scalpx/replay/experiment_workstation.py
etc/replay/schemas/replay_experiment_workstation_contract_v1.json
etc/replay/experiments/replay_experiment_profile_manifest_v1.json
bin/replay_experiments.py
bin/proof_replay_experiment_profiles.py
bin/proof_replay_differential_parameter_sweep.py
```

## Files patched additively

```text
app/mme_scalpx/replay/contracts.py
app/mme_scalpx/replay/experiments.py
app/mme_scalpx/replay/differential.py
app/mme_scalpx/replay/comparison_artifacts.py
bin/replay_run.py
```

## Replay experiment profiles proven

```text
baseline_vs_shadow
parameter_sweep
threshold_sweep
family_enable_disable
side_only
scenario_matrix_comparison
```

## Replay experiment exports proven

```text
00_experiment_manifest.json
01_experiment_summary.json
02_variant_results.json
03_differential_summary.json
04_parameter_sweep_summary.json
05_threshold_sweep_summary.json
06_family_side_summary.json
07_experiment_reproducibility.json
08_experiment_comparison_export.json
```

## Proof artifacts

```text
run/proofs/proof_replay_experiment_profiles.json
run/proofs/proof_replay_differential_parameter_sweep.json
run/proofs/proof_replay_differential_parameter_sweep_workstation.json
run/proofs/proof_replay_differential_parameter_sweep_workstation_latest.json
run/proofs/proof_replay_no_broker_call.json
run/proofs/proof_replay_no_live_redis_write.json
run/proofs/proof_replay_no_runtime_promotion.json
run/proofs/proof_replay_report_exports.json
run/proofs/proof_replay_baseline_shadow_comparison.json
```

## Confirmed pass condition

```text
differential_parameter_sweep_workstation_ok = true
experiment_profiles_ok = true
differential_parameter_sweep_ok = true
baseline_vs_shadow_ok = true
parameter_sweep_ok = true
threshold_sweep_ok = true
family_enable_disable_ok = true
side_only_ok = true
scenario_matrix_comparison_ok = true
all_artifacts_ok = true
all_required_exports_ok = true
all_hashes_ok = true
exported_manifest_no_live_ok = true
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
experiment_profile_shape = PROVEN_BY_27M
differential_summary_shape = PROVEN_BY_27M
parameter_sweep_shape = PROVEN_BY_27M
threshold_sweep_shape = PROVEN_BY_27M
family_side_filter_shape = PROVEN_BY_27M
experiment_reproducibility_hash = PROVEN_BY_27M
strategy_improvement_claim = NOT_PROVEN_IN_27M
full_live_replay_parity = NOT_PROVEN_IN_27M
```

## Meaning

Replay now has a safe replay-only differential / experiment workstation surface for research comparisons.

This still does not approve strategy changes. Any production doctrine revision must be separately reviewed, proven, and frozen.

## Next batch

```text
Batch 27N — Replay final integration audit / workstation acceptance gate
```

27N should run a full consolidated replay workstation acceptance gate across 27C through 27M, verify no live contamination, and produce the final replay-readiness milestone without approving paper/live.
