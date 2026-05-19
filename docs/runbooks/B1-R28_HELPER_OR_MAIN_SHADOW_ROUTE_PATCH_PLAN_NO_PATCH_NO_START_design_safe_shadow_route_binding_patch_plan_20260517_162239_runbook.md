# B1-R28 Helper Or Main Shadow Route Patch Plan

Safety: patch plan only. No source patch, no helper patch, no service start, no replay, no Redis write/delete, no broker call, no order, no paper/live, no PnL.

Classification: `PLAN_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH`

## Derived facts

- main_has_broker_gate: `True`
- main_has_register_bootstrap: `True`
- execution_has_shadow_hints: `True`
- execution_has_stream_writer: `True`
- helper_uses_services: `True`
- danger_in_helper: `True`

## Recommended option

`{'option': 'B', 'name': 'main_shadow_execution_route_binding', 'touches': ['app/mme_scalpx/main.py', 'bin/b1_observe_only_stack_start_helper.py'], 'pros': ['can preserve risk+execution lifecycle', 'binds existing shadow/no-broker seam'], 'cons': ['touches main composition root', 'requires very narrow proof'], 'risk': 'medium_high', 'recommended': True}`

## Hard guards

- Do not register a real broker.
- Do not enable paper/live.
- Do not allow broker orders.
- Do not fake risk approval.
- Do not fake execution stream rows.
- Patch must fail closed unless SCALPX_OBSERVE_ONLY=1.
- Patch must preserve existing live broker path unchanged unless explicit future approval.

Next: `B1-R29_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH_DRY_PROOF_NO_START`

Audit: `run/audits/B1-R28_HELPER_OR_MAIN_SHADOW_ROUTE_PATCH_PLAN_NO_PATCH_NO_START_design_safe_shadow_route_binding_patch_plan_20260517_162239_audit.json`
