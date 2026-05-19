# B1B-R2_CAPTURE_BUNDLE_LANE_E_HANDOFF_PREREQ_PACK_NO_PATCH_NO_START runbook

When B1A provides evidence, B1B may:

1. Confirm dirty runtime ownership/clean-tree status is resolved by B1A.
2. Confirm capture bundle contains required files.
3. Run `bin/b1_capture_bundle_validator.py` only against the real B1A bundle.
4. Refresh five-strategy admission matrix.
5. If at least one family has real candidate/risk/execution-shadow lifecycle evidence, mark as `ADMITTED_FOR_LANE_E_REVIEW` only.

B1B must still not run replay or PnL.