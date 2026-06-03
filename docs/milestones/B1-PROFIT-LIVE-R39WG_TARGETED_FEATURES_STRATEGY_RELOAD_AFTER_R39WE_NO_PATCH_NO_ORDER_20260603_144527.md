# B1-PROFIT-LIVE-R39WG_TARGETED_FEATURES_STRATEGY_RELOAD_AFTER_R39WE_NO_PATCH_NO_ORDER_20260603_144527

Classification: `PASS_R39WG_FEATURES_STRATEGY_RELOAD_RUNTIME_ALIAS_VISIBLE_READY_FOR_R39WA`

## Reload result
- features_old: `3067`
- features_new: `169069`
- strategy_old: `3068`
- strategy_new: `169070`
- new_process_env_ok: True
- runtime_alias_visible: True

## Safety
- orders_clean: True
- risk_clean: True
- execution_clean: True

## Next route
- If PASS: rerun R39WA to verify score/regime surfaces move.
- If alias still missing: inspect insertion call path in features.py.
- Paper remains blocked.