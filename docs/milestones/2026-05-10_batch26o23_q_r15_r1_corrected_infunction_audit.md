# 2026-05-10 — 26-O23-Q-R15-R1

Verdict: `FAIL_O23_Q_R15_R1_PRECHECK_BLOCKED`

## Purpose
Correct Q-R15 producer contract audit by checking ordering inside `StrategyService.publish_decision`, not by broad/global source-line ordering.

## Contract result
- status: `SKIPPED_PRECHECK_FAILED`
- producer_contract_ok: `None`
- runtime_consumer_count: `None`
- ast_runtime_consumer_candidate_count: `None`
- consumer_contract: `None`

## Corrected producer ordering
- hold_validate_before_redis_fields: `True`
- redis_fields_before_stream_validate: `True`
- stream_validate_before_projection: `True`
- projection_before_xadd: `True`

## Safety
- source_patch_applied: `False`
- source hash unchanged: `True`
- service_start_attempted: `False`
- paper_start_attempted: `False`
- real_live_attempted: `False`
- broker_call_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- runtime_no_risk_execution_pids: `True`

## Next
Fix Q-R15-R1 precheck false_keys; no paper/live.
