# Batch 26-O20-R3 — Corrected Bounded Observation Rerun

## Purpose

O20-R2 canonical proof failed because features/strategy process liveness was not proven, and logs showed strategy could read stale invalid feature-family ABI data.

O20-R3 reruns bounded controlled-paper observation with:

- pre-runtime feature hash hygiene,
- strategy one-shot ABI hygiene,
- stricter feature/strategy/risk/execution liveness accounting,
- latest error check for `FeatureFamilyContractError`,
- no stale PASS reuse.

## Safety

This batch remains controlled paper only:

- MIST CALL only
- 1 lot only
- real-live false
- no broker failover
- no mid-position provider migration
- no heavy monitor
- no unbounded Redis polling
- no threshold relaxation
- no forced candidate

## Required PASS

`PASS_O20_R3_CORRECTED_BOUNDED_OBSERVATION_OK_NO_ORDER`

If PASS, do not go directly to O23. Run O22-R2 plan proof correction using O20-R3 as the canonical bounded observation proof.
