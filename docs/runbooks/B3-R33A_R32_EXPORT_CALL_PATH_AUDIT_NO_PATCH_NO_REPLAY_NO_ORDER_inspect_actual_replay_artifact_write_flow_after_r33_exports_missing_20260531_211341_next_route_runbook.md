# B3-R33A_R32_EXPORT_CALL_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If root cause is unused `write_core_artifact_bundle`:

1. Do not patch strategy/risk/execution/provider.
2. Patch only artifact/materializer flow.
3. Add a call to `write_b3_r32_analysis_exports` from the actual replay artifact materialization path.
4. Compile/AST only in patch batch.
5. Then rerun R33 smoke.

If root cause differs, inspect audit before patching.
