# R33A3 side/symbol/runtime audit
- timestamp: 2026-06-18T13:40:02+05:30
- mode: AUDIT_ONLY_NO_START_NO_ORDER
- reason: R33A2 did not find stable green and showed side/symbol/runtime inconsistencies
=== SAFETY BEFORE ===
=== PROCESS FULL SNAPSHOT ===
=== AUDIT CURRENT + RECENT STREAMS ===
=== FINAL OBSERVE PSTATUS ===
=== FINAL PROCESS ===

## R33A3 verdict
REVIEW_R33A3_SIDE_SYMBOL_OR_ACTION_MISMATCH_NO_START_NO_ORDER
- xlen: {'decisions': 439, 'execution': 0, 'features': 2632, 'orders': 0, 'risk': 0, 'trades': 0}
- runtime_bad_count: 0
- feature_mismatch_count: 0
- decision_mismatch_count: 10
- latest_green_features_count: 5
- audit_rc=0
- runtime_started=NO
- paper_armed=NO
- order_attempted=NO
