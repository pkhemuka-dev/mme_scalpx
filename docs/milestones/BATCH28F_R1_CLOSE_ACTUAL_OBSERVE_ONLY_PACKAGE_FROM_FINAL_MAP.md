Batch 28F-R1 Close actual observe_only market-session package collection from final map

Date: 2026-05-01

Verdict:
FAIL_OBSERVE_ONLY_MARKET_SESSION_PACKAGE_COLLECTION_28F_R1_FROM_FINAL_MAP

Accepted for:
RERUN_28F_PACKAGE_COLLECTION_FROM_GENERATED_FINAL_MAP

Source final evidence map:
etc/replay/parity/observe_only_actual_generated_evidence_map.json

Final map:
present=true
sha256=bb54ece3138e42d0114525676ab8c9f69547ab8de92a5f7d6fad6516d4cbeb4b
evidence_count=0
all_evidence_paths_present=false

Executed:
- bin/proof_observe_only_actual_evidence_map_collection_contract.py
- bin/proof_observe_only_actual_evidence_map_collection_no_enablement.py
- bin/observe_only_market_session_package_collect.py

Safety:
starts_services=false
reads_live_redis=false
writes_live_redis=false
calls_broker_api=false
paper_armed_approved=false
live_trading_approved=false
execution_arming_created=false
real_order_sent=false
production_doctrine_changed=false
full_live_replay_parity=NOT_PROVEN_IN_28F_R1

Result interpretation:
This batch only closes the actual observe_only evidence package collection path from the final 28G map.
It does not approve paper_armed.
It does not approve live trading.
It does not prove replay/live parity.

Next:
Inspect compile/static/preflight/run failure and write narrow repair batch.
