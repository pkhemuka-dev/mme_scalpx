# PDASH-R2_PLAIN_LANGUAGE_BLOCKER_CONTRACT_WATCH_READONLY_NO_START_NO_ORDER_add_simple_blocker_contract_watch_panel_20260710_004016

Classification: **PASS_PDASH_R2_PLAIN_LANGUAGE_BLOCKER_CONTRACT_WATCH_READONLY_SEALED_NO_START_NO_ORDER**

## Purpose

Add a simple PDASH-only plain-language blocker and contract-watch panel.

## Scope

- Dashboard-only source patch: `app/mme_scalpx/pdash/stream_lite.py`
- No strategy/risk/execution/broker/order files touched.
- No service start.
- No paper/live enablement.
- No broker order.
- No Redis write/delete/trim.

## Gates

- compile_ok=True
- import_render_once_ok=True
- readonly_ast_issues_count=0
- env_assignment_hits=0
- sensitive_stream_delta_ok=True
- failed_gates=['NONE']

## UI added

- Trade candidates
- Active strategy/family
- Latest score
- Projected ENTER
- Last blocker in plain language
- PnL
- Position
- Orders/risk/execution/trades counts
- Safety state
- Contract-watch tokens
