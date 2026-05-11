# 30J-R5BF Runbook

Purpose: prove the R5BE guarded option-only futures-context seam behaves fail-closed before any replay execution.

Validated surfaces:

- CLI flag exists in `bin/replay_run.py --help`
- default disabled guard returns disabled
- non-staging dataset root fails
- non-single-day selection mode fails
- final replay repository date present fails when an existing final date is available
- missing `opt_ticks.jsonl` fails using a transient removed staging fixture
- positive staging option-only dataset with `fut_ltp` passes helper validation

This batch does not authorize A64 execution by itself. Lane E must inspect the proof first.

Latest proof: `run/proofs/proof_batch30j_r5bf_no_execution_cli_guard_validation_latest.json`
