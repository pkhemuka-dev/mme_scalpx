# LANE-X-R34K-R1_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER_prove_r34k_helper_extracts_symbol_token_from_selected_and_view_without_service_start_20260613_133256

classification: PASS_R34K_R1_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34K-R1_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER_prove_r34k_helper_extracts_symbol_token_from_selected_and_view_without_service_start_20260613_133256.json`
summary: `run/audits/LANE-X-R34K-R1_IDENTITY_SOURCE_SMOKE_NO_PATCH_NO_REPLAY_NO_ORDER_prove_r34k_helper_extracts_symbol_token_from_selected_and_view_without_service_start_20260613_133256/r34k_r1_smoke_summary.json`

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
    "direct_enter_true": true,
    "direct_symbol": true,
    "direct_token": true,
    "hold_not_exported": true,
    "view_enter_true": true,
    "view_symbol": true,
    "view_token": true
  },
  "direct_result": {
    "broker_calls_executed_shadow": 0,
    "candidate_action_shadow": "ENTER_CALL",
    "candidate_branch_id_shadow": "MIST_CALL_TEST",
    "candidate_family_id_shadow": "MIST",
    "candidate_instrument_token_shadow": "123456",
    "candidate_present_shadow": 1,
    "candidate_score_shadow": 0.88,
    "candidate_shadow_only": 1,
    "candidate_symbol_shadow": "NIFTY26JUN25000CE",
    "candidate_true_shadow": 1,
    "candidate_truth_mode_shadow": "activation_selected_report_only_shadow",
    "instrument_token": "123456",
    "real_order_sent_shadow": 0,
    "redis_trading_stream_write_attempted_shadow": 0,
    "symbol": "NIFTY26JUN25000CE"
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
  "view_result": {
    "broker_calls_executed_shadow": 0,
    "candidate_action_shadow": "ENTER_PUT",
    "candidate_branch_id_shadow": "MIST_PUT_TEST",
    "candidate_family_id_shadow": "MIST",
    "candidate_instrument_token_shadow": "654321",
    "candidate_present_shadow": 1,
    "candidate_score_shadow": 0.77,
    "candidate_shadow_only": 1,
    "candidate_symbol_shadow": "NIFTY26JUN25000PE",
    "candidate_true_shadow": 1,
    "candidate_truth_mode_shadow": "activation_selected_report_only_shadow",
    "instrument_token": "654321",
    "real_order_sent_shadow": 0,
    "redis_trading_stream_write_attempted_shadow": 0,
    "symbol": "NIFTY26JUN25000PE"
  }
}