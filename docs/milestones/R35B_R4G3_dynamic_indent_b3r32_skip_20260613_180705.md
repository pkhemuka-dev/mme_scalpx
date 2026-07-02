# R35B_R4G3_dynamic_indent_b3r32_skip_20260613_180705

classification: PASS_R35B_R4G3_B3R32_SKIP_PATCH_COMPILE_SAFETY_CLEAN_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4G3_dynamic_indent_b3r32_skip_20260613_180705.json`
restored_from: `run/_code_backups/R35B_R4G_skip_b3r32_heavy_export_20260613_180252_bin_replay_run.py.bak`
new_backup: `run/_code_backups/R35B_R4G3_dynamic_indent_b3r32_skip_20260613_180705_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## Patch log
{'patched': True, 'target_line_index': 3484, 'indent_len': 8}

## Markers
3484:        if os.environ.get("SCALPX_REPLAY_SKIP_B3_R32_EXPORTS", "0").strip().lower() in {"1", "true", "yes"}:
3489:                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",
3500:            writer.write_b3_r32_analysis_exports(run_context)

## Context
  3476	
  3477	    persisted_execution_shadow_results = [dict(row) for row in transport.execution_shadow_results]
  3478	
  3479	    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
  3480	
  3481	    # B3_R36A_LATE_REPLAY_ANALYSIS_EXPORTS_AFTER_ROW_ARTIFACTS_BEGIN
  3482	    # Offline replay analysis exports. Runs after row artifacts are materialized.
  3483	    try:
  3484	        if os.environ.get("SCALPX_REPLAY_SKIP_B3_R32_EXPORTS", "0").strip().lower() in {"1", "true", "yes"}:
  3485	            (replay_artifacts_dir / "b3_r32_analysis_exports_status.json").write_text(
  3486	                json.dumps(
  3487	                    {
  3488	                        "status": "skipped",
  3489	                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",
  3490	                        "paper_live_enabled": False,
  3491	                        "broker_order_attempted": False,
  3492	                    },
  3493	                    separators=(",", ":"),
  3494	                    ensure_ascii=False,
  3495	                    default=str,
  3496	                ) + "\n",
  3497	                encoding="utf-8",
  3498	            )
  3499	        else:
  3500	            writer.write_b3_r32_analysis_exports(run_context)
  3501	    except Exception as exc:
  3502	        try:
  3503	            writer.write_json_artifact(
  3504	                run_context.artifact_plan.artifacts_dir / "b3_r36a_late_export_error.json",
  3505	                {
  3506	                    "schema_version": "b3_r36a_late_export_error_v1",
  3507	                    "status": "error",
  3508	                    "error": repr(exc),

## Compile log
