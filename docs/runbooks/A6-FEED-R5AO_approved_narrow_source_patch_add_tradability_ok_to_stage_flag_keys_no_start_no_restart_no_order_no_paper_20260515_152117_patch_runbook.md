# A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117 Patch Runbook

Batch: A6-FEED-R5AO

Verdict: PASS_A6_FEED_R5AO_TRADABILITY_OK_ADDED_TO_STAGE_FLAG_KEYS_COMPILED_NO_RESTART_NO_ORDER_NO_PAPER

Patch summary:
- Patched exactly one file: `app/mme_scalpx/services/feature_family/contracts.py`.
- Patched exactly one symbol: `STAGE_FLAG_KEYS`.
- Added exactly one key: `tradability_ok`.
- No service start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Patch result:

```json
{
  "inserted_line_after": "warmup_complete",
  "inserted_line_text": "    \"tradability_ok\",",
  "patched": true,
  "reason": "ADDED_TARGET_KEY",
  "surface_after": {
    "end_line": 250,
    "found": true,
    "has_canonical_required": true,
    "has_target_key": true,
    "line": 234,
    "target_count": 1,
    "values": [
      "data_valid",
      "data_quality_ok",
      "session_eligible",
      "warmup_complete",
      "tradability_ok",
      "risk_veto_active",
      "reconciliation_lock_active",
      "active_position_present",
      "provider_ready_classic",
      "provider_ready_miso",
      "dhan_context_fresh",
      "selected_option_present",
      "futures_present",
      "call_present",
      "put_present"
    ],
    "window": "    226:     \"call\",\n    227:     \"put\",\n    228:     \"selected_option\",\n    229:     \"cross_option\",\n    230:     \"economics\",\n    231:     \"signals\",\n    232: )\n    233: \n >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (\n    235:     \"data_valid\",\n    236:     \"data_quality_ok\",\n    237:     \"session_eligible\",\n    238:     \"warmup_complete\",\n    239:     \"tradability_ok\",\n    240:     \"risk_veto_active\",\n    241:     \"reconciliation_lock_active\",\n    242:     \"active_position_present\",\n    243:     \"provider_ready_classic\",\n    244:     \"provider_ready_miso\",\n    245:     \"dhan_context_fresh\",\n    246:     \"selected_option_present\",\n    247:     \"futures_present\",\n    248:     \"call_present\",\n    249:     \"put_present\",\n    250: )\n    251: \n    252: COMMON_FUTURES_KEYS: Final[tuple[str, ...]] = (\n    253:     \"ltp\",\n    254:     \"spread\",\n    255:     \"spread_ratio\",\n    256:     \"depth_total\",\n    257:     \"depth_ok\",\n    258:     \"top5_bid_qty\","
  },
  "surface_before": {
    "end_line": 249,
    "found": true,
    "has_canonical_required": true,
    "has_target_key": false,
    "line": 234,
    "target_count": 0,
    "values": [
      "data_valid",
      "data_quality_ok",
      "session_eligible",
      "warmup_complete",
      "risk_veto_active",
      "reconciliation_lock_active",
      "active_position_present",
      "provider_ready_classic",
      "provider_ready_miso",
      "dhan_context_fresh",
      "selected_option_present",
      "futures_present",
      "call_present",
      "put_present"
    ],
    "window": "    226:     \"call\",\n    227:     \"put\",\n    228:     \"selected_option\",\n    229:     \"cross_option\",\n    230:     \"economics\",\n    231:     \"signals\",\n    232: )\n    233: \n >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (\n    235:     \"data_valid\",\n    236:     \"data_quality_ok\",\n    237:     \"session_eligible\",\n    238:     \"warmup_complete\",\n    239:     \"risk_veto_active\",\n    240:     \"reconciliation_lock_active\",\n    241:     \"active_position_present\",\n    242:     \"provider_ready_classic\",\n    243:     \"provider_ready_miso\",\n    244:     \"dhan_context_fresh\",\n    245:     \"selected_option_present\",\n    246:     \"futures_present\",\n    247:     \"call_present\",\n    248:     \"put_present\",\n    249: )\n    250: \n    251: COMMON_FUTURES_KEYS: Final[tuple[str, ...]] = (\n    252:     \"ltp\",\n    253:     \"spread\",\n    254:     \"spread_ratio\",\n    255:     \"depth_total\",\n    256:     \"depth_ok\",\n    257:     \"top5_bid_qty\","
  }
}
```

Diff:

```diff
--- contracts.py.before
+++ contracts.py.after
@@ -236,6 +236,7 @@
     "data_quality_ok",
     "session_eligible",
     "warmup_complete",
+    "tradability_ok",
     "risk_veto_active",
     "reconciliation_lock_active",
     "active_position_present",
```

Backup:

```json
{
  "backup_dir": "/home/Lenovo/scalpx/projects/mme_scalpx/run/_code_backups/A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117",
  "backup_file": "/home/Lenovo/scalpx/projects/mme_scalpx/run/_code_backups/A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117/app/mme_scalpx/services/feature_family/contracts.py",
  "backup_sha256": "54b24f128d39725aecf73e1f1eb9ee50f302fe2931c9ab80b4129ca65c1b23d6",
  "patched_file_sha256": "c7404e03e647db289baf7610bbdaeedb7bbe3f9df59c2853bf3d7e0e4f1ce032"
}
```

Next rule:
- Next batch must be static contract proof/import validation only.
- No service restart until separate explicit approval.
