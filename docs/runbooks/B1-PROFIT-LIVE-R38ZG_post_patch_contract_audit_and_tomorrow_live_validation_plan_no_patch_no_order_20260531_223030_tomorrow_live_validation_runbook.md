# B1-PROFIT-LIVE-R38ZG_post_patch_contract_audit_and_tomorrow_live_validation_plan_no_patch_no_order_20260531_223030 tomorrow live validation runbook

## Step 1: pre-start safety
```bash
cd /home/Lenovo/scalpx/projects/mme_scalpx
source ~/.bash_aliases 2>/dev/null || true
pcheck
```

Proceed only if orders/risk/execution are zero and no risk/execution process exists.

## Step 2: observe-only start
```bash
pauto_start
sleep 60
pauto_status
pcheck
```

## Step 3: live feature validity check
Inspect latest features/decisions for:
- selected_option_snapshot_ns
- futures_snapshot_ns
- snapshot_sync_valid
- provider_ready_classic
- data_valid
- VIEW_DATA_INVALID

## Step 4: candidate preflight
Only if data_valid improves:
- MIST/MISB/MISC/MISR only
- identify CALL/PUT
- safe_to_promote must be true
- live_orders_allowed must remain false

## Step 5: approval gate
Paper still requires exact approval phrase and separate micro-batch.
