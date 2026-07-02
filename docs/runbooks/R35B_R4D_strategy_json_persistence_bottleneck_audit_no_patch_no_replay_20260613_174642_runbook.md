# R35B_R4D_strategy_json_persistence_bottleneck_audit_no_patch_no_replay_20260613_174642

classification: PASS_R35B_R4D_STRATEGY_JSON_PERSISTENCE_BOTTLENECK_CAPTURED_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4D_strategy_json_persistence_bottleneck_audit_no_patch_no_replay_20260613_174642.json`
audit: `run/audits/R35B_R4D_strategy_json_persistence_bottleneck_audit_no_patch_no_replay_20260613_174642`

## match_count
201

## Safety
orders/risk/execution: 0 / 0 / 0
risk/execution proc: 0 / 0

## Replay output persistence lines
  3380	        checks=build_placeholder_checks(
  3381	            allow_option_only_fut_context=bool(args.allow_option_only_fut_context),
  3382	        ),
  3383	    )
  3384	
  3385	    report_bundle = build_report_bundle(
  3386	        run_context=run_context,
  3387	        selection_plan=selection_plan,
  3388	        topology_plan=topology_plan,
  3389	        engine_result=engine_result,
  3390	        integrity_bundle=integrity_bundle,
  3391	    )
  3392	
  3393	    writer = ReplayArtifactsWriter()
  3394	    writer.ensure_directories(run_context.artifact_plan)
  3395	    artifact_bundle = writer.write_core_artifact_bundle(
  3396	        run_context,
  3397	        topology_plan,
  3398	        integrity_verdict=integrity_bundle.verdict.value,
  3399	        metrics={"stage_count": engine_result.stage_count},
  3400	    )
  3401	    writer.write_engine_result(engine_result, run_context.artifact_plan)
  3402	
  3403	    replay_artifacts_dir = Path(run_context.artifact_plan.artifacts_dir)
  3404	    replay_artifacts_dir.mkdir(parents=True, exist_ok=True)
  3405	
  3406	    persisted_feature_rows = build_persisted_feature_rows(transport.feature_frames)
  3407	
  3408	    (replay_artifacts_dir / "features_rows.json").write_text(
  3409	        json.dumps(persisted_feature_rows, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
  3410	        encoding="utf-8",
  3411	    )
  3412	    persisted_strategy_decisions = build_persisted_strategy_decisions(
  3413	        transport.strategy_decisions,
  3414	        persisted_feature_rows,
  3415	    )
  3416	
  3417	    (replay_artifacts_dir / "strategy_decisions.json").write_text(
  3418	        json.dumps(persisted_strategy_decisions, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
  3419	        encoding="utf-8",
  3420	    )
  3421	    persisted_risk_outputs = build_persisted_risk_outputs(
  3422	        transport.risk_outputs,
  3423	        persisted_strategy_decisions,
  3424	    )
  3425	
  3426	    (replay_artifacts_dir / "risk_outputs.json").write_text(
  3427	        json.dumps(persisted_risk_outputs, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
  3428	        encoding="utf-8",
  3429	    )
  3430	
  3431	    persisted_execution_shadow_results = [dict(row) for row in transport.execution_shadow_results]
  3432	
  3433	    (replay_artifacts_dir / "execution_shadow_results.json").write_text(
  3434	        json.dumps(persisted_execution_shadow_results, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
  3435	        encoding="utf-8",

## Strategy adapter candidate JSON lines
    55	
    56	
    57	@dataclass(frozen=True)
    58	class ReplayStrategyAdapterResult:
    59	    schema_version: str
    60	    run_id: str
    61	    candidates: tuple[dict[str, Any], ...]
    62	    arbitration: dict[str, Any]
    63	    decision_payload: dict[str, Any]
    64	    strategy_decision_generated: bool = True
    65	    real_order_intent_generated: bool = False
    66	    paper_armed_approved: bool = False
    67	    live_trading_approved: bool = False
    68	    execution_arming_created: bool = False
    69	    production_doctrine_changed: bool = False
    70	
    71	
    72	def _canonical_json(value: Any) -> str:
    73	    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    74	
    75	
    76	def _truthy(value: Any) -> bool:
    77	    if isinstance(value, str):
    78	        return value.strip().lower() in {"1", "true", "yes", "y", "ok", "pass"}
    79	    return bool(value)
    80	
    81	
    82	def _family_surface_score(family: str, surface: Mapping[str, Any]) -> tuple[float, tuple[str, ...]]:
    83	    terms = REPLAY_FAMILY_REQUIRED_SURFACE_TERMS[family]
    84	    blockers: list[str] = []
    85	    score = 0.0
    86	
    87	    for term in terms:
    88	        value = surface.get(term)
    89	        if isinstance(value, bool):
    90	            if value:
    91	                score += 1.0
    92	            else:
    93	                blockers.append(f"{term}_false")
    94	        elif value is None:
    95	            blockers.append(f"{term}_missing")

   215	def build_replay_strategy_decision_payload(
   216	    *,
   217	    run_id: str,
   218	    feature_payload: Mapping[str, Any],
   219	) -> ReplayStrategyAdapterResult:
   220	    candidates = build_replay_strategy_candidates(run_id=run_id, feature_payload=feature_payload)
   221	    arbitration = arbitrate_replay_strategy_candidates(run_id=run_id, candidates=candidates)
   222	
   223	    decision_payload = {
   224	        "schema_version": REPLAY_STRATEGY_ADAPTER_CONTRACT_VERSION,
   225	        "run_id": str(run_id),
   226	        "candidates": candidates,
   227	        "candidate_count": len(candidates),
   228	        "arbitration": arbitration,
   229	        "final_action": "HOLD_REPORT_ONLY",
   230	        "action": "HOLD_REPORT_ONLY",
   231	        "order_allowed": False,
   232	        "real_order_intent_generated": False,
   233	        "strategy_decision_generated": True,
   234	        "strategy_decision_replay_only": True,
   235	        "strategy_decision_parity": "NOT_PROVEN_IN_27H",
   236	        "safe_decision_shape_parity": "PROVEN_BY_27H",
   237	        "candidate_json": _canonical_json(candidates),
   238	        "arbitration_json": _canonical_json(arbitration),
   239	        "paper_armed_approved": False,
   240	        "live_trading_approved": False,
   241	        "execution_arming_created": False,
   242	        "production_doctrine_changed": False,
   243	    }
   244	
   245	    return ReplayStrategyAdapterResult(
   246	        schema_version=REPLAY_STRATEGY_ADAPTER_CONTRACT_VERSION,
   247	        run_id=str(run_id),
   248	        candidates=tuple(dict(c) for c in candidates),
   249	        arbitration=arbitration,
   250	        decision_payload=decision_payload,

## Existing R35B R4C logs
run/audits/R35B_R4C_june12_strategy_shortpath_20260613_174035/replay.log
run/audits/R35B_R4C_june12_strategy_shortpath_20260613_174035_report.md

## Existing partial run roots
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/00_manifest.json 3947 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/01_dataset_summary.json 6557 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/02_scope_profile.json 10946 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/03_integrity_report.json 55 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/04_metrics_summary.json 59 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/06_candidate_audit.csv 202 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/17_effective_inputs.json 2308 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/18_effective_overrides_flat.json 285 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/artifacts/b3_r32_analysis_exports_status.json 783 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/artifacts/blocker_distribution.csv 113 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/artifacts/economics_summary.json 10361 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/artifacts/engine_result.json 3143 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/artifacts/family_side_summary.csv 81 bytes
run/replay/r35b_r4c/20260613_174035/replay_locked_single_day_r35b_r4c_june12_strategy_20260613_121037_f14c5775/artifacts/features_rows.json 1599452734 bytes

## Grep serialization patterns
bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py:600:            print(json.dumps(sample, indent=2, sort_keys=True))
bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py:715:        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py:755:                json.dumps(req, indent=2, sort_keys=True),
bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py:804:        MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py:821:        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d34_candidate_replay_materialization.py:306:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d34_candidate_replay_materialization.py:340:}, indent=2, sort_keys=True))
bin/proof_observe_only_live_evidence_existing_proof_package.py:186:    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/proof_observe_only_live_evidence_existing_proof_package.py:208:    }, indent=2, sort_keys=True))
bin/proof_replay_final_no_live_contamination.py:148:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_final_no_live_contamination.py:162:    }, indent=2, sort_keys=True))
bin/proof_replay_optimization_d40_lane_d_freeze_summary.py:274:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d40_lane_d_freeze_summary.py:320:}, indent=2, sort_keys=True))
bin/b1_profit_live_recorder_backtest_handoff_builder.py:290:        pathlib.Path(args.proof).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
bin/b1_profit_live_recorder_backtest_handoff_builder.py:361:    pathlib.Path(args.replay_handoff).write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
bin/b1_profit_live_recorder_backtest_handoff_builder.py:362:    (audit_dir / "candidate_sessions.json").write_text(json.dumps(sessions[:100], indent=2, sort_keys=True) + "\n", encoding="utf-8")
bin/b1_profit_live_recorder_backtest_handoff_builder.py:363:    (audit_dir / "recorder_jsonl_stats.json").write_text(json.dumps(recorder_jsonl, indent=2, sort_keys=True) + "\n", encoding="utf-8")
bin/b1_profit_live_recorder_backtest_handoff_builder.py:364:    (audit_dir / "generic_gz_stats.json").write_text(json.dumps(gz_stats[:120], indent=2, sort_keys=True) + "\n", encoding="utf-8")
bin/b1_profit_live_recorder_backtest_handoff_builder.py:365:    (audit_dir / "jsonl_samples.json").write_text(json.dumps(jsonl_samples, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
bin/b1_profit_live_recorder_backtest_handoff_builder.py:378:    pathlib.Path(args.proof).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
bin/observe_only_market_session_package_collect.py:32:    print(json.dumps(result, indent=2, sort_keys=True, default=str))
bin/raw_t_post_raw_s_rerun.py:50:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_replay_optimization_d1_contracts.py:192:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d1_contracts.py:217:}, indent=2, sort_keys=True))
bin/proof_feeds_features_batch7_freeze.py:301:    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_feeds_features_batch7_freeze.py:302:    print(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_5family_producer_consumer_matrix.py:35:    print(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_batch26o16e_selected_option_feed_source_o8c_bridge.py:460:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16e_selected_option_feed_source_o8c_bridge.py:461:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16e_selected_option_feed_source_o8c_bridge.py:462:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:805:    DEEP_SURFACE_JSON.write_text(json.dumps(deep_surface, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:810:    CORRECTED_RANKING_JSON.write_text(json.dumps(corrected, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:817:    O23L_BUG_AUDIT_JSON.write_text(json.dumps(bug_audit, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:858:    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:915:    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:951:            json.dumps(req, indent=2, sort_keys=True),
bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py:1001:    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d2_sweep_space.py:289:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d2_sweep_space.py:325:}, indent=2, sort_keys=True))
bin/ensure_zerodha_shared_token.py:91:    SHARED_TOKEN.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
bin/proof_replay_optimization_d21_candidate_trade_readiness.py:283:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d21_candidate_trade_readiness.py:314:}, indent=2, sort_keys=True))
bin/raw_aa13b_economics_derivation.py:140:    pathlib.Path(ns.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
bin/raw_aa13b_economics_derivation.py:141:    print(json.dumps(summary, indent=2, sort_keys=True))
bin/proof_replay_workstation_acceptance_gate.py:262:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_workstation_acceptance_gate.py:278:    }, indent=2, sort_keys=True))
bin/proof_miv_r2_zerodha_lite_research_evaluator_no_replay_no_order.py:172:    }, indent=2, sort_keys=True))
bin/proof_strategy_family_shared_layer_contracts.py:364:    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_strategy_family_shared_layer_contracts.py:365:    print(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_contract_field_registry.py:395:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_contract_field_registry.py:408:    }, indent=2, sort_keys=True))
bin/proof_replay_optimization_d30_candidate_context_value_source.py:323:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d30_candidate_context_value_source.py:359:}, indent=2, sort_keys=True))
bin/proof_batch26o16h_final_data_valid_composition.py:521:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16h_final_data_valid_composition.py:522:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16h_final_data_valid_composition.py:523:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_batch26o16h_final_data_valid_composition.py:728:print(json.dumps(out, indent=2, sort_keys=True))
bin/replay_compare.py:152:        json.dumps(_json_safe_value(payload), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
bin/proof_batch26o16_consumer_view_mapping_repair.py:375:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16_consumer_view_mapping_repair.py:376:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16_consumer_view_mapping_repair.py:378:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_replay_optimization_d33_candidate_replay_binding_plan_validator.py:315:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d33_candidate_replay_binding_plan_validator.py:351:}, indent=2, sort_keys=True))
bin/proof_observe_only_market_session_operator_no_enablement.py:108:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_market_session_family_surfaces.py:111:    print(json.dumps(proof, indent=2, sort_keys=True))
bin/raw_aa13b_r3_true_row_artifact_resolver.py:490:    (RUN_DIR / "candidate_profiles.json").write_text(json.dumps(profiles, indent=2, sort_keys=True), encoding="utf-8")
bin/raw_aa13b_r3_true_row_artifact_resolver.py:491:    (RUN_DIR / "eligible_candidates.json").write_text(json.dumps(eligible, indent=2, sort_keys=True), encoding="utf-8")
bin/raw_aa13b_r3_true_row_artifact_resolver.py:492:    (RUN_DIR / "resolver_summary.json").write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/raw_aa13b_r3_true_row_artifact_resolver.py:493:    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/raw_aa13b_r3_true_row_artifact_resolver.py:514:    FREEZE_PATH.write_text(json.dumps(freeze, indent=2, sort_keys=True), encoding="utf-8")
bin/raw_aa13b_r3_true_row_artifact_resolver.py:583:    }, indent=2, sort_keys=True))
bin/observe_only_market_session_capture_execute.py:33:        print(json.dumps(market_session_status(), indent=2, sort_keys=True, default=str))
bin/observe_only_market_session_capture_execute.py:54:    print(json.dumps(result, indent=2, sort_keys=True, default=str))
bin/proof_batch26o16g_r2_runtime_symbol_provider_quality.py:584:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16g_r2_runtime_symbol_provider_quality.py:585:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16g_r2_runtime_symbol_provider_quality.py:586:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_batch26o16g_r2_runtime_symbol_provider_quality.py:791:print(json.dumps(out, indent=2, sort_keys=True))
bin/replay_build_comparison_summary.py:141:        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
bin/proof_feature_family_shared_core_guards.py:17:        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
bin/proof_feature_family_shared_core_guards.py:378:    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_feature_family_shared_core_guards.py:380:    print(json.dumps(proof["summary"], indent=2, sort_keys=True))
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py:175:                if "path=" in line and "strategy_decisions.json" in line:
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py:181:    hits = sh("find run/replay -path '*artifacts/strategy_decisions.json' -type f 2>/dev/null | sort | tail -1")
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py:204:    parser.add_argument("--input", default="", help="Replay strategy_decisions.json path. If empty, auto-discovers latest.")
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py:322:    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py:323:    print(json.dumps(proof, indent=2, sort_keys=True))
bin/guarded_offline_replay_dry_run_adapter_28p_r2.py:38:    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/guarded_offline_replay_dry_run_adapter_28p_r2.py:235:    print(json.dumps(result, indent=2, sort_keys=True))
bin/run_batch26o11_controlled_paper_monitor.py:145:    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
bin/run_batch26o11_controlled_paper_monitor.py:157:    }, indent=2, sort_keys=True))
bin/proof_order_intent_adapter_disabled.py:211:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26d_strategy_leaf_required_surface_failclosed.py:240:    PROOF.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
bin/proof_batch26d_strategy_leaf_required_surface_failclosed.py:303:    print(json.dumps(report["final_verdict"], indent=2, sort_keys=True))
bin/proof_replay_optimization_d8_result_binding.py:312:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d8_result_binding.py:360:}, indent=2, sort_keys=True))
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:533:    R4_REVIEW_JSON.write_text(json.dumps(r4_review, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:543:    LOG_REVIEW_JSON.write_text(json.dumps(log_review, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:586:    R3_REVIEW_JSON.write_text(json.dumps(r3_review, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:612:    NO_STREAM_JSON.write_text(json.dumps(no_stream_freeze, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:639:    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:692:    }, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:703:    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:739:            json.dumps(req, indent=2, sort_keys=True),
bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py:790:    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/prepair_safe.py:93:        print(json.dumps(proof, indent=2, sort_keys=True))
bin/prepair_safe.py:100:        print(json.dumps(proof, indent=2, sort_keys=True))
bin/prepair_safe.py:166:    print(json.dumps(proof, indent=2, sort_keys=True))
bin/replay_experiments.py:33:        print(json.dumps(experiment, indent=2, sort_keys=True, default=str))
bin/replay_experiments.py:40:    print(json.dumps(materialized, indent=2, sort_keys=True, default=str))
bin/proof_replay_optimization_d17_row_count_normalization.py:266:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d17_row_count_normalization.py:296:}, indent=2, sort_keys=True))
bin/proof_batch26o1_recovery_singleton_baseline.py:372:    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
bin/proof_batch26o1_recovery_singleton_baseline.py:379:    }, indent=2, sort_keys=True))
bin/proof_runtime_config_alignment.py:178:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_runtime_config_alignment.py:187:    }, indent=2, sort_keys=True))
bin/proof_oi_context_surface_audit.py:568:    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_oi_context_surface_audit.py:582:    }, indent=2, sort_keys=True))
bin/proof_replay_optimization_d42_post_result_pack_ingestion_schema.py:374:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d42_post_result_pack_ingestion_schema.py:424:}, indent=2, sort_keys=True))
bin/proof_replay_optimization_d43_label_binding_precondition_validator.py:402:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d43_label_binding_precondition_validator.py:460:}, indent=2, sort_keys=True))
bin/proof_strategy_hold_bridge_contract.py:16:        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
bin/proof_strategy_hold_bridge_contract.py:368:    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_strategy_hold_bridge_contract.py:370:    print(json.dumps(proof["summary"], indent=2, sort_keys=True))
bin/phealth_safe.py:381:    print(json.dumps(asdict(health), indent=2, sort_keys=True))
bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py:675:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py:676:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py:678:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_replay_optimization_d27_context_source_mapping.py:284:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d27_context_source_mapping.py:317:}, indent=2, sort_keys=True))
bin/proof_replay_optimization_d38_phase_gate_summary.py:279:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d38_phase_gate_summary.py:326:}, indent=2, sort_keys=True))
bin/raw_x_source_lineage_probe.py:31:print(json.dumps({"ok": ok, "outputs": out}, indent=2, sort_keys=True))
bin/proof_observe_only_market_session_capture_execution_no_enablement.py:121:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_no_runtime_promotion.py:60:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_no_runtime_promotion.py:68:    }, indent=2, sort_keys=True))
bin/proof_batch26o20_r3g_corrected_r3e_proof_parser.py:555:        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3g_corrected_r3e_proof_parser.py:593:                json.dumps(req, indent=2, sort_keys=True),
bin/proof_batch26o20_r3g_corrected_r3e_proof_parser.py:645:        MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3g_corrected_r3e_proof_parser.py:662:        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_live_parity_audit_plan.py:119:    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/proof_replay_live_parity_audit_plan.py:135:    }, indent=2, sort_keys=True))
bin/proof_aftermarket_broad_replay_materialization.py:380:    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))
bin/proof_or_publish_feed_snapshot_state.py:327:    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
bin/proof_or_publish_feed_snapshot_state.py:341:    }, indent=2, sort_keys=True))
bin/proof_replay_optimization_d24_match_key_adapter.py:281:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d24_match_key_adapter.py:315:}, indent=2, sort_keys=True))
bin/b1_capture_bundle_validator.py:384:    (out_dir / "capture_validator_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
bin/b1_capture_bundle_validator.py:385:    (out_dir / "family_admission_matrix.json").write_text(json.dumps(report["family_admission_matrix"], indent=2, sort_keys=True), encoding="utf-8")
bin/b1_capture_bundle_validator.py:386:    (out_dir / "identity_continuity_report.json").write_text(json.dumps(report["details"]["identity"], indent=2, sort_keys=True), encoding="utf-8")
bin/b1_capture_bundle_validator.py:387:    (out_dir / "lifecycle_presence_report.json").write_text(json.dumps(report["details"]["lifecycle"], indent=2, sort_keys=True), encoding="utf-8")
bin/b1_capture_bundle_validator.py:388:    (out_dir / "safety_validation_report.json").write_text(json.dumps(report["details"]["safety"], indent=2, sort_keys=True), encoding="utf-8")
bin/b1_capture_bundle_validator.py:394:    }, indent=2, sort_keys=True), encoding="utf-8")
bin/b1_capture_bundle_validator.py:414:    }, indent=2, sort_keys=True))
bin/proof_aftermarket_historical_replay_readiness.py:165:    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))
bin/proof_batch26o23_c_r1_completion_safety_readback.py:424:    }, indent=2, sort_keys=True)[:12000])
bin/proof_batch26o23_c_r1_completion_safety_readback.py:429:    print(json.dumps(stop_results, indent=2, sort_keys=True))
bin/proof_batch26o23_c_r1_completion_safety_readback.py:443:    }, indent=2, sort_keys=True)[:12000])
bin/proof_batch26o23_c_r1_completion_safety_readback.py:512:    }, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_c_r1_completion_safety_readback.py:524:    }, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_c_r1_completion_safety_readback.py:526:    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_c_r1_completion_safety_readback.py:551:            json.dumps(req, indent=2, sort_keys=True),
bin/proof_batch26o23_c_r1_completion_safety_readback.py:599:    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d14_grouped_precondition_audit.py:344:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d14_grouped_precondition_audit.py:395:}, indent=2, sort_keys=True))
bin/proof_repo_hygiene_quarantine.py:135:    latest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
bin/proof_repo_hygiene_quarantine.py:136:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_execution_family_entry_safety.py:526:    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str))
bin/proof_execution_family_entry_safety.py:527:    print(json.dumps(proof, indent=2, sort_keys=True, default=str))
bin/proof_strategy_candidate_metadata_contract.py:293:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_strategy_candidate_metadata_contract.py:303:    }, indent=2, sort_keys=True))
bin/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.py:536:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.py:537:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.py:538:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.py:706:    strategy_text = json.dumps(strategy_once.get("result"), sort_keys=True, default=str)
bin/proof_batch26o20_controlled_paper_extended_observation.py:368:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_controlled_paper_extended_observation.py:369:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_controlled_paper_extended_observation.py:370:    print(json.dumps(result, indent=2, sort_keys=True))
bin/raw_w_reports_hook_lineage_probe.py:60:    print(json.dumps({"ok": ok, "outputs": outputs}, indent=2, sort_keys=True))
bin/proof_batch26o20_r3_corrected_bounded_observation.py:525:    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3_corrected_bounded_observation.py:526:    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o20_r3_corrected_bounded_observation.py:528:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_or_publish_provider_runtime_state.py:275:    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
bin/proof_or_publish_provider_runtime_state.py:288:    }, indent=2, sort_keys=True))
bin/proof_replay_optimization_d28_context_enrichment_dry_run.py:320:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d28_context_enrichment_dry_run.py:356:}, indent=2, sort_keys=True))
bin/guarded_replay_engine_execute_dry_run_29g.py:313:    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/guarded_replay_engine_execute_dry_run_29g.py:349:    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/guarded_replay_engine_execute_dry_run_29g.py:994:    print(json.dumps(result, indent=2, sort_keys=True))
bin/audit_guarded_replay_engine_runtime_gap_29h.py:13:    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/audit_guarded_replay_engine_runtime_gap_29h.py:323:    print(json.dumps(result, indent=2, sort_keys=True))
bin/proof_main_batch4_freeze.py:275:    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_main_batch4_freeze.py:276:    print(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_observe_only_replay_input_dataset_preflight_28j.py:86:    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/proof_observe_only_replay_input_dataset_preflight_28j.py:482:print(json.dumps(proof, indent=2, sort_keys=True))
bin/proof_replay_optimization_d23_matching_dry_run.py:293:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d23_matching_dry_run.py:325:}, indent=2, sort_keys=True))
bin/replay_batch.py:72:        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
bin/replay_batch.py:81:    print(json.dumps(materialized, indent=2, sort_keys=True, default=str))
bin/proof_oi_family_soft_scoring.py:319:    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_oi_family_soft_scoring.py:333:    }, indent=2, sort_keys=True))
bin/proof_replay_report_exports.py:73:    candidate_json = read_json(root / "02_candidate_log.json")
bin/proof_replay_report_exports.py:83:    candidate_log_ok = len(candidate_json) == len(REPLAY_REQUIRED_SCENARIOS) * 10 and csv_row_count(root / "02_candidate_log.csv") == len(candidate_json)
bin/proof_replay_report_exports.py:119:            candidate_json,
bin/proof_replay_report_exports.py:195:    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")
bin/proof_replay_report_exports.py:214:    }, indent=2, sort_keys=True))
bin/raw_u_constructor_audit.py:54:    print(json.dumps(report, indent=2, sort_keys=True))
bin/patch_batch26c_risk_controlled_paper_veto.py:486:    PATCH_STEP.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
bin/patch_batch26c_risk_controlled_paper_veto.py:487:    print(json.dumps(report["verdict"], indent=2, sort_keys=True))
bin/proof_replay_integrity.py:167:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_integrity.py:180:    }, indent=2, sort_keys=True))
bin/proof_replay_feature_family_parity.py:251:    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_feature_family_parity.py:266:    }, indent=2, sort_keys=True))
bin/proof_replay_optimization_d15_result_pack_discovery.py:348:proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_replay_optimization_d15_result_pack_discovery.py:401:}, indent=2, sort_keys=True))
bin/_batch25v_market_observation_common.py:69:        json.dumps(dict(proof), indent=2, sort_keys=True, ensure_ascii=False, default=str),
bin/proof_miv_r1a_strategy_family_dormant_contract_no_replay_no_order.py:150:    }, indent=2, sort_keys=True))
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:846:    }, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:856:    }, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:999:            PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1015:            print(json.dumps(res, indent=2, sort_keys=True))
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1044:            print(json.dumps(compact, indent=2, sort_keys=True)[:8000])
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1074:        SAMPLE_REVIEW_JSON.write_text(json.dumps(sample_review, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1078:        SURFACE_MATRIX_JSON.write_text(json.dumps(surface_matrix, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1150:        NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1189:        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1226:                json.dumps(req, indent=2, sort_keys=True),
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1280:        MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py:1322:        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o15_activation_candidate_surface_audit.py:280:    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
bin/proof_batch26o15_activation_candidate_surface_audit.py:295:    }, indent=2, sort_keys=True))
bin/proof_paper_armed_readiness_gate_v2.py:148:    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:375:    print(json.dumps(proof["disk_state"], indent=2, sort_keys=True)[:6000])
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:384:    PRIOR_LOADER_JSON.write_text(json.dumps(prior_loader, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:459:    CORRECTED_EQUIVALENCE_JSON.write_text(json.dumps(corrected_equivalence, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:489:    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:537:    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:557:            json.dumps(corrected_equivalence, indent=2, sort_keys=True),
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:567:            json.dumps(req, indent=2, sort_keys=True),
bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py:614:    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
