# 26-O23-Q-R17 — temp Redis namespace one-shot publish verify

Final verdict: `PASS_O23_Q_R17_TEMP_REDIS_NAMESPACE_PUBLISH_VERIFIED_NO_PROD_STREAM_GROWTH`

This batch monkeypatches only the in-memory `STREAM_DECISIONS` module constant to a temporary Redis stream key, calls `StrategyService.publish_decision` once with a HOLD-only fixture, reads back the temp stream, verifies `family_scope_candidates_json`, and deletes the temp key.

It does not patch source, start services, write to production decisions stream, write to orders stream, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r17_temp_redis_publish_verify_20260510_193800/o23q_r17_precheck.json`
- `run/live_capture/batch26o23_q_r17_temp_redis_publish_verify_20260510_193800/o23q_r17_helper_signature_audit.json`
- `run/live_capture/batch26o23_q_r17_temp_redis_publish_verify_20260510_193800/o23q_r17_temp_redis_publish_verify.json`
- `run/live_capture/batch26o23_q_r17_temp_redis_publish_verify_20260510_193800/o23q_r17_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r17_temp_redis_publish_verify_20260510_193800/o23q_r17_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r17_temp_redis_publish_verify_20260510_193800/o23q_r17_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r17_temp_redis_publish_verify_20260510_193800/o23q_r17_final_summary.json`
- `run/proofs/proof_batch26o23_q_r17_temp_redis_publish_verify.json`
- `run/proofs/proof_batch26o23_q_r17_temp_redis_publish_verify_latest.json`

Next:
26-O23-Q-R18 after-market closeout bundle for Q-R13 through Q-R17; no source patch, no service start, no paper/live.
