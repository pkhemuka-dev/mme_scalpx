# B1-PROFIT-LIVE-R38D_FIXTURE_BEHAVIOR_VALIDATION_AFTER_PROVIDER_FALLBACK_PATCH_NO_START_NO_ORDER

Classification: **PASS_R38D_FIXTURE_BEHAVIOR_VALIDATION_NO_START_NO_ORDER**

## Safety

- orders=0
- risk_stream=0
- execution_stream=0
- risk_pids=0
- execution_pids=0

## Fixture expectations

{
  "case1_selected_fallback_to_zerodha": true,
  "case1_status_healthy": true,
  "case1_pending_false": true,
  "case1_patch_fired": true,
  "case2_dhan_stays_dhan": true,
  "case2_patch_not_fired": true,
  "case3_no_fallback_when_zerodha_unavailable": true,
  "case3_status_unavailable": true,
  "option_context_not_defaulted_to_zerodha": true,
  "miso_law_present": true,
  "mid_position_does_not_switch": true
}

## Cases

{
  "dhan_selected_unavailable_zerodha_selected_healthy": {
    "role": "selected_option_marketdata",
    "previous_provider": "DHAN",
    "preferred_provider": "DHAN",
    "candidate_order": [
      "DHAN",
      "ZERODHA"
    ],
    "statuses": {
      "DHAN": "UNAVAILABLE",
      "ZERODHA": "HEALTHY"
    },
    "first_eligible": "ZERODHA",
    "desired_provider": "ZERODHA",
    "status": "HEALTHY",
    "pending_failover": false,
    "r38b_patch_fired": true
  },
  "dhan_selected_healthy": {
    "role": "selected_option_marketdata",
    "previous_provider": "DHAN",
    "preferred_provider": "DHAN",
    "candidate_order": [
      "DHAN",
      "ZERODHA"
    ],
    "statuses": {
      "DHAN": "HEALTHY",
      "ZERODHA": "HEALTHY"
    },
    "first_eligible": "DHAN",
    "desired_provider": "DHAN",
    "status": "HEALTHY",
    "pending_failover": false,
    "r38b_patch_fired": false
  },
  "dhan_unavailable_zerodha_unavailable": {
    "role": "selected_option_marketdata",
    "previous_provider": "DHAN",
    "preferred_provider": "DHAN",
    "candidate_order": [
      "DHAN",
      "ZERODHA"
    ],
    "statuses": {
      "DHAN": "UNAVAILABLE",
      "ZERODHA": "UNAVAILABLE"
    },
    "first_eligible": null,
    "desired_provider": "DHAN",
    "status": "UNAVAILABLE",
    "pending_failover": false,
    "r38b_patch_fired": false
  },
  "option_context_dhan_unavailable_remains_dhan": {
    "role": "option_context",
    "previous_provider": "DHAN",
    "preferred_provider": "DHAN",
    "candidate_order": [
      "DHAN"
    ],
    "statuses": {
      "DHAN": "UNAVAILABLE"
    },
    "first_eligible": null,
    "desired_provider": "DHAN",
    "status": "UNAVAILABLE",
    "pending_failover": false,
    "r38b_patch_fired": false
  },
  "mid_position_switch_blocked": {
    "role": "selected_option_marketdata",
    "previous_provider": "DHAN",
    "preferred_provider": "DHAN",
    "candidate_order": [
      "DHAN",
      "ZERODHA"
    ],
    "statuses": {
      "DHAN": "UNAVAILABLE",
      "ZERODHA": "HEALTHY"
    },
    "first_eligible": "ZERODHA",
    "desired_provider": "DHAN",
    "status": "UNAVAILABLE",
    "pending_failover": true,
    "r38b_patch_fired": false
  }
}

## Guardrails

- compile_ok=True
- patch_before_status_assignment=True
- dangerous_hits=[]
- source_patch_applied=false
- service_start_attempted=false
- risk_start_attempted=false
- execution_start_attempted=false
- order_attempted=false

## Next

If PASS, create R38E pre-open / live-observe readiness checklist. Do not start paper yet.

Proof: `run/proofs/B1-PROFIT-LIVE-R38D_FIXTURE_BEHAVIOR_VALIDATION_AFTER_PROVIDER_FALLBACK_PATCH_NO_START_NO_ORDER_prove_selected_option_dhan_unavailable_zerodha_fallback_without_runtime_start_20260528_221343.json`
