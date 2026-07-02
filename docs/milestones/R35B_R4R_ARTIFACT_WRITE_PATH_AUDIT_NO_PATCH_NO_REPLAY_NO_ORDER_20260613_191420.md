# R35B_R4R_ARTIFACT_WRITE_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_191420

classification: PASS_R35B_R4R_ARTIFACT_WRITE_PATH_AUDIT_DONE_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4R_ARTIFACT_WRITE_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_191420.json`

safety pre=0/0/0 post=0/0/0 proc=0/0

## compact helper context
3406:    def _r35b_json_slim(value):
3409:        Set SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 or similar to persist only a
3414:            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
3449:                    "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
3458:    def _r35b_write_compact_json(path, value):
3460:            json.dumps(_r35b_json_slim(value), separators=(",", ":"), ensure_ascii=False, default=str) + "\n",
3467:    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
3473:    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
3479:    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
3483:    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)

## artifact write calls
3467:    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
3473:    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
3479:    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
3483:    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
3493:                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",

## context 3395-3475
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
  3407	        """R35B replay-only artifact slimming with optional row cap.
  3408	
  3409	        Set SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 or similar to persist only a
  3410	        bounded sample of huge replay row artifacts. This does not alter
  3411	        in-memory strategy/risk/execution decisions.
  3412	        """
  3413	        try:
  3414	            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3415	        except Exception:
  3416	            cap = 0
  3417	
  3418	        heavy_keys = (
  3419	            "candidate_json",
  3420	            "arbitration_json",
  3421	            "candidates",
  3422	            "candidate",
  3423	            "all_candidates",
  3424	            "feature_payload",
  3425	            "feature_json",
  3426	            "raw",
  3427	            "raw_payload",
  3428	        )
  3429	
  3430	        def slim_one(item):
  3431	            if isinstance(item, dict):
  3432	                d = dict(item)
  3433	                for k in heavy_keys:
  3434	                    if k in d:
  3435	                        d[k] = f"<omitted_by_R35B_R4I:{k}>"
  3436	                return d
  3437	            return item
  3438	
  3439	        if isinstance(value, list):
  3440	            original_len = len(value)
  3441	            selected = value[:cap] if cap and cap > 0 else value
  3442	            out = [slim_one(item) for item in selected]
  3443	            if cap and cap > 0 and original_len > cap:
  3444	                out.append({
  3445	                    "_r35b_r4i_truncated": True,
  3446	                    "original_len": original_len,
  3447	                    "persisted_len": len(selected),
  3448	                    "cap": cap,
  3449	                    "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
  3450	                })
  3451	            return out
  3452	
  3453	        if isinstance(value, dict):
  3454	            return slim_one(value)
  3455	
  3456	        return value
  3457	
  3458	    def _r35b_write_compact_json(path, value):
  3459	        path.write_text(
  3460	            json.dumps(_r35b_json_slim(value), separators=(",", ":"), ensure_ascii=False, default=str) + "\n",
  3461	            encoding="utf-8",
  3462	        )
  3463	
  3464	
  3465	    persisted_feature_rows = build_persisted_feature_rows(transport.feature_frames)
  3466	
  3467	    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
  3468	    persisted_strategy_decisions = build_persisted_strategy_decisions(
  3469	        transport.strategy_decisions,
  3470	        persisted_feature_rows,
  3471	    )
  3472	
  3473	    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
  3474	    persisted_risk_outputs = build_persisted_risk_outputs(
  3475	        transport.risk_outputs,
