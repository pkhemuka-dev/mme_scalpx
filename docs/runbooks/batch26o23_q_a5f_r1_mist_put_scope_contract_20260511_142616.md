# batch26o23_q_a5f_r1_mist_put_scope_contract_20260511_142616 Runbook

Lane A5F MIST PUT controlled-paper scope contract.

This batch only freezes the A5F selected-scope contract.
It does not start services, start risk/execution, enable paper, enable real live, call broker, place orders, patch source, or write Redis trading streams.

Controlled paper remains blocked until:
1. A5F-R1 PASS
2. A5F-R2 preflight PASS
3. User types exact A5F MIST PUT approval phrase after A5F-R2

Exact A5F approval phrase:

`I APPROVE CONTROLLED PAPER: MIST PUT ONLY, 1 LOT ONLY, PAPER/SANDBOX ONLY, REAL LIVE FORBIDDEN, NO BROKER FAILOVER, NO MID-POSITION PROVIDER MIGRATION`

Proof:
- run/proofs/proof_batch26o23_q_a5f_r1_mist_put_scope_contract.json
- run/proofs/proof_batch26o23_q_a5f_r1_mist_put_scope_contract_latest.json
