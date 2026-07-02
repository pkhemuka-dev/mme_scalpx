# LANE-X-R26A_day5_bundle_root_cause_freeze_no_patch_no_order_20260607_112913

classification: PASS_LANE_X_R26A_DAY5_ROOT_CAUSE_FROZEN_MICRO_FUTURES_KINETICS_GAP_NO_ORDER

## Source of truth

```
run/evidence_bundles/LANE-X-R25P_day5_compact_evidence_bundle_no_patch_no_order_20260605_152449.tar.gz
run/evidence_bundles/LANE-X-R25P_day5_compact_evidence_bundle_no_patch_no_order_20260605_152449.tar.gz.sha256
run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027
```

## Root cause

Day-5 proved that R22 option micro-response is live-working, but production candidates still do not promote because futures kinetic primitives are not reaching the production strategy consumer view.

Observed production-side blocker:

```
activation_candidate_count = 0
MIST failed_stage = futures_impulse
MISB failed_stage = shelf_validation
MISC failed_stage = compression_detection
MISR failed_stage = active_trap_zone_selection
MISO failed_stage = runtime_disabled
```

MIST production activation remains below threshold because futures impulse score is zero or unavailable:

```
futures_impulse_score = 0.0
fut_delta = 0.0
fut_velocity_ratio = 0.0
fut_volume_norm = 0.0
option_confirmation_score = strong / 1.0
```

But raw futures ticks proved movement exists:

```
RAW_MULTI_LTP_SAMPLES=8
HYPOTHETICAL_DELTA_3_NONZERO_SAMPLES=8
HYPOTHETICAL_VELOCITY_RATIO_3_NONZERO_SAMPLES=8
```

## Correct next patch target

Add an additive micro futures kinetic producer in features.py, analogous to R22 option micro-response.

The patch must:

```
- compute futures delta_3 from recent futures LTP history
- compute velocity_ratio / vel_ratio from tick-size-normalized movement
- attach source marker micro_futures_kinetics
- not lower thresholds
- not force candidates
- not weaken MISO
- not enable paper/live/order/risk/execution
```

## Not the target

```
- Do not tune MIST thresholds blindly.
- Do not reduce min_score.
- Do not bypass proof/window/exits.
- Do not fix MISO by ignoring Dhan context.
```
