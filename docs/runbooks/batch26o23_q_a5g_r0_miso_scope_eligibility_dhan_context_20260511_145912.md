# batch26o23_q_a5g_r0_miso_scope_eligibility_dhan_context_20260511_145912 Runbook

Lane A5G MISO scope eligibility and Dhan-context inspection.

This batch does not patch source, start services, start risk/execution, enable paper, enable real live, call broker, place orders, or write Redis trading streams.

Rules:
- MISO CALL may proceed only if matrix-eligible and safety is clean.
- MISO PUT may proceed only if matrix-eligible and Dhan context current/fresh is proven.
- No MISO contract is written in R0.

Proof:
- run/proofs/proof_batch26o23_q_a5g_r0_miso_scope_eligibility_dhan_context.json
- run/proofs/proof_batch26o23_q_a5g_r0_miso_scope_eligibility_dhan_context_latest.json
