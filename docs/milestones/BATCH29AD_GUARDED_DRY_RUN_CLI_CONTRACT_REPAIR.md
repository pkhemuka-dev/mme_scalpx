# Batch 29AD — Guarded Dry-Run CLI Contract Repair

generated_at_utc: 2026-05-02T06:32:12.373243+00:00
verdict: `DEFER_GUARDED_DRY_RUN_CLI_CONTRACT_REPAIR_29AD`
blockers: `['GUARDED_DRY_RUN_RETURNED_NONZERO:2', 'BROKER_OR_LIVE_MARKER_IN_OUTPUT_REVIEW_REQUIRED']`

## Scope

- repair dry-run invocation contract via wrapper only
- no production doctrine change
- no broker IO
- no live Redis writes
- no service start
- no order sending
- no paper/live enablement

## Proofs

- proof: `run/proofs/proof_guarded_dry_run_cli_contract_repair_29ad.json`
- latest: `run/proofs/proof_guarded_dry_run_cli_contract_repair_29ad_latest.json`
- driver_proof: `run/proofs/batch29ad_guarded_dry_run_cli_contract_repair_20260502_120212_driver_proof.json`
- config: `etc/replay/parity/guarded_dry_run_cli_contract_repair_29ad.json`
- wrapper: `bin/guarded_replay_engine_execute_retry_29ad.py`
- backup_dir: `run/_code_backups/batch29ad_guarded_dry_run_cli_contract_repair_20260502_120212`

## Next

Batch 29AE — inspect 29AD retry artifacts and repair next bounded offline parity gap only.
