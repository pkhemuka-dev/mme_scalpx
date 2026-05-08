# RAW-Z2 Current Evidence Filter Validation

created_at_utc: 2026-05-01T12:13:55.066059+00:00

## Verdict

- validation_verdict: `RAW_Z2_CURRENT_EVIDENCE_VALIDATION_COMPLETED`
- raw_z2_freeze_final_ok: `true`
- validation_only: `true`
- patching_performed: `false`

## Clean current trade evidence

- trade_count: `1703`
- known_family_trade_count: `850`
- unknown_family_trade_count: `853`
- known_family_ratio: `0.49911920140927774`
- unknown_family_ratio: `0.5008807985907222`
- family_pnl_bucket_readiness: `NOT_READY`

## Excluded contaminated sources

Old diagnostic unknown-gap maps/summaries were excluded from current trade-readiness calculation.

## Next

If unknown ratio remains high, proceed to RAW-AA source-specific lineage repair targeting only the current backfilled record producer/source-row mapping.
