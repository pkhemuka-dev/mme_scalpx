# batch26o23_q_a5g_r1_miso_call_scope_contract_20260511_150042

Lane: A5G — MISO CALL Controlled-Paper Scope Contract

Verdict: `PASS_A5G_R1_MISO_CALL_CONTROLLED_PAPER_SCOPE_CONTRACT_NO_ORDER_NO_BROKER_CALL`

Next batch: `26-O23-Q-A5G-R2 MISO CALL controlled-paper preflight / no order / no broker call`

Selected A5G contract scope:
- family: MISO
- side: CALL
- qty: 1 lot only
- paper/sandbox route only
- real live forbidden
- broker failover forbidden
- mid-position provider migration forbidden
- no automatic strategy switching
- no all-5 order cycle
- no forced candidate
- no threshold relaxation

MISO boundary:
- MISO CALL selected because matrix-eligible.
- MISO PUT remains forbidden unless Dhan context current/fresh is separately proven.
- A5G-R0 MISO PUT block reason: `MISO_DHAN_CONTEXT_NOT_OBSERVED`

Approval:
- Prior lane approvals are not valid for A5G.
- A5G requires exact fresh approval phrase after A5G-R2:
`I APPROVE CONTROLLED PAPER: MISO CALL ONLY, 1 LOT ONLY, PAPER/SANDBOX ONLY, REAL LIVE FORBIDDEN, NO BROKER FAILOVER, NO MID-POSITION PROVIDER MIGRATION`

Safety:
- source_patch_applied: false
- contract_written: true
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_call_attempted: false
- order_attempted: false
- redis_trading_stream_write_attempted: false
- orders_zero_before: True
- orders_zero_after: True
- orders_no_growth: True
- position_flat_after: True
- runtime_no_risk_execution_pids: True

Artifacts:
- contract: docs/contracts/a5g_miso_call_controlled_paper_scope_contract_v1.json
- timestamped_contract: docs/contracts/a5g_miso_call_controlled_paper_scope_contract_v1_150042.json
- proof: run/proofs/proof_batch26o23_q_a5g_r1_miso_call_scope_contract.json
- latest: run/proofs/proof_batch26o23_q_a5g_r1_miso_call_scope_contract_latest.json

Blockers:
- none
