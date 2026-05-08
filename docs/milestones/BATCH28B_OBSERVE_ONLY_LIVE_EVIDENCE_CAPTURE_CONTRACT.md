# Batch 28B — Observe-only Live Evidence Capture Contract for Parity Audit

Date: 2026-05-01

## Verdict

```text
PASS_OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_28B
```

## Accepted for

```text
OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY
```

## R2 note

Initial 28B passed contract/import/core safety proofs, but the no-enablement proof failed because its static scanner scanned proof-helper implementation code and flagged Python helper usage.

R2 narrows the static scan to the 28B operational surface:

```text
app/mme_scalpx/replay/live_evidence.py
bin/observe_only_live_evidence_collect.py
```

R2 also avoids broad `compileall app` because an unrelated pre-existing blocker was observed in:

```text
app/mme_scalpx/research_gate/constructor_audit.py
```

That unrelated compile blocker is recorded in:

```text
run/proofs/batch28b_r2_unrelated_compileall_blocker.json
```

It is not patched in Batch 28B.

## Scope

Batch 28B defines the future observe_only live evidence capture package required for replay/live parity audit.

It does not perform a live market capture.
It does not start services.
It does not read live Redis.
It does not write live Redis.
It does not call brokers.
It does not approve paper_armed.
It does not approve live trading.
It does not prove full replay/live parity.

## Required future observe_only evidence

```text
provider_runtime
feed_snapshot
feature_payload
family_surfaces
strategy_activation
no_order_sent
live_capture_log
live_stream_inventory
live_hash_inventory
provider_health_snapshot
selected_option_context
dhan_oi_ladder_context_if_available
```

## Required capture artifacts

```text
00_live_evidence_manifest.json
01_provider_runtime.json
02_feed_snapshot.json
03_feature_payload.json
04_family_surfaces.json
05_strategy_activation.json
06_no_order_sent.json
07_live_stream_inventory.json
08_live_hash_inventory.json
09_provider_health_snapshot.json
10_selected_option_context.json
11_dhan_oi_ladder_context.json
12_live_capture_log_reference.json
13_capture_completeness.json
14_no_enablement_boundary.json
15_capture_reproducibility.json
```

## Proof artifacts

```text
run/proofs/proof_observe_only_live_evidence_capture_contract.json
run/proofs/proof_observe_only_live_evidence_no_enablement.json
run/proofs/proof_observe_only_live_evidence_capture_28b.json
run/proofs/proof_observe_only_live_evidence_capture_28b_latest.json
run/proofs/batch28b_r2_static_scan_before.json
run/proofs/batch28b_r2_targeted_compile.json
run/proofs/batch28b_r2_import_check.json
run/proofs/batch28b_r2_unrelated_compileall_blocker.json
```

## Confirmed pass condition

```text
observe_only_live_evidence_capture_28b_ok = true
observe_only_live_evidence_capture_contract_ok = true
observe_only_live_evidence_no_enablement_ok = true
plan28a_ok = true
reachability_ok = true
targeted_compile_ok = true
import_ok = true
schema_ok = true
static_plan_ok = true
runtime_validation_ok = true
materialized_validation_ok = true
required_artifacts_ok = true
static_scan_ok = true
actual_live_evidence_collected = false
starts_services = false
reads_live_redis = false
writes_live_redis = false
calls_broker_api = false
broker_call_reachable = false
live_redis_write_reachable = false
runtime_promotion_reachable = false
paper_armed_approved = false
live_trading_approved = false
real_order_sent = false
production_doctrine_changed = false
```

## Explicit not-approved / not-proven boundary

```text
paper_armed_readiness = NOT_APPROVED_IN_28B
live_trading_readiness = NOT_APPROVED_IN_28B
production_strategy_improvement_claim = NOT_PROVEN_IN_28B
production_doctrine_revision = NOT_APPROVED_IN_28B
full_live_replay_parity = NOT_PROVEN_IN_28B
```

## Next best move

```text
Batch 28C — Observe-only live evidence collector dry-run / existing-proof package materialization
```
