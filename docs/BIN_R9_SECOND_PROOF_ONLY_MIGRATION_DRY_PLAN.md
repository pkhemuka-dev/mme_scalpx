# R9 Second Proof-Only Bin Migration Dry Plan

Generated: 2026-05-11T23:46:03.808678

## Safety

- No files moved.
- No files deleted.
- No scripts executed.
- No services started.
- No broker calls.
- No Redis writes.
- No paper/live enablement.

## Inputs

- R4 proof: `run/proofs/repo_hygiene_r4_bin_classification_audit_20260511_231100.json`
- R8G proof: `run/proofs/repo_hygiene_r8g_final_verify_r8_closure_20260511_233524.json`

## Summary

- total_proof_rows_from_R4: 296
- already_migrated_sources: 7
- excluded_sources: 5
- candidate_rows: 9
- rejected_rows: 287
- second_batch_size: 9

## Second Batch Dry Plan

### `bin/proof_clock_session_policy.py`

- target: `bin/proofs/proof_clock_session_policy.py`
- size_bytes: 4209
- content_flags: `CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `none`
- reference_hit_count: 6
- compatibility_wrapper_required: True
- score: 8
- reference_hits_sample:
  - `docs/milestones/2026-04-25_batch17_clock_proof_replayclock_api_corrective.md:15` — `bin/proof_clock_session_policy.py` used stale ReplayClock constructor names:
  - `docs/milestones/2026-04-25_batch17_clock_proof_replayclock_api_corrective.md:37` — - `bin/proof_clock_session_policy.py` returns PASS
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:293` — "bin/proof_clock_session_policy.py",
  - `docs/milestones/2026-04-25_batch3_clock_proof_api_fix.md:7` — `bin/proof_clock_session_policy.py` called non-existent API:
  - `docs/milestones/2026-04-25_batch3_clock_proof_api_fix.md:28` — - `bin/proof_clock_session_policy.py`

### `bin/proof_monitor_redis_attr_contract.py`

- target: `bin/proofs/proof_monitor_redis_attr_contract.py`
- size_bytes: 1485
- content_flags: `REDIS_TERM, CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `REDIS_MENTION`
- reference_hit_count: 2
- compatibility_wrapper_required: True
- score: 10
- reference_hits_sample:
  - `docs/milestones/2026-04-27_batch25v_market_session_hold_observation.md:215` — - added proof `bin/proof_monitor_redis_attr_contract.py`
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:315` — "bin/proof_monitor_redis_attr_contract.py",

### `bin/proof_lock_refresh_contract.py`

- target: `bin/proofs/proof_lock_refresh_contract.py`
- size_bytes: 3223
- content_flags: `REDIS_TERM, CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `REDIS_MENTION`
- reference_hit_count: 3
- compatibility_wrapper_required: True
- score: 11
- reference_hits_sample:
  - `docs/milestones/2026-04-27_batch25v_market_session_hold_observation.md:274` — - rewrote `bin/proof_lock_refresh_contract.py` with correct redisx call signature
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:165` — "bin/proof_lock_refresh_contract.py",
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:305` — "bin/proof_lock_refresh_contract.py",

### `bin/proof_family_features_canonical_support.py`

- target: `bin/proofs/proof_family_features_canonical_support.py`
- size_bytes: 11650
- content_flags: `REDIS_TERM, CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `REDIS_MENTION`
- reference_hit_count: 4
- compatibility_wrapper_required: True
- score: 12
- reference_hits_sample:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:156` — "bin/proof_family_features_canonical_support.py",
  - `docs/research_gate/RAW_SOURCE_SURFACE_AUDIT.md:386` — - `bin/proof_family_features_canonical_support.py`
  - `bin/proof_5family_integration_master.py:129` — script_candidates=("bin/proof_family_features_canonical_support.py",),
  - `bin/proof_5family_integration_master.py:241` — "bin/proof_family_features_canonical_support.py",

### `bin/proof_redisx_typed_stream_helpers.py`

- target: `bin/proofs/proof_redisx_typed_stream_helpers.py`
- size_bytes: 2281
- content_flags: `REDIS_TERM, CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `REDIS_MENTION`
- reference_hit_count: 4
- compatibility_wrapper_required: True
- score: 12
- reference_hits_sample:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:321` — "bin/proof_redisx_typed_stream_helpers.py",
  - `docs/milestones/2026-04-25_batch3_clock_proof_api_fix.md:26` — - `bin/proof_redisx_typed_stream_helpers.py`
  - `bin/run_final_freeze_bundle.py:52` — "bin/proof_redisx_typed_stream_helpers.py",
  - `bin/proof_core_infra_batch18_freeze.py:16` — ("redisx_typed_stream_helpers", "bin/proof_redisx_typed_stream_helpers.py", "run/proofs/redisx_typed_stream_helpers.json"),

### `bin/proof_names_alias_lifecycle.py`

- target: `bin/proofs/proof_names_alias_lifecycle.py`
- size_bytes: 4993
- content_flags: `REDIS_TERM, CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `ORDER_MENTION`
- reference_hit_count: 5
- compatibility_wrapper_required: True
- score: 13
- reference_hits_sample:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:172` — "bin/proof_names_alias_lifecycle.py",
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:604` — "bin/proof_names_alias_lifecycle.py",
  - `docs/milestones/2026-04-25_batch25R1_replay_integrity_and_redis_matrix_scope_fix.md:57` — bin/proof_names_alias_lifecycle.py	PASS	0
  - `docs/milestones/2026-04-25_batch20_legacy_quarantine_freeze.md:13` — - `bin/proof_names_alias_lifecycle.py`
  - `bin/run_final_freeze_bundle.py:53` — "bin/proof_names_alias_lifecycle.py",

### `bin/proof_risk_trade_ledger_idempotency.py`

- target: `bin/proofs/proof_risk_trade_ledger_idempotency.py`
- size_bytes: 1076
- content_flags: `REDIS_TERM, CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `ORDER_MENTION|REDIS_MENTION`
- reference_hit_count: 5
- compatibility_wrapper_required: True
- score: 13
- reference_hits_sample:
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131955.md:33` — - `bin/proof_risk_trade_ledger_idempotency.py`
  - `docs/milestones/2026-04-25_remaining_offline_final_proofs_20260425_133419.md:12` — - bin/proof_risk_trade_ledger_idempotency.py
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131221.md:33` — - `bin/proof_risk_trade_ledger_idempotency.py`
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131053.md:33` — - `bin/proof_risk_trade_ledger_idempotency.py`
  - `bin/run_final_freeze_bundle.py:93` — "bin/proof_risk_trade_ledger_idempotency.py",

### `bin/proof_core_codec_transport.py`

- target: `bin/proofs/proof_core_codec_transport.py`
- size_bytes: 3808
- content_flags: `CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `ORDER_MENTION`
- reference_hit_count: 7
- compatibility_wrapper_required: True
- score: 14
- reference_hits_sample:
  - `docs/BIN_CLASSIFICATION_AUDIT.md:199` — - `bin/proof_core_codec_transport.py` — ORDER_MENTION
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:152` — "bin/proof_core_codec_transport.py",
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:295` — "bin/proof_core_codec_transport.py",
  - `docs/milestones/2026-04-25_batch25R1_replay_integrity_and_redis_matrix_scope_fix.md:47` — bin/proof_core_codec_transport.py	PASS	0
  - `docs/milestones/2026-04-25_batch3_clock_proof_api_fix.md:25` — - `bin/proof_core_codec_transport.py`

### `bin/proof_redis_contract_matrix.py`

- target: `bin/proofs/proof_redis_contract_matrix.py`
- size_bytes: 5832
- content_flags: `REDIS_TERM, CONFIG_TERM, PROOF_TERM`
- r4_risk_flags: `REDIS_MENTION`
- reference_hit_count: 10
- compatibility_wrapper_required: True
- score: 18
- reference_hits_sample:
  - `etc/proof_registry.yaml:139` — bin/proof_redis_contract_matrix.py:
  - `docs/milestones/2026-04-25_batch25R_closed_market_proof_hygiene_corrective.md:39` — bin/proof_redis_contract_matrix.py --strict-raw	FAIL	1
  - `docs/milestones/2026-04-25_batch1_names_freeze_pass.md:18` — - `bin/proof_redis_contract_matrix.py`
  - `docs/milestones/2026-04-25_batch17_clock_proof_replayclock_api_corrective.md:39` — - `bin/proof_redis_contract_matrix.py --strict-raw` returns PASS
  - `docs/milestones/2026-04-25_batch25R1_replay_integrity_and_redis_matrix_scope_fix.md:34` — bin/proof_redis_contract_matrix.py --strict-raw	PASS	0

## Migration Rule

Actual R10 migration must:

1. Move only the R9 selected batch.
2. Leave compatibility wrappers at old paths.
3. Compile wrappers and targets.
4. Exclude any file whose target becomes wrapper/stub-shaped.
5. Execute no scripts.
6. Touch no runtime/broker/Redis/paper/live.
