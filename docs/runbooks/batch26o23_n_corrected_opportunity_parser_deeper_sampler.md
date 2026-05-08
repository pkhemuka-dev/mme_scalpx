# 26-O23-N — corrected opportunity parser / deeper read-only sampler

- generated_at_utc: 2026-05-07T09:27:43.058747+00:00
- proof: `run/proofs/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.json`
- corrected_ranking: `run/live_capture/batch26o23_n_corrected_opportunity_parser_deeper_sampler_20260507_145733/controlled_paper_o23n_corrected_opportunity_ranking.json`
- deep_surface: `run/live_capture/batch26o23_n_corrected_opportunity_parser_deeper_sampler_20260507_145733/controlled_paper_o23n_deep_surface_sampler.json`
- o23l_bug_audit: `run/live_capture/batch26o23_n_corrected_opportunity_parser_deeper_sampler_20260507_145733/controlled_paper_o23n_o23l_ranking_bug_audit.json`
- next_decision: `run/live_capture/batch26o23_n_corrected_opportunity_parser_deeper_sampler_20260507_145733/controlled_paper_o23n_next_decision.json`

## Scope
- Correct parser/ranking law only.
- Read-only deep sampler.
- No service start.
- No paper start.
- No real live.
- No threshold relaxation.
- No forced candidate.

## Correction law
- `NO_SURFACE_SEEN` can never be selected for next paper scope.
- `surface_seen=True` and `hit_count>0` are mandatory.
- MISO remains penalized until Dhan context freshness is proven.

## Result
- final_verdict: `PASS_O23_N_CORRECTED_OPPORTUNITY_PARSER_OK_NO_START_NO_REAL_LIVE`
- classification: `O23N_NO_EVIDENCE_BACKED_SCOPE_IN_CURRENT_REDIS_HISTORY`
- false_keys: `[]`
- best_evidence_backed_scope: `None`
- next_recommended_batch: `26-O23-O live-session read-only family-surface materialization sampler; no paper start, no real live.`

## Required verdicts
```json
{
  "best_scope_if_any_is_evidence_backed": true,
  "broker_call_false": true,
  "compile_pass": true,
  "corrected_ranking_json_written": true,
  "deep_surface_json_written": true,
  "family_side_matrix_complete": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "o23j_pass_loaded": true,
  "o23k_pass_loaded": true,
  "o23l_bug_audit_json_written": true,
  "o23l_no_surface_bug_classified": true,
  "o23l_pass_loaded": true,
  "o23m_pass_loaded": true,
  "order_write_false": true,
  "paper_start_false": true,
  "production_source_patch_false": true,
  "ranking_correction_law_present": true,
  "real_live_false": true,
  "runtime_no_controlled_pids": true,
  "runtime_orders_zero": true,
  "runtime_position_flat": true,
  "runtime_risk_execution_not_running": true,
  "service_start_false": true,
  "threshold_relaxation_false": true
}
```