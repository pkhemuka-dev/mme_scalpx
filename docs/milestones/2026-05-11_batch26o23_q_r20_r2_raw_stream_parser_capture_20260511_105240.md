# batch26o23_q_r20_r2_raw_stream_parser_capture_20260511_105240

Lane: A3 — Live Observe-Only Field Capture

Verdict: `PASS_O23_Q_R20_LIVE_SESSION_OBSERVE_ONLY_DECISION_FIELD_CAPTURE`

Next batch: `26-O23-Q-R21 A3 live-session evidence bundle`

Safety:
- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_order_path_attempted: false
- controlled_paper_status: BLOCKED_NO_EVIDENCE_BACKED_SCOPE
- real_live_status: BLOCKED
- orders_zero: True
- orders_growth: 0
- position_flat: True
- runtime_no_risk_execution_pids: True

Market:
- now_ist: 2026-05-11T10:52:40.295540+05:30
- market_session_window_ok: True

Streams:
- features_growth: 25
- decisions_growth: 202
- raw_parser_ok: True
- new_decision_entries_seen: True

Decision field proof:
- rows_total_analyzed: 202
- rows_with_family_scope_candidates_json: 202
- rows_with_activation_report_json: 202
- rows_with_payload_json: 202
- rows_family_scope_candidates_parse_ok: 202
- rows_schema_ok: 202
- projection_ok_rows: 202
- expected_schema: o23q_family_scope_candidates_v1

Artifacts:
- r2_proof: run/proofs/proof_batch26o23_q_r20_r2_raw_stream_parser_capture.json
- r2_latest: run/proofs/proof_batch26o23_q_r20_r2_raw_stream_parser_capture_latest.json
- timestamped: run/proofs/proof_batch26o23_q_r20_r2_raw_stream_parser_capture_20260511_105240.json
- capture_sample: run/live_observe/a3/captures/batch26o23_q_r20_r2_raw_stream_parser_capture_20260511_105240_raw_decision_capture_sample.json
- canonical_q_r20_promoted: True

Blockers:
- none
