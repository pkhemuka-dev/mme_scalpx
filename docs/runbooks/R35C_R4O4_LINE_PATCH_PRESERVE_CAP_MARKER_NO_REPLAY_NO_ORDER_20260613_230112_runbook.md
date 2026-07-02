# R35C_R4O4_LINE_PATCH_PRESERVE_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_230112

classification: PASS_R35C_R4O4_CAP_MARKER_PRESERVE_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4O4_LINE_PATCH_PRESERVE_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_230112.json`
backup: `run/_code_backups/R35C_R4O4_LINE_PATCH_PRESERVE_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_230112_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1
block_start_line=3503
block_end_line=3515

## Patch errors

## Markers
3504:                # R35C/R4O4: preserve R4L/R4J top-level cap marker.
3507:                existing_marker = None
3510:                    obj[-1].get("_r35c_r4l_top_level_truncated")
3511:                    or obj[-1].get("_r35c_r4j_top_level_truncated")
3513:                    existing_marker = obj[-1]
3520:                if existing_marker is not None:
3521:                    out.append(slim(existing_marker, depth + 1))
3558:                "_r35c_r4j_top_level_truncated": True,
3583:                "_r35c_r4l_top_level_truncated": True,

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
  3504	                # R35C/R4O4: preserve R4L/R4J top-level cap marker.
  3505	                # R4L/R4J may already append a truncation marker. The older
  3506	                # R35B/R4S nested slim pass must not drop that marker.
  3507	                existing_marker = None
  3508	                body = obj
  3509	                if obj and isinstance(obj[-1], dict) and (
  3510	                    obj[-1].get("_r35c_r4l_top_level_truncated")
  3511	                    or obj[-1].get("_r35c_r4j_top_level_truncated")
  3512	                ):
  3513	                    existing_marker = obj[-1]
  3514	                    body = obj[:-1]
  3515	
  3516	                original_len = len(body)
  3517	                selected = body[:cap] if cap and cap > 0 else body
  3518	                out = [slim(x, depth + 1) for x in selected]
  3519	
  3520	                if existing_marker is not None:
  3521	                    out.append(slim(existing_marker, depth + 1))
  3522	                elif cap and cap > 0 and original_len > cap:
  3523	                    out.append({
  3524	                        "_r35b_r4s_truncated": True,
  3525	                        "original_len": original_len,
  3526	                        "persisted_len": len(selected),
  3527	                        "cap": cap,
  3528	                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
  3529	                    })
  3530	                return out
  3531	
  3532	            if isinstance(obj, dict):
  3533	                out = {}
  3534	                for k, v in obj.items():
  3535	                    if k in heavy_keys:
  3536	                        out[k] = f"<omitted_by_R35B_R4S:{k}>"
  3537	                    else:
  3538	                        out[k] = slim(v, depth + 1)
  3539	                return out
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

## Compile log
