# RAW-Z3 Unknown Family Recovery Feasibility

created_at_utc: 2026-05-01T12:15:01.107659+00:00

## Verdict

- raw_z3_freeze_final_ok: `true`
- validation_only: `true`
- patching_performed: `false`

## Current file

`run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl`

## Counts

- total_rows: `1703`
- known_rows: `850`
- unknown_rows: `853`
- unknown_ratio: `0.5008807985907222`

## Inline-pattern recovery feasibility

- recoverable_by_inline_pattern_count: `0`
- recoverable_by_inline_pattern_ratio_of_unknown: `0.0`

## Next

If inline recovery is low, RAW-AA must inspect/join source candidate audit rows instead of guessing family from the trade row alone.
