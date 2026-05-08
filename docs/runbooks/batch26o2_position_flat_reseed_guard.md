# Batch 26-O2 — Position FLAT Reseed Guard

Proof/reseed utility for restoring `state:position:mme` to FLAT only when:
- Redis PONG
- orders stream length is 0
- latest order is empty
- risk/execution are not running
- no suspicious broker/order fields exist
- existing position hash is empty or already FLAT

No paper/live approval.
