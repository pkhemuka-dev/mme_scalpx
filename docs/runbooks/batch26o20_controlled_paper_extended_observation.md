# Batch 26-O20 — Controlled-Paper Extended Observation

## Purpose

O20 extends the O19 controlled-paper runtime using bounded lightweight monitoring only.

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

## Default Runtime

- `BATCH26O20_RUN_SECONDS=300`
- `BATCH26O20_SAMPLE_COUNT=10`

The script clamps runtime between 120 and 900 seconds and samples between 5 and 20.

## Required PASS

`PASS_O20_CONTROLLED_PAPER_EXTENDED_OBSERVATION_OK_NO_ORDER`

If PASS, next batch is O21 controlled-paper promotion readiness review.

If FAIL, inspect proof JSON and logs; do not proceed.
