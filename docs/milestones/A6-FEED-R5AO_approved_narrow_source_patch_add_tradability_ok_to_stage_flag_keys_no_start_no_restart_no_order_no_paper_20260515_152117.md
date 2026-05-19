# A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117

Batch: A6-FEED-R5AO

Purpose: approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5AO_TRADABILITY_OK_ADDED_TO_STAGE_FLAG_KEYS_COMPILED_NO_RESTART_NO_ORDER_NO_PAPER

Safety: approved narrow source patch only; contracts.py STAGE_FLAG_KEYS add tradability_ok; no service start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "approval_text": "I APPROVE A6-FEED-R5AO NARROW SOURCE PATCH: ADD tradability_ok TO STAGE_FLAG_KEYS IN app/mme_scalpx/services/feature_family/contracts.py ONLY, NO SERVICE START, NO RESTART, NO PAPER, NO LIVE, NO BROKER ORDER, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT",
  "changed_feature_family_files": [
    "app/mme_scalpx/services/feature_family/contracts.py"
  ],
  "changed_watch_files": [
    "app/mme_scalpx/services/feature_family/contracts.py"
  ],
  "decisions_stream_age_ms": 19690778,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 16406477,
  "features_stream_xlen": 131,
  "likely_condition": "STAGE_FLAG_KEYS_VALIDATOR_NOW_ACCEPTS_TRADABILITY_OK",
  "next_action": "Next run static contract proof/import validation only. No service restart until separate explicit approval.",
  "patch_result": {
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
  },
  "post_services": [
    "feeds"
  ],
  "pre_services": [
    "feeds"
  ],
  "r5an_final_verdict": "PASS_A6_FEED_R5AN_CORRECTED_VALIDATOR_EXPECTED_KEYS_PATCH_PLAN_READY_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5an_likely_condition": "CORRECT_PATCH_PLAN_IS_ADD_TRADABILITY_OK_TO_STAGE_FLAG_KEYS_VALIDATOR",
  "r5an_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AN_read_only_corrected_stage_flags_validator_expected_keys_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_151923.json",
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

Required checks:

```json
{
  "canonical_required_still_present_after": true,
  "explicit_approval_captured": true,
  "latest_r5an_proof_found": true,
  "no_broker_order": true,
  "no_doctrine_change": true,
  "no_paper_live": true,
  "no_redis_write": true,
  "no_risk_execution_start": true,
  "no_service_start_restart_stop": true,
  "no_strategy_threshold_change": true,
  "only_contracts_py_changed_among_feature_family": true,
  "only_contracts_py_changed_among_watch_files": true,
  "patch_applied": true,
  "patch_result_added_target_key": true,
  "post_all_feature_family_sources_compile": true,
  "post_all_watched_sources_compile": true,
  "post_no_risk_execution_order_process_visible": true,
  "post_orders_mme_stream_zero_or_absent": true,
  "post_position_flat": true,
  "pre_all_feature_family_sources_compile": true,
  "pre_all_watched_sources_compile": true,
  "pre_no_risk_execution_order_process_visible": true,
  "pre_orders_mme_stream_zero_or_absent": true,
  "pre_position_flat": true,
  "r5an_patch_plan_ready": true,
  "surface_found_before": true,
  "surface_has_target_after": true,
  "surface_missing_target_before": true,
  "surface_target_count_after_one": true
}
```

Failures:

```json
[]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117.json
- Runbook: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117_patch_runbook.md
- Backup dir: /home/Lenovo/scalpx/projects/mme_scalpx/run/_code_backups/A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117
