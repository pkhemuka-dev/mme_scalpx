# OPS-DASH-R3L-LITE_LIVE_MARKET_PREFLIGHT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_compact_live_market_observe_only_feed_capture_preflight_20260601_092139

classification: `PASS_OPS_DASH_R3L_LITE_READY_FOR_APPROVED_PFEEDS_OBSERVE_ONLY_CAPTURE_NO_PATCH_NO_START_NO_ORDER_NO_PAPER`

## Safety

- redis_ping: `PONG`
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- risk_proc: `0`
- execution_proc: `0`
- dangerous_env_present: `NO`

## Current streams

- errors: `10000`
- decisions: `1682`
- features: `4420`
- fut_zerodha: `284`
- fut_dhan: `0`
- opt_selected_zerodha: `1027`
- opt_selected_dhan: `0`
- opt_context_dhan: `0`

## Processes

- feeds: `0`
- features: `0`
- strategy: `0`
- risk: `0`
- execution: `0`
- dashboard: `0`

## Locks

- lock:feeds: `feeds:mme-scalpx:1434`
- lock:feeds ttl: `27910`
- lock:execution: `execution:mme-scalpx:1434`
- lock:execution ttl: `29712`

## Next if PASS

Run approved `pfeeds` observe-only capture only.

Still forbidden:
- risk start
- execution start
- paper/live enablement
- broker orders
