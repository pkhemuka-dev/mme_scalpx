# B1-PROFIT-LIVE-R38ZL_capture_grade_eligibility_and_partial_capture_root_cause_audit_no_patch_no_order_20260531_232815 runbook

## Tomorrow capture-grade ladder

1. Pre-start:
   pcheck

2. Observe-only start:
   pauto_start
   sleep 60
   pauto_status
   pcheck

3. Periodic health checks:
   pauto_status
   pcheck

4. Acceptance gates:
   - useful span >= 120 min; preferred >= 240 min
   - fut/opt/features/decisions each >= 1000 records, unless session is intentionally short
   - data_valid true appears
   - snapshot_sync_valid true appears
   - provider_ready_classic true appears
   - candidate/blocker lifecycle visible

5. Only after capture-grade data:
   - strict candidate audit
   - replay/shadow PnL audit
   - controlled paper only after fresh approval
