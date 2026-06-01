# B3-R29_REPLAY_EXPORT_SCHEMA_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER next route

Recommended next:

`B3-R30_REPLAY_EXPORT_WRITER_SOURCE_OWNERSHIP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER`

Goal:

1. Inspect artifact writer/materializer ownership.
2. Find exact function that writes replay artifact exports.
3. Confirm where to add:
   - candidate_audit.csv
   - blocker_distribution.csv
   - economics_summary.json
   - family_side_summary.csv
4. Do not patch until writer ownership is proven.

No broker, no paper/live, no risk/execution.
