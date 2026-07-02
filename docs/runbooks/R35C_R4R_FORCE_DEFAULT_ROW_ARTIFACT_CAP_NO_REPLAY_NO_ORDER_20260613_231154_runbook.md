# R35C_R4R_FORCE_DEFAULT_ROW_ARTIFACT_CAP_NO_REPLAY_NO_ORDER_20260613_231154

classification: REVIEW_R35C_R4R_PATCH_OR_SAFETY_NEEDS_INSPECTION_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4R_FORCE_DEFAULT_ROW_ARTIFACT_CAP_NO_REPLAY_NO_ORDER_20260613_231154.json`
backup: `run/_code_backups/R35C_R4R_FORCE_DEFAULT_ROW_ARTIFACT_CAP_NO_REPLAY_NO_ORDER_20260613_231154_bin_replay_run.py.bak`

patch_rc=1 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log

## Patch errors
write_compact_json_header_block_not_found

## Markers
3594:    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
3601:    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
3608:    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)
3613:    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)
3623:                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",

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
  3554	        payload = value
  3555	        if hard_cap and hard_cap > 0 and isinstance(value, list) and len(value) > hard_cap:
  3556	            payload = list(value[:hard_cap])
  3557	            payload.append({
  3558	                "_r35c_r4j_top_level_truncated": True,
  3559	                "original_len": len(value),
  3560	                "persisted_len": hard_cap,
  3561	                "cap": hard_cap,
  3562	                "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP hard top-level cap before write",
  3563	            })
  3564	
  3565	        path.write_text(
  3566	            json.dumps(_r35b_json_slim(payload), separators=(",", ":"), ensure_ascii=False, default=str) + "\n",
  3567	            encoding="utf-8",
  3568	        )
  3569	
  3570	    persisted_feature_rows = build_persisted_feature_rows(transport.feature_frames)
  3571	
  3572	    # R35C/R4L: force cap row lists before artifact writes.
  3573	    # This is artifact-only. It does not change in-memory replay decisions,
  3574	    # risk outputs, execution shadow, broker state, or Redis streams.
  3575	    def _r35c_r4l_force_row_cap(label, rows):
  3576	        try:
  3577	            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
  3578	        except Exception:

## Compile log
