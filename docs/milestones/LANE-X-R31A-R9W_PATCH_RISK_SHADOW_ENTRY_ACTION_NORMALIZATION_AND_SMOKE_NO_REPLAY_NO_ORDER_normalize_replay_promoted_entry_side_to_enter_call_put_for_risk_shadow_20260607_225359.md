# LANE-X-R31A-R9W_PATCH_RISK_SHADOW_ENTRY_ACTION_NORMALIZATION_AND_SMOKE_NO_REPLAY_NO_ORDER_normalize_replay_promoted_entry_side_to_enter_call_put_for_risk_shadow_20260607_225359

classification: PASS_R9W_RISK_SHADOW_ENTRY_ACTION_NORMALIZATION_PATCH_AND_SMOKE_NO_REPLAY_NO_ORDER

## Patch purpose

Normalize replay-promoted strategy rows from:

- `action=ENTRY`
- `side=CALL/PUT`
- `candidate=True`

into the risk-shadow expected action:

- `ENTER_CALL`
- `ENTER_PUT`

This is replay shadow action normalization only. It is not threshold tuning and not candidate forcing.

## Smoke

- smoke_classification: PASS_R9W_RISK_SHADOW_ENTRY_ACTION_NORMALIZATION_SMOKE_VISIBLE_NO_REPLAY_NO_ORDER
- next_decision: `RUN_R9X_MICRO_REPLAY_AND_INSPECT_EXECUTION_SHADOW_FILL_PNL_SURFACES`
- candidate_strategy_rows: 211
- risk_action_counts: `{'ENTER_CALL': 35, 'ENTER_PUT': 15}`
- risk_reason_counts: `{'entry_allowed': 50}`
- execution_non_hold: 50
- execution_filled: 50
- execution_reason_counts: `{'immediate_market_fill': 50}`

## Integrity

- patch_rc: 0
- pycompile_rc: 0
- smoke_rc: 0
- patch_marker_count: 1
- dirty_allowlist_pass: True
- post_allowlist_pass: True
- backup_dir: `run/_code_backups/LANE-X-R31A-R9W_PATCH_RISK_SHADOW_ENTRY_ACTION_NORMALIZATION_AND_SMOKE_NO_REPLAY_NO_ORDER_normalize_replay_promoted_entry_side_to_enter_call_put_for_risk_shadow_20260607_225359_dirty_file_backups`
- patch_diff: `run/patches/LANE-X-R31A-R9W_PATCH_RISK_SHADOW_ENTRY_ACTION_NORMALIZATION_AND_SMOKE_NO_REPLAY_NO_ORDER_normalize_replay_promoted_entry_side_to_enter_call_put_for_risk_shadow_20260607_225359_patch.diff`

## Safety

- post_safety_pass: True
- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- replay_proc: 0
- risk_proc: 0
- execution_proc: 0

## Boundary

- patch only `bin/replay_run.py`
- no replay run
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete
- no PnL claim
