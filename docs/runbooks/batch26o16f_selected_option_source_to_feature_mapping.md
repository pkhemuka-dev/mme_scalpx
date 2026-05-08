# Batch 26-O16F — Exact Selected-Option Source-to-Feature Mapping Repair

## Purpose

O16E found selected-option/provider evidence but feature `stage_flags` still did not mark selected-option readiness. O16F maps concrete selected-option stream truth into the feature common/stage surface.

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

Only `features.py` may be patched, and only with a selected-option source-to-feature mapping bridge.

The bridge may prove:

- selected option source presence,
- selected option common block,
- selected-option stage presence,
- classic provider readiness.

It must not force full `data_quality_ok` or `data_valid` if the selected-option tick is anomaly-clamped or otherwise invalid.

## Possible Final Verdicts

### PASS_O16F_SELECTED_OPTION_MAPPING_DATA_VALID_OK

Proceed to O17 activation candidate extraction proof, no risk/execution.

### PASS_O16F_SELECTED_OPTION_MAPPING_REPAIRED_DATA_QUALITY_STILL_FAIL_CLOSED

Proceed to O16G selected-option data-quality/tradability validation repair.

### FAIL_O16F_SELECTED_OPTION_MAPPING_NOT_PROVEN

Stop and inspect proof JSON.
