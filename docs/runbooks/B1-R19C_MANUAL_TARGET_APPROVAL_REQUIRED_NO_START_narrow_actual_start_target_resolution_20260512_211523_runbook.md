# B1-R19C Manual Target Approval / Narrow Actual Start Target Resolution

Safety: target-resolution audit only. No source patch, no service start, no replay, no Redis write/delete, no broker call, no order, no paper/live, no PnL.

Classification: `NO_SAFE_START_TARGET_FOUND_REPAIR_PLAN_REQUIRED`

## Systemd unit names

- `scalpx-mme-close.service`
- `scalpx-mme-open.service`
- `scalpx-mme.service`

## Safe risk units



## Safe execution units

- `scalpx-mme.service`

## Operator command candidates



## Next

`B1-R20_RISK_EXECUTION_START_ARTIFACT_REPAIR_PLAN_NO_PATCH_NO_START`

Audit: `run/audits/B1-R19C_MANUAL_TARGET_APPROVAL_REQUIRED_NO_START_narrow_actual_start_target_resolution_20260512_211523_audit.json`
