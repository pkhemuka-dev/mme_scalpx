# RAW-Z Larger Bounded RAW-X Validation

Timestamp UTC: 2026-05-01T12:10:29.695973+00:00

## Verdict

- validation_verdict: `RAW_Z_VALIDATION_COMPLETED`
- raw_z_freeze_final_ok: `True`
- validation_only: `true`
- patching_performed: `false`
- timed_out: `False`

## Bounds

- max_files: `75`
- max_rows_per_file: `3000`
- timeout_sec: `180`

## Coverage

- baseline_unknown_family_ratio: `0.772727`
- baseline_source: `run/proofs/proof_raw_y_small_raw_x_validation.json`
- post_raw_z_unknown_family_ratio: `0.7242945183263055`
- unknown_family_ratio_delta_after_minus_before: `-0.048432481673694516`
- coverage_improved: `True`
- trade_count: `3083`
- known_family_trade_count: `850`
- unknown_family_trade_count: `2233`

## Family PnL bucket readiness

- family_pnl_bucket_readiness: `NOT_READY`
- best_family: `MIST`
- worst_family: `MISB`

## Safety

RAW-Z was run as validation-only. It did not patch code, did not touch broker IO, did not write live Redis truth, did not send orders, and did not enable paper/live.

## Outputs

- `run/proofs/proof_raw_z_larger_raw_x_validation.json`
- `run/proofs/proof_raw_z_freeze_final.json`
- `run/research_gate/raw_z_larger_raw_x_validation_20260501_174029`
- `run/_code_backups/batch_raw_z_larger_raw_x_validation_20260501_174029`
