# 30J-R5BE-R3 Runbook

Purpose: capture exact current `bin/replay_run.py` function ranges and candidate anchors after R5BE-R2 failed before mutation.

Review these audit files before patch retry:

- `run/audits/batch30j_r5be_r3_exact_source_anchor_audit_20260510_130120/build_feed_events_for_day_snippet.txt`
- `run/audits/batch30j_r5be_r3_exact_source_anchor_audit_20260510_130120/build_placeholder_checks_snippet.txt`
- `run/audits/batch30j_r5be_r3_exact_source_anchor_audit_20260510_130120/make_stage_executor_snippet.txt`
- `run/audits/batch30j_r5be_r3_exact_source_anchor_audit_20260510_130120/main_snippet.txt`
- `run/audits/batch30j_r5be_r3_exact_source_anchor_audit_20260510_130120/bin_replay_run_current_source.txt`

If verdict is PASS_EXACT_SOURCE_ANCHORS_CAPTURED_R5BE_R4_READY_NO_PATCH, next batch may retry the R5BE patch using exact anchors from this audit only.
