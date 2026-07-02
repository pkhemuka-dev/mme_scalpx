# R35C_R4O_BROKEN_PASTE_RECOVERY_NO_REPLAY_NO_ORDER_20260613_225505

classification: PASS_R35C_R4O_BROKEN_PASTE_RECOVERY_SAFE_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4O_BROKEN_PASTE_RECOVERY_NO_REPLAY_NO_ORDER_20260613_225505.json`

## safety
orders=0 risk=0 execution=0 proc=0/0 replay_proc=0

## compile_rc
0

## R4O markers
3568:                "_r35c_r4l_top_level_truncated": True,

## source context
  3485	            "feature_rows",
  3486	            "linked_feature",
  3487	            "linked_feature_row",
  3488	            "decision_payload",
  3489	            "payload",
  3490	            "raw",
  3491	            "raw_payload",
  3492	            "raw_frame",
  3493	            "debug",
  3494	            "debug_payload",
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

## recent R4O backups/audits
run/_code_backups/R35C_R4O_PRESERVE_TOP_LEVEL_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225136_bin_replay_run.py.bak
run/_code_backups/R35C_R4O_PRESERVE_TOP_LEVEL_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225117_bin_replay_run.py.bak
run/audits/R35C_R4O_PRESERVE_TOP_LEVEL_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225117_report.md

run/audits/R35C_R4O_BROKEN_PASTE_RECOVERY_NO_REPLAY_NO_ORDER_20260613_225505:
audit.txt
r4o_markers.txt
compile.log

run/audits/R35C_R4O_PRESERVE_TOP_LEVEL_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225136:

run/audits/R35C_R4O_PRESERVE_TOP_LEVEL_CAP_MARKER_NO_REPLAY_NO_ORDER_20260613_225117:

## Compile log
