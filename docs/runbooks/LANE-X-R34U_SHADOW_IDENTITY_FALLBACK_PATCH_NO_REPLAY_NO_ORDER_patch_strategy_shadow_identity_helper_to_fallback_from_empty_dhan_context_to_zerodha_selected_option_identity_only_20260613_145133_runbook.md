# LANE-X-R34U_SHADOW_IDENTITY_FALLBACK_PATCH_NO_REPLAY_NO_ORDER_patch_strategy_shadow_identity_helper_to_fallback_from_empty_dhan_context_to_zerodha_selected_option_identity_only_20260613_145133

classification: REVIEW_R34U_PATCH_OR_SMOKE_OR_SAFETY_NOT_CLEAN_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R34U_SHADOW_IDENTITY_FALLBACK_PATCH_NO_REPLAY_NO_ORDER_patch_strategy_shadow_identity_helper_to_fallback_from_empty_dhan_context_to_zerodha_selected_option_identity_only_20260613_145133.json`
audit: `run/audits/LANE-X-R34U_SHADOW_IDENTITY_FALLBACK_PATCH_NO_REPLAY_NO_ORDER_patch_strategy_shadow_identity_helper_to_fallback_from_empty_dhan_context_to_zerodha_selected_option_identity_only_20260613_145133`

## Safety
- compile_pre_rc: 0
- patch_rc: 2
- compile_post_rc: 0
- smoke_rc: 0
- orders pre/post: 0 / 0
- risk pre/post: 0 / 0
- execution pre/post: 0 / 0
- risk/execution proc post: 0 / 0

## Scope
- patched file: app/mme_scalpx/services/strategy.py
- patch scope: strategy shadow identity fallback only
- no replay
- no service start
- no paper/live
- no broker/order
- no top-level action promotion

## Markers

## Static smoke
{"candidate_action_shadow": "ENTER_CALL", "candidate_instrument_token_shadow": "123456", "candidate_symbol_shadow": "NIFTY26JUN25000CE", "fallback_source": null, "instrument_token": "123456", "symbol": "NIFTY26JUN25000CE", "top_level_action": null}

## Compile post
