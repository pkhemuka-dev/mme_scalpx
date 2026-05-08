# Batch 26-O16A — Consumer View Proof Correction + Runtime Data-Valid Source Audit

## Purpose

O16 produced a mixed result:

- Synthetic consumer-view mapping was correct.
- `consumer_view_json` was present.
- All 10 branch frames were present.
- `mist_call` branch frame was present.
- Orders remained zero.
- Real live remained false.

But the final O16 verdict failed because:

1. risk/execution process checks matched their own `pgrep` shell commands, causing a false positive; and
2. actual runtime feature payload still had `frame_valid=false`.

O16A corrects the proof detector and audits the runtime `data_valid` / `frame_valid` source path.

## Safety Boundary

This batch is diagnostic only.

It does not:

- patch production source,
- start risk,
- start execution,
- restart paper,
- write orders,
- approve real live,
- relax thresholds,
- force signals,
- enable MISO.

## Generated Files

- `bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py`
- `run/proofs/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.json`
- `run/proofs/manifest_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.json`
- `docs/runbooks/batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.md`
- `docs/milestones/2026-05-04_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.md`

## Important Verdicts

O16A can pass in two valid ways:

### 1. Runtime blocker confirmed

`PASS_O16A_PROOF_CORRECTED_RUNTIME_DATA_VALID_SOURCE_BLOCKER_CONFIRMED`

Meaning:

- O16 process detector false-positive is corrected.
- Risk/execution are truly not running.
- Synthetic mapping is OK.
- Runtime `frame_valid` is still false.
- Next batch must be O16B root-cause repair plan.

### 2. Runtime valid now OK

`PASS_O16A_PROOF_CORRECTED_RUNTIME_DATA_VALID_NOW_OK`

Meaning:

- O16 process detector false-positive is corrected.
- Runtime `frame_valid`, `consumer_view.data_valid`, and `consumer_view.safe_to_consume` are now true.
- Next batch may be O17 activation candidate extraction proof, still no risk/execution.

## Do Not Proceed To Paper

Do not restart controlled paper after O16A.

Only proceed to O17 if O16A proves runtime data-valid now OK.
