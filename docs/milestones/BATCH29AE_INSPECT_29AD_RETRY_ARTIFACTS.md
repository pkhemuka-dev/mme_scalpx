# Batch 29AE — Inspect 29AD Retry Artifacts

generated_at_utc: 2026-05-02T06:33:37.071916+00:00
verdict: `PASS_INSPECT_29AD_RETRY_ARTIFACTS_29AE`
blockers: `['NEXT_GAP_CLASSIFIED_REPAIR_NOT_APPLIED_IN_29AE']`
classified_failure_kind: `NEXT_ATTRIBUTE_RUNTIME_GAP`

## Scope

- inspect 29AD stdout/stderr/output-root artifacts only
- classify next bounded offline parity gap
- no code patch
- no replay execution
- no broker IO
- no live Redis writes
- no paper/live enablement

## Repair recommendation

Patch only the missing offline attribute alias after inspecting producer/consumer. Observed: 'OfflineReplayStage' object has no attribute 'owns_runtime_decisioning'"

## Proofs

- proof: `run/proofs/proof_inspect_29ad_retry_artifacts_29ae.json`
- latest: `run/proofs/proof_inspect_29ad_retry_artifacts_29ae_latest.json`
- driver_proof: `run/proofs/batch29ae_inspect_29ad_retry_artifacts_20260502_120337_driver_proof.json`
- config: `etc/replay/parity/inspect_29ad_retry_artifacts_29ae.json`
- backup_dir: `run/_code_backups/batch29ae_inspect_29ad_retry_artifacts_20260502_120337`

## Next

Batch 29AF — repair next offline attribute alias only, still no paper/live enablement.
