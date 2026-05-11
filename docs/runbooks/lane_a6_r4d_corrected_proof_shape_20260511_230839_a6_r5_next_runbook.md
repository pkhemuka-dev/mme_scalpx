# lane_a6_r4d_corrected_proof_shape_20260511_230839 — A6-R5 next runbook

## Current status

A6-R4D closed the A6-R4 proof-shape polarity issue. No source patch was applied. Controlled paper remains blocked. Real live remains blocked.

## Next batch

`A6-R5 recorded-live-data dry-run one-active-scope route selection / no broker call / no Redis trading write`

## A6-R5 must do

- use recorded live data only if available
- dry-run one-active-scope selection logic
- no broker call
- no order
- no Redis trading-stream write
- no risk/execution service start
- prove all-five monitoring can reduce to exactly one approved scoped candidate or fail closed
- prove multiple valid scoped candidates fail closed, not fan out

## Hard prohibitions

- no real live
- no broker call
- no order placement
- no paper/live enablement
- no all-5 simultaneous order firing
- no automatic strategy switching into execution
- no threshold relaxation
- no forced candidate
