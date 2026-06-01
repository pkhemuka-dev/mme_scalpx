# B1-PROFIT-LIVE-R38ZA_classic_failover_feature_validity_patch_target_audit_no_patch_no_order_no_paper_20260531_211728

## Verdict
`PASS_R38ZA_PATCH_TARGET_IDENTIFIED_NO_PATCH`

## Meaning
R38ZA identifies the exact patch target for `VIEW_DATA_INVALID`. No patch was applied.

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_execution: ``

## Diagnosis
`['FEATURE_FAMILY_FEATURES_PRESENT', 'CLASSIC_FAILOVER_MARKETDATA_PRESENT', 'PROVIDER_READY_CLASSIC_FALSE_DESPITE_FAILOVER', 'CLASSIC_DEGRADED_SAFE_FALSE_DESPITE_FAILOVER', 'SNAPSHOT_SYNC_FALSE', 'SELECTED_OPTION_TIMESTAMP_NOT_PROPAGATED_TO_FAMILY_FEATURES', 'TRADABILITY_FALSE', 'DATA_VALID_FALSE']`

## Patch target
`features.py selected option surface must carry ts_event_ns/last_update_ns into family_features snapshot`

## Core stage counts
`{'provider_ready_classic': {'False': 446}, 'classic_provider_degraded_safe': {'False': 446}, 'snapshot_sync_valid': {'False': 446}, 'data_valid': {'False': 446}, 'tradability_ok': {'False': 446}, 'selected_option_present': {'False': 111, 'True': 335}}`

## Provider counts
`{'active_selected_option_provider_id': {'DHAN': 1, 'ZERODHA': 445}, 'failover_active': {'False': 1, 'True': 445}, 'family_runtime_mode': {'OBSERVE_ONLY': 446}, 'futures_marketdata_status': {'HEALTHY': 445, 'UNAVAILABLE': 1}, 'futures_provider_status': {'HEALTHY': 445, 'UNAVAILABLE': 1}, 'option_context_provider_status': {'UNAVAILABLE': 446}, 'provider_ready_classic': {'False': 446}, 'provider_ready_miso': {'False': 446}, 'selected_option_marketdata_status': {'FAILOVER_ACTIVE': 445, 'UNAVAILABLE': 1}, 'selected_option_provider_status': {'FAILOVER_ACTIVE': 445, 'UNAVAILABLE': 1}, 'transition_reason': {'BOOTSTRAP': 446}}`

## Snapshot counts
`{'active_snapshot_ns': {'1780068078000000000': 3, '1780068080000000000': 7, '1780068103000000000': 3, '1780068119000000000': 3, '1780068126000000000': 3, '1780068154000000000': 3, '1780068173000000000': 4, '1780068190000000000': 3, '1780068210000000000': 3, '1780068223000000000': 3, '1780068249000000000': 3, '1780068315000000000': 5, '1780068343000000000': 5, '1780068378000000000': 7, '1780068401000000000': 4, '1780068418000000000': 8, '1780068466000000000': 6, '1780068496000000000': 4, '1780068550000000000': 6, '1780068595000000000': 85}, 'freshness_ok': {'True': 446}, 'fut_opt_skew_ms': {'': 446}, 'futures_snapshot_ns': {'': 110, '1780068078000000000': 3, '1780068080000000000': 7, '1780068103000000000': 3, '1780068119000000000': 3, '1780068126000000000': 3, '1780068154000000000': 3, '1780068173000000000': 4, '1780068190000000000': 3, '1780068210000000000': 3, '1780068223000000000': 3, '1780068315000000000': 5, '1780068343000000000': 5, '1780068378000000000': 7, '1780068401000000000': 4, '1780068418000000000': 8, '1780068466000000000': 6, '1780068496000000000': 4, '1780068550000000000': 6, '1780068595000000000': 85}, 'max_member_age_ms': {'0': 446}, 'packet_gap_ok': {'True': 446}, 'samples_seen': {'1': 446}, 'selected_option_snapshot_ns': {'': 446}, 'sync_ok': {'False': 446}, 'valid': {'False': 446}, 'validity': {'MARKETDATA_INCOMPLETE_OR_UNSYNCED': 446}}`

## Selected option timestamp keys
`{}`

## Next
Run R38ZB to patch only this target. No risk/execution/order.
