# R35B_R4S_RECURSIVE_ARTIFACT_SLIM_PATCH_NO_REPLAY_NO_ORDER_20260613_191514

classification: PASS_R35B_R4S_RECURSIVE_ARTIFACT_SLIM_PATCHED_COMPILE_SAFETY_CLEAN_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4S_RECURSIVE_ARTIFACT_SLIM_PATCH_NO_REPLAY_NO_ORDER_20260613_191514.json`
backup: `run/_code_backups/R35B_R4S_RECURSIVE_ARTIFACT_SLIM_PATCH_NO_REPLAY_NO_ORDER_20260613_191514_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## Patch log
patched_R35B_R4S_recursive_artifact_slim=1

## Markers
3407:        """R35B/R4S replay artifact slimming.
3410:        Use SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 to persist small samples instead
3414:            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
3445:                return "<omitted_by_R35B_R4S:max_depth>"
3453:                        "_r35b_r4s_truncated": True,
3457:                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
3465:                        out[k] = f"<omitted_by_R35B_R4S:{k}>"

## Compile log
