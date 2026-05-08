# Batch 26-O17B-R2 — Common ABI Proof Correction + HOLD-only Strategy One-shot Safety Audit

## Purpose

O17B functionally repaired the ABI:

- `common_key_match = true`
- `selected_option_key_match = true`
- `selected_option_rich_not_in_common = true`
- `selected_option_rich_preserved_outside_common = true`
- `strategy_oneshot_no_feature_contract_error = true`

But O17B failed because its proof still required `patch_performed_or_already_present = true`.

O17B-R2 is proof-only and accepts the already-repaired state if strategy one-shot is clean and any decision-stream writes are HOLD-only/no-order.

## Safety

This batch does not:

- start paper,
- start risk,
- start execution,
- call broker,
- write orders,
- approve real live,
- force candidates,
- relax thresholds,
- patch strategy.

## Required PASS

`PASS_O17B_R2_STRATEGY_ONESHOT_CONTRACT_OK_HOLD_ONLY_NO_ORDER`

Then next:

- Batch 26-O18 lightweight controlled-paper preflight
- MIST CALL only
- 1 lot only
- no heavy monitor
