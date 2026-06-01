# B3-R35A_ROW_ARTIFACT_WRITE_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If root cause confirms early B3 export call:

Recommended next:

`B3-R36_MOVE_B3_EXPORT_CALL_AFTER_ROW_ARTIFACTS_NO_REPLAY_NO_ORDER`

Patch only the actual row-artifact materialization flow.

Do not patch:
- strategy
- risk
- execution
- provider
- live services

After patch, rerun B3-R35 smoke.
