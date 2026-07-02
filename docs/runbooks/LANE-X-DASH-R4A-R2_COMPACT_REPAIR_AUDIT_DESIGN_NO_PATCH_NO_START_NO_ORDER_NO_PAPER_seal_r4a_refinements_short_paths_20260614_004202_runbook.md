# LANE-X-DASH-R4A-R2_COMPACT_REPAIR_AUDIT_DESIGN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_seal_r4a_refinements_short_paths_20260614_004202 runbook

Next batch: R4B UI-only skeleton patch in existing dashboard.

Patch target:

`app/mme_scalpx/ops_dashboard/server.py`

Required R4B guards:

- no subprocess
- no replay execution
- latest-N bounded inventory
- 500 row UI cap
- MIV-R research-only label
- separate PnL labels
- historical replay must not change Live Truth Board
