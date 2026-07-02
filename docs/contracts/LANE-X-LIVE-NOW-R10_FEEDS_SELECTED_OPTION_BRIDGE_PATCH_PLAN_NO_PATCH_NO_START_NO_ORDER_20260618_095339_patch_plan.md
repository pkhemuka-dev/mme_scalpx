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
