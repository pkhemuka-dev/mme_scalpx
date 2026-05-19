# A6-FEED-R5I_read_only_extract_broad_process_and_redis_client_owner_for_active_feeds_lock_no_clear_no_restart_no_order_no_paper_20260513_151255

Batch: A6-FEED-R5I

Purpose: read_only_extract_broad_process_and_redis_client_owner_for_active_feeds_lock_no_clear_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5I_OWNER_EVIDENCE_EXTRACTED_NO_CLEAR_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only owner extraction only; no lock clear/delete, no service start/restart/stop, no patch, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "broad_owner_candidate_count": 2,
  "broad_owner_candidates": [
    "44118 1 Ssl 08:07 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main",
    "44118 1 Ssl 08:18 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main"
  ],
  "feed_stream_growth_during_probe": true,
  "likely_condition": "BROAD_PROCESS_SCAN_FOUND_FEED_OR_STACK_OWNER_CANDIDATE_DO_NOT_CLEAR_LOCK",
  "lock_post": {
    "key": "lock:feeds",
    "ttl_info": {
      "pttl": "20315",
      "ttl": "20"
    },
    "type": "string",
    "value_sample_redacted": "feeds:mme-scalpx:44118"
  },
  "lock_pre": {
    "key": "lock:feeds",
    "ttl_info": {
      "pttl": "20098",
      "ttl": "20"
    },
    "type": "string",
    "value_sample_redacted": "feeds:mme-scalpx:44118"
  },
  "next_action": "Inspect owner candidate; if valid, run read-only readiness consolidation without lock clear.",
  "r5h_final_verdict": "PASS_A6_FEED_R5H_REAPPEARED_LOCK_OWNER_INSPECTION_CAPTURED_NO_CLEAR_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5h_likely_condition": "LOCK_PRESENT_AND_FEED_STREAMS_GROWING_BUT_STANDARD_FEEDS_PROCESS_NOT_VISIBLE",
  "r5h_next_action": "Inspect broad process/client owner evidence before any second lock clear or restart.",
  "r5h_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5H_read_only_inspect_reappeared_feeds_lock_with_stream_growth_no_clear_no_restart_no_order_no_paper_20260513_151115.json",
  "redis_client_candidate_count": 18,
  "redis_client_candidates": [
    "id=15021 addr=127.0.0.1:52816 fd=13 name=scalpx-mme age=480 idle=2 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=20648 events=r cmd=xadd user=default",
    "id=15022 addr=127.0.0.1:52824 fd=14 name=scalpx-mme age=480 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=20504 events=r cmd=hgetall user=default",
    "id=15016 addr=127.0.0.1:52766 fd=8 name=scalpx-mme age=480 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=20504 events=r cmd=hgetall user=default",
    "id=15017 addr=127.0.0.1:52780 fd=9 name=scalpx-mme age=480 idle=480 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=20536 events=r cmd=xgroup user=default",
    "id=15023 addr=127.0.0.1:52838 fd=15 name=scalpx-mme age=479 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=32768 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=61520 events=r cmd=hset user=default",
    "id=15018 addr=127.0.0.1:52784 fd=10 name=scalpx-mme age=480 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=32768 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=61456 events=r cmd=hgetall user=default",
    "id=15019 addr=127.0.0.1:52800 fd=11 name=scalpx-mme age=480 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=20584 events=r cmd=xreadgroup user=default",
    "id=15020 addr=127.0.0.1:52804 fd=12 name=scalpx-mme age=480 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=5 omem=44040312 tot-mem=44060848 events=rw cmd=xrange user=default",
    "id=15396 addr=127.0.0.1:54844 fd=16 name= age=0 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=26 qbuf-free=32742 argv-mem=10 obl=0 oll=0 omem=0 tot-mem=61466 events=r cmd=client user=default",
    "id=15019 addr=127.0.0.1:52800 fd=11 name=scalpx-mme age=493 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=201 omem=1680892632 tot-mem=1680913168 events=rw cmd=xrange user=default",
    "id=15020 addr=127.0.0.1:52804 fd=12 name=scalpx-mme age=493 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=3998124 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=4215104 events=r cmd=hset user=default",
    "id=15021 addr=127.0.0.1:52816 fd=13 name=scalpx-mme age=493 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=32768 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=61600 events=r cmd=xadd user=default",
    "id=15022 addr=127.0.0.1:52824 fd=14 name=scalpx-mme age=493 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=32768 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=61456 events=r cmd=hgetall user=default",
    "id=15016 addr=127.0.0.1:52766 fd=8 name=scalpx-mme age=493 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=32768 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=61456 events=r cmd=hgetall user=default",
    "id=15017 addr=127.0.0.1:52780 fd=9 name=scalpx-mme age=493 idle=493 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=20536 events=r cmd=xgroup user=default",
    "id=15023 addr=127.0.0.1:52838 fd=15 name=scalpx-mme age=492 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=30633 qbuf-free=2135 argv-mem=127 obl=0 oll=0 omem=0 tot-mem=62847 events=r cmd=hgetall user=default",
    "id=15018 addr=127.0.0.1:52784 fd=10 name=scalpx-mme age=493 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=0 argv-mem=0 obl=0 oll=0 omem=0 tot-mem=20584 events=r cmd=xreadgroup user=default",
    "id=15437 addr=127.0.0.1:36716 fd=16 name= age=0 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=26 qbuf-free=32742 argv-mem=10 obl=0 oll=0 omem=0 tot-mem=61466 events=r cmd=client user=default"
  ],
  "standard_services_post": [],
  "standard_services_pre": []
}
```

Required checks:

```json
{
  "checked_sources_unchanged_by_batch": true,
  "latest_r5h_proof_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_redis_write": true,
  "no_risk_execution_order_process_visible_post": true,
  "no_risk_execution_order_process_visible_pre": true,
  "no_service_start_restart_stop": true,
  "no_source_patch": true,
  "orders_mme_stream_zero_or_absent_post": true,
  "orders_mme_stream_zero_or_absent_pre": true,
  "position_flat_post": true,
  "position_flat_pre": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5I_read_only_extract_broad_process_and_redis_client_owner_for_active_feeds_lock_no_clear_no_restart_no_order_no_paper_20260513_151255.json
