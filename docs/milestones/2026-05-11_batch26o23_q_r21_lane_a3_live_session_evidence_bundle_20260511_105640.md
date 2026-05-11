# batch26o23_q_r21_lane_a3_live_session_evidence_bundle_20260511_105640

Lane: A3 — Live Observe-Only Field Capture

Verdict: `BLOCKED_O23_Q_R21_EVIDENCE_BUNDLE_INCOMPLETE`

Next batch: `resolve blockers before any downstream use; no paper/live`

This is live-session evidence bundling only, not after-market patch work.

Safety:
- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_order_path_attempted: false
- controlled_paper_status: BLOCKED_NO_EVIDENCE_BACKED_SCOPE
- real_live_status: BLOCKED
- current_safety_ok: True
- orders_len_now: 0
- position_flat_now: True
- runtime_no_risk_execution_pids_now: True

Q-R20/R2:
- q_r20_r2_pass: False
- q_r20_canonical_pass: False
- canonical_corrected_by_r2: True
- decision_field_pass: True
- stream_growth_pass: True
- raw_parser_pass: True
- safety_pass: True

Decision field counts:
- rows_total_analyzed: 209
- rows_with_family_scope_candidates_json: 209
- rows_with_activation_report_json: 209
- rows_with_payload_json: 209
- rows_family_scope_candidates_parse_ok: 209
- rows_schema_ok: 209
- projection_ok_rows: 209

Evidence bundle:
- archive: run/evidence_bundles/batch26o23_q_r21_lane_a3_live_session_evidence_bundle_20260511_105640.tar.gz
- sha256: run/evidence_bundles/batch26o23_q_r21_lane_a3_live_session_evidence_bundle_20260511_105640.tar.gz.sha256
- summary: run/evidence_bundles/batch26o23_q_r21_lane_a3_live_session_evidence_bundle_20260511_105640/bundle_summary.json
- manifest: run/evidence_bundles/batch26o23_q_r21_lane_a3_live_session_evidence_bundle_20260511_105640/bundle_manifest.json

Blockers:
- Q_R20_R2_PASS_NOT_CONFIRMED
- CANONICAL_Q_R20_PASS_NOT_CONFIRMED
