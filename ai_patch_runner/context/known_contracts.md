# Known Contracts — MME AI Runner

## Replay chain current contract

- A7/A8/A8B/A9/A10 built selector-ready quote dataset.
- A11 wrote features_rows_candidate.csv.
- A12 wrote strategy_decisions_candidate.csv with conservative HOLD/NO_TRADE shadow rows.
- A13 wrote risk_outputs_candidate.csv with conservative risk/no-order shadow rows.
- A14 should create execution_shadow_candidate.csv only if schema-safe.
- Full replay engine remains disabled until all required candidate surfaces exist and selector/probe proofs pass.

## Safety contract

- No live/paper approval.
- No broker/API call.
- No service start.
- No Redis write.
- No production risk/execution/main patch.
- Candidate reconstruction is sandbox/offline under run/replay/parity/offline_materialization only.
