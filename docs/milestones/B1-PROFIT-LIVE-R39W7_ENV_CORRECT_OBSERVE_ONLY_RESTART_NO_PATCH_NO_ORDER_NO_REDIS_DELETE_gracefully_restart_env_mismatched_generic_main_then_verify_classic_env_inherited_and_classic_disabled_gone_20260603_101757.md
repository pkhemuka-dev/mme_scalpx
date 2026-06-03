# B1-PROFIT-LIVE-R39W7_ENV_CORRECT_OBSERVE_ONLY_RESTART_NO_PATCH_NO_ORDER_NO_REDIS_DELETE_gracefully_restart_env_mismatched_generic_main_then_verify_classic_env_inherited_and_classic_disabled_gone_20260603_101757

Classification: `PASS_R39W7_ENV_PRESENT_CLASSIC_DISABLED_GONE_NOW_CAPTURE_REAL_NO_SIGNAL_OR_BLOCKERS_OBSERVE_ONLY_NO_ORDER`

## Safety
```text
orders:mme:stream=0
risk:mme:stream=0
execution:mme:stream=0
system:errors:stream=3
decisions:mme:stream=1198
features:mme:stream=407
```

## New process env
```text
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
SCALPX_OBSERVE_ONLY=1
```

## Classic runtime disabled check
- classic_runtime_disabled_count_in_latest_80: 0
- candidate_count_positive_in_latest_80: 0

## Decision reason counts
- hold_only_family_features_consumer_bridge: 80

## Activation reason counts
- no_candidate: 66
- view_data_invalid: 14

## No-signal reason counts
- score_below_threshold: 264
- directional_breakout_not_confirmed: 132
- reversal_direction_not_confirmed: 132
- stage_provider_ready_miso_failed: 132

## Latest decision samples
```json
[
  {
    "activation_candidate_count": 0,
    "activation_reason": "view_data_invalid",
    "activation_report_candidates_len": 0,
    "activation_report_no_signal_first_5": [],
    "activation_report_reason": "view_data_invalid",
    "data_valid": 0,
    "id": "1780462155550-0",
    "provider_ready_classic": 0,
    "reason": "hold_only_family_features_consumer_bridge",
    "safe_to_consume": 1
  },
  {
    "activation_candidate_count": 0,
    "activation_reason": "no_candidate",
    "activation_report_candidates_len": 0,
    "activation_report_no_signal_first_5": [
      {
        "action": "HOLD",
        "blocker": {},
        "branch_id": "CALL",
        "candidate": {},
        "family_id": "MIST",
        "is_blocked": false,
        "is_candidate": false,
        "is_no_signal": true,
        "priority": 0.0,
        "raw": {
          "action": "HOLD",
          "blocker": null,
          "branch_id": "CALL",
          "candidate": null,
          "doctrine_id": "MIST",
          "family_id": "MIST",
          "is_blocked": false,
          "is_candidate": false,
          "is_no_signal": true,
          "metadata": {
            "context_blocker": null,
            "context_pass": true,
            "context_score": 0.6,
            "futures_impulse_score": 0.0,
            "min_score": 0.62,
            "option_confirmation_score": 0.45,
            "pullback_resume_score": 0.1,
            "reason": "score_below_threshold",
            "regime": "LOWVOL",
            "score": 0.2325
          }
        },
        "reason": "score_below_threshold",
        "score": 0.0
      },
      {
        "action": "HOLD",
        "blocker": {},
        "branch_id": "PUT",
        "candidate": {},
        "family_id": "MIST",
        "is_blocked": false,
        "is_candidate": false,
        "is_no_signal": true,
        "priority": 0.0,
        "raw": {
          "action": "HOLD",
          "blocker": null,
          "branch_id": "PUT",
          "candidate": null,
          "doctrine_id": "MIST",
          "family_id": "MIST",
          "is_blocked": false,
          "is_candidate": false,
          "is_no_signal": true,
          "metadata": {
            "context_blocker": null,
            "context_pass": true,
            "context_score": 0.6,
            "futures_impulse_score": 0.0,
            "min_score": 0.62,
            "option_confirmation_score": 0.0,
            "pullback_resume_score": 0.1,
            "reason": "score_below_threshold",
            "regime": "LOWVOL",
            "score": 0.12
          }
        },
        "reason": "score_below_threshold",
        "score": 0.0
      },
      {
        "action": "HOLD",
        "blocker": {},
        "branch_id": "CALL",
        "candidate": {},
        "family_id": "MISB",
        "is_blocked": false,
        "is_candidate": false,
        "is_no_signal": true,
        "priority": 0.0,
        "raw": {
          "action": "HOLD",
          "blocker": null,
          "branch_id": "CALL",
          "candidate": null,
          "doctrine_id": "MISB",
          "family_id": "MISB",
          "is_blocked": false,
          "is_candidate": false,
          "is_no_signal": true,
          "metadata": {
            "breakout_score": 0.004615384615384616,
            "context_blocker": null,
            "context_pass": true,
            "context_score": 0.62,
            "futures_bias_ok": true,
            "min_score": 0.64,
            "option_confirmation_score": 0.5,
            "reason": "score_below_threshold",
            "regime": "LOWVOL",
            "score": 0.35993846153846154
          }
        },
        "reason": "score_below_threshold",
        "score": 0.0
      },
      {
        "action": "HOLD",
        "blocker": {},
        "branch_id": "PUT",
        "candidate": {},
        "family_id": "MISB",
        "is_blocked": false,
        "is_candidate": false,
        "is_no_signal": true,
        "priority": 0.0,
        "raw": {
          "action": "HOLD",
          "blocker": null,
          "branch_id": "PUT",
          "candidate": null,
          "doctrine_id": "MISB",
          "family_id": "MISB",
          "is_blocked": false,
          "is_candidate": false,
          "is_no_signal": true,
          "metadata": {
            "breakout_score": 0.004615384615384616,
            "context_blocker": null,
            "context_pass": true,
            "context_score": 0.62,
            "futures_bias_ok": true,
            "min_score": 0.64,
            "option_confirmation_score": 0.0,
            "reason": "score_below_threshold",
            "regime": "LOWVOL",
            "score": 0.19493846153846156
          }
        },
        "reason": "score_below_threshold",
        "score": 0.0
      },
      {
        "action": "HOLD",
        "blocker": {},
        "branch_id": "CALL",
        "candidate": {},
        "family_id": "MISC",
        "is_blocked": false,
        "is_candidate": false,
        "is_no_signal": true,
        "priority": 0.0,
        "raw": {
          "action": "HOLD",
          "blocker": null,
          "branch_id": "CALL",
          "candidate": null,
          "doctrine_id": "MISC",
          "family_id": "MISC",
          "is_blocked": false,
          "is_candidate": false,
          "is_no_signal": true,
          "metadata": {
            "reason": "directional_breakout_not_confirmed"
          }
        },
        "reason": "directional_breakout_not_confirmed",
        "score": 0.0
      }
    ],
    "activation_report_reason": "no_candidate",
    "data_valid": 1,
    "id": "1780462155264-0",
    "provider_ready_classic": 1,
    "reason": "hold_only_family_features_consumer_bridge",
    "safe_to_consume": 1
  },
  {
    "activation_candidate_count": 0,
    "activation_reason": "no_candidate",
    "activation_report_candidates_len": 0,
    "activation_report_no_signal_first_5": [
      {
        "action": "HOLD",
        "blocker": {},
        "branch_id": "CALL",
        "can
```

## Next route
- If classic_runtime_disabled is gone, continue observe-only capture and classify real blockers/no-signal.
- If classic_runtime_disabled remains despite process env, next is tiny gate patch-plan only.
- Paper remains blocked.