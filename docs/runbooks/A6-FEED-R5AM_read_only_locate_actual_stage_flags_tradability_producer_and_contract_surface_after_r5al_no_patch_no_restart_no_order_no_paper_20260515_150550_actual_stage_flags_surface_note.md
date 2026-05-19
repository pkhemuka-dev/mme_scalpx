# A6-FEED-R5AM_read_only_locate_actual_stage_flags_tradability_producer_and_contract_surface_after_r5al_no_patch_no_restart_no_order_no_paper_20260515_150550 Actual Stage Flags Surface Note

Batch: A6-FEED-R5AM

Verdict: FAIL_A6_FEED_R5AM_SAFETY_OR_SURFACE_LOCATION_CHECK

Safety: read-only actual producer/contract-surface location only; no patch, no restart, no Redis write, no paper/live, no broker/order, no risk/execution.

Classification:

```json
{
  "decisions_stream_age_ms": 18763338,
  "decisions_stream_xlen": 1684,
  "feature_stream_stage_flags_with_tradability": [],
  "features_stream_age_ms": 15478987,
  "features_stream_xlen": 131,
  "likely_condition": "SURFACE_LOCATION_OR_SAFETY_CHECK_FAILED",
  "next_action": "Stop and review proof.",
  "r5ak_final_verdict": "PASS_A6_FEED_R5AK_STAGE_FLAGS_CONTRACT_ALIGNMENT_PATCH_PLAN_READY_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ak_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AK_read_only_stage_flags_contract_alignment_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_150204.json",
  "r5al_final_verdict": "FAIL_A6_FEED_R5AL_STAGE_FLAGS_PATCH_OR_SAFETY_CHECK",
  "r5al_patch_applied": null,
  "r5al_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AL_narrow_stage_flags_contract_alignment_patch_remove_extra_tradability_flag_no_restart_no_order_no_paper_20260515_150353.json",
  "services": [],
  "stage_dicts_with_tradability": [
    {
      "end_lineno": 407,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 390
    },
    {
      "end_lineno": 425,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 412
    },
    {
      "end_lineno": 808,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 791
    },
    {
      "end_lineno": 825,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 812
    },
    {
      "end_lineno": 733,
      "file": "app/mme_scalpx/services/feature_family/option_core.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "depth_total_min",
        "premium_floor_min",
        "premium_floor_ok",
        "response_efficiency_min",
        "response_efficiency_ok",
        "spread_ratio_max",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 718
    },
    {
      "end_lineno": 5650,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "ask",
        "ask_qty",
        "ask_qty_5",
        "best_ask",
        "best_bid",
        "bid",
        "bid_qty",
        "bid_qty_5",
        "delta",
        "depth_total",
        "instrument_key",
        "instrument_token",
        "iv",
        "ltp",
        "oi",
        "oi_change",
        "option_side",
        "option_symbol",
        "option_token",
        "present",
        "provider_id",
        "raw",
        "role",
        "side",
        "source_member_key",
        "spread",
        "spread_ratio",
        "strike",
        "tradability_ok",
        "trading_symbol",
        "ts_event_ns",
        "valid",
        "volume"
      ],
      "lineno": 5616
    },
    {
      "end_lineno": 6922,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "anomaly",
        "best_ask",
        "best_bid",
        "book_ok",
        "depth_ok",
        "depth_total",
        "ltp",
        "quote_ok",
        "selected_present",
        "side",
        "spread",
        "spread_ok",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 6907
    },
    {
      "end_lineno": 7139,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7126
    },
    {
      "end_lineno": 7310,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7297
    },
    {
      "end_lineno": 7507,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7494
    },
    {
      "end_lineno": 1727,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "ask",
        "bid",
        "delta_3",
        "depth_ok",
        "depth_total",
        "instrument_key",
        "instrument_token",
        "ltp",
        "oi",
        "option_side",
        "present",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "tradability_ok",
        "trading_symbol",
        "valid",
        "volume"
      ],
      "lineno": 1705
    },
    {
      "end_lineno": 2476,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "blocked_reason",
        "depth_ok",
        "depth_total",
        "entry_pass",
        "premium_floor_ok",
        "response_efficiency",
        "response_efficiency_ok",
        "side",
        "spread_ratio",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 2464
    },
    {
      "end_lineno": 3242,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "nof_slope",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "spread_ticks",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok",
        "weighted_ofi_persist"
      ],
      "lineno": 3219
    },
    {
      "end_lineno": 3724,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "active_futures_provider_id",
        "active_option_context_provider_id",
        "active_selected_option_provider_id",
        "branch_id",
        "eligible",
        "family_id",
        "family_runtime_mode",
        "frame_id",
        "frame_ts_ns",
        "instrument_key",
        "instrument_token",
        "option_price",
        "option_symbol",
        "runtime_mode",
        "side",
        "stop_points",
        "strike",
        "surface",
        "target_points",
        "tick_size",
        "tradability_ok"
      ],
      "lineno": 3698
    },
    {
      "end_lineno": 6732,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "entry_pass",
        "source_bridge",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 6726
    },
    {
      "end_lineno": 7016,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "entry_pass",
        "quote_ok",
        "source_bridge",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7009
    },
    {
      "end_lineno": 467,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "branch_id",
        "eligible",
        "family_id",
        "instrument_key",
        "instrument_token",
        "key",
        "option_price",
        "option_symbol",
        "side",
        "strike",
        "tradability_ok"
      ],
      "lineno": 455
    },
    {
      "end_lineno": 407,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 390
    },
    {
      "end_lineno": 425,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 412
    },
    {
      "end_lineno": 808,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 791
    },
    {
      "end_lineno": 825,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 812
    },
    {
      "end_lineno": 733,
      "file": "app/mme_scalpx/services/feature_family/option_core.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "depth_total_min",
        "premium_floor_min",
        "premium_floor_ok",
        "response_efficiency_min",
        "response_efficiency_ok",
        "spread_ratio_max",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 718
    }
  ],
  "stage_flag_source_files": [
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/common.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/mist.py"
  ],
  "tradability_source_files": [
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/feature_family/misb_surface.py",
    "app/mme_scalpx/services/feature_family/misc_surface.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/services/feature_family/misr_surface.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/services/feature_family/option_core.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/mist.py"
  ]
}
```

Source hits:

```json
{
  "app/mme_scalpx/core/models.py": {
    "compile": {
      "error": null,
      "ok": true
    },
    "sha256": "fe2fb4ac45b290069067179336778c8f15046d0e95a78db8d49162a8a6845144",
    "windows": [
      {
        "line": 1135,
        "matched": "warmup_complete: bool",
        "window": "1117:             \"oi_score\",\n1118:             \"iv_score\",\n1119:             \"delta_score\",\n1120:             \"gamma_score\",\n1121:             \"iv_sanity_score\",\n1122:         ):\n1123:             value = getattr(self, field_name)\n1124:             if value is not None:\n1125:                 _require_float(value, field_name)\n1126: \n1127: \n1128: @dataclass(frozen=True, slots=True)\n1129: class FeatureFrame(SchemaBase):\n1130:     ts_event_ns: int\n1131:     instrument_key: str\n1132:     system_state: str\n1133:     strategy_mode: str\n1134:     frame_valid: bool\n1135:     warmup_complete: bool\n1136:     futures_snapshot: FuturesSnapshot\n1137:     strategy_family_id: str | None = None\n1138:     doctrine_id: str | None = None\n1139:     branch_id: str | None = None\n1140:     strategy_runtime_mode: str | None = None\n1141:     family_runtime_mode: str | None = None\n1142:     active_futures_provider_id: str | None = None\n1143:     active_selected_option_provider_id: str | None = None\n1144:     active_option_context_provider_id: str | None = None\n1145:     snapshot_frame: SnapshotFrame | None = None\n1146:     economic_viability: EconomicViability | None = None\n1147:     four_pillar: FourPillarSignal | None = None\n1148:     delta_proxy_normalization: DeltaProxyNormalization | None = None\n1149:     entry_mode_hint: str | None = None\n1150:     explain: str | None = None\n1151:     tags: tuple[str, ...] = ()\n1152: \n1153:     _TYPE: ClassVar[str] = \"feature_frame\""
      },
      {
        "line": 1161,
        "matched": "_require_bool(self.warmup_complete, \"warmup_complete\")",
        "window": "1143:     active_selected_option_provider_id: str | None = None\n1144:     active_option_context_provider_id: str | None = None\n1145:     snapshot_frame: SnapshotFrame | None = None\n1146:     economic_viability: EconomicViability | None = None\n1147:     four_pillar: FourPillarSignal | None = None\n1148:     delta_proxy_normalization: DeltaProxyNormalization | None = None\n1149:     entry_mode_hint: str | None = None\n1150:     explain: str | None = None\n1151:     tags: tuple[str, ...] = ()\n1152: \n1153:     _TYPE: ClassVar[str] = \"feature_frame\"\n1154: \n1155:     def validate(self) -> None:\n1156:         _require_int(self.ts_event_ns, \"ts_event_ns\", min_value=0)\n1157:         _require_non_empty_str(self.instrument_key, \"instrument_key\")\n1158:         _require_literal(self.system_state, \"system_state\", allowed=ALLOWED_SYSTEM_STATES)\n1159:         _require_literal(self.strategy_mode, \"strategy_mode\", allowed=ALLOWED_STRATEGY_MODES)\n1160:         _require_bool(self.frame_valid, \"frame_valid\")\n1161:         _require_bool(self.warmup_complete, \"warmup_complete\")\n1162:         _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)\n1163:         if self.branch_id is not None:\n1164:             _require_literal(self.branch_id, \"branch_id\", allowed=ALLOWED_BRANCH_IDS)\n1165:         if self.strategy_runtime_mode is not None:\n1166:             _validate_strategy_runtime_mode_for_family(\n1167:                 self.strategy_family_id,\n1168:                 self.strategy_runtime_mode,\n1169:                 field_name=\"strategy_runtime_mode\",\n1170:             )\n1171:         if self.family_runtime_mode is not None:\n1172:             _require_literal(self.family_runtime_mode, \"family_runtime_mode\", allowed=ALLOWED_FAMILY_RUNTIME_MODES)\n1173:         if self.active_futures_provider_id is not None:\n1174:             _require_literal(self.active_futures_provider_id, \"active_futures_provider_id\", allowed=ALLOWED_PROVIDER_IDS)\n1175:         if self.active_selected_option_provider_id is not None:\n1176:             _require_literal(\n1177:                 self.active_selected_option_provider_id,\n1178:                 \"active_selected_option_provider_id\",\n1179:                 allowed=ALLOWED_PROVIDER_IDS,"
      },
      {
        "line": 2713,
        "matched": "warmup_complete: bool",
        "window": "2695:         _require_bool(self.risk_heartbeat_stale, \"risk_heartbeat_stale\")\n2696:         _require_int(self.max_new_lots, \"max_new_lots\", min_value=0)\n2697:         _require_float(self.day_realized_pnl, \"day_realized_pnl\")\n2698:         _require_int(self.trades_today, \"trades_today\", min_value=0)\n2699:         if self.reason_code is not None:\n2700:             _optional_non_empty_str(self.reason_code, \"reason_code\")\n2701:         if self.reason_message is not None:\n2702:             _optional_non_empty_str(self.reason_message, \"reason_message\")\n2703:         _require_int(self.last_update_ns, \"last_update_ns\", min_value=0)\n2704:         if self.cooldown_active:\n2705:             _require(self.cooldown_until_ns is not None, \"cooldown_active=True requires cooldown_until_ns\")\n2706: \n2707: \n2708: @dataclass(frozen=True, slots=True)\n2709: class FeatureState(SchemaBase):\n2710:     ts_event_ns: int\n2711:     instrument_key: str\n2712:     frame_valid: bool\n2713:     warmup_complete: bool\n2714:     strategy_mode: str\n2715:     system_state: str\n2716:     strategy_family_id: str | None = None\n2717:     doctrine_id: str | None = None\n2718:     branch_id: str | None = None\n2719:     strategy_runtime_mode: str | None = None\n2720:     family_runtime_mode: str | None = None\n2721:     explain: str | None = None\n2722: \n2723:     _TYPE: ClassVar[str] = \"feature_state\"\n2724: \n2725:     def validate(self) -> None:\n2726:         _require_int(self.ts_event_ns, \"ts_event_ns\", min_value=0)\n2727:         _require_non_empty_str(self.instrument_key, \"instrument_key\")\n2728:         _require_bool(self.frame_valid, \"frame_valid\")\n2729:         _require_bool(self.warmup_complete, \"warmup_complete\")\n2730:         _require_literal(self.strategy_mode, \"strategy_mode\", allowed=ALLOWED_STRATEGY_MODES)\n2731:         _require_literal(self.system_state, \"system_state\", allowed=ALLOWED_SYSTEM_STATES)"
      },
      {
        "line": 2729,
        "matched": "_require_bool(self.warmup_complete, \"warmup_complete\")",
        "window": "2711:     instrument_key: str\n2712:     frame_valid: bool\n2713:     warmup_complete: bool\n2714:     strategy_mode: str\n2715:     system_state: str\n2716:     strategy_family_id: str | None = None\n2717:     doctrine_id: str | None = None\n2718:     branch_id: str | None = None\n2719:     strategy_runtime_mode: str | None = None\n2720:     family_runtime_mode: str | None = None\n2721:     explain: str | None = None\n2722: \n2723:     _TYPE: ClassVar[str] = \"feature_state\"\n2724: \n2725:     def validate(self) -> None:\n2726:         _require_int(self.ts_event_ns, \"ts_event_ns\", min_value=0)\n2727:         _require_non_empty_str(self.instrument_key, \"instrument_key\")\n2728:         _require_bool(self.frame_valid, \"frame_valid\")\n2729:         _require_bool(self.warmup_complete, \"warmup_complete\")\n2730:         _require_literal(self.strategy_mode, \"strategy_mode\", allowed=ALLOWED_STRATEGY_MODES)\n2731:         _require_literal(self.system_state, \"system_state\", allowed=ALLOWED_SYSTEM_STATES)\n2732:         _validate_family_doctrine_pair(self.strategy_family_id, self.doctrine_id)\n2733:         if self.branch_id is not None:\n2734:             _require_literal(self.branch_id, \"branch_id\", allowed=ALLOWED_BRANCH_IDS)\n2735:         if self.strategy_runtime_mode is not None:\n2736:             _validate_strategy_runtime_mode_for_family(\n2737:                 self.strategy_family_id,\n2738:                 self.strategy_runtime_mode,\n2739:                 field_name=\"strategy_runtime_mode\",\n2740:             )\n2741:         if self.family_runtime_mode is not None:\n2742:             _require_literal(self.family_runtime_mode, \"family_runtime_mode\", allowed=ALLOWED_FAMILY_RUNTIME_MODES)\n2743:         if self.explain is not None:\n2744:             _optional_non_empty_str(self.explain, \"explain\")\n2745: \n2746: \n2747: @dataclass(frozen=True, slots=True)"
      }
    ]
  },
  "app/mme_scalpx/services/feature_family/common.py": {
    "compile": {
      "error": null,
      "ok": true
    },
    "sha256": "59a595e226f714112daf5105b78c0c9b1b561b96ef7703b1369956ce21abd57b",
    "windows": [
      {
        "line": 28,
        "matched": "provider_runtime, market, common, stage_flags, families.",
        "window": "10: This module OWNS:\n11: - pure deterministic helpers for building contract-valid family_features payloads\n12: - exact-key subtree construction aligned with feature_family.contracts\n13: - compatibility helper names used by services/features.py and proof scripts\n14: \n15: This module DOES NOT own:\n16: - Redis I/O\n17: - service loops\n18: - provider selection / failover policy\n19: - strategy decisions\n20: - doctrine state machines\n21: - cooldown / proof / execution logic\n22: \n23: Freeze fix\n24: ----------\n25: The previous helper emitted payload_source/payload_version/legacy/metadata while\n26: contracts.py required the exact canonical payload keys:\n27: schema_version, service, family_features_version, generated_at_ns, snapshot,\n28: provider_runtime, market, common, stage_flags, families.\n29: \n30: This file now makes common.py subordinate to contracts.py with no top-level\n31: contract drift.\n32: \"\"\"\n33: \n34: from math import isfinite\n35: from typing import Any, Final, Mapping\n36: \n37: from app.mme_scalpx.core import names as N\n38: from app.mme_scalpx.services.feature_family import contracts as C\n39: \n40: \n41: EPSILON: Final[float] = 1e-8\n42: \n43: OPTION_SIDE_CALL: Final[str] = N.SIDE_CALL\n44: OPTION_SIDE_PUT: Final[str] = N.SIDE_PUT\n45: OPTION_SIDE_IDS: Final[tuple[str, ...]] = (\n46:     OPTION_SIDE_CALL,"
      },
      {
        "line": 224,
        "matched": "def derive_tradability_ok(",
        "window": "206: \n207: def derive_common_premium_floor_ok(premium: Any, *, premium_floor: float) -> bool:\n208:     return (_safe_float(premium, 0.0) or 0.0) >= max(float(premium_floor), 0.0)\n209: \n210: \n211: def derive_depth_ok(depth_total: Any, *, depth_min: int) -> bool:\n212:     return _safe_int(depth_total, 0) >= max(int(depth_min), 0)\n213: \n214: \n215: def derive_spread_ratio_ok(spread_ratio: Any, *, spread_ratio_max: float) -> bool:\n216:     ratio = _safe_float(spread_ratio, None)\n217:     return bool(ratio is not None and ratio <= max(float(spread_ratio_max), 0.0))\n218: \n219: \n220: def derive_response_efficiency_ok(response_efficiency: Any, *, response_efficiency_min: float) -> bool:\n221:     return (_safe_float(response_efficiency, 0.0) or 0.0) >= float(response_efficiency_min)\n222: \n223: \n224: def derive_tradability_ok(\n225:     *,\n226:     premium_floor_ok: bool,\n227:     depth_ok: bool,\n228:     spread_ratio_ok: bool,\n229:     response_efficiency_ok: bool,\n230: ) -> bool:\n231:     return bool(premium_floor_ok and depth_ok and spread_ratio_ok and response_efficiency_ok)\n232: \n233: \n234: def derive_selected_option_tradability_ok(\n235:     *,\n236:     premium: Any,\n237:     premium_floor: float,\n238:     depth_total: Any,\n239:     depth_min: int,\n240:     spread_ratio: Any,\n241:     spread_ratio_max: float,\n242:     response_efficiency: Any,"
      },
      {
        "line": 234,
        "matched": "def derive_selected_option_tradability_ok(",
        "window": "216:     ratio = _safe_float(spread_ratio, None)\n217:     return bool(ratio is not None and ratio <= max(float(spread_ratio_max), 0.0))\n218: \n219: \n220: def derive_response_efficiency_ok(response_efficiency: Any, *, response_efficiency_min: float) -> bool:\n221:     return (_safe_float(response_efficiency, 0.0) or 0.0) >= float(response_efficiency_min)\n222: \n223: \n224: def derive_tradability_ok(\n225:     *,\n226:     premium_floor_ok: bool,\n227:     depth_ok: bool,\n228:     spread_ratio_ok: bool,\n229:     response_efficiency_ok: bool,\n230: ) -> bool:\n231:     return bool(premium_floor_ok and depth_ok and spread_ratio_ok and response_efficiency_ok)\n232: \n233: \n234: def derive_selected_option_tradability_ok(\n235:     *,\n236:     premium: Any,\n237:     premium_floor: float,\n238:     depth_total: Any,\n239:     depth_min: int,\n240:     spread_ratio: Any,\n241:     spread_ratio_max: float,\n242:     response_efficiency: Any,\n243:     response_efficiency_min: float,\n244: ) -> bool:\n245:     return derive_tradability_ok(\n246:         premium_floor_ok=derive_common_premium_floor_ok(premium, premium_floor=premium_floor),\n247:         depth_ok=derive_depth_ok(depth_total, depth_min=depth_min),\n248:         spread_ratio_ok=derive_spread_ratio_ok(spread_ratio, spread_ratio_max=spread_ratio_max),\n249:         response_efficiency_ok=derive_response_efficiency_ok(\n250:             response_efficiency,\n251:             response_efficiency_min=response_efficiency_min,\n252:         ),"
      },
      {
        "line": 245,
        "matched": "return derive_tradability_ok(",
        "window": "227:     depth_ok: bool,\n228:     spread_ratio_ok: bool,\n229:     response_efficiency_ok: bool,\n230: ) -> bool:\n231:     return bool(premium_floor_ok and depth_ok and spread_ratio_ok and response_efficiency_ok)\n232: \n233: \n234: def derive_selected_option_tradability_ok(\n235:     *,\n236:     premium: Any,\n237:     premium_floor: float,\n238:     depth_total: Any,\n239:     depth_min: int,\n240:     spread_ratio: Any,\n241:     spread_ratio_max: float,\n242:     response_efficiency: Any,\n243:     response_efficiency_min: float,\n244: ) -> bool:\n245:     return derive_tradability_ok(\n246:         premium_floor_ok=derive_common_premium_floor_ok(premium, premium_floor=premium_floor),\n247:         depth_ok=derive_depth_ok(depth_total, depth_min=depth_min),\n248:         spread_ratio_ok=derive_spread_ratio_ok(spread_ratio, spread_ratio_max=spread_ratio_max),\n249:         response_efficiency_ok=derive_response_efficiency_ok(\n250:             response_efficiency,\n251:             response_efficiency_min=response_efficiency_min,\n252:         ),\n253:     )\n254: \n255: \n256: def build_snapshot_block(\n257:     *,\n258:     valid: bool | None = None,\n259:     snapshot_valid: bool | None = None,\n260:     validity: str | None = None,\n261:     snapshot_validity: str | None = None,\n262:     sync_ok: bool | None = None,\n263:     snapshot_sync_ok: bool | None = None,"
      },
      {
        "line": 267,
        "matched": "warmup_complete: bool | None = None,",
        "window": "249:         response_efficiency_ok=derive_response_efficiency_ok(\n250:             response_efficiency,\n251:             response_efficiency_min=response_efficiency_min,\n252:         ),\n253:     )\n254: \n255: \n256: def build_snapshot_block(\n257:     *,\n258:     valid: bool | None = None,\n259:     snapshot_valid: bool | None = None,\n260:     validity: str | None = None,\n261:     snapshot_validity: str | None = None,\n262:     sync_ok: bool | None = None,\n263:     snapshot_sync_ok: bool | None = None,\n264:     freshness_ok: bool = True,\n265:     packet_gap_ok: bool = True,\n266:     warmup_ok: bool | None = None,\n267:     warmup_complete: bool | None = None,\n268:     active_snapshot_ns: Any = None,\n269:     futures_snapshot_ns: Any = None,\n270:     selected_option_snapshot_ns: Any = None,\n271:     dhan_futures_snapshot_ns: Any = None,\n272:     dhan_option_snapshot_ns: Any = None,\n273:     max_member_age_ms: Any = None,\n274:     fut_opt_skew_ms: Any = None,\n275:     hard_packet_gap_ms: Any = None,\n276:     samples_seen: Any = 1,\n277:     **_: Any,\n278: ) -> dict[str, Any]:\n279:     resolved_valid = bool(snapshot_valid if snapshot_valid is not None else valid)\n280:     return {\n281:         \"valid\": resolved_valid,\n282:         \"validity\": _safe_str(snapshot_validity or validity, \"VALID\" if resolved_valid else \"INVALID\"),\n283:         \"sync_ok\": bool(snapshot_sync_ok if snapshot_sync_ok is not None else sync_ok if sync_ok is not None else resolved_valid),\n284:         \"freshness_ok\": bool(freshness_ok),\n285:         \"packet_gap_ok\": bool(packet_gap_ok),"
      },
      {
        "line": 286,
        "matched": "\"warmup_ok\": bool(warmup_complete if warmup_complete is not None else warmup_ok if warmup_ok is not None else True),",
        "window": "268:     active_snapshot_ns: Any = None,\n269:     futures_snapshot_ns: Any = None,\n270:     selected_option_snapshot_ns: Any = None,\n271:     dhan_futures_snapshot_ns: Any = None,\n272:     dhan_option_snapshot_ns: Any = None,\n273:     max_member_age_ms: Any = None,\n274:     fut_opt_skew_ms: Any = None,\n275:     hard_packet_gap_ms: Any = None,\n276:     samples_seen: Any = 1,\n277:     **_: Any,\n278: ) -> dict[str, Any]:\n279:     resolved_valid = bool(snapshot_valid if snapshot_valid is not None else valid)\n280:     return {\n281:         \"valid\": resolved_valid,\n282:         \"validity\": _safe_str(snapshot_validity or validity, \"VALID\" if resolved_valid else \"INVALID\"),\n283:         \"sync_ok\": bool(snapshot_sync_ok if snapshot_sync_ok is not None else sync_ok if sync_ok is not None else resolved_valid),\n284:         \"freshness_ok\": bool(freshness_ok),\n285:         \"packet_gap_ok\": bool(packet_gap_ok),\n286:         \"warmup_ok\": bool(warmup_complete if warmup_complete is not None else warmup_ok if warmup_ok is not None else True),\n287:         \"active_snapshot_ns\": _safe_int(active_snapshot_ns, 0) or None,\n288:         \"futures_snapshot_ns\": _safe_int(futures_snapshot_ns, 0) or None,\n289:         \"selected_option_snapshot_ns\": _safe_int(selected_option_snapshot_ns, 0) or None,\n290:         \"dhan_futures_snapshot_ns\": _safe_int(dhan_futures_snapshot_ns, 0) or None,\n291:         \"dhan_option_snapshot_ns\": _safe_int(dhan_option_snapshot_ns, 0) or None,\n292:         \"max_member_age_ms\": _safe_int(max_member_age_ms, 0) or None,\n293:         \"fut_opt_skew_ms\": _safe_int(fut_opt_skew_ms, 0) or None,\n294:         \"hard_packet_gap_ms\": _safe_int(hard_packet_gap_ms, 0) or None,\n295:         \"samples_seen\": max(_safe_int(samples_seen, 1), 1),\n296:     }\n297: \n298: \n299: def build_provider_runtime_block(\n300:     *,\n301:     active_futures_provider_id: Any = None,\n302:     active_selected_option_provider_id: Any = None,\n303:     active_option_context_provider_id: Any = None,\n304:     active_execution_provider_id: Any = None,"
      },
      {
        "line": 403,
        "matched": "\"tradability_ok\": _safe_bool(kwargs.get(\"tradability_ok\"), False),",
        "window": "385:         \"below_vwap\": _safe_bool(kwargs.get(\"below_vwap\"), False),\n386:     }\n387: \n388: \n389: def build_common_option_block(*, side: str | None = None, **kwargs: Any) -> dict[str, Any]:\n390:     return {\n391:         \"ltp\": _safe_float(kwargs.get(\"ltp\"), None),\n392:         \"spread\": _safe_float(kwargs.get(\"spread\"), None),\n393:         \"spread_ratio\": _safe_float(kwargs.get(\"spread_ratio\"), None),\n394:         \"depth_total\": _safe_int(kwargs.get(\"depth_total\"), 0) or None,\n395:         \"depth_ok\": _safe_bool(kwargs.get(\"depth_ok\"), False),\n396:         \"top5_bid_qty\": _safe_int(kwargs.get(\"top5_bid_qty\", kwargs.get(\"bid_qty_5\")), 0) or None,\n397:         \"top5_ask_qty\": _safe_int(kwargs.get(\"top5_ask_qty\", kwargs.get(\"ask_qty_5\")), 0) or None,\n398:         \"ofi_ratio_proxy\": _safe_float(kwargs.get(\"ofi_ratio_proxy\", kwargs.get(\"weighted_ofi_persist\")), None),\n399:         \"microprice\": _safe_float(kwargs.get(\"microprice\"), None),\n400:         \"micro_edge\": _safe_float(kwargs.get(\"micro_edge\"), None),\n401:         \"delta_3\": _safe_float(kwargs.get(\"delta_3\"), None),\n402:         \"response_efficiency\": _safe_float(kwargs.get(\"response_efficiency\"), None),\n403:         \"tradability_ok\": _safe_bool(kwargs.get(\"tradability_ok\"), False),\n404:         \"tick_size\": _safe_float(kwargs.get(\"tick_size\"), None),\n405:         \"lot_size\": _safe_int(kwargs.get(\"lot_size\"), 0) or None,\n406:         \"strike\": _safe_float(kwargs.get(\"strike\"), None),\n407:     }\n408: \n409: \n410: def build_selected_option_block(*, side: str | None = None, **kwargs: Any) -> dict[str, Any]:\n411:     base = build_common_option_block(side=side, **kwargs)\n412:     return {\n413:         \"side\": _safe_str(side or kwargs.get(\"side\")) or None,\n414:         \"ltp\": base[\"ltp\"],\n415:         \"spread\": base[\"spread\"],\n416:         \"spread_ratio\": base[\"spread_ratio\"],\n417:         \"depth_total\": base[\"depth_total\"],\n418:         \"depth_ok\": base[\"depth_ok\"],\n419:         \"ofi_ratio_proxy\": base[\"ofi_ratio_proxy\"],\n420:         \"microprice\": base[\"microprice\"],\n421:         \"micro_edge\": base[\"micro_edge\"],"
      },
      {
        "line": 424,
        "matched": "\"tradability_ok\": base[\"tradability_ok\"],",
        "window": "406:         \"strike\": _safe_float(kwargs.get(\"strike\"), None),\n407:     }\n408: \n409: \n410: def build_selected_option_block(*, side: str | None = None, **kwargs: Any) -> dict[str, Any]:\n411:     base = build_common_option_block(side=side, **kwargs)\n412:     return {\n413:         \"side\": _safe_str(side or kwargs.get(\"side\")) or None,\n414:         \"ltp\": base[\"ltp\"],\n415:         \"spread\": base[\"spread\"],\n416:         \"spread_ratio\": base[\"spread_ratio\"],\n417:         \"depth_total\": base[\"depth_total\"],\n418:         \"depth_ok\": base[\"depth_ok\"],\n419:         \"ofi_ratio_proxy\": base[\"ofi_ratio_proxy\"],\n420:         \"microprice\": base[\"microprice\"],\n421:         \"micro_edge\": base[\"micro_edge\"],\n422:         \"delta_3\": base[\"delta_3\"],\n423:         \"response_efficiency\": base[\"response_efficiency\"],\n424:         \"tradability_ok\": base[\"tradability_ok\"],\n425:     }\n426: \n427: \n428: def build_cross_option_block(\n429:     *,\n430:     call_features: Mapping[str, Any] | None = None,\n431:     put_features: Mapping[str, Any] | None = None,\n432:     **kwargs: Any,\n433: ) -> dict[str, Any]:\n434:     call = _mapping(call_features)\n435:     put = _mapping(put_features)\n436:     call_ltp = _safe_float(call.get(\"ltp\"), None)\n437:     put_ltp = _safe_float(put.get(\"ltp\"), None)\n438:     call_depth = _safe_float(call.get(\"depth_total\"), None)\n439:     put_depth = _safe_float(put.get(\"depth_total\"), None)\n440:     call_spread = _safe_float(call.get(\"spread_ratio\"), None)\n441:     put_spread = _safe_float(put.get(\"spread_ratio\"), None)\n442: "
      },
      {
        "line": 515,
        "matched": "def build_stage_flags_block(",
        "window": "497:     **_: Any,\n498: ) -> dict[str, Any]:\n499:     call_block = dict(call or selected_call or {})\n500:     put_block = dict(put or selected_put or {})\n501:     return {\n502:         \"regime\": _regime(regime),\n503:         \"strategy_runtime_mode_classic\": _classic_runtime_mode(strategy_runtime_mode_classic),\n504:         \"strategy_runtime_mode_miso\": _miso_runtime_mode(strategy_runtime_mode_miso),\n505:         \"futures\": dict(futures or futures_features or build_common_futures_block()),\n506:         \"call\": call_block or build_common_option_block(side=N.SIDE_CALL),\n507:         \"put\": put_block or build_common_option_block(side=N.SIDE_PUT),\n508:         \"selected_option\": dict(selected_option or build_selected_option_block(side=None)),\n509:         \"cross_option\": dict(cross_option or build_cross_option_block(call_features=call_block, put_features=put_block)),\n510:         \"economics\": dict(economics or build_economics_block()),\n511:         \"signals\": dict(signals or build_signals_block()),\n512:     }\n513: \n514: \n515: def build_stage_flags_block(\n516:     *,\n517:     data_valid: bool = False,\n518:     data_quality_ok: bool = False,\n519:     session_eligible: bool = True,\n520:     warmup_complete: bool = True,\n521:     risk_veto_active: bool = False,\n522:     reconciliation_lock_active: bool = False,\n523:     active_position_present: bool = False,\n524:     provider_ready_classic: bool = False,\n525:     provider_ready_miso: bool = False,\n526:     dhan_context_fresh: bool = False,\n527:     selected_option_present: bool = False,\n528:     futures_present: bool = False,\n529:     call_present: bool = False,\n530:     put_present: bool = False,\n531:     **_: Any,\n532: ) -> dict[str, Any]:\n533:     return {"
      },
      {
        "line": 518,
        "matched": "data_quality_ok: bool = False,",
        "window": "500:     put_block = dict(put or selected_put or {})\n501:     return {\n502:         \"regime\": _regime(regime),\n503:         \"strategy_runtime_mode_classic\": _classic_runtime_mode(strategy_runtime_mode_classic),\n504:         \"strategy_runtime_mode_miso\": _miso_runtime_mode(strategy_runtime_mode_miso),\n505:         \"futures\": dict(futures or futures_features or build_common_futures_block()),\n506:         \"call\": call_block or build_common_option_block(side=N.SIDE_CALL),\n507:         \"put\": put_block or build_common_option_block(side=N.SIDE_PUT),\n508:         \"selected_option\": dict(selected_option or build_selected_option_block(side=None)),\n509:         \"cross_option\": dict(cross_option or build_cross_option_block(call_features=call_block, put_features=put_block)),\n510:         \"economics\": dict(economics or build_economics_block()),\n511:         \"signals\": dict(signals or build_signals_block()),\n512:     }\n513: \n514: \n515: def build_stage_flags_block(\n516:     *,\n517:     data_valid: bool = False,\n518:     data_quality_ok: bool = False,\n519:     session_eligible: bool = True,\n520:     warmup_complete: bool = True,\n521:     risk_veto_active: bool = False,\n522:     reconciliation_lock_active: bool = False,\n523:     active_position_present: bool = False,\n524:     provider_ready_classic: bool = False,\n525:     provider_ready_miso: bool = False,\n526:     dhan_context_fresh: bool = False,\n527:     selected_option_present: bool = False,\n528:     futures_present: bool = False,\n529:     call_present: bool = False,\n530:     put_present: bool = False,\n531:     **_: Any,\n532: ) -> dict[str, Any]:\n533:     return {\n534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),"
      },
      {
        "line": 519,
        "matched": "session_eligible: bool = True,",
        "window": "501:     return {\n502:         \"regime\": _regime(regime),\n503:         \"strategy_runtime_mode_classic\": _classic_runtime_mode(strategy_runtime_mode_classic),\n504:         \"strategy_runtime_mode_miso\": _miso_runtime_mode(strategy_runtime_mode_miso),\n505:         \"futures\": dict(futures or futures_features or build_common_futures_block()),\n506:         \"call\": call_block or build_common_option_block(side=N.SIDE_CALL),\n507:         \"put\": put_block or build_common_option_block(side=N.SIDE_PUT),\n508:         \"selected_option\": dict(selected_option or build_selected_option_block(side=None)),\n509:         \"cross_option\": dict(cross_option or build_cross_option_block(call_features=call_block, put_features=put_block)),\n510:         \"economics\": dict(economics or build_economics_block()),\n511:         \"signals\": dict(signals or build_signals_block()),\n512:     }\n513: \n514: \n515: def build_stage_flags_block(\n516:     *,\n517:     data_valid: bool = False,\n518:     data_quality_ok: bool = False,\n519:     session_eligible: bool = True,\n520:     warmup_complete: bool = True,\n521:     risk_veto_active: bool = False,\n522:     reconciliation_lock_active: bool = False,\n523:     active_position_present: bool = False,\n524:     provider_ready_classic: bool = False,\n525:     provider_ready_miso: bool = False,\n526:     dhan_context_fresh: bool = False,\n527:     selected_option_present: bool = False,\n528:     futures_present: bool = False,\n529:     call_present: bool = False,\n530:     put_present: bool = False,\n531:     **_: Any,\n532: ) -> dict[str, Any]:\n533:     return {\n534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),\n537:         \"warmup_complete\": bool(warmup_complete),"
      },
      {
        "line": 520,
        "matched": "warmup_complete: bool = True,",
        "window": "502:         \"regime\": _regime(regime),\n503:         \"strategy_runtime_mode_classic\": _classic_runtime_mode(strategy_runtime_mode_classic),\n504:         \"strategy_runtime_mode_miso\": _miso_runtime_mode(strategy_runtime_mode_miso),\n505:         \"futures\": dict(futures or futures_features or build_common_futures_block()),\n506:         \"call\": call_block or build_common_option_block(side=N.SIDE_CALL),\n507:         \"put\": put_block or build_common_option_block(side=N.SIDE_PUT),\n508:         \"selected_option\": dict(selected_option or build_selected_option_block(side=None)),\n509:         \"cross_option\": dict(cross_option or build_cross_option_block(call_features=call_block, put_features=put_block)),\n510:         \"economics\": dict(economics or build_economics_block()),\n511:         \"signals\": dict(signals or build_signals_block()),\n512:     }\n513: \n514: \n515: def build_stage_flags_block(\n516:     *,\n517:     data_valid: bool = False,\n518:     data_quality_ok: bool = False,\n519:     session_eligible: bool = True,\n520:     warmup_complete: bool = True,\n521:     risk_veto_active: bool = False,\n522:     reconciliation_lock_active: bool = False,\n523:     active_position_present: bool = False,\n524:     provider_ready_classic: bool = False,\n525:     provider_ready_miso: bool = False,\n526:     dhan_context_fresh: bool = False,\n527:     selected_option_present: bool = False,\n528:     futures_present: bool = False,\n529:     call_present: bool = False,\n530:     put_present: bool = False,\n531:     **_: Any,\n532: ) -> dict[str, Any]:\n533:     return {\n534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),\n537:         \"warmup_complete\": bool(warmup_complete),\n538:         \"risk_veto_active\": bool(risk_veto_active),"
      },
      {
        "line": 535,
        "matched": "\"data_quality_ok\": bool(data_quality_ok),",
        "window": "517:     data_valid: bool = False,\n518:     data_quality_ok: bool = False,\n519:     session_eligible: bool = True,\n520:     warmup_complete: bool = True,\n521:     risk_veto_active: bool = False,\n522:     reconciliation_lock_active: bool = False,\n523:     active_position_present: bool = False,\n524:     provider_ready_classic: bool = False,\n525:     provider_ready_miso: bool = False,\n526:     dhan_context_fresh: bool = False,\n527:     selected_option_present: bool = False,\n528:     futures_present: bool = False,\n529:     call_present: bool = False,\n530:     put_present: bool = False,\n531:     **_: Any,\n532: ) -> dict[str, Any]:\n533:     return {\n534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),\n537:         \"warmup_complete\": bool(warmup_complete),\n538:         \"risk_veto_active\": bool(risk_veto_active),\n539:         \"reconciliation_lock_active\": bool(reconciliation_lock_active),\n540:         \"active_position_present\": bool(active_position_present),\n541:         \"provider_ready_classic\": bool(provider_ready_classic),\n542:         \"provider_ready_miso\": bool(provider_ready_miso),\n543:         \"dhan_context_fresh\": bool(dhan_context_fresh),\n544:         \"selected_option_present\": bool(selected_option_present),\n545:         \"futures_present\": bool(futures_present),\n546:         \"call_present\": bool(call_present),\n547:         \"put_present\": bool(put_present),\n548:     }\n549: \n550: \n551: def derive_stage_flags(**kwargs: Any) -> dict[str, Any]:\n552:     return build_stage_flags_block(**kwargs)\n553: "
      },
      {
        "line": 536,
        "matched": "\"session_eligible\": bool(session_eligible),",
        "window": "518:     data_quality_ok: bool = False,\n519:     session_eligible: bool = True,\n520:     warmup_complete: bool = True,\n521:     risk_veto_active: bool = False,\n522:     reconciliation_lock_active: bool = False,\n523:     active_position_present: bool = False,\n524:     provider_ready_classic: bool = False,\n525:     provider_ready_miso: bool = False,\n526:     dhan_context_fresh: bool = False,\n527:     selected_option_present: bool = False,\n528:     futures_present: bool = False,\n529:     call_present: bool = False,\n530:     put_present: bool = False,\n531:     **_: Any,\n532: ) -> dict[str, Any]:\n533:     return {\n534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),\n537:         \"warmup_complete\": bool(warmup_complete),\n538:         \"risk_veto_active\": bool(risk_veto_active),\n539:         \"reconciliation_lock_active\": bool(reconciliation_lock_active),\n540:         \"active_position_present\": bool(active_position_present),\n541:         \"provider_ready_classic\": bool(provider_ready_classic),\n542:         \"provider_ready_miso\": bool(provider_ready_miso),\n543:         \"dhan_context_fresh\": bool(dhan_context_fresh),\n544:         \"selected_option_present\": bool(selected_option_present),\n545:         \"futures_present\": bool(futures_present),\n546:         \"call_present\": bool(call_present),\n547:         \"put_present\": bool(put_present),\n548:     }\n549: \n550: \n551: def derive_stage_flags(**kwargs: Any) -> dict[str, Any]:\n552:     return build_stage_flags_block(**kwargs)\n553: \n554: "
      },
      {
        "line": 537,
        "matched": "\"warmup_complete\": bool(warmup_complete),",
        "window": "519:     session_eligible: bool = True,\n520:     warmup_complete: bool = True,\n521:     risk_veto_active: bool = False,\n522:     reconciliation_lock_active: bool = False,\n523:     active_position_present: bool = False,\n524:     provider_ready_classic: bool = False,\n525:     provider_ready_miso: bool = False,\n526:     dhan_context_fresh: bool = False,\n527:     selected_option_present: bool = False,\n528:     futures_present: bool = False,\n529:     call_present: bool = False,\n530:     put_present: bool = False,\n531:     **_: Any,\n532: ) -> dict[str, Any]:\n533:     return {\n534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),\n537:         \"warmup_complete\": bool(warmup_complete),\n538:         \"risk_veto_active\": bool(risk_veto_active),\n539:         \"reconciliation_lock_active\": bool(reconciliation_lock_active),\n540:         \"active_position_present\": bool(active_position_present),\n541:         \"provider_ready_classic\": bool(provider_ready_classic),\n542:         \"provider_ready_miso\": bool(provider_ready_miso),\n543:         \"dhan_context_fresh\": bool(dhan_context_fresh),\n544:         \"selected_option_present\": bool(selected_option_present),\n545:         \"futures_present\": bool(futures_present),\n546:         \"call_present\": bool(call_present),\n547:         \"put_present\": bool(put_present),\n548:     }\n549: \n550: \n551: def derive_stage_flags(**kwargs: Any) -> dict[str, Any]:\n552:     return build_stage_flags_block(**kwargs)\n553: \n554: \n555: def build_mist_branch_support(**kwargs: Any) -> dict[str, Any]:"
      },
      {
        "line": 551,
        "matched": "def derive_stage_flags(**kwargs: Any) -> dict[str, Any]:",
        "window": "533:     return {\n534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),\n537:         \"warmup_complete\": bool(warmup_complete),\n538:         \"risk_veto_active\": bool(risk_veto_active),\n539:         \"reconciliation_lock_active\": bool(reconciliation_lock_active),\n540:         \"active_position_present\": bool(active_position_present),\n541:         \"provider_ready_classic\": bool(provider_ready_classic),\n542:         \"provider_ready_miso\": bool(provider_ready_miso),\n543:         \"dhan_context_fresh\": bool(dhan_context_fresh),\n544:         \"selected_option_present\": bool(selected_option_present),\n545:         \"futures_present\": bool(futures_present),\n546:         \"call_present\": bool(call_present),\n547:         \"put_present\": bool(put_present),\n548:     }\n549: \n550: \n551: def derive_stage_flags(**kwargs: Any) -> dict[str, Any]:\n552:     return build_stage_flags_block(**kwargs)\n553: \n554: \n555: def build_mist_branch_support(**kwargs: Any) -> dict[str, Any]:\n556:     trend_confirmed = _safe_bool(\n557:         kwargs.get(\"trend_confirmed\", kwargs.get(\"futures_bias_ok\", kwargs.get(\"trend_direction_ok\"))),\n558:         False,\n559:     )\n560:     micro_trap_resolved = _safe_bool(\n561:         kwargs.get(\"micro_trap_resolved\", kwargs.get(\"micro_trap_clear\", kwargs.get(\"micro_trap_blocked\"))),\n562:         False,\n563:     )\n564:     return {\n565:         # Canonical Batch 26D support keys.\n566:         \"trend_confirmed\": trend_confirmed,\n567:         \"futures_impulse_ok\": _safe_bool(kwargs.get(\"futures_impulse_ok\", kwargs.get(\"resume_support\")), False),\n568:         \"pullback_detected\": _safe_bool(kwargs.get(\"pullback_detected\"), False),\n569:         \"micro_trap_resolved\": micro_trap_resolved,"
      },
      {
        "line": 552,
        "matched": "return build_stage_flags_block(**kwargs)",
        "window": "534:         \"data_valid\": bool(data_valid),\n535:         \"data_quality_ok\": bool(data_quality_ok),\n536:         \"session_eligible\": bool(session_eligible),\n537:         \"warmup_complete\": bool(warmup_complete),\n538:         \"risk_veto_active\": bool(risk_veto_active),\n539:         \"reconciliation_lock_active\": bool(reconciliation_lock_active),\n540:         \"active_position_present\": bool(active_position_present),\n541:         \"provider_ready_classic\": bool(provider_ready_classic),\n542:         \"provider_ready_miso\": bool(provider_ready_miso),\n543:         \"dhan_context_fresh\": bool(dhan_context_fresh),\n544:         \"selected_option_present\": bool(selected_option_present),\n545:         \"futures_present\": bool(futures_present),\n546:         \"call_present\": bool(call_present),\n547:         \"put_present\": bool(put_present),\n548:     }\n549: \n550: \n551: def derive_stage_flags(**kwargs: Any) -> dict[str, Any]:\n552:     return build_stage_flags_block(**kwargs)\n553: \n554: \n555: def build_mist_branch_support(**kwargs: Any) -> dict[str, Any]:\n556:     trend_confirmed = _safe_bool(\n557:         kwargs.get(\"trend_confirmed\", kwargs.get(\"futures_bias_ok\", kwargs.get(\"trend_direction_ok\"))),\n558:         False,\n559:     )\n560:     micro_trap_resolved = _safe_bool(\n561:         kwargs.get(\"micro_trap_resolved\", kwargs.get(\"micro_trap_clear\", kwargs.get(\"micro_trap_blocked\"))),\n562:         False,\n563:     )\n564:     return {\n565:         # Canonical Batch 26D support keys.\n566:         \"trend_confirmed\": trend_confirmed,\n567:         \"futures_impulse_ok\": _safe_b
```

AST stage dicts with tradability:

```json
[
  {
    "end_lineno": 407,
    "file": "app/mme_scalpx/services/feature_family/common.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "lot_size",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "spread",
      "spread_ratio",
      "strike",
      "tick_size",
      "top5_ask_qty",
      "top5_bid_qty",
      "tradability_ok"
    ],
    "lineno": 390
  },
  {
    "end_lineno": 425,
    "file": "app/mme_scalpx/services/feature_family/common.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 412
  },
  {
    "end_lineno": 808,
    "file": "app/mme_scalpx/services/feature_family/contracts.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "lot_size",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "spread",
      "spread_ratio",
      "strike",
      "tick_size",
      "top5_ask_qty",
      "top5_bid_qty",
      "tradability_ok"
    ],
    "lineno": 791
  },
  {
    "end_lineno": 825,
    "file": "app/mme_scalpx/services/feature_family/contracts.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 812
  },
  {
    "end_lineno": 733,
    "file": "app/mme_scalpx/services/feature_family/option_core.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "depth_ok",
      "depth_total_min",
      "premium_floor_min",
      "premium_floor_ok",
      "response_efficiency_min",
      "response_efficiency_ok",
      "spread_ratio_max",
      "spread_ratio_ok",
      "tradability_ok"
    ],
    "lineno": 718
  },
  {
    "end_lineno": 5650,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "ask",
      "ask_qty",
      "ask_qty_5",
      "best_ask",
      "best_bid",
      "bid",
      "bid_qty",
      "bid_qty_5",
      "delta",
      "depth_total",
      "instrument_key",
      "instrument_token",
      "iv",
      "ltp",
      "oi",
      "oi_change",
      "option_side",
      "option_symbol",
      "option_token",
      "present",
      "provider_id",
      "raw",
      "role",
      "side",
      "source_member_key",
      "spread",
      "spread_ratio",
      "strike",
      "tradability_ok",
      "trading_symbol",
      "ts_event_ns",
      "valid",
      "volume"
    ],
    "lineno": 5616
  },
  {
    "end_lineno": 6922,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "anomaly",
      "best_ask",
      "best_bid",
      "book_ok",
      "depth_ok",
      "depth_total",
      "ltp",
      "quote_ok",
      "selected_present",
      "side",
      "spread",
      "spread_ok",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 6907
  },
  {
    "end_lineno": 7139,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 7126
  },
  {
    "end_lineno": 7310,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 7297
  },
  {
    "end_lineno": 7507,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 7494
  },
  {
    "end_lineno": 1727,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "ask",
      "bid",
      "delta_3",
      "depth_ok",
      "depth_total",
      "instrument_key",
      "instrument_token",
      "ltp",
      "oi",
      "option_side",
      "present",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "strike",
      "tick_size",
      "tradability_ok",
      "trading_symbol",
      "valid",
      "volume"
    ],
    "lineno": 1705
  },
  {
    "end_lineno": 2476,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "blocked_reason",
      "depth_ok",
      "depth_total",
      "entry_pass",
      "premium_floor_ok",
      "response_efficiency",
      "response_efficiency_ok",
      "side",
      "spread_ratio",
      "spread_ratio_ok",
      "tradability_ok"
    ],
    "lineno": 2464
  },
  {
    "end_lineno": 3242,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "lot_size",
      "ltp",
      "nof_slope",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "spread_ticks",
      "strike",
      "tick_size",
      "top5_ask_qty",
      "top5_bid_qty",
      "tradability_ok",
      "weighted_ofi_persist"
    ],
    "lineno": 3219
  },
  {
    "end_lineno": 3724,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "active_futures_provider_id",
      "active_option_context_provider_id",
      "active_selected_option_provider_id",
      "branch_id",
      "eligible",
      "family_id",
      "family_runtime_mode",
      "frame_id",
      "frame_ts_ns",
      "instrument_key",
      "instrument_token",
      "option_price",
      "option_symbol",
      "runtime_mode",
      "side",
      "stop_points",
      "strike",
      "surface",
      "target_points",
      "tick_size",
      "tradability_ok"
    ],
    "lineno": 3698
  },
  {
    "end_lineno": 6732,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "depth_ok",
      "entry_pass",
      "source_bridge",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 6726
  },
  {
    "end_lineno": 7016,
    "file": "app/mme_scalpx/services/features.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "depth_ok",
      "entry_pass",
      "quote_ok",
      "source_bridge",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 7009
  },
  {
    "end_lineno": 467,
    "file": "app/mme_scalpx/services/strategy.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "branch_id",
      "eligible",
      "family_id",
      "instrument_key",
      "instrument_token",
      "key",
      "option_price",
      "option_symbol",
      "side",
      "strike",
      "tradability_ok"
    ],
    "lineno": 455
  },
  {
    "end_lineno": 407,
    "file": "app/mme_scalpx/services/feature_family/common.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "lot_size",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "spread",
      "spread_ratio",
      "strike",
      "tick_size",
      "top5_ask_qty",
      "top5_bid_qty",
      "tradability_ok"
    ],
    "lineno": 390
  },
  {
    "end_lineno": 425,
    "file": "app/mme_scalpx/services/feature_family/common.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 412
  },
  {
    "end_lineno": 808,
    "file": "app/mme_scalpx/services/feature_family/contracts.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "lot_size",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "spread",
      "spread_ratio",
      "strike",
      "tick_size",
      "top5_ask_qty",
      "top5_bid_qty",
      "tradability_ok"
    ],
    "lineno": 791
  },
  {
    "end_lineno": 825,
    "file": "app/mme_scalpx/services/feature_family/contracts.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "delta_3",
      "depth_ok",
      "depth_total",
      "ltp",
      "micro_edge",
      "microprice",
      "ofi_ratio_proxy",
      "response_efficiency",
      "side",
      "spread",
      "spread_ratio",
      "tradability_ok"
    ],
    "lineno": 812
  },
  {
    "end_lineno": 733,
    "file": "app/mme_scalpx/services/feature_family/option_core.py",
    "has_canonical_stage_flags": false,
    "has_tradability_ok": true,
    "keys": [
      "depth_ok",
      "depth_total_min",
      "premium_floor_min",
      "premium_floor_ok",
      "response_efficiency_min",
      "response_efficiency_ok",
      "spread_ratio_max",
      "spread_ratio_ok",
      "tradability_ok"
    ],
    "lineno": 718
  }
]
```

Latest feature stream stage_flags:

```json
{
  "family_stage_flags": [
    {
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "classic_provider_degraded_safe",
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
        "snapshot_sync_valid",
        "warmup_complete"
      ],
      "path": "family_features_json.stage_flags",
      "values": {
        "active_position_present": false,
        "call_present": true,
        "classic_provider_degraded_safe": true,
        "data_quality_ok": false,
        "data_valid": true,
        "dhan_context_fresh": false,
        "futures_present": true,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "put_present": true,
        "reconciliation_lock_active": false,
        "risk_veto_active": false,
        "selected_option_present": true,
        "session_eligible": true,
        "snapshot_sync_valid": false,
        "warmup_complete": true
      }
    },
    {
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "classic_provider_degraded_safe",
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
        "snapshot_sync_valid",
        "warmup_complete"
      ],
      "path": "consumer_view_json.stage_flags",
      "values": {
        "active_position_present": false,
        "call_present": true,
        "classic_provider_degraded_safe": true,
        "data_quality_ok": false,
        "data_valid": true,
        "dhan_context_fresh": false,
        "futures_present": true,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "put_present": true,
        "reconciliation_lock_active": false,
        "risk_veto_active": false,
        "selected_option_present": true,
        "session_eligible": true,
        "snapshot_sync_valid": false,
        "warmup_complete": true
      }
    },
    {
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "classic_provider_degraded_safe",
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
        "snapshot_sync_valid",
        "warmup_complete"
      ],
      "path": "family_features_json.stage_flags",
      "values": {
        "active_position_present": false,
        "call_present": true,
        "classic_provider_degraded_safe": true,
        "data_quality_ok": false,
        "data_valid": true,
        "dhan_context_fresh": false,
        "futures_present": true,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "put_present": true,
        "reconciliation_lock_active": false,
        "risk_veto_active": false,
        "selected_option_present": true,
        "session_eligible": true,
        "snapshot_sync_valid": false,
        "warmup_complete": true
      }
    },
    {
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "classic_provider_degraded_safe",
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
        "snapshot_sync_valid",
        "warmup_complete"
      ],
      "path": "consumer_view_json.stage_flags",
      "values": {
        "active_position_present": false,
        "call_present": true,
        "classic_provider_degraded_safe": true,
        "data_quality_ok": false,
        "data_valid": true,
        "dhan_context_fresh": false,
        "futures_present": true,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "put_present": true,
        "reconciliation_lock_active": false,
        "risk_veto_active": false,
        "selected_option_present": true,
        "session_eligible": true,
        "snapshot_sync_valid": false,
        "warmup_complete": true
      }
    },
    {
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "classic_provider_degraded_safe",
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
        "snapshot_sync_valid",
        "warmup_complete"
      ],
      "path": "family_features_json.stage_flags",
      "values": {
        "active_position_present": false,
        "call_present": true,
        "classic_provider_degraded_safe": true,
        "data_quality_ok": false,
        "data_valid": true,
        "dhan_context_fresh": false,
        "futures_present": true,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "put_present": true,
        "reconciliation_lock_active": false,
        "risk_veto_active": false,
        "selected_option_present": true,
        "session_eligible": true,
        "snapshot_sync_valid": false,
        "warmup_complete": true
      }
    },
    {
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "classic_provider_degraded_safe",
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
        "snapshot_sync_valid",
        "warmup_complete"
      ],
      "path": "consumer_view_json.stage_flags",
      "values": {
        "active_position_present": false,
        "call_present": true,
        "classic_provider_degraded_safe": true,
        "data_quality_ok": false,
        "data_valid": true,
        "dhan_context_fresh": false,
        "futures_present": true,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "put_present": true,
        "reconciliation_lock_active": false,
        "risk_veto_active": false,
        "selected_option_present": true,
        "session_eligible": true,
        "snapshot_sync_valid": false,
        "warmup_complete": true
      }
    }
  ],
  "raw_excerpt": "teps\":0.0,\"wall_strength_score\":0.7729847251288857,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"put_wall\":{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"wall_kind\":\"PUT_OI_SUPPORT\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.6348880364441802,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"call_wall_distance_points\":0.0,\"put_wall_distance_points\":0.0,\"call_wall_strength_score\":0.7729847251288857,\"put_wall_strength_score\":0.6348880364441802,\"call_wall_near\":true,\"put_wall_near\":true,\"total_call_oi\":47794565.0,\"total_put_oi\":48960665.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":1.0243981716331134,\"oi_bias_score\":0.008436443177283544,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":true,\"atm_reference_present\":true,\"wall_computable\":true,\"oi_wall_ready\":true},\"ladder_present\":true,\"atm_reference_present\":true,\"wall_computable\":true},\"oi_wall_context\":{\"call\":{\"strike\":23800.0,\"side\":\"CALL\",\"ltp\":165.25,\"oi\":9575735,\"oi_change\":0,\"volume\":92718405,\"iv\":14.486104088720214,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":205.25,\"rank_hint\":null,\"wall_kind\":\"CALL_OI_RESISTANCE\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.7729847251288857,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"put\":{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"wall_kind\":\"PUT_OI_SUPPORT\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.6348880364441802,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"summary\":{\"present\":true,\"atm_reference_strike\":23800.0,\"strike_step\":50.0,\"nearest_call_oi_resistance_strike\":23800.0,\"nearest_put_oi_support_strike\":23800.0,\"call_wall\":{\"strike\":23800.0,\"side\":\"CALL\",\"ltp\":165.25,\"oi\":9575735,\"oi_change\":0,\"volume\":92718405,\"iv\":14.486104088720214,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":205.25,\"rank_hint\":null,\"wall_kind\":\"CALL_OI_RESISTANCE\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.7729847251288857,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"put_wall\":{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"wall_kind\":\"PUT_OI_SUPPORT\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.6348880364441802,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"call_wall_distance_points\":0.0,\"put_wall_distance_points\":0.0,\"call_wall_strength_score\":0.7729847251288857,\"put_wall_strength_score\":0.6348880364441802,\"call_wall_near\":true,\"put_wall_near\":true,\"total_call_oi\":47794565.0,\"total_put_oi\":48960665.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":1.0243981716331134,\"oi_bias_score\":0.008436443177283544,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":true,\"atm_reference_present\":true,\"wall_computable\":true,\"oi_wall_ready\":true},\"oi_bias\":\"NEUTRAL\",\"law\":\"context_not_trigger\",\"wall_authority\":\"app.mme_scalpx.services.feature_family.strike_selection.build_oi_wall_summary\",\"canonical\":true},\"nearest_call_oi_resistance\":{\"strike\":23800.0,\"side\":\"CALL\",\"ltp\":165.25,\"oi\":9575735,\"oi_change\":0,\"volume\":92718405,\"iv\":14.486104088720214,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":205.25,\"rank_hint\":null,\"wall_kind\":\"CALL_OI_RESISTANCE\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.7729847251288857,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"nearest_put_oi_support\":{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"wall_kind\":\"PUT_OI_SUPPORT\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.6348880364441802,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"nearest_call_oi_resistance_strike\":23800.0,\"nearest_put_oi_support_strike\":23800.0,\"call_wall_strength\":0.7729847251288857,\"put_wall_strength\":0.6348880364441802},\"tradability\":{\"present\":true,\"runtime_mode\":\"BASE_5DEPTH\",\"spread_ratio\":0.0023154494731367583,\"depth_total\":7605,\"age_ms\":0.0,\"stale\":false,\"crossed_book\":false,\"queue_reload_veto\":false,\"impact_depth_fraction\":null,\"spread_ratio_max\":1.6,\"depth_min\":80,\"impact_depth_fraction_max\":0.27,\"futures_present\":true,\"futures_liquidity_pass\":true,\"futures_spread_ratio\":0.0004959671148583876,\"futures_depth_total\":2470,\"spread_pass\":true,\"depth_pass\":true,\"stale_pass\":true,\"crossed_book_pass\":true,\"queue_pass\":true,\"impact_pass\":true,\"entry_pass\":true,\"blocked_reason\":\"\",\"source_surface_key\":\"miso_put\",\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"side\":\"PUT\"},\"regime_surface\":{\"present\":true,\"stale\":false,\"regime\":\"LOWVOL\",\"regime_reason\":\"lowvol_ratio_event_rate_volume\",\"regime_score\":80000000.0,\"velocity_ratio\":0.0,\"event_rate_spike_ratio\":0.0,\"volume_norm\":0.0,\"direction_score\":0.0,\"weighted_ofi\":0.0,\"spread_ratio\":0.0004959671148583876,\"futures_surface_present\":true,\"is_lowvol\":true,\"is_normal\":false,\"is_fast\":false,\"is_known\":true,\"cross_option_ready\":true},\"runtime_mode_surface\":{\"mode\":\"BASE_5DEPTH\",\"runtime_mode\":\"BASE_5DEPTH\",\"provider_ready\":true,\"depth20_ready\":false},\"strike_bundle_present\":true,\"selected_strike\":{\"strike\":24000.0,\"side\":\"PUT\",\"ltp\":291.95,\"oi\":2228590,\"oi_change\":0,\"volume\":7425015,\"iv\":18.35253736146147,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":331.95,\"rank_hint\":null,\"selection_score\":797.805,\"distance_from_atm_points\":200.0,\"distance_from_atm_steps\":4.0,\"otm_directional_distance\":-200.0},\"selected_strike_value\":24000.0,\"selected_strike_score\":797.805,\"monitored\":[{\"strike\":24000.0,\"side\":\"PUT\",\"ltp\":291.95,\"oi\":2228590,\"oi_change\":0,\"volume\":7425015,\"iv\":18.35253736146147,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":331.95,\"rank_hint\":null,\"selection_score\":797.805,\"distance_from_atm_points\":200.0,\"distance_from_atm_steps\":4.0,\"otm_directional_distance\":-200.0},{\"strike\":23950.0,\"side\":\"PUT\",\"ltp\":259.05,\"oi\":481585,\"oi_change\":0,\"volume\":2846350,\"iv\":18.183267690817082,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":283.86585,\"rank_hint\":null,\"selection_score\":682.65304,\"distance_from_atm_points\":150.0,\"distance_from_atm_steps\":3.0,\"otm_directional_distance\":-150.0},{\"strike\":23900.0,\"side\":\"PUT\",\"ltp\":229.3,\"oi\":1955720,\"oi_change\":0,\"volume\":12503725,\"iv\":18.149608305096,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":268.85720000000003,\"rank_hint\":null,\"selection_score\":647.3072800000001,\"distance_from_atm_points\":100.0,\"distance_from_atm_steps\":2.0,\"otm_directional_distance\":-100.0},{\"strike\":23850.0,\"side\":\"PUT\",\"ltp\":201.55,\"oi\":2046980,\"oi_change\":0,\"volume\":17215380,\"iv\":18.08999613863036,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":241.55,\"rank_hint\":null,\"selection_score\":582.2700000000001,\"distance_from_atm_points\":50.0,\"distance_from_atm_steps\":1.0,\"otm_directional_distance\":-50.0},{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"selection_score\":520.71,\"distance_from_atm_points\":0.0,\"distance_from_atm_steps\":0.0,\"otm_directional_distance\":0.0}],\"tradable\":[{\"strike\":24000.0,\"side\":\"PUT\",\"ltp\":291.95,\"oi\":2228590,\"oi_change\":0,\"volume\":7425015,\"iv\":18.35253736146147,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":331.95,\"rank_hint\":null,\"selection_score\":797.805,\"distance_from_atm_points\":200.0,\"distance_from_atm_steps\":4.0,\"otm_directional_distance\":-200.0},{\"strike\":23950.0,\"side\":\"PUT\",\"ltp\":259.05,\"oi\":481585,\"oi_change\":0,\"volume\":2846350,\"iv\":18.183267690817082,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":283.86585,\"rank_hint\":null,\"selection_score\":682.65304,\"distance_from_atm_points\":150.0,\"distance_from_atm_steps\":3.0,\"otm_directional_distance\":-150.0},{\"strike\":23900.0,\"side\":\"PUT\",\"ltp\":229.3,\"oi\":1955720,\"oi_change\":0,\"volume\":12503725,\"iv\":18.149608305096,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":268.85720000000003,\"rank_hint\":null,\"selection_score\":647.3072800000001,\"distance_from_atm_points\":100.0,\"distance_from_atm_steps\":2.0,\"otm_directional_distance\":-100.0}],\"shadow\":[{\"strike\":23850.0,\"side\":\"PUT\",\"ltp\":201.55,\"oi\":2046980,\"oi_change\":0,\"volume\":17215380,\"iv\":18.08999613863036,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":241.55,\"rank_hint\":null,\"selection_score\":582.2700000000001,\"distance_from_atm_points\":50.0,\"distance_from_atm_steps\":1.0,\"otm_directional_distance\":-50.0},{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"selection_score\":520.71,\"distance_from_atm_points\":0.0,\"distance_from_atm_steps\":0.0,\"otm_directional_distance\":0.0}],\"shadow_support_count\":2,\"aggressive_flow_ratio\":0.0,\"speed_of_tape\":0.0,\"imbalance_persist_score\":0.0,\"queue_reload_score\":0.0,\"aggression_ok\":false,\"tape_speed_ok\":false,\"tape_urgency_ok\":false,\"imbalance_persist_ok\":false,\"persistence_ok\":false,\"live_flow_ok\":false,\"response_ok\":false,\"spread_ok\":true,\"depth_ok\":false,\"queue_reload_blocked\":false,\"queue_reload_clear\":true,\"queue_ok\":true,\"shadow_support_ok\":true,\"burst_detected\":false,\"burst_valid\":false,\"futures_vwap_align_ok\":true,\"futures_alignment_ok\":true,\"futures_contradiction_score\":1.0,\"futures_contradiction_blocked\":false,\"futures_veto_clear\":true,\"context_pass\":false,\"option_tradability_pass\":true,\"entry_eligibility\":false,\"oi_bias_alignment\":true,\"near_same_side_wall\":false,\"same_side_wall_strength_score\":0.0,\"setup_score\":111.9727,\"risk_shell\":{\"target_points\":5.0,\"hard_stop_points\":4.0,\"disaster_stop_points\":5.0,\"ratchet_arm_points\":3.0,\"breakeven_plus_points\":0.5,\"entry_timeout_ms\":700.0,\"aggr_window_ms\":600.0,\"tape_window_ms\":600.0,\"persistence_window_ms\":600.0,\"max_hold_sec\":60.0,\"early_stall_sec\":30.0},\"feature_refs\":{\"fut_ltp\":23800.0,\"fut_delta\":0.0,\"fut_velocity_ratio\":0.0,\"fut_weighted_ofi\":0.0,\"fut_weighted_ofi_persist\":0.0,\"fut_vwap_distance\":0.0,\"fut_volume_norm\":0.0,\"fut_direction_score\":0.0,\"fut_event_rate_spike_ratio\":0.0,\"opt_ltp\":0.0,\"opt_delta\":0.0,\"opt_velocity_ratio\":0.0,\"opt_weighted_ofi\":0.0,\"opt_weighted_ofi_persist\":0.0,\"opt_response_efficiency\":0.0,\"opt_context_score\":0.6,\"opt_spread_ratio\":0.0,\"opt_touch_depth\":0,\"opt_oi_bias\":\"UNKNOWN\",\"aggressive_flow_ratio\":0.0,\"speed_of_tape\":0.0,\"imbalance_persist_score\":0.0,\"queue_reload_score\":0.0,\"burst_event_id\":null},\"passed_stages\":[\"strike_bundle_present\",\"shadow_strike_support\",\"futures_vwap_alignment\",\"futures_contradiction_veto_clear\",\"option_tradability\"],\"failed_stage\":\"provider_not_ready\",\"eligible\":false,\"batch9_freeze_blocked_reason\":\"provider_not_ready\",\"pre_batch9_failed_stage\":\"aggression_inference\",\"tradability_pass\":true,\"queue_clear\":true,\"futures_clear\":true,\"selected_features\":{\"present\":true,\"side\":\"PUT\",\"provider_id\":\"DHAN\",\"instrument_key\":\"13152002\",\"instrument_token\":\"13152002\",\"option_symbol\":\"NIFTY2651923800PE\",\"strike\":23800.0,\"entry_mode\":null,\"ltp\":172.60000610351562,\"best_bid\":172.5500030517578,\"best_ask\":172.9499969482422,\"mid\":172.75,\"spread\":0.399993896484375,\"spread_ratio\":0.0023154494731367583,\"spread_ticks\":7.9998779296875,\"bid_qty_5\":4355,\"ask_qty_5\":3250,\"depth_total\":7605,\"volume\":null,\"ltq\":null,\"ltt_ns\":null,\"recent_ticks\":[],\"trade_ticks\":[],\"oi\":null,\"delta_proxy\":null,\"tick_size\":0.05,\"lot_size\":65,\"delta_3\":null,\"velocity_ratio\":0.0,\"weighted_ofi_persist\":0.5726495726495726,\"response_efficiency\":0.0,\"impact_depth_fraction_one_lot\":0.008547008547008548,\"packet_gap_ms\":0,\"ask_reloaded\":false,\"bid_reloaded\":false,\"raw\":{\"role\":\"SELECTED_PUT\",\"instrument_token\":\"13152002\",\"trading_symbol\":\"NIFTY2651923800PE\",\"ts_event_ns\":1778840002000000000,\"ltp\":172.60000610351562,\"best_bid\":172.5500030517578,\"best_ask\":172.9499969482422,\"bid_qty_5\":4355,\"ask_qty_5\":3250,\"spread\":0.399993896484375,\"spread_ticks\":7.9998779296875,\"age_ms\":0,\"tick_size\":0.05,\"lot_size\":65,\"strike\":23800.0,\"validity\":\"OK\",\"side\":\"PUT\",\"option_side\":\"PUT\",\"source_member_key\":\"selected_put_json\"},\"metadata_present\":true,\"quote_present\":true,\"book_present\":true,\"timestamp_present\":true,\"live_present\":true,\"fresh\":true,\"stale\":false,\"valid\":true,\"option_side\":\"PUT\",\"role\":\"SELECTED_PUT\",\"option_token\":\"13152002\",\"trading_symbol\":\"NIFTY2651923800PE\"},\"option_features\":{\"present\":true,\"side\":\"PUT\",\"provider_id\":\"DHAN\",\"instrument_key\":\"13152002\",\"instrument_token\":\"13152002\",\"option_symbol\":\"NIFTY2651923800PE\",\"strike\":23800.0,\"entry_mode\":null,\"ltp\":172.60000610351562,\"best_bid\":172.5500030517578,\"best_ask\":172.9499969482422,\"mid\":172.75,\"spread\":0.399993896484375,\"spread_ratio\":0.0023154494731367583,\"spread_ticks\":7.9998779296875,\"bid_qty_5\":4355,\"ask_qty_5\":3250,\"depth_total\":7605,\"volume\":null,\"ltq\":null,\"ltt_ns\":null,\"recent_ticks\":[],\"trade_ticks\":[],\"oi\":null,\"delta_proxy\":null,\"tick_size\":0.05,\"lot_size\":65,\"delta_3\":null,\"velocity_ratio\":0.0,\"weighted_ofi_persist\":0.5726495726495726,\"response_efficiency\":0.0,\"impact_depth_fraction_one_lot\":0.008547008547008548,\"packet_gap_ms\":0,\"ask_reloaded\":false,\"bid_reloaded\":false,\"raw\":{\"role\":\"SELECTED_PUT\",\"instrument_token\":\"13152002\",\"trading_symbol\":\"NIFTY2651923800PE\",\"ts_event_ns\":1778840002000000000,\"ltp\":172.60000610351562,\"best_bid\":172.5500030517578,\"best_ask\":172.9499969482422,\"bid_qty_5\":4355,\"ask_qty_5\":3250,\"spread\":0.399993896484375,\"spread_ticks\":7.9998779296875,\"age_ms\":0,\"tick_size\":0.05,\"lot_size\":65,\"strike\":23800.0,\"validity\":\"OK\",\"side\":\"PUT\",\"option_side\":\"PUT\",\"source_member_key\":\"selected_put_json\"},\"metadata_present\":true,\"quote_present\":true,\"book_present\":true,\"timestamp_present\":true,\"live_present\":true,\"fresh\":true,\"stale\":false,\"valid\":true,\"option_side\":\"PUT\",\"role\":\"SELECTED_PUT\",\"option_token\":\"13152002\",\"trading_symbol\":\"NIFTY2651923800PE\"},\"tradability_surface\":{\"present\":true,\"runtime_mode\":\"BASE_5DEPTH\",\"spread_ratio\":0.0023154494731367583,\"depth_total\":7605,\"age_ms\":0.0,\"stale\":false,\"crossed_book\":false,\"queue_reload_veto\":false,\"impact_depth_fraction\":null,\"spread_ratio_max\":1.6,\"depth_min\":80,\"impact_depth_fraction_max\":0.27,\"futures_present\":true,\"futures_liquidity_pass\":true,\"futures_spread_ratio\":0.0004959671148583876,\"futures_depth_total\":2470,\"spread_pass\":true,\"depth_pass\":true,\"stale_pass\":true,\"crossed_book_pass\":true,\"queue_pass\":true,\"impact_pass\":true,\"entry_pass\":true,\"blocked_reason\":\"\",\"source_surface_key\":\"miso_put\",\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"side\":\"PUT\"},\"oi_wall_context\":{\"call\":{\"strike\":23800.0,\"side\":\"CALL\",\"ltp\":165.25,\"oi\":9575735,\"oi_change\":0,\"volume\":92718405,\"iv\":14.486104088720214,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":205.25,\"rank_hint\":null,\"wall_kind\":\"CALL_OI_RESISTANCE\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.7729847251288857,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"put\":{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"wall_kind\":\"PUT_OI_SUPPORT\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.6348880364441802,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"summary\":{\"present\":true,\"atm_reference_strike\":23800.0,\"strike_step\":50.0,\"nearest_call_oi_resistance_strike\":23800.0,\"nearest_put_oi_support_strike\":23800.0,\"call_wall\":{\"strike\":23800.0,\"side\":\"CALL\",\"ltp\":165.25,\"oi\":9575735,\"oi_change\":0,\"volume\":92718405,\"iv\":14.486104088720214,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":205.25,\"rank_hint\":null,\"wall_kind\":\"CALL_OI_RESISTANCE\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.7729847251288857,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"put_wall\":{\"strike\":23800.0,\"side\":\"PUT\",\"ltp\":175.9,\"oi\":9478885,\"oi_change\":0,\"volume\":67371265,\"iv\":18.028418801387517,\"bid\":null,\"ask\":null,\"spread\":null,\"spread_ratio\":null,\"bid_qty\":null,\"ask_qty\":null,\"touch_depth\":null,\"delta\":null,\"gamma\":null,\"strike_score\":215.9,\"rank_hint\":null,\"wall_kind\":\"PUT_OI_SUPPORT\",\"wall_distance_points\":0.0,\"wall_distance_steps\":0.0,\"wall_strength_score\":0.6348880364441802,\"wall_strength_label\":\"STRONG\",\"near_wall\":true},\"call_wall_distance_points\":0.0,\"put_wall_distance_points\":0.0,\"call_wall_strength_score\":0.7729847251288857,\"put_wall_strength_score\":0.6348880364441802,\"call_wall_near\":true,\"put_wall_near\":true,\"total_call_oi\":47794565.0,\"total_put_oi\":48960665.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":1.0243981716331134,\"oi_bias_score\":0.008436443177283544,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":true,\"atm_reference_present\":true,\"wall_computable\":true,\"oi_wall_ready\":true},\"oi_bias\":\"NEUTRAL\",\"law\":\"context_not_trigger\",\"wall_authority\":\"app.mme_scalpx.services.feature_family.strike_selection.build_oi_wall_summary\",\"canonical\":true},\"cross_option_context\":{\"call_minus_put_ltp\":-3.25,\"call_put_depth_ratio\":4.547008547008547,\"call_put_spread_ratio\":0.6370874383186149,\"call_present\":true,\"put_present\":true,\"selected_option_present\":true,\"nearest_call_oi_resistance_strike\":23800.0,\"nearest_put_oi_support_strike\":23800.0,\"call_wall_distance_pts\":null,\"put_wall_distance_pts\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"oi_bias\":\"NEUTRAL\",\"cross_option_ready\":true},\"rich_surface\":true}}},\"mapping_repair\":{\"batch\":\"26-O16\",\"all_required_branch_keys\":[\"misb_call\",\"misb_put\",\"misc_call\",\"misc_put\",\"miso_call\",\"miso_put\",\"misr_call\",\"misr_put\",\"mist_call\",\"mist_put\"],\"missing_branch_keys\":[],\"branch_frame_count\":10,\"miso_provider_ready_truth_preserved\":false,\"no_doctrine_evaluation\":true,\"no_order_side_effect\":true,\"no_threshold_relaxation\":true},\"structural_valid\":true,\"consumer_view_structural_valid\":true,\"consumer_view_validity_semantics\":\"structural_safe_not_trade_eligibility\",\"forced_candidate\":false,\"threshold_relaxation\":false,\"real_live_enablement\":false}\no23p_r6b_r3_family_payload_publish_patch\n1",
  "raw_has_tradability_ok": true,
  "raw_stage_flags_mentions": 6,
  "xrevrange_ok": true
}
```

Next rule:
- Patch only after exact producer surface is located.
- No service restart until separate explicit approval.
- No paper/live/risk/execution/order work.
