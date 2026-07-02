# LANE-X-R31A-R9T-R3B_SEAL_MUTABLEMAPPING_PATCH_SHORTPATH_VERIFY_NO_PATCH_NO_REPLAY_NO_ORDER_verify_compile_import_bridge_focus_after_r3a_20260607_223909

classification: PASS_R9T_R3B_PATCH_SEALED_SHORTPATH_VERIFY_NO_PATCH_NO_REPLAY_NO_ORDER

## What this seals

R9T-R3A already patched `bin/replay_run.py` and the bridge focus smoke passed, but its final classification failed because the py_compile output filename was too long. R9T-R3B does no patching and uses short artifact paths.

## Verification

- compile_pass: True
- pycompile_rc: 0
- import_pass: True
- mutable_lines: `33:from collections.abc import MutableMapping;2172:                if isinstance(merged.get("decision_payload"), MutableMapping):`
- dirty_allowlist_pass: True
- smoke_classification: PASS_R9T_R3B_PATCH_SEALED_COMPILE_AND_BRIDGE_FOCUS_PROMOTION_VISIBLE_NO_PATCH_NO_REPLAY_NO_ORDER
- direct_strict_total_focus: 13
- bridge_strict_total_focus: 39
- bridge_entry_rows_focus: 13
- bridge_candidate_true_rows_focus: 13
- bridge_status_counts: `{'adapter_payload_used': 13}`
- bridge_error_counts: `{}`

## Safety

- safety_pass: True
- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- replay_proc: 0
- risk_proc: 0
- execution_proc: 0

## Next decision

`RUN_R9U_MICRO_REPLAY_AND_INSPECT_CANDIDATE_AUDIT_RISK_EXECUTION_SHADOW`

## Boundary

- no patch
- no replay runner
- no risk service
- no execution service
- no broker order
- no Redis delete
- no lock delete
