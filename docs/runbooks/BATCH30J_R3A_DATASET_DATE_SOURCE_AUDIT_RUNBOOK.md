# Batch 30J-R3A Runbook

Audits date sources for the selected replay dataset and repairs the required replay CLI args only if the date is proven from artifacts.

This batch does not execute replay and does not create tar bundles.

If GREEN_CONTINUE, run 30J-R4 guarded offline replay execution retry with strict no-broker/no-live/no-order checks.
