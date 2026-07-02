# R26D-R3 Day-5 Sealed Micro Futures Kinetics Validator

fut_path: run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz
raw_lines: 71250
redis_entries: 1250
parsed_rows: 1250
valid_ltp_rows: 1250
ready_rows: 1249
nonzero_delta_rows: 992
nonzero_velocity_rows: 992
nonzero_volume_norm_rows: 0

## First entry keys
['ask', 'ask_qty', 'asks', 'bid', 'bid_qty', 'bids', 'exchange', 'expiry', 'instrument_key', 'instrument_role', 'instrument_token', 'is_selected_option', 'is_shadow_option', 'last_qty', 'ltp', 'oi', 'option_side', 'provider_id', 'provider_role', 'reject_reason', 'seq_no', 'strike', 'tick_validity', 'trading_symbol', 'ts_event_ns', 'ts_provider_ns', 'ts_recv_ns', 'volume']

## First good payload
{'stream_id': '1780653023842-0', 'ltp': '23466.9', 'bid': '23462.3', 'ask': '23466.9', 'trading_symbol': 'NIFTY26JUNFUT', 'ts_event_ns': '1780672822000000000'}

## Most common raw fields
- instrument_key: 1250
- instrument_role: 1250
- ts_event_ns: 1250
- provider_id: 1250
- provider_role: 1250
- exchange: 1250
- instrument_token: 1250
- trading_symbol: 1250
- ts_provider_ns: 1250
- ts_recv_ns: 1250
- seq_no: 1250
- ltp: 1250
- last_qty: 1250
- volume: 1250
- oi: 1250
- bid: 1250
- ask: 1250
- bid_qty: 1250
- ask_qty: 1250
- bids: 1250
- asks: 1250
- option_side: 1250
- strike: 1250
- expiry: 1250
- tick_validity: 1250
- reject_reason: 1250
- is_selected_option: 1250
- is_shadow_option: 1250

## Examples
- {'stream_id': '1780653016904-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': -2.900000000001455, 'velocity_ratio': 58.000000000029104, 'volume_norm': 0.0, 'sample_count': 2, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780653011469-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23462.1, 'delta_3': -4.80000000000291, 'velocity_ratio': 96.00000000005821, 'volume_norm': 0.0, 'sample_count': 3, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780653007975-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23462.2, 'delta_3': -4.700000000000728, 'velocity_ratio': 94.00000000001455, 'volume_norm': 0.0, 'sample_count': 4, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780653004663-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23465.0, 'delta_3': 1.0, 'velocity_ratio': 20.0, 'volume_norm': 0.0, 'sample_count': 5, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652999888-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23465.0, 'delta_3': 2.900000000001455, 'velocity_ratio': 58.000000000029104, 'volume_norm': 0.0, 'sample_count': 6, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652998198-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': 1.7999999999992724, 'velocity_ratio': 35.99999999998545, 'volume_norm': 0.0, 'sample_count': 7, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652991450-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23461.6, 'delta_3': -3.400000000001455, 'velocity_ratio': 68.0000000000291, 'volume_norm': 0.0, 'sample_count': 8, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652985981-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': -1.0, 'velocity_ratio': 20.0, 'volume_norm': 0.0, 'sample_count': 9, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652983453-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': 0.0, 'velocity_ratio': 0.0, 'volume_norm': 0.0, 'sample_count': 10, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652976863-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': 2.400000000001455, 'velocity_ratio': 48.000000000029104, 'volume_norm': 0.0, 'sample_count': 11, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652974368-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': 0.0, 'velocity_ratio': 0.0, 'volume_norm': 0.0, 'sample_count': 12, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652973680-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23462.6, 'delta_3': -1.4000000000014552, 'velocity_ratio': 28.000000000029104, 'volume_norm': 0.0, 'sample_count': 12, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652971635-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': 0.0, 'velocity_ratio': 0.0, 'volume_norm': 0.0, 'sample_count': 12, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652968696-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': 0.0, 'velocity_ratio': 0.0, 'volume_norm': 0.0, 'sample_count': 12, 'source': 'micro_futures_kinetics'}
- {'stream_id': '1780652964440-0', 'symbol': 'NIFTY26JUNFUT', 'ltp': 23464.0, 'delta_3': 1.4000000000014552, 'velocity_ratio': 28.000000000029104, 'volume_norm': 0.0, 'sample_count': 12, 'source': 'micro_futures_kinetics'}

R26D_R3_SEALED_FUTURES_KINETICS_VALIDATOR_OK=False

## Interpretation
- R26D/R26D-R2 were parser-shape failures, not R26B patch failures.
- R26D-R3 preserves blank Redis values and restores field/value alignment.
- This does not run replay, start services, write Redis, or create candidates.
- If OK, R26B can extract futures kinetics from Day-5 sealed futures ticks.