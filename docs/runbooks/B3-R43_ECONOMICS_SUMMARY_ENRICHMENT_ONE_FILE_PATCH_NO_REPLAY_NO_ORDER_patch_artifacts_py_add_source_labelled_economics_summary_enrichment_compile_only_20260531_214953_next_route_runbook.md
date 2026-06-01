# B3-R43_ECONOMICS_SUMMARY_ENRICHMENT_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER next route

Run:

`B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION`

Expected:

- replay_returncode=0
- integrity=pass
- economics_summary.json contains:
  - enrichment_schema_version
  - enrichment_status
  - enriched_field_values
  - enrichment_sources
  - fields_left_missing
  - governance_notes
- strategy row count unchanged
- candidate row count unchanged
