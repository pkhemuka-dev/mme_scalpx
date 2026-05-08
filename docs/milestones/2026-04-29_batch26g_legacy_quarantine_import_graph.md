# Batch 26G-R4 — Active Registry Classifier Repair

Date: 2026-04-29

## Verdict

- legacy_quarantine_import_graph_ok: `True`
- legacy_modules_not_imported_by_runtime: `True`
- main_active_registry_excludes_legacy_or_reports: `True`
- main_quarantine_registry_may_reference_legacy: `True`
- replay_reports_import_allowed: `True`
- systemd_uses_canonical_main: `True`
- systemd_excludes_legacy: `True`
- paper_armed_approved: `False`
- real_live_approved: `False`

## R4 Classifier Law

- Active runtime assignments are checked as blockers.
- Quarantine/forbidden registries may mention legacy modules as quarantine evidence.
- `app.mme_scalpx.replay.reports` is allowed.
- Only `app.mme_scalpx.services.reports` is stale/forbidden.

## Blockers

- none

## Main Active Forbidden Hits

```json
[]
```

## Quarantine Forbidden Hits

```json
[
  {
    "assignment_names": [
      "FORBIDDEN_RUNTIME_PATHS"
    ],
    "line_end": 144,
    "line_start": 136,
    "literal": "app.mme_scalpx.services.features_legacy_single"
  },
  {
    "assignment_names": [
      "FORBIDDEN_RUNTIME_PATHS"
    ],
    "line_end": 144,
    "line_start": 136,
    "literal": "app.mme_scalpx.services.strategy_legacy_single"
  }
]
```

## True Forbidden Import Hits

```json
{}
```

## Allowed Replay Reports Imports

```json
{
  "bin/replay_run.py": [
    {
      "line": 58,
      "module": "app.mme_scalpx.replay.reports",
      "names": [
        "build_report_bundle",
        "report_bundle_to_dict"
      ],
      "type": "allowed_replay_report_from_import"
    }
  ]
}
```

## Artifacts

- `run/proofs/proof_legacy_quarantine_import_graph.json`
- `run/proofs/proof_legacy_quarantine_import_graph_repair.json`
- `run/proofs/proof_legacy_quarantine_import_graph_manifest.sha256`
- backup: `run/_code_backups/batch26g_r4_active_registry_classifier_20260429_223846`

## Continuation

Next recommended batch: `26H — alias / override inventory`.

Do not enable paper_armed. Do not enable real live. Do not start controlled paper runtime chain from this batch.
