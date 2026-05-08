# Batch 26-O16C-R2 — Environment-Corrected Guarded Mapping Repair

## Purpose

O16C failed safely because Redis was unavailable and the post-check subprocess could not import `app`.

O16C-R2 corrects the environment:

- `PYTHONPATH=$PWD`
- Redis PING precheck
- fail-closed if Redis is unavailable
- guarded O16B gate
- no paper/risk/execution start
- no forced `data_valid`

## Allowed Repair

Only if:

- O16B passed,
- Redis is available,
- active `FeatureService.run_once()` produces `family_features`, `family_surfaces`, and `family_frames`,
- but consumer view is absent.

Then O16C-R2 may add only a consumer-view publication bridge on the active `run_once` path.

## Safety

This batch does not:

- start paper,
- start risk,
- start execution,
- write orders,
- approve real live,
- force `data_valid=true`,
- relax thresholds,
- enable MISO.

## Proof

- `run/proofs/proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.json`
- `run/proofs/manifest_batch26o16c_r2_env_corrected_guarded_mapping_repair.json`
