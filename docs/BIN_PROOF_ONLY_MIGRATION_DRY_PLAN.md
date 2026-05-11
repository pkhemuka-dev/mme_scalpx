# MME-ScalpX Proof-Only Bin Migration Dry Plan

Generated: 2026-05-11T23:22:53.229610

## Safety

- No files moved.
- No files deleted.
- No git index changed.
- No services started.
- No broker calls.
- No Redis writes.
- No paper/live enablement.

## Source Proofs

- R4 classification proof: `run/proofs/repo_hygiene_r4_bin_classification_audit_20260511_231100.json`
- R6 manual audit proof: `run/proofs/repo_hygiene_r6_manual_bin_script_audit_20260511_231540.json`

## Candidate Summary

- total_proof_rows: 296
- safe_proof_candidates: 12
- rejected_proof_candidates: 284
- first_batch_size: 12

## First Batch Dry Plan

### `bin/proof_feature_family_strategy_surfaces.py`

- target: `bin/proofs/proof_feature_family_strategy_surfaces.py`
- size_bytes: 743
- reference_hit_count: 6
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131955.md:27` — - `bin/proof_feature_family_strategy_surfaces.py`
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:159` — "bin/proof_feature_family_strategy_surfaces.py",
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:301` — "bin/proof_feature_family_strategy_surfaces.py",
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131221.md:27` — - `bin/proof_feature_family_strategy_surfaces.py`
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131053.md:27` — - `bin/proof_feature_family_strategy_surfaces.py`

### `bin/proof_feature_family_surfaces_batch9_freeze.py`

- target: `bin/proofs/proof_feature_family_surfaces_batch9_freeze.py`
- size_bytes: 11296
- reference_hit_count: 5
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:302` — "bin/proof_feature_family_surfaces_batch9_freeze.py",
  - `docs/milestones/2026-04-25_batch9_feature_family_surfaces_corrective_freeze_final.md:39` — - `bin/proof_feature_family_surfaces_batch9_freeze.py` returns status PASS
  - `docs/research_gate/RAW_SOURCE_SURFACE_AUDIT.md:383` — - `bin/proof_feature_family_surfaces_batch9_freeze.py`
  - `bin/proof_feature_family_strategy_surfaces.py:11` — proof_feature_family_surfaces_batch9_freeze.py
  - `bin/proof_feature_family_strategy_surfaces.py:21` — TARGET = Path(__file__).resolve().with_name("proof_feature_family_surfaces_batch9_freeze.py")

### `bin/proof_feature_selected_side_isolation.py`

- target: `bin/proofs/proof_feature_selected_side_isolation.py`
- size_bytes: 1735
- reference_hit_count: 0
- compatibility_wrapper_required: False

### `bin/proof_feature_side_direct_member_surface.py`

- target: `bin/proofs/proof_feature_side_direct_member_surface.py`
- size_bytes: 1748
- reference_hit_count: 0
- compatibility_wrapper_required: False

### `bin/proof_features_false_readiness_guards.py`

- target: `bin/proofs/proof_features_false_readiness_guards.py`
- size_bytes: 1473
- reference_hit_count: 5
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131955.md:25` — - `bin/proof_features_false_readiness_guards.py`
  - `docs/milestones/2026-04-25_remaining_offline_final_proofs_20260425_133419.md:6` — - bin/proof_features_false_readiness_guards.py
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131221.md:25` — - `bin/proof_features_false_readiness_guards.py`
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131053.md:25` — - `bin/proof_features_false_readiness_guards.py`
  - `bin/run_final_freeze_bundle.py:71` — "bin/proof_features_false_readiness_guards.py",

### `bin/proof_feeds_lock_refresh_pre_poll.py`

- target: `bin/proofs/proof_feeds_lock_refresh_pre_poll.py`
- size_bytes: 2000
- reference_hit_count: 1
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:160` — "bin/proof_feeds_lock_refresh_pre_poll.py",

### `bin/proof_provider_runtime_roles.py`

- target: `bin/proofs/proof_provider_runtime_roles.py`
- size_bytes: 374
- reference_hit_count: 5
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `etc/proof_registry.yaml:145` — bin/proof_provider_runtime_roles.py:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:320` — "bin/proof_provider_runtime_roles.py",
  - `docs/milestones/2026-04-25_integrations_batch5_freeze_final.md:20` — bin/proof_provider_runtime_roles.py
  - `docs/milestones/2026-04-25_batch25R1_replay_integrity_and_redis_matrix_scope_fix.md:49` — bin/proof_provider_runtime_roles.py	PASS	0
  - `bin/run_final_freeze_bundle.py:62` — "bin/proof_provider_runtime_roles.py",

### `bin/proof_replay_engine_contracts.py`

- target: `bin/proofs/proof_replay_engine_contracts.py`
- size_bytes: 659
- reference_hit_count: 10
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `etc/proof_registry.yaml:166` — bin/proof_replay_engine_contracts.py:
  - `docs/milestones/2026-04-25_batch25R_closed_market_proof_hygiene_corrective.md:41` — bin/proof_replay_engine_contracts.py	FAIL	1
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131955.md:34` — - `bin/proof_replay_engine_contracts.py`
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:178` — "bin/proof_replay_engine_contracts.py",
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:323` — "bin/proof_replay_engine_contracts.py",

### `bin/proof_risk_exit_never_blocked.py`

- target: `bin/proofs/proof_risk_exit_never_blocked.py`
- size_bytes: 339
- reference_hit_count: 4
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `etc/proof_registry.yaml:160` — bin/proof_risk_exit_never_blocked.py:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:328` — "bin/proof_risk_exit_never_blocked.py",
  - `docs/milestones/2026-04-25_batch25R1_replay_integrity_and_redis_matrix_scope_fix.md:53` — bin/proof_risk_exit_never_blocked.py	PASS	0
  - `bin/run_final_freeze_bundle.py:90` — "bin/proof_risk_exit_never_blocked.py",

### `bin/proof_risk_replay_key_separation.py`

- target: `bin/proofs/proof_risk_replay_key_separation.py`
- size_bytes: 934
- reference_hit_count: 5
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131955.md:32` — - `bin/proof_risk_replay_key_separation.py`
  - `docs/milestones/2026-04-25_remaining_offline_final_proofs_20260425_133419.md:11` — - bin/proof_risk_replay_key_separation.py
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131221.md:32` — - `bin/proof_risk_replay_key_separation.py`
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131053.md:32` — - `bin/proof_risk_replay_key_separation.py`
  - `bin/run_final_freeze_bundle.py:92` — "bin/proof_risk_replay_key_separation.py",

### `bin/proof_runtime_effective_config.py`

- target: `bin/proofs/proof_runtime_effective_config.py`
- size_bytes: 2227
- reference_hit_count: 7
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `etc/config_registry.yaml:43` — in current main.py behavior, proof_runtime_effective_config.py must show the
  - `etc/proof_registry.yaml:142` — bin/proof_runtime_effective_config.py:
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:330` — "bin/proof_runtime_effective_config.py",
  - `docs/milestones/2026-04-25_batch25R1_replay_integrity_and_redis_matrix_scope_fix.md:48` — bin/proof_runtime_effective_config.py	PASS	0
  - `docs/milestones/2026-04-25_batch3_clock_proof_api_fix.md:27` — - `bin/proof_runtime_effective_config.py`

### `bin/proof_strategy_family_doctrine_leaves.py`

- target: `bin/proofs/proof_strategy_family_doctrine_leaves.py`
- size_bytes: 709
- reference_hit_count: 5
- compatibility_wrapper_required: True
- reference_hits_sample:
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131955.md:28` — - `bin/proof_strategy_family_doctrine_leaves.py`
  - `docs/milestones/2026-04-29_batch26h_alias_override_inventory.md:191` — "bin/proof_strategy_family_doctrine_leaves.py",
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131221.md:28` — - `bin/proof_strategy_family_doctrine_leaves.py`
  - `docs/milestones/2026-04-25_final_freeze_gap_triage_20260425_131053.md:28` — - `bin/proof_strategy_family_doctrine_leaves.py`
  - `bin/run_final_freeze_bundle.py:80` — "bin/proof_strategy_family_doctrine_leaves.py",

## Rule For Actual Migration

Actual migration must be a separate patch.

For each moved script:

1. Move `bin/file.py` to `bin/proofs/file.py`.
2. Leave a compatibility wrapper at the old path if reference hits exist.
3. Compile moved Python files where applicable.
4. Do not execute proof scripts.
5. Write proof JSON and milestone.

Do not include broker/token/provider/probe/runtime/controlled-paper scripts in first migration.
