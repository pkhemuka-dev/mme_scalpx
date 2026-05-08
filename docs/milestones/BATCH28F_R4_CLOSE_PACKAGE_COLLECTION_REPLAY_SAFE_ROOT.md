Batch 28F-R4 Close observe_only package collection with replay-safe artifact root

Date: 2026-05-01

Verdict:
PASS_OBSERVE_ONLY_MARKET_SESSION_PACKAGE_COLLECTION_28F_R4_REPLAY_SAFE_ROOT

Accepted for:
COLLECTOR_REPLAY_SAFE_ARTIFACT_ROOT_INVOCATION_FROM_FINAL_MAP

Reason:
28F-R3 invoked the collector with required CLI arguments, but passed project root as --root.
The collector treats --root as the package artifact output root and replay safety requires it to stay under run/replay.
28F-R4 reruns with:
--root /home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/live_evidence/pstrategy_20260430_094557

Final map:
path=etc/replay/parity/observe_only_actual_generated_evidence_map.json
present=true
sha256=bb54ece3138e42d0114525676ab8c9f69547ab8de92a5f7d6fad6516d4cbeb4b
shape=direct_top_level_path_map
normalized_evidence_count=12
missing_expected_keys=[]
all_evidence_paths_present=true

Artifact root:
/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/live_evidence/pstrategy_20260430_094557
artifact_root_replay_safe=true

Package result:
actual_package_collected=True
collection_deferred=False
actual_evidence_map_valid=True
written_count=6
copied_count=12

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
full_live_replay_parity=NOT_PROVEN_IN_28F_R4

Result interpretation:
This batch only closes observe_only package collection from the final 28G evidence map.
It does not approve paper_armed.
It does not approve live trading.
It does not prove replay/live parity.

Next:
Batch 28I — build replay/live parity comparison manifest from closed observe_only evidence package, still not paper/live enablement.
