# Replay Integrity + Execution Shadow Persistence Patch — 2026-04-25

## Purpose
Persist real integrity report and execution shadow result rows.

## Patch
- Overwrite placeholder 03_integrity_report.json with real evaluated integrity bundle.
- Write artifacts/execution_shadow_results.json.
- Add execution shadow row/fill counts and action breakdown to run summary.

## Dataset
- run/replay_datasets/session_exports_quote_compat_20260425_150651/2026-04-21

## Artifacts
- run/proofs/replay_integrity_execution_shadow_persist_20260425_153204/replay_execution_shadow_after_patch.log
- run/proofs/replay_integrity_execution_shadow_persist_20260425_153204/verify_patched_artifacts.log
- run/replay_audits/integrity_execution_shadow_persist_20260425_153204
