# B3-R25A_REPLAY_ROW_SURFACE_DEEP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification is HOLD-only/no economics:

Recommended next:

`B3-R26_REPLAY_ARTIFACT_SCHEMA_ENRICHMENT_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER`

Goal:

1. Inspect replay artifact writers/materializers.
2. Identify where candidate audit, blocker audit, trade log, and economics export should be generated.
3. Do not patch before source ownership is proven.

If candidate/economics fields are present, map them into frozen CSV/JSON exports before strategy-combination testing.
