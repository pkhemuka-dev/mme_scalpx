# R35B_R4G2_fix_b3r32_skip_patch_20260613_180454

classification: REVIEW_R35B_R4G2_REPAIR_INCOMPLETE_OR_SAFETY_NOT_CLEAN_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4G2_fix_b3r32_skip_patch_20260613_180454.json`
restored_from: `run/_code_backups/R35B_R4G_skip_b3r32_heavy_export_20260613_180252_bin_replay_run.py.bak`
new_backup: `run/_code_backups/R35B_R4G2_fix_b3r32_skip_patch_20260613_180454_bin_replay_run.py.bak`

patch_rc=0 compile_rc=1
safety pre=0/0/0 post=0/0/0 proc=0/0

## Patch log
patched R4G2 skip block

## Markers
3484:        if os.environ.get("SCALPX_REPLAY_SKIP_B3_R32_EXPORTS", "0").strip().lower() in {"1", "true", "yes"}:
3489:                    "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G2 to avoid heavy features_rows.json readback",
3500:        writer.write_b3_r32_analysis_exports(run_context)

## Compile log
Sorry: IndentationError: expected an indented block after 'if' statement on line 3484 (replay_run.py, line 3485)