# R35C_R4I_R4H_SUMMARY_AND_ARTIFACT_CAP_FAILURE_AUDIT_NO_REPLAY_NO_ORDER_20260613_223245

classification: PASS_R35C_R4I_R4H_FAILURE_AUDIT_DONE_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4I_R4H_SUMMARY_AND_ARTIFACT_CAP_FAILURE_AUDIT_NO_REPLAY_NO_ORDER_20260613_223245.json`

## Paths
R4H_ROOT=run/replay/r35c_r4h/20260613_222843
RUN_DIR=run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd
ART=run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts

## Safety
orders=0 risk=0 execution=0 proc=0/0 replay_proc=0

## Artifact sizes
662784524 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/features_rows.json
185213756 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/strategy_decisions.json
91105668 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/risk_outputs.json
40520799 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/execution_shadow_results.json
12622 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/02_scope_profile.json
10361 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/economics_summary.json
7811 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/03_integrity_report.json
7642 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/01_dataset_summary.json
5029 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/engine_result.json
3884 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/00_manifest.json
2483 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/10_run_summary.json
2336 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/17_effective_inputs.json
962 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/11_run_summary.csv
769 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/b3_r32_analysis_exports_status.json
278 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/18_effective_overrides_flat.json
233 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/10_run_summary_early_write_error.json
202 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/06_candidate_audit.csv
113 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/blocker_distribution.csv
81 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/artifacts/family_side_summary.csv
59 run/replay/r35c_r4h/20260613_222843/replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd/04_metrics_summary.json

## Early summary error
{
  "broker_order_attempted": false,
  "error": "TypeError(\"build_run_summary_payload() got an unexpected keyword argument 'selection_plan'\")",
  "paper_live_enabled": false,
  "schema_version": "r35c_r4c_early_summary_error_v1"
}

## Official run summary
{
  "batch_profile": null,
  "blocker_count": 59959,
  "candidate_count": 2109,
  "chapter": "replay",
  "completed_at": "2026-06-13T16:59:40Z",
  "created_at": "2026-06-13T16:58:51Z",
  "dataset_fingerprint": "e89b6fce7a913ecced77a4d48f448e561a88c591a52a1bf129baa515ac2f453c",
  "dataset_id": "r35c_r4h",
  "dataset_profile": null,
  "doctrine_mode": "locked",
  "duration_ms": null,
  "execution_shadow_action_breakdown": {},
  "execution_shadow_filled_count": 2109,
  "execution_shadow_row_count": 59959,
  "experiment_profile": null,
  "feature_blocker_non_null_count": 59959,
  "feature_candidate_true_count": 0,
  "feature_economics_valid_true_count": 0,
  "feature_leg_breakdown": {
    "CALL_ATM": 25111,
    "FUTURES": 9698,
    "PUT_ATM": 25150
  },
  "feature_regime_pass_true_count": 59959,
  "feature_row_count": 59959,
  "feature_side_breakdown": {
    "CALL": 25111,
    "CONTEXT": 9698,
    "PUT": 25150
  },
  "forensic_profile": null,
  "input_fingerprint": "88d33caebd042b59240139a53209fa381809937d2799eec5cf430aa1cf0ada64",
  "integrity_profile": null,
  "integrity_verdict": "fail",
  "loss_count": 0,
  "ml_export_eligible": false,
  "notes": [],
  "operator_verdict": null,
  "override_pack_id": null,
  "pnl_total": null,
  "regime_pass_count": 59959,
  "remarks": null,
  "replay_profile": null,
  "replay_scope": "feeds_features_strategy_risk_execution_shadow",
  "research_tags": [],
  "risk_action_breakdown": {
    "ENTER_CALL": 993,
    "ENTER_PUT": 1116,
    "HOLD": 57850
  },
  "risk_blocker_non_null_count": 59959,
  "risk_economics_valid_true_count": 0,
  "risk_regime_pass_true_count": 59959,
  "risk_row_count": 59959,
  "risk_vetoed_true_count": 0,
  "run_id": "replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd",
  "selection_mode": "single_day",
  "shadow_label": null,
  "side_mode": "mirrored_both",
  "speed_mode": "accelerated",
  "stage_count": 5,
  "stage_names": [
    "feeds",
    "features",
    "strategy",
    "risk",
    "execution_shadow"
  ],
  "started_at": "2026-06-13T16:58:51Z",
  "strategy_action_breakdown": {
    "ENTRY": 2109,
    "HOLD": 57850
  },
  "strategy_blocker_non_null_count": 59959,
  "strategy_candidate_true_count": 2109,
  "strategy_economics_valid_true_count": 0,
  "strategy_regime_pass_true_count": 59959,
  "strategy_row_count": 59959,
  "trade_count": 0,
  "trading_dates": [
    "2026-06-03"
  ],
  "waiver_count": 0,
  "win_count": 0,
  "window_end": null,
  "window_start": null
}

## Engine result
{
  "engine_finished_at": "2026-06-13T16:59:40Z",
  "engine_started_at": "2026-06-13T16:58:51Z",
  "final_state": "completed",
  "notes": [],
  "run_id": "replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd",
  "stage_count": 5,
  "stage_records": [
    {
      "finished_at": "2026-06-13T16:58:55Z",
      "order_index": 0,
      "output_summary": {
        "clock_after_stage": "2026-06-03T12:46:01Z",
        "day_breakdown": [
          {
            "injected_count": 59959,
            "last_sequence_id": 59959,
            "trading_day": "2026-06-03"
          }
        ],
        "run_id": "replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd",
        "stage_name": "feeds",
        "status": "ok",
        "total_injected": 59959
      },
      "stage_name": "feeds",
      "started_at": "2026-06-13T16:58:51Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:59:10Z",
      "order_index": 1,
      "output_summary": {
        "feature_channel": "replay:features",
        "feature_frames_published": 59959,
        "mode": "replay_feature_bridge",
        "run_id": "replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd",
        "source_feed_events": 59959,
        "stage_name": "features",
        "status": "ok"
      },
      "stage_name": "features",
      "started_at": "2026-06-13T16:58:55Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:59:39Z",
      "order_index": 2,
      "output_summary": {
        "action_breakdown": {
          "ENTRY": 2109,
          "HOLD": 57850
        },
        "decision_channel": "replay:decisions",
        "mode": "replay_strategy_bridge",
        "run_id": "replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd",
        "source_feature_frames": 59959,
        "stage_name": "strategy",
        "status": "ok",
        "strategy_decisions_published": 59959
      },
      "stage_name": "strategy",
      "started_at": "2026-06-13T16:59:10Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:59:40Z",
      "order_index": 3,
      "output_summary": {
        "mode": "replay_risk_bridge",
        "risk_action_breakdown": {
          "ENTER_CALL": 993,
          "ENTER_PUT": 1116,
          "HOLD": 57850
        },
        "risk_channel": "replay:risk",
        "risk_outputs_published": 59959,
        "run_id": "replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd",
        "source_strategy_decisions": 59959,
        "stage_name": "risk",
        "status": "ok",
        "vetoed_entries": 0
      },
      "stage_name": "risk",
      "started_at": "2026-06-13T16:59:39Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:59:40Z",
      "order_index": 4,
      "output_summary": {
        "execution_channel": "replay:execution_shadow",
        "execution_results_published": 59959,
        "fill_model_name": "immediate_market",
        "filled_count": 2109,
        "mode": "replay_execution_shadow_bridge",
        "run_id": "replay_locked_single_day_r35c_r4h_20260603_20260613_165851_4a1e79bd",
        "source_risk_outputs": 59959,
        "stage_name": "execution_shadow",
        "status": "ok"
      },
      "stage_name": "execution_shadow",
      "started_at": "2026-06-13T16:59:40Z",
      "success": true,
      "terminal_stage": true
    }
  ],
  "topology_summary": {
    "notes": [],
    "scope": "feeds_features_strategy_risk_execution_shadow",
    "stage_names": [
      "feeds",
      "features",
      "strategy",
      "risk",
      "execution_shadow"
    ],
    "stages": [
      {
        "description": "Replay input publication / feed-stage chain entry.",
        "order_index": 0,
        "owns_runtime_decisioning": false,
        "stage_name": "feeds",
        "terminal_stage": false
      },
      {
        "description": "Feature computation stage driven from replayed feed truth.",
        "order_index": 1,
        "owns_runtime_decisioning": true,
        "stage_name": "features",
        "terminal_stage": false
      },
      {
        "description": "Strategy decision stage driven from replay feature truth.",
        "order_index": 2,
        "owns_runtime_decisioning": true,
        "stage_name": "strategy",
        "terminal_stage": false
      },
      {
        "description": "Risk gating stage applied to replay strategy outputs.",
        "order_index": 3,
        "owns_runtime_decisioning": true,
        "stage_name": "risk",
        "terminal_stage": false
      },
      {
        "description": "Replay-only execution shadow stage with no live side effects.",
        "order_index": 4,
        "owns_runtime_decisioning": true,
        "stage_name": "execution_shadow",
        "terminal_stage": true
      }
    ],
    "topology_fingerprint": "4b6fc95a56eb8cd691208a5c21bd70994aa136956bd1f683863f0090813eda59"
  }
}

## R35B/R4S and R35C/R4C markers
3403:    # R35C/R4C: write an early compact official run summary immediately after
3417:        early_run_summary_payload["summary_write_mode"] = "early_compact_r35c_r4c"
3454:        """R35B/R4S replay artifact slimming.
3457:        Use SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 to persist small samples instead
3461:            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
3504:                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
3521:    def _r35b_write_compact_json(path, value):
3530:    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
3536:    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
3542:    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
3546:    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
3556:                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",

## Context around row artifact writes
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
  3403	    # R35C/R4C: write an early compact official run summary immediately after
  3404	    # engine_result is available, before heavy row-artifact exports. This is
  3405	    # artifact-only and does not change replay decisions, risk, execution shadow,
  3406	    # broker state, or Redis streams.
  3407	    try:
  3408	        replay_artifacts_dir = Path(run_context.artifact_plan.artifacts_dir)
  3409	        replay_artifacts_dir.mkdir(parents=True, exist_ok=True)
  3410	        early_run_summary_payload = build_run_summary_payload(
  3411	            run_context=run_context,
  3412	            selection_plan=selection_plan,
  3413	            topology_plan=topology_plan,
  3414	            engine_result=engine_result,
  3415	            integrity_bundle=integrity_bundle,
  3416	        )
  3417	        early_run_summary_payload["summary_write_mode"] = "early_compact_r35c_r4c"
  3418	        early_run_summary_payload["artifact_note"] = (
  3419	            "Written before heavy row-artifact export so completed engine runs "
  3420	            "always have official 10_run_summary.json even when row artifacts "
  3421	            "are capped/skipped/interrupted."
  3422	        )
  3423	        early_run_summary_json_path = replay_artifacts_dir / "10_run_summary.json"
  3424	        early_run_summary_csv_path = replay_artifacts_dir / "11_run_summary.csv"
  3425	        early_run_summary_json_path.write_text(
  3426	            json.dumps(early_run_summary_payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
  3427	            encoding="utf-8",
  3428	        )
  3429	        write_run_summary_csv(early_run_summary_csv_path, early_run_summary_payload)
  3430	    except Exception as exc:
  3431	        try:
  3432	            (Path(run_context.artifact_plan.artifacts_dir) / "10_run_summary_early_write_error.json").write_text(
  3433	                json.dumps(
  3434	                    {
  3435	                        "schema_version": "r35c_r4c_early_summary_error_v1",
  3436	                        "error": repr(exc),
  3437	                        "paper_live_enabled": False,
  3438	                        "broker_order_attempted": False,
  3439	                    },
  3440	                    indent=2,
  3441	                    sort_keys=True,
  3442	                    ensure_ascii=False,
  3443	                    default=str,
  3444	                ) + "\n",
  3445	                encoding="utf-8",
  3446	            )
  3447	        except Exception:
  3448	            pass
  3449	
  3450	    replay_artifacts_dir = Path(run_context.artifact_plan.artifacts_dir)
  3451	    replay_artifacts_dir.mkdir(parents=True, exist_ok=True)
  3452	
  3453	    def _r35b_json_slim(value):
  3454	        """R35B/R4S replay artifact slimming.
  3455	
  3456	        This is artifact-only. It does not change in-memory replay decisions.
  3457	        Use SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 to persist small samples instead
  3458	        of multi-GB row artifacts.
  3459	        """
  3460	        try:
  3461	            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3462	        except Exception:
  3463	            cap = 0
  3464	
  3465	        heavy_keys = {
  3466	            "candidate_json",
  3467	            "arbitration_json",
  3468	            "candidates",
  3469	            "candidate",
  3470	            "all_candidates",
  3471	            "feature_payload",
  3472	            "feature_json",
  3473	            "feature",
  3474	            "features",
  3475	            "feature_row",
  3476	            "feature_rows",
  3477	            "linked_feature",
  3478	            "linked_feature_row",
  3479	            "decision_payload",
  3480	            "payload",
  3481	            "raw",
  3482	            "raw_payload",
  3483	            "raw_frame",
  3484	            "debug",
  3485	            "debug_payload",
  3486	            "context",
  3487	            "snapshot",
  3488	        }
  3489	
  3490	        def slim(obj, depth=0):
  3491	            if depth > 6:
  3492	                return "<omitted_by_R35B_R4S:max_depth>"
  3493	
  3494	            if isinstance(obj, list):
  3495	                original_len = len(obj)
  3496	                selected = obj[:cap] if cap and cap > 0 else obj
  3497	                out = [slim(x, depth + 1) for x in selected]
  3498	                if cap and cap > 0 and original_len > cap:
  3499	                    out.append({
  3500	                        "_r35b_r4s_truncated": True,
  3501	                        "original_len": original_len,
  3502	                        "persisted_len": len(selected),
  3503	                        "cap": cap,
  3504	                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
  3505	                    })
  3506	                return out
  3507	
  3508	            if isinstance(obj, dict):
  3509	                out = {}
  3510	                for k, v in obj.items():

## Context around official summary writes
  3540	    )
  3541	
  3542	    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
  3543	
  3544	    persisted_execution_shadow_results = [dict(row) for row in transport.execution_shadow_results]
  3545	
  3546	    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
  3547	
  3548	    # B3_R36A_LATE_REPLAY_ANALYSIS_EXPORTS_AFTER_ROW_ARTIFACTS_BEGIN
  3549	    # Offline replay analysis exports. Runs after row artifacts are materialized.
  3550	    try:
  3551	        if os.environ.get("SCALPX_REPLAY_SKIP_B3_R32_EXPORTS", "0").strip().lower() in {"1", "true", "yes"}:
  3552	            (replay_artifacts_dir / "b3_r32_analysis_exports_status.json").write_text(
  3553	                json.dumps(
  3554	                    {
  3555	                        "status": "skipped",
  3556	                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",
  3557	                        "paper_live_enabled": False,
  3558	                        "broker_order_attempted": False,
  3559	                    },
  3560	                    separators=(",", ":"),
  3561	                    ensure_ascii=False,
  3562	                    default=str,
  3563	                ) + "\n",
  3564	                encoding="utf-8",
  3565	            )
  3566	        else:
  3567	            writer.write_b3_r32_analysis_exports(run_context)
  3568	    except Exception as exc:
  3569	        try:
  3570	            writer.write_json_artifact(
  3571	                run_context.artifact_plan.artifacts_dir / "b3_r36a_late_export_error.json",
  3572	                {
  3573	                    "schema_version": "b3_r36a_late_export_error_v1",
  3574	                    "status": "error",
  3575	                    "error": repr(exc),
  3576	                    "note": "Optional late B3 export failed; replay artifacts remain available.",
  3577	                },
  3578	            )
  3579	        except Exception:
  3580	            pass
