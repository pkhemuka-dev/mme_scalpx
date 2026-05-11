# 26-O23-Q-R14-R6 — exact HOLD-validator fixture projection verification

Final verdict: `PASS_O23_Q_R14_R6_EXACT_HOLD_FIXTURE_PROJECTION_VERIFIED`

This batch uses an exact synthetic decision fixture satisfying the frozen HOLD-only validator:
`action=HOLD`, `qty=0`, `hold_only=1`, `activation_report_only=1`,
`activation_action=HOLD`, `activation_promoted=0`,
`activation_safe_to_promote=0`, and `live_orders_allowed=0`.

It verifies that the Q-R13 `family_scope_candidates_json` projection is emitted on the publish path with fake Redis. It does not patch source, start services, write orders, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_precheck.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_exact_hold_fixture.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_hold_contract_validation.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_publish_projection_permissive_stream_validator.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_publish_projection_real_stream_validator_advisory.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r14_r6_exact_hold_fixture_verify_20260510_191356/o23q_r14_r6_final_summary.json`
- `run/proofs/proof_batch26o23_q_r14_r6_exact_hold_fixture_verify.json`
- `run/proofs/proof_batch26o23_q_r14_r6_exact_hold_fixture_verify_latest.json`

Next:
26-O23-Q-R15 source/consumer contract audit for family_scope_candidates_json; no paper/live, no risk/execution patch.
