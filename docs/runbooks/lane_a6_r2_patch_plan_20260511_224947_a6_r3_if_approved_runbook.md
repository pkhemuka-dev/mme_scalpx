# lane_a6_r2_patch_plan_20260511_224947 — A6-R3 runbook if user approves patch

## Current status

A6-R2 created a patch plan only. No source patch was applied.

## A6-R3 may patch only these surfaces

1. `app/mme_scalpx/integrations/broker_api.py`
2. `app/mme_scalpx/services/execution.py`
3. `app/mme_scalpx/services/controlled_paper_runtime.py`

## Required A6-R3 behavior

- add explicit paper/sandbox order backend seam
- add execution real-live-forbidden guard
- keep order path fail-closed when paper backend is absent
- one active scope only
- 1 lot only
- position must be flat before entry
- no broker failover
- no mid-position provider migration
- no real live
- no order during patch/proof
- no broker call during patch/proof

## Required A6-R3 proofs

- source backups
- compile proof
- fail-closed dry-run proof
- `broker_calls_executed=false`
- `order_sent=false`
- `orders:mme:stream=0`
- position remains `FLAT`
- no risk/execution PID
- milestone, runbook, sha256
