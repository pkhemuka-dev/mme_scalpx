# R26D Day-5 Sealed Micro Futures Kinetics Validator

fut_path: run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz
raw_rows: 71250
parsed_rows: 0
valid_ltp_rows: 0
ready_rows: 0
nonzero_delta_rows: 0
nonzero_velocity_rows: 0
nonzero_volume_norm_rows: 0

## Examples

R26D_SEALED_FUTURES_KINETICS_VALIDATOR_OK=False

## Interpretation
- This is a sealed-data validator only.
- It does not run replay, start services, write Redis, or create candidates.
- It proves the R26B producer can extract futures kinetics from Day-5 frozen futures ticks.