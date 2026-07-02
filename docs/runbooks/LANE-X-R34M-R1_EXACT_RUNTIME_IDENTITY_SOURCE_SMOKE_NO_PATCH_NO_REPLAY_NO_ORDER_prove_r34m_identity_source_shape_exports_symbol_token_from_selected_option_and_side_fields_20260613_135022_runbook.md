# LANE-X-R34M-R1_EXACT_RUNTIME_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER_prove_r34m_identity_source_shape_exports_symbol_token_from_selected_option_and_side_fields_20260613_135022

classification: PASS_R34M_R1_EXACT_RUNTIME_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34M-R1_EXACT_RUNTIME_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER_prove_r34m_identity_source_shape_exports_symbol_token_from_selected_option_and_side_fields_20260613_135022.json`
summary: `run/audits/LANE-X-R34M-R1_EXACT_RUNTIME_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER_prove_r34m_identity_source_shape_exports_symbol_token_from_selected_option_and_side_fields_20260613_135022/r34m_r1_smoke_summary.json`

## RCs
- compile_rc: 0
- smoke_rc: 0

## Safety
- pre orders/risk/execution: 0 / 0 / 0
- post orders/risk/execution: 0 / 0 / 0
- post risk/execution proc: 0 / 0

## Smoke output
{
  "checks": {
    "broker_zero": true,
    "hold_not_exported": true,
    "selected_option_enter_true": true,
    "selected_option_symbol_exported": true,
    "selected_option_token_exported": true,
    "side_specific_enter_true": true,
    "side_specific_symbol_exported": true,
    "side_specific_token_exported": true
  },
  "hold_result": {
    "broker_calls_executed_shadow": 0,
    "candidate_action_shadow": "",
    "candidate_branch_id_shadow": "",
    "candidate_family_id_shadow": "",
    "candidate_instrument_token_shadow": "",
    "candidate_present_shadow": 0,
    "candidate_score_shadow": null,
    "candidate_shadow_only": 0,
    "candidate_symbol_shadow": "",
    "candidate_true_shadow": 0,
    "candidate_truth_mode_shadow": "",
    "instrument_token": "",
    "real_order_sent_shadow": 0,
    "redis_trading_stream_write_attempted_shadow": 0,
    "symbol": ""
  },
  "ok": true,
  "selected_option_result": {
    "broker_calls_executed_shadow": 0,
    "candidate_action_shadow": "ENTER_CALL",
    "candidate_branch_id_shadow": "MIST_CALL_R34M",
    "candidate_family_id_shadow": "MIST",
    "candidate_instrument_token_shadow": "111222",
    "candidate_present_shadow": 1,
    "candidate_score_shadow": 0.91,
    "candidate_shadow_only": 1,
    "candidate_symbol_shadow": "NIFTY26JUN25000CE",
    "candidate_true_shadow": 1,
    "candidate_truth_mode_shadow": "activation_selected_report_only_shadow",
    "instrument_token": "111222",
    "real_order_sent_shadow": 0,
    "redis_trading_stream_write_attempted_shadow": 0,
    "symbol": "NIFTY26JUN25000CE"
  },
  "side_specific_result": {
    "broker_calls_executed_shadow": 0,
    "candidate_action_shadow": "ENTER_PUT",
    "candidate_branch_id_shadow": "MIST_PUT_R34M",
    "candidate_family_id_shadow": "MIST",
    "candidate_instrument_token_shadow": "333444",
    "candidate_present_shadow": 1,
    "candidate_score_shadow": 0.89,
    "candidate_shadow_only": 1,
    "candidate_symbol_shadow": "NIFTY26JUN25000PE",
    "candidate_true_shadow": 1,
    "candidate_truth_mode_shadow": "activation_selected_report_only_shadow",
    "instrument_token": "333444",
    "real_order_sent_shadow": 0,
    "redis_trading_stream_write_attempted_shadow": 0,
    "symbol": "NIFTY26JUN25000PE"
  }
}