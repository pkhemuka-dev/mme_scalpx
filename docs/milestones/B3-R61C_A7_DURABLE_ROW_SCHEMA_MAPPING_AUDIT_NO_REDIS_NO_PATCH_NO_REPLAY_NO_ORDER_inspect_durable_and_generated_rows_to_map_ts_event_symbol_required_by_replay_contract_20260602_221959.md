# B3-R61C_A7_DURABLE_ROW_SCHEMA_MAPPING_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R61C_SCHEMA_GAP_CONFIRMED_TS_EVENT_SYMBOL_MAPPING_REQUIRED`

R61B failed because replay contract requires `ts_event` and `symbol`.

Generated contract gap: `{"fut_ticks": ["ts_event", "symbol"], "opt_ticks": ["ts_event", "symbol"]}`

No Redis, no replay, no patch, no broker/order/paper/live/risk/execution.
