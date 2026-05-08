# Batch 29AG — Bounded Guarded Replay Retry After 29AF

generated_at_utc: 2026-05-02T06:36:09.777700+00:00
verdict: `DEFER_BOUNDED_GUARDED_REPLAY_RETRY_AFTER_29AF_29AG`
blockers: `['GUARDED_RETRY_RETURNED_NONZERO:2']`
classified_failure_kind: `RETURN_CODE_2_AFTER_29AF_UNCLASSIFIED`

## Scope

- bounded guarded offline replay dry-run retry
- no code patch
- no broker IO
- no live Redis writes
- no service start
- no order sending
- no paper/live enablement

## Proofs

- proof: `run/proofs/proof_bounded_guarded_replay_retry_after_29af_29ag.json`
- latest: `run/proofs/proof_bounded_guarded_replay_retry_after_29af_29ag_latest.json`
- driver_proof: `run/proofs/batch29ag_bounded_guarded_replay_retry_after_29af_20260502_120609_driver_proof.json`
- config: `etc/replay/parity/bounded_guarded_replay_retry_after_29af_29ag.json`
- backup_dir: `run/_code_backups/batch29ag_bounded_guarded_replay_retry_after_29af_20260502_120609`

## Next

Batch 29AH — inspect 29AG retry artifacts and repair next bounded offline parity gap only.
