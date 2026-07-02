# LANE-X-R34I_POINTS_FIRST_SHADOW_PNL_JOIN_DIAG_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_diagnose_candidate_to_pnl_join_from_r34g_shadow_and_confirm_identity_blocker_before_paper_gate_20260613_132430

classification: PASS_R34I_JOIN_DIAG_CONFIRMS_POINTS_PNL_BLOCKED_BY_SYMBOL_TOKEN_IDENTITY_NO_ORDER
proof: `run/proofs/LANE-X-R34I_POINTS_FIRST_SHADOW_PNL_JOIN_DIAG_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_diagnose_candidate_to_pnl_join_from_r34g_shadow_and_confirm_identity_blocker_before_paper_gate_20260613_132430.json`
summary: `run/audits/LANE-X-R34I_POINTS_FIRST_SHADOW_PNL_JOIN_DIAG_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_diagnose_candidate_to_pnl_join_from_r34g_shadow_and_confirm_identity_blocker_before_paper_gate_20260613_132430/r34i_join_diag_summary.json`
report: `run/audits/LANE-X-R34I_POINTS_FIRST_SHADOW_PNL_JOIN_DIAG_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_diagnose_candidate_to_pnl_join_from_r34g_shadow_and_confirm_identity_blocker_before_paper_gate_20260613_132430/r34i_join_diag_report.md`
identity_source_locator: `run/audits/LANE-X-R34I_POINTS_FIRST_SHADOW_PNL_JOIN_DIAG_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_diagnose_candidate_to_pnl_join_from_r34g_shadow_and_confirm_identity_blocker_before_paper_gate_20260613_132430/r34i_identity_source_locator.txt`

## Safety
pre orders/risk/execution: 0 / 0 / 0
post orders/risk/execution: 0 / 0 / 0
post risk/execution proc: 0 / 0

## Embedded report
# R34I points-first shadow PnL join diagnostic

classification: PASS_R34I_JOIN_DIAG_CONFIRMS_POINTS_PNL_BLOCKED_BY_SYMBOL_TOKEN_IDENTITY_NO_ORDER

latest_r34g_shadow: `run/audits/LANE-X-R34F-R0-R34F-R1-R34G_RECOVERY_PATCH_AND_OFFLINE_SHADOW_EXTRACTION_NO_REPLAY_NO_ORDER_recover_r34f_patch_strategy_shadow_candidate_truth_then_extract_friday_durable_shadow_candidates_20260613_122544/r34g_activation_selected_shadow_candidates.jsonl`


## Counts

- shadow_candidate_count: 7297
- family_counts: {'MIST': 7297}
- candidate_id_present/unique: 7297 / 7297
- family_present: 7297
- branch_present: 7297
- side_present: 7297
- symbol_or_token_present: 0
- joinable_for_trade_grade_pnl: 0

## PnL result

- points PnL is primary, but not computed because no stable instrument identity exists.
- percent PnL is secondary only and not computed.
- risk_shadow_count: 0
- execution_shadow_count: 0
- simulated_fill_count: 0

## Safety

- broker_calls_executed: 0
- real_order_sent: 0
- redis_trading_stream_write_attempted: 0
- future_leakage_used: False
- future_pnl_tiebreak_used: False

## Hard blockers

- symbol/token missing on shadow candidates; stable instrument join and trade-grade PnL are blocked.

## Next

Patch symbol/token identity export into shadow candidate truth, then rerun R34G/R34H/R34I before R34J.
