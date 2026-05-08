# RAW-AA2-R2 Bounded Re-enrichment Validation

created_at_utc: 2026-05-01T12:29:04.423988+00:00

## Verdict

- raw_aa2_r2_freeze_final_ok: `True`
- validation_verdict: `RAW_AA2_R2_REENRICHMENT_NO_MATERIAL_IMPROVEMENT`
- validation_only: `true`
- patching_performed: `false`
- compile_ok: `True`
- import_ok: `True`

## Baseline backfilled trade file

- total_rows: `1703`
- known_family_rows: `850`
- unknown_family_rows: `853`
- unknown_family_ratio: `0.5008807985907222`

## Re-enriched backfilled file

- total_rows: `1703`
- known_family_rows: `850`
- unknown_family_rows: `853`
- unknown_family_ratio: `0.5008807985907222`

## Conclusion

- coverage_improved: `False`
- unknown_family_row_delta_after_minus_before: `0`
- family_pnl_bucket_readiness: `NOT_READY`

No live runtime, broker IO, Redis live writes, order sending, strategy/risk/execution mutation, or paper/live enablement.
