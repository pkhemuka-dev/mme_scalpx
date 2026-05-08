# REPLAY-DATA-A11 features_rows reconstruction 20260508T180133Z

- canonical_root: `run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z`
- source_date: `2026-04-17`
- features_rows_candidate_written: `true`
- row_count: `50021`
- selector_plan_ok: `true`
- engine_ready: `false`
- replay_engine_execution: `false`
- candidate_path: `run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/features_rows_candidate.csv`
- proof: `run/proofs/proof_replay_data_a11_features_rows_reconstruction_20260508T180133Z.json`
- next_batch: `REPLAY-DATA-A12 strategy_decisions shadow reconstruction audit`

A11 only materialized a conservative quote-derived features_rows candidate and ran a selector-only filesystem validation. It did not create strategy_decisions, risk_outputs, or execution_shadow.
