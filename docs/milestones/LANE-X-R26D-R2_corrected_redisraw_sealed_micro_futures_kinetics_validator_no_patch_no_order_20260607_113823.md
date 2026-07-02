# R26D-R2 Corrected Day-5 Sealed Micro Futures Kinetics Validator

fut_path: run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz
raw_lines: 71250
redis_entries: 1250
parsed_rows: 1250
valid_ltp_rows: 0
ready_rows: 0
nonzero_delta_rows: 0
nonzero_velocity_rows: 0
nonzero_volume_norm_rows: 0

## First entry keys
['23462.3', '23466.9', '260', '585', 'False', '[{"price":23462.3,"quantity":260,"orders":3},{"price":23462.2,"quantity":65,"orders":1},{"price":23462.0,"quantity":65,"orders":1},{"price":23460.1,"quantity":195,"orders":2},{"price":23460.0,"quantity":1950,"orders":5}]', '[{"price":23466.9,"quantity":585,"orders":3},{"price":23467.6,"quantity":650,"orders":1},{"price":23467.7,"quantity":65,"orders":1},{"price":23468.0,"quantity":65,"orders":1},{"price":23468.4,"quantity":65,"orders":1}]', 'exchange', 'expiry', 'instrument_key', 'instrument_role', 'instrument_token', 'oi', 'provider_id', 'provider_role', 'reject_reason', 'seq_no', 'strike', 'tick_validity', 'trading_symbol', 'ts_event_ns', 'ts_provider_ns', 'ts_recv_ns', 'volume']

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
- volume: 1250
- oi: 1250
- strike: 1250
- expiry: 1250
- tick_validity: 1250
- reject_reason: 1250
- False: 1138
- 65: 844
- 130: 389
- 23450.0: 240
- 195: 158
- 23455.0: 120
- is_selected_option: 112
- is_shadow_option: 112
- 260: 99
- 23449.0: 94
- 23465.0: 91
- 23470.0: 76
- 23440.0: 76
- 23445.0: 71
- 23448.0: 71
- 325: 63
- 390: 62
- 23454.9: 56
- 23469.0: 47
- 23454.0: 47
- 23450.1: 44
- 23466.9: 42
- 650: 42

## Examples

R26D_R2_SEALED_FUTURES_KINETICS_VALIDATOR_OK=False

## Interpretation
- R26D failed because the first parser expected JSON-per-line.
- R26D-R2 parses pseal Redis raw stream id + field/value format.
- This does not run replay, start services, write Redis, or create candidates.
- If OK, R26B can extract futures kinetics from Day-5 sealed futures ticks.