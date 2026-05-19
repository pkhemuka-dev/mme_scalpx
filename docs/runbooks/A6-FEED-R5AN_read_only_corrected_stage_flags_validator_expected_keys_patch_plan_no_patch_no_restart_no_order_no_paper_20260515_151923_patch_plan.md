# A6-FEED-R5AN_read_only_corrected_stage_flags_validator_expected_keys_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_151923 Corrected Patch Plan

Batch: A6-FEED-R5AN

Verdict: PASS_A6_FEED_R5AN_CORRECTED_VALIDATOR_EXPECTED_KEYS_PATCH_PLAN_READY_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: patch-plan only; no source patch, no service start/restart, no Redis write, no paper/live, no broker/order, no risk/execution.

Classification:

```json
{
  "contracts_stage_flag_surface": {
    "end_line": 249,
    "found": true,
    "has_canonical_required": true,
    "has_tradability_ok": false,
    "insertion_after": "warmup_complete",
    "line": 234,
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
    "window": "    224:     \"strategy_runtime_mode_miso\",\n    225:     \"futures\",\n    226:     \"call\",\n    227:     \"put\",\n    228:     \"selected_option\",\n    229:     \"cross_option\",\n    230:     \"economics\",\n    231:     \"signals\",\n    232: )\n    233: \n >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (\n    235:     \"data_valid\",\n    236:     \"data_quality_ok\",\n    237:     \"session_eligible\",\n    238:     \"warmup_complete\",\n    239:     \"risk_veto_active\",\n    240:     \"reconciliation_lock_active\",\n    241:     \"active_position_present\",\n    242:     \"provider_ready_classic\",\n    243:     \"provider_ready_miso\",\n    244:     \"dhan_context_fresh\",\n    245:     \"selected_option_present\",\n    246:     \"futures_present\",\n    247:     \"call_present\",\n    248:     \"put_present\",\n    249: )\n    250: \n    251: COMMON_FUTURES_KEYS: Final[tuple[str, ...]] = (\n    252:     \"ltp\",\n    253:     \"spread\",\n    254:     \"spread_ratio\",\n    255:     \"depth_total\",\n    256:     \"depth_ok\",\n    257:     \"top5_bid_qty\",\n    258:     \"top5_ask_qty\",\n    259:     \"ofi_ratio_proxy\","
  },
  "decisions_stream_age_ms": 19575827,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 16291535,
  "features_stream_xlen": 131,
  "likely_condition": "CORRECT_PATCH_PLAN_IS_ADD_TRADABILITY_OK_TO_STAGE_FLAG_KEYS_VALIDATOR",
  "next_action": "Next may patch only app/mme_scalpx/services/feature_family/contracts.py STAGE_FLAG_KEYS by adding tradability_ok. No restart/paper/live.",
  "r5aj_final_verdict": "PASS_A6_FEED_R5AJ_FEATURE_FAMILY_STAGE_FLAGS_CONTRACT_MISMATCH_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5aj_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AJ_read_only_extract_feature_family_stage_flags_contract_mismatch_no_patch_no_restart_no_order_no_paper_20260515_150025.json",
  "r5am_r2_failures": [
    "latest_r5al_found_and_no_patch_applied"
  ],
  "r5am_r2_final_verdict": "FAIL_A6_FEED_R5AM_R2_SURFACE_RANKING_OR_SAFETY_CHECK",
  "r5am_r2_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AM-R2_corrected_read_only_rank_actual_stage_flags_tradability_patch_surface_after_r5am_no_patch_no_restart_no_order_no_paper_20260515_151733.json",
  "services": [],
  "top_ranked_surface": {
    "candidate": {
      "classification": "validator_expected_keys_likely_patch_target_add_tradability_ok",
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_four": true,
      "has_canonical_plus_tradability": false,
      "has_tradability_ok": false,
      "line": 234,
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
      "window": "    218:     \"premium_floor_ok\",\n    219: )\n    220: \n    221: COMMON_KEYS: Final[tuple[str, ...]] = (\n    222:     \"regime\",\n    223:     \"strategy_runtime_mode_classic\",\n    224:     \"strategy_runtime_mode_miso\",\n    225:     \"futures\",\n    226:     \"call\",\n    227:     \"put\",\n    228:     \"selected_option\",\n    229:     \"cross_option\",\n    230:     \"economics\",\n    231:     \"signals\",\n    232: )\n    233: \n >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (\n    235:     \"data_valid\",\n    236:     \"data_quality_ok\",\n    237:     \"session_eligible\",\n    238:     \"warmup_complete\",\n    239:     \"risk_veto_active\",\n    240:     \"reconciliation_lock_active\",\n    241:     \"active_position_present\",\n    242:     \"provider_ready_classic\",\n    243:     \"provider_ready_miso\",\n    244:     \"dhan_context_fresh\",\n    245:     \"selected_option_present\",\n    246:     \"futures_present\",\n    247:     \"call_present\",\n    248:     \"put_present\",\n    249: )\n    250: "
    },
    "patch_direction": "add tradability_ok to stage_flags expected keys in validator contract",
    "rank": 1,
    "reason": "producers/feature-family surfaces reference tradability_ok, while validator expected set appears canonical-four only"
  }
}
```

Patch plan:

```json
{
  "current_values": [
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
  "do_not_touch": [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "risk/execution",
    "paper/live enablement",
    "broker/order paths",
    "strategy thresholds",
    "family doctrine",
    "Redis state",
    "service start/restart"
  ],
  "intended_change": "insert 'tradability_ok' into STAGE_FLAG_KEYS, preferably after 'warmup_complete'",
  "patch_scope": "one-file validator contract update only",
  "post_patch_required_proofs": [
    "compile contracts.py",
    "compile feature_family package",
    "compile features.py and strategy.py",
    "static AST proof STAGE_FLAG_KEYS includes tradability_ok",
    "no order stream growth",
    "position remains FLAT",
    "no service restart until explicit approval"
  ],
  "reason": "Feature-family producers and strategy-family surfaces already reference tradability_ok; validator expected-key contract rejects payload before strategy decisions can publish.",
  "target_file": "app/mme_scalpx/services/feature_family/contracts.py",
  "target_line": 234,
  "target_symbol": "STAGE_FLAG_KEYS"
}
```

Current STAGE_FLAG_KEYS window:

```text
    224:     "strategy_runtime_mode_miso",
    225:     "futures",
    226:     "call",
    227:     "put",
    228:     "selected_option",
    229:     "cross_option",
    230:     "economics",
    231:     "signals",
    232: )
    233: 
 >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (
    235:     "data_valid",
    236:     "data_quality_ok",
    237:     "session_eligible",
    238:     "warmup_complete",
    239:     "risk_veto_active",
    240:     "reconciliation_lock_active",
    241:     "active_position_present",
    242:     "provider_ready_classic",
    243:     "provider_ready_miso",
    244:     "dhan_context_fresh",
    245:     "selected_option_present",
    246:     "futures_present",
    247:     "call_present",
    248:     "put_present",
    249: )
    250: 
    251: COMMON_FUTURES_KEYS: Final[tuple[str, ...]] = (
    252:     "ltp",
    253:     "spread",
    254:     "spread_ratio",
    255:     "depth_total",
    256:     "depth_ok",
    257:     "top5_bid_qty",
    258:     "top5_ask_qty",
    259:     "ofi_ratio_proxy",
```

Next rule:
- Patch exactly one file: app/mme_scalpx/services/feature_family/contracts.py.
- Add only `tradability_ok` to STAGE_FLAG_KEYS.
- No service restart until separate explicit approval.
