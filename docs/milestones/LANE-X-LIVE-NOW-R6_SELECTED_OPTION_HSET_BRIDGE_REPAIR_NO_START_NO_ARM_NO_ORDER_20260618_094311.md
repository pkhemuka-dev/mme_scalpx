# Lane X R6 Selected Option HSET Bridge Repair

- timestamp: 2026-06-18T09:43:11+05:30
- mode: HSET_ONLY_NO_START_NO_ARM_NO_ORDER
- purpose: copy latest selected-option tick market fields into active selected-option hashes

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=***MASKED***
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== PROCESS SNAPSHOT BEFORE ===
=== HSET-ONLY SELECTED OPTION BRIDGE REPAIR ===
repair_rc=0
=== WAIT 10S THEN FEATURE/DECISION QUICK CHECK ===
=== PSTATUS AFTER ===
=== FINAL PROCESS SNAPSHOT ===

## R6 verdict
PASS_R6_SELECTED_OPTION_ACTIVE_HASH_HSET_BRIDGE_REPAIR_WRITTEN_NO_ORDER
- hset_results: {'state:feed:selected_option:active': '33', 'state:snapshot:mme:opt:selected:active': '33'}
- missing_after: {'state:feed:selected_option:active': [], 'state:snapshot:mme:opt:selected:active': []}
- repair_rc=0
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO
