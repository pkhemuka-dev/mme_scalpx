# 26-O20-R3G — corrected R3E proof parser only

- generated_at_utc: 2026-05-06T06:46:43.979297+00:00
- tag: `batch26o20_r3g_corrected_r3e_proof_parser_20260506_121639`
- proof: `run/proofs/proof_batch26o20_r3g_corrected_r3e_proof_parser.json`
- manifest: `run/proofs/manifest_batch26o20_r3g_corrected_r3e_proof_parser.json`
- corrected_report: `run/live_capture/batch26o20_r3g_corrected_r3e_proof_parser_20260506_121639/corrected_r3e_equivalent_report.json`
- backup_dir: `run/_code_backups/batch26o20_r3g_corrected_r3e_proof_parser_20260506_121639`

## Evidence
- R3F classified the R3E failure as a proof-parser gap.
- Latest persisted feature entries contain expected branch frames under `consumer_view_json`; R3E parser looked in insufficient locations.

## Corrected parser law
- Structural validity is proven by all 10 expected branch frames plus MIST CALL visibility.
- `data_valid` and `safe_to_consume` are data/provider validity semantics and are not forced or reclassified as true.
- No production source patch is applied in this batch.

## Safety
- No real live.
- No paper start.
- No broker call.
- No order write.
- No threshold relaxation.
- No forced candidate.
- Risk/execution not started.

## Verdict
- final_verdict: `PASS_O20_R3G_CORRECTED_R3E_PROOF_PARSER_OK_HOLD_ONLY`
- false_keys: `[]`
- next_recommended_batch: `26-O20-R3H current-frame corrected bounded observation with corrected parser; no source patch, no real live.`

## Required verdicts
```json
{
  "all_10_branch_frames_present_corrected": true,
  "compile_pass": true,
  "consumer_view_present": true,
  "corrected_structural_shape_ok": true,
  "data_valid_semantics_observed_not_forced": true,
  "decision_samples_present": true,
  "decisions_hold_no_candidate": true,
  "execution_not_running": true,
  "features_samples_present": true,
  "import_pass": true,
  "mist_call_visible_corrected": true,
  "no_broker_call": true,
  "no_forced_candidate": true,
  "no_order_write_intent": true,
  "no_paper_start": true,
  "no_threshold_relaxation": true,
  "orders_zero": true,
  "position_flat": true,
  "production_source_patch_false": true,
  "proof_parser_only": true,
  "r3f_classified_proof_parser_gap": true,
  "r3f_latest_branch_ok": true,
  "r3f_latest_mist_call": true,
  "r3f_pass_loaded": true,
  "r3f_recommended_r3g_parser_only": true,
  "real_live_false": true,
  "risk_not_running": true,
  "safe_to_consume_semantics_observed_not_forced": true
}
```