# One-lot, one-event micro-real readiness

This runbook prepares the first micro-real lifecycle but does not authorize or
transmit an order.

## Required sequence

1. Fresh Monday no-start preflight.
2. Broker GET-only proof:
   - authenticated session healthy;
   - broker positions FLAT;
   - active/open orders zero;
   - sufficient available margin.
3. Fresh market-data proof:
   - provider ready;
   - safe to consume;
   - quote fresh;
   - selected symbol/token stable.
4. TQAG:
   - decision AUTHORIZE;
   - hard veto count zero;
   - bid and ask quantity valid;
   - spread acceptable;
   - underlying and option aligned;
   - no chase;
   - conservative edge after all costs positive;
   - timeframe complete.
5. Exact charge and breakeven model configured from official rates.
6. First real policy:
   - MARKETABLE_LIMIT;
   - max attempts 1;
   - retry 0;
   - replacement 0;
   - averaging 0;
   - max lots 1;
   - max positions 1;
   - max events 1;
   - unfilled order is a safe outcome.
7. Fresh explicit user authorization after reviewing the complete readiness
   record.
8. Separate transport binding and controlled operator launch.

## Absolute blocks

- A previously fired daily stop.
- Any TQAG hard veto.
- Missing charge component.
- Missing broker-flat or open-order proof.
- Data gap, stale quote, symbol reset, pending order, or cutoff passed.
- Any request for retry, replacement, averaging, second position, second lot,
  or second event.
