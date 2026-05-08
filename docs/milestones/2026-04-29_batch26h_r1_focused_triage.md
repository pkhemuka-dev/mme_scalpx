# Batch 26H-R1 — Focused Alias / Override Triage

Date: 2026-04-29

## Verdict

- focused_triage_ok: `True`
- source_code_patched: `False`
- paper_armed_approved: `False`
- real_live_approved: `False`
- runtime_promotion_allowed: `False`
- p0_actionable_items_present: `True`
- p0_actionable_count: `1720`
- p1_actionable_count: `162`

## Focused Counts

```json
{
  "P0_LEGACY_RUNTIME_REFERENCE": 4,
  "P0_PAPER_LIVE_PROMOTION_SURFACE": 3,
  "P0_RAW_REDIS_OUTSIDE_NAMES": 27,
  "P0_RECENT_RUNTIME_SAFETY_WRAPPER_REVIEW": 121,
  "P0_RUNTIME_MONKEY_PATCH_OR_OVERRIDE": 1565,
  "P1_RUNTIME_TEMP_ALIAS_WITH_EXPIRY": 158,
  "P1_TOP_RUNTIME_PATCH_REQUIRED_REVIEW": 4,
  "P2_FAMILY_RUNTIME_PATCH_REQUIRED_REVIEW": 10,
  "P3_DEFER": 5
}
```

## P0 Next Patch Candidates

```json
[
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Runtime legacy/stale path reference requires direct review.",
    "focused_classification": "P0_LEGACY_RUNTIME_REFERENCE",
    "focused_reason": "Live runtime legacy/stale reference outside quarantine.",
    "groups": [
      "legacy_runtime_reference"
    ],
    "line": 140,
    "path": "app/mme_scalpx/main.py",
    "text": "    \"app.mme_scalpx.services.features_legacy_single\","
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Runtime legacy/stale path reference requires direct review.",
    "focused_classification": "P0_LEGACY_RUNTIME_REFERENCE",
    "focused_reason": "Live runtime legacy/stale reference outside quarantine.",
    "groups": [
      "legacy_runtime_reference"
    ],
    "line": 141,
    "path": "app/mme_scalpx/main.py",
    "text": "    \"app/mme_scalpx/services/features_legacy_single.py\","
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Runtime legacy/stale path reference requires direct review.",
    "focused_classification": "P0_LEGACY_RUNTIME_REFERENCE",
    "focused_reason": "Live runtime legacy/stale reference outside quarantine.",
    "groups": [
      "legacy_runtime_reference"
    ],
    "line": 142,
    "path": "app/mme_scalpx/main.py",
    "text": "    \"app.mme_scalpx.services.strategy_legacy_single\","
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Runtime legacy/stale path reference requires direct review.",
    "focused_classification": "P0_LEGACY_RUNTIME_REFERENCE",
    "focused_reason": "Live runtime legacy/stale reference outside quarantine.",
    "groups": [
      "legacy_runtime_reference"
    ],
    "line": 143,
    "path": "app/mme_scalpx/main.py",
    "text": "    \"app/mme_scalpx/services/strategy_legacy_single.py\","
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 477,
    "path": "app/mme_scalpx/main.py",
    "text": "_BOOTSTRAP_DEPENDENCY_LOCK: Final[threading.RLock] = threading.RLock()"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 710,
    "path": "app/mme_scalpx/main.py",
    "text": "    with _BOOTSTRAP_DEPENDENCY_LOCK:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 727,
    "path": "app/mme_scalpx/main.py",
    "text": "    with _BOOTSTRAP_DEPENDENCY_LOCK:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 733,
    "path": "app/mme_scalpx/main.py",
    "text": "    with _BOOTSTRAP_DEPENDENCY_LOCK:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 864,
    "path": "app/mme_scalpx/main.py",
    "text": "    clock: BaseClock"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 897,
    "path": "app/mme_scalpx/main.py",
    "text": "    clock: BaseClock"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 999,
    "path": "app/mme_scalpx/main.py",
    "text": "def build_app_context(*, settings: AppSettings, clock: BaseClock) -> AppContext:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 1380,
    "path": "app/mme_scalpx/main.py",
    "text": ") -> BaseClock:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 496,
    "path": "app/mme_scalpx/services/execution.py",
    "text": "        clock: Any,"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 2975,
    "path": "app/mme_scalpx/services/features.py",
    "text": "        if \"samples_seen\" in block:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 3804,
    "path": "app/mme_scalpx/services/features.py",
    "text": "        clock: Any,"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 1544,
    "path": "app/mme_scalpx/services/feeds.py",
    "text": "        clock: ClockProtocol,"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 579,
    "path": "app/mme_scalpx/services/monitor.py",
    "text": "        clock: Any,"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 684,
    "path": "app/mme_scalpx/services/monitor.py",
    "text": "        if not self._owns_lock:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 700,
    "path": "app/mme_scalpx/services/monitor.py",
    "text": "        if not self._owns_lock:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 720,
    "path": "app/mme_scalpx/services/report.py",
    "text": "    def __init__(self, repo: ReportRepository, *, cfg: ReportConfig, clock: Any) -> None:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 1183,
    "path": "app/mme_scalpx/services/report.py",
    "text": "        clock: Any,"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 514,
    "path": "app/mme_scalpx/services/risk.py",
    "text": "        clock: Any,"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 402,
    "path": "app/mme_scalpx/services/strategy.py",
    "text": "def _now_ns_from_clock(clock: Any) -> int:"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 888,
    "path": "app/mme_scalpx/services/strategy.py",
    "text": "        clock: Any,"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
    "focused_reason": "Raw Redis name appears outside names.py in live runtime path.",
    "groups": [
      "raw_redis_name"
    ],
    "line": 259,
    "path": "app/mme_scalpx/services/strategy_family/doctrine_runtime.py",
    "text": "    daily_loss_lock: bool = False"
  },
  {
    "classification": "PATCH_REQUIRED",
    "classification_reason": "Raw Redis name inside runtime source should be routed through names.py or justified.",
    "focused_classification": "P0_RAW_REDIS_OUTSIDE_NAMES",
  
```

## Paths by Focused Classification

```json
{
  "P0_LEGACY_RUNTIME_REFERENCE": [
    "app/mme_scalpx/main.py"
  ],
  "P0_PAPER_LIVE_PROMOTION_SURFACE": [
    "app/mme_scalpx/services/strategy.py"
  ],
  "P0_RAW_REDIS_OUTSIDE_NAMES": [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/monitor.py",
    "app/mme_scalpx/services/report.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/doctrine_runtime.py",
    "app/mme_scalpx/services/strategy_legacy_single.py"
  ],
  "P0_RECENT_RUNTIME_SAFETY_WRAPPER_REVIEW": [
    "app/mme_scalpx/services/controlled_paper_runtime.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/mist.py"
  ],
  "P0_RUNTIME_MONKEY_PATCH_OR_OVERRIDE": [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/feature_family/futures_core.py",
    "app/mme_scalpx/services/feature_family/misb_surface.py",
    "app/mme_scalpx/services/feature_family/misc_surface.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/services/feature_family/misr_surface.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/services/feature_family/option_core.py",
    "app/mme_scalpx/services/feature_family/regime.py",
    "app/mme_scalpx/services/feature_family/strike_selection.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/monitor.py",
    "app/mme_scalpx/services/report.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/common.py",
    "app/mme_scalpx/services/strategy_family/cooldowns.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/services/strategy_family/doctrine_runtime.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/event_registry.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/mist.py",
    "app/mme_scalpx/services/strategy_family/order_intent.py",
    "app/mme_scalpx/services/strategy_family/registry.py",
    "app/mme_scalpx/services/strategy_legacy_single.py"
  ],
  "P1_RUNTIME_TEMP_ALIAS_WITH_EXPIRY": [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/feature_family/__init__.py",
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/feature_family/futures_core.py",
    "app/mme_scalpx/services/feature_family/misb_surface.py",
    "app/mme_scalpx/services/feature_family/misc_surface.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/services/feature_family/misr_surface.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/services/feature_family/option_core.py",
    "app/mme_scalpx/services/feature_family/regime.py",
    "app/mme_scalpx/services/feature_family/strike_selection.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/report.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/common.py",
    "app/mme_scalpx/services/strategy_family/cooldowns.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/services/strategy_family/doctrine_contracts.py",
    "app/mme_scalpx/services/strategy_family/doctrine_runtime.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/mist.py",
    "app/mme_scalpx/services/strategy_family/registry.py"
  ],
  "P1_TOP_RUNTIME_PATCH_REQUIRED_REVIEW": [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/risk.py"
  ],
  "P2_FAMILY_RUNTIME_PATCH_REQUIRED_REVIEW": [
    "app/mme_scalpx/services/feature_family/common.py",
    "app/mme_scalpx/services/strategy_family/doctrine_contracts.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/misr.py"
  ],
  "P3_DEFER": [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/features_legacy_single.py",
    "app/mme_scalpx/services/strategy_legacy_single.py"
  ]
}
```

## Prior Safety Proof Summary

```json
{
  "26B_execution_hard_arming_guard": {
    "blockers": [],
    "exists": true,
    "ok": true,
    "paper_armed_approved": false,
    "parse_ok": true,
    "path": "run/proofs/batch26b_execution_hard_arming_guard_thin.json",
    "real_live_approved": false,
    "runtime_promotion_allowed": false,
    "warnings": []
  },
  "26C_risk_controlled_paper_veto": {
    "blockers": [],
    "exists": true,
    "ok": true,
    "paper_armed_approved": false,
    "parse_ok": true,
    "path": "run/proofs/proof_risk_controlled_paper_veto.json",
    "real_live_approved": false,
    "runtime_promotion_allowed": false,
    "warnings": []
  },
  "26D_strategy_leaf_required_surface_failclosed": {
    "blockers": [],
    "exists": true,
    "ok": true,
    "paper_armed_approved": false,
    "parse_ok": true,
    "path": "run/proofs/proof_batch26d_strategy_leaf_required_surface_failclosed.json",
    "real_live_approved": false,
    "runtime_promotion_allowed": false,
    "warnings": []
  },
  "26E_misr_trap_event_registry": {
    "blockers": [],
    "exists": true,
    "ok": true,
    "paper_armed_approved": false,
    "parse_ok": true,
    "path": "run/proofs/proof_misr_trap_event_consumption_registry.json",
    "real_live_approved": false,
    "runtime_promotion_allowed": null,
    "warnings": []
  },
  "26F_miso_burst_event_registry": {
    "blockers": [],
    "exists": true,
    "ok": true,
    "paper_armed_approved": false,
    "parse_ok": true,
    "path": "run/proofs/proof_miso_burst_event_consumption_registry.json",
    "real_live_approved": false,
    "runtime_promotion_allowed": null,
    "warnings": []
  },
  "26G_legacy_quarantine_import_graph": {
    "blockers": [],
    "exists": true,
    "ok": true,
    "paper_armed_approved": false,
    "parse_ok": true,
    "path": "run/proofs/proof_legacy_quarantine_import_graph.json",
    "real_live_approved": false,
    "runtime_promotion_allowed": false,
    "warnings": [
      "QUARANTINE_REGISTRY_LEGACY_STRINGS_PRESENT_EXPECTED"
    ]
  }
}
```

## Artifacts

- `run/proofs/proof_alias_and_override_inventory_focused_triage.json`
- `run/proofs/proof_alias_and_override_inventory_focused_triage_manifest.sha256`

## Continuation

Patch only the top P0 seam next. Do not broadly cleanup all inventory hits.

Do not enable paper_armed. Do not enable real live. Do not start controlled paper runtime chain from this batch.
