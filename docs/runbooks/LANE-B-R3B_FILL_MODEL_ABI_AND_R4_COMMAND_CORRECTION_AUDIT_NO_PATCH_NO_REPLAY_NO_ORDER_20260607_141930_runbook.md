# LANE-B-R3B_FILL_MODEL_ABI_AND_R4_COMMAND_CORRECTION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141930

If PASS:
- Rewrite R4 command using the exact fill-model ABI proven in this report.
- Do not reuse R3A's --fill-model immediate_market unless the ABI proves it.

If REVIEW:
- Do not run R4.
- Inspect fill_model.py and replay_run.py integration first.
