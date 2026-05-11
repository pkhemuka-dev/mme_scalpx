# batch26o23_q_a5h_r0_misr_scope_eligibility_selector_20260511_151748 Runbook

Lane A5H MISR scope eligibility and selector.

This batch does not patch source, start services, start risk/execution, enable paper, enable real live, call broker, place orders, or write Redis trading streams.

Rules:
- MISR CALL is preferred first if matrix-eligible.
- MISR PUT may be selected only if CALL is unavailable and PUT is matrix-eligible.
- No MISR contract is written in R0.

Proof:
- run/proofs/proof_batch26o23_q_a5h_r0_misr_scope_eligibility_selector.json
- run/proofs/proof_batch26o23_q_a5h_r0_misr_scope_eligibility_selector_latest.json
