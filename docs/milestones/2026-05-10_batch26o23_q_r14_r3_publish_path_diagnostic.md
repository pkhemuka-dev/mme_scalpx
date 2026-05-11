# 2026-05-10 — 26-O23-Q-R14-R3

Verdict: `PASS_O23_Q_R14_R3_PUBLISH_PATH_DIAGNOSED_NO_SOURCE_PATCH`

## Purpose
Inspect Q-R14-R2 failure and diagnose the publish/projection path without changing source.

## Diagnosis
`PUBLISH_PATH_RAISES_BEFORE_XADD_UNDER_SYNTHETIC_SERVICE_OBJECT`

## Key checks
- local projection reconstruction ok: `True`
- publish validate_any ok: `False`
- publish validate_keyword ok: `False`
- publish real_validate ok: `False`
- Q14-R2 synthetic error: `StrategyBridgeError('strategy.py HOLD-only bridge requires hold_only=1')`
- Q14-R2 xadd called: `False`
- Q14-R2 field present: `False`

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
26-O23-Q-R14-R4 build faithful StrategyService test object or exact source repair only if source-backed by traceback.
