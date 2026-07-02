# LANE-X-R33A-R4_TIMEOUT_BOUNDED_THREE_DAY_BLOCKER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_finish_blocker_rank_with_timeout_grep_no_hang_20260611_235518

classification: PASS_R33A_R4_TIMEOUT_BOUNDED_THREE_DAY_BLOCKER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## File count

`733`

## Raw hit lines

`5234`

## Blocker rank

```
file_count=733
raw_hit_lines=5234

===== DAY/LANE FILE COUNTS =====
20260529     30
20260602     102
20260611     236
pseal        98
R32D         56
R32E         12
R32F         9
R32G         25
R32H         11
R32I         18
R32J         13
R32K         5
R39          363

===== BLOCKER COUNTS =====
    1316  tradability_ok
    1186  UNAVAILABLE
     813  runtime_disabled
     714  safe_to_consume
     704  hold_only
     684  provider_ready_classic
     665  data_valid
     549  FAILOVER_ACTIVE
     489  classic_runtime_disabled
     422  option_context_status
     353  snapshot_sync_valid
     346  data_quality_ok
     324  ANOMALY_CLAMPED
     247  candidate_present
     105  system_state
      81  economics_valid
      77  surface_available
      39  strict_candidate_count
      33  selected_option_status
      15  MARKETDATA_COMPOSITION_FAIL
      12  snapshot_valid
```

## Next fix order

Patch only the top repeated blocker first.

Expected order:
1. provider/context readiness
2. selected option failover/context unavailable
3. snapshot sync/validity
4. tradability/data_valid/safe_to_consume
5. MIV-R frequent candidates
6. shadow PnL percentage
