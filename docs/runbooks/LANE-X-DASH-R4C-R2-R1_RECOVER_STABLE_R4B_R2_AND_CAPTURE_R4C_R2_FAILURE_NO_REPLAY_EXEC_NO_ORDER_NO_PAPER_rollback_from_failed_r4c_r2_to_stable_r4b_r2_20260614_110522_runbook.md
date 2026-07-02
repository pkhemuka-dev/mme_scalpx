# LANE-X-DASH-R4C-R2-R1_RECOVER_STABLE_R4B_R2_AND_CAPTURE_R4C_R2_FAILURE_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_rollback_from_failed_r4c_r2_to_stable_r4b_r2_20260614_110522 runbook

Next step:

Stop patching R4C UI until the exact runtime exception is diagnosed.

Run an explicit diagnostic batch that reads:

- latest R4C-R2 dashboard runtime log
- page curl HTTP result
- source diff around inserted panel
- Python import/single render traceback

No patch in the diagnostic batch.
