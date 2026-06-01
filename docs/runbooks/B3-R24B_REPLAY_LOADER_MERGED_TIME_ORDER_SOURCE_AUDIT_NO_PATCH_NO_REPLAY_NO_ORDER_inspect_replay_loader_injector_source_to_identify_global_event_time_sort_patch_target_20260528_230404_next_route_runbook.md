# B3-R24B_REPLAY_LOADER_MERGED_TIME_ORDER_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER next route

Recommended next batch:

`B3-R24C_MERGED_EVENT_TIME_SORT_PATCH_NO_REPLAY_NO_ORDER`

Patch principle:

1. Do not modify broker/order/risk/execution.
2. Do not weaken `ReplayInjectorValidationError` or `_validate_event_batch`.
3. Patch only replay/offline event batch assembly.
4. Globally sort feed-stage events by parsed event_time before `injector.inject_batch`.
5. Add static/compile proof.
6. Then rerun B3-R24 as B3-R24D.

Likely patch target:

`bin/replay_run.py stage_executor event-batch assembly before injector.inject_batch`
