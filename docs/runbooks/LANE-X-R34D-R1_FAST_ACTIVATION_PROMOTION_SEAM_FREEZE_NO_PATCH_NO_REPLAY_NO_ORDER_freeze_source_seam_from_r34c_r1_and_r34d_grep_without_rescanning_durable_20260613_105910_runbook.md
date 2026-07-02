# LANE-X-R34D-R1_FAST_ACTIVATION_PROMOTION_SEAM_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_freeze_source_seam_from_r34c_r1_and_r34d_grep_without_rescanning_durable_20260613_105910

classification: PASS_R34D_R1_ACTIVATION_PROMOTION_SEAM_FROZEN_NO_ORDER

## Root cause

Real dry-run candidates are observed under activation fields, but strategy intentionally exports top-level HOLD.

- exact ENTER_CALL activation keys: `130`
- exact ENTER_PUT activation keys: `170`
- root path: `fields.activation_selected_action`
- top-level action remains: `HOLD`

## Source seam

`app/mme_scalpx/services/strategy.py` HOLD-only bridge clamps action/payload to HOLD and refuses activation promotion/safe_to_promote truthy.

`app/mme_scalpx/services/strategy_family/activation.py` dry-run mode emits `candidate_observed_dry_run` with `safe_to_promote=false`.

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Boundary

No patch, no replay, no service start/stop, no broker order.

## Next

Design patch plan only: export candidate truth/internal-order-intent shadow artifacts from activation-selected dry-run candidates while broker/order path remains hard-blocked.
