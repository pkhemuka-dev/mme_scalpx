# Batch 25R-1 — Replay Integrity + Redis Matrix Scope Fix

Date: 2026-04-25  
Timestamp: 20260425_210232  
Run root: `run/batch25R1_replay_integrity_and_redis_matrix_scope_20260425_210232`

## Purpose

Close the remaining Batch 25R proof failures without changing strategy behavior or enabling paper/live order flow.

## Safety posture

```text
SCALPX_ALLOW_LIVE_ORDERS=0
MME_USE_NULL_BROKER=1
MME_USE_NULL_FEED_ADAPTER=1
PYTHONDONTWRITEBYTECODE=1
```

## Changes

```text
1. Patched app/mme_scalpx/replay/integrity.py with a final authoritative compute_integrity_verdict().
2. Placeholder PASS integrity checks now aggregate to FAIL.
3. Replaced Redis contract matrix proof with active-runtime-source scoped scanner.
4. Excluded run artifacts, generated proof bundles, __pycache__, and proof fixtures from strict raw Redis proof scope.
5. Quarantined inactive Batch 25 generated snapshot directory outside project root.
```

## Targeted proof summary

```text
proof	status	rc
bin/proof_redis_contract_matrix.py --strict-raw	PASS	0
bin/proof_replay_batch16_freeze.py	PASS	0
bin/proof_replay_engine_contracts.py	PASS	0
bin/proof_repo_hygiene_quarantine.py	FAIL	1
bin/proof_proof_layer_contracts.py	PASS	0
bin/proof_repo_hygiene_quarantine.py	PASS	0
```

## Compact regression summary

```text
proof	status	rc
bin/proof_models_batch2_freeze.py	PASS	0
bin/proof_core_codec_transport.py	PASS	0
bin/proof_runtime_effective_config.py	PASS	0
bin/proof_provider_runtime_roles.py	PASS	0
bin/proof_runtime_instrument_provider_equivalence.py	PASS	0
bin/proof_execution_family_entry_safety.py	PASS	0
bin/proof_execution_hold_no_order.py	PASS	0
bin/proof_risk_exit_never_blocked.py	PASS	0
bin/proof_risk_batch14_freeze.py	PASS	0
bin/proof_research_capture_contracts.py	PASS	0
bin/proof_legacy_baseline_quarantine.py	PASS	0
bin/proof_names_alias_lifecycle.py	PASS	0
```

## Result

```text
targeted_fail_count=1
compact_regression_fail_count=0
```

## Remaining rule

No strategy redesign.  
No market-session paper_armed until market-hour report-only observation passes.  
Real live trading remains blocked.
