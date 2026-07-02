# R27H Rerun Sealed Prior-Shelf Ref Contract Validator

fut_path: run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz
raw_lines: 71250
redis_entries: 1250
valid_rows: 1250

## Surface prior-ref validation
- surface_prior_ready_rows: 1247
- surface_call_breakouts_ge_0_20: 43
- surface_put_breakouts_ge_0_20: 32
- surface_call_extension_stats: {'n': 1247, 'min': 0.0, 'median': 0.0, 'mean': 0.0758620689655219, 'p90': 0.0, 'p95': 0.0, 'max': 9.0}
- surface_put_extension_stats: {'n': 1247, 'min': 0.0, 'median': 0.0, 'mean': 0.05292702485966319, 'p90': 0.0, 'p95': 0.0, 'max': 6.0}

## Contract block prior-ref validation
- block_prior_ready_rows: 1247
- block_call_breakouts_ge_0_20: 43
- block_put_breakouts_ge_0_20: 32
- block_call_extension_stats: {'n': 1247, 'min': 0.0, 'median': 0.0, 'mean': 0.0758620689655219, 'p90': 0.0, 'p95': 0.0, 'max': 9.0}
- block_put_extension_stats: {'n': 1247, 'min': 0.0, 'median': 0.0, 'mean': 0.05292702485966319, 'p90': 0.0, 'p95': 0.0, 'max': 6.0}

## Examples from contract block
- {'sid': '1780651741718-0', 'ltp': 23455.0, 'surface_ref_high': 23446.0, 'surface_ref_low': 23446.0, 'surface_call_ext': 9.0, 'surface_put_ext': 0.0, 'block_ref_high': 23446.0, 'block_ref_low': 23446.0, 'block_call_ext': 9.0, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651742435-0', 'ltp': 23463.9, 'surface_ref_high': 23455.0, 'surface_ref_low': 23446.0, 'surface_call_ext': 8.900000000001455, 'surface_put_ext': 0.0, 'block_ref_high': 23455.0, 'block_ref_low': 23446.0, 'block_call_ext': 8.900000000001455, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651746479-0', 'ltp': 23466.9, 'surface_ref_high': 23464.0, 'surface_ref_low': 23446.0, 'surface_call_ext': 2.900000000001455, 'surface_put_ext': 0.0, 'block_ref_high': 23464.0, 'block_ref_low': 23446.0, 'block_call_ext': 2.900000000001455, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651747946-0', 'ltp': 23468.0, 'surface_ref_high': 23466.9, 'surface_ref_low': 23446.0, 'surface_call_ext': 1.0999999999985448, 'surface_put_ext': 0.0, 'block_ref_high': 23466.9, 'block_ref_low': 23446.0, 'block_call_ext': 1.0999999999985448, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651749432-0', 'ltp': 23469.0, 'surface_ref_high': 23468.0, 'surface_ref_low': 23446.0, 'surface_call_ext': 1.0, 'surface_put_ext': 0.0, 'block_ref_high': 23468.0, 'block_ref_low': 23446.0, 'block_call_ext': 1.0, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651790482-0', 'ltp': 23444.4, 'surface_ref_high': 23469.0, 'surface_ref_low': 23450.0, 'surface_call_ext': 0.0, 'surface_put_ext': 5.599999999998545, 'block_ref_high': 23469.0, 'block_ref_low': 23450.0, 'block_call_ext': 0.0, 'block_put_ext': 5.599999999998545, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651808457-0', 'ltp': 23444.0, 'surface_ref_high': 23461.1, 'surface_ref_low': 23444.4, 'surface_call_ext': 0.0, 'surface_put_ext': 0.4000000000014552, 'block_ref_high': 23461.1, 'block_ref_low': 23444.4, 'block_call_ext': 0.0, 'block_put_ext': 0.4000000000014552, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651808694-0', 'ltp': 23441.2, 'surface_ref_high': 23461.1, 'surface_ref_low': 23444.0, 'surface_call_ext': 0.0, 'surface_put_ext': 2.7999999999992724, 'block_ref_high': 23461.1, 'block_ref_low': 23444.0, 'block_call_ext': 0.0, 'block_put_ext': 2.7999999999992724, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651809450-0', 'ltp': 23440.0, 'surface_ref_high': 23461.1, 'surface_ref_low': 23441.2, 'surface_call_ext': 0.0, 'surface_put_ext': 1.2000000000007276, 'block_ref_high': 23461.1, 'block_ref_low': 23441.2, 'block_call_ext': 0.0, 'block_put_ext': 1.2000000000007276, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651810487-0', 'ltp': 23435.0, 'surface_ref_high': 23461.1, 'surface_ref_low': 23440.0, 'surface_call_ext': 0.0, 'surface_put_ext': 5.0, 'block_ref_high': 23461.1, 'block_ref_low': 23440.0, 'block_call_ext': 0.0, 'block_put_ext': 5.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651811445-0', 'ltp': 23429.0, 'surface_ref_high': 23461.1, 'surface_ref_low': 23435.0, 'surface_call_ext': 0.0, 'surface_put_ext': 6.0, 'block_ref_high': 23461.1, 'block_ref_low': 23435.0, 'block_call_ext': 0.0, 'block_put_ext': 6.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651812231-0', 'ltp': 23425.0, 'surface_ref_high': 23461.1, 'surface_ref_low': 23429.0, 'surface_call_ext': 0.0, 'surface_put_ext': 4.0, 'block_ref_high': 23461.1, 'block_ref_low': 23429.0, 'block_call_ext': 0.0, 'block_put_ext': 4.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651817209-0', 'ltp': 23421.5, 'surface_ref_high': 23461.1, 'surface_ref_low': 23425.0, 'surface_call_ext': 0.0, 'surface_put_ext': 3.5, 'block_ref_high': 23461.1, 'block_ref_low': 23425.0, 'block_call_ext': 0.0, 'block_put_ext': 3.5, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651818484-0', 'ltp': 23421.0, 'surface_ref_high': 23455.2, 'surface_ref_low': 23421.5, 'surface_call_ext': 0.0, 'surface_put_ext': 0.5, 'block_ref_high': 23455.2, 'block_ref_low': 23421.5, 'block_call_ext': 0.0, 'block_put_ext': 0.5, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651818677-0', 'ltp': 23416.5, 'surface_ref_high': 23455.2, 'surface_ref_low': 23421.0, 'surface_call_ext': 0.0, 'surface_put_ext': 4.5, 'block_ref_high': 23455.2, 'block_ref_low': 23421.0, 'block_call_ext': 0.0, 'block_put_ext': 4.5, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651820463-0', 'ltp': 23415.6, 'surface_ref_high': 23455.2, 'surface_ref_low': 23416.5, 'surface_call_ext': 0.0, 'surface_put_ext': 0.9000000000014552, 'block_ref_high': 23455.2, 'block_ref_low': 23416.5, 'block_call_ext': 0.0, 'block_put_ext': 0.9000000000014552, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651821457-0', 'ltp': 23412.5, 'surface_ref_high': 23455.2, 'surface_ref_low': 23415.6, 'surface_call_ext': 0.0, 'surface_put_ext': 3.099999999998545, 'block_ref_high': 23455.2, 'block_ref_low': 23415.6, 'block_call_ext': 0.0, 'block_put_ext': 3.099999999998545, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651938442-0', 'ltp': 23425.5, 'surface_ref_high': 23425.0, 'surface_ref_low': 23420.0, 'surface_call_ext': 0.5, 'surface_put_ext': 0.0, 'block_ref_high': 23425.0, 'block_ref_low': 23420.0, 'block_call_ext': 0.5, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651942477-0', 'ltp': 23429.0, 'surface_ref_high': 23425.5, 'surface_ref_low': 23420.0, 'surface_call_ext': 3.5, 'surface_put_ext': 0.0, 'block_ref_high': 23425.5, 'block_ref_low': 23420.0, 'block_call_ext': 3.5, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}
- {'sid': '1780651942688-0', 'ltp': 23429.8, 'surface_ref_high': 23429.0, 'surface_ref_low': 23420.0, 'surface_call_ext': 0.7999999999992724, 'surface_put_ext': 0.0, 'block_ref_high': 23429.0, 'block_ref_low': 23420.0, 'block_call_ext': 0.7999999999992724, 'block_put_ext': 0.0, 'surface_ref_source': 'prior_micro_shelf', 'block_ref_source': 'prior_micro_shelf'}

## Interpretation
- R27F expectedly failed because surface prior refs did not pass into the contract futures block.
- R27G added contract-block passthrough only.
- R27H proves whether the passthrough works on sealed Day-5 futures.

R27H_SURFACE_PRIOR_REF_OK=True
R27H_CONTRACT_PRIOR_REF_OK=True
R27H_SEALED_PRIOR_REF_VALIDATOR_OK=True