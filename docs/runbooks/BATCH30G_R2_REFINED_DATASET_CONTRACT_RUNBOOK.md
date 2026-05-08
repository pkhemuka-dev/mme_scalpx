# Batch 30G-R2 Runbook

Freezes the refined leaf dataset candidate selected by 30G.

This is artifact-only. It writes a dataset contract under the selected offline materialization folder.

It does not run replay, materialize data, start services, delete Redis keys, enable paper/live, or send orders.

If GREEN_CONTINUE, proceed to Batch 30H replay dry-run plan/adapter compatibility audit, offline only.
