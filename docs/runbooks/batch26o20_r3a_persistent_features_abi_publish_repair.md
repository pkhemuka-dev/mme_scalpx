# Batch 26-O20-R3A — Persistent Features-Service ABI Publish Repair

## Purpose

O20-R3 proved one-shot ABI hygiene, but the persistent features service still published invalid ABI after service start.

O20-R3A patches only `features.py` to guard the persistent Redis hash publish path for:

- `family_features_json`
- `payload_json`

It keeps rich selected-option data outside `family_features.common`.

## Safety

This batch does not:

- start paper,
- start strategy,
- start risk,
- start execution,
- call broker,
- write orders,
- enable real live,
- relax thresholds,
- force candidates.

## Required PASS

`PASS_O20_R3A_PERSISTENT_FEATURES_ABI_PUBLISH_REPAIR_OK`

Then next:

`26-O20-R3B corrected bounded observation rerun after persistent ABI repair`
