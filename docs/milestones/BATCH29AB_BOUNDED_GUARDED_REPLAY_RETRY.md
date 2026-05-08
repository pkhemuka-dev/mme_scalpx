# Batch 29AB — Bounded Guarded Replay Retry

generated_at_utc: 2026-05-02T06:27:26.136822+00:00
verdict: `DEFER_BOUNDED_GUARDED_REPLAY_RETRY_29AB`
blockers: `['DRY_RUN_RETURNED_NONZERO:2']`

## Scope

- bounded guarded offline replay dry-run retry
- no broker IO
- no live Redis writes
- no service start
- no order sending
- no paper/live enablement

## Proofs

- proof: `run/proofs/proof_bounded_guarded_replay_retry_29ab.json`
- latest: `run/proofs/proof_bounded_guarded_replay_retry_29ab_latest.json`
- driver_proof: `run/proofs/batch29ab_bounded_guarded_replay_retry_20260502_115726_driver_proof.json`
- config: `etc/replay/parity/bounded_guarded_replay_retry_29ab.json`
- backup_dir: `run/_code_backups/batch29ab_bounded_guarded_replay_retry_20260502_115726`

## Next

Batch 29AC — inspect 29AB dry-run artifacts and repair next bounded offline replay parity gap only.
