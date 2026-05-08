# Batch 27J — Assumption / Scenario Profile Engine

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_ASSUMPTION_SCENARIO_PROFILE_ENGINE
```

## Scope

Batch 27J creates replay-only assumption/scenario profiles and proves explicit scenario application.

It does not send orders.
It does not arm execution.
It does not approve paper/live.
It does not prove full replay scenario outcome parity.

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
```

## Files created / refreshed

```text
app/mme_scalpx/replay/scenarios.py
etc/replay/schemas/replay_scenario_profile_contract_v1.json
etc/replay/scenarios/replay_scenario_profile_manifest_v1.json
bin/proof_replay_scenario_profiles.py
bin/proof_replay_scenario_application.py
```

## Files patched additively

```text
app/mme_scalpx/replay/contracts.py
app/mme_scalpx/replay/engine.py
app/mme_scalpx/replay/dataset.py
bin/replay_run.py
```

## Replay scenarios covered

```text
missing_futures_feed
missing_selected_option_feed
stale_futures_feed
stale_selected_option_feed
dhan_context_unavailable
dhan_context_stale
oi_ladder_missing
oi_wall_shock
wide_spread
low_depth
high_slippage
packet_gaps
timestamp_skew
event_burst
liquidity_shock
forced_risk_veto
full_fill
partial_fill
no_fill
rejected
forced_flatten
session_close
```

## Proof artifacts

```text
run/proofs/proof_replay_scenario_profiles.json
run/proofs/proof_replay_scenario_application.json
run/proofs/proof_replay_assumption_scenario_profile_engine.json
run/proofs/proof_replay_assumption_scenario_profile_engine_latest.json
run/proofs/proof_replay_risk_execution_shadow.json
run/proofs/proof_replay_shadow_fill_pnl.json
run/proofs/proof_replay_no_broker_call.json
run/proofs/proof_replay_no_live_redis_write.json
run/proofs/proof_replay_no_runtime_promotion.json
```

## Confirmed pass condition

```text
assumption_scenario_profile_engine_ok = true
scenario_profiles_ok = true
scenario_application_ok = true
required_scenarios_ok = true
validations_ok = true
forced_veto_ok = true
partial_fill_ok = true
no_fill_ok = true
rejected_ok = true
risk_adapter_execution_shadow_ok = true
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
scenario_profile_shape = PROVEN_BY_27J
scenario_application_shape = PROVEN_BY_27J
full_replay_scenario_outcome_parity = NOT_PROVEN_IN_27J
```

## Meaning

Replay now has an explicit scenario/assumption profile engine.

This is still not a complete live-mimic workstation because batch/date runners, report exports, and full replay/live parity are not yet proven.

## Next batch

```text
Batch 27K — Replay batch/date-range runner and artifact materialization
```

27K should add single-day/date-range/intraday-window runner surfaces and run/replay artifact materialization while preserving no paper/live and no broker/no live Redis guarantees.
