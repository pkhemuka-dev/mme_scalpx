# Batch 11 — Activation Candidate Action Corrective

Date: 2026-04-25 11:08:50 IST

## Problem

Initial Batch 11 proof failed:

```text
IndexError: tuple index out of range
A.rank_activation_candidates(frames)[0]
```

Cause:

- Shared `DoctrineEvaluationResult(candidate=...)` carries candidate truth.
- It does not carry direct `action=ENTER_CALL/ENTER_PUT`.
- `activation._evaluation_to_frame()` defaulted action to HOLD.
- `rank_activation_candidates()` filters to ENTER_CALL / ENTER_PUT only.

## Fix

`activation.py` now infers candidate entry action from branch:

- CALL -> ENTER_CALL
- PUT -> ENTER_PUT

This is still candidate-selection only. It does not publish, route to broker, or place orders.

## Result required

Batch 11 is freeze-final only if:

- compile proof passes
- import/surface proof passes
- `bin/proof_strategy_family_shared_layer_contracts.py` returns status PASS
- strict Redis contract regression remains PASS
- prior batch regression smoke remains PASS where proof scripts exist

## Proof artifact

- `run/proofs/strategy_family_shared_layer_contracts.json`

## Boundary

This closes activation candidate normalization only. It does not close:

- whole-tree replay/dataset.py P0 indentation error
- Batch 12 doctrine leaves
- provider/broker live equivalence
- live MISO promotion proof
- Dhan execution fallback implementation/quarantine

