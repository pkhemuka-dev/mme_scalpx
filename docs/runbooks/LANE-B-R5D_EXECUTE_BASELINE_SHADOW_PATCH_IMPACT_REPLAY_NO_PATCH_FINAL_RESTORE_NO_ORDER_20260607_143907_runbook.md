# LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907

If PASS:
- Next: R5E compare baseline vs shadow summaries/candidate/blocker/execution-shadow outputs.
- Do not claim PnL unless shadow or baseline has execution_shadow_filled_count > 0.

If REVIEW:
- If active runtime blocked execution, stop here and do not rerun until Lane X confirms no live process.
- If restore failed, restore manually from RESTORE_DIR shown in report before doing anything else.
- If replay failed, inspect baseline/shadow logs.
