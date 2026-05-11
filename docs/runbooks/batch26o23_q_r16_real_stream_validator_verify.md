# 26-O23-Q-R16 — real stream-field validator / payload_json verify

Final verdict: `PASS_O23_Q_R16_REAL_STREAM_VALIDATOR_PAYLOAD_JSON_PROJECTION_VERIFIED`

This batch verifies `StrategyService.publish_decision` using the real `_redis_stream_fields` and real `_validate_decision_stream_fields` path, with fake Redis and an exact HOLD-only off-market fixture.

It does not patch source, start services, write orders, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_precheck.json`
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_exact_decision_fixture.json`
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_helper_signature_audit.json`
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_real_publish_verify.json`
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r16_real_stream_validator_verify_20260510_193519/o23q_r16_final_summary.json`
- `run/proofs/proof_batch26o23_q_r16_real_stream_validator_verify.json`
- `run/proofs/proof_batch26o23_q_r16_real_stream_validator_verify_latest.json`

Next:
26-O23-Q-R17 off-market one-shot strategy publish fixture against temporary Redis key namespace; no service start, no paper/live, no orders stream growth.
