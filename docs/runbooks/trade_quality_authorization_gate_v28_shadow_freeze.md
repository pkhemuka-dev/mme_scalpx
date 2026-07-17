# Trade Quality Authorization Gate v28 — Shadow-Only Freeze

## Ownership

The existing strategy remains the sole candidate owner. The v28 gate may return only `AUTHORIZE`, `VETO`, `HOLD`, or `RESET_OBSERVATION`. An `AUTHORIZE` result is an evidence record, not an order instruction.

Direction is owned by NIFTY futures, spot, VWAP relationship/slope, market structure and reliable breadth. The selected option is used only for instrument stability, microstructure, liquidity and execution quality.

## Hard vetoes

No score may override a hard veto. Positive checks must be true: quote freshness, bid/ask quantities, acceptable spread, symbol stability, valid instrument lock, underlying/option alignment, no chase, positive conservative edge after cost, broker flat, zero active broker orders, risk gate open and complete timeframes. Data gaps, pending orders or passed cutoff veto authorization.

## Score

Five components are retained independently at 20 points each: 15-minute regime, 5-minute setup, 3-minute trigger, option microstructure and liquidity/execution. Initial research threshold is total score 75 with every component at least 10. Session-specific policies may be stricter.

## Instrument lock

`CANDIDATE_CREATED → OPTION_SELECTED → OPTION_SYMBOL_LOCKED → MICRO_OBSERVATION_ACTIVE → MICRO_OBSERVATION_COMPLETE → AUTHORIZED`

Symbol, token or strike-classification changes; stale quotes; spread/depth failure; data gaps; and directional inconsistency reset observation. Evidence is never transferred between instruments.

## No-chase and edge after cost

The gate records candidate-creation underlying/option prices, spread and ATR. It compares displacement and spread deterioration at authorization time. Edge after cost includes optimistic and conservative entry/exit spread, slippage, brokerage, taxes and exchange charges.

## First-live planning contract

The module may produce a shadow `MARKETABLE_LIMIT` price-cap plan with one attempt, no retry, no replacement, no averaging, one lot, one position and one event. It cannot submit that plan.

## Session phases

Opening, mid-session, closing and no-new-entry phases have separate score, observation, chase and holding policies. Strategy maximum hold remains 300 seconds. Closing shadow policy is shorter. The lifecycle runner observation bound remains 360 seconds.

## Promotion boundary

Default configuration has `calibration_id=UNSET`, so the gate cannot authorize even in shadow until replay calibration is recorded. Promotion requires Friday replay, one clean controlled-paper retest, a separate real-money preflight and fresh explicit authorization. No v28 file imports a broker order method or writes to Redis.
