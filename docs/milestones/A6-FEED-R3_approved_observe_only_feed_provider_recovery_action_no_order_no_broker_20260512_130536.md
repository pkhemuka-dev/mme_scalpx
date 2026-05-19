# A6-FEED-R3_approved_observe_only_feed_provider_recovery_action_no_order_no_broker_20260512_130536

## Verdict
BLOCKED_A6_FEED_R3_PFEED_OR_PFEEDSTOP_NOT_AVAILABLE_NO_FALLBACK_USED

## Blocked reason
PFEED_OR_PFEEDSTOP_NOT_AVAILABLE_NO_FALLBACK_USED

## Safety
- approval_ok: True
- source_patch_applied: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false
- final_safety_ok: True
- orders_growth_pre_to_final: 0

## Feed recovery action
- service_stop_attempted: False
- service_start_attempted: False

## Canonical post-recovery hints
- provider_runtime_present_final: False
- futures_active_present: False
- selected_option_present: False
- option_context_present: False
- canonical_tick_growth_pre_to_final: {
  "fut_zerodha": 0,
  "fut_dhan": 0,
  "opt_selected_zerodha": 0,
  "opt_selected_dhan": 0,
  "opt_context_dhan": 0
}

## Next
A6-FEED-R4 post-recovery canonical stream/hash proof.
