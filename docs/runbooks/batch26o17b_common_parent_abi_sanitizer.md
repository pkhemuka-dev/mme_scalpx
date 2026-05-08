# Batch 26-O17B — Common Parent ABI Sanitizer

## Purpose

O17A fixed the 12-key `common.selected_option` ABI but added `common.selected_option_rich`, causing the parent `common` ABI to fail.

O17B removes rich runtime selected-option data from `common`, preserves it outside `common`, and proves strategy one-shot again.

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

`PASS_O17B_STRATEGY_ONESHOT_CONTRACT_OK_NO_ORDER`

Acceptable continuation:

`PASS_O17B_COMMON_ABI_FIXED_STRATEGY_ONESHOT_NEXT_ERROR_REVIEW`

If fail, inspect proof JSON and do not proceed to paper.
