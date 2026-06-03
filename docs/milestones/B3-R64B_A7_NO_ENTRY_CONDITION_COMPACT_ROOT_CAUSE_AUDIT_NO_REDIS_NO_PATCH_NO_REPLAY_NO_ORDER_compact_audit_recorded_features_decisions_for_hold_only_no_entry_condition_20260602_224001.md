# B3-R64B_A7_NO_ENTRY_CONDITION_COMPACT_ROOT_CAUSE_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R64_A7_NO_ENTRY_ROOT_CAUSE_AUDITED_FEATURE_GATES_BLOCKED_CANDIDATES_NO_PATCH`

Primary root cause:

[
  "consumer_view data_valid=false",
  "stage_flags data_quality_ok=false",
  "stage_flags snapshot_sync_valid=false",
  "stage_flags tradability_ok=false",
  "provider_ready_classic=false even though selected-option failover may be active"
]

Secondary:

[
  "Dhan option_context_status=UNAVAILABLE; MISO remains blocked by design"
]

Evidence:

{
  "action": {
    "HOLD": 3000
  },
  "data_quality_ok": {
    "False": 8147
  },
  "data_valid": {
    "False": 8147
  },
  "decision_reason": {
    "hold_only_family_features_consumer_bridge": 3000
  },
  "failover_active": {
    "True": 8147
  },
  "hold_only": {
    "True": 8147
  },
  "option_context_status": {
    "UNAVAILABLE": 8147
  },
  "provider_ready_classic": {
    "False": 8147
  },
  "safe_to_consume": {
    "False": 8147
  },
  "selected_option_status": {
    "FAILOVER_ACTIVE": 8147
  },
  "snapshot_sync_valid": {
    "False": 8147
  },
  "tradability_ok": {
    "False": 8147
  }
}

No Redis, no replay, no patch, no broker/order/paper/live/risk/execution.
