Batch 28F-R2 Shape-aware close of actual observe_only market-session package collection from final map

Date: 2026-05-01

Verdict:
FAIL_OBSERVE_ONLY_MARKET_SESSION_PACKAGE_COLLECTION_28F_R2_SHAPE_AWARE_FROM_FINAL_MAP

Accepted for:
SHAPE_AWARE_RERUN_28F_PACKAGE_COLLECTION_FROM_GENERATED_FINAL_MAP

Reason:
Batch 28F-R1 failed before running the collector because its wrapper interpreted the final map as having zero evidence entries.
28F-R2 treats the generated final map as shape-aware:
- nested evidence map if present
- otherwise direct top-level project-path evidence map

Final map:
path=etc/replay/parity/observe_only_actual_generated_evidence_map.json
present=true
sha256=bb54ece3138e42d0114525676ab8c9f69547ab8de92a5f7d6fad6516d4cbeb4b
shape=direct_top_level_path_map
normalized_evidence_count=12
missing_expected_keys=[]
all_evidence_paths_present=true

Executed when preflight passed:
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
full_live_replay_parity=NOT_PROVEN_IN_28F_R2

Result interpretation:
This batch only closes observe_only package collection from the final 28G evidence map.
It does not approve paper_armed.
It does not approve live trading.
It does not prove replay/live parity.

Next:
Inspect driver proof, shape report, and collector outputs; write narrow repair only.
