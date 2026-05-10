# Batch 30J-R5Z Guarded Replay After Feature Source Promotion

Verdict: PASS_RERUN_REPLAY_FEATURE_SOURCE_PROMOTION_CLEAN
Classification: FEATURE_SOURCE_FIELDS_TOP_LEVEL_REPLAY_RUNTIME_SAFE

Selected root: run/replay
Selected date: 2026-04-17
Doctrine mode: locked
Scope: feeds_features_strategy_risk_execution_shadow
Replay rc: 0
Run root: run/replay/guarded_offline/batch30j_r5z_20260417_20260510_094436
Inner run: run/replay/guarded_offline/batch30j_r5z_20260417_20260510_094436/replay_locked_single_day_20260510_041436_cca8f049
Integrity verdict: pass
Integrity failed checks: 0
Integrity placeholder count: 0
Feature source promotion OK: true
Row counts aligned: true

No paper/live enablement.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution service start.

Stdout:
run/proofs/stdout_batch30j_r5z_guarded_replay_after_feature_promotion_20260510_094436.log

Stderr:
run/proofs/stderr_batch30j_r5z_guarded_replay_after_feature_promotion_20260510_094436.log

Next:
Rerun replay/live parity surface audit; still no paper/live.
