# LANE-X-R34A_WEEKEND_OFFLINE_CANDIDATE_TRUE_AND_MIV_ROOT_CAUSE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_enter_actions_without_candidate_true_and_miv_not_emitted_from_sealed_friday_durable_tape_20260613_101627

classification: PASS_R34A_WEEKEND_OFFLINE_CANDIDATE_TRUE_AND_MIV_ROOT_CAUSE_AUDIT_WRITTEN_NO_ORDER

## What this audited

Bounded offline scan of sealed Friday durable tape:

- decisions: `run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/decisions.jsonl.gz`
- features: `run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/features.jsonl.gz`
- provider_runtime: `run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/provider_runtime.jsonl.gz`
- errors: `run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/errors.jsonl.gz`

## Key result

- decision_rows_scanned: `6540`
- ENTER actions found: `0`
- candidate_true_total: `0`
- MIV decision objects: `0`
- MIV feature objects: `0`

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Artifacts

- durable audit: `run/audits/LANE-X-R34A_WEEKEND_OFFLINE_CANDIDATE_TRUE_AND_MIV_ROOT_CAUSE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_enter_actions_without_candidate_true_and_miv_not_emitted_from_sealed_friday_durable_tape_20260613_101627/durable_candidate_true_miv_audit.json`
- ENTER samples: `run/audits/LANE-X-R34A_WEEKEND_OFFLINE_CANDIDATE_TRUE_AND_MIV_ROOT_CAUSE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_enter_actions_without_candidate_true_and_miv_not_emitted_from_sealed_friday_durable_tape_20260613_101627/enter_without_candidate_true_samples.jsonl`
- MIV source grep: `run/audits/LANE-X-R34A_WEEKEND_OFFLINE_CANDIDATE_TRUE_AND_MIV_ROOT_CAUSE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_enter_actions_without_candidate_true_and_miv_not_emitted_from_sealed_friday_durable_tape_20260613_101627/miv_source_grep.txt`
- candidate source grep: `run/audits/LANE-X-R34A_WEEKEND_OFFLINE_CANDIDATE_TRUE_AND_MIV_ROOT_CAUSE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_enter_actions_without_candidate_true_and_miv_not_emitted_from_sealed_friday_durable_tape_20260613_101627/candidate_true_source_grep.txt`

## Boundary

- no patch
- no replay
- no service start/stop
- no broker order
- no risk/execution
- no paper/live
- no Redis delete
- no lock delete
