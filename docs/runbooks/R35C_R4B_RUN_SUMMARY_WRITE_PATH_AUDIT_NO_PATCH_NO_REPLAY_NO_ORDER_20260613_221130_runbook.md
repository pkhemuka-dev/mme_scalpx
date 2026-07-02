# R35C_R4B_RUN_SUMMARY_WRITE_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_221130

classification: PASS_R35C_R4B_RUN_SUMMARY_WRITE_PATH_AUDIT_DONE_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4B_RUN_SUMMARY_WRITE_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_221130.json`

safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## summary write references in bin/replay_run.py
2689:def build_run_summary_payload(
2693:    engine_result,
2715:        "started_at": getattr(engine_result, "engine_started_at", None),
2716:        "completed_at": getattr(engine_result, "engine_finished_at", None),
2752:        "stage_count": engine_result.stage_count,
2785:def _run_summary_csv_scalar(value: Any) -> str | int | float | bool:
2793:def write_run_summary_csv(
2803:        column: _run_summary_csv_scalar(payload.get(column))
3362:    engine_result = engine.execute(
3389:        engine_result=engine_result,
3399:        metrics={"stage_count": engine_result.stage_count},
3401:    writer.write_engine_result(engine_result, run_context.artifact_plan)
3554:    run_summary_payload = build_run_summary_payload(
3557:        engine_result=engine_result,
3565:    run_summary_json_path = replay_artifacts_dir / "10_run_summary.json"
3566:    run_summary_csv_path = replay_artifacts_dir / "11_run_summary.csv"
3568:    run_summary_json_path.write_text(
3569:        json.dumps(run_summary_payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
3572:    write_run_summary_csv(run_summary_csv_path, run_summary_payload)
3580:        "engine_final_state": engine_result.final_state.value,
3587:            for item in engine_result.stage_records

## context around artifact writes
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
  3406	    def _r35b_json_slim(value):
  3407	        """R35B/R4S replay artifact slimming.
  3408	
  3409	        This is artifact-only. It does not change in-memory replay decisions.
  3410	        Use SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 to persist small samples instead
  3411	        of multi-GB row artifacts.
  3412	        """
  3413	        try:
  3414	            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3415	        except Exception:
  3416	            cap = 0
  3417	
  3418	        heavy_keys = {
  3419	            "candidate_json",
  3420	            "arbitration_json",
  3421	            "candidates",
  3422	            "candidate",
  3423	            "all_candidates",
  3424	            "feature_payload",
  3425	            "feature_json",
  3426	            "feature",
  3427	            "features",
  3428	            "feature_row",
  3429	            "feature_rows",
  3430	            "linked_feature",
  3431	            "linked_feature_row",
  3432	            "decision_payload",
  3433	            "payload",
  3434	            "raw",
  3435	            "raw_payload",
  3436	            "raw_frame",
  3437	            "debug",
  3438	            "debug_payload",
  3439	            "context",
  3440	            "snapshot",
  3441	        }
  3442	
  3443	        def slim(obj, depth=0):
  3444	            if depth > 6:
  3445	                return "<omitted_by_R35B_R4S:max_depth>"
  3446	
  3447	            if isinstance(obj, list):
  3448	                original_len = len(obj)
  3449	                selected = obj[:cap] if cap and cap > 0 else obj
  3450	                out = [slim(x, depth + 1) for x in selected]
  3451	                if cap and cap > 0 and original_len > cap:
  3452	                    out.append({
  3453	                        "_r35b_r4s_truncated": True,
  3454	                        "original_len": original_len,
  3455	                        "persisted_len": len(selected),
  3456	                        "cap": cap,
  3457	                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
  3458	                    })
  3459	                return out
  3460	
  3461	            if isinstance(obj, dict):
  3462	                out = {}
  3463	                for k, v in obj.items():
  3464	                    if k in heavy_keys:
  3465	                        out[k] = f"<omitted_by_R35B_R4S:{k}>"
  3466	                    else:
  3467	                        out[k] = slim(v, depth + 1)
  3468	                return out
  3469	
  3470	            return obj
  3471	
  3472	        return slim(value)
  3473	
  3474	    def _r35b_write_compact_json(path, value):
  3475	        path.write_text(
  3476	            json.dumps(_r35b_json_slim(value), separators=(",", ":"), ensure_ascii=False, default=str) + "\n",
  3477	            encoding="utf-8",
  3478	        )
  3479	
  3480	
  3481	    persisted_feature_rows = build_persisted_feature_rows(transport.feature_frames)
  3482	
  3483	    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
  3484	    persisted_strategy_decisions = build_persisted_strategy_decisions(
  3485	        transport.strategy_decisions,
  3486	        persisted_feature_rows,
  3487	    )
  3488	
  3489	    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
  3490	    persisted_risk_outputs = build_persisted_risk_outputs(
  3491	        transport.risk_outputs,
  3492	        persisted_strategy_decisions,
  3493	    )
  3494	
  3495	    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
  3496	
  3497	    persisted_execution_shadow_results = [dict(row) for row in transport.execution_shadow_results]
  3498	
  3499	    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
  3500	
  3501	    # B3_R36A_LATE_REPLAY_ANALYSIS_EXPORTS_AFTER_ROW_ARTIFACTS_BEGIN
  3502	    # Offline replay analysis exports. Runs after row artifacts are materialized.
  3503	    try:
  3504	        if os.environ.get("SCALPX_REPLAY_SKIP_B3_R32_EXPORTS", "0").strip().lower() in {"1", "true", "yes"}:
  3505	            (replay_artifacts_dir / "b3_r32_analysis_exports_status.json").write_text(
  3506	                json.dumps(
  3507	                    {
  3508	                        "status": "skipped",
  3509	                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",
  3510	                        "paper_live_enabled": False,
  3511	                        "broker_order_attempted": False,
  3512	                    },
  3513	                    separators=(",", ":"),
  3514	                    ensure_ascii=False,
  3515	                    default=str,
  3516	                ) + "\n",
  3517	                encoding="utf-8",
  3518	            )
  3519	        else:
  3520	            writer.write_b3_r32_analysis_exports(run_context)
  3521	    except Exception as exc:
  3522	        try:
  3523	            writer.write_json_artifact(
  3524	                run_context.artifact_plan.artifacts_dir / "b3_r36a_late_export_error.json",
  3525	                {

## summary references in replay package
app/mme_scalpx/replay/reports.py:61:from .engine import ReplayEngineResult, engine_result_to_dict
app/mme_scalpx/replay/reports.py:151:        engine_result: ReplayEngineResult,
app/mme_scalpx/replay/reports.py:158:        _validate_engine_result(engine_result, expected_run_id=run_context.run_id)
app/mme_scalpx/replay/reports.py:167:            final_engine_state=engine_result.final_state.value,
app/mme_scalpx/replay/reports.py:203:            "engine_result": engine_result_to_dict(engine_result),
app/mme_scalpx/replay/reports.py:226:    engine_result: ReplayEngineResult,
app/mme_scalpx/replay/reports.py:235:        engine_result=engine_result,
app/mme_scalpx/replay/reports.py:312:def _validate_engine_result(
app/mme_scalpx/replay/reports.py:313:    engine_result: ReplayEngineResult,
app/mme_scalpx/replay/reports.py:317:    if engine_result.run_id != expected_run_id:
app/mme_scalpx/replay/reports.py:319:            f"engine_result.run_id mismatch: expected {expected_run_id!r}, "
app/mme_scalpx/replay/reports.py:320:            f"got {engine_result.run_id!r}"
app/mme_scalpx/replay/engine.py:319:def engine_result_to_dict(result: ReplayEngineResult) -> dict[str, Any]:
app/mme_scalpx/replay/engine.py:421:    "engine_result_to_dict",
app/mme_scalpx/replay/artifacts.py:88:from .engine import engine_result_to_dict
app/mme_scalpx/replay/artifacts.py:268:    def write_engine_result(
app/mme_scalpx/replay/artifacts.py:270:        engine_result,
app/mme_scalpx/replay/artifacts.py:273:        payload = engine_result_to_dict(engine_result)
app/mme_scalpx/replay/artifacts.py:274:        engine_result_path = Path(artifact_plan.artifacts_dir) / "engine_result.json"
app/mme_scalpx/replay/artifacts.py:275:        return self.write_json_artifact(engine_result_path, payload)
app/mme_scalpx/replay/contracts.py:51:ARTIFACT_RUN_SUMMARY_JSON = "10_run_summary.json"
app/mme_scalpx/replay/contracts.py:52:ARTIFACT_RUN_SUMMARY_CSV = "11_run_summary.csv"
app/mme_scalpx/replay/contracts.py:855:def validate_run_summary_row(row: RunSummaryRow) -> None:
app/mme_scalpx/replay/contracts.py:1010:    "validate_run_summary_row",
app/mme_scalpx/replay/differential.py:37:from .engine import ReplayEngineResult, engine_result_to_dict
app/mme_scalpx/replay/differential.py:106:        baseline_engine_result: ReplayEngineResult,
app/mme_scalpx/replay/differential.py:107:        shadow_engine_result: ReplayEngineResult,
app/mme_scalpx/replay/differential.py:113:        _validate_engine_result(
app/mme_scalpx/replay/differential.py:114:            baseline_engine_result,
app/mme_scalpx/replay/differential.py:116:            name="baseline_engine_result",
app/mme_scalpx/replay/differential.py:118:        _validate_engine_result(
app/mme_scalpx/replay/differential.py:119:            shadow_engine_result,
app/mme_scalpx/replay/differential.py:121:            name="shadow_engine_result",
app/mme_scalpx/replay/differential.py:125:            expected_run_id=baseline_engine_result.run_id,
app/mme_scalpx/replay/differential.py:130:            expected_run_id=shadow_engine_result.run_id,
app/mme_scalpx/replay/differential.py:140:            baseline_engine_result=baseline_engine_result,
app/mme_scalpx/replay/differential.py:141:            shadow_engine_result=shadow_engine_result,
app/mme_scalpx/replay/differential.py:149:            baseline_run_id=baseline_engine_result.run_id,
app/mme_scalpx/replay/differential.py:150:            shadow_run_id=shadow_engine_result.run_id,
app/mme_scalpx/replay/differential.py:153:            baseline_final_state=baseline_engine_result.final_state.value,
app/mme_scalpx/replay/differential.py:154:            shadow_final_state=shadow_engine_result.final_state.value,
app/mme_scalpx/replay/differential.py:155:            baseline_stage_count=baseline_engine_result.stage_count,
app/mme_scalpx/replay/differential.py:156:            shadow_stage_count=shadow_engine_result.stage_count,
app/mme_scalpx/replay/differential.py:163:            "baseline_engine_result": engine_result_to_dict(baseline_engine_result),
app/mme_scalpx/replay/differential.py:164:            "shadow_engine_result": engine_result_to_dict(shadow_engine_result),
app/mme_scalpx/replay/differential.py:173:            baseline_run_id=baseline_engine_result.run_id,
app/mme_scalpx/replay/differential.py:174:            shadow_run_id=shadow_engine_result.run_id,
app/mme_scalpx/replay/differential.py:186:    baseline_engine_result: ReplayEngineResult,
app/mme_scalpx/replay/differential.py:187:    shadow_engine_result: ReplayEngineResult,
app/mme_scalpx/replay/differential.py:195:        baseline_engine_result=baseline_engine_result,
app/mme_scalpx/replay/differential.py:196:        shadow_engine_result=shadow_engine_result,
app/mme_scalpx/replay/differential.py:246:    baseline_engine_result: ReplayEngineResult,
app/mme_scalpx/replay/differential.py:247:    shadow_engine_result: ReplayEngineResult,
app/mme_scalpx/replay/differential.py:254:            baseline_value=baseline_engine_result.final_state.value,
app/mme_scalpx/replay/differential.py:255:            shadow_value=shadow_engine_result.final_state.value,
app/mme_scalpx/replay/differential.py:259:            baseline_value=baseline_engine_result.stage_count,
app/mme_scalpx/replay/differential.py:260:            shadow_value=shadow_engine_result.stage_count,
app/mme_scalpx/replay/differential.py:330:def _validate_engine_result(
bin/replay_build_comparison_summary.py:54:    summary_path = run_dir / "artifacts" / "10_run_summary.json"
bin/guarded_replay_engine_execute_dry_run_29g.py:49:        "engine_result",
bin/replay_run.py:2689:def build_run_summary_payload(
bin/replay_run.py:2693:    engine_result,
bin/replay_run.py:2715:        "started_at": getattr(engine_result, "engine_started_at", None),
bin/replay_run.py:2716:        "completed_at": getattr(engine_result, "engine_finished_at", None),
bin/replay_run.py:2752:        "stage_count": engine_result.stage_count,
bin/replay_run.py:2785:def _run_summary_csv_scalar(value: Any) -> str | int | float | bool:
bin/replay_run.py:2793:def write_run_summary_csv(
bin/replay_run.py:2803:        column: _run_summary_csv_scalar(payload.get(column))
bin/replay_run.py:3362:    engine_result = engine.execute(
bin/replay_run.py:3389:        engine_result=engine_result,
bin/replay_run.py:3399:        metrics={"stage_count": engine_result.stage_count},
bin/replay_run.py:3401:    writer.write_engine_result(engine_result, run_context.artifact_plan)
bin/replay_run.py:3554:    run_summary_payload = build_run_summary_payload(
bin/replay_run.py:3557:        engine_result=engine_result,
bin/replay_run.py:3565:    run_summary_json_path = replay_artifacts_dir / "10_run_summary.json"
bin/replay_run.py:3566:    run_summary_csv_path = replay_artifacts_dir / "11_run_summary.csv"
bin/replay_run.py:3568:    run_summary_json_path.write_text(
bin/replay_run.py:3569:        json.dumps(run_summary_payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
bin/replay_run.py:3572:    write_run_summary_csv(run_summary_csv_path, run_summary_payload)
bin/replay_run.py:3580:        "engine_final_state": engine_result.final_state.value,
bin/replay_run.py:3587:            for item in engine_result.stage_records
bin/proof_replay_batch16_freeze.py:340:        engine.engine_result_to_dict(result),
