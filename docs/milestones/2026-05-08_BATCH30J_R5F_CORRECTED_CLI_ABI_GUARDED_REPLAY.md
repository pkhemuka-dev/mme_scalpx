# Batch 30J-R5F Corrected CLI ABI Guarded Replay

Verdict: PASS_CORRECTED_CLI_GUARDED_OFFLINE_REPLAY_COMPLETED
Classification: REPLAY_EXECUTED_RUNTIME_SAFETY_CLEAN

Selected root: run/replay
Selected date: 2026-04-17
Doctrine mode: locked
Scope: feeds_features_strategy_risk_execution_shadow
Replay rc: 0
Run root: run/replay/guarded_offline/batch30j_r5f_20260417_20260508_123636

No paper/live enablement.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution service start.

Stdout:
run/proofs/stdout_batch30j_r5f_corrected_cli_abi_replay_20260508_123636.log

Stderr:
run/proofs/stderr_batch30j_r5f_corrected_cli_abi_replay_20260508_123636.log

Next:
Classify replay outputs: features, strategy, risk/execution-shadow artifacts, reports, metrics.
