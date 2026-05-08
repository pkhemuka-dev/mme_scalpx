# Batch 29AC — Inspect 29AB Retry Failure

generated_at_utc: 2026-05-02T06:29:40.074416+00:00
verdict: `PASS_INSPECT_29AB_RETRY_FAILURE_29AC`
blockers: `['NEXT_GAP_CLASSIFIED_REPAIR_NOT_APPLIED_IN_29AC']`
classified_failure_kind: `CLI_OR_ARGPARSE_GAP`

## Scope

- inspect 29AB stdout/stderr only
- classify next bounded offline replay parity gap
- no code patch
- no replay execution
- no broker IO
- no live Redis writes
- no paper/live enablement

## Repair recommendation

Inspect guarded dry-run invocation/argparse contract; patch only the dry-run wrapper or expected argument names.

## Proofs

- proof: `run/proofs/proof_inspect_29ab_retry_failure_29ac.json`
- latest: `run/proofs/proof_inspect_29ab_retry_failure_29ac_latest.json`
- driver_proof: `run/proofs/batch29ac_inspect_29ab_retry_failure_20260502_115940_driver_proof.json`
- config: `etc/replay/parity/inspect_29ab_retry_failure_29ac.json`
- backup_dir: `run/_code_backups/batch29ac_inspect_29ab_retry_failure_20260502_115940`

## Next

Batch 29AD — repair guarded dry-run CLI/argparse contract only, still no paper/live enablement.
