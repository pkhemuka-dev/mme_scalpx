# B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133 — Dedicated Dhan Context Service Design

## Objective

Make Dhan option context a supervised provider subsystem instead of a fragile side path inside normal feeds.

## Proposed service

`app/mme_scalpx/services/dhan_context.py`

## Writes

- `ticks:mme:opt:context:dhan:stream`
- `ticks:mme:opt:selected:dhan:stream`
- `state:dhan:context:mme`
- `health:dhan:context:mme`

## Health states

- `LIVE`
- `STALE`
- `RATE_LIMITED`
- `AUTH_FAILED`
- `DISABLED`
- `DEGRADED`

## Non-goals

- No order routing
- No strategy threshold changes
- No fake provider_ready_miso
- No stale context silently treated as live

## Contract-first implementation order

1. Freeze names/model contracts for Dhan context health/state if missing
2. Extract existing Dhan option-chain/context adapter call
3. Create dedicated publisher/service wrapper
4. Compile/static proof
5. Live-session observe-only Dhan context growth proof

## Acceptance criteria

- No broker/order integration.
- No strategy threshold changes.
- Compile/static proof passes.
- Live observe-only proof shows Dhan context stream growth.
- Strategy candidate audit is rerun after Dhan context is restored.
