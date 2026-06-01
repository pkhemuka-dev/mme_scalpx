# B3-R44A_ECONOMICS_ENRICHMENT_VALUE_AUTHORITY_QUALITY_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER next route

If zero/default authority is confirmed:

Do not freeze R44 as value-correct.

Recommended next:

`B3-R45_ECONOMICS_ENRICHMENT_AUTHORITY_FILTER_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER`

Goal:

- reject `min_value=0.0`, validation defaults, and model defaults as authority
- allow only explicit non-zero strategy constants/config authority
- otherwise keep fields missing with reason `authority_not_proven`
