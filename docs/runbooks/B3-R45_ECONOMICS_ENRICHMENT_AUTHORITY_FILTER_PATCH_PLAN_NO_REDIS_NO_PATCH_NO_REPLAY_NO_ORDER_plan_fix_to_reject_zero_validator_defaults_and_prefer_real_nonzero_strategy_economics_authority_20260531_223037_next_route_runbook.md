# B3-R45_ECONOMICS_ENRICHMENT_AUTHORITY_FILTER_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER next route

If PASS:

Run:

`B3-R46_ECONOMICS_AUTHORITY_FILTER_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER`

Patch only:

`app/mme_scalpx/replay/artifacts.py`

Rules:

1. Reject zero/default/validator authority.
2. Prefer explicit non-zero strategy-family constants.
3. Preserve source labels.
4. No replay in patch batch.
5. Then rerun B3-R44-style smoke replay.
