# LANE-X-R32D-R1_REPAIR_SMOKE_INTERNAL_ORDER_INTENT_PIPELINE_NO_NEW_PATCH_NO_REPLAY_NO_ORDER_rerun_existing_r32d_patch_smoke_with_pythonpath_and_capture_untracked_files_20260611_225709

classification: PASS_R32D_R1_INTERNAL_ORDER_INTENT_PIPELINE_SMOKE_REPAIRED_NO_NEW_PATCH_NO_REPLAY_NO_ORDER

## What R32D-R1 did

R32D-R1 did not rewrite the patch. It repaired the smoke execution by running the existing R32D proof with:

`PYTHONPATH=$PWD`

## Smoke result

- underlying_smoke_classification: `PASS_R32D_INTERNAL_ORDER_INTENT_PIPELINE_PATCHED_AND_SMOKED_BROKER_HARD_BLOCKED_NO_ORDER`
- smoke_rc: `0`
- candidate_intent_count: `3`
- risk_accept_shadow_count: `2`
- risk_reject_shadow_count: `1`
- execution_sim_filled_count: `2`
- order_intent_recorded_count: `3`
- would_have_order_count: `2`
- real_order_sent_count: `0`
- broker_calls_executed_count: `0`

## Broker hard block

- dangerous_env_blocked: `True`
- forbidden_broker_call_names_in_new_code: `[]`
- broker_transport_block_reason: `R32D_BROKER_TRANSPORT_HARD_BLOCKED_NO_SEND`

## Safety

- orders_before: `0`
- risk_before: `0`
- execution_before: `0`
- orders_after: `0`
- risk_after: `0`
- execution_after: `0`

## Files

- module: `app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py`
- proof_script: `/home/Lenovo/scalpx/projects/mme_scalpx/bin/proof_r32d_internal_order_intent_pipeline_no_broker.py`
- ledgers: `run/audits/LANE-X-R32D-R1_REPAIR_SMOKE_INTERNAL_ORDER_INTENT_PIPELINE_NO_NEW_PATCH_NO_REPLAY_NO_ORDER_rerun_existing_r32d_patch_smoke_with_pythonpath_and_capture_untracked_files_20260611_225709/internal_ledgers`
- git_status_short: `run/audits/LANE-X-R32D-R1_REPAIR_SMOKE_INTERNAL_ORDER_INTENT_PIPELINE_NO_NEW_PATCH_NO_REPLAY_NO_ORDER_rerun_existing_r32d_patch_smoke_with_pythonpath_and_capture_untracked_files_20260611_225709/git_status_short.txt`

## Boundary

- no new source patch in R1
- no replay
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete
- no live/paper broker transport
