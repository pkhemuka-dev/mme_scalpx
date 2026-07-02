# LANE-X-AFTERMARKET-R33K_READINESS_HYGIENE_REDIS_POLICY_FLAT_GUARD_NO_START_NO_ORDER_20260620_065411

## Current after-market goal

Prepare Lane X for next live session without starting runtime or paper tonight.

## Must be true before one-event controlled paper tomorrow

1. Redis maxmemory-policy should be noeviction.
2. Position hash must be strict flat:
   - has_position=0
   - position_side=FLAT
   - qty_lots=0
   - qty_units=0
3. orders/risk/execution/trades/cmd streams must be 0 before controlled-paper start.
4. feeds/features/strategy observe-only services must be healthy.
5. A real eligible frame must appear naturally from family frames.
6. Hard gate must pass.
7. User must explicitly approve exactly one-event controlled paper.
8. No all-strategy paper.
9. No real-live broker orders.

## Important note

R33I already patched R38EN runner to avoid skipping consumer-group bootstrap. Tomorrow's controlled-paper attempt should verify whether projected ENTER now reaches risk/execution/orders stream.
