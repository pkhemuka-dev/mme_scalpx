# R35C_R4J2_ROBUST_EARLY_SUMMARY_AND_HARD_ROW_CAP_PATCH_NO_REPLAY_NO_ORDER_20260613_223612

classification: PASS_R35C_R4J2_ROBUST_EARLY_SUMMARY_AND_HARD_ROW_CAP_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4J2_ROBUST_EARLY_SUMMARY_AND_HARD_ROW_CAP_PATCH_NO_REPLAY_NO_ORDER_20260613_223612.json`
backup: `run/_code_backups/R35C_R4J2_ROBUST_EARLY_SUMMARY_AND_HARD_ROW_CAP_PATCH_NO_REPLAY_NO_ORDER_20260613_223612_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1

## Patch errors

## Markers
3410:        # R35C/R4J2: minimal early summary must not call build_run_summary_payload.
3417:            "summary_write_mode": "early_minimal_r35c_r4j2",
3531:        # R35C/R4J2: hard top-level row cap before JSON serialization.
3543:                "_r35c_r4j_top_level_truncated": True,

## Compile log
