# B3-R31A_ARTIFACTS_PY_EXPORT_INSERTION_POINT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification is PASS:

Run B3-R32 one-file offline patch in `app/mme_scalpx/replay/artifacts.py`.

Patch law:

1. Do not insert export logic inside `validate_artifact_plan_path_containment`.
2. Add B3_R32 helper functions near artifact/write helpers.
3. Call export generation only after existing replay row artifacts are written.
4. No strategy/risk/execution/provider changes.
5. No replay in patch batch.
6. Compile/AST proof only.
