# A6-FEED-R5AS_read_only_patch_plan_add_tradability_ok_to_empty_family_features_payload_no_patch_no_restart_no_order_no_paper_20260515_152824 Patch Plan

Batch: A6-FEED-R5AS

Verdict: PASS_A6_FEED_R5AS_EMPTY_PAYLOAD_STAGE_FLAGS_PATCH_PLAN_READY_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: patch-plan only; no source patch, no service start/restart, no Redis write, no paper/live, no broker/order, no risk/execution.

Classification:

```json
{
  "ast_stage_flag_surface": {
    "end_line": 250,
    "found": true,
    "line": 234,
    "required_keys_present": true,
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
    "window": "    222:     \"regime\",\n    223:     \"strategy_runtime_mode_classic\",\n    224:     \"strategy_runtime_mode_miso\",\n    225:     \"futures\",\n    226:     \"call\",\n    227:     \"put\",\n    228:     \"selected_option\",\n    229:     \"cross_option\",\n    230:     \"economics\",\n    231:     \"signals\",\n    232: )\n    233: \n >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (\n    235:     \"data_valid\",\n    236:     \"data_quality_ok\",\n    237:     \"session_eligible\",\n    238:     \"warmup_complete\",\n    239:     \"tradability_ok\",\n    240:     \"risk_veto_active\",\n    241:     \"reconciliation_lock_active\",\n    242:     \"active_position_present\",\n    243:     \"provider_ready_classic\",\n    244:     \"provider_ready_miso\",\n    245:     \"dhan_context_fresh\",\n    246:     \"selected_option_present\","
  },
  "decisions_stream_age_ms": 20116690,
  "decisions_stream_xlen": 1684,
  "empty_builder": {
    "function_end_line": 1057,
    "function_found": true,
    "function_line": 1032,
    "function_window": "    992:             BRANCH_PUT: build_empty_misc_branch_support(),\n    993:         },\n    994:     }\n    995: \n    996: \n    997: def build_empty_misr_family_support() -> dict[str, Any]:\n    998:     return {\n    999:         \"eligible\": False,\n    1000:         \"active_zone\": build_empty_misr_active_zone(),\n    1001:         \"branches\": {\n    1002:             BRANCH_CALL: build_empty_misr_branch_support(),\n    1003:             BRANCH_PUT: build_empty_misr_branch_support(),\n    1004:         },\n    1005:     }\n    1006: \n    1007: \n    1008: def build_empty_miso_family_support() -> dict[str, Any]:\n    1009:     return {\n    1010:         \"eligible\": False,\n    1011:         \"mode\": None,\n    1012:         \"chain_context_ready\": False,\n    1013:         \"selected_side\": None,\n    1014:         \"selected_strike\": None,\n    1015:         \"shadow_call_strike\": None,\n    1016:         \"shadow_put_strike\": None,\n    1017:         \"call_support\": build_empty_miso_side_support(),\n    1018:         \"put_support\": build_empty_miso_side_support(),\n    1019:     }\n    1020: \n    1021: \n    1022: def build_empty_families_block() -> dict[str, Any]:\n    1023:     return {\n    1024:         FAMILY_ID_MIST: build_empty_mist_family_support(),\n    1025:         FAMILY_ID_MISB: build_empty_misb_family_support(),\n    1026:         FAMILY_ID_MISC: build_empty_misc_family_support(),\n    1027:         FAMILY_ID_MISR: build_empty_misr_family_support(),\n    1028:         FAMILY_ID_MISO: build_empty_miso_family_support(),\n    1029:     }\n    1030: \n    1031: \n >> 1032: def build_empty_family_features_payload(\n    1033:     *,\n    1034:     schema_version: int = N.DEFAULT_SCHEMA_VERSION,\n    1035:     service: str = N.SERVICE_FEATURES,\n    1036:     family_features_version: str = FAMILY_FEATURES_VERSION,\n    1037:     generated_at_ns: int = 0,\n    1038: ) -> dict[str, Any]:\n    1039:     \"\"\"\n    1040:     Scaffold-safe builder for proofs/tests.\n    1041: \n    1042:     This builder is intentionally not publishable by default because provider/runtime\n    1043:     fields may remain None. Use validate_publishable_family_features_payload() to\n    1044:     guard runtime publication.\n    1045:     \"\"\"\n    1046:     return {\n    1047:         \"schema_version\": schema_version,\n    1048:         \"service\": service,\n    1049:         \"family_features_version\": family_features_version,\n    1050:         \"generated_at_ns\": generated_at_ns,\n    1051:         \"snapshot\": build_empty_snapshot_block(),\n    1052:         \"provider_runtime\": build_empty_provider_runtime_block(),\n    1053:         \"market\": build_empty_market_block(),\n    1054:         \"common\": build_empty_common_block(),\n    1055:         \"stage_flags\": build_empty_stage_flags_block(),\n    1056:         \"families\": build_empty_families_block(),\n    1057:     }\n    1058: \n    1059: \n    1060: # ============================================================================\n    1061: # Validators\n    1062: # ============================================================================\n    1063: \n    1064: \n    1065: def validate_snapshot_block(snapshot: Mapping[str, Any]) -> None:\n    1066:     _require_exact_keys(snapshot, required_keys=SNAPSHOT_KEYS, field_name=\"snapshot\")\n    1067:     for key in (\"valid\", \"sync_ok\", \"freshness_ok\", \"packet_gap_ok\", \"warmup_ok\"):\n    1068:         _require_bool(snapshot[key], field_name=f\"snapshot.{key}\")\n    1069:     _require_int(snapshot[\"samples_seen\"], field_name=\"snapshot.samples_seen\", min_value=0)\n    1070: \n    1071: \n    1072: def validate_provider_runtime_block(",
    "stage_flags_dicts": [
      {
        "end_line": 1057,
        "has_tradability_ok": false,
        "keys": [
          "common",
          "families",
          "family_features_version",
          "generated_at_ns",
          "market",
          "provider_runtime",
          "schema_version",
          "service",
          "snapshot",
          "stage_flags"
        ],
        "line": 1046,
        "missing_required": [
          "active_position_present",
          "call_present",
          "data_quality_ok",
          "data_valid",
          "dhan_context_fresh",
          "futures_present",
          "provider_ready_classic",
          "provider_ready_miso",
          "put_present",
          "reconciliation_lock_active",
          "risk_veto_active",
          "selected_option_present",
          "session_eligible",
          "tradability_ok",
          "warmup_complete"
        ],
        "window": "    1030: \n    1031: \n    1032: def build_empty_family_features_payload(\n    1033:     *,\n    1034:     schema_version: int = N.DEFAULT_SCHEMA_VERSION,\n    1035:     service: str = N.SERVICE_FEATURES,\n    1036:     family_features_version: str = FAMILY_FEATURES_VERSION,\n    1037:     generated_at_ns: int = 0,\n    1038: ) -> dict[str, Any]:\n    1039:     \"\"\"\n    1040:     Scaffold-safe builder for proofs/tests.\n    1041: \n    1042:     This builder is intentionally not publishable by default because provider/runtime\n    1043:     fields may remain None. Use validate_publishable_family_features_payload() to\n    1044:     guard runtime publication.\n    1045:     \"\"\"\n >> 1046:     return {\n    1047:         \"schema_version\": schema_version,\n    1048:         \"service\": service,\n    1049:         \"family_features_version\": family_features_version,\n    1050:         \"generated_at_ns\": generated_at_ns,\n    1051:         \"snapshot\": build_empty_snapshot_block(),\n    1052:         \"provider_runtime\": build_empty_provider_runtime_block(),\n    1053:         \"market\": build_empty_market_block(),\n    1054:         \"common\": build_empty_common_block(),\n    1055:         \"stage_flags\": build_empty_stage_flags_block(),\n    1056:         \"families\": build_empty_families_block(),\n    1057:     }\n    1058: \n    1059: \n    1060: # ============================================================================\n    1061: # Validators\n    1062: # ============================================================================"
      }
    ],
    "stage_flags_key_mentions": [
      {
        "line": 1055,
        "text": "\"stage_flags\": build_empty_stage_flags_block(),"
      }
    ]
  },
  "features_stream_age_ms": 16832394,
  "features_stream_xlen": 131,
  "likely_condition": "EMPTY_PAYLOAD_BUILDER_MISSING_TRADABILITY_OK",
  "next_action": "Next may patch only build_empty_family_features_payload stage_flags to include tradability_ok. No restart/paper/live.",
  "r5ao_final_verdict": "PASS_A6_FEED_R5AO_TRADABILITY_OK_ADDED_TO_STAGE_FLAG_KEYS_COMPILED_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ao_likely_condition": "STAGE_FLAG_KEYS_VALIDATOR_NOW_ACCEPTS_TRADABILITY_OK",
  "r5ao_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117.json",
  "r5ar_final_verdict": "PASS_A6_FEED_R5AR_IMPORT_TRACEBACK_ROOT_CAUSE_CAPTURED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ar_likely_condition": "IMPORT_FAILURE_ROOT_CAUSE_CAPTURED",
  "r5ar_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AR_read_only_capture_exact_feature_family_contracts_import_traceback_root_cause_no_patch_no_restart_no_order_no_paper_20260515_152641.json",
  "services": [
    "feeds"
  ]
}
```

Patch plan:

```json
{
  "do_not_touch": [
    "STAGE_FLAG_KEYS again",
    "features.py",
    "strategy.py",
    "risk/execution",
    "paper/live enablement",
    "broker/order paths",
    "strategy thresholds",
    "family doctrine",
    "Redis state",
    "service start/restart"
  ],
  "intended_change": "add 'tradability_ok': False to the stage_flags dict produced by build_empty_family_features_payload()",
  "patch_scope": "one-file contracts.py empty payload builder update only",
  "post_patch_required_proofs": [
    "compile contracts.py",
    "compile feature_family package",
    "import app.mme_scalpx.services.feature_family.contracts",
    "import app.mme_scalpx.services.strategy",
    "AST proof build_empty_family_features_payload stage_flags includes tradability_ok",
    "orders stream remains 0",
    "position remains FLAT",
    "no service start/restart"
  ],
  "reason": "STAGE_FLAG_KEYS now includes tradability_ok, but build_empty_family_features_payload() still builds stage_flags without tradability_ok, causing import-time validate_family_features_payload(build_empty_family_features_payload()) to fail.",
  "target_file": "app/mme_scalpx/services/feature_family/contracts.py",
  "target_function": "build_empty_family_features_payload",
  "target_key": "tradability_ok"
}
```

Function window:

```text
    1000:         "active_zone": build_empty_misr_active_zone(),
    1001:         "branches": {
    1002:             BRANCH_CALL: build_empty_misr_branch_support(),
    1003:             BRANCH_PUT: build_empty_misr_branch_support(),
    1004:         },
    1005:     }
    1006: 
    1007: 
    1008: def build_empty_miso_family_support() -> dict[str, Any]:
    1009:     return {
    1010:         "eligible": False,
    1011:         "mode": None,
    1012:         "chain_context_ready": False,
    1013:         "selected_side": None,
    1014:         "selected_strike": None,
    1015:         "shadow_call_strike": None,
    1016:         "shadow_put_strike": None,
    1017:         "call_support": build_empty_miso_side_support(),
    1018:         "put_support": build_empty_miso_side_support(),
    1019:     }
    1020: 
    1021: 
    1022: def build_empty_families_block() -> dict[str, Any]:
    1023:     return {
    1024:         FAMILY_ID_MIST: build_empty_mist_family_support(),
    1025:         FAMILY_ID_MISB: build_empty_misb_family_support(),
    1026:         FAMILY_ID_MISC: build_empty_misc_family_support(),
    1027:         FAMILY_ID_MISR: build_empty_misr_family_support(),
    1028:         FAMILY_ID_MISO: build_empty_miso_family_support(),
    1029:     }
    1030: 
    1031: 
 >> 1032: def build_empty_family_features_payload(
    1033:     *,
    1034:     schema_version: int = N.DEFAULT_SCHEMA_VERSION,
    1035:     service: str = N.SERVICE_FEATURES,
    1036:     family_features_version: str = FAMILY_FEATURES_VERSION,
    1037:     generated_at_ns: int = 0,
    1038: ) -> dict[str, Any]:
    1039:     """
    1040:     Scaffold-safe builder for proofs/tests.
    1041: 
    1042:     This builder is intentionally not publishable by default because provider/runtime
    1043:     fields may remain None. Use validate_publishable_family_features_payload() to
    1044:     guard runtime publication.
    1045:     """
    1046:     return {
    1047:         "schema_version": schema_version,
    1048:         "service": service,
    1049:         "family_features_version": family_features_version,
    1050:         "generated_at_ns": generated_at_ns,
    1051:         "snapshot": build_empty_snapshot_block(),
    1052:         "provider_runtime": build_empty_provider_runtime_block(),
    1053:         "market": build_empty_market_block(),
    1054:         "common": build_empty_common_block(),
    1055:         "stage_flags": build_empty_stage_flags_block(),
    1056:         "families": build_empty_families_block(),
    1057:     }
    1058: 
    1059: 
    1060: # ============================================================================
    1061: # Validators
    1062: # ============================================================================
    1063: 
    1064: 
```

Next rule:
- Patch exactly one file: app/mme_scalpx/services/feature_family/contracts.py.
- Patch exactly one function: build_empty_family_features_payload.
- Add only `tradability_ok` to the empty stage_flags payload.
- No service restart until separate explicit approval.
