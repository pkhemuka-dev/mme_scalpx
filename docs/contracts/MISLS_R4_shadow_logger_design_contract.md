# MISLS R4 Shadow Logger Design Contract

## Canonical in-memory surface

```text
research.misls.events
```

## Research JSONL outputs

- run/research/misls_r3/events_YYYYMMDD.jsonl
- run/research/misls_r3/candidates_YYYYMMDD.jsonl
- run/research/misls_r3/rejections_YYYYMMDD.jsonl
- run/research/misls_r3/forward_paths_YYYYMMDD.jsonl

## Minimum full-candidate fields

- family_id
- branch_id
- side
- final_classification
- event_id
- candidate_id
- shadow_entry_price
- shadow_entry_underlying_price
- selected_option_bid_post
- selected_option_ask_post
- selected_option_bid_qty_post
- selected_option_ask_qty_post
- selected_option_quote_age_ms
- paired_option_bid_post
- paired_option_ask_post
- paired_option_bid_qty_post
- paired_option_ask_qty_post
- score

## Forbidden actions

- broker order
- paper order
- risk stream emit
- execution stream emit
- Redis delete
- lock delete
- service start
- replay start
- registry wiring
- FAMILY_ORDER change
