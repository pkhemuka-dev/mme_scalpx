Batch 26-O7 - Controlled runtime start preflight

Created:
- bin/proof_batch26o7_controlled_runtime_start_preflight.py
- run/proofs/proof_batch26o7_controlled_runtime_start_preflight.json

Purpose:
- prevent duplicate risk/execution startup
- block controlled startup during bad Redis/disk/provider/feed/position state
- preserve real live block

No Redis writes.
No service restart.
No paper/live approval.
