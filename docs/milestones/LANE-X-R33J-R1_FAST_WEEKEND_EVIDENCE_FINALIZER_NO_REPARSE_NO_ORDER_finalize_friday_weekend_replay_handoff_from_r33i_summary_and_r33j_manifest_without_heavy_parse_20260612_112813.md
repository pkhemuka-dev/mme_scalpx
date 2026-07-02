# LANE-X-R33J-R1_FAST_WEEKEND_EVIDENCE_FINALIZER_NO_REPARSE_NO_ORDER_finalize_friday_weekend_replay_handoff_from_r33i_summary_and_r33j_manifest_without_heavy_parse_20260612_112813

classification: PASS_R33J_R1_FAST_WEEKEND_EVIDENCE_FINALIZED_NO_ORDER

## Friday evidence status

The weekend evidence is now finalized without re-parsing the large durable tape.

## Primary durable tape

`run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture`

- durable_bytes: `848432584`
- durable_files: `13`
- decisions.jsonl.gz: `658887912`
- features.jsonl.gz: `89455502`

## Candidate / near-candidate evidence

- candidate_true_count: `0`
- score_positive_count: `83108`
- ENTER_PUT: `7446`
- ENTER_CALL: `5610`
- MIV_like_count: `0`

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Weekend work

Saturday/Sunday should use:
1. R33I bundle for quick candidate/blocker audit;
2. durable tape path for full replay;
3. evidence map and manifest for file integrity;
4. no broker order, no paper/live until replay/shadow result is clean.
