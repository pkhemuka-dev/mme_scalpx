# Batch 26-O16G-R2 — Runtime-Symbol Provider/Data-Quality Repair

## Purpose

O16G failed because the patch script required literal source text `class FeatureService`, while the runtime module exposes `features.FeatureService`.

O16G-R2 patches using runtime symbol availability instead of brittle source text.

## Safety

This batch does not:

- start paper,
- start risk,
- start execution,
- patch strategy,
- write orders,
- approve real live,
- force `data_valid=true`,
- relax thresholds,
- force MISO readiness mutation.

## Allowed Patch

Only `features.py` may be patched, and only by appending a runtime-symbol `FeatureService.run_once` bridge.

## Possible Verdicts

### PASS_O16G_R2_RUNTIME_DATA_VALID_SAFE_TO_CONSUME_OK

Proceed to O17 activation candidate extraction proof, no risk/execution.

### PASS_O16G_R2_PROVIDER_DATA_QUALITY_REPAIRED_DATA_VALID_STILL_FAIL_CLOSED

Proceed to O16H final data-valid composition audit/repair.

### FAIL_O16G_R2_PROVIDER_DATA_QUALITY_REPAIR_NOT_PROVEN

Stop and inspect proof JSON.
