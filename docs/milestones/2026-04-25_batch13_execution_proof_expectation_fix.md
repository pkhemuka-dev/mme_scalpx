# Batch 13 — Execution Proof Expectation Fix

Date: 2026-04-25 11:21:48 IST

## Problem

Initial Batch 13 proof failed 3 cases even though execution rejected them correctly:

- missing option token
- zero limit price
- negative limit price

The ACK rejection reasons were correct:

- `decision_contract_error:missing_option_token`
- `decision_contract_error:missing_or_invalid_limit_price`

But the proof script expected the wrong substring for these cases.

## Fix

Updated `bin/proof_execution_family_entry_safety.py` to use explicit expected rejection reasons per invalid-entry case.

## Result required

Batch 13 is freeze-final only if:

- compile proof passes
- import/surface proof passes
- `bin/proof_execution_family_entry_safety.py` returns status PASS
- strict Redis contract regression remains PASS
- prior batch regression smoke remains PASS where proof scripts exist

## Proof artifact

- `run/proofs/execution_family_entry_safety.json`

## Boundary

This fixes proof expectations only. It does not expand execution scope and does not activate Dhan fallback execution.

