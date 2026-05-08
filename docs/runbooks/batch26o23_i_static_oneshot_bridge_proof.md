# 26-O23-I — static / one-shot bridge proof after O23-H

- generated_at_utc: 2026-05-07T08:49:54.520458+00:00
- proof: `run/proofs/proof_batch26o23_i_static_oneshot_bridge_proof.json`
- static_proof: `run/live_capture/batch26o23_i_static_oneshot_bridge_proof_20260507_141953/controlled_paper_o23i_static_bridge_proof.json`
- oneshot_proof: `run/live_capture/batch26o23_i_static_oneshot_bridge_proof_20260507_141953/controlled_paper_o23i_oneshot_helper_matrix.json`
- diff_audit: `run/live_capture/batch26o23_i_static_oneshot_bridge_proof_20260507_141953/controlled_paper_o23i_o23h_diff_safety_audit.json`
- next_decision: `run/live_capture/batch26o23_i_static_oneshot_bridge_proof_20260507_141953/controlled_paper_o23i_next_decision.json`
- backup_dir: `run/_code_backups/batch26o23_i_static_oneshot_bridge_proof_20260507_141953`

## Purpose
- Prove O23-H bridge repair without starting services.
- Validate helper behavior with synthetic one-shot scenarios.
- Confirm no order write, no real live, no threshold relaxation, no forced candidate.

## One-shot proof
```json
{
  "all_helpers_present": true,
  "all_scenarios_passed": true,
  "helper_presence": {
    "_o23h_boolish": true,
    "_o23h_consumer_view_truth": true,
    "_o23h_find_consumer_view": true,
    "_o23h_jsonish": true,
    "_o23h_repair_hold_bridge_decision": true
  },
  "safety_assertions": {
    "no_scenario_changes_buy_action": true,
    "no_scenario_creates_positive_candidate": false,
    "repair_only_on_bridge_reason": true
  },
  "scenario_count": 5,
  "scenarios": [
    {
      "expectation": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "activation_reason": "no_candidate",
        "consumer_view_repair_reason": "O23H_PROMOTED_VALID_CONSUMER_VIEW",
        "consumer_view_repaired": true,
        "data_valid": true,
        "reason": "no_candidate",
        "safe_to_consume": true,
        "structural_valid": true
      },
      "input_decision": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "activation_reason": "hold_only_family_features_consumer_bridge",
        "data_valid": false,
        "reason": "hold_only_family_features_consumer_bridge",
        "safe_to_consume": true
      },
      "local_vars": {
        "consumer_view": {
          "data_valid": true,
          "safe_to_consume": true,
          "structural_valid": true
        }
      },
      "name": "valid_consumer_view_bridge_hold_no_candidate_promotes_validity_only",
      "ok": true,
      "output": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "activation_reason": "no_candidate",
        "consumer_view_repair_reason": "O23H_PROMOTED_VALID_CONSUMER_VIEW",
        "consumer_view_repaired": true,
        "data_valid": true,
        "reason": "no_candidate",
        "safe_to_consume": true,
        "structural_valid": true
      }
    },
    {
      "expectation": {
        "__unchanged__": true
      },
      "input_decision": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "data_valid": false,
        "reason": "hold_only_family_features_consumer_bridge"
      },
      "local_vars": {
        "consumer_view": {
          "data_valid": false,
          "safe_to_consume": true,
          "structural_valid": true
        }
      },
      "name": "invalid_consumer_view_does_not_promote",
      "ok": true,
      "output": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "data_valid": false,
        "reason": "hold_only_family_features_consumer_bridge"
      }
    },
    {
      "expectation": {
        "__unchanged__": true
      },
      "input_decision": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "data_valid": false,
        "reason": "no_candidate"
      },
      "local_vars": {
        "consumer_view": {
          "data_valid": true,
          "safe_to_consume": true,
          "structural_valid": true
        }
      },
      "name": "non_bridge_reason_unchanged",
      "ok": true,
      "output": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "data_valid": false,
        "reason": "no_candidate"
      }
    },
    {
      "expectation": {
        "__unchanged__": true
      },
      "input_decision": {
        "action": "BUY",
        "activation_candidate_count": 1,
        "data_valid": false,
        "reason": "hold_only_family_features_consumer_bridge"
      },
      "local_vars": {
        "consumer_view": {
          "data_valid": true,
          "safe_to_consume": true,
          "structural_valid": true
        }
      },
      "name": "entry_action_never_modified",
      "ok": true,
      "output": {
        "action": "BUY",
        "activation_candidate_count": 1,
        "data_valid": false,
        "reason": "hold_only_family_features_consumer_bridge"
      }
    },
    {
      "expectation": {
        "activation_candidate_count": 0,
        "activation_reason": "no_candidate",
        "consumer_view_repaired": true,
        "data_valid": true,
        "reason": "no_candidate",
        "safe_to_consume": true,
        "structural_valid": true
      },
      "input_decision": {
        "action": "HOLD",
        "activation_candidate_count": "0",
        "data_valid": 0,
        "reason": "hold_only_family_features_consumer_bridge"
      },
      "local_vars": {
        "feature_payload": {
          "consumer_view_json": "{\"data_valid\": \"true\", \"safe_to_consume\": \"1\", \"structural_valid\": \"yes\"}"
        }
      },
      "name": "json_encoded_consumer_view_supported",
      "ok": true,
      "output": {
        "action": "HOLD",
        "activation_candidate_count": 0,
        "activation_reason": "no_candidate",
        "consumer_view_repair_reason": "O23H_PROMOTED_VALID_CONSUMER_VIEW",
        "consumer_view_repaired": true,
        "data_valid": true,
        "reason": "no_candidate",
        "safe_to_consume": true,
        "structural_valid": true
      }
    }
  ]
}
```

## Verdict
- final_verdict: `FAIL_O23_I_STATIC_ONESHOT_BRIDGE_PROOF_NOT_PROVEN`
- false_keys: `['oneshot_no_positive_candidate_created']`
- next_recommended_batch: `Inspect false_keys; do not restart controlled paper.`

## Required verdicts
```json
{
  "broker_call_false": true,
  "compile_pass": true,
  "diff_audit_json_written": true,
  "execution_has_no_o23h_marker": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "no_controlled_pids_now": true,
  "o23h_pass_loaded": true,
  "o23h_patch_applied_or_already_present": true,
  "oneshot_all_helpers_present": true,
  "oneshot_all_scenarios_passed": true,
  "oneshot_no_buy_action_changed": true,
  "oneshot_no_positive_candidate_created": false,
  "oneshot_proof_json_written": true,
  "oneshot_repair_only_on_bridge_reason": true,
  "order_write_false": true,
  "orders_zero_now": true,
  "position_flat_now": true,
  "production_source_patch_false_in_this_batch": true,
  "real_live_approval_false": true,
  "risk_execution_not_running_now": true,
  "risk_has_no_o23h_marker": true,
  "service_start_false": true,
  "static_features_has_consumer_view": true,
  "static_features_has_validity_fields": true,
  "static_proof_json_written": true,
  "static_strategy_has_activation_candidate_count": true,
  "static_strategy_has_bridge_reason": true,
  "static_strategy_has_data_valid": true,
  "static_strategy_has_o23h_helper": true,
  "static_strategy_has_o23h_return_wrapper": true,
  "static_strategy_has_safe_to_consume": true,
  "static_strategy_has_structural_valid": true,
  "strategy_has_no_banned_intent_hits": true,
  "threshold_relaxation_false": true
}
```