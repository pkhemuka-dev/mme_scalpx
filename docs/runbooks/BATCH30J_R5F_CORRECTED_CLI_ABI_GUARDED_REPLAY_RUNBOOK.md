# Batch 30J-R5F Runbook

Purpose:
Correct replay_run.py CLI ABI after 30J-R5E failed with invalid scope.

Corrected ABI:
- --doctrine-mode locked
- --scope feeds_features_strategy_risk_execution_shadow

Proof:
run/proofs/proof_batch30j_r5f_corrected_cli_abi_guarded_replay_latest.json

Stdout:
run/proofs/stdout_batch30j_r5f_corrected_cli_abi_replay_20260508_123636.log

Stderr:
run/proofs/stderr_batch30j_r5f_corrected_cli_abi_replay_20260508_123636.log

Run root:
run/replay/guarded_offline/batch30j_r5f_20260417_20260508_123636

Next:
Classify replay outputs: features, strategy, risk/execution-shadow artifacts, reports, metrics.
