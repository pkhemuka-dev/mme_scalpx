# Replay Integrity Fail Diagnosis — 2026-04-25

## Purpose
Diagnose why full replay pipeline materializes rows but integrity verdict remains FAIL.

## Current confirmed
- feeds injected 50,021 rows
- features published 50,021 rows
- strategy published 50,021 HOLD decisions
- risk published 50,021 HOLD outputs
- execution shadow published 50,021 outputs
- filled_count = 0

## Artifact
- run/proofs/replay_integrity_fail_diagnosis_20260425_152144/replay_integrity_fail_diagnosis.json
- run/proofs/replay_integrity_fail_diagnosis_20260425_152144/integrity_fail_diagnosis.log

## Next
Patch integrity criteria or dataset cleanliness only after diagnosis.
