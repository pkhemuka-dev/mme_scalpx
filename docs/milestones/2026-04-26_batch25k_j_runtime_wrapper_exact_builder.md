# Batch 25K-J — Runtime Wrapper Exact-Builder Corrective

Date: 2026-04-26
Timestamp: 20260426_150830

## Objective

Repair the actual runtime `FeatureEngine._option_surface` dispatch path after diagnostics showed it points to `_batch25l_option_surface_kw_compat`, not the class method patched earlier.

## Evidence

Diagnostics showed:

```text
runtime_source_start_line = 4756
runtime function = _batch25l_option_surface_kw_compat
has_option_core_builder_used = False
```

The original class method was patched, but Batch25L monkeypatching overrode runtime dispatch.

## Files Patched

- `app/mme_scalpx/services/features.py`

## Contract Repaired

The effective runtime wrapper now calls:

```text
option_core.build_live_option_surface(
  side=...,
  live_source=...,
  provider_id=...,
  strike=...,
  instrument_key=...,
  instrument_token=...
)
```

## Proofs

- `run/proofs/proof_feature_family_shared_builder_abi.json`
- `run/proofs/proof_5family_integration_master.json`

## Runtime Safety

This batch does not enable strategy promotion, execution arming, broker orders, provider failover, risk mutation, or execution mutation.

## Required Verdict

```text
feature_family_shared_builder_abi_ok = True
option_core_builder_used = True
fallback_builder_count = 0
final_verdict = HOLD_OBSERVE_READY
```
