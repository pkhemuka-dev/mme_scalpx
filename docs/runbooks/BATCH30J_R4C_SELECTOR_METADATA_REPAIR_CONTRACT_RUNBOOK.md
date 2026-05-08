# Batch 30J-R4C Runbook

Builds selector-compatible available_dates metadata/index repair contracts in a dataset-local repair directory only.

This batch does not install metadata into the dataset root, does not patch production source, and does not execute replay.

If GREEN_CONTINUE, run 30J-R4D to validate the candidate selector metadata path/readability before any replay retry.
