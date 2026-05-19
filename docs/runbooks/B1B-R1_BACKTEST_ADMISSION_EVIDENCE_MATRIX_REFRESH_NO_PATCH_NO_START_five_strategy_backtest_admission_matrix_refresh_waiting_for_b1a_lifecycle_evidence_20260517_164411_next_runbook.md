# B1B-R1_BACKTEST_ADMISSION_EVIDENCE_MATRIX_REFRESH_NO_PATCH_NO_START next runbook

B1B action after this package:

1. If no real validator report exists, wait for B1A lifecycle evidence.
2. Once B1A provides observe-only lifecycle capture evidence, run only the dry validator:

```bash
.venv/bin/python bin/b1_capture_bundle_validator.py \
  --bundle <capture_bundle_dir> \
  --out <capture_bundle_dir>/validator_out \
  --dry-only
```

3. B1B may admit a strategy only as `ADMITTED_FOR_LANE_E_REVIEW`.
4. B1B must not calculate PnL, run replay, start services, or create fake lifecycle rows.

Lane E handoff requires:

- capture bundle shape pass
- safety pass
- identity continuity pass
- lifecycle presence pass
- at least one family admitted for Lane E review
- orders stream safety remains clean