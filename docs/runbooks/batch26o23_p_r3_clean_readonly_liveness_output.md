# 26-O23-P-R3 — clean read-only service liveness/output rerun

- generated_at_utc: `2026-05-08T06:34:40.218876+00:00`
- final_verdict: `FAIL_O23_P_R3_CLEAN_READONLY_SERVICE_DIAGNOSTIC_NOT_PROVEN`
- false_keys: `['manifest_written', 'milestone_written', 'proof_written', 'runbook_written', 'summary_written']`
- service_output_status: `FEATURE_AND_DECISION_GROWTH_OBSERVED`
- services_started: `['feeds', 'features', 'strategy']`
- liveness_by_service: `{'feeds': True, 'features': True, 'strategy': True}`
- features_growth: `8`
- decisions_growth: `113`
- orders_growth: `0`
- feed_stream_growth: `{'fut_zerodha': 38, 'fut_dhan': 0, 'opt_selected_zerodha': 278, 'opt_selected_dhan': 0, 'opt_context_dhan': 0}`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids_after_stop: `True`
- runtime_no_risk_execution_pids_after_stop: `True`
- no paper / no real-live / no broker call / no order write / no source patch: `True`
- next_recommended_batch: `Inspect false_keys/service audit logs; do not advance.`

## Artifacts
- proof: `run/proofs/proof_batch26o23_p_r3_clean_readonly_liveness_output.json`
- latest_proof: `run/proofs/proof_batch26o23_p_r3_clean_readonly_liveness_output_latest.json`
- manifest: `run/live_capture/batch26o23_p_r3_clean_readonly_liveness_output_20260508_120440/manifest_batch26o23_p_r3_clean_readonly_liveness_output.json`
- service_audit: `run/live_capture/batch26o23_p_r3_clean_readonly_liveness_output_20260508_120440/o23p_r3_service_liveness_output_audit.json`
- safety: `run/live_capture/batch26o23_p_r3_clean_readonly_liveness_output_20260508_120440/o23p_r3_runtime_safety_readback.json`
