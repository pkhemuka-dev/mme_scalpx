# A6-R0 — Lane A proof reconciliation / canonical blocker classification / no order / no broker call

Generated IST: `2026-05-11T22:30:30.046327+05:30`

## Verdict

`BLOCKED_A6_R0_CANONICAL_BLOCKER_CLASSIFIED_NO_ORDER_NO_BROKER`

## Canonical blocker

- canonical_blocker: `EXPLICIT_CONTROLLED_PAPER_ORDER_TOOL_NOT_FOUND_FAIL_CLOSED`
- canonical_blocker_class: `MISSING_EXPLICIT_CONTROLLED_PAPER_SANDBOX_ORDER_ROUTE`
- blocker_scope: `Lane A5H / MISB CALL one controlled-paper order-cycle`
- conflict_resolution: Canonical Lane A6 blocker is the missing explicit controlled-paper/sandbox order-cycle route. MARKET_WINDOW_NOT_OPEN belongs to a separate MISR CALL attempt; SCOPE_SIGNAL_NOT_PRESENT belongs to natural no-signal windows and does not resolve the route gap.

## Safety

- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- order_attempted: false
- order_created: false
- order_sent: false
- broker_calls_executed: false
- redis_trading_stream_write_attempted: false
- current_safety_ok: `True`
- orders_xlen_after: `0`
- orders_growth_2s: `0`
- position_flat: `True`
- risk_execution_pids: `0`

## Evidence classes found

- route_evidence_count: `1`
- market_window_evidence_count: `1`
- scope_signal_absence_evidence_count: `2`
- proof_shape_evidence_count: `1`

## Next batch

`A6-R1 controlled-paper order-cycle route audit / no order / no broker call`

Do not patch runtime from A6-R0. A6-R1 must inspect complete route source and producer/consumer ownership before any patch plan is accepted.

## Artifacts

- proof: `run/proofs/proof_lane_a6_r0_proof_reconciliation_20260511_223030.json`
- latest proof: `run/proofs/proof_lane_a6_r0_proof_reconciliation_latest.json`
- runbook: `docs/runbooks/lane_a6_r0_proof_reconciliation_20260511_223030_next_route_audit_runbook.md`
