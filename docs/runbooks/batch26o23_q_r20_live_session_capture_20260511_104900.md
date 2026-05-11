# batch26o23_q_r20_live_session_capture_20260511_104900 Runbook

This batch captures live-session observe-only decision stream fields only.

It verifies:
- family_scope_candidates_json exists
- activation_report_json exists
- payload_json exists
- family_scope_candidates_json parses
- schema == o23q_family_scope_candidates_v1
- projection_ok_rows > 0
- features/decisions streams grow
- orders:mme:stream remains zero
- state:position:mme remains flat
- risk/execution are not running

It does not patch source, does not start services, does not enable paper, does not enable real live, and does not use broker order path.

Proof:
- run/proofs/proof_batch26o23_q_r20_live_session_capture.json
- run/proofs/proof_batch26o23_q_r20_live_session_capture_latest.json
- run/proofs/proof_batch26o23_q_r20_live_session_capture_20260511_104900.json
