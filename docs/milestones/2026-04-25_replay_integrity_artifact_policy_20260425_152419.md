# Replay Integrity and Artifact Policy Inspection — 2026-04-25

## Purpose
Inspect why replay pipeline materializes rows but integrity verdict remains FAIL.

## Current known facts
- features rows materialized
- strategy rows materialized
- risk rows materialized
- execution shadow stage reported outputs in stage records
- integrity report has verdict=fail with checks=[]

## Artifacts
- run/proofs/replay_integrity_and_artifact_policy_20260425_152419/integrity_code_context.log
- run/proofs/replay_integrity_and_artifact_policy_20260425_152419/replay_output_distribution.log
