# Batch 26-O16D — Selected-Option + Classic Provider Readiness Mapping Audit/Repair

## Purpose

O16C-R2 proved:

- Redis is available.
- `consumer_view_json` is already present.
- All 10 branch frames are present.
- `mist_call` is present.
- Futures are present.
- Selected option / CALL / PUT / classic provider readiness are still false.

O16D focuses narrowly on the selected-option and classic-provider readiness source.

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

Only if Redis already contains concrete selected-option and provider evidence, O16D may patch `features.py` to map that evidence into:

- `selected_option_present`
- `call_present`
- `put_present`
- `provider_ready_classic`
- `data_quality_ok`

The patch must not invent truth. It must not force MISO readiness.

## Expected Final Verdicts

### PASS_O16D_SELECTED_OPTION_CLASSIC_PROVIDER_READY_DATA_VALID_OK

Proceed to O17 activation candidate extraction proof, no risk/execution.

### PASS_O16D_MAPPING_BRIDGE_APPLIED_BUT_RUNTIME_READINESS_STILL_FAIL_CLOSED

Proceed to O16E live-feed selected option source repair or feed-start evidence.

### PASS_O16D_AUDIT_ONLY_SELECTED_OPTION_PROVIDER_EVIDENCE_NOT_SUFFICIENT_FOR_SAFE_PATCH

Proceed to O16E selected-option feed/source evidence collection and O8C bridge verification.

### FAIL_O16D_NOT_PROVEN

Stop and inspect proof JSON.
