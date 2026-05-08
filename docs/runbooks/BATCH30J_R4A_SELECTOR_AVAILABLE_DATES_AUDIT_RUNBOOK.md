# Batch 30J-R4A Runbook

Audits actual selector-available dates after 30J-R4 rejected the fixture-derived date. Excludes generated repair paths, proof paths, fixture paths, and validator/smoke contract paths.

This batch does not execute replay and does not create tar bundles.

If GREEN_CONTINUE, run 30J-R5 guarded offline replay execution using the actual selector-available date. If FAIL, inspect dataset inventory/selector source and rebuild dataset metadata with selectable dates.
