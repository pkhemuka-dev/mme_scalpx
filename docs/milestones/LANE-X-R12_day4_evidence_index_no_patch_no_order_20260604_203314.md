# LANE-X-R12_day4_evidence_index_no_patch_no_order_20260604_203314

classification: PASS_LANE_X_R12_DAY4_EVIDENCE_INDEX_COMPLETE_NO_PATCH_NO_ORDER

## Day-4 Lane X truth

- R5P live micro-shelf producer was validated.
- Classic live observe-only became healthy after instrument refresh.
- All five family surfaces evaluated, but MISO remained runtime-disabled because Dhan context was unavailable.
- Candidate count remained zero.
- Top nearest miss: MIST PUT around score 0.46, failed at futures_impulse / response.
- MISB PUT around score 0.31, failed at shelf_validation / shelf_width_out_of_bounds.
- No paper/live/order/risk/execution path was enabled.

## Primary evidence

Primary live pseal:

```
run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929
```

Supplemental post-market pseal:

```
run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_203023
```

R4 is supplemental only because its Zerodha live tick streams had xlen=0 after market; R3 remains the primary clean live close freeze.

## Indexed proof files

```
run/proofs/LANE-X-R0_prestart_verify_20260604_093055.json
run/proofs/LANE-X-R0B_helper_discovery_20260604_093205.json
run/proofs/LANE-X-R1_live_observe_only_start_20260604_093504.json
run/proofs/LANE-X-R8_post_refresh_consumer_validation_20260604_095634.json
run/proofs/LANE-X-R9C_family_surface_nested_map_extractor_20260604_100238.json
run/proofs/LANE-X-R10_rolling_nearest_miss_sampler_20260604_100336.json
run/proofs/LANE-X-R11_final_live_close_window_sampler_20260604_152512.json
run/proofs/LANE-X-CLOSE-R3_corrected_pseal_completion_finalizer_20260604_152311.json
run/proofs/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203209.json
run/proofs/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203215.json
```

## Indexed sampler CSV files

```
run/audits/LANE-X-R10_rolling_nearest_miss_sampler_20260604_100336_samples.csv
run/audits/LANE-X-R11_final_live_close_window_sampler_20260604_152512_samples.csv
```
