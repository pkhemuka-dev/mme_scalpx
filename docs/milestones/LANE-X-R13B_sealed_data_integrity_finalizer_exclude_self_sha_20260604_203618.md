# LANE-X-R13B_sealed_data_integrity_finalizer_exclude_self_sha_20260604_203618

classification: PASS_LANE_X_R13B_SEALED_DATA_INTEGRITY_FINALIZED_PRIMARY_R3_VALID_R4_SUPPLEMENTAL_SHA_SELF_ISSUE_CLOSED

R13 review was caused by R4 SHA256SUMS self-reference / manifest-check issue, not by gzip corruption or stream-summary mismatch.

## Final evidence interpretation

- R3 remains primary live-market pseal.
- R4 remains supplemental post-market export.
- R4 no-live-tick status is expected because it was run after market/runtime stopped.
- R4 excluding-self SHA verification rc: 0

## Key counts

- R3 fut_zerodha xlen: 567
- R3 opt_selected_zerodha xlen: 2819
- R3 features xlen: 246
- R3 decisions xlen: 1753
- R4 fut_zerodha xlen: 0
- R4 opt_selected_zerodha xlen: 0
- R4 features xlen: 4220
- R4 decisions xlen: 1682

No patch, no replay, no delete, no paper/order action was attempted.
