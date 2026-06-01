# PDEV-RESTORE-R1_RESTORE_OLD_PDEV_R6_ADD_DASHBOARD_ONLY_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_PDEV_RESTORE_R1_OLD_PDEV_R6_RECOVERED_WITH_DASHBOARD_ONLY_ADDITION_NO_START_NO_ORDER_NO_PAPER**

## Decision

Recovered previous old `pdev` contract and added only dashboard inclusion.

## Preserved old pdev behavior

- `pdev_01_manifest.md`
- `pdev_08_recent_index.tsv`
- `pdev_recent_files/`
- recent limit = 300
- old archive shape: `pdev_current.tar.gz`
- old pointer: `run/evidence_bundles/LATEST_PDEV_PACK.txt`

## Dashboard added

- `pdev_files/app/mme_scalpx/ops_dashboard/server.py`
- `pdev_files/app/mme_scalpx/ops_dashboard/__init__.py`
- OPS-DASH evidence forced into candidates where available

## Checks

- archive_ok=1
- sha_ok=1
- has_old_manifest=1
- has_recent_index=1
- has_dashboard_server=1
- has_dashboard_init=1
- has_old_pdev=1
- has_ops_dash_evidence=1
- safety_ok=1

## Latest recovered pdev archive

- Archive: `run/evidence_bundles/pdev_current.tar.gz`
- SHA: `run/evidence_bundles/pdev_current.tar.gz.sha256`

## Safety

No service start, no broker call, no order, no paper/live.

- orders_before=0
- orders_after=0
- risk_stream_after=0
- execution_stream_after=0
- risk_proc_after=0
- execution_proc_after=0
