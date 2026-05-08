# Batch 26-O16G — Selected-Option Provider/Data-Quality/Tradability Validation Repair

## Purpose

O16F proved selected option is already present, but the remaining blocker is:

- `provider_ready_classic = false`
- `data_quality_ok = false`
- `data_valid = false`

O16G repairs only selected-option provider, quote-quality, and tradability mapping in `features.py`.

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
- enable MISO.

## Allowed Patch

Only `features.py` may be patched, and only with selected-option provider/data-quality/tradability mapping.

## Possible Final Verdicts

### PASS_O16G_RUNTIME_DATA_VALID_SAFE_TO_CONSUME_OK

Proceed to O17 activation candidate extraction proof, no risk/execution.

### PASS_O16G_PROVIDER_DATA_QUALITY_REPAIRED_DATA_VALID_STILL_FAIL_CLOSED

Proceed to O16H final data-valid composition audit/repair.

### FAIL_O16G_PROVIDER_DATA_QUALITY_REPAIR_NOT_PROVEN

Stop and inspect proof JSON.
