# B3-R25C_RECURSIVE_ARTIFACT_PATH_RECONCILE_AND_SHAPE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification is `PASS_R25C_ROW_SURFACES_FOUND_NO_CANDIDATE_NO_ECONOMICS`:

Recommended next:

`B3-R26_REPLAY_ARTIFACT_SCHEMA_ENRICHMENT_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER`

Goal:

1. Inspect replay artifact writers/materializers.
2. Identify where candidate audit, blocker audit, trade log, and economics export should be generated.
3. Do not patch before source ownership is proven.

If candidate/economics exists, map exact fields first.
