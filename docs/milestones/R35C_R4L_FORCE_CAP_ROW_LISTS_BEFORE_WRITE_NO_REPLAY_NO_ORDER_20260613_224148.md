# R35C_R4L_FORCE_CAP_ROW_LISTS_BEFORE_WRITE_NO_REPLAY_NO_ORDER_20260613_224148

classification: PASS_R35C_R4L_FORCE_CAP_ROW_LISTS_BEFORE_WRITE_PATCHED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4L_FORCE_CAP_ROW_LISTS_BEFORE_WRITE_NO_REPLAY_NO_ORDER_20260613_224148.json`
backup: `run/_code_backups/R35C_R4L_FORCE_CAP_ROW_LISTS_BEFORE_WRITE_NO_REPLAY_NO_ORDER_20260613_224148_bin_replay_run.py.bak`

patch_rc=0 compile_rc=0 marker_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Patch log
patched=1

## Patch errors

## Markers
3557:    # R35C/R4L: force cap row lists before artifact writes.
3560:    def _r35c_r4l_force_row_cap(label, rows):
3568:                "_r35c_r4l_top_level_truncated": True,
3573:                "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP force cap before artifact write",
3578:    persisted_feature_rows = _r35c_r4l_force_row_cap("features_rows", persisted_feature_rows)
3585:    persisted_strategy_decisions = _r35c_r4l_force_row_cap("strategy_decisions", persisted_strategy_decisions)
3592:    persisted_risk_outputs = _r35c_r4l_force_row_cap("risk_outputs", persisted_risk_outputs)
3597:    persisted_execution_shadow_results = _r35c_r4l_force_row_cap("execution_shadow_results", persisted_execution_shadow_results)

## Compile log
