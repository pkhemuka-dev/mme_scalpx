# B1-PROFIT-LIVE-R39WL_DYNAMIC_DERIVATION_INSERTION_SITE_AUDIT_NO_PATCH_NO_START_NO_ORDER_ast_find_valid_family_frames_local_scope_r39we_call_sites_exclude_module_scope_20260603_152524

Classification: `PASS_R39WL_VALID_LOCAL_R39WE_CALL_SITES_FOUND_PATCH_READY_NO_PATCH`

## Summary
- total_r39we_call_sites: 5
- valid_site_count: 5
- invalid_site_count: 0
- module_level_count: 0

## Valid insertion lines
- line 4191 in `publish_payload`: `family_frames = _b1_profit_live_r39we_apply_dynamic_score_aliases(family_frames)`
- line 7402 in `_batch26o17a_run_once`: `family_frames = _b1_profit_live_r39we_apply_dynamic_score_aliases(family_frames)`
- line 7592 in `_batch26o17b_run_once`: `family_frames = _b1_profit_live_r39we_apply_dynamic_score_aliases(family_frames)`
- line 6958 in `_batch26o16g_r2_run_once`: `family_frames = _b1_profit_live_r39we_apply_dynamic_score_aliases(family_frames)`
- line 7240 in `_batch26o16h_r2_run_once`: `family_frames = _b1_profit_live_r39we_apply_dynamic_score_aliases(family_frames)`

## Invalid insertion lines

## Patch plan
```json
{
  "exclude": [
    "module scope",
    "helper function bodies",
    "source strings",
    "any line where nearest function is None",
    "any function where family_frames was not assigned before call line"
  ],
  "invalid_line_numbers": [],
  "next_patch": "R39WM",
  "rule": "insert R39WK call only before R39WE calls inside functions where family_frames is assigned earlier in the same function",
  "target": "app/mme_scalpx/services/features.py",
  "valid_line_numbers": [
    4191,
    7402,
    7592,
    6958,
    7240
  ]
}
```

## Context files
- `run/audits/B1-PROFIT-LIVE-R39WL_DYNAMIC_DERIVATION_INSERTION_SITE_AUDIT_NO_PATCH_NO_START_NO_ORDER_ast_find_valid_family_frames_local_scope_r39we_call_sites_exclude_module_scope_20260603_152524_raw/r39we_call_sites.json`
- `run/audits/B1-PROFIT-LIVE-R39WL_DYNAMIC_DERIVATION_INSERTION_SITE_AUDIT_NO_PATCH_NO_START_NO_ORDER_ast_find_valid_family_frames_local_scope_r39we_call_sites_exclude_module_scope_20260603_152524_raw/r39we_call_contexts.txt`

## Next route
- If PASS: apply R39WM with AST-local insertion only.
- No reload until patch compile/import/self-test passes.
- Paper remains blocked.