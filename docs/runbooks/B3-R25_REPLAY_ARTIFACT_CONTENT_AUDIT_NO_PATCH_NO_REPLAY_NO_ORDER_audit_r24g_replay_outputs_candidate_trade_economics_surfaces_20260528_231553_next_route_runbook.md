# B3-R25_REPLAY_ARTIFACT_CONTENT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification shows no trade/candidate/economics artifacts:

Recommended next batch:

`B3-R26_REPLAY_ARTIFACT_SCHEMA_ENRICHMENT_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER`

Goal:

1. Inspect replay artifact writer/materializer/source surfaces.
2. Identify where candidate audit, trade log, economics summary should be generated.
3. Do not patch until source ownership is proven.
4. Continue no broker, no paper/live, no risk/execution.

If trade/candidate artifacts exist, audit their columns before any patch.
