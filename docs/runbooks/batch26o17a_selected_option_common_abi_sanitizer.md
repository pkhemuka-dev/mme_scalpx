# Batch 26-O17A — Selected-Option Common ABI Sanitizer

## Purpose

O17 proved activation view consumption, but strategy one-shot failed on:

`FeatureFamilyContractError: common.selected_option keys mismatch`

O17A sanitizes only `common.selected_option` to the frozen 12-key ABI and preserves rich runtime fields separately under `common.selected_option_rich`.

## Safety

This batch does not:

- start paper,
- start risk,
- start execution,
- call broker,
- write orders,
- approve real live,
- force candidates,
- relax thresholds.

## Required PASS

Preferred:

`PASS_O17A_STRATEGY_ONESHOT_CONTRACT_OK_NO_ORDER`

Acceptable continuation:

`PASS_O17A_COMMON_ABI_FIXED_STRATEGY_ONESHOT_NEXT_ERROR_REVIEW`

If fail, inspect proof JSON and do not proceed to paper.
