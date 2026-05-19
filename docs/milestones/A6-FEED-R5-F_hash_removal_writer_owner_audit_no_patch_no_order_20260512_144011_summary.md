# A6-FEED-R5-F — Hash removal writer/owner audit

Generated IST: `2026-05-12T14:40:11.478475+05:30`

## Verdict

`PASS_A6_FEED_R5_F_HASH_REMOVAL_WRITER_OWNER_AUDITED_NO_PATCH_NO_ORDER`

## Root cause

`SOURCE_CONTAINS_DELETE_OR_EXPIRE_PATHS_THAT_MAY_REMOVE_CANONICAL_HASHES`

## Classification inputs

`{'all_required_absent_now': True, 'delete_hit_file_count': 7, 'write_hit_file_count': 10, 'alt_state_feed_key_count': 0, 'feeds_running': True, 'features_running': True, 'strategy_running': True, 'risk_execution_order_running': False, 'dependency_ok': True}`

## Active services

`{'feeds_running': True, 'features_running': True, 'strategy_running': True, 'risk_execution_order_running': False}`

## Required present now

`{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`

## Delete/expire hit files

`['app/mme_scalpx/core/names.py', 'app/mme_scalpx/core/redisx.py', 'app/mme_scalpx/core/settings.py', 'app/mme_scalpx/services/feeds.py', 'app/mme_scalpx/services/features.py', 'app/mme_scalpx/services/strategy.py', 'app/mme_scalpx/main.py']`

## Write hit files

`['app/mme_scalpx/core/names.py', 'app/mme_scalpx/core/redisx.py', 'app/mme_scalpx/core/settings.py', 'app/mme_scalpx/services/feeds.py', 'app/mme_scalpx/services/features.py', 'app/mme_scalpx/services/strategy.py', 'app/mme_scalpx/services/risk.py', 'app/mme_scalpx/services/execution.py', 'app/mme_scalpx/integrations/provider_runtime.py', 'app/mme_scalpx/main.py']`

## Safety

- source_patch_applied: false
- service_start_attempted: false
- service_stop_attempted: false
- hash_publish_attempted: false
- broker_order_executed: false
- order_sent: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`

## Next

`A6-FEED-R5-G delete/expire path ownership plan / no patch until approved`
