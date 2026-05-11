# R8E Failed Migration Inspection

Generated: 2026-05-11T23:32:21.081914

## Safety

- Inspection only.
- No files moved.
- No files deleted.
- No scripts executed.
- No services started.
- No broker calls.
- No Redis writes.
- No paper/live enablement.

## Failed Items

### `bin/proof_feature_family_strategy_surfaces.py` -> `bin/proofs/proof_feature_family_strategy_surfaces.py`

- source_exists_now: True
- target_exists_now: True
- source_is_wrapper_now: True
- target_is_wrapper_now: False
- source_points_to_target_now: True
- target_has_real_body_now: False
- recommended_action: `REVIEW_TARGET_NOT_REAL_BODY`

### `bin/proof_provider_runtime_roles.py` -> `bin/proofs/proof_provider_runtime_roles.py`

- source_exists_now: True
- target_exists_now: True
- source_is_wrapper_now: True
- target_is_wrapper_now: False
- source_points_to_target_now: True
- target_has_real_body_now: False
- recommended_action: `REVIEW_TARGET_NOT_REAL_BODY`

### `bin/proof_replay_engine_contracts.py` -> `bin/proofs/proof_replay_engine_contracts.py`

- source_exists_now: True
- target_exists_now: True
- source_is_wrapper_now: True
- target_is_wrapper_now: False
- source_points_to_target_now: True
- target_has_real_body_now: False
- recommended_action: `REVIEW_TARGET_NOT_REAL_BODY`

### `bin/proof_strategy_family_doctrine_leaves.py` -> `bin/proofs/proof_strategy_family_doctrine_leaves.py`

- source_exists_now: True
- target_exists_now: True
- source_is_wrapper_now: True
- target_is_wrapper_now: False
- source_points_to_target_now: True
- target_has_real_body_now: False
- recommended_action: `REVIEW_TARGET_NOT_REAL_BODY`

## Action Counts

- REVIEW_TARGET_NOT_REAL_BODY: 4

## Next

Run a targeted R8F repair only after reviewing this inspection.
