# R35C_R4R2_LINE_PATCH_FORCE_DEFAULT_ROW_CAP_NO_REPLAY_NO_ORDER_20260613_231323

classification: PASS_R35C_R4R2_FORCE_DEFAULT_ROW_ARTIFACT_CAP_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4R2_LINE_PATCH_FORCE_DEFAULT_ROW_CAP_NO_REPLAY_NO_ORDER_20260613_231323.json`
backup: `run/_code_backups/R35C_R4R2_LINE_PATCH_FORCE_DEFAULT_ROW_CAP_NO_REPLAY_NO_ORDER_20260613_231323_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1
func_start_line=3545
insert_before_line=3554

## Patch errors

## Markers
3554:        # R35C/R4R2: force default cap for known row artifact files.
3557:        row_artifact_names = {
3558:            "features_rows.json",
3559:            "strategy_decisions.json",
3560:            "risk_outputs.json",
3561:            "execution_shadow_results.json",
3563:        if (not hard_cap or hard_cap <= 0) and getattr(path, "name", "") in row_artifact_names:
3564:            hard_cap = 50
3606:    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
3613:    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
3620:    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
3625:    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
3635:                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",

## Source context
  3540	
  3541	            return obj
  3542	
  3543	        return slim(value)
  3544	
  3545	    def _r35b_write_compact_json(path, value):
  3546	        # R35C/R4J2: hard top-level row cap before JSON serialization.
  3547	        # R35B/R4S slimmed nested payloads, but R4H proved top-level row files
  3548	        # could still become multi-hundred-MB. This is artifact-only.
  3549	        try:
  3550	            hard_cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3551	        except Exception:
  3552	            hard_cap = 0
  3553	
  3554	        # R35C/R4R2: force default cap for known row artifact files.
  3555	        # Artifact-only guard: if env cap is missing inside recursive replay,
  3556	        # still cap the four huge row artifact JSON files to 50 rows.
  3557	        row_artifact_names = {
  3558	            "features_rows.json",
  3559	            "strategy_decisions.json",
  3560	            "risk_outputs.json",
  3561	            "execution_shadow_results.json",
  3562	        }
  3563	        if (not hard_cap or hard_cap <= 0) and getattr(path, "name", "") in row_artifact_names:
  3564	            hard_cap = 50
  3565	
  3566	        payload = value
  3567	        if hard_cap and hard_cap > 0 and isinstance(value, list) and len(value) > hard_cap:
  3568	            payload = list(value[:hard_cap])
  3569	            payload.append({
  3570	                "_r35c_r4j_top_level_truncated": True,
  3571	                "original_len": len(value),
  3572	                "persisted_len": hard_cap,
  3573	                "cap": hard_cap,
  3574	                "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP hard top-level cap before write",
  3575	            })
  3576	
  3577	        path.write_text(
  3578	            json.dumps(_r35b_json_slim(payload), separators=(",", ":"), ensure_ascii=False, default=str) + "\n",
  3579	            encoding="utf-8",
  3580	        )
  3581	
  3582	    persisted_feature_rows = build_persisted_feature_rows(transport.feature_frames)
  3583	
  3584	    # R35C/R4L: force cap row lists before artifact writes.
  3585	    # This is artifact-only. It does not change in-memory replay decisions,

## Compile log
