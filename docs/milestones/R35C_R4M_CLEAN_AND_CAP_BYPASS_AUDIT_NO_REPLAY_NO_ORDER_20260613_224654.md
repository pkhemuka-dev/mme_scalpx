# R35C_R4M_CLEAN_AND_CAP_BYPASS_AUDIT_NO_REPLAY_NO_ORDER_20260613_224654

classification: PASS_R35C_R4M_STOPPED_PROCESS_CLEANED_CAP_BYPASS_AUDITED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4M_CLEAN_AND_CAP_BYPASS_AUDIT_NO_REPLAY_NO_ORDER_20260613_224654.json`

## Before
## before jobs
[1]+ 258997 Stopped                 timeout 900s "$PY" bin/replay_run.py --dataset-root "$D" --selection-mode single_day --single-day 2026-06-03 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4m_20260603 --dataset-id r35c_r4m --run-root "$RR" --recurse > "$A/replay.log" 2>&1

## before processes
 258997  257971 T          03:41 timeout 900s .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-03 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4m_20260603 --dataset-id r35c_r4m --run-root run/replay/r35c_r4m/20260613_224314 --recurse
 258998  258997 T          03:41 .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-03 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4m_20260603 --dataset-id r35c_r4m --run-root run/replay/r35c_r4m/20260613_224314 --recurse

## Audit
## after processes

## after jobs

## safety
orders=0 risk=0 execution=0 proc=0/0 replay_proc=0

## latest R4M artifact sizes
R4M_ROOT=run/replay/r35c_r4m/20260613_224314
R4M_RUN=run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2
662784524 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/features_rows.json
12622 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/02_scope_profile.json
10361 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/economics_summary.json
7642 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/01_dataset_summary.json
5029 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/engine_result.json
3884 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/00_manifest.json
2336 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/17_effective_inputs.json
769 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/b3_r32_analysis_exports_status.json
763 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/10_run_summary.json
741 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/11_run_summary.csv
278 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/18_effective_overrides_flat.json
202 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/06_candidate_audit.csv
113 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/blocker_distribution.csv
81 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/artifacts/family_side_summary.csv
59 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/04_metrics_summary.json
55 run/replay/r35c_r4m/20260613_224314/replay_locked_single_day_r35c_r4m_20260603_20260613_171322_a3ed96f2/03_integrity_report.json

## check feature file for truncation marker

## exact source around cap/write
  3515	                return out
  3516	
  3517	            if isinstance(obj, dict):
  3518	                out = {}
  3519	                for k, v in obj.items():
  3520	                    if k in heavy_keys:
  3521	                        out[k] = f"<omitted_by_R35B_R4S:{k}>"
  3522	                    else:
  3523	                        out[k] = slim(v, depth + 1)
  3524	                return out
  3525	
  3526	            return obj
  3527	
  3528	        return slim(value)
  3529	
  3530	    def _r35b_write_compact_json(path, value):
  3531	        # R35C/R4J2: hard top-level row cap before JSON serialization.
  3532	        # R35B/R4S slimmed nested payloads, but R4H proved top-level row files
  3533	        # could still become multi-hundred-MB. This is artifact-only.
  3534	        try:
  3535	            hard_cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3536	        except Exception:
  3537	            hard_cap = 0
  3538	
  3539	        payload = value
  3540	        if hard_cap and hard_cap > 0 and isinstance(value, list) and len(value) > hard_cap:
  3541	            payload = list(value[:hard_cap])
  3542	            payload.append({
  3543	                "_r35c_r4j_top_level_truncated": True,
  3544	                "original_len": len(value),
  3545	                "persisted_len": hard_cap,
  3546	                "cap": hard_cap,
  3547	                "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP hard top-level cap before write",
  3548	            })
  3549	
  3550	        path.write_text(
  3551	            json.dumps(_r35b_json_slim(payload), separators=(",", ":"), ensure_ascii=False, default=str) + "\n",
  3552	            encoding="utf-8",
  3553	        )
  3554	
  3555	    persisted_feature_rows = build_persisted_feature_rows(transport.feature_frames)
  3556	
  3557	    # R35C/R4L: force cap row lists before artifact writes.
  3558	    # This is artifact-only. It does not change in-memory replay decisions,
  3559	    # risk outputs, execution shadow, broker state, or Redis streams.
  3560	    def _r35c_r4l_force_row_cap(label, rows):
  3561	        try:
  3562	            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3563	        except Exception:
  3564	            cap = 0
  3565	        if cap and cap > 0 and isinstance(rows, list) and len(rows) > cap:
  3566	            out = list(rows[:cap])
  3567	            out.append({
  3568	                "_r35c_r4l_top_level_truncated": True,
  3569	                "label": label,
  3570	                "original_len": len(rows),
  3571	                "persisted_len": cap,
  3572	                "cap": cap,
  3573	                "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP force cap before artifact write",
  3574	            })
  3575	            return out
  3576	        return rows
  3577	
  3578	    persisted_feature_rows = _r35c_r4l_force_row_cap("features_rows", persisted_feature_rows)
  3579	    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
  3580	    persisted_strategy_decisions = build_persisted_strategy_decisions(
  3581	        transport.strategy_decisions,
  3582	        persisted_feature_rows,
  3583	    )
  3584	
  3585	    persisted_strategy_decisions = _r35c_r4l_force_row_cap("strategy_decisions", persisted_strategy_decisions)
  3586	    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
  3587	    persisted_risk_outputs = build_persisted_risk_outputs(
  3588	        transport.risk_outputs,
  3589	        persisted_strategy_decisions,
  3590	    )
  3591	
  3592	    persisted_risk_outputs = _r35c_r4l_force_row_cap("risk_outputs", persisted_risk_outputs)
  3593	    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
  3594	
  3595	    persisted_execution_shadow_results = [dict(row) for row in transport.execution_shadow_results]
  3596	
  3597	    persisted_execution_shadow_results = _r35c_r4l_force_row_cap("execution_shadow_results", persisted_execution_shadow_results)
  3598	    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
  3599	
  3600	    # B3_R36A_LATE_REPLAY_ANALYSIS_EXPORTS_AFTER_ROW_ARTIFACTS_BEGIN
  3601	    # Offline replay analysis exports. Runs after row artifacts are materialized.
  3602	    try:
  3603	        if os.environ.get("SCALPX_REPLAY_SKIP_B3_R32_EXPORTS", "0").strip().lower() in {"1", "true", "yes"}:
  3604	            (replay_artifacts_dir / "b3_r32_analysis_exports_status.json").write_text(
  3605	                json.dumps(
  3606	                    {
  3607	                        "status": "skipped",
  3608	                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",
  3609	                        "paper_live_enabled": False,
  3610	                        "broker_order_attempted": False,
