# R38QT_R29A_AFTERMARKET_SELECTOR_STATE_CONTRACT_AND_SHADOW_FIELDS_PATCH_DRY_PLAN_NO_PATCH_NO_ORDER_20260708_154611

## Purpose
Dry plan only. No source patch, no restart, no Redis write, no broker/order.

R28 OK: True

## Selector state contract
- selector_key_shadow: string
- selector_family_shadow: string
- selector_action_shadow: string
- selector_symbol_shadow: string
- selector_token_shadow: string
- selector_stable_for_sec_shadow: float
- selector_sample_count_shadow: int
- selector_switch_count_60s_shadow: int
- selector_cooldown_active_shadow: bool
- entry_allowed_shadow: bool
- entry_block_reason_shadow: string
- entry_policy_version_shadow: R29A_SELECTOR_STABILITY_V1

## Initial gate values
- min_persistence_sec: 10
- min_samples: 3
- max_switches_per_60s: 6
- cooldown_after_switch_sec: 20
- allowed_action_initial: ENTER_PUT_ONLY

## Proposed owner map
### app/mme_scalpx/services/strategy_family/activation.py
- Role: Pure selector evidence helper if suitable.
- Future patch type: add pure helper or small dataclass; no broker/order side effects
### app/mme_scalpx/services/strategy.py
- Role: Attach selector shadow fields to emitted decision payload.
- Future patch type: shadow-field projection only; keep hold_only/report_only behavior
### app/mme_scalpx/core/models.py
- Role: Only if existing decision model requires explicit schema extension.
- Future patch type: schema-compatible optional fields only
### app/mme_scalpx/core/names.py
- Role: Only if stream/key constants are needed.
- Future patch type: constant-only, no behavior

## Future patch acceptance gates
- No broker/order/risk/execution code path touched.
- Decision stream still hold/report/shadow only.
- New selector fields present in emitted decisions.
- compileall PASS.
- import PASS for modified modules.
- Redis safety streams remain zero during proof.
- Replay/captured-data simulation can read selector fields.

## Next batch
R38QT_R29B_SELECTOR_STATE_CONTRACT_SHADOW_FIELDS_MICRO_PATCH_IF_APPROVED

## Final verdict
PASS_R38QT_R29A_SELECTOR_STATE_CONTRACT_DRY_PLAN_CREATED_NO_PATCH_NO_ORDER
