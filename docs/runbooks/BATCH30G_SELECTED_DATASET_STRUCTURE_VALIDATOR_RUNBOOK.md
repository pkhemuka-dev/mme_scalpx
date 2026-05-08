# Batch 30G Runbook

Offline-only selected dataset structure validator. This validates candidate structure and may refine an overbroad `run/replay` root candidate into a leaf candidate.

It does not run replay and does not materialize any dataset.

If GREEN_CONTINUE, proceed to 30H replay dry-run plan/adapter compatibility audit. If REVIEW_REQUIRED due refined candidate, freeze the refined candidate contract in 30G-R2 first.
