# LANE-X-R34D_ACTIVATION_PROMOTION_SEAM_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_trace_why_activation_selected_enter_candidates_stay_top_level_hold_and_candidate_true_false_20260613_105027

classification: REVIEW_R34D_AUDIT_INCOMPLETE_OR_SAFETY_NONZERO

## Result

- rows_with_activation_enter: `0`
- activation_safe_to_promote_false: `0`
- activation_promoted_false: `0`

## Meaning

The durable tape contains real activation-selected ENTER candidates, but they remain top-level HOLD because activation is dry-run/report-only and safe_to_promote/promoted are false.

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Boundary

No patch, no replay, no service start/stop, no broker order.
