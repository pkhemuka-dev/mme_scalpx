# batch26o23_q_a5a_r1_r1_corrected_controlled_paper_enablement_contract_20260511_115915

Lane: A5A — Controlled Paper Enablement Contract / No Broker Call

Verdict: `PASS_A5A_R1_R1_CONTROLLED_PAPER_ENABLEMENT_CONTRACT_NO_ORDER_NO_BROKER_CALL`

Next batch: `26-O23-Q-A5A-R2 explicit approval phrase and controlled-paper governance checklist / no enablement`

Contract output:
- controlled_paper_contract_scope: MIST_CALL_ONLY
- controlled_paper_qty_cap: 1_LOT_ONLY
- paper_route_only: true
- real_live_forbidden: true
- broker_failover_forbidden: true
- mid_position_provider_migration_forbidden: true
- require_flat_position_before_entry: true
- require_orders_zero_before_entry: true
- require_explicit_user_approval_phrase: true
- approval phrase exact: `I APPROVE CONTROLLED PAPER: MIST CALL ONLY, 1 LOT ONLY, PAPER/SANDBOX ONLY, REAL LIVE FORBIDDEN, NO BROKER FAILOVER, NO MID-POSITION PROVIDER MIGRATION`

Safety:
- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_call_attempted: false
- order_placement_attempted: false
- redis_trading_stream_write_attempted: false
- controlled_paper_status: BLOCKED_PENDING_A5A_R2_A5B_PREFLIGHT_AND_EXPLICIT_USER_APPROVAL
- real_live_status: BLOCKED
- orders_zero_before: True
- orders_zero_after: True
- orders_no_growth: True
- position_flat_before: True
- position_flat_after: True
- runtime_no_risk_execution_pids: True

Artifacts:
- contract: docs/contracts/a5a_controlled_paper_enablement_contract_v1.json
- timestamped contract: docs/contracts/a5a_controlled_paper_enablement_contract_v1_20260511_115915.json
- proof: run/proofs/proof_batch26o23_q_a5a_r1_r1_controlled_paper_enablement_contract.json
- latest proof: run/proofs/proof_batch26o23_q_a5a_r1_r1_controlled_paper_enablement_contract_latest.json

Blockers:
- none
