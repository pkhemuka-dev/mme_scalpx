# Lane X R10 Feeds Selected Option Bridge Patch Plan

- timestamp: 2026-06-18T09:53:39+05:30
- mode: NO_PATCH_NO_START_NO_ORDER
- purpose: identify exact feeds.py bridge location and write patch plan after R8/R9

## Current known facts
- R8 proved selected-option tick stream can sync with futures when latest option tick is HSET into active selected-option hashes.
- R9 restored fail-closed and stopped R38EN runtime; no orders/risk/execution streams.
- Required patch should be shared Lane X feeds bridge only, not MISLS.

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=***MASKED***
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== PROCESS SAFETY SNAPSHOT ===
=== PSTATUS FAIL-CLOSED CHECK ===
=== EXACT FEEDS.PY SOURCE CONTEXT ===
=== LIVE CONFIRM BEFORE PATCH PLAN ===
=== PATCH PLAN WRITTEN ===
# R10 Patch Plan: selected-option active bridge refresh

## Problem

R4 proved that `ticks:mme:opt:stream` contains full selected-option market data but `state:snapshot:mme:opt:selected:active` can miss those market fields.

R6 proved that HSET-copying latest option tick fields into both selected-option active hashes fills all missing fields.

R7 proved stale selected-option timestamp causes `snapshot.sync_ok=false`, `MARKETDATA_INCOMPLETE_OR_UNSYNCED`, and provider/tradability false.

R8 proved a continuous HSET refresh from latest option tick can keep fut/option skew at 0ms and make snapshot validity OK.

R9 restored fail-closed after R38EN runtime was seen running.

## Required patch

Patch only the shared Lane X feed bridge/writer in `app/mme_scalpx/services/feeds.py`.

The patch should:

1. When the feed service has latest selected-option tick from `ticks:mme:opt:stream` or provider-specific selected option stream, copy market fields into:
   - `state:snapshot:mme:opt:selected:active`
   - `state:feed:selected_option:active`

2. Required copied fields:
   - `ltp`
   - `trading_symbol`
   - `instrument_key`
   - `instrument_token`
   - `bid`
   - `ask`
   - `bid_qty`
   - `ask_qty`
   - `option_side`
   - `strike`
   - `expiry`
   - `ts_event_ns`
   - `ts_provider_ns`
   - `ts_recv_ns`
   - `provider_id`
   - `provider_role`
   - `tick_validity`
   - `instrument_role`
   - `exchange`
   - `bids`
   - `asks`

3. Derived/normalized fields:
   - `selected_option_snapshot_ns = ts_event_ns or ts_provider_ns`
   - `selected_option_marketdata_provider_id = provider_id`
   - `active_selected_option_provider_id = provider_id`
   - `selected_option_marketdata_status = HEALTHY` only if tick validity OK and bid/ask/ltp present
   - `selected_option_provider_status = HEALTHY`
   - `validity = OK`
   - `validity_reason = selected_option_bridge_refresh_from_latest_tick`

4. Must not:
   - DEL / FLUSH / XTRIM / XDEL / lock delete
   - start risk/execution
   - start paper/live
   - change strategy eligibility
   - fake candidates
   - force ENTER
   - modify MISLS files

5. Post-patch validation:
   - `python3 -m py_compile app/mme_scalpx/services/feeds.py`
   - run R8 again to prove skew <= 1000ms naturally
   - run R2 candidate gate again
   - keep pstatus fail-closed until explicit controlled-paper gate
=== STATIC SAFETY SCAN: FORBIDDEN OPS IN PLAN ONLY ===

## R10 verdict
PASS_R10_FEEDS_SELECTED_OPTION_BRIDGE_PATCH_PLAN_WRITTEN_NO_PATCH_NO_START_NO_ORDER
- source_patch_performed=NO
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO
- next_step=R11_PATCH_FEEDS_SELECTED_OPTION_BRIDGE_REFRESH
