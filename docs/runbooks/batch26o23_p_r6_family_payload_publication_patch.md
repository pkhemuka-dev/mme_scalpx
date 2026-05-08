# 26-O23-P-R6 — minimal feature stream family payload publication patch

- generated_at_utc: `2026-05-08T07:05:21.086202+00:00`
- final_verdict: `FAIL_O23_P_R6_FAMILY_PAYLOAD_PUBLICATION_PATCH_NOT_PROVEN`
- false_keys: `['manifest_written', 'milestone_written', 'patch_applied_or_already_present', 'proof_written', 'runbook_written', 'summary_written']`
- latest_r5: `run/proofs/proof_batch26o23_p_r5_exact_line_family_payload_audit_latest.json`
- r5_likely_gap: `EXPECTED_KEYS_EXIST_IN_SOURCE_BUT_NOT_ON_ACTIVE_RUNTIME_PUBLICATION_PATH`
- patch_applied: `False`
- already_present: `False`
- patch_blocked: `True`
- patched_file: `app/mme_scalpx/services/features.py`
- patch_diff: `run/live_capture/batch26o23_p_r6_family_payload_publication_patch_20260508_123521/o23p_r6_applied_family_payload_publication.diff`
- compile_ok: `True`
- import_ok: `True`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- runtime_no_risk_execution_pids: `True`
- no service start / no paper / no real-live / no broker call / no order write: `True`
- next_recommended_batch: `Inspect false_keys and source inspection; do not run services until patch compiles and imports cleanly.`

## Artifacts
- proof: `run/proofs/proof_batch26o23_p_r6_family_payload_publication_patch.json`
- latest_proof: `run/proofs/proof_batch26o23_p_r6_family_payload_publication_patch_latest.json`
- source_inspection: `run/live_capture/batch26o23_p_r6_family_payload_publication_patch_20260508_123521/o23p_r6_source_inspection.json`
- patch_diff: `run/live_capture/batch26o23_p_r6_family_payload_publication_patch_20260508_123521/o23p_r6_applied_family_payload_publication.diff`
- safety: `run/live_capture/batch26o23_p_r6_family_payload_publication_patch_20260508_123521/o23p_r6_runtime_safety_readback.json`
