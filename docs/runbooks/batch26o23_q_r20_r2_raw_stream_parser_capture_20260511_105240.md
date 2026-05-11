# batch26o23_q_r20_r2_raw_stream_parser_capture_20260511_105240 Runbook

This is a Lane A3 live-session corrected raw Redis stream parser capture.

It does not patch source, does not start services, does not start risk/execution, does not enable paper, does not enable real live, and does not use broker order path.

It corrects the prior Q-R20 harness failure where stream growth existed but analyzed rows were zero.

Proof:
- run/proofs/proof_batch26o23_q_r20_r2_raw_stream_parser_capture.json
- run/proofs/proof_batch26o23_q_r20_r2_raw_stream_parser_capture_latest.json
- run/proofs/proof_batch26o23_q_r20_r2_raw_stream_parser_capture_20260511_105240.json
