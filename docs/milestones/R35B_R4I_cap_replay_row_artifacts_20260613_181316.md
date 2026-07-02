# R35B_R4I_cap_replay_row_artifacts_20260613_181316

classification: PASS_R35B_R4I_REPLAY_ROW_ARTIFACT_CAP_PATCHED_COMPILE_SAFETY_CLEAN_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4I_cap_replay_row_artifacts_20260613_181316.json`
backup: `run/_code_backups/R35B_R4I_cap_replay_row_artifacts_20260613_181316_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## Patch log
patched_R35B_R4I_row_cap=1

## Markers
3409:        Set SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 or similar to persist only a
3414:            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
3435:                        d[k] = f"<omitted_by_R35B_R4I:{k}>"
3445:                    "_r35b_r4i_truncated": True,
3449:                    "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",

## Compile log
