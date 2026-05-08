Batch 28F-R3 Close observe_only package collection with required collector arguments

Date: 2026-05-01

Verdict:
FAIL_OBSERVE_ONLY_PACKAGE_COLLECTION_28F_R3_WITH_REQUIRED_ARGS

Accepted for:
COLLECTOR_REQUIRED_ARGUMENT_INVOCATION_FROM_FINAL_MAP

Reason:
28F-R2 proved the final evidence map shape and all 12 evidence paths, but the actual collector was invoked without required CLI arguments.
28F-R3 reruns the collector with:
--capture-id pstrategy_20260430_094557
--evidence-map etc/replay/parity/observe_only_actual_generated_evidence_map.json
--root /home/Lenovo/scalpx/projects/mme_scalpx

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
- bin/observe_only_market_session_package_collect.py --capture-id pstrategy_20260430_094557 --evidence-map /home/Lenovo/scalpx/projects/mme_scalpx/etc/replay/parity/observe_only_actual_generated_evidence_map.json --root /home/Lenovo/scalpx/projects/mme_scalpx

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
full_live_replay_parity=NOT_PROVEN_IN_28F_R3

Result interpretation:
This batch only closes observe_only package collection from the final 28G evidence map.
It does not approve paper_armed.
It does not approve live trading.
It does not prove replay/live parity.

Next:
Inspect collector stderr/stdout and write narrow collector invocation/schema repair only.
