# B3-R33B_R32_EXPORT_CALL_PLACEMENT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

If classification says call after return or outside method:

Run B3-R34 one-file patch in `app/mme_scalpx/replay/artifacts.py`.

Patch goal:

- Move `self.write_b3_r32_analysis_exports(...)` before final return in `write_core_artifact_bundle`.
- Do not touch strategy/risk/execution/provider/replay_run.
- Compile/AST only.
- Then rerun R33 smoke.
