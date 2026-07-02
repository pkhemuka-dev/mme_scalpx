# Monday Observe-Only Runbook — LANE-X-R28A_weekend_consolidated_finalizer_monday_observe_checklist_no_patch_no_order_20260607_121432

## Scope

Observe-only validation of R26/R27 changes.

No paper, no live, no broker order.

## Premarket sequence

1. Source shell helpers.
2. Unset all paper/live/order env flags.
3. Run premarket safety check.
4. Compile/import modified modules.
5. Start/reuse observe-only supervisor only.
6. Wait for fresh fut/opt/features/decisions.
7. Run live samplers for:
   - micro_futures_kinetics
   - prior_micro_shelf refs
   - MIST futures_impulse
   - MISB shelf_validation / breakout_extension

## During market

Allowed:

```
pcheck
pauto_status
pfeedcheck
read-only samplers
dashboard
pseal after close
```

Forbidden:

```
paper/live/order/risk/execution start
Redis delete
lock delete
threshold tuning
candidate forcing
MISO weakening
```

## Success criteria

```
orders=0
risk_stream=0
execution_stream=0
micro_futures_kinetics_source seen live
prior_micro_shelf seen live
MIST/MISB blockers progress from bridge-missing to real doctrine stages
```
