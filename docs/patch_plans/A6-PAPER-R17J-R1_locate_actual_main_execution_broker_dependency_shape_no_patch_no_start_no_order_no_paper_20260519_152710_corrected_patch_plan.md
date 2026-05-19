# A6-PAPER-R17J-R1_locate_actual_main_execution_broker_dependency_shape_no_patch_no_start_no_order_no_paper_20260519_152710

Verdict: `PASS_A6_PAPER_R17J_R1_EXECUTION_BROKER_DEPENDENCY_SHAPE_LOCATED_NO_PATCH_NO_START_NO_ORDER_NO_PAPER`

Lane: A6-PAPER / execution bootstrap route locator only.

## Boundary
- No patch in R17J-R1.
- No service start/stop.
- No Redis mutation.
- No risk/execution start.
- No paper order.
- No broker/live/real money.

## Located shape
```json
{
  "contains_execution_broker_logic": true,
  "contains_registered_broker_phrase": true,
  "contains_runtime_error": false,
  "exact_execution_broker_strings": [
    {
      "lineno": 1,
      "value": "\napp/mme_scalpx/main.py\n\nSingle canonical bootstrap and orchestration entrypoint for ScalpX MME.\n\nFrozen contract\n---------------\nThis module OWNS:\n- process bootstrap sequencing\n- settings load\n- logging bootstrap\n- shutdown signal wiring\n- clock lifecycle bootstrap\n- Redis runtime bootstrap\n- Redis connectivity validation\n- optional consumer-group bootstrap\n- shared application context construction\n- per-service runtime context construction\n- runtime service supervision\n- single-service execution\n- lightweight doctor/status reporting\n- best-effort application shutdown\n- strict runtime service module validation (import, run(context) signature, location)\n\nThis module DOES NOT own:\n- Redis naming contracts\n- schema definitions\n- serialization\n- broker APIs\n- instrument/domain logic\n- service business logic\n- alternate bootstrap roots\n- integration worker orchestration\n- domain worker orchestration\n- service-specific builder helpers\n\nDesign contract\n---------------\n- main.py is the ONLY composition root.\n- All spine imports come from app.mme_scalpx.core.*\n- Only frozen runtime services under app.mme_scalpx.services.* are supervised here.\n- integrations/login.py is NOT a runtime supervised service.\n- domain/instruments.py is NOT a runtime supervised service.\n- ops/ is helper-only and not a second root.\n- Runtime behavior comes from settings.py and explicit dependency registration only.\n- Redis transport behavior remains owned by redisx.py.\n- Clock lifecycle remains owned by clock.py.\n- Replay mode requires an explicit replay wall-time anchor.\n- Shutdown is explicit, cooperative, and idempotent.\n- Every supervised runtime module MUST export a callable run(context).\n- Module paths must not drift to pluralized or stale names (e.g., reports.py).\n\nImportant dependency rule\n-------------------------\nfeeds.py and execution.py require external runtime dependencies that are NOT\ndefined by settings.py:\n\n- feeds.py requires:\n  - context.runtime_instruments / context.instrument_se"
    },
    {
      "lineno": 136,
      "value": "b1_execution_shadow_no_broker"
    },
    {
      "lineno": 137,
      "value": "b1_execution_shadow_no_broker"
    },
    {
      "lineno": 1094,
      "value": "\n    Enforce only proven service dependency requirements.\n\n    feeds.py requires:\n      - runtime_instruments / instrument_set\n      - at least one feed adapter surface, ideally provider-aware\n\n    execution.py requires:\n      - broker\n\n    These dependencies are not represented in settings.py, so they must be\n    explicitly registered before startup.\n    "
    },
    {
      "lineno": 155,
      "value": "b1_execution_shadow_no_broker_refuses_entry_order"
    },
    {
      "lineno": 158,
      "value": "b1_execution_shadow_no_broker_refuses_exit_order"
    },
    {
      "lineno": 164,
      "value": "b1_execution_shadow_no_broker_refuses_cancel_order"
    },
    {
      "lineno": 123,
      "value": "SCALPX_B1_EXECUTION_SHADOW_NO_BROKER"
    },
    {
      "lineno": 1140,
      "value": "execution service requires registered broker. Use register_bootstrap_dependencies(broker=...)."
    }
  ],
  "likely_patch_shape": "patch_actual__require_service_dependencies_function_around_execution_broker_branch",
  "prior_r17j_reason": "registered_broker_raise_not_found",
  "r17j_blocked_expected": true,
  "require_service_dependencies_end_lineno": 1142,
  "require_service_dependencies_found": true,
  "require_service_dependencies_lineno": 1093,
  "target_hash": "e891d29bc22b3fe6ace6744e019db175d3c8833793c7384050c84139846f4d63"
}
```

## Corrected patch direction
- Patch the actual `_require_service_dependencies` function shape found in `app/mme_scalpx/main.py`.
- Do not rely on exact old error string.
- Locate the execution/broker dependency branch structurally.
- Add report-only no-broker guard before the execution broker failure branch.
- Keep the guard fail-closed: observe-only required; real-live/broker flags forbidden; paper flags still forbidden.
- Do not touch broker_api, Dhan/Zerodha adapters, execution.py order placement, strategy, or risk.

## Required next approval
```text
I APPROVE A6 CONTROLLED-PAPER EXECUTION BOOTSTRAP ROUTE SOURCE PATCH R2 ONLY: PATCH LOCATED MAIN.PY EXECUTION BROKER DEPENDENCY SHAPE ONLY, REPORT-ONLY NO-BROKER PREFLIGHT ONLY, NO PAPER ORDER, NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```