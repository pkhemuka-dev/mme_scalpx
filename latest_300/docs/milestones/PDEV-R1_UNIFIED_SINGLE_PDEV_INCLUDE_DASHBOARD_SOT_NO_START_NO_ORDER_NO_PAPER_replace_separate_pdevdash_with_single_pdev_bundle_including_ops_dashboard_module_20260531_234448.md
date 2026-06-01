# PDEV-R1_UNIFIED_SINGLE_PDEV_INCLUDE_DASHBOARD_SOT_NO_START_NO_ORDER_NO_PAPER

Classification: **FAIL_PDEV_R1_UNIFIED_SINGLE_PDEV_CHECK_FAILED**

## Decision

Single evidence command only:

```bash
pdev
```

No separate `pdevdash` command is needed.

## What pdev now includes

- `app/mme_scalpx/ops_dashboard/`
- OPS-DASH proofs/audits/patches/milestones/runbooks/handoffs
- dashboard logs and pid pointer files
- current dashboard page snapshot
- pdash/pdev helper extract
- core/services/integrations/replay source slices
- recent proof/audit/milestone/runbook/handoff context
- manifest, file list, sha256 hashes

## Immediate bundle created

- Latest pointer: `run/evidence_bundles/LATEST_PDEV_CURRENT_BUNDLE.txt`
- Latest archive: `run/evidence_bundles/pdev_current_20260531_234448.tar.gz`

## Checks

- helper_ok=1
- no_pdevdash_block=1
- dashboard_module_exists=1
- pdev_exit=0
- bundle_ok=1
- archive_has_dashboard=0
- archive_has_manifest=1
- safety_ok=1

## Safety

No MME service start, no broker call, no order, no paper/live.

- orders_before=0
- orders_after=0
- risk_stream_after=0
- execution_stream_after=0
- risk_proc_after=0
- execution_proc_after=0

## Use

```bash
source ~/.bashrc
pdev
cat run/evidence_bundles/LATEST_PDEV_CURRENT_BUNDLE.txt
```
