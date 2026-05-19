# B1B-R4B_CORRECTED_INGEST_B1A_LIFECYCLE_SCHEMA_NO_REPLAY_NO_PNL runbook

B1B next route:

1. Do not run replay or PnL.
2. Do not admit any family for backtest from status lifecycle rows.
3. Wait for a real observe-only capture containing strategy candidate lifecycle plus risk approval lifecycle plus execution-shadow trade lifecycle.
4. Only after that, run a new B1B admission matrix refresh.

Current accepted evidence type:

`observe_only_runtime_lifecycle_status_activation_only`