# B3-R34_MOVE_R32_EXPORT_CALL_BEFORE_RETURN_NO_REPLAY_NO_ORDER

Classification: `PASS_R34_R32_EXPORT_CALL_MOVED_BEFORE_RETURN_NO_REPLAY_NO_ORDER`  
Created: `2026-05-31T21:17:39.337903+05:30`

## Patch

- Target: `app/mme_scalpx/replay/artifacts.py`
- Backup: `run/_code_backups/B3-R34_MOVE_R32_EXPORT_CALL_BEFORE_RETURN_NO_REPLAY_NO_ORDER_patch_artifacts_py_move_b3_r32_analysis_export_call_before_final_return_compile_only_20260531_211739_artifacts.py.bak`
- Diff: `run/audits/B3-R34_MOVE_R32_EXPORT_CALL_BEFORE_RETURN_NO_REPLAY_NO_ORDER_patch_artifacts_py_move_b3_r32_analysis_export_call_before_final_return_compile_only_20260531_211739_patch.diff`
- Changed: `True`
- Compile OK: `True`
- AST OK: `True`

## Placement

- Before: `{'method_found': True, 'method_lineno': 682, 'method_end_lineno': 732, 'first_return_line': 727, 'first_b3_line': 732, 'placement': 'B3_CALL_AFTER_RETURN_LIKELY_UNREACHABLE', 'b3_call_lines': [{'line': 732, 'call': 'self.write_b3_r32_analysis_exports(run_context)'}], 'return_lines': [{'line': 727, 'text': 'return ReplayArtifactBundleResult('}]}`
- After: `{'method_found': True, 'method_lineno': 682, 'method_end_lineno': 733, 'first_return_line': 730, 'first_b3_line': 728, 'placement': 'B3_CALL_BEFORE_RETURN_APPARENTLY_REACHABLE', 'b3_call_lines': [{'line': 728, 'call': 'self.write_b3_r32_analysis_exports(run_context)'}], 'return_lines': [{'line': 730, 'text': 'return ReplayArtifactBundleResult('}]}`

## Safety

One-file call-placement patch only. No Redis. No replay. No service action. No broker/order/paper/live/risk/execution.

## Next

Rerun B3-R33 smoke test.
