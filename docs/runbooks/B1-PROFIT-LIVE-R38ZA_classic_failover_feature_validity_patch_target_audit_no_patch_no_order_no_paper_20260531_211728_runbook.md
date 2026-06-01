# B1-PROFIT-LIVE-R38ZA_classic_failover_feature_validity_patch_target_audit_no_patch_no_order_no_paper_20260531_211728 runbook

## Next
R38ZB patch should target:

`features.py selected option surface must carry ts_event_ns/last_update_ns into family_features snapshot`

Rules:
- do not fake sync if selected-option timestamp is missing
- do not enable MISO without Dhan context
- do not touch risk/execution/broker
- do not tune thresholds
