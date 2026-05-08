# Batch 30J-R3 Runbook

Repairs the 30J-R2 replay command by adding required `replay_run.py` arguments: `--selection-mode`, `--doctrine-mode`, and `--scope`.

This batch does not execute replay. It writes a repaired command contract for 30J-R4.

Chosen safe values: `selection-mode=single_day`, `doctrine-mode=locked`, and `scope=feeds_features_strategy_risk_execution_shadow`.

If GREEN_CONTINUE, run 30J-R4 guarded offline replay execution retry with strict no-broker/no-live/no-order checks.
