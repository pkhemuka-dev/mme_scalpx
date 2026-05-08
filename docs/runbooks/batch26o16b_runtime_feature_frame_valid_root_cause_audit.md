# Batch 26-O16B — Runtime Feature `frame_valid` Root-Cause Audit / Plan

## Purpose

O16A proved:

- O16 synthetic consumer-view mapper is correct.
- Corrected process detector shows risk/execution are not running.
- Orders remain zero.
- Real-live approval remains false.
- Runtime feature payload still has `frame_valid=false`.

O16B is an audit/plan-only batch to identify the exact source family for runtime `frame_valid=false`.

## Safety Boundary

This batch does not:

- patch production source,
- start paper,
- start risk,
- start execution,
- write orders,
- approve real live,
- force `data_valid=true`,
- relax thresholds,
- enable MISO.

## What O16B Audits

1. `features.py` frame-valid/data-valid source path.
2. `feeds.py` producer keys and published surfaces.
3. `names.py` Redis hash/stream constants.
4. Provider runtime fields and readiness mapping.
5. Redis hashes/streams for:
   - futures feed,
   - selected option feed,
   - Dhan context,
   - provider runtime,
   - feed snapshot,
   - feature state,
   - order stream.
6. Safety:
   - risk not running,
   - execution not running,
   - orders zero,
   - real-live false.

## Expected PASS

`PASS_O16B_RUNTIME_FRAME_VALID_ROOT_CAUSE_AUDIT_OK`

This means the root-cause family is classified, but no production patch has been performed.

## Expected Next Batch

If O16B proves the exact producer/consumer mismatch, next batch should be:

**Batch 26-O16C — exact feature input snapshot mapping repair**

O16C must remain narrow and must not force data validity.
