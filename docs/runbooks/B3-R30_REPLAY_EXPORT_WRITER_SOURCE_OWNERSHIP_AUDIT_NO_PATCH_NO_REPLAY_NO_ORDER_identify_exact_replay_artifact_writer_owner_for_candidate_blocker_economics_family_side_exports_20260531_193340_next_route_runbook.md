# B3-R30_REPLAY_EXPORT_WRITER_SOURCE_OWNERSHIP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If owner is clear:

Recommended next:

`B3-R31_REPLAY_EXPORT_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER`

Goal:

1. Design exact patch in the owner file only.
2. Add export generation for:
   - candidate_audit.csv
   - blocker_distribution.csv
   - economics_summary.json
   - family_side_summary.csv
3. Preserve existing artifacts.
4. Do not change strategy decisions.
5. Do not touch risk/execution/provider/live files.

Patch only after reviewing B3-R30 proof.
