# DATAKEEP-C6F-R5_controlled_stop_rogue_unscoped_main_lock_owner_no_start_no_delete_no_order_20260518_100909

## Verdict

DATAKEEP_C6F_R5_PASS_ROGUE_UNSCOPED_MAIN_STOPPED_LOCKS_CLEARED_NO_ORDER

## What this did

- Stopped only the rogue unscoped app.mme_scalpx.main lock owner if it exactly matched the safe signature.
- Did not start pfeeds.
- Did not start pstack.
- Did not delete locks.
- Did not touch broker/order/paper/live/risk/execution.

## Safety

- target pid: 2533
- orders:mme:stream after: 0
- has_position after: 0
- position_side after: FLAT
- all app main processes after: absent
- service processes after: absent
- risk/execution after: absent

## Locks after

- lock:feeds: none, ttl=-2
- lock:execution: none, ttl=-2

## pfeedcheck after

```text
status=NOT_HEALTHY_PROCESS_DEAD
```

## Next

Run a narrow pfeeds-only retry package next.

No paper/live approval comes from this batch.
