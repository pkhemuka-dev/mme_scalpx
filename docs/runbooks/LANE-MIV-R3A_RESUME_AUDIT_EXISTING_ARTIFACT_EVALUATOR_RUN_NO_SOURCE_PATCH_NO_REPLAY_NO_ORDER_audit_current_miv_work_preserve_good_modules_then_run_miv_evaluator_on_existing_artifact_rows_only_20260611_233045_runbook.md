# LANE-MIV-R3A_RESUME_AUDIT_EXISTING_ARTIFACT_EVALUATOR_RUN_NO_SOURCE_PATCH_NO_REPLAY_NO_ORDER_audit_current_miv_work_preserve_good_modules_then_run_miv_evaluator_on_existing_artifact_rows_only_20260611_233045 Runbook

This batch:
1. Audits current MIV-R work.
2. Preserves existing good modules.
3. Reads existing artifact rows only.
4. Applies MIV-ZERODHA-LITE evaluator.
5. Writes combined MIV artifacts.
6. Confirms candidate_intent-compatible fields.

It must not:
- run replay_run.py
- start services
- send orders
- mutate production registries
- touch Redis or locks
