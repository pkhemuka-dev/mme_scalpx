# LANE-X-R30C_DHAN_PROVIDER_RUNTIME_PUBLICATION_PATH_AUDIT_NO_PATCH_NO_START_NO_ORDER_locate_option_context_status_publisher_keys_names_and_pcheck_expectations_20260607_141147

classification: PASS_LANE_X_R30C_DHAN_PROVIDER_RUNTIME_PUBLICATION_PATH_AUDIT_COMPLETED_NO_PATCH_NO_START_NO_ORDER

## Safety
- redis_ok: 1
- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- risk_proc: 0
- execution_proc: 0
- safe: 1

## Publication-path counts
- source_option_context_status_count: 41
- source_option_context_provider_id_count: 55
- source_provider_runtime_count: 405
- source_dhan_count: 377
- redis_provider_key_count: 0
- redis_option_context_status_count: 0
- redis_option_context_field_count: 0
- root_hint: PROVIDER_RUNTIME_REDIS_KEY_NOT_FOUND

## Evidence files
- source grep: `run/audits/LANE-X-R30C_DHAN_PROVIDER_RUNTIME_PUBLICATION_PATH_AUDIT_NO_PATCH_NO_START_NO_ORDER_locate_option_context_status_publisher_keys_names_and_pcheck_expectations_20260607_141147_source_grep.txt`
- redis provider dump: `run/audits/LANE-X-R30C_DHAN_PROVIDER_RUNTIME_PUBLICATION_PATH_AUDIT_NO_PATCH_NO_START_NO_ORDER_locate_option_context_status_publisher_keys_names_and_pcheck_expectations_20260607_141147_redis_provider_dump.txt`
- safety: `run/audits/LANE-X-R30C_DHAN_PROVIDER_RUNTIME_PUBLICATION_PATH_AUDIT_NO_PATCH_NO_START_NO_ORDER_locate_option_context_status_publisher_keys_names_and_pcheck_expectations_20260607_141147_safety.txt`

## Interpretation

If provider runtime key exists but option_context_status field is missing, likely fix is a narrow provider-runtime publication contract patch.
If source contract lacks option_context_status, likely fix is names/model contract surface first.
If option_context_status is published as UNAVAILABLE/STALE, then inspect Dhan producer freshness/auth/session separately.

Boundary: no patch, no start, no order, no paper/live, no risk/execution, no Redis delete, no lock delete, no MISO weakening.
