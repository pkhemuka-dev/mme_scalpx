# Batch 30J-R4G Runbook

Builds candidate selector metadata in a repair directory using confirmed market-reference dates from 30J-R4F-R2.

This batch validates JSON readability and semantic consistency only. It does not install metadata into the dataset root and does not execute replay.

If GREEN_CONTINUE, proceed to 30J-R4H for a non-mutating selector readability probe. No replay execution until selector probe passes.
