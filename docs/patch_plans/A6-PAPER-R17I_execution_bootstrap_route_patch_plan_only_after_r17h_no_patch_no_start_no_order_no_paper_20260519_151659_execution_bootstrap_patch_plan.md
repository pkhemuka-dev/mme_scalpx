# A6-PAPER-R17I_execution_bootstrap_route_patch_plan_only_after_r17h_no_patch_no_start_no_order_no_paper_20260519_151659

Verdict: `PASS_A6_PAPER_R17I_EXECUTION_BOOTSTRAP_ROUTE_PATCH_PLAN_CREATED_NO_PATCH_NO_START_NO_ORDER_NO_PAPER`

Lane: A6-PAPER / execution bootstrap route patch-plan only.

## Boundary
- No source patch in R17I.
- No service start/stop.
- No Redis mutation.
- No risk/execution start.
- No paper order.
- No broker/live/real money.
- orders:mme:stream must remain 0.
- position must remain FLAT.

## R17H diagnosis consumed
```json
{
  "controlled_paper_route_exists": true,
  "execution_has_broker_hits": true,
  "likely_root_cause": "execution_service_bootstrap_requires_real_registered_broker_even_for_controlled_paper_preflight",
  "main_has_broker_bootstrap_hits": true,
  "paper_trial_status": "blocked_until_execution_bootstrap_route_defined",
  "r17g_execution_failed_registered_broker": true,
  "r17g_verdict": "PASS_A6_PAPER_R17G_RUNTIME_ARMING_PREFLIGHT_RETRY_RISK_EXECUTION_START_STOP_NO_ORDER_NO_PAPER",
  "source_contains_registered_broker_error": true
}
```

## Chosen patch design
```json
{
  "chosen_design": "execution_report_only_preflight_mode_first",
  "controlled_paper_route_target": "app/mme_scalpx/services/controlled_paper_route.py only for gate reuse; do not weaken existing gates",
  "expected_source_patch_shape": [
    "Add a small report-only execution dependency/adapter or bootstrap branch with explicit marker.",
    "Do not modify broker_api real submit/place/cancel methods.",
    "Do not modify Dhan/Zerodha adapters.",
    "Do not modify strategy or risk rules.",
    "Prefer minimal main.py composition-root patch if the missing broker check is in main.py.",
    "Add proof-only import tests for observe/report-only no-broker bootstrap and real-live flag fail-closed cases."
  ],
  "fail_closed_rules": [
    "If SCALPX_ALLOW_BROKER_ORDERS, SCALPX_REAL_LIVE_ALLOWED, SCALPX_ALLOW_REAL_LIVE, or SCALPX_ENABLE_LIVE is present, execution bootstrap must fail closed.",
    "If observe-only is not set, report-only brokerless execution mode must fail closed.",
    "If order stream is non-zero before bootstrap, fail closed.",
    "If state:position:mme is not FLAT before bootstrap, fail closed.",
    "If risk/execution lock is already held unexpectedly, fail closed.",
    "Any order intent in this mode must be reported/refused, not submitted."
  ],
  "paper_order_remains_blocked": true,
  "patch_goal": [
    "Allow execution service to start in observe/report-only controlled-paper preflight mode without registered real broker.",
    "The route must refuse all actual order placement.",
    "The route must never call Dhan/Zerodha/broker_api real adapter.",
    "The route must be allowed only when SCALPX_OBSERVE_ONLY=1 and all real broker/live flags are unset.",
    "The route is only for R17 arming-preflight readiness; it is not approval for one-lot paper order."
  ],
  "primary_patch_target": "app/mme_scalpx/main.py",
  "required_after_patch_chain": [
    "R17J source patch only.",
    "R17K static proof only: compile, AST audit, import matrix, no broker/order fragments in patch region.",
    "R17L no-start safety proof only.",
    "R17M runtime arming preflight retry only.",
    "Only after R17M PASS may one-lot paper trial runbook be considered."
  ],
  "secondary_patch_target": "app/mme_scalpx/services/execution.py only if main.py cannot inject a report-only broker/backend seam cleanly",
  "why_not_one_lot_paper_yet": "A paper order backend is a higher-risk step. First prove execution can bootstrap without a real broker only in explicit report-only/observe-only mode and still refuse all order placement."
}
```

## Source scan summary
```json
{
  "app/mme_scalpx/core/models.py": {
    "class_count": 11,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 1567,
        "lineno": 1505,
        "name": "validate"
      },
      {
        "end_lineno": 1601,
        "lineno": 1569,
        "name": "to_execution_metadata"
      },
      {
        "end_lineno": 1633,
        "lineno": 1603,
        "name": "to_strategy_decision_payload"
      },
      {
        "end_lineno": 1683,
        "lineno": 1660,
        "name": "validate"
      },
      {
        "end_lineno": 1775,
        "lineno": 1759,
        "name": "validate"
      },
      {
        "end_lineno": 1811,
        "lineno": 1795,
        "name": "validate"
      },
      {
        "end_lineno": 2359,
        "lineno": 2343,
        "name": "validate"
      },
      {
        "end_lineno": 2414,
        "lineno": 2387,
        "name": "validate"
      },
      {
        "end_lineno": 2587,
        "lineno": 2537,
        "name": "validate"
      },
      {
        "end_lineno": 2666,
        "lineno": 2616,
        "name": "validate"
      },
      {
        "end_lineno": 2822,
        "lineno": 2777,
        "name": "validate"
      },
      {
        "end_lineno": 2849,
        "lineno": 2837,
        "name": "validate"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 1350,
        "value": "Provider/broker equivalence reference for one tradable option instrument."
      },
      {
        "lineno": 1462,
        "value": "Strict promoted family order-intent bridge before StrategyDecision publish.\n\n    This model is intentionally stricter than StrategyDecision. StrategyDecision\n    remains the broad transport payload; StrategyOrderIntent is the promoted\n    entry-only contract that must have execution-critical option fields.\n    "
      },
      {
        "lineno": 2503,
        "value": "\n    Canonical flat position truth.\n\n    This is the single shared position-state contract to be used by:\n    - execution hash writes\n    - strategy position reads\n    - monitor reads\n    - report reconstruction assistance\n    "
      },
      {
        "lineno": 2614,
        "value": "execution_state"
      },
      {
        "lineno": 3061,
        "value": "ALLOWED_EXECUTION_MODES"
      },
      {
        "lineno": 3089,
        "value": "ExecutionState"
      },
      {
        "lineno": 3104,
        "value": "MODEL_CONTRACT_EXECUTION_ENTRY_TOP_LEVEL_KEYS"
      },
      {
        "lineno": 3105,
        "value": "MODEL_CONTRACT_EXECUTION_ENTRY_METADATA_KEYS"
      }
    ],
    "function_count": 12,
    "line_hit_count": 79,
    "parse_ok": true,
    "sha256": "fe2fb4ac45b290069067179336778c8f15046d0e95a78db8d49162a8a6845144",
    "string_hit_count": 35
  },
  "app/mme_scalpx/core/names.py": {
    "class_count": 5,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 676,
        "lineno": 636,
        "name": "validate_contract_field_registry"
      },
      {
        "end_lineno": 2518,
        "lineno": 2231,
        "name": "validate_names_contract"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 3,
        "value": "\napp/mme_scalpx/core/names.py\n\nCanonical contract names and symbolic constants for ScalpX MME.\n\nPurpose\n-------\nSingle source of truth for:\n- Redis stream names\n- Redis latest-state hash names\n- heartbeat / health keys\n- process-safety lock keys\n- notify channel names\n- consumer-group names\n- replay namespace derivation\n- service identity registry and bootstrap order\n- contract-level symbolic constants\n- ownership registries\n- additive observability publisher registries\n- bootstrap consumer-group specs\n- event type constants\n- grouped live/replay bundles\n- compatibility aliases required during integration freeze\n\nOwnership\n---------\nThis module OWNS:\n- canonical Redis names\n- replay-name derivation rules\n- service identity constants and service registry\n- consumer-group names\n- contract constants such as commands / actions / sides / modes / ack types\n- ownership registries\n- additive-publisher registries where a stream has one primary semantic owner\n  but multiple allowed additive publishers\n- stream bootstrap group specs\n- event symbolic names\n- common defaults used across transport callers\n- compatibility aliases for legacy/generic symbol names\n\nThis module DOES NOT own:\n- runtime settings / environment parsing\n- Redis client lifecycle\n- serialization behavior\n- payload / state schemas\n- trading logic\n- broker symbols\n- holiday calendars\n\nCore contract rules\n-------------------\n- Streams are event/history transport.\n- Hashes / scalar keys are latest state / control / liveness.\n- No raw Redis names should be hardcoded elsewhere.\n- Replay names must remain namespace-isolate"
      },
      {
        "lineno": 190,
        "value": "execution"
      },
      {
        "lineno": 324,
        "value": "execution_primary"
      },
      {
        "lineno": 325,
        "value": "execution_fallback"
      },
      {
        "lineno": 784,
        "value": "state:execution"
      },
      {
        "lineno": 918,
        "value": "health:execution"
      },
      {
        "lineno": 936,
        "value": "health:zerodha:execution"
      },
      {
        "lineno": 939,
        "value": "health:dhan:execution"
      }
    ],
    "function_count": 2,
    "line_hit_count": 120,
    "parse_ok": true,
    "sha256": "2f0c3b11b6e8b883a4ea49c131bd4a435a78d4c84b51c6a5d128134d029d7d4a",
    "string_hit_count": 56
  },
  "app/mme_scalpx/core/settings.py": {
    "class_count": 2,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 440,
        "lineno": 429,
        "name": "validate_runtime_mode_input_snapshot"
      },
      {
        "end_lineno": 1134,
        "lineno": 1114,
        "name": "build_execution_settings"
      },
      {
        "end_lineno": 1184,
        "lineno": 1137,
        "name": "validate_settings"
      },
      {
        "end_lineno": 1241,
        "lineno": 1187,
        "name": "build_settings"
      },
      {
        "end_lineno": 703,
        "lineno": 690,
        "name": "__post_init__"
      },
      {
        "end_lineno": 775,
        "lineno": 744,
        "name": "to_safe_dict"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 1,
        "value": "\napp/mme_scalpx/core/settings.py\n\nCanonical runtime settings for ScalpX MME.\n\nPurpose\n-------\nSingle source of truth for:\n- environment loading\n- typed runtime configuration\n- Redis connection and transport settings\n- logging settings\n- replay/live runtime settings\n- fail-fast startup validation policy\n- centralized service/runtime thresholds\n- bootstrap-safe validated settings access\n\nOwnership\n---------\nThis module OWNS:\n- configuration schema\n- environment parsing\n- validation of runtime configuration\n- process-wide cached settings access\n- safe redaction helpers for sensitive fields\n- bootstrap logging setup\n\nThis module DOES NOT own:\n- Redis names / contracts\n- Redis client lifecycle\n- clock implementation\n- payload schemas / serialization\n- trading logic\n- broker APIs\n- market calendars\n- service transport ownership\n\nCore design rules\n-----------------\n- One canonical settings object per process.\n- All callers must use get_settings().\n- No other module should maintain its own mutable config singleton.\n- Validation failures must be explicit and early.\n- Sensitive values must never be logged raw.\n- Environment parsing must remain deterministic and dependency-light.\n- Operational transport thresholds belong here, not in service modules.\n- Cross-service runtime policy belongs here unless constitutionally frozen elsewhere.\n- Logging bootstrap must be idempotent and safe for repeated initialization.\n"
      },
      {
        "lineno": 430,
        "value": "Validate runtime-mode input surface for proof bundles.\n\n    This is intentionally observational. It does not reinterpret paper mode or\n    SCALPX_* into settings.runtime.runtime_mode before the main.py audit.\n    "
      },
      {
        "lineno": 1393,
        "value": "DEFAULT_EXECUTION_DECISION_BLOCK_MS"
      },
      {
        "lineno": 1394,
        "value": "DEFAULT_EXECUTION_IDLE_SLEEP_MS"
      },
      {
        "lineno": 1395,
        "value": "DEFAULT_EXECUTION_LOCK_ACQUIRE_TIMEOUT_MS"
      },
      {
        "lineno": 1439,
        "value": "ExecutionSettings"
      },
      {
        "lineno": 1450,
        "value": "build_execution_settings"
      },
      {
        "lineno": 774,
        "value": "execution"
      }
    ],
    "function_count": 6,
    "line_hit_count": 32,
    "parse_ok": true,
    "sha256": "594bd00a6f56812959540af5531d601240ef1022ef4e0fbbf68fa6b896169f35",
    "string_hit_count": 18
  },
  "app/mme_scalpx/integrations/bootstrap_provider.py": {
    "class_count": 0,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 86,
        "lineno": 68,
        "name": "_build_real_zerodha_broker"
      },
      {
        "end_lineno": 202,
        "lineno": 135,
        "name": "_build_bootstrap_payload_for_runtime_instruments"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 51,
        "value": "brokers"
      },
      {
        "lineno": 172,
        "value": "zerodha_broker_configured"
      },
      {
        "lineno": 186,
        "value": "dhan_execution_fallback_status"
      },
      {
        "lineno": 187,
        "value": "dhan_execution_fallback_reason"
      },
      {
        "lineno": 188,
        "value": "Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled"
      },
      {
        "lineno": 200,
        "value": "broker"
      }
    ],
    "function_count": 2,
    "line_hit_count": 13,
    "parse_ok": true,
    "sha256": "13e3d468c535a30a9eda30a1f585b87c665fcc404895ab6906dfaef7eac24c09",
    "string_hit_count": 6
  },
  "app/mme_scalpx/integrations/broker_api.py": {
    "class_count": 16,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 122,
        "lineno": 114,
        "name": "_wrap_validation"
      },
      {
        "end_lineno": 228,
        "lineno": 209,
        "name": "_coerce_order_price"
      },
      {
        "end_lineno": 247,
        "lineno": 231,
        "name": "_normalize_mapping_list"
      },
      {
        "end_lineno": 1363,
        "lineno": 1355,
        "name": "build_null_broker_adapter"
      },
      {
        "end_lineno": 1403,
        "lineno": 1366,
        "name": "build_real_broker_adapter"
      },
      {
        "end_lineno": 1489,
        "lineno": 1480,
        "name": "_a6_r3_request_from_any"
      },
      {
        "end_lineno": 1582,
        "lineno": 1492,
        "name": "submit_controlled_paper_sandbox_order"
      },
      {
        "end_lineno": 317,
        "lineno": 316,
        "name": "info"
      },
      {
        "end_lineno": 439,
        "lineno": 394,
        "name": "__post_init__"
      },
      {
        "end_lineno": 452,
        "lineno": 441,
        "name": "to_dict"
      },
      {
        "end_lineno": 499,
        "lineno": 486,
        "name": "get_order"
      },
      {
        "end_lineno": 514,
        "lineno": 501,
        "name": "place_order"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 3,
        "value": "\napp/mme_scalpx/integrations/broker_api.py\n\nFreeze-grade broker adapter contract and provider-aware execution seam for ScalpX MME.\n\nPurpose\n-------\nThis module OWNS:\n- broker adapter protocol surface consumed by execution/bootstrap\n- normalized order / cancel / position / open-order adapter behavior\n- broker-auth attachment for execution-capable adapters\n- provider-aware adapter metadata and capability truth\n- canonical open-orders normalization to list[Mapping[str, Any]] | None\n- compatibility builder surface for bootstrap_provider.py\n\nThis module DOES NOT own:\n- broker login/session lifecycle policy\n- provider-runtime role resolution\n- websocket lifecycle / live feed handling\n- strategy logic\n- Redis IO\n- main.py composition\n- Dhan market-data orchestration\n\nImportant contract laws\n-----------------------\n- execution.py remains the sole broker-truth owner.\n- broker_api.py is an integration seam only.\n- reconcile_open_orders() must return only:\n  - None\n  - list[Mapping[str, Any]]\n  Never a wrapper dict.\n- auth/session truth is consumed from broker_auth.py.\n- this module stays model-light to avoid drift with the parallel core.models lane.\n"
      },
      {
        "lineno": 60,
        "value": "mme-broker-api-freeze-v2"
      },
      {
        "lineno": 90,
        "value": "Base error for broker-adapter failures."
      },
      {
        "lineno": 94,
        "value": "Raised when broker-adapter config or inputs are invalid."
      },
      {
        "lineno": 98,
        "value": "Raised when broker-auth/session is unavailable for an adapter call."
      },
      {
        "lineno": 102,
        "value": "Raised when a broker transport request fails or returns invalid data."
      },
      {
        "lineno": 257,
        "value": "Protocol for provider-specific execution/order reconciliation transport."
      },
      {
        "lineno": 314,
        "value": "Canonical adapter surface consumed by bootstrap and execution."
      }
    ],
    "function_count": 38,
    "line_hit_count": 120,
    "parse_ok": true,
    "sha256": "d3e7aad669e1674868f1a8d78174a08e6aa78ae4f2b330989fe5d8a8be1b9dd5",
    "string_hit_count": 78
  },
  "app/mme_scalpx/main.py": {
    "class_count": 3,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 129,
        "lineno": 120,
        "name": "_b1_allow_execution_shadow_no_broker"
      },
      {
        "end_lineno": 172,
        "lineno": 167,
        "name": "_b1_resolve_execution_shadow_broker"
      },
      {
        "end_lineno": 626,
        "lineno": 612,
        "name": "_infer_single_feed_provider_id"
      },
      {
        "end_lineno": 691,
        "lineno": 629,
        "name": "_resolve_feed_surface_bundle"
      },
      {
        "end_lineno": 779,
        "lineno": 740,
        "name": "register_bootstrap_dependencies"
      },
      {
        "end_lineno": 838,
        "lineno": 812,
        "name": "_load_bootstrap_provider"
      },
      {
        "end_lineno": 913,
        "lineno": 841,
        "name": "maybe_register_bootstrap_dependencies"
      },
      {
        "end_lineno": 1142,
        "lineno": 1093,
        "name": "_require_service_dependencies"
      },
      {
        "end_lineno": 1200,
        "lineno": 1163,
        "name": "build_runtime_context"
      },
      {
        "end_lineno": 1971,
        "lineno": 1873,
        "name": "main"
      },
      {
        "end_lineno": 149,
        "lineno": 143,
        "name": "reconcile_position"
      },
      {
        "end_lineno": 155,
        "lineno": 154,
        "name": "place_entry_order"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 1,
        "value": "\napp/mme_scalpx/main.py\n\nSingle canonical bootstrap and orchestration entrypoint for ScalpX MME.\n\nFrozen contract\n---------------\nThis module OWNS:\n- process bootstrap sequencing\n- settings load\n- logging bootstrap\n- shutdown signal wiring\n- clock lifecycle bootstrap\n- Redis runtime bootstrap\n- Redis connectivity validation\n- optional consumer-group bootstrap\n- shared application context construction\n- per-service runtime context construction\n- runtime service supervision\n- single-service execution\n- lightweight doctor/status reporting\n- best-effort application shutdown\n- strict runtime service module validation (import, run(context) signature, location)\n\nThis module DOES NOT own:\n- Redis naming contracts\n- schema definitions\n- serialization\n- broker APIs\n- instrument/domain logic\n- service business logic\n- alternate bootstrap roots\n- integration worker orchestration\n- domain worker orchestration\n- service-specific builder helpers\n\nDesign contract\n---------------\n- main.py is the ONLY composition root.\n- All spine imports come from app.mme_scalpx.core.*\n- Only frozen runtime services under app.mme_scalpx.services.* are supervised here.\n- integrations/login.py is NOT a runtime supervised service.\n- domain/instruments.py is NOT a runtime supervised service.\n- ops/ is helper-only and not a second root.\n- Runtime behavior comes from settings.py and explicit dependency registration only.\n- Redis transport behavior remains owned by redisx.py.\n- Clock lifecycle remains owned by clock.py.\n- Replay mode requires an explicit replay wall-time anchor.\n- Shutdown is explicit, cooperativ"
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
        "lineno": 189,
        "value": "execution"
      },
      {
        "lineno": 189,
        "value": "app.mme_scalpx.services.execution"
      },
      {
        "lineno": 813,
        "value": "\n    Import and validate the explicit bootstrap provider callable.\n\n    The provider is expected to be callable and may either:\n    - call register_bootstrap_dependencies(...) directly, or\n    - return a dict containing any of:\n        runtime_instruments, feed_adapter, market_data_adapter,\n        feed_adapters, zerodha_feed_adapter, dhan_feed_adapter,\n        dhan_context_adapter, broker\n    "
      },
      {
        "lineno": 1094,
        "value": "\n    Enforce only proven service dependency requirements.\n\n    feeds.py requires:\n      - runtime_instruments / instrument_set\n      - at least one feed adapter surface, ideally provider-aware\n\n    execution.py requires:\n      - broker\n\n    These dependencies are not represented in settings.py, so they must be\n    explicitly registered before startup.\n    "
      },
      {
        "lineno": 880,
        "value": "broker"
      }
    ],
    "function_count": 16,
    "line_hit_count": 71,
    "parse_ok": true,
    "sha256": "e891d29bc22b3fe6ace6744e019db175d3c8833793c7384050c84139846f4d63",
    "string_hit_count": 28
  },
  "app/mme_scalpx/services/controlled_paper_observability.py": {
    "class_count": 2,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 104,
        "lineno": 76,
        "name": "build_controlled_paper_route_observation"
      },
      {
        "end_lineno": 118,
        "lineno": 107,
        "name": "build_fail_closed_controlled_paper_observation"
      },
      {
        "end_lineno": 45,
        "lineno": 39,
        "name": "as_dict"
      },
      {
        "end_lineno": 73,
        "lineno": 62,
        "name": "as_dict"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 1,
        "value": "Report-only controlled-paper route observability surface.\n\nThis module is intentionally side-effect free. It does not start services, touch\nRedis, call brokers, publish decisions, write order streams, place paper orders,\nor mutate position/order state.\n\nA6-PAPER-R7 wires the R4 fail-closed guard into an import-safe observability\nsurface only. Runtime integration, risk/execution start, and any paper order path\nrequire later explicit approvals and proofs.\n"
      },
      {
        "lineno": 23,
        "value": "a6_paper_r7_report_only_v1"
      },
      {
        "lineno": 28,
        "value": "External safety facts supplied by a caller.\n\n    The class is pure data. It never reads Redis, process lists, files, broker\n    state, or environment variables on its own.\n    "
      },
      {
        "lineno": 81,
        "value": "Build a pure report-only controlled-paper route observation.\n\n    This function may return ``route_allowed=True`` only to report that the pure\n    gate would pass. It still keeps order/broker/risk-execution action booleans\n    false because R7 is observability-only and not an execution route.\n    "
      },
      {
        "lineno": 43,
        "value": "risk_execution_absent"
      },
      {
        "lineno": 44,
        "value": "lock_execution_absent"
      },
      {
        "lineno": 71,
        "value": "broker_call_allowed"
      },
      {
        "lineno": 72,
        "value": "risk_execution_start_allowed"
      }
    ],
    "function_count": 4,
    "line_hit_count": 38,
    "parse_ok": true,
    "sha256": "c62507900c4b5132cd9805da0c7422a628ce6a34ac35527de56210879ec379b4",
    "string_hit_count": 8
  },
  "app/mme_scalpx/services/controlled_paper_route.py": {
    "class_count": 1,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 114,
        "lineno": 74,
        "name": "evaluate_controlled_paper_route_env"
      },
      {
        "end_lineno": 125,
        "lineno": 117,
        "name": "build_fail_closed_controlled_paper_verdict"
      },
      {
        "end_lineno": 63,
        "lineno": 53,
        "name": "as_dict"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 1,
        "value": "Fail-closed controlled-paper route guard surface.\n\nThis module is intentionally side-effect free. It does not start services, touch\nRedis, call brokers, place paper orders, or mutate position/order state.\n\nA6-PAPER-R4 adds this as an additive guard surface only. Runtime wiring and any\npaper execution path require separate approvals and later proofs.\n"
      },
      {
        "lineno": 16,
        "value": "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"
      },
      {
        "lineno": 17,
        "value": "SCALPX_CONTROLLED_PAPER_SCOPE_ACK"
      },
      {
        "lineno": 18,
        "value": "SCALPX_REAL_LIVE_ALLOWED"
      },
      {
        "lineno": 19,
        "value": "SCALPX_ALLOW_REAL_LIVE"
      },
      {
        "lineno": 20,
        "value": "SCALPX_ALLOW_BROKER_ORDERS"
      },
      {
        "lineno": 21,
        "value": "SCALPX_PAPER_ARMED"
      },
      {
        "lineno": 22,
        "value": "SCALPX_ENABLE_PAPER"
      }
    ],
    "function_count": 3,
    "line_hit_count": 52,
    "parse_ok": true,
    "sha256": "519672a722849e828d3e4b8e3e6e2c52e97084ab953fa12814a58ef707044028",
    "string_hit_count": 22
  },
  "app/mme_scalpx/services/execution.py": {
    "class_count": 8,
    "compile_ok": true,
    "exists": true,
    "first_functions": [
      {
        "end_lineno": 139,
        "lineno": 133,
        "name": "_validate_name_surface_or_die"
      },
      {
        "end_lineno": 186,
        "lineno": 160,
        "name": "_batch26b_execution_entry_hard_arming_verdict"
      },
      {
        "end_lineno": 336,
        "lineno": 335,
        "name": "_is_open_broker_status"
      },
      {
        "end_lineno": 363,
        "lineno": 355,
        "name": "_health_status_from_execution_mode"
      },
      {
        "end_lineno": 2133,
        "lineno": 2072,
        "name": "_b1a_observe_only_lifecycle_publish"
      },
      {
        "end_lineno": 2171,
        "lineno": 2136,
        "name": "run"
      },
      {
        "end_lineno": 2267,
        "lineno": 2237,
        "name": "_batch13_parse_decision"
      },
      {
        "end_lineno": 2286,
        "lineno": 2276,
        "name": "_batch13_resolve_entry_lots"
      },
      {
        "end_lineno": 2305,
        "lineno": 2295,
        "name": "_batch13_handle_entry_decision"
      },
      {
        "end_lineno": 2350,
        "lineno": 2311,
        "name": "_batch13_infer_recovered_open_order_action"
      },
      {
        "end_lineno": 2391,
        "lineno": 2356,
        "name": "_batch13_publish_malformed_decision_reject"
      },
      {
        "end_lineno": 2450,
        "lineno": 2400,
        "name": "_batch13_poll_decisions"
      }
    ],
    "first_string_hits": [
      {
        "lineno": 3,
        "value": "\napp/mme_scalpx/services/execution.py\n\nCanonical execution service for ScalpX MME.\n\nFrozen contract\n---------------\nThis module OWNS:\n- consumption of canonical strategy decisions\n- publication of canonical ACK / order / trade-ledger outputs\n- canonical execution state\n- canonical position state\n- execution singleton lock ownership\n- sole position truth\n- broker-order terminality for submitted execution intents\n\nThis module DOES NOT own:\n- strategy generation\n- risk truth\n- monitor / report truth\n- startup / composition logic\n- alternate runtime roots\n\nDesign rules\n------------\n- execution = sole position truth\n- risk may block entries but never exits\n- pending execution must map to WAIT semantics upstream and must not be turned\n  into degraded execution mode by itself\n- entry orders that time out must be actively cancelled by execution\n- names.py is the only symbolic source of truth\n- redisx.py is the only transport fa\u00e7ade\n- main.py is the only startup root\n- runtime entrypoint is exactly run(context)\n- replay-safe and restart-safe\n\nImportant freeze correction\n---------------------------\nThis rewrite consumes only the proven settings surface:\n- settings.execution.idle_sleep_ms\n- settings.execution.decision_block_ms\n- settings.execution.lock_acquire_timeout_ms\n- settings.runtime.heartbeat_ttl_ms\n- settings.runtime.lock_ttl_ms\n- settings.runtime.lock_refresh_interval_ms\n- settings.redis.stream_maxlen_approx\n- settings.startup.fail_fast\n\nNo guessed root-level execution_* settings are used.\n\nStrategy wire correction\n------------------------\nstrategy.py publishes the canonical "
      },
      {
        "lineno": 2573,
        "value": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN"
      },
      {
        "lineno": 2574,
        "value": "CONTROLLED_PAPER_SANDBOX_BACKEND_REQUIRED"
      },
      {
        "lineno": 2575,
        "value": "CONTROLLED_PAPER_SCOPE_REQUIRED"
      },
      {
        "lineno": 2576,
        "value": "CONTROLLED_PAPER_SCOPE_MISMATCH"
      },
      {
        "lineno": 2577,
        "value": "CONTROLLED_PAPER_QTY_CAP_FAIL"
      },
      {
        "lineno": 2578,
        "value": "CONTROLLED_PAPER_POSITION_NOT_FLAT"
      },
      {
        "lineno": 2579,
        "value": "CONTROLLED_PAPER_INVALID_ROUTE"
      }
    ],
    "function_count": 61,
    "line_hit_count": 120,
    "parse_ok": true,
    "sha256": "1e7d0d42af54305a0b94ddbd84e3822155dd63a6228059e734f377049e8ef6ba",
    "string_hit_count": 120
  }
}
```

## Next approval
```text
I APPROVE A6 CONTROLLED-PAPER EXECUTION BOOTSTRAP ROUTE SOURCE PATCH ONLY: PATCH EXECUTION BOOTSTRAP REPORT-ONLY/CONTROLLED-PAPER NULL-BROKER ROUTE ONLY, NO PAPER ORDER, NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```