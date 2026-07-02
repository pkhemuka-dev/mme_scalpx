# R35C_R4O3_BOUNDARY_PATCH_PRESERVE_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225907

classification: REVIEW_R35C_R4O3_PATCH_OR_SAFETY_NEEDS_INSPECTION_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4O3_BOUNDARY_PATCH_PRESERVE_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225907.json`
backup: `run/_code_backups/R35C_R4O3_BOUNDARY_PATCH_PRESERVE_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225907_bin_replay_run.py.bak`

patch_rc=1 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log

## Patch errors
r35b_json_slim_function_boundaries_not_found

## Markers
3543:                "_r35c_r4j_top_level_truncated": True,
3568:                "_r35c_r4l_top_level_truncated": True,

## Source context
  3495	            "context",
  3496	            "snapshot",
  3497	        }
  3498	
  3499	        def slim(obj, depth=0):
  3500	            if depth > 6:
  3501	                return "<omitted_by_R35B_R4S:max_depth>"
  3502	
  3503	            if isinstance(obj, list):
  3504	                original_len = len(obj)
  3505	                selected = obj[:cap] if cap and cap > 0 else obj
  3506	                out = [slim(x, depth + 1) for x in selected]
  3507	                if cap and cap > 0 and original_len > cap:
  3508	                    out.append({
  3509	                        "_r35b_r4s_truncated": True,
  3510	                        "original_len": original_len,
  3511	                        "persisted_len": len(selected),
  3512	                        "cap": cap,
  3513	                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
  3514	                    })
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

## Compile log
