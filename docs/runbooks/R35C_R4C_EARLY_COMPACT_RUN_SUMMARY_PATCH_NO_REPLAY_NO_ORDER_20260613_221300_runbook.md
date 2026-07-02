# R35C_R4C_EARLY_COMPACT_RUN_SUMMARY_PATCH_NO_REPLAY_NO_ORDER_20260613_221300

classification: PASS_R35C_R4C_EARLY_COMPACT_RUN_SUMMARY_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4C_EARLY_COMPACT_RUN_SUMMARY_PATCH_NO_REPLAY_NO_ORDER_20260613_221300.json`
backup: `run/_code_backups/R35C_R4C_EARLY_COMPACT_RUN_SUMMARY_PATCH_NO_REPLAY_NO_ORDER_20260613_221300_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1

## Patch errors

## Markers
3403:    # R35C/R4C: write an early compact official run summary immediately after
3417:        early_run_summary_payload["summary_write_mode"] = "early_compact_r35c_r4c"
3432:            (Path(run_context.artifact_plan.artifacts_dir) / "10_run_summary_early_write_error.json").write_text(

## Compile log
