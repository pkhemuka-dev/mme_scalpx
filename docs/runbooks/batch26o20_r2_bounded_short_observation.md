# Batch 26-O20-R2 — Bounded Short Observation

## Purpose

O20 was terminated before proof creation. O20R recovered safely. O20-R2 reruns the observation with:

- reduced duration,
- bounded samples,
- nohup-safe driver,
- fail-safe proof writing on interruption.

## Scope

- MIST CALL only
- 1 lot only
- controlled paper/sandbox only
- real-live false
- no automatic broker failover
- no mid-position provider migration
- no heavy O11 monitor
- no unbounded Redis polling
- no threshold relaxation
- no forced candidate

## Defaults

- `BATCH26O20_R2_RUN_SECONDS=150`
- `BATCH26O20_R2_SAMPLE_COUNT=6`

## Required PASS

`PASS_O20_R2_BOUNDED_SHORT_OBSERVATION_OK_NO_ORDER`

If PASS, next batch is O21 controlled-paper promotion readiness review.

If FAIL, inspect proof JSON and logs; do not proceed.
