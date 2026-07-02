# MISLS R3 Shadow Logger Surface Contract

MISLS logger should publish shadow events to one canonical surface first:

```text
research.misls.events
```

Allowed compatibility surfaces:

- direct_event
- top_level_misls_events
- top_level_misls_candidates
- research_misls_events
- metadata_misls_events
- family_surfaces_MISLS_events
- family_features_MISLS_events
- families_MISLS_events
- mixed_top_level_misls_events_call_then_put

Every full MISLS event must contain:

```text
family_id = MISLS
branch_id = CALL or PUT
final_classification = FULL_MISLS_R3_CALL_CANDIDATE or FULL_MISLS_R3_PUT_CANDIDATE
event_id nonblank
candidate_id nonblank
shadow_entry_price nonblank
shadow_entry_underlying_price nonblank
selected and paired option post quote price/qty fields
selected_option_quote_age_ms <= 250
```

Safety:

```text
Logger may write research JSONL only.
No service start.
No replay start.
No broker order.
No paper.
No risk start.
No execution start.
No Redis delete.
```