# LANE-X-R31A-R9T-R3A_ALLOWLISTED_DIRTY_TREE_MUTABLEMAPPING_IMPORT_PATCH_AND_FOCUS_SMOKE_NO_REPLAY_NO_ORDER_allow_expected_dirty_lane_files_patch_only_replay_run_mutablemapping_import_verify_bridge_focus_20260607_223735

classification: FAIL_R9T_R3A_PATCH_OR_SAFETY_INTEGRITY_FAILED_NO_REPLAY_NO_ORDER

## Why R9T-R3A exists

R9T-R3 correctly aborted because the repo was already dirty. R9T-R3A allows only the known dirty lane files and patches only `bin/replay_run.py`.

## Dirty allowlist

- dirty_allowlist_pass: True
- pre_diff_names: `app/mme_scalpx/ops_dashboard/server.py app/mme_scalpx/replay/strategy_adapter.py app/mme_scalpx/services/feature_family/misb_surface.py app/mme_scalpx/services/features.py bin/replay_run.py`
- expected_diff_names: `app/mme_scalpx/ops_dashboard/server.py app/mme_scalpx/replay/strategy_adapter.py app/mme_scalpx/services/feature_family/misb_surface.py app/mme_scalpx/services/features.py bin/replay_run.py`
- post_diff_allowlist_pass: True

## Patch scope

- target: `bin/replay_run.py`
- patch: add/confirm runtime import `from collections.abc import MutableMapping`
- backup_dir: `run/_code_backups/LANE-X-R31A-R9T-R3A_ALLOWLISTED_DIRTY_TREE_MUTABLEMAPPING_IMPORT_PATCH_AND_FOCUS_SMOKE_NO_REPLAY_NO_ORDER_allow_expected_dirty_lane_files_patch_only_replay_run_mutablemapping_import_verify_bridge_focus_20260607_223735_dirty_file_backups`
- pre_diff: `run/patches/LANE-X-R31A-R9T-R3A_ALLOWLISTED_DIRTY_TREE_MUTABLEMAPPING_IMPORT_PATCH_AND_FOCUS_SMOKE_NO_REPLAY_NO_ORDER_allow_expected_dirty_lane_files_patch_only_replay_run_mutablemapping_import_verify_bridge_focus_20260607_223735_pre_existing_dirty_tree.diff`
- patch_diff: `run/patches/LANE-X-R31A-R9T-R3A_ALLOWLISTED_DIRTY_TREE_MUTABLEMAPPING_IMPORT_PATCH_AND_FOCUS_SMOKE_NO_REPLAY_NO_ORDER_allow_expected_dirty_lane_files_patch_only_replay_run_mutablemapping_import_verify_bridge_focus_20260607_223735_patch.diff`
- post_diff: `run/patches/LANE-X-R31A-R9T-R3A_ALLOWLISTED_DIRTY_TREE_MUTABLEMAPPING_IMPORT_PATCH_AND_FOCUS_SMOKE_NO_REPLAY_NO_ORDER_allow_expected_dirty_lane_files_patch_only_replay_run_mutablemapping_import_verify_bridge_focus_20260607_223735_post_patch_dirty_tree.diff`
- mutable_mapping_lines: `33:from collections.abc import MutableMapping;2172:                if isinstance(merged.get("decision_payload"), MutableMapping):`

## Safety

- hard_safety_pass: True
- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- replay_proc: 0
- risk_proc: 0
- execution_proc: 0

## Bridge focus smoke

- smoke_classification: PASS_R9T_R3A_MUTABLEMAPPING_IMPORT_PATCH_BRIDGE_FOCUS_CANDIDATE_PROMOTION_VISIBLE_NO_REPLAY_NO_ORDER
- direct_strict_total_focus: 13
- direct_misb_strict_total_focus: 13
- bridge_strict_total_focus: 39
- bridge_misb_strict_total_focus: 39
- bridge_entry_rows_focus: 13
- bridge_candidate_true_rows_focus: 13
- bridge_status_counts: `{'adapter_payload_used': 13}`
- bridge_error_counts: `{}`
- next_decision: `RUN_R9U_MICRO_REPLAY_AND_INSPECT_CANDIDATE_AUDIT_RISK_EXECUTION_SHADOW`

## Boundary

- no replay CLI main called
- no replay runner started
- no risk service started
- no execution service started
- no broker order attempted
- no Redis delete
- no lock delete
