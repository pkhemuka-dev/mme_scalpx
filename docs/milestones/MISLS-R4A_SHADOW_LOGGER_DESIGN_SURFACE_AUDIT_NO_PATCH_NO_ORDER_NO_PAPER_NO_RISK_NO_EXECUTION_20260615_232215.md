# MISLS-R4A_SHADOW_LOGGER_DESIGN_SURFACE_AUDIT_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260615_232215

## Proof

```json
{
  "canonical_surface_ok": true,
  "classification": "PASS_MISLS_R4A_SHADOW_LOGGER_DESIGN_AUDIT_WRITTEN_NO_PATCH_NO_ORDER",
  "no_execution_start": true,
  "no_order": true,
  "no_paper": true,
  "no_redis_delete": true,
  "no_replay_started": true,
  "no_risk_start": true,
  "no_service_started": true,
  "no_source_patch": true,
  "recommended_logger_contract": {
    "canonical_in_memory_surface": "research.misls.events",
    "compatibility_surfaces": [
      "misls.events",
      "misls.candidates",
      "metadata.misls.events",
      "family_surfaces.MISLS.events",
      "family_features.MISLS.events",
      "families.MISLS.events"
    ],
    "minimum_full_candidate_fields": [
      "family_id",
      "branch_id",
      "side",
      "final_classification",
      "event_id",
      "candidate_id",
      "shadow_entry_price",
      "shadow_entry_underlying_price",
      "selected_option_bid_post",
      "selected_option_ask_post",
      "selected_option_bid_qty_post",
      "selected_option_ask_qty_post",
      "selected_option_quote_age_ms",
      "paired_option_bid_post",
      "paired_option_ask_post",
      "paired_option_bid_qty_post",
      "paired_option_ask_qty_post",
      "score"
    ],
    "must_not_do": [
      "broker order",
      "paper order",
      "risk stream emit",
      "execution stream emit",
      "Redis delete",
      "lock delete",
      "service start",
      "replay start",
      "registry wiring",
      "FAMILY_ORDER change"
    ],
    "research_files": [
      "run/research/misls_r3/events_YYYYMMDD.jsonl",
      "run/research/misls_r3/candidates_YYYYMMDD.jsonl",
      "run/research/misls_r3/rejections_YYYYMMDD.jsonl",
      "run/research/misls_r3/forward_paths_YYYYMMDD.jsonl"
    ]
  },
  "recommended_next_patch": "MISLS-R4B_SHADOW_LOGGER_SKELETON_NO_WIRING_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION",
  "sample_action": "HOLD",
  "sample_blocker": "MISLS_RESEARCH_ONLY_NO_PROMOTION",
  "sample_is_blocked": true,
  "sample_is_candidate": false,
  "source_scan_file_count_with_hits": 283,
  "top_source_scan_hits": [
    {
      "hit_count": 245,
      "path": "app/mme_scalpx/services/features.py",
      "sample_hits": [
        {
          "line": 20,
          "text": "- publishing stable family_features"
        },
        {
          "line": 21,
          "text": "- publishing stable family_surfaces"
        },
        {
          "line": 37,
          "text": "- family_features is the strict contract payload consumed later by strategy.py /"
        },
        {
          "line": 39,
          "text": "- family_surfaces is the richer audit/support payload."
        },
        {
          "line": 483,
          "text": "return json.dumps("
        },
        {
          "line": 1008,
          "text": "_nested(shared_core, \"trap_events\", branch_id, default={}),"
        },
        {
          "line": 1106,
          "text": "shadow = dict(_nested(out, \"shadow_features\", default={}) or {})"
        },
        {
          "line": 1107,
          "text": "shadow_sources = ("
        },
        {
          "line": 1108,
          "text": "_nested(shared_core, \"miso_shadow_microstructure\", branch_id, default={}),"
        },
        {
          "line": 1109,
          "text": "_nested(shared_core, \"miso_shadow_microstructure\", branch_key, default={}),"
        },
        {
          "line": 1110,
          "text": "_nested(shared_core, \"microstructure\", \"miso_shadow\", branch_id, default={}),"
        },
        {
          "line": 1111,
          "text": "_nested(shared_core, \"microstructure\", \"miso_shadow\", branch_key, default={}),"
        }
      ]
    },
    {
      "hit_count": 245,
      "path": "app/mme_scalpx/services/features.py",
      "sample_hits": [
        {
          "line": 20,
          "text": "- publishing stable family_features"
        },
        {
          "line": 21,
          "text": "- publishing stable family_surfaces"
        },
        {
          "line": 37,
          "text": "- family_features is the strict contract payload consumed later by strategy.py /"
        },
        {
          "line": 39,
          "text": "- family_surfaces is the richer audit/support payload."
        },
        {
          "line": 483,
          "text": "return json.dumps("
        },
        {
          "line": 1008,
          "text": "_nested(shared_core, \"trap_events\", branch_id, default={}),"
        },
        {
          "line": 1106,
          "text": "shadow = dict(_nested(out, \"shadow_features\", default={}) or {})"
        },
        {
          "line": 1107,
          "text": "shadow_sources = ("
        },
        {
          "line": 1108,
          "text": "_nested(shared_core, \"miso_shadow_microstructure\", branch_id, default={}),"
        },
        {
          "line": 1109,
          "text": "_nested(shared_core, \"miso_shadow_microstructure\", branch_key, default={}),"
        },
        {
          "line": 1110,
          "text": "_nested(shared_core, \"microstructure\", \"miso_shadow\", branch_id, default={}),"
        },
        {
          "line": 1111,
          "text": "_nested(shared_core, \"microstructure\", \"miso_shadow\", branch_key, default={}),"
        }
      ]
    },
    {
      "hit_count": 112,
      "path": "app/mme_scalpx/services/strategy.py",
      "sample_hits": [
        {
          "line": 6,
          "text": "Freeze-grade HOLD-only family_features consumer bridge for ScalpX MME."
        },
        {
          "line": 14,
          "text": "- parsing family_features_json / family_surfaces_json / family_frames_json"
        },
        {
          "line": 15,
          "text": "- validating family_features against feature_family/contracts.py"
        },
        {
          "line": 256,
          "text": "def _r38zr_backfill_family_features_provider_runtime(strategy_self, family_features):"
        },
        {
          "line": 257,
          "text": "ff = dict(family_features) if isinstance(family_features, dict) else {}"
        },
        {
          "line": 279,
          "text": "# R38Z timestamp repair diagnostics must not remain as top-level family_features keys."
        },
        {
          "line": 281,
          "text": "def _r38zu_strip_repair_metadata_keys_from_family_features(family_features):"
        },
        {
          "line": 282,
          "text": "ff = dict(family_features) if isinstance(family_features, dict) else {}"
        },
        {
          "line": 387,
          "text": "return json.dumps("
        },
        {
          "line": 433,
          "text": "# R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_BEGIN"
        },
        {
          "line": 434,
          "text": "def _r34f_shadow_candidate_truth_from_activation_selected("
        },
        {
          "line": 439,
          "text": "Shadow-only candidate truth export from activation-selected dry-run candidate."
        }
      ]
    },
    {
      "hit_count": 112,
      "path": "app/mme_scalpx/services/strategy.py",
      "sample_hits": [
        {
          "line": 6,
          "text": "Freeze-grade HOLD-only family_features consumer bridge for ScalpX MME."
        },
        {
          "line": 14,
          "text": "- parsing family_features_json / family_surfaces_json / family_frames_json"
        },
        {
          "line": 15,
          "text": "- validating family_features against feature_family/contracts.py"
        },
        {
          "line": 256,
          "text": "def _r38zr_backfill_family_features_provider_runtime(strategy_self, family_features):"
        },
        {
          "line": 257,
          "text": "ff = dict(family_features) if isinstance(family_features, dict) else {}"
        },
        {
          "line": 279,
          "text": "# R38Z timestamp repair diagnostics must not remain as top-level family_features keys."
        },
        {
          "line": 281,
          "text": "def _r38zu_strip_repair_metadata_keys_from_family_features(family_features):"
        },
        {
          "line": 282,
          "text": "ff = dict(family_features) if isinstance(family_features, dict) else {}"
        },
        {
          "line": 387,
          "text": "return json.dumps("
        },
        {
          "line": 433,
          "text": "# R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_BEGIN"
        },
        {
          "line": 434,
          "text": "def _r34f_shadow_candidate_truth_from_activation_selected("
        },
        {
          "line": 439,
          "text": "Shadow-only candidate truth export from activation-selected dry-run candidate."
        }
      ]
    },
    {
      "hit_count": 110,
      "path": "app/mme_scalpx/replay/contracts.py",
      "sample_hits": [
        {
          "line": 60,
          "text": "ARTIFACT_RESEARCH_SUMMARY_JSON = \"19_research_summary.json\""
        },
        {
          "line": 79,
          "text": "ARTIFACT_RESEARCH_SUMMARY_JSON,"
        },
        {
          "line": 240,
          "text": "\"shadow_label\","
        },
        {
          "line": 253,
          "text": "\"research_tags\","
        },
        {
          "line": 261,
          "text": "\"shadow_run_id\","
        },
        {
          "line": 265,
          "text": "\"shadow_override_id\","
        },
        {
          "line": 268,
          "text": "\"shadow_pnl\","
        },
        {
          "line": 271,
          "text": "\"shadow_trade_count\","
        },
        {
          "line": 274,
          "text": "\"shadow_candidate_count\","
        },
        {
          "line": 277,
          "text": "\"shadow_blocker_count\","
        },
        {
          "line": 280,
          "text": "\"shadow_regime_pass_count\","
        },
        {
          "line": 293,
          "text": "\"shadow_value\","
        }
      ]
    },
    {
      "hit_count": 110,
      "path": "app/mme_scalpx/replay/contracts.py",
      "sample_hits": [
        {
          "line": 60,
          "text": "ARTIFACT_RESEARCH_SUMMARY_JSON = \"19_research_summary.json\""
        },
        {
          "line": 79,
          "text": "ARTIFACT_RESEARCH_SUMMARY_JSON,"
        },
        {
          "line": 240,
          "text": "\"shadow_label\","
        },
        {
          "line": 253,
          "text": "\"research_tags\","
        },
        {
          "line": 261,
          "text": "\"shadow_run_id\","
        },
        {
          "line": 265,
          "text": "\"shadow_override_id\","
        },
        {
          "line": 268,
          "text": "\"shadow_pnl\","
        },
        {
          "line": 271,
          "text": "\"shadow_trade_count\","
        },
        {
          "line": 274,
          "text": "\"shadow_candidate_count\","
        },
        {
          "line": 277,
          "text": "\"shadow_blocker_count\","
        },
        {
          "line": 280,
          "text": "\"shadow_regime_pass_count\","
        },
        {
          "line": 293,
          "text": "\"shadow_value\","
        }
      ]
    },
    {
      "hit_count": 77,
      "path": "app/mme_scalpx/replay/comparison_artifacts.py",
      "sample_hits": [
        {
          "line": 4,
          "text": "Deterministic baseline-vs-shadow comparison artifact builder for replay studies."
        },
        {
          "line": 36,
          "text": "shadow_frames: Iterable[Mapping[str, Any]],"
        },
        {
          "line": 39,
          "text": "shadow_label: str = \"shadow\","
        },
        {
          "line": 42,
          "text": "shadow_index = _index_frames(shadow_frames, context=\"shadow_frames\")"
        },
        {
          "line": 45,
          "text": "shadow_ids = set(shadow_index)"
        },
        {
          "line": 46,
          "text": "shared_ids = sorted(baseline_ids & shadow_ids)"
        },
        {
          "line": 53,
          "text": "shadow = shadow_index[frame_id]"
        },
        {
          "line": 56,
          "text": "shadow_candidate = _as_bool(shadow[\"candidate\"], \"shadow.candidate\")"
        },
        {
          "line": 58,
          "text": "changed = baseline_candidate != shadow_candidate"
        },
        {
          "line": 59,
          "text": "newly_admitted = (not baseline_candidate) and shadow_candidate"
        },
        {
          "line": 60,
          "text": "removed_in_shadow = baseline_candidate and (not shadow_candidate)"
        },
        {
          "line": 70,
          "text": "\"shadow_candidate\": shadow_candidate,"
        }
      ]
    },
    {
      "hit_count": 77,
      "path": "app/mme_scalpx/replay/comparison_artifacts.py",
      "sample_hits": [
        {
          "line": 4,
          "text": "Deterministic baseline-vs-shadow comparison artifact builder for replay studies."
        },
        {
          "line": 36,
          "text": "shadow_frames: Iterable[Mapping[str, Any]],"
        },
        {
          "line": 39,
          "text": "shadow_label: str = \"shadow\","
        },
        {
          "line": 42,
          "text": "shadow_index = _index_frames(shadow_frames, context=\"shadow_frames\")"
        },
        {
          "line": 45,
          "text": "shadow_ids = set(shadow_index)"
        },
        {
          "line": 46,
          "text": "shared_ids = sorted(baseline_ids & shadow_ids)"
        },
        {
          "line": 53,
          "text": "shadow = shadow_index[frame_id]"
        },
        {
          "line": 56,
          "text": "shadow_candidate = _as_bool(shadow[\"candidate\"], \"shadow.candidate\")"
        },
        {
          "line": 58,
          "text": "changed = baseline_candidate != shadow_candidate"
        },
        {
          "line": 59,
          "text": "newly_admitted = (not baseline_candidate) and shadow_candidate"
        },
        {
          "line": 60,
          "text": "removed_in_shadow = baseline_candidate and (not shadow_candidate)"
        },
        {
          "line": 70,
          "text": "\"shadow_candidate\": shadow_candidate,"
        }
      ]
    },
    {
      "hit_count": 70,
      "path": "app/mme_scalpx/replay/metrics.py",
      "sample_hits": [
        {
          "line": 4,
          "text": "Replay comparison metrics for baseline-vs-shadow studies."
        },
        {
          "line": 26,
          "text": "shadow_regime_pass_count: int"
        },
        {
          "line": 28,
          "text": "shadow_economics_valid_count: int"
        },
        {
          "line": 30,
          "text": "shadow_economics_source_insufficient_count: int"
        },
        {
          "line": 32,
          "text": "shadow_candidate_count: int"
        },
        {
          "line": 34,
          "text": "shadow_put_candidate_count: int"
        },
        {
          "line": 36,
          "text": "shadow_put_atm_count: int"
        },
        {
          "line": 38,
          "text": "shadow_put_atm1_candidate_count: int"
        },
        {
          "line": 39,
          "text": "newly_admitted_shadow_frames: int"
        },
        {
          "line": 40,
          "text": "new_shadow_put_atm_count: int"
        },
        {
          "line": 41,
          "text": "new_shadow_put_atm1_count: int"
        },
        {
          "line": 43,
          "text": "blocker_mix_shadow: dict[str, int]"
        }
      ]
    },
    {
      "hit_count": 70,
      "path": "app/mme_scalpx/replay/metrics.py",
      "sample_hits": [
        {
          "line": 4,
          "text": "Replay comparison metrics for baseline-vs-shadow studies."
        },
        {
          "line": 26,
          "text": "shadow_regime_pass_count: int"
        },
        {
          "line": 28,
          "text": "shadow_economics_valid_count: int"
        },
        {
          "line": 30,
          "text": "shadow_economics_source_insufficient_count: int"
        },
        {
          "line": 32,
          "text": "shadow_candidate_count: int"
        },
        {
          "line": 34,
          "text": "shadow_put_candidate_count: int"
        },
        {
          "line": 36,
          "text": "shadow_put_atm_count: int"
        },
        {
          "line": 38,
          "text": "shadow_put_atm1_candidate_count: int"
        },
        {
          "line": 39,
          "text": "newly_admitted_shadow_frames: int"
        },
        {
          "line": 40,
          "text": "new_shadow_put_atm_count: int"
        },
        {
          "line": 41,
          "text": "new_shadow_put_atm1_count: int"
        },
        {
          "line": 43,
          "text": "blocker_mix_shadow: dict[str, int]"
        }
      ]
    },
    {
      "hit_count": 61,
      "path": "app/mme_scalpx/replay/miv_research_evaluator.py",
      "sample_hits": [
        {
          "line": 14,
          "text": "MIV_EVALUATOR_VERSION = \"miv_zerodha_lite_research_evaluator_v0_1_r2\""
        },
        {
          "line": 171,
          "text": "return 0.45, True, \"spread_wide_but_research_acceptable\""
        },
        {
          "line": 196,
          "text": "def _candidate_id("
        },
        {
          "line": 231,
          "text": "trade_shadow_eligible = not label_only and score_total >= MIV.MIV_SCORE_MIN_RESEARCH and not hard_blocked"
        },
        {
          "line": 243,
          "text": "\"schema_version\": \"miv_research_candidate_v0_1\","
        },
        {
          "line": 249,
          "text": "\"research_mode\": MIV.MIV_MODE_ZERODHA_LITE,"
        },
        {
          "line": 251,
          "text": "\"miv_candidate_id\": _candidate_id(run_id, dataset_id, candidate_type, symbol, event_ns, score_total),"
        },
        {
          "line": 264,
          "text": "\"research_shadow_only\": True,"
        },
        {
          "line": 266,
          "text": "\"trade_shadow_eligible\": bool(trade_shadow_eligible),"
        },
        {
          "line": 268,
          "text": "\"route_to_risk_shadow\": bool(trade_shadow_eligible),"
        },
        {
          "line": 269,
          "text": "\"route_to_execution_shadow\": bool(trade_shadow_eligible),"
        },
        {
          "line": 270,
          "text": "\"route_to_order_intent_ledger\": bool(trade_shadow_eligible),"
        }
      ]
    },
    {
      "hit_count": 61,
      "path": "app/mme_scalpx/replay/miv_research_evaluator.py",
      "sample_hits": [
        {
          "line": 14,
          "text": "MIV_EVALUATOR_VERSION = \"miv_zerodha_lite_research_evaluator_v0_1_r2\""
        },
        {
          "line": 171,
          "text": "return 0.45, True, \"spread_wide_but_research_acceptable\""
        },
        {
          "line": 196,
          "text": "def _candidate_id("
        },
        {
          "line": 231,
          "text": "trade_shadow_eligible = not label_only and score_total >= MIV.MIV_SCORE_MIN_RESEARCH and not hard_blocked"
        },
        {
          "line": 243,
          "text": "\"schema_version\": \"miv_research_candidate_v0_1\","
        },
        {
          "line": 249,
          "text": "\"research_mode\": MIV.MIV_MODE_ZERODHA_LITE,"
        },
        {
          "line": 251,
          "text": "\"miv_candidate_id\": _candidate_id(run_id, dataset_id, candidate_type, symbol, event_ns, score_total),"
        },
        {
          "line": 264,
          "text": "\"research_shadow_only\": True,"
        },
        {
          "line": 266,
          "text": "\"trade_shadow_eligible\": bool(trade_shadow_eligible),"
        },
        {
          "line": 268,
          "text": "\"route_to_risk_shadow\": bool(trade_shadow_eligible),"
        },
        {
          "line": 269,
          "text": "\"route_to_execution_shadow\": bool(trade_shadow_eligible),"
        },
        {
          "line": 270,
          "text": "\"route_to_order_intent_ledger\": bool(trade_shadow_eligible),"
        }
      ]
    },
    {
      "hit_count": 59,
      "path": "app/mme_scalpx/replay/differential.py",
      "sample_hits": [
        {
          "line": 10,
          "text": "- canonical baseline-vs-shadow comparison contracts"
        },
        {
          "line": 25,
          "text": "- differential comparison must always remain explicit baseline vs shadow"
        },
        {
          "line": 59,
          "text": "shadow_value: Any"
        },
        {
          "line": 71,
          "text": "shadow_run_id: str"
        },
        {
          "line": 73,
          "text": "shadow_integrity_verdict: str"
        },
        {
          "line": 75,
          "text": "shadow_final_state: str"
        },
        {
          "line": 77,
          "text": "shadow_stage_count: int"
        },
        {
          "line": 85,
          "text": "Canonical aggregate baseline-vs-shadow comparison bundle."
        },
        {
          "line": 89,
          "text": "shadow_run_id: str"
        },
        {
          "line": 107,
          "text": "shadow_engine_result: ReplayEngineResult,"
        },
        {
          "line": 109,
          "text": "shadow_integrity_bundle: ReplayIntegrityBundle,"
        },
        {
          "line": 119,
          "text": "shadow_engine_result,"
        }
      ]
    },
    {
      "hit_count": 59,
      "path": "app/mme_scalpx/replay/differential.py",
      "sample_hits": [
        {
          "line": 10,
          "text": "- canonical baseline-vs-shadow comparison contracts"
        },
        {
          "line": 25,
          "text": "- differential comparison must always remain explicit baseline vs shadow"
        },
        {
          "line": 59,
          "text": "shadow_value: Any"
        },
        {
          "line": 71,
          "text": "shadow_run_id: str"
        },
        {
          "line": 73,
          "text": "shadow_integrity_verdict: str"
        },
        {
          "line": 75,
          "text": "shadow_final_state: str"
        },
        {
          "line": 77,
          "text": "shadow_stage_count: int"
        },
        {
          "line": 85,
          "text": "Canonical aggregate baseline-vs-shadow comparison bundle."
        },
        {
          "line": 89,
          "text": "shadow_run_id: str"
        },
        {
          "line": 107,
          "text": "shadow_engine_result: ReplayEngineResult,"
        },
        {
          "line": 109,
          "text": "shadow_integrity_bundle: ReplayIntegrityBundle,"
        },
        {
          "line": 119,
          "text": "shadow_engine_result,"
        }
      ]
    },
    {
      "hit_count": 53,
      "path": "app/mme_scalpx/replay/execution_shadow.py",
      "sample_hits": [
        {
          "line": 10,
          "text": "REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = \"replay_execution_shadow_v1\""
        },
        {
          "line": 12,
          "text": "REPLAY_SHADOW_FILL_POLICIES = ("
        },
        {
          "line": 19,
          "text": "REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS = ("
        },
        {
          "line": 30,
          "text": "\"shadow_position_state\","
        },
        {
          "line": 31,
          "text": "\"shadow_trade_log\","
        },
        {
          "line": 32,
          "text": "\"shadow_pnl_summary\","
        },
        {
          "line": 42,
          "text": "class ReplayShadowAssumptionProfile:"
        },
        {
          "line": 57,
          "text": "def replay_shadow_assumption_profile(**kwargs: Any) -> dict[str, Any]:"
        },
        {
          "line": 58,
          "text": "profile = ReplayShadowAssumptionProfile(**kwargs)"
        },
        {
          "line": 59,
          "text": "if profile.fill_policy not in REPLAY_SHADOW_FILL_POLICIES:"
        },
        {
          "line": 60,
          "text": "raise ValueError(f\"unsupported replay shadow fill_policy: {profile.fill_policy}\")"
        },
        {
          "line": 77,
          "text": "def simulate_replay_execution_shadow("
        }
      ]
    },
    {
      "hit_count": 53,
      "path": "app/mme_scalpx/replay/execution_shadow.py",
      "sample_hits": [
        {
          "line": 10,
          "text": "REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = \"replay_execution_shadow_v1\""
        },
        {
          "line": 12,
          "text": "REPLAY_SHADOW_FILL_POLICIES = ("
        },
        {
          "line": 19,
          "text": "REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS = ("
        },
        {
          "line": 30,
          "text": "\"shadow_position_state\","
        },
        {
          "line": 31,
          "text": "\"shadow_trade_log\","
        },
        {
          "line": 32,
          "text": "\"shadow_pnl_summary\","
        },
        {
          "line": 42,
          "text": "class ReplayShadowAssumptionProfile:"
        },
        {
          "line": 57,
          "text": "def replay_shadow_assumption_profile(**kwargs: Any) -> dict[str, Any]:"
        },
        {
          "line": 58,
          "text": "profile = ReplayShadowAssumptionProfile(**kwargs)"
        },
        {
          "line": 59,
          "text": "if profile.fill_policy not in REPLAY_SHADOW_FILL_POLICIES:"
        },
        {
          "line": 60,
          "text": "raise ValueError(f\"unsupported replay shadow fill_policy: {profile.fill_policy}\")"
        },
        {
          "line": 77,
          "text": "def simulate_replay_execution_shadow("
        }
      ]
    },
    {
      "hit_count": 49,
      "path": "app/mme_scalpx/services/strategy_family/misls.py",
      "sample_hits": [
        {
          "line": 8,
          "text": "Freeze-grade dormant shadow validator."
        },
        {
          "line": 17,
          "text": "- shadow candidate only inside metadata"
        },
        {
          "line": 229,
          "text": "def _extend_misls_candidates(candidates: list[dict[str, Any]], value: Any) -> None:"
        },
        {
          "line": 232,
          "text": "_extend_misls_candidates(candidates, item)"
        },
        {
          "line": 239,
          "text": "for child_key in (\"events\", \"candidates\", \"shadow_candidates\"):"
        },
        {
          "line": 245,
          "text": "candidates.append(row_map)"
        },
        {
          "line": 249,
          "text": "candidates.append(child_map)"
        },
        {
          "line": 257,
          "text": "final_classification = safe_str(item.get(\"final_classification\"))"
        },
        {
          "line": 261,
          "text": "if branch or final_classification or event_id or family == FAMILY_ID:"
        },
        {
          "line": 262,
          "text": "candidates.append(item)"
        },
        {
          "line": 268,
          "text": "candidates: list[dict[str, Any]] = []"
        },
        {
          "line": 270,
          "text": "_extend_misls_candidates(candidates, view)"
        }
      ]
    },
    {
      "hit_count": 49,
      "path": "app/mme_scalpx/services/strategy_family/misls.py",
      "sample_hits": [
        {
          "line": 8,
          "text": "Freeze-grade dormant shadow validator."
        },
        {
          "line": 17,
          "text": "- shadow candidate only inside metadata"
        },
        {
          "line": 229,
          "text": "def _extend_misls_candidates(candidates: list[dict[str, Any]], value: Any) -> None:"
        },
        {
          "line": 232,
          "text": "_extend_misls_candidates(candidates, item)"
        },
        {
          "line": 239,
          "text": "for child_key in (\"events\", \"candidates\", \"shadow_candidates\"):"
        },
        {
          "line": 245,
          "text": "candidates.append(row_map)"
        },
        {
          "line": 249,
          "text": "candidates.append(child_map)"
        },
        {
          "line": 257,
          "text": "final_classification = safe_str(item.get(\"final_classification\"))"
        },
        {
          "line": 261,
          "text": "if branch or final_classification or event_id or family == FAMILY_ID:"
        },
        {
          "line": 262,
          "text": "candidates.append(item)"
        },
        {
          "line": 268,
          "text": "candidates: list[dict[str, Any]] = []"
        },
        {
          "line": 270,
          "text": "_extend_misls_candidates(candidates, view)"
        }
      ]
    },
    {
      "hit_count": 46,
      "path": "app/mme_scalpx/services/feature_family/contracts.py",
      "sample_hits": [
        {
          "line": 11,
          "text": "- the canonical family_features payload contract consumed by strategy-family"
        },
        {
          "line": 30,
          "text": "- services/features.py publishes the family_features payload"
        },
        {
          "line": 58,
          "text": "FAMILY_FEATURES_VERSION: Final[str] = \"1.1\""
        },
        {
          "line": 138,
          "text": "KEY_FAMILY_FEATURES_VERSION: Final[str] = \"family_features_version\""
        },
        {
          "line": 150,
          "text": "KEY_FAMILY_FEATURES_VERSION,"
        },
        {
          "line": 399,
          "text": "\"shadow_call_strike\","
        },
        {
          "line": 400,
          "text": "\"shadow_put_strike\","
        },
        {
          "line": 1117,
          "text": "\"shadow_call_strike\": None,"
        },
        {
          "line": 1118,
          "text": "\"shadow_put_strike\": None,"
        },
        {
          "line": 1134,
          "text": "def build_empty_family_features_payload("
        },
        {
          "line": 1138,
          "text": "family_features_version: str = FAMILY_FEATURES_VERSION,"
        },
        {
          "line": 1145,
          "text": "fields may remain None. Use validate_publishable_family_features_payload() to"
        }
      ]
    },
    {
      "hit_count": 46,
      "path": "app/mme_scalpx/services/feature_family/contracts.py",
      "sample_hits": [
        {
          "line": 11,
          "text": "- the canonical family_features payload contract consumed by strategy-family"
        },
        {
          "line": 30,
          "text": "- services/features.py publishes the family_features payload"
        },
        {
          "line": 58,
          "text": "FAMILY_FEATURES_VERSION: Final[str] = \"1.1\""
        },
        {
          "line": 138,
          "text": "KEY_FAMILY_FEATURES_VERSION: Final[str] = \"family_features_version\""
        },
        {
          "line": 150,
          "text": "KEY_FAMILY_FEATURES_VERSION,"
        },
        {
          "line": 399,
          "text": "\"shadow_call_strike\","
        },
        {
          "line": 400,
          "text": "\"shadow_put_strike\","
        },
        {
          "line": 1117,
          "text": "\"shadow_call_strike\": None,"
        },
        {
          "line": 1118,
          "text": "\"shadow_put_strike\": None,"
        },
        {
          "line": 1134,
          "text": "def build_empty_family_features_payload("
        },
        {
          "line": 1138,
          "text": "family_features_version: str = FAMILY_FEATURES_VERSION,"
        },
        {
          "line": 1145,
          "text": "fields may remain None. Use validate_publishable_family_features_payload() to"
        }
      ]
    },
    {
      "hit_count": 44,
      "path": "app/mme_scalpx/replay/report_exporter.py",
      "sample_hits": [
        {
          "line": 30,
          "text": "\"07_pnl_execution_shadow_summary.csv\","
        },
        {
          "line": 31,
          "text": "\"07_pnl_execution_shadow_summary.json\","
        },
        {
          "line": 32,
          "text": "\"08_baseline_vs_shadow_comparison.json\","
        },
        {
          "line": 38,
          "text": "return json.loads(json.dumps(value, sort_keys=True, default=str))"
        },
        {
          "line": 44,
          "text": "path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True), encoding=\"utf-8\")"
        },
        {
          "line": 52,
          "text": "with path.open(\"w\", encoding=\"utf-8\", newline=\"\") as fh:"
        },
        {
          "line": 67,
          "text": "exec_summary = dict(result.get(\"execution_shadow_summary\") or {})"
        },
        {
          "line": 78,
          "text": "\"research_trade_allowed\": risk_summary.get(\"research_trade_allowed\"),"
        },
        {
          "line": 105,
          "text": "\"candidate_id\": f\"{result.get('run_id')}|{family}|{side}\","
        },
        {
          "line": 182,
          "text": "\"filled_qty_total\": sum(int(row.get(\"execution_shadow_summary\", {}).get(\"filled_qty\") or 0) for row in subset),"
        },
        {
          "line": 183,
          "text": "\"net_pnl_total\": sum(float(row.get(\"execution_shadow_summary\", {}).get(\"net_pnl\") or 0.0) for row in subset),"
        },
        {
          "line": 191,
          "text": "def build_pnl_execution_shadow_summary(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:"
        }
      ]
    },
    {
      "hit_count": 44,
      "path": "app/mme_scalpx/replay/report_exporter.py",
      "sample_hits": [
        {
          "line": 30,
          "text": "\"07_pnl_execution_shadow_summary.csv\","
        },
        {
          "line": 31,
          "text": "\"07_pnl_execution_shadow_summary.json\","
        },
        {
          "line": 32,
          "text": "\"08_baseline_vs_shadow_comparison.json\","
        },
        {
          "line": 38,
          "text": "return json.loads(json.dumps(value, sort_keys=True, default=str))"
        },
        {
          "line": 44,
          "text": "path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True), encoding=\"utf-8\")"
        },
        {
          "line": 52,
          "text": "with path.open(\"w\", encoding=\"utf-8\", newline=\"\") as fh:"
        },
        {
          "line": 67,
          "text": "exec_summary = dict(result.get(\"execution_shadow_summary\") or {})"
        },
        {
          "line": 78,
          "text": "\"research_trade_allowed\": risk_summary.get(\"research_trade_allowed\"),"
        },
        {
          "line": 105,
          "text": "\"candidate_id\": f\"{result.get('run_id')}|{family}|{side}\","
        },
        {
          "line": 182,
          "text": "\"filled_qty_total\": sum(int(row.get(\"execution_shadow_summary\", {}).get(\"filled_qty\") or 0) for row in subset),"
        },
        {
          "line": 183,
          "text": "\"net_pnl_total\": sum(float(row.get(\"execution_shadow_summary\", {}).get(\"net_pnl\") or 0.0) for row in subset),"
        },
        {
          "line": 191,
          "text": "def build_pnl_execution_shadow_summary(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:"
        }
      ]
    },
    {
      "hit_count": 43,
      "path": "app/mme_scalpx/research_capture/contracts.py",
      "sample_hits": [
        {
          "line": 4,
          "text": "app/mme_scalpx/research_capture/contracts.py"
        },
        {
          "line": 6,
          "text": "Frozen contract surface for the MME research data capture chapter."
        },
        {
          "line": 10,
          "text": "This module freezes the symbolic contract for research/archive capture so that"
        },
        {
          "line": 19,
          "text": "- field specifications for research capture"
        },
        {
          "line": 37,
          "text": "- researched != contract-changed"
        },
        {
          "line": 40,
          "text": "- Redis is hot/latest/live only; archive Parquet is long-term research truth"
        },
        {
          "line": 48,
          "text": "SCHEMA_NAME = \"MME Research Data Capture Schema\""
        },
        {
          "line": 50,
          "text": "CONSTITUTION_NAME = \"MME Research Data Capture Constitution v1\""
        },
        {
          "line": 52,
          "text": "CHAPTER_NAME = \"research_capture\""
        },
        {
          "line": 55,
          "text": "\"research/archive contract only\","
        },
        {
          "line": 59,
          "text": "\"researched != contract-changed\","
        },
        {
          "line": 62,
          "text": "ARCHIVE_ROOT_RELATIVE = \"run/research_capture\""
        }
      ]
    },
    {
      "hit_count": 40,
      "path": "app/mme_scalpx/replay/feature_adapter.py",
      "sample_hits": [
        {
          "line": 20,
          "text": "\"family_features\","
        },
        {
          "line": 21,
          "text": "\"family_surfaces\","
        },
        {
          "line": 22,
          "text": "\"family_features_json\","
        },
        {
          "line": 23,
          "text": "\"family_surfaces_json\","
        },
        {
          "line": 82,
          "text": "family_features_json: str"
        },
        {
          "line": 83,
          "text": "family_surfaces_json: str"
        },
        {
          "line": 92,
          "text": "return json.dumps(value, sort_keys=True, separators=(\",\", \":\"), default=str)"
        },
        {
          "line": 174,
          "text": "def build_replay_family_surfaces(row: Mapping[str, Any]) -> dict[str, Any]:"
        },
        {
          "line": 175,
          "text": "family_surfaces: dict[str, Any] = {}"
        },
        {
          "line": 177,
          "text": "family_surfaces[family] = {}"
        },
        {
          "line": 179,
          "text": "family_surfaces[family][side] = _family_side_surface(row, family=family, side=side)"
        },
        {
          "line": 180,
          "text": "return family_surfaces"
        }
      ]
    },
    {
      "hit_count": 40,
      "path": "app/mme_scalpx/replay/feature_adapter.py",
      "sample_hits": [
        {
          "line": 20,
          "text": "\"family_features\","
        },
        {
          "line": 21,
          "text": "\"family_surfaces\","
        },
        {
          "line": 22,
          "text": "\"family_features_json\","
        },
        {
          "line": 23,
          "text": "\"family_surfaces_json\","
        },
        {
          "line": 82,
          "text": "family_features_json: str"
        },
        {
          "line": 83,
          "text": "family_surfaces_json: str"
        },
        {
          "line": 92,
          "text": "return json.dumps(value, sort_keys=True, separators=(\",\", \":\"), default=str)"
        },
        {
          "line": 174,
          "text": "def build_replay_family_surfaces(row: Mapping[str, Any]) -> dict[str, Any]:"
        },
        {
          "line": 175,
          "text": "family_surfaces: dict[str, Any] = {}"
        },
        {
          "line": 177,
          "text": "family_surfaces[family] = {}"
        },
        {
          "line": 179,
          "text": "family_surfaces[family][side] = _family_side_surface(row, family=family, side=side)"
        },
        {
          "line": 180,
          "text": "return family_surfaces"
        }
      ]
    }
  ]
}
```

## Contract

docs/contracts/MISLS_R4_shadow_logger_design_contract.md

## Safety

NO source patch
NO service start
NO replay start
NO broker order
NO paper
NO risk start
NO execution start
NO Redis delete