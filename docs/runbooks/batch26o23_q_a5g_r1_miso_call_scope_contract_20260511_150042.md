# batch26o23_q_a5g_r1_miso_call_scope_contract_20260511_150042 Runbook

Lane A5G MISO CALL controlled-paper scope contract.

This batch only freezes the A5G selected-scope contract.
It does not start services, start risk/execution, enable paper, enable real live, call broker, place orders, patch source, or write Redis trading streams.

Controlled paper remains blocked until:
1. A5G-R1 PASS
2. A5G-R2 preflight PASS
3. User types exact A5G MISO CALL approval phrase after A5G-R2

Exact A5G approval phrase:

`I APPROVE CONTROLLED PAPER: MISO CALL ONLY, 1 LOT ONLY, PAPER/SANDBOX ONLY, REAL LIVE FORBIDDEN, NO BROKER FAILOVER, NO MID-POSITION PROVIDER MIGRATION`

Proof:
- run/proofs/proof_batch26o23_q_a5g_r1_miso_call_scope_contract.json
- run/proofs/proof_batch26o23_q_a5g_r1_miso_call_scope_contract_latest.json
